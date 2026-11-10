import geopandas as gpd
from shapely.geometry import box
from pathlib import Path

aoi = gpd.GeoDataFrame(
  {"name":["Enshi_area"]},
  geometry=[box(246033.78, 3221337.27, 464818.29, 3474661.79)],
  crs="EPSG:32649"
)


print("CRS:",aoi.crs)
print("Bounds:",aoi.total_bounds)

# 写出GeoJSON
out = Path(r"C:\Users\WYF18\Desktop\三上\自学\批量处理\area_enshi\Enshi_area.json")
aoi.to_file(out, driver="GeoJSON", encoding="utf-8")

print("写出",out)