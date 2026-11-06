import json
import numpy as np
import rasterio

path = r"C:\Users\WYF18\Desktop\三上\自学\first\NDVI\YBU_NDVI.tif"

def get_ndvi_stats():
    with rasterio.open(path) as src:
        data = src.read(1,masked=True)
        valid =data.compressed()  # 获取有效数据（非掩膜区域）
        total =data.size  # 总像素数
        valid_count = valid.size  # 有效像素数

        if valid_count == 0:
            raise ValueError("没有有效的NDVI数据，请检查输入影像。")

        return {
            "crs": str(src.crs),
            "transform": [float(v) for v in src.transform],
            "bounds": [float(v) for v in src.bounds],
            "res": [float(src.res[0]), float(src.res[1])],
            "width": src.width,
            "height": src.height,
            "mean": float(np.mean(valid)),
            "std": float(np.std(valid)),
            "min": float(np.min(valid)),
            "max": float(np.max(valid)),
            "total_pixels": int(total),
            "valid_pixels": int(valid_count),
            "valid_percentage": float((valid_count / total) * 100)
        }

def main() -> None:
    stats = get_ndvi_stats()
    print(json.dumps(stats, indent=2, ensure_ascii=False))  # 输出统计信息为JSON格式

    with open("C:\\Users\\WYF18\\Desktop\\三上\\自学\\first\\NDVI\\ndvi_stats.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
