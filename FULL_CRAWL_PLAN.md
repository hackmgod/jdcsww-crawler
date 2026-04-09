# 全量新能源汽车爬虫 - 详细执行方案

## 📊 任务规模

```
┌─────────────────────────────────────────────────────┐
│ 任务规模统计                                         │
├─────────────────────────────────────────────────────┤
│ 车辆类型: 34 种                                      │
│ 批次范围: 1-403                                      │
│ 总任务数: 13,702 次                                  │
│ 预计时间: 76 小时 (3.2 天)                           │
│ 预计数据量: ~411,060 辆车                            │
│ 预计文件大小: ~500 MB                                │
└─────────────────────────────────────────────────────┘
```

---

## 🚀 快速开始

### **1. 基础运行（从批次1开始）**

```bash
cd /Users/hackm/Applications/2026-jhoo/tram-inspection/jdcsww-crawler

# 启动爬虫（支持断点续传）
python3 crawl_new_energy_full.py

# 指定批次范围
python3 crawl_new_energy_full.py --start-batch 300 --end-batch 403

# 从头开始（忽略断点续传）
python3 crawl_new_energy_full.py --no-resume
```

### **2. 后台运行（推荐）**

```bash
# 使用 nohup 后台运行
nohup python3 crawl_new_energy_full.py > crawl.log 2>&1 &

# 查看运行状态
tail -f crawl.log

# 查看进程
ps aux | grep crawl_new_energy_full
```

### **3. 定时任务（每天凌晨运行）**

```bash
# 编辑 crontab
crontab -e

# 添加以下行（每天凌晨2点运行）
0 2 * * * cd /Users/hackm/Applications/2026-jhoo/tram-inspection/jdcsww-crawler && python3 crawl_new_energy_full.py >> crawl.log 2>&1
```

---

## 📋 执行策略

### **策略A：连续执行（不推荐）**

```bash
# 一次性运行全部 13,702 个任务
python3 crawl_new_energy_full.py
```

**优点：** 简单
**缺点：**
- ❌ 需要76小时连续运行
- ❌ 中途失败需要重新开始
- ❌ 容易被网站封禁

---

### **策略B：分批执行（推荐）** ⭐

#### **方案1：按批次分段**

```bash
# 第1天：批次 1-150
python3 crawl_new_energy_full.py --start-batch 1 --end-batch 150

# 第2天：批次 151-300
python3 crawl_new_energy_full.py --start-batch 151 --end-batch 300

# 第3天：批次 301-403
python3 crawl_new_energy_full.py --start-batch 301 --end-batch 403
```

**优点：**
- ✅ 每天约28小时，可控
- ✅ 可以每天检查数据质量
- ✅ 失败影响范围小

#### **方案2：按车辆类型分段**

创建辅助脚本 `split_by_type.py`：

```python
#!/usr/bin/env python3
# 按车辆类型分段运行

from crawl_new_energy_full import FullNewEnergyCrawler

# 分5组，每组7种类型
type_groups = [
    (0, 7),    # 纯电动系列1
    (7, 14),   # 纯电动系列2
    (14, 21),  # 混合动力系列
    (21, 28),  # 插电式混合动力系列1
    (27, 34),  # 插电式混合动力系列2
]

for start_idx, end_idx in type_groups:
    crawler = FullNewEnergyCrawler()
    crawler.NEW_ENERGY_VEHICLE_TYPES = crawler.NEW_ENERGY_VEHICLE_TYPES[start_idx:end_idx]
    crawler.crawl_all()
```

---

### **策略C：智能分段（最优）** ⭐⭐⭐

#### **创建智能调度器**

```bash
# 创建智能执行脚本
vim smart_crawl.sh
```

```bash
#!/bin/bash
# smart_crawl.sh - 智能分段爬取

LOG_FILE="crawl_log_$(date +%Y%m%d).log"
DATA_DIR="data/full_new_energy_34types"
STATE_FILE="$DATA_DIR/crawler_state.json"

# 检查上次的执行状态
check_last_run() {
    if [ -f "$STATE_FILE" ]; then
        COMPLETED=$(python3 -c "import json; print(len(json.load(open('$STATE_FILE'))['completed_tasks']))")
        echo "✅ 已完成任务: $COMPLETED"
    else
        echo "⚠️  未找到状态文件，将从头开始"
        COMPLETED=0
    fi
}

# 预计剩余时间
estimate_remaining() {
    TOTAL=13702
    COMPLETED=$1
    REMAINING=$((TOTAL - COMPLETED))
    HOURS=$((REMAINING * 2 / 3600))  # 假设每个任务2秒
    echo "📊 预计剩余: $HOURS 小时"
}

# 主执行函数
run_crawl() {
    echo "=" >> "$LOG_FILE"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - 启动爬虫" >> "$LOG_FILE"

    python3 crawl_new_energy_full.py "$@" >> "$LOG_FILE" 2>&1

    echo "$(date '+%Y-%m-%d %H:%M:%S') - 爬虫结束" >> "$LOG_FILE"
    echo "=" >> "$LOG_FILE"
}

# 检查状态
check_last_run

# 执行爬虫（支持断点续传）
run_crawl "$@"

# 显示最终状态
check_last_run
```

