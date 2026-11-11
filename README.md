# GEE 影像获取与一体化预处理工具

一套可复现的遥感影像获取与预处理流水线：

**在 Google Earth Engine 取数 → 本地统一网格 → 自动去云/缩放/裁剪 → 输出 QGIS 可直接分析的多波段 GeoTIFF。**

代码不绑定具体研究区：换区域、换时段、换传感器，只需要改配置里的几个参数。

---

## 1. 它解决什么问题

| 痛点 | 传统做法 | 本仓库做法 |
| --- | --- | --- |
| 取数慢 | 逐景下载原始产品，几十个文件 | GEE 一次导出多波段影像 |
| 去云麻烦 | 本地写 QA 位运算，容易错 | GEE 端按 QA_PIXEL/SCL 掩膜，或本地统一处理 |
| 网格对不齐 | 每景各自裁剪、各自重采样 | `crsTransform` 锁定同一网格 |
| 格式不统一 | 有的 DN、有的反射率、有的单波段 | 自动识别并统一为 Float32 反射率 |
| 流程不可重复 | 手工点击、路径写死 | 改参数重跑，附 `manifest.csv` 记账 |

---

## 2. 两个核心脚本

| 脚本 | 角色 | 输入 | 输出 |
| --- | --- | --- | --- |
| `out/gee_export.py` | **云端取数** | 研究区 + 日期范围 | 多波段 GeoTIFF（Drive 或本地） |
| `out/preprocess_auto.py` | **本地一体化规整** | 多波段或单波段影像目录 | `*_done.tif` + `manifest.csv` |

辅助脚本：

| 脚本 | 作用 |
| --- | --- |
| `out/target.py` | 计算所有影像共用的目标网格（`transform`、`width`、`height`） |
| `out/area_out.py` | 由矩形范围生成研究区 GeoJSON（可选，也可直接用现成边界） |

---

## 3. 核心一：从 GEE 获取影像

### 3.1 处理链路

```text
研究区 GeoJSON
   │  本地计算目标网格（CRS + 分辨率 + 左上角）
   ▼
GEE 影像集合
   │  filterBounds / filterDate / 云量筛选
   ▼
逐像元去云（QA_PIXEL 位掩膜 或 SCL 类别掩膜）
   │
   ▼
时间中值合成（补洞）或取单景
   │
   ▼
地表反射率缩放（Landsat 2.75e-5/−0.2；Sentinel-2 1e-4）
   │
   ▼
Export.image.toDrive —— crsTransform 锁定网格
   │
   ├─ 小区域：先尝试直下（< 32 MB）
   └─ 失败：自动转 Drive 任务
```

### 3.2 为什么用 `crsTransform`

GEE 默认按自己的网格对齐。如果只给 `scale`，每次导出的原点可能差半个像元，多景之间就叠不齐。

本仓库的做法是：**本地先用 `target.py` 算出 6 个仿射参数，再原样传给 GEE**。

```python
crsTransform = [xres, 0, x0, 0, -yres, y0]
```

这样 GEE 导出的像元和本地网格完全一致，后续处理几乎不用重投影。

> 注意：`crsTransform` 与 `scale` 互斥，不能同时传。

### 3.3 直下优先，失败转 Drive

GEE 的同步下载（`getDownloadURL`）单次上限约 32 MB，全州/全省尺度必然超限。

脚本的策略是：

```python
if prefer_direct:
    try:
        download_direct(...)   # 小区域几十秒拿到
        return
    except Exception:
        # 超限、超时、网络中断都走这里
        submit_drive(...)      # 提交异步任务
```

输出时会明确打印：

```text
预计文件约 2 MB（直下上限约 32 MB）
直下完成: ...
```

或

```text
预计文件约 274 MB（直下上限约 32 MB）
直下失败，改走 Drive: ...
已提交 Drive 任务: ...
```

### 3.4 关键参数

| 参数 | 作用 | 建议 |
| --- | --- | --- |
| `collection` | GEE 数据集 | Landsat 9：`LANDSAT/LC09/C02/T1_L2` |
| `bands` | 导出波段 | NDVI 用红 + 近红外 |
| `start, end` | 时间范围 | 单季 3 个月，避免跨年混物候 |
| `cloud_pct` | 整景云量阈值 | 中值合成可放宽到 40 或 `None` |
| `composite` | `"median"` 合成 / `"single"` 单景 | 州级用 median |
| `scale_in_gee` | 是否云端缩放 | 保持 `True` |
| `prefer_direct` | 先直下再回退 | 保持 `True` |
| `crs` / `crsTransform` | 输出坐标系与网格 | 由本地 `target.py` 给出 |

---

## 4. 核心二：一体化本地预处理

`out/preprocess_auto.py` 会**逐景判断输入类型**，自动选择处理路径。

