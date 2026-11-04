import os
import ee
import geemap
ee.Initialize()

area = ee.Geometry.Rectangle([130.35,42.85,130.45,42.93])
start_date = '2025-01-01'
end_date = '2026-12-31'
collection =( 
    ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
    .filterDate(start_date, end_date)
    .filterBounds(area)
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
)


receive = collection.sort('CLOUDY_PIXEL_PERCENTAGE').first()
scene_id = receive.get("system:index").getInfo()
cloud = receive.get("CLOUDY_PIXEL_PERCENTAGE").getInfo()

if scene_id is None:
    raise ValueError(f"Scene ID: {scene_id}, Cloud Percentage: {cloud}%，没有找到合适的图像")

NDVI = receive.normalizedDifference(['B8', 'B4']).rename('YBU_NDVI')

scl = receive.select('SCL')
clear = (
  scl.neq(3)
  .And(scl.neq(8))
  .And(scl.neq(9))
  .And(scl.neq(10))
  .And(scl.neq(11))
)
ndvi_masked = NDVI.updateMask(clear)
out = os.path.abspath("C:\\Users\\WYF18\\Desktop\\三上\\自学\\first\\DVI\\YBU_NDVI.tif")
os.makedirs(os.path.dirname(out), exist_ok=True)
geemap.ee_export_image(
    ndvi_masked,
    filename = out,
    scale = 10,
    region = area,
)

print(f"珲春校区NDVI成功导出到{out}")