# 汽车公告数据爬虫项目

## 📁 项目结构

```
jdcsww-crawler/
├── README.md              # 基础说明
├── USAGE.md               # 详细使用说明
├── README_PROJECT.md      # 本文件 - 项目总览
├── requirements.txt       # 基础依赖
├── requirements_full.txt  # 完整依赖（含Selenium）
├── config.py             # 配置文件
│
├── final_crawler.py      # ⭐ 推荐：基础爬虫
├── advanced_crawler.py   # ⭐ 推荐：高级爬虫（多批次）
├── jdcsww_crawler.py     # 完整版爬虫（需要安装依赖）
├── test_crawler.py       # 测试版爬虫
├── analyze_page.py       # 页面分析工具
│
├── install_selenium.sh   # Selenium安装脚本
│
└── data/                 # 数据输出目录
    ├── vehicle_list_batch403.json
    ├── list_page_sample.html
    └── detail_page_sample.html
```

## 🚀 快速开始

### 1️⃣ 基础使用（推荐）

```bash
# 爬取单个批次
python3 final_crawler.py

# 爬取多个批次
python3 advanced_crawler.py
```

### 2️⃣ 自定义配置

编辑 `advanced_crawler.py`:

```python
crawler.run_multiple_batches(
    start_batch=403,  # 起始批次
    end_batch=400,    # 结束批次
    delay=5           # 请求间隔（秒）
)
```

## 📊 数据说明

### 已爬取数据字段

- ✅ 车辆名称
- ✅ 公告编号
- ✅ 公告型号
- ✅ 发布时间
- ✅ 公告批次
- ✅ 轴数
- ✅ 外形尺寸
- ✅ 货箱尺寸
- ✅ 额定载质量
- ✅ 生产企业
- ✅ 详情链接

## 📈 测试结果

```
======================================================================
汽车公告数据爬虫
======================================================================
正在获取批次 403 的列表页...
解析到 30 条车辆信息

  [1] 欧曼牌换电式纯电动半挂牵引车
  [2] 乐洁牌纯电动洗扫车
  [3] 豪沃牌换电式纯电动牵引汽车
  ... (共30条)

✓ 数据已保存到: data/vehicle_list_batch403.json
✓ 列表数据: 30 条
======================================================================
✓ 爬取完成！
======================================================================
```

## 🔧 技术实现

### 反爬虫处理

- ✅ 模拟真实浏览器 User-Agent
- ✅ 使用合理的请求延迟
- ✅ 支持多批次分批爬取

### 详情页处理

详情页有更强的反爬虫机制，需要使用 Selenium：

```python
# 安装依赖
pip3 install selenium --user
brew install chromedriver

# 修改配置
crawler.run(
    batch=403,
    fetch_details=True,  # 启用详情页
    detail_limit=10
)
```

## 📝 示例数据

```json
{
  "序号": 1,
  "车辆名称": "欧曼牌换电式纯电动半挂牵引车",
  "详情链接": "https://www.jdcsww.com/qcggdetail?bh=SV2026031300004",
  "公告编号": "SV2026031300004",
  "公告型号": "BJ4189EVADF-01",
  "发布时间": "2026-02-09",
  "公告批次": "403",
  "轴数": "2",
  "车辆外形长宽高(mm)": "6665,6265,5905...",
  "生产企业": "北京福田戴姆勒汽车有限公司",
  "额定载质量(KG)": "4170,4105,4570,4505"
}
```

## ⚠️ 注意事项

1. **访问频率**: 建议每批次间隔5-10秒
2. **数据用途**: 仅供学习研究
3. **商业用途**: 请联系官方购买数据接口
4. **批次范围**: 当前最新403批次（2026/03/13）

## 📞 官方联系方式

- 网站：https://www.jdcsww.com
- 微信：19828933515
- QQ：965676271

## 🛠️ 文件说明

### 推荐使用

- `final_crawler.py` - 单批次爬取，最稳定
- `advanced_crawler.py` - 多批次爬取，功能强大

### 开发测试

- `test_crawler.py` - 测试网络连接
- `analyze_page.py` - 分析页面结构

### 完整功能

- `jdcsww_crawler.py` - 完整版，支持详情页（需要Selenium）

## 📖 更多文档

- [基础说明](README.md)
- [详细使用指南](USAGE.md)

## ✨ 功能特性

- ✅ 无需安装额外依赖（使用标准库）
- ✅ 支持多批次批量爬取
- ✅ 自动保存JSON格式数据
- ✅ 详细的爬取进度显示
- ✅ 完善的错误处理
- ✅ 数据统计功能

## 🎯 下一步

1. 运行 `python3 final_crawler.py` 测试
2. 查看 `data/vehicle_list_batch403.json` 数据
3. 根据需要修改批次号重新爬取
4. 分析数据或导入数据库

---

📍 项目路径: `tram-inspection/jdcsww-crawler/`
📅 创建时间: 2026-03-18
👤 作者: Claude