### 4.1 自动识别规则

| 判断项 | 依据 | 处理 |
| --- | --- | --- |
| 掩膜 | 波段名含 `QA_PIXEL` | Landsat 位掩膜（bit1–5） |
| | 波段名含 `SCL` | Sentinel-2 类别掩膜 |
| | 都没有 | 视为云端已去云，跳过 |
| 缩放 | 浮点数据 | 已是反射率，不缩放 |
| | uint16 + `SR_B*` | Landsat DN → 反射率 |
| | uint16 + `B4`/`B8` | Sentinel-2 DN → 反射率 |
| 输入形态 | 多波段文件 | 直接处理 |
| | 单波段文件 | 按文件名前缀分组，自动堆叠 |

### 4.2 单波段自动堆叠

同一景的逐波段文件，文件名前缀相同即可识别：

```text
<scene>_SR_B1.TIF   ┐
<scene>_SR_B2.TIF   │  自动分组
<scene>_SR_B4.TIF   ├→ 堆叠成一个多波段
<scene>_QA_PIXEL.TIF┘  QA 当掩膜，不进输出
```

不需要 `gdalbuildvrt`，也不需要手工合并。

### 4.3 统一输出

所有输出都满足：

- 同一 CRS、同一 `transform`、同一宽高；
- `Float32`，`nodata = NaN`；
- Deflate 压缩 + 分块（tiled）；
- 每景一行 `manifest.csv`：场景、来源、输出、波段数、缩放方式、掩膜方式、有效率、耗时、错误。

### 4.4 输出命名与防覆盖

```text
<scene>_gee_done.tif     # 无需缩放、无需掩膜（已处理产品）
<scene>_raw_done.tif     # 需要缩放或掩膜（原始产品）
<scene>_gee_v2_done.tif  # 已存在且允许覆盖时自动加版本号
```

- `skip_existing = True`：已存在则跳过；
- `skip_existing = False`：生成 `_v2`、`_v3`，**不覆盖原文件**；
- `dry_run = True`：只打印识别结果与预计输出名，不实际处理。

---

## 5. Fork 之后怎么用

### 5.1 前置条件

- 一个能登录 Google Earth Engine 的 Google 账号；
- 能访问 Google Drive（大区域导出必需）；
- Python 3.9+，建议 conda 环境。

### 5.2 拉取与建环境

```bash
git clone <your-fork-url>
cd <repo>

conda create -n geoai python=3.11 -y
conda activate geoai
pip install rasterio geopandas pyproj numpy earthengine-api geemap
```

首次使用 GEE 需要授权：

```bash
earthengine authenticate
```

### 5.3 准备研究区

任意 GeoJSON / Shapefile 都可以，坐标系不限（脚本内部会 `to_crs`）：

```text
data/aoi/study_area.geojson
```

如果只有矩形范围，改 `out/area_out.py` 里的 `BBOX` 生成即可。

### 5.4 选择目标坐标系与分辨率

`target_crs` 按研究区所在 UTM 带选择：

```text
zone = int((lon + 180) / 6) + 1
北半球：EPSG = 32600 + zone
南半球：EPSG = 32700 + zone
```

分辨率一般用传感器原生值：Landsat 30 m，Sentinel-2 10 m。

### 5.5 先验证网格

```bash
python out/target.py
```

确认打印的宽高与预期量级一致（太大意味着内存会吃紧）。

### 5.6 取数

编辑 `out/gee_export.py` 顶部配置：

```python
aoi_path = Path("data/aoi/study_area.geojson")
target_crs = "EPSG:326xx"        # 按研究区所在带
res = 30.0
collection = "LANDSAT/LC09/C02/T1_L2"
bands = ["SR_B4", "SR_B5"]
start, end = "YYYY-MM-DD", "YYYY-MM-DD"
test_mode = True                 # 先导中心 20 km 小方块
```

```bash
python out/gee_export.py
```

小区域会直接下载；大区域会提交 Drive 任务，去 Tasks 页面等待完成后下载。

### 5.7 本地预处理

编辑 `out/preprocess_auto.py` 顶部：

```python
input_dir = Path("data/raw")        # GEE 下载或原始产品所在目录
out_dir   = Path("data/processed")
aoi_path  = Path("data/aoi/study_area.geojson")
```

先看识别结果：

```python
dry_run = True
```

```bash
python out/preprocess_auto.py
```

输出类似：

```text
发现 2 景:
  - <scene_a> [multi]: SR_B4, SR_B5
  - <scene_b> [single]: SR_B1..SR_B5, QA_PIXEL
  → <scene_a>: 来源=gee, 缩放=none, 掩膜=无
  → <scene_b>: 来源=raw, 缩放=landsat, 掩膜=landsat
```