```bash
# 赋予执行权限
chmod +x smart_crawl.sh

# 运行
./smart_crawl.sh
```

---

## 📊 监控方案

### **1. 实时监控脚本**

创建 `monitor.py`：

```python
#!/usr/bin/env python3
# monitor.py - 实时监控爬虫状态

import json
import os
import time
from datetime import datetime

STATE_FILE = "data/full_new_energy_34types/crawler_state.json"

def monitor():
    """实时监控"""
    try:
        while True:
            if os.path.exists(STATE_FILE):
                with open(STATE_FILE, 'r') as f:
                    state = json.load(f)

                completed = len(state['completed_tasks'])
                failed = len(state['failed_tasks'])
                total = 13702

                print(f"\r[{datetime.now().strftime('%H:%M:%S')}] "
                      f"已完成: {completed}/{total} ({completed/total*100:.1f}%) | "
                      f"失败: {failed} | "
                      f"已采集: {state.get('total_vehicles', 0)} 辆", end='')

            time.sleep(5)  # 每5秒刷新

    except KeyboardInterrupt:
        print("\n\n👋 监控已停止")

if __name__ == "__main__":
    monitor()
```

```bash
# 运行监控（另开一个终端）
python3 monitor.py
```

### **2. 进度统计**

```bash
# 创建统计脚本
vim stats.sh
```

```bash
#!/bin/bash
# stats.sh - 统计爬虫进度

STATE_FILE="data/full_new_energy_34types/crawler_state.json"

if [ ! -f "$STATE_FILE" ]; then
    echo "❌ 未找到状态文件"
    exit 1
fi

COMPLETED=$(python3 -c "import json; print(len(json.load(open('$STATE_FILE'))['completed_tasks']))")
FAILED=$(python3 -c "import json; print(len(json.load(open('$STATE_FILE'))['failed_tasks']))")
TOTAL=13702

echo "📊 爬虫进度统计"
echo "================================"
echo "总任务数: $TOTAL"
echo "已完成: $COMPLETED ($(python3 -c "print(f'{$COMPLETED/$TOTAL*100:.2f}%')"))"
echo "失败: $FAILED"
echo "剩余: $((TOTAL - COMPLETED))"
echo "================================"

# 显示最后更新时间
LAST_UPDATE=$(python3 -c "import json; print(json.load(open('$STATE_FILE'))['last_update'])")
echo "最后更新: $LAST_UPDATE"
```

---

## ⚠️ 错误处理

### **1. 自动重试机制**

代码中已包含自动重试，默认会：
- ❌ 失败的任务会被记录到 `failed_tasks`
- ✅ 重新运行时会自动跳过已完成的任务
- ✅ 只重试失败的任务

### **2. 失败任务重试**

```bash
# 创建重试脚本
vim retry_failed.py
```

```python
#!/usr/bin/env python3
# retry_failed.py - 重试失败的任务

import json
from crawl_new_energy_full import FullNewEnergyCrawler

STATE_FILE = "data/full_new_energy_34types/crawler_state.json"

# 加载状态
with open(STATE_FILE, 'r') as f:
    state = json.load(f)

# 获取失败的任务
failed_tasks = state['failed_tasks']

if not failed_tasks:
    print("✅ 没有失败的任务")
    exit(0)

print(f"🔄 发现 {len(failed_tasks)} 个失败的任务，开始重试...")

crawler = FullNewEnergyCrawler()

# 重试每个失败的任务
for task_info in failed_tasks:
    task = task_info['task']
    batch, clmc_code = task.split('-')

    # 查找对应的车辆类型
    vehicle_type = None
    for vt in crawler.NEW_ENERGY_VEHICLE_TYPES:
        if vt['code'] == clmc_code:
            vehicle_type = vt
            break

    if vehicle_type:
        print(f"🔄 重试: 批次{batch} - {vehicle_type['name']}")
        crawler.crawl_single_task(batch, vehicle_type)

print("✅ 重试完成")
```

