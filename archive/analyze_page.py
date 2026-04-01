#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取并保存页面HTML用于分析
"""

import urllib.request
import urllib.parse


def save_page_html():
    """保存页面HTML"""

    # 请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    }

    # 列表页URL
    url = "https://www.jdcsww.com/qcggs?ggxh=&ggpc=403&zwpp=&clmc=1&fdjxh=&qymc=&cph=&rylx=C&viewtype=0"

    print(f"正在获取: {url}")
    req = urllib.request.Request(url, headers=headers)

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            html = response.read().decode('utf-8')

            # 保存到文件
            with open('data/list_page_sample.html', 'w', encoding='utf-8') as f:
                f.write(html)

            print(f"✓ 列表页已保存到 data/list_page_sample.html")
            print(f"  文件大小: {len(html)} 字符")

            # 简单分析
            if '欧曼牌' in html:
                print("  ✓ 确认包含车辆数据")

            # 查找可能的链接模式
            import re
            links = re.findall(r'href="(/qcggdetail\?[^"]+)"', html)
            if links:
                print(f"  找到 {len(links)} 个详情链接:")
                for link in links[:5]:
                    print(f"    - {link}")

    except Exception as e:
        print(f"✗ 获取失败: {e}")


if __name__ == "__main__":
    save_page_html()
