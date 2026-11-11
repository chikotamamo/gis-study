# -*- coding: utf-8 -*-
"""一体化影像预处理：自动识别 GEE 产品 / USGS 原始单波段，统一到研究区网格。

支持两种输入，可混放在同一个目录：
  A) 多波段文件：GEE 导出成果、gdalbuildvrt 生成的 VRT、已堆叠产品
  B) 单波段文件：USGS 逐波段下载的 SR_B1..SR_B7 / QA_PIXEL 等

自动判断：
  1. 掩膜：波段名含 QA_PIXEL → Landsat 位掩膜
           波段名含 SCL      → Sentinel-2 类别掩膜
           都没有            → 不掩膜（视为云端已处理）
  2. 缩放：浮点数据                → 不缩放（GEE 已缩放过）
           uint16 且波段名 SR_B*   → Landsat 系数 2.75e-5 / -0.2
           uint16 且波段名 B4/B8   → Sentinel-2 系数 1e-4
  3. 单波段文件按文件名前缀分组，同一景自动堆叠成一个多波段输出
  4. 输出名自动带来源标记：<场景>_gee_aligned.tif / <场景>_raw_aligned.tif
     来源由「是否需要缩放或掩膜」决定，同名不会互相覆盖
"""

import csv
import re
import time
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import rasterio
from rasterio.features import geometry_mask
from rasterio.warp import reproject, Resampling

from target import target

# ================= 配置 =================
input_dir = Path(r"C:\Users\WYF18\Desktop\三上\自学\批量处理\影像raw_single")
out_dir = Path(r"C:\Users\WYF18\Desktop\三上\自学\批量处理\影像out_single")
aoi_path = Path(r"C:\Users\WYF18\Desktop\三上\自学\批量处理\area_enshi\Enshi_area.json")

target_crs = "EPSG:32649"
res = 30.0

recursive = False        # True 会扫子目录（如 bands\）
max_scenes = None        # None = 全部；先跑 1 景可改 1
skip_existing = True

# 自动判断的强制覆盖：None 表示自动；也可写 "none" / "landsat" / "s2" / "scl"
scale_override = None
mask_override = None
assume_mask_last = False   # 多波段文件没有波段名时，是否把最后一个波段当 QA

dry_run = False            # True 只列出识别结果，不处理
skip_unknown = True        # 无波段描述的多波段文件：跳过而不是报错

output_suffix = "_done"
# ========================================

MANIFEST_FIELDS = [
    "scene", "source", "output", "bands", "scale", "mask",
    "width", "height", "valid_fraction", "seconds", "error",
]

# 从单波段文件名里拆出「场景」和「波段」
BAND_RE = re.compile(
    r"^(?P<scene>.+?)_(?P<band>SR_B\d{1,2}|B\d{1,2}|QA_PIXEL|QA_RADSAT|SCL|BQA)$",
    re.IGNORECASE,
)

MASK_KINDS = {"QA_PIXEL": "landsat", "SCL": "scl"}


class UnknownBandsError(ValueError):
    """多波段文件没有波段描述，无法判断哪个是掩膜波段。"""


@dataclass
class BandRef:
    """一个波段：来自哪个文件、第几波段、叫什么名字。"""
    name: str
    path: Path
    index: int


@dataclass
class Scene:
    """一景：一个多波段文件，或一组同前缀的单波段文件。"""
    name: str
    bands: list = field(default_factory=list)
    kind: str = "multi"          # "multi" | "single"


def list_files(folder, is_recursive=False):
    """收集 .tif/.tiff/.vrt；辅助文件（.aux.xml）自然被排除。"""
    pattern = "**/*" if is_recursive else "*"
    return sorted(
        p for p in folder.glob(pattern)
        if p.suffix.lower() in {".tif", ".tiff", ".vrt"}
    )


