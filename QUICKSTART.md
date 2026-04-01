# 🚀 快速开始指南

## 一键启动

```bash
cd /Users/hackm/Applications/2026-jhoo/tram-inspection/jdcsww-crawler/
python3 crawl_production.py
```

选择 `1` 即可开始爬取所有批次(1-403)的纯电动车辆数据。

---

## 📊 你将得到

**输出文件**: `data/production/vehicles_all_batches.xlsx`

**包含字段**:
- ✅ 公告型号
- ✅ 批次
- ✅ 燃料类型 (纯电动)
- ✅ 生产企业
- ✅ 公告编号
- ✅ 车辆名称

**预计**:
- 车辆数量: ~12,000 辆
- 爬取时间: 1-2 小时
- 文件大小: 1-2 MB

---

## 🎯 核心特性

✅ **断点续传** - 中断可继续
✅ **增量保存** - 每批次自动保存
✅ **Excel导出** - 直接可用
✅ **自动重试** - 网络错误自动恢复

---

## ⚠️ 关于混合动力

**当前已实现**: 纯电动 (rylx='C')

**混合动力**: 需要确认参数代码
- 访问网站查看实际URL参数
- 确认后添加到 `fuel_types` 列表

详细说明: 见 [README_PRODUCTION.md](README_PRODUCTION.md)

---

## 📁 文件说明

| 文件 | 用途 |
|------|------|
| `crawl_production.py` | ⭐ 生产环境爬虫 (使用这个) |
| `full_data_crawler.py` | 测试爬虫 (已测试通过) |
| `data/production/` | 输出目录 |

---

## 🔄 断点续传

如果爬取中断:

```bash
python3 crawl_production.py
# 选择 3. 继续上次中断的任务
```

会自动从上次中断处继续。

---

## 📊 验证数据

```bash
# 查看爬取进度
python3 -c "
import json
with open('data/production/all_vehicles.json', 'r') as f:
    vehicles = json.load(f)
print(f'总计: {len(vehicles)} 辆')
"
```

---

## 💡 建议

1. **首次使用**: 可以先测试小范围(如批次400-403)
2. **生产运行**: 选择非网络高峰期
3. **数据备份**: 定期备份 `data/production/` 目录

---

**准备好了吗?**

```bash
python3 crawl_production.py
```

选择 `1`，开始爬取！
