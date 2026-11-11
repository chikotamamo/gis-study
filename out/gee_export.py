'''
旨在代码GEE → Drive：导出研究区影像（Landsat 9 C2 L2，30 m，EPSG:32649）

流程：读本地 AOI → 用 target() 算网格 → GEE 里筛选/去云/缩放
      → 用 crsTransform 锁定同一网格 → 提交 Drive 导出任务

通过gee_export输出图像，再利用preprocess对图像进行预处理，获得研究区图像，
从而进行后续研究

目前的crs为"EPSG:32649"、res为30、研究区为恩施州
使用的产品为"LANDSAT/LC09/C02/T1_L2"
提取的波段为"SR_B4", "SR_B5"，用于计算NDVI
'''

import ee
from pathlib import Path
from pyproj import Transformer
from target import target

aoi_path = Path(r"C:\Users\WYF18\Desktop\三上\自学\批量处理\area_enshi\Enshi_area.json")
target_crs = "EPSG:32649"
res = 30.0

collection = "LANDSAT/LC09/C02/T1_L2"
bands = ["SR_B4", "SR_B5"]
start,end = "2025-06-01","2026-10-01"
cloud_pct = 40

composite = "median"               # "single" 单景 / "median" 时间中值合成
scale_in_gee = True

test_mode = False
test_size_km = 20

prefer_direct = True
drive_folder = "gee_export"  #导出文件放 Drive 哪个目录，不存在会自动建  
prefix = "enshi_LC09_B45_FULL"    #文件名前缀	输出文件叫 <prefix>.tif，也是 Tasks 里的任务名

mask_bits = 62
max_pixels = 1e10


def use_grid():              #用本地 target() 算网格，返回 (bbox, transform, width, height)。
  geom, t, w, h = target(aoi_path, target_crs, res)
  bbox = (t.c, t.f + t.e * h, t.c + t.a * w, t.f)
  return bbox, t, w, h

def sub_grid(t, width, height, size_km):        #从整幅网格正中间，切一个 20 km × 20 km 的小方块，专门用来做「试跑」。
  n = int(size_km * 1000 / res)
  c0 = (width - n) // 2
  r0 = (height - n) // 2
  minx = t.c + c0 * t.a
  maxy = t.f + r0 * t.e
  bbox = (minx, maxy + n * t.e, minx + n * t.a, maxy)
  tf = [t.a, t.b, minx, t.d, t.e, maxy]
  return bbox, tf, n, n

def build_image(region):
  """筛选 → 去云 → 合成 → 缩放。"""
  col = (ee.ImageCollection(collection).filterBounds(region).filterDate(start,end))
  if cloud_pct:
    col = col.filter(ee.Filter.lt("CLOUD_COVER", cloud_pct))

  def clear(image):
    qa = image.select("QA_PIXEL")
    return image.updateMask(qa.bitwiseAnd(mask_bits).eq(0))

  if composite == "median":
    image = col.map(clear).select(bands).median()
  else:
    image = clear(col.sort("CLOUD_COVER").first()).select(bands)
  if scale_in_gee:
    image = image.multiply(0.0000275).add(-0.2)
  return image.toFloat()   # ← 64 位 → 32 位，体积减半,对图像影响不大

def to_region(bbox):
  """把 UTM 矩形转成 GEE 的经纬度多边形。

    坑：ee.Geometry.Rectangle(..., proj="EPSG:32649") 并不会真正投影，
    实测 getInfo() 返回的坐标仍是米制，filterBounds 因此查不到任何影像。
    所以必须用 pyproj 把 4 个角点转成经纬度，再建 Polygon。
  """
  tr = Transformer.from_crs(target_crs, "EPSG:4326", always_xy=True)
  minx, miny, maxx, maxy = bbox
  pts = [(minx, miny), (maxx, miny), (maxx, maxy), (minx, maxy)]
  ring = [list(tr.transform(x, y)) for x, y in pts]
  ring.append(ring[0])          # 多边形首尾闭合
  return ee.Geometry.Polygon([ring], geodesic=False)

def estimate_mb(width, height, n_bands, bytes_per_sample=4, ratio=1.8):
  """粗估文件大小（MB），只用于打印提示，不参与判断。"""
  raw = width * height * n_bands * bytes_per_sample
  return raw / ratio / 1e6

def download_direct(img,region,name):
  """先试直下：getDownloadURL，上限约 32 MB。失败会抛异常。"""
  import geemap
  out = Path.cwd() / f"{name}.tif"
  geemap.ee_export_image(
    img,filename=str(out),scale=res,crs=target_crs,
    region=region,file_per_band=False,
  )
  if not out.exists() or out.stat().st_size == 0:
    raise RuntimeError("直下没有生成有效文件")
  return out

def submit_drive(img,region,tf,name):
  """提交 Drive 导出任务，返回 task 对象。"""
  task = ee.batch.Export.image.toDrive(
    image=img,
    description=name,
    folder=drive_folder,
    fileNamePrefix=name,
    region=region,
    crs=target_crs,
    crsTransform=tf,          # crsTransform 与 scale 不能同时给
    maxPixels=max_pixels,
    fileFormat="GeoTIFF",
  )
  task.start()
  return task

def main():
  ee.Initialize()

  bbox, t, width, height = use_grid()
  print("整幅网格:", width, "x", height,
          " 像元≈ %.1f M" % (width * height / 1e6))

  if test_mode:
    bbox, tf, w, h = sub_grid(t, width, height, test_size_km)
    name = prefix + "_test"
    print("测试网格:", w, "x", h)
  else:
    tf = [t.a, t.b, t.c, t.d, t.e, t.f]
    w, h = width, height
    name = prefix

  region = to_region(bbox)
  print("region: UTM 矩形已转为经纬度多边形")
  print("crsTransform:", tf)
  img = build_image(region)

  est_mb = estimate_mb(w, h, len(bands))
  print("预计文件约 %.0f MB（直下上限约 32 MB）" % est_mb)

  if prefer_direct:
      try:
          out = download_direct(img, region, name)
          print("直下完成:", out)
          return                       # 直下成功，流程结束
      except Exception as e:
          print("直下失败，改走 Drive:", repr(e))
          partial = Path.cwd() / f"{name}.tif"
          if partial.exists():         # 清掉可能写了一半的残文件
              partial.unlink()
  task = submit_drive(img, region, tf, name)
  print("已提交 Drive 任务:", task.id)
  print("进度页: https://code.earthengine.google.com/tasks")

if __name__ == "__main__":
  main()