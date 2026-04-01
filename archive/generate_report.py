#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据分析报告生成器
"""

import json
from collections import Counter
from datetime import datetime


def generate_report():
    """生成数据分析报告"""

    # 读取数据
    with open('data/vehicle_complete_data_batch385.json', 'r', encoding='utf-8') as f:
        vehicles = json.load(f)

    report = []
    report.append("# 汽车公告数据分析报告\n\n")
    report.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    report.append(f"**数据批次**: 385\n")
    report.append(f"**车辆数量**: {len(vehicles)} 辆\n")
    report.append(f"**数据字段**: 平均 {len(vehicles[0])} 个/辆\n\n")
    report.append("---\n\n")

    # 1. 基本信息
    report.append("## 📋 基本信息\n\n")
    report.append("| 序号 | 车辆名称 | 生产企业 | 公告编号 |\n")
    report.append("|------|----------|----------|----------|\n")

    for idx, v in enumerate(vehicles[:10], 1):
        report.append(f"| {idx} | {v.get('车辆名称', 'N/A')[:30]} | {v.get('生产企业', 'N/A')[:20]} | {v.get('公告编号', 'N/A')} |\n")

    if len(vehicles) > 10:
        report.append(f"| ... | ... | ... | ... |\n")
        report.append(f"| {len(vehicles)} | 共{len(vehicles)}辆车 | ... | ... |\n")

    report.append("\n---\n\n")

    # 2. 三电系统统计
    report.append("## ⚡ 三电系统统计\n\n")

    # 电芯供应商
    report.append("### 🔋 电芯供应商分布\n\n")
    cell_suppliers = {}
    for v in vehicles:
        supplier = v.get('电芯参数_电芯生产企业', '未知')
        if supplier and supplier != '未知':
            cell_suppliers[supplier] = cell_suppliers.get(supplier, 0) + 1

    report.append("| 供应商 | 车辆数量 | 市场份额 |\n")
    report.append("|--------|----------|----------|\n")
    for supplier, count in sorted(cell_suppliers.items(), key=lambda x: x[1], reverse=True):
        percent = (count / len(vehicles) * 100)
        report.append(f"| {supplier} | {count} | {percent:.1f}% |\n")

    report.append("\n---\n\n")

    # 电池电量分布
    report.append("### 🔋 电池电量分布\n\n")

    batteries = []
    for v in vehicles:
        kwh = v.get('电池信息_电池电量(KWh)')
        if kwh and kwh != 'N/A':
            try:
                batteries.append({
                    'name': v.get('车辆名称', 'N/A'),
                    'kwh': float(kwh),
                    'supplier': v.get('电池信息_电池管理系统BMS', 'N/A')
                })
            except:
                pass

    if batteries:
        batteries_sorted = sorted(batteries, key=lambda x: x['kwh'], reverse=True)

        report.append("**TOP 10 大电量车型：**\n\n")
        report.append("| 排名 | 车辆名称 | 电池电量(KWh) | 电池管理系统 |\n")
        report.append("|------|----------|---------------|--------------|\n")

        for idx, bat in enumerate(batteries_sorted[:10], 1):
            report.append(f"| {idx} | {bat['name'][:40]} | {bat['kwh']} | {bat['supplier'][:30]} |\n")

        report.append(f"\n**统计信息：**\n\n")
        all_kwh = [b['kwh'] for b in batteries]
        report.append(f"- 平均电量: **{sum(all_kwh)/len(all_kwh):.2f} KWh**\n")
        report.append(f"- 最小电量: **{min(all_kwh):.2f} KWh**\n")
        report.append(f"- 最大电量: **{max(all_kwh):.2f} KWh**\n")
        report.append(f"- 电量区间: **{max(all_kwh) - min(all_kwh):.2f} KWh**\n")

    report.append("\n---\n\n")

    # 电机信息统计
    report.append("### ⚙️ 电机供应商分布\n\n")

    motor_suppliers = {}
    for v in vehicles:
        supplier = v.get('电机信息_电机生产企业', '未知')
        if supplier and supplier != '未知' and supplier != '--':
            motor_suppliers[supplier] = motor_suppliers.get(supplier, 0) + 1

    report.append("| 供应商 | 车辆数量 | 市场份额 |\n")
    report.append("|--------|----------|----------|\n")
    for supplier, count in sorted(motor_suppliers.items(), key=lambda x: x[1], reverse=True):
        percent = (count / len(vehicles) * 100)
        report.append(f"| {supplier} | {count} | {percent:.1f}% |\n")

    report.append("\n---\n\n")

    # 3. 详细数据示例
    report.append("## 📄 完整数据示例\n\n")

    report.append("### 示例1：大电量牵引车\n\n")
    if batteries_sorted:
        example = batteries_sorted[0]
        for v in vehicles:
            if v.get('车辆名称') == example['name']:
                report.append(f"**{v.get('车辆名称')}**\n\n")
                report.append(f"- 公告编号: `{v.get('公告编号')}`\n")
                report.append(f"- 生产企业: `{v.get('生产企业')}`\n")
                report.append(f"- 电池电量: `{example['kwh']} KWh`\n")
                report.append(f"- 电池管理系统: `{example['supplier']}`\n")
                report.append(f"- 电机型号: `{v.get('电机信息_电机型号')}`\n")
                report.append(f"- 电机企业: `{v.get('电机信息_电机生产企业')}`\n")
                report.append(f"- 电芯类型: `{v.get('电芯参数_电芯类型')}`\n")
                report.append(f"- 电芯企业: `{v.get('电芯参数_电芯生产企业')}`\n")
                break

    report.append("\n---\n\n")

    # 4. 技术趋势分析
    report.append("## 📈 技术趋势分析\n\n")

    # 电芯类型分布
    cell_types = Counter([v.get('电芯参数_电芯类型', '未知') for v in vehicles])
    report.append("### 🔋 电芯技术路线\n\n")
    for cell_type, count in cell_types.most_common():
        report.append(f"- **{cell_type}**: {count} 辆 ({count/len(vehicles)*100:.1f}%)\n")

    report.append("\n")

    # 电机冷却方式
    cooling_methods = Counter([v.get('电机信息_电机冷却方式', '未知') for v in vehicles])
    report.append("### ⚙️ 电机冷却方式\n\n")
    for method, count in cooling_methods.most_common():
        report.append(f"- **{method}**: {count} 辆 ({count/len(vehicles)*100:.1f}%)\n")

    report.append("\n---\n\n")

    # 5. 数据文件说明
    report.append("## 📁 数据文件说明\n\n")
    report.append("### 文件信息\n\n")
    report.append(f"- **文件名**: `vehicle_complete_data_batch385.json`\n")
    report.append(f"- **数据量**: {len(vehicles)} 辆车\n")
    report.append(f"- **数据字段**: 每辆车约 {len(vehicles[0])} 个字段\n")
    report.append(f"- **文件大小**: 约 {os.path.get('data/vehicle_complete_data_batch385.json') / 1024:.1f} KB\n")

    report.append("\n### 数据结构\n\n")
    report.append("```json\n")
    report.append("{\n")
    report.append("  \"车辆名称\": \"...\",\n")
    report.append("  \"公告编号\": \"...\",\n")
    report.append("  \"公告型号\": \"...\",\n")
    report.append("  \"生产企业\": \"...\",\n")
    report.append("  \"发布时间\": \"...\",\n")
    report.append("  \"额定载质量(KG)\": \"...\",\n")
    report.append("  \"车辆外形长宽高(mm)\": \"...\",\n")
    report.append("  \n")
    report.append("  // 电芯参数\n")
    report.append("  \"电芯参数_动力类型\": \"纯电动\",\n")
    report.append("  \"电芯参数_电芯类型\": \"磷酸铁锂\",\n")
    report.append("  \"电芯参数_电芯电压(v)\": \"3.22\",\n")
    report.append("  \"电芯参数_电芯生产企业\": \"...\",\n")
    report.append("  \n")
    report.append("  // 电池信息\n")
    report.append("  \"电池信息_电池电量(KWh)\": \"86.554\",\n")
    report.append("  \"电池信息_电池管理系统BMS\": \"...\",\n")
    report.append("  \n")
    report.append("  // 电机信息\n")
    report.append("  \"电机信息_电机型号\": \"...\",\n")
    report.append("  \"电机信息_电机生产企业\": \"...\",\n")
    report.append("  \n")
    report.append("  // 电控系统\n")
    report.append("  \"电控系统_电控供应商\": \"...\"\n")
    report.append("}\n")
    report.append("```\n")

    report.append("\n---\n\n")

    # 6. 使用建议
    report.append("## 💡 使用建议\n\n")
    report.append("### 数据用途\n\n")
    report.append("1. **市场分析**\n")
    report.append("   - 电池供应商市场份额分析\n")
    report.append("   - 电机技术路线研究\n")
    report.append("   - 车型配置统计\n\n")

    report.append("2. **技术调研**\n")
    report.append("   - 电芯技术路线对比\n")
    report.append("   - 电池能量密度分析\n")
    report.append("   - 电机功率区间分布\n\n")

    report.append("3. **供应链分析**\n")
    report.append("   - 识别主要供应商\n")
    report.append("   - 供应链关系图谱\n")
    report.append("   - 国产化率分析\n\n")

    report.append("### 扩展数据\n\n")
    report.append("如需更多批次数据，可以：\n\n")
    report.append("```bash\n")
    report.append("# 修改批次号\n")
    report.append("crawler.run(batch=403, detail_limit=30)  # 爬取403批次\n")
    report.append("crawler.run(batch=402, detail_limit=30)  # 爬取402批次\n")
    report.append("```\n\n")

    report.append("---\n\n")
    report.append(f"**报告生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append(f"**数据来源**: 司机宝宝网 (jdcsww.com)\n")

    # 保存报告
    report_text = ''.join(report)

    with open('data/analysis_report.md', 'w', encoding='utf-8') as f:
        f.write(report_text)

    print(report_text)

    print("\n" + "=" * 70)
    print("✅ 分析报告已生成: data/analysis_report.md")
    print("=" * 70)


if __name__ == "__main__":
    def main():
    import os
    generate_report()
