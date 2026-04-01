# ✅ 断点续传功能说明

## 🎯 功能概述

爬虫已经实现了完整的**断点续传**功能，即使中断也能从上次位置继续！

---

## 📁 记录文件

爬虫会自动保存两个重要文件：

### 1. `crawler_state.json` - 状态记录
```json
{
  "completed_batches": [
    "1-C", "1-O",      // 批次1完成（纯电动+混合动力）
    "2-C", "2-O",      // 批次2完成
    ...
    "16-C", "16-O"     // 批次16完成
  ],
  "failed_batches": [
    "17-C", "17-O"     // 批次17失败
  ],
  "total_vehicles": 480,
  "last_update": "2026-03-19 01:00:00"
}
```

### 2. `all_vehicles.json` - 数据文件
```json
[
  {
    "批次": 1,
    "燃料类型": "纯电动",
    "公告型号": "...",
    "生产企业": "...",
    ...
  },
  ...
]
```

---

## 🔄 使用方法

### 场景1: 正常中断（如IP被封）

```bash
# 1. 爬取被中断（Ctrl+C 或自动停止）
#    进度已自动保存

# 2. 等待20分钟，更换网络

# 3. 重新运行
python3 crawl_production.py

# 4. 选择 3 - 继续上次中断的任务
#    会自动跳过已完成的批次1-16
#    从批次17继续
```

### 场景2: 用户主动中断

```bash
# 按 Ctrl+C 中断

# 输出：
# ⚠️  用户中断！保存当前进度...
# ✓ 进度已保存

# 下次继续：
python3 crawl_production.py
# 选择 3
```

### 场景3: 程序异常退出

```bash
# 程序崩溃/断网/错误
# 状态已自动保存

# 恢复：
python3 crawl_production.py
# 选择 3
```

---

## 💡 工作原理

### 自动保存机制

```
每完成1个批次 → 立即保存
├─ 状态文件更新
├─ 数据文件追加
└─ 进度显示更新
```

### 智能跳过

```
for batch in range(1, 404):
    for fuel_type in ['纯电动', '混合动力']:
        task_key = f"{batch}-{fuel_type.code}"

        # ⭐ 检查是否已完成
        if task_key in completed_batches:
            print(f"跳过已完成: {task_key}")
            continue

        # 爬取数据
        crawl_batch(batch, fuel_type)
```

---

## ⏱️ 时间随机化

### 优化后的延迟策略

```python
# 基础延迟: 7-12秒
base_delay = random.uniform(7, 12)

# 随机波动: ±3秒
random_jitter = random.uniform(-3, 3)

# 最终延迟: 5-15秒
delay = max(5, base_delay + random_jitter)
```

**优势**:
- ✅ 避免固定模式
- ✅ 模拟真实用户行为
- ✅ 大幅降低被检测风险

---

## 📊 实际使用示例

### 完整流程

```bash
# === 第1次运行 ===
$ python3 crawl_production.py
选择: 1 - 爬取所有批次

开始爬取...
✓ 批次1 [纯电动] - 30辆
✓ 批次1 [混合动力] - 2辆
✓ 批次2 [纯电动] - 30辆
...
✓ 批次16 [纯电动] - 30辆

⚠️ 批次17 [纯电动] - 被拦截
⚠️  用户中断！保存当前进度...
✓ 进度已保存

# === 等待20分钟，更换网络 ===

# === 第2次运行 ===
$ python3 crawl_production.py
选择: 3 - 继续上次中断的任务

📊 已有数据: 480 辆
✓ 已完成批次: 32 个任务

🔄 断点续传模式:
   上次完成: 16-O
   下一个: 批次17

跳过已完成: 1-C
跳过已完成: 1-O
...
跳过已完成: 16-C
跳过已完成: 16-O

继续爬取...
✓ 批次17 [纯电动] - 30辆
✓ 批次17 [混合动力] - 1辆
✓ 批次18 [纯电动] - 30辆
...
```

---

## 🔍 查看当前进度

### 方法1: 运行时查看

```bash
python3 crawl_production.py
# 选择 3
# 会显示详细进度
```

### 方法2: 查看文件

```bash
# 查看状态
cat data/production/crawler_state.json | python3 -m json.tool

# 查看数据量
wc -l data/production/all_vehicles.json
```

### 方法3: 统计信息

```python
import json

with open('data/production/crawler_state.json') as f:
    state = json.load(f)

print(f"已完成: {len(state['completed_batches'])} 个任务")
print(f"失败: {len(state['failed_batches'])} 个任务")
print(f"总车辆: {state['total_vehicles']} 辆")
```

---

## ⚙️ 高级配置

### 修改延迟范围

编辑 `crawl_production.py` 第327-332行：

```python
# 更保守（不易被拦截）
base_delay = random.uniform(10, 15)
random_jitter = random.uniform(-5, 5)

# 更激进（可能被拦截）
base_delay = random.uniform(5, 8)
random_jitter = random.uniform(-2, 2)
```

### 修改休息策略

编辑第337-342行：

```python
# 每30批次休息（更频繁）
if completed_tasks % 60 == 0:  # 30批次 × 2
    rest_time = 60  # 休息1分钟

# 每100批次休息（更稳定）
if completed_tasks % 200 == 0:  # 100批次 × 2
    rest_time = 30  # 休息30秒
```

---

## ❓ 常见问题

### Q: 中断后数据会丢失吗？
A: **不会**。每个批次完成后立即保存，不会丢失。

### Q: 可以从任意批次开始吗？
A: **可以**。选择选项2，输入起始和结束批次。

### Q: 失败的批次会重试吗？
A: **会**。选择选项3时，会询问是否重试失败批次。

### Q: 如何确认进度已保存？
A: 查看这两个文件：
- `data/production/crawler_state.json`
- `data/production/all_vehicles.json`

### Q: 时间是真正随机的吗？
A: **是的**。每次延迟都是5-15秒之间的随机值。

---

## ✅ 总结

### 核心特性

- ✅ **自动保存** - 每批次完成后立即保存
- ✅ **智能跳过** - 自动跳过已完成的批次
- ✅ **断点续传** - 中断后从上次位置继续
- ✅ **随机延迟** - 5-15秒随机，避免被检测
- ✅ **进度显示** - 实时显示爬取进度
- ✅ **失败重试** - 支持重试失败的批次

### 使用建议

1. ⭐ 使用凌晨时间爬取（2-6点）
2. ⭐ 随机延迟已优化，无需修改
3. ⭐ 中断后选择"选项3"继续
4. ⭐ 定期查看data/production/目录
5. ⭐ 如持续失败，等待20分钟后继续

---

**现在就可以放心使用，不用担心中断了！** 🎉
