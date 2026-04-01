# 机动车环保网数据爬虫

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

**一键爬取机动车环保网所有车辆数据**

[⬇️ 下载Windows版](../../releases/latest/download/JDCCrawler-windows.zip) • 
[⬇️ 下载Mac版](../../releases/latest/download/JDCCrawler-macos-latest.tar.gz) • 
[⬇️ 下载Linux版](../../releases/latest/download/JDCCrawler-ubuntu-latest.tar.gz)

</div>

---

## ✨ 特性

- ✅ **完整数据** - 爬取82个完整字段（基本信息+三电参数）
- ✅ **断点续传** - 支持中断后继续，不重复爬取
- ✅ **增量保存** - 每批次自动保存，避免数据丢失
- ✅ **自动导出** - 生成Excel和JSON两种格式
- ✅ **跨平台** - 支持Windows、macOS、Linux
- ✅ **绿色软件** - 无需安装Python，双击即用

---

## 🚀 快速开始

### 1. 下载对应版本

| 平台 | 下载链接 | 文件大小 |
|------|---------|---------|
| **Windows** | [JDCCrawler-windows.zip](../../releases/latest/download/JDCCrawler-windows.zip) | ~10MB |
| **macOS** | [JDCCrawler-macos-latest.tar.gz](../../releases/latest/download/JDCCrawler-macos-latest.tar.gz) | ~12MB |
| **Linux** | [JDCCrawler-ubuntu-latest.tar.gz](../../releases/latest/download/JDCCrawler-ubuntu-latest.tar.gz) | ~11MB |

### 2. 运行程序

**Windows:**
```bash
# 解压 zip 文件
# 双击 JDCCrawler.exe 运行
```

**Mac/Linux:**
```bash
# 解压 tar.gz 文件
chmod +x JDCCrawler
./JDCCrawler
```

### 3. 选择模式

```
选项:
1. 完整模式 - 爬取所有批次+详情页 (82个字段，非常慢)
2. 快速模式 - 仅爬取列表页 (7个字段，快速)
3. 测试模式 - 爬取单个批次测试 (385批次)
4. 继续上次中断的任务
5. 仅导出已有数据为Excel
```

**首次使用建议选择 "3. 测试模式"**

---

## 📂 数据文件位置

程序运行后，数据保存在程序同目录的 `data` 文件夹：

```
JDCCrawler/
├── JDCCrawler          ← 程序
└── data/               ← 所有数据在这里
    └── production_enhanced/
        ├── vehicles_complete_all.xlsx   ← 🎯 Excel表格
        ├── all_vehicles_complete.json   ← JSON数据
        └── crawler_*.log                ← 运行日志
```

---

## 📋 数据字段（82个）

### 基本信息（7个）
批次、燃料类型、公告编号、公告型号、车辆名称、生产企业、详情链接

### 生产企业信息（24个）
中文品牌、企业名称、生产地址、注册地址、法人代表、电话、传真等

### 车辆参数
车辆总质量、外形尺寸、最高车速、整备质量等

### 三电参数（13个）
- **电芯信息**: 电芯类型、电压、容量、生产企业
- **电池信息**: 电池容量、电量、BMS、组合方式
- **电机信息**: 电机型号、功率、转速、生产企业
- **电控系统**: 电控供应商、充电机、DC/DC等

---

## ⚡ 运行模式对比

| 模式 | 字段数 | 时间 | 适用场景 |
|------|--------|------|---------|
| **完整模式** | 82 | 3-5天 | 需要完整数据 |
| **快速模式** | 7 | 1-2小时 | 仅需要基本信息 |
| **测试模式** | 82 | 5分钟 | 测试验证 |

---

## 💡 使用技巧

### 断点续传
- 程序每次运行自动保存进度
- 中断后选择 "4. 继续上次" 即可
- 不会重复爬取已完成批次

### 数据导出
- 自动生成Excel文件
- 包含所有82个字段
- 格式化表格（蓝色表头、冻结首行）

---

## 🛠️ 从源码运行

```bash
# 安装依赖
pip install openpyxl

# 运行爬虫
python crawl_production_enhanced.py
```

---

## 📄 许可证

MIT License

---

## ⭐ Star History

如果这个项目对你有帮助，请给个Star支持！

<div align="center">

**Made with ❤️**

</div>
