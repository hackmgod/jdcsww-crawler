# 汽车公告数据爬虫

## 📁 目录结构

```
jdcsww-crawler/
├── crawl_production.py          ⭐ 生产环境爬虫（主要使用）
├── complete_data_crawler.py     📦 完整数据爬虫（参考版本）
│
├── README_PRODUCTION.md         📖 生产环境完整文档
├── READY_TO_START.md            🚀 快速开始指南
├── QUICKSTART.md                💡 使用说明
├── PROJECT_SUMMARY.md           📊 项目总结
│
├── data/                        💾 数据输出目录
│   ├── production/              生产数据
│   │   ├── all_vehicles.json
│   │   ├── crawler_state.json
│   │   └── vehicles_all_batches.xlsx
│   └── full_data/               测试数据
│
└── archive/                     📦 已归档的旧版本和测试文件
```

---

## 🚀 快速开始

### 一键启动

```bash
python3 crawl_production.py
```

选择 `1` - 爬取所有批次(1-403)

### 输出

- **Excel**: `data/production/vehicles_all_batches.xlsx`
- **JSON**: `data/production/all_vehicles.json`

---

## ✅ 功能特性

- ✅ 爬取所有批次(1-403)
- ✅ 纯电动 + 混合动力
- ✅ 断点续传
- ✅ Excel导出
- ✅ 自动重试

---

## 📖 文档

- [README_PRODUCTION.md](README_PRODUCTION.md) - 完整文档
- [READY_TO_START.md](READY_TO_START.md) - 快速开始
- [QUICKSTART.md](QUICKSTART.md) - 使用说明
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - 项目总结

---

**项目状态**: ✅ 可生产使用
**更新时间**: 2026-03-19
