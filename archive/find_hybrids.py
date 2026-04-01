#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查找混合动力车辆 - 检查多个批次
"""

import urllib.request
import urllib.parse
import re
import time


def check_batch_for_hybrids(batch_num):
    """检查某个批次是否有混合动力车辆"""
    base_url = "https://www.jdcsww.com"

    # 尝试不同的URL模式
    test_urls = [
        f"{base_url}/qcggs?ggpc={batch_num}&clmc=1&viewtype=0",  # 无燃料限制
        f"{base_url}/qcggs?ggpc={batch_num}&clmc=1&rylx=C&viewtype=0",  # 纯电动
        f"{base_url}/qcggs?ggpc={batch_num}&clmc=1&rylx=H&viewtype=0",  # 可能的混合动力
    ]

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    }

    for idx, test_url in enumerate(test_urls, 1):
        try:
            req = urllib.request.Request(test_url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as response:
                html = response.read().decode('utf-8', errors='ignore')

                # 提取车辆名称
                pattern = r'<span class="car_name"><a href="[^"]+"[^>]*>([^<]+)</a></span>'
                matches = re.findall(pattern, html)

                # 检查是否有"混合"、"插电"等关键词
                hybrids = [name for name in matches if any(keyword in name for keyword in ['混合', '插电', '混动', 'HEV', 'PHEV'])]

                if hybrids:
                    print(f"\n批次{batch_num} - URL {idx}:")
                    print(f"  总车辆: {len(matches)}")
                    print(f"  混合动力: {len(hybrids)}")
                    print(f"  示例: {hybrids[:3]}")

        except Exception as e:
            print(f"批次{batch_num} - URL {idx}: 失败 - {e}")

        time.sleep(1)


def main():
    """检查多个批次"""
    print("检查最近批次是否有混合动力车辆...")
    print("=" * 60)

    # 检查最近几个批次
    for batch in [403, 402, 401, 400, 399, 398]:
        check_batch_for_hybrids(batch)
        time.sleep(2)

    print("\n" + "=" * 60)
    print("如果上面没有显示混合动力车辆，可能的原因：")
    print("1. 这些批次没有混合动力车型")
    print("2. 混合动力使用不同的参数代码")
    print("3. 需要选择不同的查询条件")
    print("=" * 60)


if __name__ == "__main__":
    main()
