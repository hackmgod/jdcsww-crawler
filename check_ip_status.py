#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查IP封禁状态
"""

import urllib.request
import json


def check_ip_status():
    """检查IP是否被封禁"""

    print("=" * 70)
    print("🔍 检查IP封禁状态")
    print("=" * 70)

    # 测试1：访问首页
    print("\n[1/3] 测试访问首页...")
    try:
        req = urllib.request.Request(
            'https://www.jdcsww.com/',
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8', errors='ignore')

            if '非正常访问' in html or '爬取数据嫌疑' in html:
                print("  ❌ IP已被封禁（检测到反爬提示）")
                return False
            elif '车数万维' in html or 'jdcsww' in html.lower():
                print("  ✅ 可以正常访问")
            else:
                print("  ⚠️  响应异常（内容不完整）")
                return False
    except Exception as e:
        print(f"  ❌ 访问失败: {e}")
        return False

    # 测试2：访问列表页
    print("\n[2/3] 测试访问列表页...")
    try:
        req = urllib.request.Request(
            'https://www.jdcsww.com/qcggs?ggpc=385&clmc=1&rylx=C&viewtype=0',
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Referer': 'https://www.jdcsww.com/'
            }
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8', errors='ignore')

            if '非正常访问' in html or '爬取数据嫌疑' in html:
                print("  ❌ IP已被封禁（检测到反爬提示）")
                return False
            elif '公告列表' in html or 'qcggs' in html:
                print("  ✅ 可以正常访问")
            else:
                print("  ⚠️  响应异常")
                return False
    except Exception as e:
        print(f"  ❌ 访问失败: {e}")
        return False

    # 测试3：访问详情页
    print("\n[3/3] 测试访问详情页...")
    try:
        req = urllib.request.Request(
            'https://www.jdcsww.com/qcggdetail?bh=SV2026031300004',
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Referer': 'https://www.jdcsww.com/qcggs'
            }
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8', errors='ignore')

            if '非正常访问' in html or '爬取数据嫌疑' in html:
                print("  ❌ IP已被封禁（检测到反爬提示）")
                return False
            elif len(html) > 1000:
                print("  ✅ 可以正常访问")
            else:
                print("  ⚠️  响应内容过短")
                return False
    except Exception as e:
        print(f"  ❌ 访问失败: {e}")
        return False

    print("\n" + "=" * 70)
    print("✅ IP状态正常，可以继续爬取")
    print("=" * 70)
    return True


def show_solution():
    """显示解决方案"""
    print("\n" + "=" * 70)
    print("🛠️  IP封禁解决方案")
    print("=" * 70)

    print("\n方案1：等待解封（推荐）")
    print("  - 临时封禁：等待 10-15 分钟")
    print("  - 长期封禁：等待 1-2 小时")
    print("  - 优点：不需要额外成本")
    print("  - 缺点：需要等待")

    print("\n方案2：修改请求策略")
    print("  - 增加延迟：5-10秒/次")
    print("  - 添加随机延迟")
    print("  - 分批爬取，避免连续请求")
    print("  - 优点：简单有效")
    print("  - 缺点：速度慢")

    print("\n方案3：使用代理IP")
    print("  - 免费代理：不稳定")
    print("  - 付费代理：稳定，但需要成本")
    print("  - 推荐服务商：")
    print("    * 阿布云（http://www.abuyun.com）")
    print("    * 讯代理（http://www.xdaili.cn）")
    print("    * 快代理（http://www.kuaidaili.com）")
    print("  - 优点：可以绕过IP限制")
    print("  - 缺点：需要成本")

    print("\n方案4：使用Selenium")
    print("  - 模拟真实浏览器")
    print("  - 难以被检测")
    print("  - 优点：最稳定")
    print("  - 缺点：速度慢，资源占用大")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    # 检查IP状态
    is_banned = not check_ip_status()

    # 显示解决方案
    show_solution()

    if is_banned:
        print("\n⏰ 建议：等待15分钟后重新测试")
    else:
        print("\n✅ 建议：使用保守策略继续爬取（延迟5-10秒）")
