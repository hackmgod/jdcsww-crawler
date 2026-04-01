#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
汽车公告爬虫 - 最终版
根据实际页面结构编写
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

        # 提取每个车辆块
        # 根据实际结构：每个车辆在一个 <li> 标签中
        vehicle_pattern = r'<li[^>]*>.*?<span class="car_name"><a href="([^"]+)"[^>]*>([^<]+)</a></span>.*?</li>'
        vehicle_matches = re.findall(vehicle_pattern, html, re.DOTALL)

        print(f"解析到 {len(vehicle_matches)} 条车辆信息")

        for idx, match in enumerate(vehicle_matches, 1):
            detail_link, car_name = match

            vehicle = {
                '序号': idx,
                '车辆名称': car_name.strip(),
                '详情链接': f"{self.base_url}{detail_link}",
            }

            # 提取公告编号
            bh_match = re.search(r'bh=([^&"\']+)', detail_link)
            if bh_match:
                vehicle['公告编号'] = bh_match.group(1)

            vehicles.append(vehicle)
            print(f"  [{idx}] {vehicle['车辆名称']}")

        return vehicles

    def parse_vehicle_details(self, html: str, vehicle_info: Dict) -> Dict:
        """从列表页HTML中提取车辆的详细信息"""
        # 查找包含该车辆详情链接的部分
        detail_link = vehicle_info['详情链接'].replace(self.base_url, '')
        detail_link_escaped = detail_link.replace('?', r'\?').replace('&', r'\&')

        # 提取该车辆的完整信息块
        vehicle_block_pattern = rf'<li[^>]*>.*?<a href="{re.escape(detail_link)}".*?</li>'
        vehicle_block_match = re.search(vehicle_block_pattern, html, re.DOTALL)

        if not vehicle_block_match:
            return vehicle_info

        block = vehicle_block_match.group(0)

        # 提取车辆型号
        model_pattern = r'<span class="car_model">([^<]+?)</span>'
        models = re.findall(model_pattern, block)
        if models:
            vehicle_info['公告型号'] = models[0].strip()

        # 提取发布时间
        publish_pattern = r'<span class="car_publish">发布时间：(\d{4}-\d{2}-\d{2})</span>'
        publish_match = re.search(publish_pattern, block)
        if publish_match:
            vehicle_info['发布时间'] = publish_match.group(1)

        # 提取所有label信息
        label_pattern = r'<label>([^<]+?)：([^<]+?)</label>'
        for label_match in re.finditer(label_pattern, block):
            key = label_match.group(1).strip()
            value = label_match.group(2).strip()

            if value:  # 只保存非空值
                vehicle_info[key] = value

        # 提取外形尺寸和货箱尺寸
        size_pattern = r'车辆外形长宽高\(mm\)：([^<\n]+?)(?:<|$)'
        size_match = re.search(size_pattern, block)
        if size_match:
            vehicle_info['车辆外形长宽高(mm)'] = size_match.group(1).strip()

        box_pattern = r'货箱长宽高：([^<\n]+?)(?:<|$)'
        box_match = re.search(box_pattern, block)
        if box_match:
            vehicle_info['货箱长宽高(mm)'] = box_match.group(1).strip()

        # 提取生产企业
        company_pattern = r'车辆生产企业名称：([^<\n]+?)(?:<|$)'
        company_match = re.search(company_pattern, block)
        if company_match:
            vehicle_info['生产企业'] = company_match.group(1).strip()

        return vehicle_info

    def get_detail_with_selenium(self, detail_url: str) -> Optional[Dict]:
        """使用 Selenium 获取详情页"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options

            # 配置 Chrome
            chrome_options = Options()
            chrome_options.add_argument('--headless')  # 无头模式
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_argument('--log-level=3')
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
            print(f"  ✗ Selenium 未安装")
            return None
        except Exception as e:
            print(f"  ✗ Selenium 获取详情页失败: {e}")
            return None

    def parse_detail_page(self, html: str) -> Dict:
        """解析详情页"""
        detail = {}

        # 提取表格数据
        table_pattern = r'<tr[^>]*>.*?<td[^>]*>([^<]+?)</td>.*?<td[^>]*>([^<]+?)(?:<span|</td|</tr)'
        for match in re.finditer(table_pattern, html, re.DOTALL):
            key = match.group(1).strip().rstrip('：')
            value = match.group(2).strip()

            if value and value != '&nbsp;':
                detail[key] = value

        return detail

    def save_json(self, data: List[Dict], filename: str):
        """保存为 JSON"""
        os.makedirs('data', exist_ok=True)
        filepath = os.path.join('data', filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"✓ 数据已保存到: {filepath}")
        return filepath

    def run(self, batch: int = 403, fetch_details: bool = False, detail_limit: int = 5):
        """运行爬虫"""
        print("=" * 70)
        print("汽车公告数据爬虫")
        print("=" * 70)

        # 1. 获取列表页
        html = self.get_list_page(batch=batch)
        if not html:
            print("✗ 获取列表页失败")
            return

        # 2. 解析基本信息
        vehicles = self.parse_list_page(html)
        if not vehicles:
            print("✗ 未找到车辆信息")
            return

        # 3. 从列表页提取详细信息
        print(f"\n正在提取详细信息...")
        detailed_vehicles = []
        for vehicle in vehicles:
            detailed_vehicle = self.parse_vehicle_details(html, vehicle)
            detailed_vehicles.append(detailed_vehicle)

        # 4. 保存列表数据
        self.save_json(detailed_vehicles, f'vehicle_list_batch{batch}.json')
        print(f"\n✓ 列表数据: {len(detailed_vehicles)} 条")

        # 5. 获取详情页（可选）
        if fetch_details:
            print(f"\n开始获取详情页（前 {detail_limit} 条）...")
            detail_data = []

            for idx, vehicle in enumerate(detailed_vehicles[:detail_limit], 1):
                print(f"\n[{idx}/{detail_limit}] {vehicle['车辆名称']}")

                if vehicle.get('详情链接'):
                    detail = self.get_detail_with_selenium(vehicle['详情链接'])
                    if detail:
                        # 合并列表和详情数据
                        merged_data = {**vehicle, **detail}
                        detail_data.append(merged_data)

                    # 延迟
                    time.sleep(2)

            # 6. 保存详情数据
            if detail_data:
                self.save_json(detail_data, f'vehicle_details_batch{batch}.json')
                print(f"\n✓ 详情数据: {len(detail_data)} 条")

        print("\n" + "=" * 70)
        print("✓ 爬取完成！")
        print(f"✓ 数据已保存在 data/ 目录")
        print("=" * 70)


def main():
    """主函数"""
    crawler = CarAnnouncementCrawler()

    # 运行爬虫
    # batch: 公告批次
    # fetch_details: 是否获取详情页（需要Selenium）
    # detail_limit: 详情页数量
    crawler.run(
        batch=403,
        fetch_details=False,  # 先不获取详情页，因为需要Selenium
        detail_limit=3
    )


if __name__ == "__main__":
    main()
