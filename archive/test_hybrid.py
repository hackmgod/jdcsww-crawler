#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试混合动力参数 rylx=O
"""

import urllib.request
import urllib.parse
import re


def test_hybrid_vehicles():
    """测试混合动力车辆"""
    base_url = "https://www.jdcsww.com/qcggs"

    # 使用您提供的URL参数
    # 测试多个批次
    test_batches = ['350', '360', '370', '380', '390']

    url = f"{base_url}?{urllib.parse.urlencode(params)}"

    print("=" * 70)
    print("测试混合动力车辆参数")
    print("=" * 70)
    print(f"URL: {url}")
    print()

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        }
        req = urllib.request.Request(url, headers=headers)

        with urllib.request.urlopen(req, timeout=30) as response:
            html = response.read().decode('utf-8', errors='ignore')

            # 提取车辆
            pattern = r'<span class="car_name"><a href="[^"]+"[^>]*>([^<]+)</a></span>'
            vehicles = re.findall(pattern, html)

            print(f"✅ 成功访问！")
            print(f"📊 找到 {len(vehicles)} 辆混合动力车")
            print()

            if vehicles:
                print("前5辆混合动力车:")
                print("-" * 70)
                for i, name in enumerate(vehicles[:5], 1):
                    print(f"{i}. {name}")

                if len(vehicles) > 5:
                    print(f"\n... 还有 {len(vehicles) - 5} 辆")

                print("\n" + "=" * 70)
                print("✅ 混合动力参数 rylx=O 验证成功！")
                print("=" * 70)
            else:
                print("⚠️  该批次没有混合动力车辆")
                print("建议: 测试更早的批次，如300-350")

    except Exception as e:
        print(f"❌ 错误: {e}")


if __name__ == "__main__":
    test_hybrid_vehicles()
