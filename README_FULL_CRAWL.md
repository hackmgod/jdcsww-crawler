# 全量新能源汽车爬虫 - 34种类型 × 403批次

## 🎯 任务目标

爬取**所有34种新能源汽车类型**的**全部403个批次**数据。

## 📊 任务规模

```
┌──────────────────────────────────────┐
│ 任务统计                              │
├──────────────────────────────────────┤
│ 车辆类型: 34 种                       │
│ 批次范围: 1-403                       │
│ 总任务数: 13,702 次                   │
│ 预计时间: 76 小时 (3.2 天)            │
│ 预计数据量: ~411,060 辆车             │
└──────────────────────────────────────┘
```

## 🚀 快速开始

### **方式1：使用快速启动脚本（推荐）**

```bash
cd /Users/hackm/Applications/2026-jhoo/tram-inspection/jdcsww-crawler

# 运行交互式启动脚本
./quick_start.sh
```

### **方式2：直接运行**

```bash
# 查看帮助
python3 crawl_new_energy_full.py --help

# 运行全部（支持断点续传）
python3 crawl_new_energy_full.py

# 指定批次范围
python3 crawl_new_energy_full.py --start-batch 300 --end-batch 403

# 从头开始
python3 crawl_new_energy_full.py --no-resume
```

### **方式3：分批执行（最推荐）**

```bash
# 第1天：批次 1-150（预计28小时）
python3 crawl_new_energy_full.py --start-batch 1 --end-batch 150

# 第2天：批次 151-300（预计28小时）
python3 crawl_new_energy_full.py --start-batch 151 --end-batch 300

# 第3天：批次 301-403（预计20小时）
python3 crawl_new_energy_full.py --start-batch 301 --end-batch 403
```

## 📂 文件说明

### **核心文件**

| 文件名 | 说明 |
|--------|------|
| `crawl_new_energy_full.py` | 主爬虫程序 |
| `FULL_CRAWL_PLAN.md` | 详细执行方案文档 |
| `quick_start.sh` | 快速启动脚本 |

### **数据目录**

```
data/full_new_energy_34types/
├── crawler_state.json          # 爬取状态（断点续传）
├── crawler_20260409_112049.log  # 运行日志
├── vehicles_20260409_183022.json # 最终数据
└── failed_tasks.json           # 失败任务记录
```

## 🔍 34种车辆类型清单

### **纯电动系列（15种）**
1. 纯电动汽车
2. 纯电动客车
3. 纯电动救护车
4. 纯电动载货车
5. 纯电动洒水车
6. 纯电动教练车
7-14. 换电式纯电动系列（轿车/自卸汽车/厢式运输车等）
15. 两用燃料汽车

### **混合动力系列（4种）**
16. 混合动力电动汽车
17. 插电式混合动力汽车
18. 增程式混合动力汽车
19. 燃料式电池汽车

### **插电式混合动力专用车型（14种）**
20-33. 各种插电式混合动力专用车型
（冷藏车/宣传车/清障车/扫路车/检测车/救护车/运钞车/房车/城市客车/垃圾车/牵引车/载货车/汽车起重机/厢式运输车/混凝土泵车/绿化喷洒车/多用途乘用车/仓栅式运输车/混凝土搅拌运输车/自卸汽车等）

## 📊 监控进度

### **查看日志**

```bash
# 实时查看日志
tail -f data/full_new_energy_34types/crawler_*.log

# 查看最近100行
tail -100 data/full_new_energy_34types/crawler_*.log
```

### **查看状态**

```bash
# 查看JSON状态文件
cat data/full_new_energy_34types/crawler_state.json | python3 -m json.tool
```

### **使用监控脚本**

```bash
# 运行实时监控（另开终端）
python3 monitor.py
```

## ⚠️ 注意事项

### **1. 网络安全**
- ⚠️ 避免高并发请求（已设置随机延迟）
- ⚠️ 如果被封禁，等待24小时后重试
- ⚠️ 不要同时运行多个实例

### **2. 断点续传**
- ✅ 程序会自动保存进度
- ✅ 意外中断后重新运行会自动跳过已完成的任务
- ✅ 状态文件：`data/full_new_energy_34types/crawler_state.json`

### **3. 数据验证**
- ✅ 定期检查数据文件大小
- ✅ 验证JSON文件格式是否正确
- ✅ 检查是否有重复数据

## 🛠️ 故障排除

### **问题：被网站封禁**

```bash
# 停止爬虫
pkill -f crawl_new_energy_full

# 等待24小时
# 或者更换网络环境
```

### **问题：程序崩溃**

```bash
# 查看错误日志
tail -100 data/full_new_energy_34types/crawler_*.log

# 重新运行（会自动断点续传）
python3 crawl_new_energy_full.py
```

### **问题：重试失败任务**

```bash
# 运行重试脚本
python3 retry_failed.py
```

## 📈 预期结果

完成后的数据文件：
- **格式：** JSON
- **大小：** 500MB - 1GB
- **记录数：** 40万+ 辆车
- **字段：** 83个完整字段

## 📞 技术支持

查看详细文档：`FULL_CRAWL_PLAN.md`

---

**祝你好运！🚀**
