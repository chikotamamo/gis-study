# -*- coding: utf-8 -*-
"""把一景 Landsat 的「单波段文件」直接处理成多波段产品。

与旧脚本 preprocess_single.py 的区别：
  旧：输入必须是「一个多波段文件」（例如 gdalbuildvrt 生成的 VRT）；
  新：输入是「一个文件夹里的多个单波段 TIF」，脚本自己按场景分组并堆叠。

流程：认波段 → 校验网格一致 → 逐波段重投影进同一个数组（等于堆叠）
      → 反射率缩放 → QA 云掩膜 → AOI 裁剪 → 写多波段 GeoTIFF。
"""

import csv
import re
import time
from pathlib import Path

from target import target

import numpy as np
import rasterio
from rasterio.features import geometry_mask
from rasterio.warp import reproject, Resampling

# ================= 配置（只改这一块） =================
input_dir = Path(r"C:\Users\WYF18\Desktop\三上\自学\批量处理\影像raw_single\bands")
out_dir = Path(r"C:\Users\WYF18\Desktop\三上\自学\批量处理\影像out_single")
aoi_path = Path(r"C:\Users\WYF18\Desktop\三上\自学\批量处理\area_enshi\Enshi_area.json")

target_crs = "EPSG:32649"
res = 30.0

# 输出哪些波段、按什么顺序（这里写文件名里的后缀，不含场景前缀）
# None = 自动使用目录里所有 SR_B* 波段，按波段号排序
band_order = ["SR_B4", "SR_B5"]      # NDVI 只要红和近红外

mask_suffix = "QA_PIXEL"             # 掩膜波段后缀；None = 不掩膜
mask_mode = "landsat"                # "landsat" / "scl" / "none"
mask_values = [3, 8, 9, 10, 11]      # 仅 mask_mode="scl" 时使用

resampling = Resampling.bilinear     # 连续变量双线性
scale_sr = True                      # Landsat C2 L2：DN * 2.75e-5 - 0.2

max_scenes = 1                       # 先跑 1 景；批量时改 None
skip_existing = True
# ======================================================

MANIFEST_FIELDS = [
    "scene", "output", "bands", "width", "height",
    "valid_fraction", "seconds", "error",
]

# 从文件名里拆出「场景前缀」和「波段名」
# 例：LC09_L2SP_126039_20250611_20250612_02_T1_SR_B4
#     -> scene=LC09_L2SP_126039_20250611_20250612_02_T1, band=SR_B4
BAND_RE = re.compile(
    r"^(?P<scene>.+)_(?P<band>SR_B\d|SR_QA_AEROSOL|QA_PIXEL|QA_RADSAT)$",
    re.IGNORECASE,
)


def landsat_bad_mask(qa):
    """Landsat QA_PIXEL -> 布尔掩膜：True 表示坏像元。"""
    # bit1 膨胀云、bit2 卷云、bit3 云、bit4 云影、bit5 雪
    bits = (1 << 1) | (1 << 2) | (1 << 3) | (1 << 4) | (1 << 5)
    return (qa & bits) != 0


def collect_scenes(folder):
    """扫描文件夹，把单波段文件按场景前缀分组。

    返回：{"场景前缀": {"SR_B4": Path, "SR_B5": Path, "QA_PIXEL": Path}, ...}
    """
    if not folder.exists():
        raise SystemExit(f"输入目录不存在: {folder}")

    scenes = {}
    for p in sorted(folder.iterdir()):
        if p.suffix.lower() not in {".tif", ".tiff"}:
            continue
        m = BAND_RE.match(p.stem)
        if not m:
            print("跳过（文件名认不出波段）:", p.name)
            continue
        scene = m.group("scene")
        band = m.group("band").upper()
        scenes.setdefault(scene, {})[band] = p
    return scenes


def check_same_grid(scene, band_files):
    """同一景的所有波段必须同 CRS、同 transform、同宽高，否则不能直接堆叠。"""
    ref = None
    ref_name = None
    for name, path in band_files.items():
        with rasterio.open(path) as s:
            grid = (str(s.crs), s.transform, s.width, s.height)
        if ref is None:
            ref, ref_name = grid, name
        elif grid != ref:
            raise ValueError(
                f"{scene}: 波段 {name} 的网格与 {ref_name} 不一致，无法直接堆叠"
            )


