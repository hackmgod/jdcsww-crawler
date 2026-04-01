#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
汽车公告数据爬虫
司机宝宝网 (jdcsww.com) 数据采集工具
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import random
from typing import List, Dict, Optional
import os
from datetime import datetime


class JdcswwCrawler:
    """汽车公告爬虫类"""

    def __init__(self):
        self.base_url = "https://www.jdcsww.com"
        self.session = requests.Session()

        # 真实浏览器请求头
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        }

        # 设置 session 请求头
        self.session.headers.update(self.headers)

    def get_list_page(self, batch: int = 403, vehicle_type: int = 1, fuel_type: str = 'C') -> Optional[str]:
        """
        获取列表页面 HTML

        Args:
            batch: 公告批次 (默认403)
            vehicle_type: 车辆类型 (默认1=纯电动)
            fuel_type: 燃料类型 (默认C=纯电动)

        Returns:
            页面 HTML 内容或 None
        """
        url = f"{self.base_url}/qcggs"
        params = {
            'ggxh': '',        # 车辆公告型号
            'ggpc': batch,     # 公告批次
            'zwpp': '',        # 车辆中文品牌
            'clmc': vehicle_type,  # 车辆类型
            'fdjxh': '',       # 发动机型号
            'qymc': '',        # 生产企业名称
            'cph': '',         # 公告产品号
            'rylx': fuel_type, # 燃料类型
            'viewtype': '0'    # 列表显示
        }

        try:
            print(f"正在获取批次 {batch} 的列表页...")
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            print(f"✓ 列表页获取成功 (状态码: {response.status_code})")
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"✗ 列表页获取失败: {e}")
            return None

    def parse_list_page(self, html: str) -> List[Dict]:
        """
        解析列表页面，提取车辆信息

        Args:
            html: 列表页 HTML 内容

        Returns:
            车辆信息列表
        """
        soup = BeautifulSoup(html, 'lxml')
        vehicles = []

        # 查找所有车辆条目
        # 根据页面结构分析，车辆信息在特定的 div 中
        vehicle_items = soup.find_all('div', class_='list-item') or \
                       soup.select('.qcgg-list-item') or \
                       soup.find_all('li', class_='list-group-item')

        print(f"找到 {len(vehicle_items)} 条车辆记录")

        for idx, item in enumerate(vehicle_items, 1):
            try:
                vehicle = {
                    '序号': idx,
                    '车辆名称': '',
                    '公告型号': '',
                    '发布时间': '',
                    '公告批次': '',
                    '额定载质量': '',
                    '轴数': '',
                    '额定载客': '',
                    '燃料类型': '',
                    '外形尺寸': '',
                    '货箱尺寸': '',
                    '生产企业': '',
                    '详情链接': ''
                }

                # 提取车辆名称和型号
                title_elem = item.find('h3') or item.find('h4') or item.find('strong')
                if title_elem:
                    title_text = title_elem.get_text(strip=True)
                    vehicle['车辆名称'] = title_text

                    # 尝试提取公告型号
                    link = title_elem.find('a', href=True)
                    if link:
                        vehicle['详情链接'] = link['href']
                        if link['href'].startswith('/'):
                            vehicle['详情链接'] = self.base_url + link['href']

                # 提取其他信息
                info_rows = item.find_all('p') or item.find_all('div', class_='info-row')
                for row in info_rows:
                    text = row.get_text(strip=True)
                    if '发布时间' in text:
                        vehicle['发布时间'] = text.split('：')[-1] if '：' in text else ''
                    elif '公告批次' in text:
                        vehicle['公告批次'] = text.split('：')[-1] if '：' in text else ''
                    elif '额定载质量' in text:
                        vehicle['额定载质量'] = text.split('：')[-1] if '：' in text else ''
                    elif '轴数' in text:
                        vehicle['轴数'] = text.split('：')[-1] if '：' in text else ''
                    elif '生产企业' in text:
                        vehicle['生产企业'] = text.split('：')[-1] if '：' in text else ''
                    elif '外形' in text:
                        vehicle['外形尺寸'] = text.split('：')[-1] if '：' in text else ''

                vehicles.append(vehicle)
                print(f"  [{idx}] {vehicle['车辆名称']} - {vehicle['生产企业']}")

            except Exception as e:
                print(f"  ✗ 解析第 {idx} 条记录时出错: {e}")
                continue

        return vehicles

    def get_detail_page(self, detail_url: str) -> Optional[Dict]:
        """
        获取详情页面数据

        Args:
            detail_url: 详情页 URL

        Returns:
            详情数据字典或 None
        """
        try:
            print(f"  正在获取详情页: {detail_url}")
            response = self.session.get(detail_url, timeout=30)

            # 检查是否被拦截
            if '非正常访问' in response.text or '爬取数据嫌疑' in response.text:
                print(f"  ✗ 详情页被反爬虫拦截")
                return None

            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'lxml')

            detail = {
                '详情页URL': detail_url,
                '车辆名称': '',
                '车辆类型': '',
                '制造国': '',
                '牌照类型': '',
                '公告批次': '',
                '发布日期': '',
                '产品号': '',
                '目录序号': '',
                '中文品牌': '',
                '英文品牌': '',
                '公告型号': '',
                '车型': '',
                '企业名称': '',
                '生产地址': '',
                '注册地址': '',
                '车辆总质量': '',
                '额定载质量': '',
                '整备质量': '',
                '最高车速': '',
                '外形尺寸': '',
                '货箱尺寸': '',
            }

            # 解析表格数据
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        key = cells[0].get_text(strip=True).rstrip('：')
                        value = cells[1].get_text(strip=True)

                        # 映射到字典
                        if '车辆名称' in key:
                            detail['车辆名称'] = value
                        elif '车辆类型' in key:
                            detail['车辆类型'] = value
                        elif '公告型号' in key:
                            detail['公告型号'] = value
                        elif '企业名称' in key:
                            detail['企业名称'] = value
                        elif '车辆总质量' in key:
                            detail['车辆总质量'] = value
                        elif '额定载质量' in key:
                            detail['额定载质量'] = value
                        elif '整备质量' in key:
                            detail['整备质量'] = value
                        elif '最高车速' in key:
                            detail['最高车速'] = value

            print(f"  ✓ 详情页获取成功")
            return detail

        except Exception as e:
            print(f"  ✗ 详情页获取失败: {e}")
            return None

    def save_to_json(self, data: List[Dict], filename: str = None):
        """
        保存数据到 JSON 文件

        Args:
            data: 要保存的数据
            filename: 文件名（默认使用时间戳）
        """
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"jdcsww_data_{timestamp}.json"

        filepath = os.path.join(os.path.dirname(__file__), 'data', filename)

        # 创建 data 目录
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"\n✓ 数据已保存到: {filepath}")
        return filepath

    def random_delay(self, min_sec: float = 1, max_sec: float = 3):
        """随机延迟，避免频繁请求"""
        delay = random.uniform(min_sec, max_sec)
        print(f"  等待 {delay:.1f} 秒...")
        time.sleep(delay)