确认无误后改 `dry_run = False`，先 `max_scenes = 1` 跑一景，再放开全量。

### 5.8 在 QGIS 里使用

把 `data/processed/*_done.tif` 拖进 QGIS：

- 2 波段（红、近红外）→ 栅格计算器算 NDVI；
- 5 波段（SR_B1–B5）→ 先确认波段顺序，再做指数或分类；
- 值域应为约 −0.2 ~ 1.0（反射率），若看到 0–10000 说明缩放没生效。

---

## 6. 换研究区 / 换传感器

### 6.1 换研究区

只改三处：

```text
aoi_path      研究区文件
target_crs    新区域所在 UTM 带
prefix        输出文件名前缀
```

其余参数与地理位置无关。

### 6.2 换传感器

| 项 | Landsat 9 | Sentinel-2 |
| --- | --- | --- |
| collection | `LANDSAT/LC09/C02/T1_L2` | `COPERNICUS/S2_SR_HARMONIZED` |
| 波段 | `SR_B4`、`SR_B5` | `B4`、`B8` |
| 云掩膜 | `QA_PIXEL` 位 1–5 | `SCL` ∈ {3,8,9,10,11} |
| 缩放 | `×2.75e-5 − 0.2` | `×1e-4` |
| 原生分辨率 | 30 m | 10 m |

`preprocess_auto.py` 会根据波段名和数据类型自动判断，一般不用改代码；识别不准时用 `scale_override` / `mask_override` 强制指定。

---

## 7. 目录结构（建议）

```text
repo/
├─ out/
│  ├─ area_out.py
│  ├─ target.py
│  ├─ gee_export.py
│  └─ preprocess_auto.py
├─ data/
│  ├─ aoi/            # 研究区矢量
│  ├─ raw/            # GEE 下载或原始产品
│  └─ processed/      # *_aligned.tif、manifest.csv
├─ .gitignore
└─ README.md
```

大文件（`*.tif`、`*.vrt`）不应提交到 Git。

---

## 8. 参数速查

| 参数 | 文件 | 说明 |
| --- | --- | --- |
| `target_crs` | 两个主脚本 | 目标 CRS |
| `res` | 两个主脚本 | 目标分辨率 |
| `collection` / `bands` | `gee_export.py` | 数据源与波段 |
| `start` / `end` | `gee_export.py` | 时间范围 |
| `cloud_pct` | `gee_export.py` | 整景云量阈值 |
| `composite` | `gee_export.py` | 合成方式 |
| `prefer_direct` | `gee_export.py` | 直下优先，失败转 Drive |
| `test_mode` | `gee_export.py` | 小方块试跑 |
| `dry_run` | `preprocess_auto.py` | 只识别不处理 |
| `scale_override` / `mask_override` | `preprocess_auto.py` | 强制缩放/掩膜方式 |
| `skip_existing` | `preprocess_auto.py` | 跳过或生成新版本 |
| `recursive` | `preprocess_auto.py` | 是否扫描子目录 |

---

## 9. 常见问题

| 现象 | 原因 | 处理 |
| --- | --- | --- |
| `CRSError: no database context` | PROJ 数据路径冲突 | 把 `PROJ_LIB` 指向当前环境的 `share/proj` |
| `filterBounds` 查到 0 景 | 用 UTM 坐标直接构造 GEE 几何 | 先转经纬度再建 `Polygon` |
| 直下报 `download too large` | 超过 32 MB | 脚本会自动转 Drive |
| 值域约 −0.2 且几乎不变 | 反射率被缩放了两次 | 关掉本地缩放，或改用 `preprocess_auto.py` |
| 输出文件特别大 | 源数据是 Float64 | 本地输出已转 Float32，约为源的一半 |
| 多波段文件无法识别掩膜 | 文件没有波段描述（如旧 VRT） | 改用单波段文件，或指定 `assume_mask_last` + `scale_override` |
| NDVI 全 0 / 全 NaN | 波段顺序或 nodata 处理有误 | 先看原图与波段统计 |

---

## 10. 已知限制

1. 研究区默认按外接矩形处理，若用行政边界需自行替换 AOI 并确认面积；
2. 单景覆盖范围有限，跨路径/行时建议用中值合成补齐；
3. 未做地形校正与 BRDF 归一化，山区结果会有坡向偏差；
4. 云边缘与薄云可能残留；
5. 未做面积加权统计，边界像元按中心判断；
6. GEE 导出网格可能比目标网格多 1–3 行/列，本地预处理会重投影回标准网格。

---

## 11. 说明

- 本仓库只包含方法代码，不含个人数据与研究区坐标；
- 配置中的路径请改成你自己机器上的相对路径；
- 不要把 `.env`、密钥、账号信息、个人目录写进仓库。