---

## 🎯 执行计划（推荐）

### **第1天：批次 1-100**

```bash
# 凌晨2点启动
nohup python3 crawl_new_energy_full.py --start-batch 1 --end-batch 100 > day1.log 2>&1 &

# 预计完成时间：当天下午6点
```

### **第2天：批次 101-250**

```bash
# 凌晨2点启动
nohup python3 crawl_new_energy_full.py --start-batch 101 --end-batch 250 > day2.log 2>&1 &

# 预计完成时间：当天晚上10点
```

### **第3天：批次 251-403**

```bash
# 凌晨2点启动
nohup python3 crawl_new_energy_full.py --start-batch 251 --end-batch 403 > day3.log 2>&1 &

# 预计完成时间：第4天凌晨4点
```

---

## 📈 优化建议

### **1. 并发优化（不推荐）**

```python
# 可以尝试使用多线程，但风险较高
# 可能导致IP被封禁
import threading

def crawl_with_threads():
    # 使用3个线程并发
    # 但需要谨慎使用
    pass
```

### **2. 代理轮换**

如果有代理池，可以添加代理支持：

```python
proxies = [
    'http://proxy1.com:8080',
    'http://proxy2.com:8080',
    # ...
]

# 随机选择代理
proxy = random.choice(proxies)
```

### **3. 分布式爬取**

如果有多台机器：

```bash
# 机器1：批次 1-150
python3 crawl_new_energy_full.py --start-batch 1 --end-batch 150

# 机器2：批次 151-300
python3 crawl_new_energy_full.py --start-batch 151 --end-batch 300

# 机器3：批次 301-403
python3 crawl_new_energy_full.py --start-batch 301 --end-batch 403
```

---

## ✅ 验收标准

### **数据完整性检查**

```bash
# 创建检查脚本
vim check_data.sh
```

```bash
#!/bin/bash
# check_data.sh - 检查数据完整性

DATA_DIR="data/full_new_energy_34types"

echo "📊 数据完整性检查"
echo "================================"

# 检查任务完成率
STATE_FILE="$DATA_DIR/crawler_state.json"
COMPLETED=$(python3 -c "import json; print(len(json.load(open('$STATE_FILE'))['completed_tasks']))")
TOTAL=13702
echo "任务完成率: $(python3 -c "print(f'{$COMPLETED/$TOTAL*100:.2f}%')")"

# 检查数据文件
JSON_FILE=$(ls -t $DATA_DIR/vehicles_*.json 2>/dev/null | head -1)
if [ -n "$JSON_FILE" ]; then
    VEHICLE_COUNT=$(python3 -c "import json; print(len(json.load(open('$JSON_FILE'))))")
    echo "总车辆数: $VEHICLE_COUNT"

    # 检查文件大小
    FILE_SIZE=$(du -h "$JSON_FILE" | cut -f1)
    echo "文件大小: $FILE_SIZE"
else
    echo "⚠️  未找到数据文件"
fi

echo "================================"
```

---

## 📞 故障排除

### **问题1：被网站封禁**

**症状：** 所有请求都返回"非正常访问"

**解决方案：**
```bash
# 停止爬虫
pkill -f crawl_new_energy_full

# 等待24小时
# 或者更换IP地址
```

### **问题2：程序崩溃**

**症状：** 程序意外退出

**解决方案：**
```bash
# 查看日志
tail -100 crawl.log

# 重新运行（会自动断点续传）
python3 crawl_new_energy_full.py
```

### **问题3：数据重复**

**症状：** 数据文件中有重复记录

**解决方案：**
```python
# 去重脚本
import json

with open('vehicles_xxx.json', 'r') as f:
    vehicles = json.load(f)

# 使用集合去重（基于唯一标识）
unique_vehicles = {v['详情链接']: v for v in vehicles}.values()

print(f"去重前: {len(vehicles)}")
print(f"去重后: {len(unique_vehicles)}")

with open('vehicles_unique.json', 'w') as f:
    json.dump(list(unique_vehicles), f, ensure_ascii=False, indent=2)
```

---

## 🎉 总结

这个方案提供了：
- ✅ 完整的代码实现
- ✅ 断点续传支持
- ✅ 多种执行策略
- ✅ 实时监控方案
- ✅ 错误处理机制
- ✅ 数据验证方法

**预计总耗时：3-4天**（取决于网络状况和机器性能）
**预计数据量：40万+辆新能源汽车**
**预计文件大小：500MB-1GB**
