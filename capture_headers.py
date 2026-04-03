#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本 - 捕获真实请求并逐步测试
用于找出被封禁的具体原因
"""

import urllib.request
import json
import time
from http.cookiejar import CookieJar


def test_step_by_step():
    """逐步测试每个请求"""

    print("=" * 70)
    print("🔍 逐步测试请求")
    print("=" * 70)

    cookie_jar = CookieJar()
    opener = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(cookie_jar)
    )

    # 真实Chrome浏览器的完整请求头
    def get_real_headers():
        return {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'DNT': '1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Sec-Ch-Ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"macOS"',
        }

    # 步骤1: 访问首页
    print("\n[步骤 1/3] 访问首页")
    print("-" * 70)

    try:
        headers = get_real_headers()
        # 移除一些可能导致问题的头
        headers.pop('Accept-Encoding', None)
        headers.pop('DNT', None)

        req = urllib.request.Request('https://www.jdcsww.com', headers=headers)
        with opener.open(req, timeout=15) as response:
            html = response.read().decode('utf-8', errors='ignore')

            print(f"✓ 响应状态: {response.status}")
            print(f"✓ 响应长度: {len(html)} 字符")
            print(f"✓ Cookies数量: {len(cookie_jar)}")

            # 检查封禁
            if '非正常访问' in html or '爬取数据嫌疑' in html:
                print("❌ 被封禁！")
                return

            # 检查关键词
            if '车数万维' in html or 'jdcsww' in html.lower():
                print("✅ 首页访问成功")

    except Exception as e:
        print(f"❌ 失败: {e}")
        return

    # 等待
    print(f"\n⏱️ 等待 5 秒...")
    time.sleep(5)

    # 步骤2: 访问查询页（不带参数）
    print("\n[步骤 2/3] 访问查询页面（不带参数）")
    print("-" * 70)

    try:
        headers = get_real_headers()
        headers.pop('Accept-Encoding', None)
        headers.pop('DNT', None)
        headers['Referer'] = 'https://www.jdcsww.com/'
        headers['Sec-Fetch-Site'] = 'same-origin'

        req = urllib.request.Request('https://www.jdcsww.com/qcggs', headers=headers)
        with opener.open(req, timeout=15) as response:
            html = response.read().decode('utf-8', errors='ignore')

            print(f"✓ 响应状态: {response.status}")
            print(f"✓ 响应长度: {len(html)} 字符")

            # 检查封禁
            if '非正常访问' in html or '爬取数据嫌疑' in html:
                print("❌ 被封禁！")
                print("\n💡 建议：此步骤被封，说明需要更真实的浏览器特征")
                return

            # 检查关键词
            if 'qcggs' in html or '查询' in html or '公告' in html:
                print("✅ 查询页访问成功")
            else:
                print("⚠️  响应内容异常")

    except Exception as e:
        print(f"❌ 失败: {e}")
        return

    # 等待
    print(f"\n⏱️ 等待 5 秒...")
    time.sleep(5)

    # 步骤3: 访问查询页（带参数）
    print("\n[步骤 3/3] 访问查询页面（带参数 - 批次385纯电动）")
    print("-" * 70)

    try:
        headers = get_real_headers()
        headers.pop('Accept-Encoding', None)
        headers.pop('DNT', None)
        headers['Referer'] = 'https://www.jdcsww.com/qcggs'
        headers['Sec-Fetch-Site'] = 'same-origin'

        url = 'https://www.jdcsww.com/qcggs?ggpc=385&clmc=1&rylx=C&viewtype=0'
        print(f"URL: {url}")

        req = urllib.request.Request(url, headers=headers)
        with opener.open(req, timeout=15) as response:
            html = response.read().decode('utf-8', errors='ignore')

            print(f"✓ 响应状态: {response.status}")
            print(f"✓ 响应长度: {len(html)} 字符")

            # 检查封禁
            if '非正常访问' in html or '爬取数据嫌疑' in html:
                print("❌ 被封禁！")
                print("\n💡 建议：步骤3被封，说明参数查询被限制")
                return

            # 检查是否有数据
            import re
            pattern = r'<span class="car_name"><a href="([^"]+)"[^>]*>([^<]+)</a></span>'
            matches = re.findall(pattern, html)

            if matches:
                print(f"✅ 找到 {len(matches)} 辆车")
                for idx, (link, name) in enumerate(matches[:5], 1):
                    print(f"  {idx}. {name}")
                if len(matches) > 5:
                    print(f"  ... 还有 {len(matches) - 5} 辆")
            else:
                print("⚠️  未找到车辆数据")
                print("   (批次385纯电动可能已爬完或无数据)")

    except Exception as e:
        print(f"❌ 失败: {e}")
        return

    print("\n" + "=" * 70)
    print("✅ 所有步骤测试完成！")
    print("=" * 70)


if __name__ == "__main__":
    test_step_by_step()
