# 获取详情页和图片完整指南

## 📋 你需要的数据

根据你提供的图片，详情页包含以下完整信息：

### 1. 基本车辆信息
- 车辆名称、型号、批次
- 生产企业、发布时间
- 外形尺寸、整备质量等

### 2. 三电系统参数（重要！）
- **电芯参数**：电芯类型、电压、容量、生产企业
- **电池信息**：电池容量、电压、电量、质量、BMS
- **电机信息**：电机型号、类型、峰值功率、生产企业
- **电控系统**：电控供应商、充电机型号等

### 3. 车辆图片
- 车辆外观照片
- 可能有多张不同角度的图片

## 🚀 使用方法

### 步骤1：安装依赖

```bash
# 进入项目目录
cd tram-inspection/jdcsww-crawler/

# 运行安装脚本
./install_selenium.sh
```

或者手动安装：

```bash
# 安装 Python 包
pip3 install selenium webdriver-manager --user

# 安装 ChromeDriver (macOS)
brew install chromedriver

# 如果没有 brew，手动下载：
# 1. 访问 https://chromedriver.chromium.org/
# 2. 下载对应版本
# 3. 移动到 /usr/local/bin/chromedriver
# 4. chmod +x /usr/local/bin/chromedriver
```

### 步骤2：运行爬虫

```bash
# 运行完整版爬虫（获取详情页和图片）
python3 selenium_crawler.py
```

### 步骤3：查看结果

爬虫会生成以下文件：

```
data/
├── vehicle_list_batch403.json          # 列表数据
├── vehicle_full_data_batch403.json     # 完整数据（含详情）
└── vehicle_images/                     # 车辆图片目录
    ├── SV2024081608897_华神牌纯电动载货汽车_1.jpg
    ├── SV2024081608897_华神牌纯电动载货汽车_2.jpg
    └── ...
```

## 📊 数据结构

### 完整数据示例

```json
{
  "序号": 1,
  "批次": 403,
  "车辆名称": "华神牌纯电动载货汽车",
  "公告编号": "SV2024081608897",
  "公告型号": "DFD5040CCYLBEV",
  "发布时间": "2024-08-16",
  "生产企业": "东风汽车集团有限公司",

  "电芯参数_动力类型": "纯电动",
  "电芯参数_电芯类型": "磷酸铁锂",
  "电芯参数_电芯型号": "CB8L0",
  "电芯参数_电芯电压(v)": "3.22",
  "电芯参数_电芯容量(Ah)": "160",
  "电芯参数_电芯生产企业": "宁德时代新能源科技股份有限公司",

  "电池信息_电池容量(Ah)": "160",
  "电池信息_电池电压(v)": "540.96",
  "电池信息_电池电量(KWh)": "86.554",
  "电池信息_电池质量(kg)": "598",
  "电池信息_电池管理系统BMS": "宁德时代新能源科技股份有限公司",

  "电机信息_电机型号": "TZ228XS-HSM1151",
  "电机信息_电机类型": "永磁同步电机",
  "电机信息_电机冷却方式": "液冷",
  "电机信息_电机峰值功率": "115/12000/350",
  "电机信息_电机生产企业": "东风华神汽车有限公司",

  "电控系统_电控供应商": "东风华神汽车有限公司",

  "车辆图片": [
    "data/vehicle_images/SV2024081608897_华神牌纯电动载货汽车_1.jpg"
  ],

  "详情页URL": "https://www.jdcsww.com/qcggdetail?bh=SV2024081608897"
}
```

## ⚙️ 自定义配置

编辑 `selenium_crawler.py` 的 `main()` 函数：

```python
crawler.run(
    batch=403,          # 批次号
    detail_limit=5      # 获取详情页的数量（None=全部）
)
```

## 🔧 故障排除

### 问题1: Selenium 未安装

```bash
pip3 install selenium --user
```

### 问题2: ChromeDriver 版本不匹配

```bash
# 卸载旧版本
brew uninstall chromedriver

# 重新安装
brew install chromedriver
```

### 问题3: 详情页被拦截

- 确保先访问主页再访问详情页（已实现）
- 增加延迟时间
- 使用非无头模式测试（去掉 `--headless`）

### 问题4: 图片下载失败

- 检查网络连接
- 检查图片URL是否有效
- 查看错误信息中的URL

## 📈 数据分析示例

```python
import json

# 读取完整数据
with open('data/vehicle_full_data_batch403.json', 'r', encoding='utf-8') as f:
    vehicles = json.load(f)

# 统计电芯供应商
cell_suppliers = {}
for v in vehicles:
    supplier = v.get('电芯参数_电芯生产企业', '未知')
    cell_suppliers[supplier] = cell_suppliers.get(supplier, 0) + 1

print("电芯供应商统计:")
for supplier, count in sorted(cell_suppliers.items(), key=lambda x: x[1], reverse=True):
    print(f"  {supplier}: {count} 辆")

# 统计电池电量
battery_capacities = []
for v in vehicles:
    capacity = v.get('电池信息_电池电量(KWh)')
    if capacity:
        try:
            battery_capacities.append(float(capacity))
        except:
            pass

if battery_capacities:
    avg_capacity = sum(battery_capacities) / len(battery_capacities)
    print(f"\n平均电池电量: {avg_capacity:.2f} kWh")
```

## 📞 技术支持

如果遇到问题：

1. 查看错误信息
2. 检查 Selenium 和 ChromeDriver 版本
3. 查看生成的 JSON 文件确认数据
4. 检查图片目录确认图片下载

## ⚠️ 注意事项

1. **访问频率**：详情页访问较慢，建议每条间隔3-5秒
2. **网络要求**：需要稳定网络连接
3. **磁盘空间**：图片会占用一定空间
4. **数据用途**：仅供学习研究使用

---

**项目路径**: `tram-inspection/jdcsww-crawler/`
**爬虫文件**: `selenium_crawler.py`
**图片目录**: `data/vehicle_images/`
