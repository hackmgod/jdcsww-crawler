#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整版爬虫 - 使用Selenium获取详情页和图片
"""

import urllib.request
import urllib.parse
import json
import time
import re
import os
from datetime import datetime
from typing import List, Dict, Optional


class FullDataCrawler:
    """完整数据爬虫 - 包含详情页和图片"""

    def __init__(self):
        self.base_url = "https://www.jdcsww.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
        }

        # 图片保存目录
        self.image_dir = 'data/vehicle_images'
        os.makedirs(self.image_dir, exist_ok=True)

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

    def get_detail_with_selenium(self, detail_url: str, vehicle_info: Dict) -> Optional[Dict]:
        """使用 Selenium 获取详情页完整数据"""
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
            chrome_options.add_argument('--log-level=3')
            chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36')

            print(f"  正在获取详情页...")
            driver = webdriver.Chrome(options=chrome_options)

            try:
                # 先访问主页建立 session
                driver.get(f"{self.base_url}/qcgg")
                time.sleep(2)

                # 访问详情页
                driver.get(detail_url)
                time.sleep(4)

                # 检查是否被拦截
                page_text = driver.page_source
                if '非正常访问' in page_text or '爬取数据嫌疑' in page_text:
                    print(f"  ✗ 详情页被拦截")
                    return None

                # 解析详情页数据
                detail = self.parse_detail_page(page_text)

                # 下载车辆图片
                images = self.download_vehicle_images(driver, vehicle_info)

                if images:
                    detail['车辆图片'] = images

                # 合并数据
                detail['详情页URL'] = detail_url
                full_data = {**vehicle_info, **detail}

                print(f"  ✓ 详情页获取成功（包含{len(images)}张图片）")
                return full_data

            finally:
                driver.quit()

        except ImportError:
            print(f"  ✗ Selenium 未安装，请运行: pip install selenium")
            return None
        except Exception as e:
            print(f"  ✗ 获取详情页失败: {e}")
            return None

    def parse_detail_page(self, html: str) -> Dict:
        """解析详情页HTML"""
        detail = {}

        # 提取表格数据 - 基本信息表格
        table_pattern = r'<tr[^>]*>.*?<td[^>]*width="20%"[^>]*>([^<]+?)</td>.*?<td[^>]*>([^<]+?)(?:<span|</td|</tr)'
        for match in re.finditer(table_pattern, html, re.DOTALL):
            key = match.group(1).strip().rstrip('：')
            value = match.group(2).strip()

            if value and value != '&nbsp;':
                detail[key] = value

        # 提取三电参数（电芯、电池、电机、电控）
        # 这些参数通常在特定的div或table中
        detail_sections = {
            '电芯参数': [],
            '电池信息': [],
            '电机信息': [],
            '电控系统': []
        }

        for section_name in detail_sections.keys():
            # 查找该部分的标题
            section_pattern = rf'{section_name}.*?<(?:table|div|tbody)[^>]*>(.*?)</(?:table|div|tbody)>'
            section_match = re.search(section_pattern, html, re.DOTALL)

            if section_match:
                section_content = section_match.group(1)

                # 提取该部分的所有参数
                param_pattern = r'([^<>：]+?)：([^<>]+?)(?:<br|<|$)'
                for param_match in re.finditer(param_pattern, section_content, re.DOTALL):
                    param_key = param_match.group(1).strip()
                    param_value = param_match.group(2).strip()

                    # 清理HTML标签
                    param_value = re.sub(r'<[^>]+>', '', param_value)
                    param_value = param_value.replace('&nbsp;', '').strip()

                    if param_key and param_value:
                        full_key = f"{section_name}_{param_key}"
                        detail[full_key] = param_value

        return detail

    def download_vehicle_images(self, driver, vehicle_info: Dict) -> List[str]:
        """下载车辆图片"""
        images = []

        try:
            # 查找所有图片元素
            img_elements = driver.find_elements(By.CSS_SELECTOR, "img[src*='ufileos'], img[src*='jdcsww']")

            bh = vehicle_info.get('公告编号', 'unknown')
            vehicle_name = vehicle_info.get('车辆名称', 'unknown')

            for idx, img in enumerate(img_elements, 1):
                try:
                    img_url = img.get_attribute('src')

                    if not img_url or img_url.startswith('data:'):
                        continue

                    # 构造图片文件名
                    ext = os.path.splitext(img_url)[1] or '.jpg'
                    filename = f"{bh}_{vehicle_name}_{idx}{ext}"
                    # 清理文件名中的特殊字符
                    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
                    filepath = os.path.join(self.image_dir, filename)

                    # 下载图片
                    try:
                        req = urllib.request.Request(img_url, headers=self.headers)
                        with urllib.request.urlopen(req, timeout=10) as response:
                            with open(filepath, 'wb') as f:
                                f.write(response.read())

                        images.append(filepath)
                        print(f"    ✓ 图片已下载: {filename}")
                    except Exception as e:
                        print(f"    ✗ 图片下载失败: {img_url}")

                except Exception as e:
                    continue

        except Exception as e:
            print(f"  ✗ 图片下载出错: {e}")

        return images

    def save_json(self, data: List[Dict], filename: str):
        """保存为JSON"""
        os.makedirs('data', exist_ok=True)
        filepath = os.path.join('data', filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"✓ 数据已保存到: {filepath}")
        return filepath

    def run(self, batch: int = 403, detail_limit: int = 3):
        """运行爬虫"""
        print("=" * 70)
        print("汽车公告完整数据爬虫（详情页+图片）")
        print("=" * 70)

        # 1. 获取列表页
        print(f"\n正在获取批次 {batch} 的列表页...")
        html = self.get_list_page(batch=batch)
        if not html:
            print("✗ 获取列表页失败")
            return

        # 2. 解析列表信息
        vehicles = self.parse_list_page(html, batch)
        if not vehicles:
            print("✗ 未找到车辆信息")
            return

        print(f"✓ 找到 {len(vehicles)} 条车辆信息")

        # 3. 提取列表中的详细信息
        print(f"\n正在提取列表详细信息...")
        for vehicle in vehicles:
            vehicle = self.parse_vehicle_details(html, vehicle)

        # 4. 保存列表数据
        self.save_json(vehicles, f'vehicle_list_batch{batch}.json')

        # 5. 获取详情页和图片
        print(f"\n开始获取详情页和图片（前 {detail_limit} 条）...")
        full_data = []

        for idx, vehicle in enumerate(vehicles[:detail_limit], 1):
            print(f"\n[{idx}/{detail_limit}] {vehicle['车辆名称']}")
            print(f"  公告编号: {vehicle.get('公告编号', 'N/A')}")

            if vehicle.get('详情链接'):
                detail_data = self.get_detail_with_selenium(vehicle['详情链接'], vehicle)
                if detail_data:
                    full_data.append(detail_data)

            # 延迟
            time.sleep(3)

        # 6. 保存完整数据
        if full_data:
            self.save_json(full_data, f'vehicle_full_data_batch{batch}.json')

            print("\n" + "=" * 70)
            print(f"✓ 爬取完成！")
            print(f"✓ 列表数据: {len(vehicles)} 条")
            print(f"✓ 详情数据: {len(full_data)} 条")
            print(f"✓ 图片保存在: {self.image_dir}/")
            print("=" * 70)

            # 显示统计
            total_images = sum(len(v.get('车辆图片', [])) for v in full_data)
            print(f"\n【统计信息】")
            print(f"  总计下载图片: {total_images} 张")

        return full_data


def main():
    """主函数"""
    crawler = FullDataCrawler()

    # 运行爬虫
    crawler.run(
        batch=403,          # 批次号
        detail_limit=2      # 获取前2条的详情页和图片
    )


if __name__ == "__main__":
    main()
