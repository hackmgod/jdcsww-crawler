# 使用说明

## 快速开始

### 1. 运行基础爬虫（列表数据）

```bash
python3 final_crawler.py
```

这将爬取第403批次的纯电动车辆列表数据，保存到 `data/vehicle_list_batch403.json`

### 2. 自定义批次

编辑 `final_crawler.py` 的 `main()` 函数：

```python
crawler.run(
    batch=402,  # 修改批次号
    fetch_details=False,
    detail_limit=3
)
```

### 3. 爬取详情页（需要Selenium）

```python
crawler.run(
    batch=403,
    fetch_details=True,  # 启用详情页爬取
    detail_limit=10      # 爬取前10条详情
)
```

## 安装 Selenium（可选）

如果要爬取详情页，需要安装 Selenium：

```bash
# 安装 Python 包
pip3 install selenium --user

# 安装 ChromeDriver (macOS)
brew install chromedriver
```

## 数据字段说明

### 列表数据字段

- `序号`: 车辆在列表中的序号
- `车辆名称`: 完整车辆名称
- `详情链接`: 详情页URL
- `公告编号`: 唯一标识符
- `公告型号`: 车辆型号
- `发布时间`: 公告发布日期
- `公告批次`: 公告批次号
- `轴数`: 车辆轴数
- `车辆外形长宽高(mm)`: 外形尺寸
- `车辆生产企业名称`: 生产厂家
- `额定载质量(KG)`: 额定载重量
- `货箱长宽高(mm)`: 货箱尺寸

## 示例代码

### 读取并分析数据

```python
import json

# 读取数据
with open('data/vehicle_list_batch403.json', 'r', encoding='utf-8') as f:
    vehicles = json.load(f)

# 统计
print(f"总共 {len(vehicles)} 辆车")

# 按生产企业统计
companies = {}
for v in vehicles:
    company = v.get('生产企业', '未知')
    companies[company] = companies.get(company, 0) + 1

for company, count in sorted(companies.items(), key=lambda x: x[1], reverse=True):
    print(f"{company}: {count} 辆")
```

## 批次范围

当前最新批次：403 (2026/03/13)

历史批次：402, 401, 400, 399...

可以修改批次号爬取不同批次的数据。

## 注意事项

1. **访问频率**: 网站可能限制访问频率，建议批次间延迟
2. **详情页**: 详情页有反爬虫，需要使用 Selenium
3. **数据用途**: 仅供学习研究，商业用途请联系官方

## 故障排除

### 问题1: 找不到车辆信息
- 检查批次号是否正确
- 检查网络连接

### 问题2: 详情页被拦截
- 需要安装 Selenium 和 ChromeDriver
- 检查 ChromeDriver 版本是否匹配

### 问题3: 导入错误
```bash
# 使用虚拟环境
python3 -m venv venv
source venv/bin/activate
pip install -r requirements_full.txt
```

## 联系方式

官方网站：https://www.jdcsww.com
微信：19828933515
