#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
手动数据获取辅助工具
提供详情链接，方便手动访问和复制数据
"""

import urllib.request
import urllib.parse
import json
import re
from typing import List, Dict


def get_vehicle_links():
    """获取车辆详情链接列表"""
    base_url = "https://www.jdcsww.com"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    }

    # 获取列表页
    url = f"{base_url}/qcggs?ggpc=403&clmc=1&rylx=C&viewtype=0"
    req = urllib.request.Request(url, headers=headers)

    with urllib.request.urlopen(req, timeout=30) as response:
        html = response.read().decode('utf-8', errors='ignore')

    # 解析链接
    vehicles = []
    pattern = r'<span class="car_name"><a href="([^"]+)"[^>]*>([^<]+)</a></span>'
    matches = re.findall(pattern, html)

    for idx, (link, name) in enumerate(matches, 1):
        vehicles.append({
            '序号': idx,
            '车辆名称': name.strip(),
            '详情链接': f"{base_url}{link}"
        })

    return vehicles


def generate_markdown_report(vehicles: List[Dict], filename: str = "data/vehicle_links_report.md"):
    """生成 Markdown 格式的报告"""
    report = []
    report.append("# 车辆详情链接清单\n")
    report.append(f"生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append(f"总计: {len(vehicles)} 辆车\n\n")
    report.append("---\n\n")

    for vehicle in vehicles:
        report.append(f"## {vehicle['序号']}. {vehicle['车辆名称']}\n\n")
        report.append(f"**详情链接**: [{vehicle['详情链接']}]({vehicle['详情链接']})\n\n")
        report.append("---\n\n")

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(''.join(report))

    print(f"✓ Markdown 报告已保存: {filename}")


def generate_html_viewer(vehicles: List[Dict], filename: str = "data/vehicle_viewer.html"):
    """生成 HTML 查看器（方便浏览器打开）"""
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>车辆详情查看器</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        h1 {{ color: #333; }}
        .vehicle-card {{
            background: white;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .vehicle-info {{ flex: 1; }}
        .vehicle-name {{ font-size: 18px; font-weight: bold; color: #333; margin-bottom: 5px; }}
        .vehicle-link {{ color: #666; font-size: 14px; }}
        .open-btn {{
            background: #007bff;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
        }}
        .open-btn:hover {{ background: #0056b3; }}
        .stats {{ background: #fff; padding: 15px; border-radius: 8px; margin-bottom: 20px; }}
        .search-box {{ margin: 20px 0; }}
        .search-box input {{
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚗 车辆详情查看器</h1>

        <div class="stats">
            <strong>总计:</strong> {len(vehicles)} 辆车 |
            <strong>批次:</strong> 403 |
            <strong>类型:</strong> 纯电动
        </div>

        <div class="search-box">
            <input type="text" id="searchInput" placeholder="搜索车辆名称..." onkeyup="filterVehicles()">
        </div>

        <div id="vehicleList">
"""

    for vehicle in vehicles:
        html += f"""
            <div class="vehicle-card" data-name="{vehicle['车辆名称']}">
                <div class="vehicle-info">
                    <div class="vehicle-name">{vehicle['序号']}. {vehicle['车辆名称']}</div>
                    <div class="vehicle-link">{vehicle['详情链接']}</div>
                </div>
                <a href="{vehicle['详情链接']}" target="_blank" class="open-btn">查看详情 →</a>
            </div>
"""

    html += """
        </div>
    </div>

    <script>
        function filterVehicles() {
            const input = document.getElementById('searchInput');
            const filter = input.value.toUpperCase();
            const cards = document.getElementsByClassName('vehicle-card');

            for (let i = 0; i < cards.length; i++) {
                const name = cards[i].getAttribute('data-name');
                if (name.toUpperCase().indexOf(filter) > -1) {
                    cards[i].style.display = "";
                } else {
                    cards[i].style.display = "none";
                }
            }
        }
    </script>
</body>
</html>
"""

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"✓ HTML 查看器已保存: {filename}")
    print(f"  在浏览器中打开该文件，点击按钮即可查看详情页")


def main():
    """主函数"""
    import time

    print("=" * 70)
    print("车辆详情链接生成工具")
    print("=" * 70)

    # 获取车辆链接
    print("\n正在获取车辆列表...")
    vehicles = get_vehicle_links()
    print(f"✓ 找到 {len(vehicles)} 辆车")

    # 生成报告
    print("\n生成报告文件...")
    generate_markdown_report(vehicles)
    generate_html_viewer(vehicles)

    # 显示前5条
    print("\n前 5 辆车:")
    for vehicle in vehicles[:5]:
        print(f"  {vehicle['序号']}. {vehicle['车辆名称']}")
        print(f"     {vehicle['详情链接']}")

    print("\n" + "=" * 70)
    print("✓ 完成！")
    print("\n使用方法:")
    print("1. 在浏览器中打开 data/vehicle_viewer.html")
    print("2. 搜索或找到需要的车辆")
    print("3. 点击 '查看详情' 按钮打开详情页")
    print("4. 手动复制数据和下载图片")
    print("=" * 70)


if __name__ == "__main__":
    main()
