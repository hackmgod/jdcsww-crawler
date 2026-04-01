#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级爬虫 - 支持多批次爬取
"""

import urllib.request
import urllib.parse
import json
import time
import re
import os
from datetime import datetime
from typing import List, Dict, Optional


class AdvancedCarCrawler:
    """高级汽车公告爬虫"""

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

    def get_list_page(self, batch: int, vehicle_type: int = 1, fuel_type: str = 'C') -> Optional[str]:
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
        return self.fetch_html(full_url)

    def parse_list_page(self, html: str, batch: int) -> List[Dict]:
        """解析列表页"""
        vehicles = []

        vehicle_pattern = r'<li[^>]*>.*?<span class="car_name"><a href="([^"]+)"[^>]*>([^<]+)</a></span>.*?</li>'
        vehicle_matches = re.findall(vehicle_pattern, html, re.DOTALL)

        for idx, (detail_link, car_name) in enumerate(vehicle_matches, 1):
            vehicle = {
                '序号': idx,
                '批次': batch,
                '车辆名称': car_name.strip(),
                '详情链接': f"{self.base_url}{detail_link}",
            }

            bh_match = re.search(r'bh=([^&"\']+)', detail_link)
            if bh_match:
                vehicle['公告编号'] = bh_match.group(1)

            vehicles.append(vehicle)

        return vehicles

    def parse_vehicle_details(self, html: str, vehicle_info: Dict) -> Dict:
        """从列表页HTML中提取详细信息"""
        detail_link = vehicle_info['详情链接'].replace(self.base_url, '')
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

            if value:
                vehicle_info[key] = value

        # 提取尺寸
        size_pattern = r'车辆外形长宽高\(mm\)：([^<\n]+?)(?:<|$)'
        size_match = re.search(size_pattern, block)
        if size_match:
            vehicle_info['车辆外形长宽高(mm)'] = size_match.group(1).replace('&#215;', '×').strip()

        box_pattern = r'货箱长宽高：([^<\n]+?)(?:<|$)'
        box_match = re.search(box_pattern, block)
        if box_match:
            vehicle_info['货箱长宽高(mm)'] = box_match.group(1).replace('&#215;', '×').strip()

        # 提取生产企业
        company_pattern = r'车辆生产企业名称：([^<\n]+?)(?:<|$)'
        company_match = re.search(company_pattern, block)
        if company_match:
            vehicle_info['生产企业'] = company_match.group(1).strip()

        return vehicle_info

    def save_json(self, data: List[Dict], filename: str):
        """保存为JSON"""
        os.makedirs('data', exist_ok=True)
        filepath = os.path.join('data', filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return filepath

    def run_multiple_batches(self, start_batch: int, end_batch: int, delay: int = 3):
        """爬取多个批次"""
        print("=" * 70)
        print(f"汽车公告数据爬虫 - 多批次爬取")
        print(f"批次范围: {start_batch} -> {end_batch}")
        print("=" * 70)

        all_vehicles = []

        for batch in range(start_batch, end_batch - 1, -1):
            print(f"\n正在爬取批次 {batch}...")

            # 获取列表页
            html = self.get_list_page(batch=batch)
            if not html:
                print(f"  ✗ 批次 {batch} 获取失败")
                continue

            # 解析基本信息
            vehicles = self.parse_list_page(html, batch)
            if not vehicles:
                print(f"  ✗ 批次 {batch} 未找到数据")
                continue

            print(f"  ✓ 找到 {len(vehicles)} 条数据")

            # 提取详细信息
            detailed_vehicles = []
            for vehicle in vehicles:
                detailed_vehicle = self.parse_vehicle_details(html, vehicle)
                detailed_vehicles.append(detailed_vehicle)

            all_vehicles.extend(detailed_vehicles)

            # 保存单个批次
            self.save_json(detailed_vehicles, f'vehicle_list_batch{batch}.json')
            print(f"  ✓ 批次 {batch} 已保存")

            # 延迟
            if batch > end_batch:
                print(f"  等待 {delay} 秒...")
                time.sleep(delay)

        # 保存合并数据
        if all_vehicles:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'vehicle_all_batches_{start_batch}_to_{end_batch}_{timestamp}.json'
            self.save_json(all_vehicles, filename)

            print("\n" + "=" * 70)
            print(f"✓ 爬取完成！")
            print(f"✓ 总计: {len(all_vehicles)} 条数据")
            print(f"✓ 批次范围: {start_batch} - {end_batch}")
            print(f"✓ 数据已保存在 data/ 目录")
            print("=" * 70)

            # 统计信息
            print(f"\n【统计信息】")
            batch_stats = {}
            for v in all_vehicles:
                batch = v.get('批次', '未知')
                batch_stats[batch] = batch_stats.get(batch, 0) + 1

            for batch, count in sorted(batch_stats.items(), reverse=True):
                print(f"  批次 {batch}: {count} 条")

        return all_vehicles


def main():
    """主函数"""
    crawler = AdvancedCarCrawler()

    # 爬取多个批次
    # 例如：爬取403、402、401三个批次
    crawler.run_multiple_batches(
        start_batch=403,  # 起始批次
        end_batch=401,    # 结束批次
        delay=5           # 每批次间隔5秒
    )


if __name__ == "__main__":
    main()