def band_name(desc, index):
    """优先用文件里的波段描述，没有就用 BAND_i。"""
    if desc and str(desc).strip():
        return str(desc).strip().upper()
    return f"BAND_{index}"


def collect_scenes(files):
    """把文件分成「多波段景」和「单波段景」。"""
    scenes = []
    single_groups = {}

    for path in files:
        with rasterio.open(path) as src:
            count = src.count
            descs = src.descriptions

        if count > 1:
            bands = [
                BandRef(band_name(descs[i - 1] if descs else None, i), path, i)
                for i in range(1, count + 1)
            ]
            scenes.append(Scene(name=path.stem, bands=bands, kind="multi"))
        else:
            m = BAND_RE.match(path.stem)
            if not m:
                print("跳过（认不出波段名）:", path.name)
                continue
            scene_name = m.group("scene")
            bname = m.group("band").upper()
            single_groups.setdefault(scene_name, []).append(BandRef(bname, path, 1))

    for scene_name, bands in single_groups.items():
        bands.sort(key=lambda b: (b.name in MASK_KINDS, b.name))
        scenes.append(Scene(name=scene_name, bands=bands, kind="single"))

    return scenes


def pick_mask(scene):
    """返回 (掩膜波段, 掩膜方式)；没有掩膜返回 (None, None)。"""
    for band in scene.bands:
        kind = MASK_KINDS.get(band.name)
        if kind:
            return band, kind
    if assume_mask_last and scene.kind == "multi" and len(scene.bands) >= 2:
        return scene.bands[-1], "landsat"
    return None, None


def pick_scale(scene, data_bands):
    """返回缩放方式："none" / "landsat" / "s2"。"""
    if scale_override:
        return scale_override

    names = {b.name for b in data_bands}
    dtypes = []
    for band in data_bands:
        with rasterio.open(band.path) as src:
            dtypes.append(src.dtypes[band.index - 1])

    if any(np.issubdtype(np.dtype(d), np.floating) for d in dtypes):
        return "none"
    if any(n.startswith("SR_B") for n in names):
        return "landsat"
    if any(re.fullmatch(r"B\d{1,2}", n) for n in names):
        return "s2"
    return "none"


def detect_scene(scene):
    """判断一景的来源与处理方式，返回 dict。"""
    if (scene.kind == "multi"
            and all(b.name.startswith("BAND_") for b in scene.bands)
            and not assume_mask_last):
        raise UnknownBandsError(
            f"{scene.name}: 多波段文件没有波段描述，无法判断掩膜波段。"
            f"请改用 GEE 导出或单波段文件；"
            f"或设 assume_mask_last=True 并把 scale_override 设成 'landsat'"
        )

    mask_band, mask_kind = pick_mask(scene)
    if mask_override:
        mask_kind = None if mask_override == "none" else mask_override

    data_bands = [b for b in scene.bands if mask_band is None or b is not mask_band]
    if not data_bands:
        raise ValueError(f"{scene.name}: 没有可输出的数据波段")

    scale_kind = pick_scale(scene, data_bands)

    # 需要缩放或需要掩膜 → 原始产品；两者都不需要 → 已处理过的 GEE 产品
    source = "gee" if (scale_kind == "none" and not mask_kind) else "raw"

    return {
        "mask_band": mask_band,
        "mask_kind": mask_kind,
        "data_bands": data_bands,
        "scale": scale_kind,
        "source": source,
    }


def target_path(scene, source):
    """输出路径：<场景>_<来源>_aligned.tif；不覆盖已有文件时自动加 _v2。"""
    base = out_dir / f"{scene.name}_{source}{output_suffix}.tif"
    if skip_existing or not base.exists():
        return base
    i = 2
    while True:
        candidate = out_dir / f"{scene.name}_{source}_v{i}{output_suffix}.tif"
        if not candidate.exists():
            return candidate
        i += 1


