import geopandas as gpd
import numpy as np
from rasterio.transform import from_origin

target_crs = "EPSG:32649"
res = 10.0
aoi_path =  r"C:\Users\WYF18\Desktop\三上\自学\批量处理\area_enshi\Enshi_area.json"

aoi = gpd.read_file(aoi_path).to_crs(target_crs)

minx,miny,maxx,maxy = aoi.total_bounds
minx = np.floor(minx / res) * res
maxx = np.ceil(maxx / res) * res
miny = np.floor(miny / res) * res
maxy = np.ceil(maxy / res) * res

dst_transform = from_origin(minx,maxy,res,res)
dst_width = int(round((maxx - minx) / res))
dst_height = int(round((maxy - miny) / res))

print("目标像元",dst_transform)
print("目标宽度",dst_width)
print("目标高度",dst_height)