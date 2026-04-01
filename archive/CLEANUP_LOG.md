# 目录清理说明

## 清理时间
2026-03-19

## 保留文件（核心文件）

### 爬虫程序
- ✅ `crawl_production.py` - 生产环境爬虫（主要使用）
- ✅ `complete_data_crawler.py` - 完整数据爬虫（参考版本）

### 文档
- ✅ `README.md` - 主文档
- ✅ `README_PRODUCTION.md` - 生产环境完整文档
- ✅ `READY_TO_START.md` - 快速开始指南
- ✅ `QUICKSTART.md` - 使用说明
- ✅ `PROJECT_SUMMARY.md` - 项目总结

### 数据目录
- ✅ `data/` - 数据输出目录

---

## 已归档文件（archive/目录）

### 测试文件
- `test_fuel_types.py` - 燃料类型测试
- `test_hybrid.py` - 混合动力测试
- `test_hybrid_multiple.py` - 多批次混合动力测试
- `test_both_fuel_types.py` - 双燃料类型测试
- `test_crawler.py` - 爬虫测试
- `batch_test.py` - 批次测试
- `find_hybrids.py` - 查找混合动力
- `analyze_page.py` - 页面分析

### 旧版本爬虫
- `session_crawler.py` - 会话爬虫 v1
- `session_crawler_v2.py` - 会话爬虫 v2
- `session_crawler_v3.py` - 会话爬虫 v3
- `jdcsww_crawler.py` - 原始爬虫
- `advanced_crawler.py` - 高级爬虫
- `complete_crawler.py` - 完整爬虫
- `final_crawler.py` - 最终爬虫
- `undetected_crawler.py` - 反检测爬虫
- `selenium_crawler.py` - Selenium爬虫
- `selenium_crawler_v2.py` - Selenium爬虫v2
- `full_data_crawler.py` - 全量数据爬虫

### 辅助工具
- `generate_links.py` - 链接生成工具
- `generate_report.py` - 报告生成工具
- `manual_data_helper.py` - 手动数据辅助工具

### 安装相关
- `install_selenium.sh` - Selenium安装脚本
- `install_selenium_guide.md` - 安装指南
- `requirements.txt` - Python依赖
- `requirements_full.txt` - 完整依赖

### 旧文档
- `README_COMPLETE.md` - 完整项目README
- `README_PROJECT.md` - 项目README
- `DETAIL_GUIDE.md` - 详细指南
- `USAGE.md` - 使用说明
- `config.py` - 配置文件

---

## 已删除

- `__pycache__/` - Python缓存目录
- `venv/` - 虚拟环境目录

---

## 清理后目录结构

```
jdcsww-crawler/
├── crawl_production.py          ⭐ 生产爬虫
├── complete_data_crawler.py     📦 参考爬虫
├── README.md                    📖 主文档
├── README_PRODUCTION.md         📖 完整文档
├── READY_TO_START.md            🚀 快速开始
├── QUICKSTART.md                💡 使用说明
├── PROJECT_SUMMARY.md           📊 项目总结
├── data/                        💾 数据目录
│   ├── production/              生产数据
│   └── full_data/               测试数据
└── archive/                     📦 归档文件
    ├── 旧版本爬虫/
    ├── 测试文件/
    ├── 辅助工具/
    └── 旧文档/
```

---

## 说明

所有已归档文件都保存在 `archive/` 目录中，如需恢复可以随时从该目录中复制回来。

核心功能完全保留，可以正常使用：
```bash
python3 crawl_production.py
```
