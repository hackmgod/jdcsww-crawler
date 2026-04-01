#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版爬虫 - 测试用
使用 urllib 无需额外安装依赖
"""

import urllib.request
import urllib.parse
import json
import time
import re
from html.parser import HTMLParser


class SimpleCrawler:
    """简化版爬虫"""

    def __init__(self):
        self.base_url = "https://www.jdcsww.com"

    def fetch_page(self, url: str) -> str:
        """获取页面内容"""
        try:
            # 模拟浏览器请求头
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Connection': 'keep-alive',
            }

            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as response:
                return response.read().decode('utf-8')
        except Exception as e:
            print(f"✗ 获取页面失败: {e}")
            return None

    def extract_vehicle_info(self, html: str) -> list:
        """提取车辆信息"""
        vehicles = []

        # 简单的正则提取
        # 查找车辆标题模式
        title_pattern = r'####\s+([^\n]+?)\s+公告属性'
        for match in re.finditer(title_pattern, html):
            title = match.group(1).strip()
            vehicles.append({'车辆名称': title})

        return vehicles

    def test_list_page(self):
        """测试列表页"""
        url = "https://www.jdcsww.com/qcggs"
        params = {
            'ggxh': '',
            'ggpc': '403',
            'zwpp': '',
            'clmc': '1',
            'fdjxh': '',
            'qymc': '',
            'cph': '',
            'rylx': 'C',
            'viewtype': '0'
        }

        full_url = f"{url}?{urllib.parse.urlencode(params)}"
        print(f"正在请求: {full_url}")

        html = self.fetch_page(full_url)
        if html:
            print(f"✓ 页面获取成功，长度: {len(html)} 字符")

            # 检查是否被拦截
            if '非正常访问' in html:
                print("✗ 页面被反爬虫拦截")
                return

            # 提取车辆信息
            vehicles = self.extract_vehicle_info(html)
            print(f"\n找到 {len(vehicles)} 辆车:")

            for idx, vehicle in enumerate(vehicles[:10], 1):
                print(f"  [{idx}] {vehicle['车辆名称']}")

            return vehicles
        return None

    def test_detail_page(self):
        """测试详情页"""
        url = "https://www.jdcsww.com/qcggdetail?bh=SV2026031300004"
        print(f"\n正在请求详情页: {url}")

        html = self.fetch_page(url)
        if html:
            print(f"✓ 详情页获取成功，长度: {len(html)} 字符")

            # 检查是否被拦截
            if '非正常访问' in html or '爬取数据嫌疑' in html:
                print("✗ 详情页被反爬虫拦截")
                print("建议：需要使用 Selenium 模拟真实浏览器")
                return None

            # 保存详情页用于分析
            with open('data/detail_page_sample.html', 'w', encoding='utf-8') as f:
                f.write(html)
            print("✓ 详情页已保存到 data/detail_page_sample.html")
            return True
        return None


def main():
    """主函数"""
    print("=" * 60)
    print("汽车公告爬虫测试")
    print("=" * 60)

    crawler = SimpleCrawler()

    # 测试1: 列表页
    print("\n【测试1】获取列表页...")
    vehicles = crawler.test_list_page()

    # 测试2: 详情页
    print("\n【测试2】获取详情页...")
    result = crawler.test_detail_page()

    print("\n" + "=" * 60)
    if vehicles:
        print(f"✓ 列表页测试成功，找到 {len(vehicles)} 辆车")
    else:
        print("✗ 列表页测试失败")

    if result:
        print("✓ 详情页测试成功")
    else:
        print("✗ 详情页测试失败（可能需要使用 Selenium）")

    print("=" * 60)


if __name__ == "__main__":
    main()
