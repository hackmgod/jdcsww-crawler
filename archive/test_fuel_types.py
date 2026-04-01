#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试不同燃料类型的参数值
"""

import urllib.request
import urllib.parse
import re


def test_fuel_type(batch, rylx_code):
    """测试燃料类型代码"""
    base_url = "https://www.jdcsww.com"
    url = f"{base_url}/qcggs"
    params = {
        'ggxh': '',
        'ggpc': str(batch),
        'zwpp': '',
        'clmc': '1',
        'fdjxh': '',
        'qymc': '',
        'cph': '',
        'rylx': rylx_code,
        'viewtype': '0'
    }
    list_url = f"{url}?{urllib.parse.urlencode(params)}"

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        }
        req = urllib.request.Request(list_url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode('utf-8', errors='ignore')

            # 检查是否被拦截
            if '非正常访问' in html or '爬取数据嫌疑' in html:
                return None, '被拦截'

            # 提取车辆数量
            pattern = r'<span class="car_name"><a href="[^"]+"[^>]*>([^<]+)</a></span>'
            matches = re.findall(pattern, html)

            # 获取燃料类型描述
            fuel_desc = '未知'
            fuel_pattern = r'燃料类型[：:]([^<\n]+?)(?:<|\.|$)'
            fuel_match = re.search(fuel_pattern, html)
            if fuel_match:
                fuel_desc = fuel_match.group(1).strip()

            return len(matches), fuel_desc

    except Exception as e:
        return None, str(e)


def main():
    """测试不同的燃料类型代码"""
    batch = 403

    print(f"测试批次: {batch}")
    print("=" * 60)

    # 常见的燃料类型代码
    test_codes = [
        ('C', '纯电动'),
        ('H', '混合动力'),
        ('Q', '燃料电池'),
        ('', '全部/空值'),
        ('D', '插电式混合动力'),
        ('B', '柴油'),
        ('G', '汽油'),
    ]

    print(f"{'代码':<10} {'含义':<20} {'车辆数':<10} {'实际描述':<20}")
    print("-" * 60)

    results = []
    for code, desc in test_codes:
        count, actual_desc = test_fuel_type(batch, code)
        display_code = f"'{code}'" if code else "(空)"
        if count is not None:
            print(f"{display_code:<10} {desc:<20} {count:<10} {actual_desc:<20}")
            results.append((code, count, actual_desc))
        else:
            print(f"{display_code:<10} {desc:<20} {'失败':<10} {actual_desc:<20}")

    print("\n" + "=" * 60)
    print("总结:")
    print("-" * 60)
    for code, count, desc in results:
        if count > 0:
            print(f"  rylx='{code}' → {desc} → {count} 辆")


if __name__ == "__main__":
    main()
