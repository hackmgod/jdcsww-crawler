#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试混合动力参数 - 多批次测试
"""

import urllib.request
import urllib.parse
import re
import time


def test_batch(batch_num):
    """测试单个批次"""
    base_url = "https://www.jdcsww.com/qcggs"

    params = {
        'ggxh': '',
        'ggpc': str(batch_num),
        'zwpp': '',
        'clmc': '',
        'fdjxh': '',
        'qymc': '',
        'cph': '',
        'rylx': 'O',  # 混合动力
        'viewtype': '0'
    }

    url = f"{base_url}?{urllib.parse.urlencode(params)}"

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

            return len(vehicles), vehicles

    except Exception as e:
        return 0, []


def main():
    """测试多个批次"""
    print("=" * 70)
    print("混合动力车辆参数测试 (rylx=O)")
    print("=" * 70)
    print()

    # 测试不同批次的混合动力
    test_batches = [350, 360, 370, 380, 390, 400, 401, 402, 403]

    found_hybrids = False

    for batch in test_batches:
        count, vehicles = test_batch(batch)

        if count > 0:
            found_hybrids = True
            print(f"✅ 批次{batch}: {count} 辆混合动力车")
            print(f"   示例: {vehicles[0][:50]}...")
            print()
        else:
            print(f"   批次{batch}: 0 辆")

        time.sleep(1)

    print()
    print("=" * 70)

    if found_hybrids:
        print("✅ 混合动力参数 rylx=O 验证成功！")
        print("✅ 已找到包含混合动力的批次")
    else:
        print("⚠️  测试批次中没有混合动力车辆")
        print("💡 可能原因:")
        print("   1. 混合动力集中在更早的批次(1-300)")
        print("   2. 混合动力使用其他查询条件")
        print("   3. 当前测试范围没有混合动力车型")
        print()
        print("📊 建议:")
        print("   - 可以开始爬取，爬虫会自动处理所有批次")
        print("   - 如果某批次有混合动力，会自动爬取")
        print("   - 如果某批次没有，会跳过(0辆)")

    print("=" * 70)


if __name__ == "__main__":
    main()
