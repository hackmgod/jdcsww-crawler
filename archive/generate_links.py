#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从已有数据生成详情链接清单
"""

import json
import os


def generate_detail_links():
    """生成详情链接清单"""

    # 读取已有数据
    with open('data/vehicle_list_batch403.json', 'r', encoding='utf-8') as f:
        vehicles = json.load(f)

    print(f"找到 {len(vehicles)} 辆车\n")

    # 生成 Markdown 报告
    md_content = ["# 车辆详情链接清单\n\n"]
    md_content.append(f"**批次**: 403\n")
    md_content.append(f"**车辆数量**: {len(vehicles)}\n")
    md_content.append(f"**更新时间**: 2026-03-19\n\n")
    md_content.append("---\n\n")

    for vehicle in vehicles:
        md_content.append(f"## {vehicle['序号']}. {vehicle['车辆名称']}\n\n")
        md_content.append(f"- **公告编号**: `{vehicle.get('公告编号', 'N/A')}`\n")
        md_content.append(f"- **公告型号**: `{vehicle.get('公告型号', 'N/A')}`\n")
        md_content.append(f"- **生产企业**: {vehicle.get('生产企业', 'N/A')}\n")
        md_content.append(f"- **发布时间**: {vehicle.get('发布时间', 'N/A')}\n")
        md_content.append(f"- **详情链接**: [{vehicle['详情链接']}]({vehicle['详情链接']})\n\n")
        md_content.append("**使用方法**:\n")
        md_content.append("1. 点击上方链接打开详情页\n")
        md_content.append("2. 查看三电参数（电池、电机、电控）\n")
        md_content.append("3. 右键保存车辆图片\n")
        md_content.append("4. 复制需要的数据\n\n")
        md_content.append("---\n\n")

    # 保存 Markdown
    with open('data/DETAIL_LINKS.md', 'w', encoding='utf-8') as f:
        f.write(''.join(md_content))

    print("✓ 已生成: data/DETAIL_LINKS.md")
    print("\n前 3 辆车:")
    for v in vehicles[:3]:
        print(f"\n{v['序号']}. {v['车辆名称']}")
        print(f"   {v['详情链接']}")

    # 生成纯文本链接列表
    txt_content = []
    txt_content.append("车辆详情链接列表\n")
    txt_content.append("=" * 60 + "\n\n")

    for vehicle in vehicles:
        txt_content.append(f"{vehicle['序号']}. {vehicle['车辆名称']}\n")
        txt_content.append(f"   {vehicle['详情链接']}\n\n")

    with open('data/detail_links.txt', 'w', encoding='utf-8') as f:
        f.write(''.join(txt_content))

    print("\n✓ 已生成: data/detail_links.txt")

    # 生成 HTML 查看器
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>车辆详情查看器 - 批次403</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; background: #f5f7fa; padding: 20px; }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; text-align: center; }}
        .header h1 {{ font-size: 32px; margin-bottom: 10px; }}
        .stats {{ display: flex; justify-content: center; gap: 30px; margin-top: 20px; }}
        .stat-item {{ font-size: 18px; }}
        .search-box {{ margin-bottom: 30px; }}
        .search-box input {{ width: 100%; padding: 15px; border: 2px solid #e0e0e0; border-radius: 10px; font-size: 16px; transition: border-color 0.3s; }}
        .search-box input:focus {{ outline: none; border-color: #667eea; }}
        .vehicle-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(400px, 1fr)); gap: 20px; }}
        .vehicle-card {{ background: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.08); transition: transform 0.2s, box-shadow 0.2s; }}
        .vehicle-card:hover {{ transform: translateY(-5px); box-shadow: 0 5px 20px rgba(0,0,0,0.12); }}
        .vehicle-number {{ color: #667eea; font-weight: bold; font-size: 14px; margin-bottom: 5px; }}
        .vehicle-name {{ font-size: 18px; font-weight: bold; color: #333; margin-bottom: 15px; line-height: 1.4; }}
        .vehicle-info {{ font-size: 14px; color: #666; margin-bottom: 5px; }}
        .vehicle-info strong {{ color: #333; }}
        .detail-btn {{ display: inline-block; margin-top: 15px; padding: 12px 25px; background: #667eea; color: white; text-decoration: none; border-radius: 8px; font-weight: 500; transition: background 0.3s; }}
        .detail-btn:hover {{ background: #5568d3; }}
        .footer {{ text-align: center; margin-top: 50px; color: #999; font-size: 14px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚗 车辆详情查看器</h1>
            <div class="stats">
                <div class="stat-item">📊 总计: <strong>{len(vehicles)}</strong> 辆</div>
                <div class="stat-item">📅 批次: <strong>403</strong></div>
                <div class="stat-item">⚡ 类型: <strong>纯电动</strong></div>
            </div>
        </div>

        <div class="search-box">
            <input type="text" id="searchInput" placeholder="🔍 搜索车辆名称、生产企业..." onkeyup="filterVehicles()">
        </div>

        <div class="vehicle-grid" id="vehicleGrid">
"""

    for vehicle in vehicles:
        html += f"""
            <div class="vehicle-card" data-name="{vehicle['车辆名称'].lower()} {vehicle.get('生产企业', '').lower()}">
                <div class="vehicle-number">#{vehicle['序号']}</div>
                <div class="vehicle-name">{vehicle['车辆名称']}</div>
                <div class="vehicle-info"><strong>公告编号:</strong> {vehicle.get('公告编号', 'N/A')}</div>
                <div class="vehicle-info"><strong>生产企业:</strong> {vehicle.get('生产企业', 'N/A')}</div>
                <div class="vehicle-info"><strong>发布时间:</strong> {vehicle.get('发布时间', 'N/A')}</div>
                <a href="{vehicle['详情链接']}" target="_blank" class="detail-btn">📋 查看详情 →</a>
            </div>
"""

    html += f"""
        </div>

        <div class="footer">
            <p>数据来源: 司机宝宝网 (jdcsww.com) | 更新时间: 2026-03-19</p>
            <p>💡 提示: 点击"查看详情"按钮打开详情页，可查看三电参数和下载图片</p>
        </div>
    </div>

    <script>
        function filterVehicles() {{
            const input = document.getElementById('searchInput');
            const filter = input.value.toLowerCase();
            const cards = document.getElementsByClassName('vehicle-card');

            for (let i = 0; i < cards.length; i++) {{
                const name = cards[i].getAttribute('data-name');
                if (name.indexOf(filter) > -1) {{
                    cards[i].style.display = "";
                }} else {{
                    cards[i].style.display = "none";
                }}
            }}
        }}
    </script>
</body>
</html>
"""

    with open('data/vehicle_viewer.html', 'w', encoding='utf-8') as f:
        f.write(html)

    print("✓ 已生成: data/vehicle_viewer.html")
    print("\n" + "=" * 60)
    print("✅ 完成！")
    print("\n📝 使用方法:")
    print("1. 在浏览器中打开 data/vehicle_viewer.html")
    print("2. 搜索或找到需要的车辆")
    print("3. 点击 '查看详情' 按钮")
    print("4. 在详情页中查看三电参数和下载图片")
    print("=" * 60)


if __name__ == "__main__":
    generate_detail_links()
