import geopandas as gpd
from shapely.geometry import box
from pathlib import Path

aoi = gpd.GeoDataFrame(
  {"name":["Enshi_area"]},
  geometry=[box(220452.41,3209210.97,482901.30,3487908.00)],
  crs="EPSG:32649"
)

print(aoi)
print("CRS:",aoi.crs)
print("Bounds:",aoi.total_bounds)

# 写出GeoJSON
aoi.to_file(Path(r"C:\Users\WYF18\Desktop\三上\自学\批量处理\area_enshi\Enshi_area.json"), driver="GeoJSON", encoding="utf-8")