def process_scene(scene, band_files, dst_path, geom,
                  dst_transform, dst_width, dst_height):
    """处理一景：堆叠 + 重投影 + 缩放 + 掩膜 + AOI 裁剪 + 写出。"""
    check_same_grid(scene, band_files)

    # 1) 决定输出哪些数据波段
    if band_order is None:
        data_bands = sorted(
            [b for b in band_files if re.fullmatch(r"SR_B\d", b)],
            key=lambda b: int(b.split("_B")[1]),
        )
    else:
        missing = [b for b in band_order if b not in band_files]
        if missing:
            raise ValueError(f"{scene}: 缺少波段 {missing}")
        data_bands = list(band_order)

    if not data_bands:
        raise ValueError(f"{scene}: 没有可输出的数据波段")

    mask_path = band_files.get(mask_suffix) if mask_suffix else None

    # 2) 目标数组：第 0 维就是波段维，这一步就是「堆叠」的容器
    dst_data = np.full(
        (len(data_bands), dst_height, dst_width),
        np.nan,
        dtype="float32",
    )

    # 3) 逐波段读一个、投一个，内存里同时只有 1 个源波段
    for i, name in enumerate(data_bands):
        with rasterio.open(band_files[name]) as s:
            reproject(
                source=rasterio.band(s, 1),
                destination=dst_data[i],
                src_transform=s.transform,
                src_crs=s.crs,
                dst_transform=dst_transform,
                dst_crs=target_crs,
                resampling=resampling,
                src_nodata=s.nodata,
                dst_nodata=np.nan,
            )

    # 4) 地表反射率缩放（原地运算，避免多复制一份大数组）
    if scale_sr:
        dst_data *= np.float32(0.0000275)
        dst_data -= np.float32(0.2)

    # 5) 云/质量掩膜
    if mask_path is not None and mask_mode != "none":
        with rasterio.open(mask_path) as s:
            mask_src = s.read(1)
            mask_dst = np.zeros((dst_height, dst_width), dtype="uint16")
            reproject(
                source=mask_src,
                destination=mask_dst,
                src_transform=s.transform,
                src_crs=s.crs,
                dst_transform=dst_transform,
                dst_crs=target_crs,
                resampling=Resampling.nearest,   # 位标志绝不能插值
                src_nodata=0,
                dst_nodata=0,
            )

        if mask_mode == "scl":
            bad = np.isin(mask_dst, mask_values)
        elif mask_mode == "landsat":
            bad = landsat_bad_mask(mask_dst)
        else:
            raise ValueError(f"未知的 mask_mode: {mask_mode}")

        for i in range(dst_data.shape[0]):
            dst_data[i][bad] = np.nan
    elif mask_suffix:
        print("警告: 没有找到掩膜波段", mask_suffix, "，这次不做云掩膜")

    # 6) 裁到 AOI：区外设 NaN，范围仍是外接矩形
    inside = geometry_mask(
        [geom],
        out_shape=(dst_height, dst_width),
        transform=dst_transform,
        invert=True,
        all_touched=False,
    )
    for i in range(dst_data.shape[0]):
        dst_data[i][~inside] = np.nan

    # 7) 写出多波段 GeoTIFF
    profile = {
        "driver": "GTiff",
        "height": dst_height,
        "width": dst_width,
        "count": len(data_bands),
        "dtype": "float32",
        "crs": target_crs,
        "transform": dst_transform,
        "nodata": np.nan,
        "compress": "deflate",
        "tiled": True,
        "predictor": 3,
        "BIGTIFF": "IF_SAFER",
    }
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(dst_path, "w", **profile) as dst:
        dst.write(dst_data)
        for i, name in enumerate(data_bands, start=1):
            dst.set_band_description(i, name)

    total = dst_data.size
    valid = int(np.isfinite(dst_data).sum())
    return {
        "bands": len(data_bands),
        "band_names": data_bands,
        "valid_fraction": round(valid / total, 4) if total else 0.0,
    }


def main():
    geom, dst_transform, dst_width, dst_height = target(aoi_path, target_crs, res)
    out_dir.mkdir(parents=True, exist_ok=True)

    print("目标网格:", dst_transform)
    print("目标尺寸:", dst_width, "x", dst_height)

    scenes = collect_scenes(input_dir)
    if not scenes:
        raise SystemExit(f"没有可用影像（.tif/.tiff 且文件名带波段后缀）: {input_dir}")

    items = sorted(scenes.items())
    print(f"发现 {len(items)} 景:")
    for scene, band_files in items:
        print("  -", scene, "波段:", ", ".join(sorted(band_files)))

    if max_scenes is not None:
        items = items[:max_scenes]

    rows = []
    for scene, band_files in items:
        dst_path = out_dir / f"{scene}_aligned.tif"
        t0 = time.time()

        if skip_existing and dst_path.exists():
            print("跳过（输出已存在）:", dst_path.name)
            rows.append({
                "scene": scene, "output": str(dst_path), "bands": None,
                "width": dst_width, "height": dst_height, "valid_fraction": None,
                "seconds": 0.0, "error": "skipped: 输出已存在",
            })
            continue

        try:
            info = process_scene(
                scene, band_files, dst_path, geom,
                dst_transform, dst_width, dst_height,
            )
            rows.append({
                "scene": scene,
                "output": str(dst_path),
                "bands": info["bands"],
                "width": dst_width,
                "height": dst_height,
                "valid_fraction": info["valid_fraction"],
                "seconds": round(time.time() - t0, 2),
                "error": "",
            })
            print("ok:", dst_path.name,
                  "波段=", info["band_names"],
                  "valid=", info["valid_fraction"])
        except Exception as e:
            rows.append({
                "scene": scene, "output": str(dst_path), "bands": None,
                "width": dst_width, "height": dst_height, "valid_fraction": None,
                "seconds": round(time.time() - t0, 2), "error": repr(e),
            })
            print("fail:", scene, repr(e))

    manifest = out_dir / "manifest.csv"
    with open(manifest, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=MANIFEST_FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    print("manifest:", manifest)


if __name__ == "__main__":
    main()
