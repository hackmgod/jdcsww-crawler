#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整版汽车公告爬虫
使用 requests 获取列表页 + selenium 获取详情页
"""

import urllib.request
import urllib.parse
import json
import time
import re
import os
from datetime import datetime
from typing import List, Dict, Optional


class CarAnnouncementCrawler:
    """汽车公告爬虫"""

    def __init__(self):
        self.base_url = "https://www.jdcsww.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
        }

    def fetch_html(self, url: str) -> Optional[str]:
        """获取页面HTML"""
        try:
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=30) as response:
                return response.read().decode('utf-8')
        except Exception as e:
            print(f"  ✗ 获取页面失败: {e}")
            return None

    def get_list_page(self, batch: int = 403, vehicle_type: int = 1, fuel_type: str = 'C') -> Optional[str]:
        """获取列表页"""
        url = f"{self.base_url}/qcggs"
        params = {
            'ggxh': '',
            'ggpc': str(batch),
            'zwpp': '',
            'clmc': str(vehicle_type),
            'fdjxh': '',
            'qymc': '',
            'cph': '',
            'rylx': fuel_type,
            'viewtype': '0'
        }

        full_url = f"{url}?{urllib.parse.urlencode(params)}"
        print(f"正在获取批次 {batch} 的列表页...")

        return self.fetch_html(full_url)

    def parse_list_page(self, html: str) -> List[Dict]:
        """解析列表页"""
        vehicles = []

        # 提取详情链接
        detail_links = re.findall(r'href="(/qcggdetail\?bh=([^"]+))"', html)
        print(f"找到 {len(detail_links)} 个详情链接")

        # 提取车辆信息块
        # 使用正则匹配每个车辆条目
        vehicle_pattern = r'<li[^>]*>.*?<h4[^>]*>.*?####\s+([^\n]+?)\s+公告属性：\s+发布时间：(\d{4}-\d{2}-\d{2})(.*?)</li>'
        vehicle_matches = re.findall(vehicle_pattern, html, re.DOTALL)

        print(f"解析到 {len(vehicle_matches)} 条车辆信息")

        for idx, match in enumerate(vehicle_matches, 1):
            title, publish_date, info_block = match

            vehicle = {
                '序号': idx,
                '车辆名称': title.strip(),
                '发布时间': publish_date,
                '详情链接': '',
                '公告编号': '',
            }

            # 提取详情链接
            if idx <= len(detail_links):
                link, bh = detail_links[idx - 1]
                vehicle['详情链接'] = f"{self.base_url}{link}"
                vehicle['公告编号'] = bh

            # 提取其他信息
            info_pattern = r'([^：]+?)：([^<\n]+?)(?:<br|\n|$)'
            for info_match in re.finditer(info_pattern, info_block):
                key = info_match.group(1).strip()
                value = info_match.group(2).strip()

                if '公告批次' in key:
                    vehicle['公告批次'] = value
                elif '额定载质量' in key:
                    vehicle['额定载质量(KG)'] = value
                elif '轴数' in key:
                    vehicle['轴数'] = value
                elif '额定载客' in key:
                    vehicle['额定载客(人)'] = value
                elif '燃料类型' in key:
                    vehicle['燃料类型'] = value
                elif '车辆外形' in key:
                    vehicle['外形尺寸(mm)'] = value
                elif '货箱' in key:
                    vehicle['货箱尺寸(mm)'] = value
                elif '车辆生产企业名称' in key:
                    vehicle['生产企业'] = value

            vehicles.append(vehicle)
            print(f"  [{idx}] {vehicle['车辆名称']} - {vehicle.get('生产企业', '')}")

        return vehicles

    def get_detail_with_selenium(self, detail_url: str) -> Optional[Dict]:
        """使用 Selenium 获取详情页"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC

            # 配置 Chrome
            chrome_options = Options()
            chrome_options.add_argument('--headless')  # 无头模式
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36')

            print(f"  正在使用 Selenium 获取详情页...")
            driver = webdriver.Chrome(options=chrome_options)

            try:
                # 先访问主页建立 session
                driver.get(f"{self.base_url}/qcgg")
                time.sleep(2)

                # 访问详情页
                driver.get(detail_url)
                time.sleep(3)

                # 检查是否被拦截
                page_text = driver.page_source
                if '非正常访问' in page_text or '爬取数据嫌疑' in page_text:
                    print(f"  ✗ 详情页被拦截")
                    return None

                # 解析详情页
                detail = self.parse_detail_page(page_text)
                detail['详情页URL'] = detail_url

                print(f"  ✓ 详情页获取成功")
                return detail

            finally:
                driver.quit()

        except ImportError:
            print(f"  ✗ Selenium 未安装，请运行: pip install selenium")
            print(f"  同时需要安装 ChromeDriver")
            return None
        except Exception as e:
            print(f"  ✗ Selenium 获取详情页失败: {e}")
            return None

    def parse_detail_page(self, html: str) -> Dict:
        """解析详情页"""
        detail = {}

        # 提取表格数据
        table_pattern = r'<tr[^>]*>.*?<td[^>]*>([^<]+?)</td>.*?<td[^>]*>([^<]+?)</td>.*?</tr>'
        for match in re.finditer(table_pattern, html, re.DOTALL):
            key = match.group(1).strip()
            value = match.group(2).strip()

            # 清理标签和多余空白
            value = re.sub(r'<[^>]+>', '', value)
            value = value.strip()

            detail[key] = value

        return detail

    def save_json(self, data: List[Dict], filename: str):
        """保存为 JSON"""
        filepath = os.path.join('data', filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"✓ 数据已保存到: {filepath}")
        return filepath

    def run(self, batch: int = 403, fetch_details: bool = True, detail_limit: int = 5):
        """运行爬虫"""
        print("=" * 70)
        print("汽车公告数据爬虫")
        print("=" * 70)

        # 1. 获取列表页
        html = self.get_list_page(batch=batch)
        if not html:
            print("✗ 获取列表页失败")
            return

        # 2. 解析列表页
        vehicles = self.parse_list_page(html)
        if not vehicles:
            print("✗ 未找到车辆信息")
            return

        # 3. 保存列表数据
        self.save_json(vehicles, f'vehicle_list_batch{batch}.json')
        print(f"\n✓ 列表数据: {len(vehicles)} 条")

        # 4. 获取详情页
        if fetch_details:
            print(f"\n开始获取详情页（前 {detail_limit} 条）...")
            detail_data = []

            for idx, vehicle in enumerate(vehicles[:detail_limit], 1):
                print(f"\n[{idx}/{detail_limit}] {vehicle['车辆名称']}")

                if vehicle.get('详情链接'):
                    detail = self.get_detail_with_selenium(vehicle['详情链接'])
                    if detail:
                        # 合并列表和详情数据
                        merged_data = {**vehicle, **detail}
                        detail_data.append(merged_data)

                    # 延迟
                    time.sleep(2)

            # 5. 保存详情数据
            if detail_data:
                self.save_json(detail_data, f'vehicle_details_batch{batch}.json')
                print(f"\n✓ 详情数据: {len(detail_data)} 条")

        print("\n" + "=" * 70)
        print("✓ 爬取完成！")
        print("=" * 70)


def main():
    """主函数"""
    crawler = CarAnnouncementCrawler()

    # 运行爬虫
    # batch: 公告批次
    # fetch_details: 是否获取详情页
    # detail_limit: 详情页数量（None=全部）
    crawler.run(
        batch=403,
        fetch_details=True,
        detail_limit=3  # 先测试3条
    )


if __name__ == "__main__":
    main()