def apply_scale(data, mode):
    """原地缩放，避免多复制一份几百 MB 的数组。"""
    if mode == "landsat":
        data *= np.float32(0.0000275)
        data -= np.float32(0.2)
    elif mode == "s2":
        data *= np.float32(0.0001)


def landsat_bad_mask(qa):
    """QA_PIXEL → 布尔掩膜：True = 坏像元（膨胀云/卷云/云/云影/雪）。"""
    bits = (1 << 1) | (1 << 2) | (1 << 3) | (1 << 4) | (1 << 5)
    return (qa & bits) != 0


def check_same_grid(scene):
    """同一景的所有波段必须同 CRS、同 transform、同宽高。"""
    ref = None
    ref_name = None
    for band in scene.bands:
        with rasterio.open(band.path) as src:
            grid = (str(src.crs), src.transform, src.width, src.height)
        if ref is None:
            ref, ref_name = grid, band.name
        elif grid != ref:
            raise ValueError(
                f"{scene.name}: 波段 {band.name} 的网格与 {ref_name} 不一致，无法堆叠"
            )


def process_scene(scene, det, dst_path, geom, dst_transform, dst_width, dst_height):
    """处理一景：堆叠重投影 → 缩放 → 掩膜 → 裁 AOI → 写出。"""
    check_same_grid(scene)

    data_bands = det["data_bands"]
    scale_kind = det["scale"]
    mask_band = det["mask_band"]
    mask_kind = det["mask_kind"]

    dst_data = np.full(
        (len(data_bands), dst_height, dst_width), np.nan, dtype="float32"
    )

    for i, band in enumerate(data_bands):
        with rasterio.open(band.path) as src:
            src_nodata = src.nodata if src.nodata is not None else 0
            reproject(
                source=rasterio.band(src, band.index),
                destination=dst_data[i],
                src_transform=src.transform,
                src_crs=src.crs,
                dst_transform=dst_transform,
                dst_crs=target_crs,
                resampling=Resampling.bilinear,
                src_nodata=src_nodata,
                dst_nodata=np.nan,
            )

    apply_scale(dst_data, scale_kind)

    if mask_band is not None and mask_kind and mask_kind != "none":
        with rasterio.open(mask_band.path) as src:
            mask_src = src.read(mask_band.index)
            mask_dst = np.zeros((dst_height, dst_width), dtype="uint16")
            reproject(
                source=mask_src,
                destination=mask_dst,
                src_transform=src.transform,
                src_crs=src.crs,
                dst_transform=dst_transform,
                dst_crs=target_crs,
                resampling=Resampling.nearest,
                src_nodata=0,
                dst_nodata=0,
            )

        if mask_kind == "landsat":
            bad = landsat_bad_mask(mask_dst)
        elif mask_kind == "scl":
            bad = np.isin(mask_dst, [3, 8, 9, 10, 11])
        else:
            raise ValueError(f"未知掩膜方式: {mask_kind}")

        for i in range(dst_data.shape[0]):
            dst_data[i][bad] = np.nan

    inside = geometry_mask(
        [geom], out_shape=(dst_height, dst_width),
        transform=dst_transform, invert=True, all_touched=False,
    )
    for i in range(dst_data.shape[0]):
        dst_data[i][~inside] = np.nan

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
        for i, band in enumerate(data_bands, start=1):
            dst.set_band_description(i, band.name)

    total = dst_data.size
    valid = int(np.isfinite(dst_data).sum())
    return {
        "bands": len(data_bands),
        "valid_fraction": round(valid / total, 4) if total else 0.0,
    }