def main():
    """主函数"""
    print("=" * 60)
    print("汽车公告数据爬虫 - 司机宝宝网")
    print("=" * 60)

    crawler = JdcswwCrawler()

    # 配置爬取参数
    batch = 403  # 公告批次
    vehicle_type = 1  # 车辆类型
    fuel_type = 'C'  # 燃料类型 (C=纯电动)

    # 1. 获取列表页
    html = crawler.get_list_page(batch=batch, vehicle_type=vehicle_type, fuel_type=fuel_type)
    if not html:
        print("✗ 无法获取列表页，程序退出")
        return

    # 2. 解析列表页
    vehicles = crawler.parse_list_page(html)
    print(f"\n共解析到 {len(vehicles)} 条车辆信息")

    if not vehicles:
        print("✗ 未找到车辆信息")
        return

    # 3. 保存列表数据
    crawler.save_to_json(vehicles, 'vehicle_list.json')

    # 4. 获取详情页（可选，根据需要启用）
    print("\n开始获取详情页...")
    detail_data = []

    for idx, vehicle in enumerate(vehicles[:5], 1):  # 先测试前5条
        print(f"\n[{idx}/{min(5, len(vehicles))}] {vehicle['车辆名称']}")

        if vehicle.get('详情链接'):
            detail = crawler.get_detail_page(vehicle['详情链接'])
            if detail:
                detail.update(vehicle)  # 合并列表信息和详情信息
                detail_data.append(detail)

            # 延迟避免被封
            crawler.random_delay(2, 4)

    # 5. 保存详情数据
    if detail_data:
        crawler.save_to_json(detail_data, 'vehicle_details.json')
        print(f"\n成功获取 {len(detail_data)} 条详情数据")

    print("\n" + "=" * 60)
    print("爬取完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
