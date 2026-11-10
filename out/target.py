'''
此步骤也是对影相进行预处理
通过规定统一的研究区坐标参考系和研究区范围
将目标影像处理到统一的研究区和规定的像元格网中
transform	-------这张栅格的左上角在哪、像元多大、有没有旋转？
width/height	---有多少行多少列？
'''
import geopandas as gpd
import numpy as np
from rasterio.transform import from_origin

def target(aoi_path, target_crs, res):
    
    aoi = gpd.read_file(aoi_path)
    if aoi.crs is None:                      # 没 CRS 就投影不了，先拦住
      raise ValueError("AOI 没有 CRS，请先在 QGIS 里定义投影")
    aoi = aoi.to_crs(target_crs)
    geom = aoi.geometry.union_all()

    minx,miny,maxx,maxy = aoi.total_bounds
    minx = np.floor(minx / res) * res
    maxx = np.ceil(maxx / res) * res
    miny = np.floor(miny / res) * res
    maxy = np.ceil(maxy / res) * res

    dst_transform = from_origin(minx,maxy,res,res)
    dst_width = int(round((maxx - minx) / res))
    dst_height = int(round((maxy - miny) / res))

    return geom, dst_transform, dst_width, dst_height

if __name__ == "__main__":
    # 单独运行 target.py 时用于检查；被 import 时不会执行
    AOI = r"C:\Users\WYF18\Desktop\三上\自学\批量处理\area_enshi\Enshi_area.json"
    geom, t, w, h = target(AOI, "EPSG:32649", 30.0)
    print("geom:", geom.geom_type)
    print("目标像元", t)
    print("size:", w, "x", h)