def main():
    geom, dst_transform, dst_width, dst_height = target(aoi_path, target_crs, res)
    out_dir.mkdir(parents=True, exist_ok=True)

    print("目标网格:", dst_width, "x", dst_height)

    files = list_files(input_dir, recursive)
    if not files:
        raise SystemExit(f"没有找到影像: {input_dir}")

    scenes = collect_scenes(files)
    if not scenes:
        raise SystemExit("没有可处理的场景（文件名或波段名无法识别）")

    print(f"发现 {len(scenes)} 景:")
    for scene in scenes:
        names = ", ".join(b.name for b in scene.bands)
        print(f"  - {scene.name} [{scene.kind}]: {names}")

    if dry_run:
        print("dry_run=True：只列识别结果，不处理")
        for scene in scenes:
            try:
                det = detect_scene(scene)
                print(f"  → {scene.name}: 来源={det['source']}, "
                      f"缩放={det['scale']}, 掩膜={det['mask_kind'] or '无'}, "
                      f"输出={scene.name}_{det['source']}{output_suffix}.tif")
            except Exception as e:
                print(f"  → {scene.name}: 无法处理 {e!r}")
        return

    if max_scenes is not None:
        scenes = scenes[:max_scenes]

    rows = []
    for scene in scenes:
        t0 = time.time()

        # 先判断来源，再决定输出名（带 _gee / _raw）
        try:
            det = detect_scene(scene)
        except UnknownBandsError as e:
            if skip_unknown:
                print("跳过（无波段描述）:", scene.name)
                rows.append({
                    "scene": scene.name, "source": None, "output": None,
                    "bands": None, "scale": None, "mask": None,
                    "width": dst_width, "height": dst_height,
                    "valid_fraction": None, "seconds": 0.0,
                    "error": "skipped: 无波段描述",
                })
                continue
            rows.append({
                "scene": scene.name, "source": None, "output": None,
                "bands": None, "scale": None, "mask": None,
                "width": dst_width, "height": dst_height,
                "valid_fraction": None,
                "seconds": round(time.time() - t0, 2), "error": repr(e),
            })
            print("fail:", scene.name, repr(e))
            continue
        except Exception as e:
            rows.append({
                "scene": scene.name, "source": None, "output": None,
                "bands": None, "scale": None, "mask": None,
                "width": dst_width, "height": dst_height,
                "valid_fraction": None,
                "seconds": round(time.time() - t0, 2), "error": repr(e),
            })
            print("fail:", scene.name, repr(e))
            continue

        source = det["source"]
        dst_path = target_path(scene, source)

        if skip_existing and dst_path.exists():
            print("跳过（输出已存在）:", dst_path.name)
            rows.append({
                "scene": scene.name, "source": source, "output": str(dst_path),
                "bands": None, "scale": det["scale"], "mask": det["mask_kind"],
                "width": dst_width, "height": dst_height,
                "valid_fraction": None, "seconds": 0.0,
                "error": "skipped: 输出已存在",
            })
            continue

        print(f"  {scene.name}: 来源={source}, {len(det['data_bands'])} 波段, "
              f"缩放={det['scale']}, 掩膜={det['mask_kind'] or '无'}")

        try:
            info = process_scene(
                scene, det, dst_path, geom,
                dst_transform, dst_width, dst_height,
            )
            rows.append({
                "scene": scene.name, "source": source, "output": str(dst_path),
                "bands": info["bands"], "scale": det["scale"],
                "mask": det["mask_kind"], "width": dst_width, "height": dst_height,
                "valid_fraction": info["valid_fraction"],
                "seconds": round(time.time() - t0, 2), "error": "",
            })
            print("ok:", dst_path.name, "valid=", info["valid_fraction"])
        except Exception as e:
            rows.append({
                "scene": scene.name, "source": source, "output": str(dst_path),
                "bands": None, "scale": det["scale"], "mask": det["mask_kind"],
                "width": dst_width, "height": dst_height,
                "valid_fraction": None,
                "seconds": round(time.time() - t0, 2), "error": repr(e),
            })
            print("fail:", scene.name, repr(e))

    manifest = out_dir / "manifest.csv"
    with open(manifest, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=MANIFEST_FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    print("manifest:", manifest)


if __name__ == "__main__":
    main()
