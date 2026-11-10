import csv
import time
from pathlib import Path

from target import target

import numpy as np
import rasterio
from rasterio.features import geometry_mask
from rasterio.warp import reproject, Resampling

input_dir = Path(r"C:\Users\WYF18\Desktop\三上\自学\批量处理\影像raw_single")
out_dir = Path(r"C:\Users\WYF18\Desktop\三上\自学\批量处理\影像out_single")
aoi_path = Path(r"C:\Users\WYF18\Desktop\三上\自学\批量处理\area_enshi\Enshi_area.json")

target_crs = "EPSG:32649"
res = 30.0

bands = None

mask_band = 3
mask_mode = "landsat"
mask_values = [3, 8, 9, 10, 11]

resampling = Resampling.bilinear

# Landsat C2 L2 地表反射率缩放：DN * 2.75e-5 - 0.2
# 如果输入本身已经是 0-1 的反射率（例如 GEE 导出的产品），把它改成 False
scale_sr = True

max_files = 1
skip_existing = True

# manifest 的列名，必须和下面 rows 里的键完全一致
MANIFEST_FIELDS = [
    "input", "output", "bands", "width", "height",
    "valid_fraction", "seconds", "error",
]


def landsat_bad_mask(qa):
    """把 Landsat QA_PIXEL 转成布尔掩膜：True 表示坏像元。"""
    # Collection 2 QA_PIXEL：bit1 膨胀云、bit2 卷云、bit3 云、bit4 云影、bit5 雪
    bits = (1 << 1) | (1 << 2) | (1 << 3) | (1 << 4) | (1 << 5)
    return (qa & bits) != 0


def process_image(src_path, dst_path, geom, dst_transform, dst_width, dst_height):
    """处理一景：重投影 → SR 缩放 → 云掩膜 → AOI 裁剪 → 写 GeoTIFF。"""
    with rasterio.open(src_path) as src:
        # 0) 先校验掩膜波段号，避免它悄悄超出范围
        if mask_band is not None and mask_band > src.count:
            raise ValueError(
                f"mask_band={mask_band} 超出波段数 {src.count}；"
                f"文件 {src_path.name} 可能只有质量波段，请先建好多波段 VRT"
            )

        # 1) 选波段：排除掩膜波段
        if bands is None:
            band_indexes = [i for i in range(1, src.count + 1) if i != mask_band]
        else:
            band_indexes = [i for i in bands if i != mask_band]
        if not band_indexes:
            raise ValueError("没有有效的波段可处理，请检查 bands 参数。")

        # 2) 先分配目标数组（全 NaN）
        dst_data = np.full(
            (len(band_indexes), dst_height, dst_width),
            np.nan,
            dtype="float32",
        )

        # 3) 逐波段重投影/重采样到目标网格（必须在 with 内部，文件还开着）
        for out_i, band_i in enumerate(band_indexes):
            reproject(
                source=rasterio.band(src, band_i),
                destination=dst_data[out_i],
                src_transform=src.transform,
                src_crs=src.crs,
                dst_transform=dst_transform,
                dst_crs=target_crs,
                resampling=resampling,
                src_nodata=src.nodata,
                dst_nodata=np.nan,
            )

        # 4) 地表反射率缩放：原地运算，避免再复制一份几百 MB 的数组
        if scale_sr:
            dst_data *= np.float32(0.0000275)
            dst_data -= np.float32(0.2)

        # 5) 云/质量掩膜
        if mask_band is not None and mask_mode != "none":
            mask_src = src.read(mask_band)
            mask_dst = np.zeros((dst_height, dst_width), dtype="uint16")
            reproject(
                source=mask_src,
                destination=mask_dst,
                src_transform=src.transform,
                src_crs=src.crs,                 # 数组没有 CRS，必须显式给
                dst_transform=dst_transform,
                dst_crs=target_crs,
                resampling=Resampling.nearest,   # 分类/位标志必须最近邻
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

        # 6) 裁到 AOI：多边形内保留，区外设 NaN（范围仍是外接矩形）
        inside = geometry_mask(
            [geom],
            out_shape=(dst_height, dst_width),
            transform=dst_transform,
            invert=True,
            all_touched=False,   # 按像元中心判断
        )
        for i in range(dst_data.shape[0]):
            dst_data[i][~inside] = np.nan

        # 7) 波段描述
        descriptions = []
        for band_i in band_indexes:
            desc = None
            if src.descriptions:
                desc = src.descriptions[band_i - 1]
            descriptions.append(desc or f"band_{band_i}")

    # 8) 写出 GeoTIFF（此时 src 已关闭，只用内存里的 dst_data）
    profile = {
        "driver": "GTiff",
        "height": dst_height,
        "width": dst_width,
        "count": len(band_indexes),
        "dtype": "float32",       # 能存 NaN
        "crs": target_crs,
        "transform": dst_transform,   # 必须写目标网格
        "nodata": np.nan,
        "compress": "deflate",
        "tiled": True,
        "predictor": 3,           # 浮点数据用 3（2 是整数用的）
        "BIGTIFF": "IF_SAFER",    # 超过 4GB 自动切 BigTIFF
    }

    dst_path.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(dst_path, "w", **profile) as dst:
        dst.write(dst_data)
        for i, desc in enumerate(descriptions, start=1):
            dst.set_band_description(i, desc)

    total = dst_data.size
    valid = int(np.isfinite(dst_data).sum())
    return {
        "bands": len(band_indexes),
        "total_pixels": total,
        "valid_pixels": valid,
        "valid_fraction": round(valid / total, 4) if total else 0.0,
    }


def main():
    geom, dst_transform, dst_width, dst_height = target(aoi_path, target_crs, res)
    out_dir.mkdir(parents=True, exist_ok=True)

    print("目标网格:", dst_transform)
    print("目标尺寸:", dst_width, "x", dst_height)

    files = [
        p for p in sorted(input_dir.iterdir())
        if p.suffix.lower() in {".tif", ".tiff", ".vrt"}
    ]
    if max_files is not None:
        files = files[:max_files]
    if not files:
        raise SystemExit(f"没有找到影像文件（.tif/.tiff/.vrt）: {input_dir}")

    rows = []
    for src_path in files:
        dst_path = out_dir / f"{src_path.stem}_enshi1.tif"
        t0 = time.time()

        if skip_existing and dst_path.exists():
            print("跳过（输出已存在）:", dst_path.name)
            rows.append({
                "input": str(src_path),
                "output": str(dst_path),
                "bands": None,
                "width": dst_width,
                "height": dst_height,
                "valid_fraction": None,
                "seconds": 0.0,
                "error": "skipped: 输出已存在",
            })
            continue

        try:
            info = process_image(
                src_path, dst_path, geom,
                dst_transform, dst_width, dst_height,
            )
            rows.append({
                "input": str(src_path),
                "output": str(dst_path),
                "bands": info["bands"],
                "width": dst_width,
                "height": dst_height,
                "valid_fraction": info["valid_fraction"],
                "seconds": round(time.time() - t0, 2),
                "error": "",
            })
            print("ok:", dst_path.name, "valid=", info["valid_fraction"])
        except Exception as e:
            rows.append({
                "input": str(src_path),
                "output": str(dst_path),
                "bands": None,
                "width": dst_width,
                "height": dst_height,
                "valid_fraction": None,
                "seconds": round(time.time() - t0, 2),
                "error": repr(e),
            })
            print("fail:", src_path.name, repr(e))

    manifest = out_dir / "manifest.csv"
    with open(manifest, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=MANIFEST_FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    print("manifest:", manifest)


if __name__ == "__main__":
    main()
