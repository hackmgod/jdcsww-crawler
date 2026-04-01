#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用 undetected-chromedriver 获取详情页
专门用于绕过反爬虫检测
"""

import urllib.request
import urllib.parse
import json
import time
import re
import os
from datetime import datetime
from typing import List, Dict, Optional


class UndetectedCrawler:
    """使用 undetected-chromedriver 的爬虫"""

    def __init__(self):
        self.base_url = "https://www.jdcsww.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }

        self.image_dir = 'data/vehicle_images'
        os.makedirs(self.image_dir, exist_ok=True)

    def get_list_page(self, batch: int = 403) -> Optional[str]:
        """获取列表页"""
        url = f"{self.base_url}/qcggs"
        params = {
            'ggxh': '',
            'ggpc': str(batch),
            'zwpp': '',
            'clmc': '1',
            'fdjxh': '',
            'qymc': '',
            'cph': '',
            'rylx': 'C',
            'viewtype': '0'
        }

        full_url = f"{url}?{urllib.parse.urlencode(params)}"
        try:
            headers = self.headers.copy()
            headers['Accept-Encoding'] = 'identity'
            req = urllib.request.Request(full_url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as response:
                return response.read().decode('utf-8', errors='ignore')
        except Exception as e:
            print(f"✗ 获取列表页失败: {e}")
            return None

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

            # 提取详细信息
            detail_link_escaped = re.escape(detail_link)
            vehicle_block_pattern = rf'<li[^>]*>.*?<a href="{detail_link_escaped}".*?</li>'
            vehicle_block_match = re.search(vehicle_block_pattern, html, re.DOTALL)

            if vehicle_block_match:
                block = vehicle_block_match.group(0)

                # 车型号
                model_pattern = r'<span class="car_model">([^<]+?)</span>'
                models = re.findall(model_pattern, block)
                if models:
                    vehicle['公告型号'] = models[0].strip()

                # 发布时间
                publish_pattern = r'<span class="car_publish">发布时间：(\d{4}-\d{2}-\d{2})</span>'
                publish_match = re.search(publish_pattern, block)
                if publish_match:
                    vehicle['发布时间'] = publish_match.group(1)

                # Label信息
                label_pattern = r'<label>([^<]+?)：([^<]+?)</label>'
                for label_match in re.finditer(label_pattern, block):
                    key = label_match.group(1).strip()
                    value = label_match.group(2).strip()
                    if value:
                        vehicle[key] = value

                # 生产企业
                company_pattern = r'车辆生产企业名称：([^<\n]+?)(?:<|$)'
                company_match = re.search(company_pattern, block)
                if company_match:
                    vehicle['生产企业'] = company_match.group(1).strip()

            vehicles.append(vehicle)

        return vehicles

    def get_detail_with_undetected(self, detail_url: str, vehicle_info: Dict) -> Optional[Dict]:
        """使用 undetected-chromedriver 获取详情页"""
        try:
            import undetected_chromedriver as uc
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC

            print(f"  正在使用 undetected-chromedriver 获取详情页...")

            # 配置选项
            options = uc.ChromeOptions()

            # 使用无头模式（新版本）
            options.add_argument('--headless=new')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--log-level=3')

            # 创建 driver
            driver = uc.Chrome(options=options, version_main=145)

            try:
                # 1. 访问主页
                print(f"    [1/3] 访问主页建立会话...")
                driver.get(f"{self.base_url}/qcgg")
                time.sleep(3)

                # 2. 访问详情页
                print(f"    [2/3] 访问详情页...")
                driver.get(detail_url)

                # 等待页面加载
                time.sleep(5)

                # 检查是否被拦截
                page_text = driver.page_source
                if '非正常访问' in page_text or '爬取数据嫌疑' in page_text:
                    print(f"    ✗ 仍被拦截")
                    return None

                print(f"    ✓ 成功访问详情页！")

                # 3. 解析数据
                print(f"    [3/3] 解析数据...")
                detail = self.parse_detail_page(page_text)

                # 4. 下载图片
                images = self.download_images(driver, vehicle_info)
                if images:
                    detail['车辆图片'] = images

                # 合并数据
                detail['详情页URL'] = detail_url
                detail['爬取时间'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                full_data = {**vehicle_info, **detail}

                print(f"  ✓ 详情页获取成功（{len(detail)}个字段，{len(images)}张图片）")
                return full_data

            finally:
                driver.quit()

        except Exception as e:
            print(f"  ✗ 获取详情页失败: {e}")
            import traceback
            traceback.print_exc()
            return None

    def parse_detail_page(self, html: str) -> Dict:
        """解析详情页"""
        detail = {}

        # 保存HTML
        with open('data/detail_page_success.html', 'w', encoding='utf-8') as f:
            f.write(html)

        # 方法1: 提取表格数据（基本信息）
        table_pattern = r'<tr[^>]*>.*?<td[^>]*width="20%"[^>]*>([^<]+?)</td>.*?<td[^>]*>([^<]+?)(?:<span|</td|</tr)'
        for match in re.finditer(table_pattern, html, re.DOTALL):
            key = match.group(1).strip().rstrip('：')
            value = match.group(2).strip()

            if value and value not in ['&nbsp;', '', '-']:
                detail[key] = value

        # 方法2: 提取三电参数
        sections = ['电芯参数', '电池信息', '电机信息', '电控系统']

        for section in sections:
            # 查找该部分的所有文本
            section_pattern = rf'{section}[^<]*</table>.*?</table>'
            section_match = re.search(section_pattern, html, re.DOTALL)

            if section_match:
                section_text = section_match.group(0)

                # 提取键值对
                kv_pattern = r'([^<>：\t]+?)[:：]\s*([^\t\n<]+?)(?=\n|<br|<|$)'
                for kv_match in re.finditer(kv_pattern, section_text):
                    key = kv_match.group(1).strip()
                    value = kv_match.group(2).strip()

                    # 清理
                    value = re.sub(r'<[^>]+>', '', value)
                    value = value.replace('&nbsp;', '').strip()

                    if key and value and value not in ['-', '', '/']:
                        full_key = f"{section}_{key}"
                        detail[full_key] = value

        return detail

    def download_images(self, driver, vehicle_info: Dict) -> List[str]:
        """下载图片"""
        images = []

        try:
            img_elements = driver.find_elements(By.TAG_NAME, "img")

            bh = vehicle_info.get('公告编号', 'unknown')
            vehicle_name = vehicle_info.get('车辆名称', 'unknown')
            vehicle_name = re.sub(r'[<>:"/\\|?*]', '_', vehicle_name)[:30]

            for idx, img in enumerate(img_elements, 1):
                try:
                    img_url = img.get_attribute('src')

                    if not img_url or img_url.startswith('data:'):
                        continue

                    # 过滤车辆图片
                    if any(x in img_url.lower() for x in ['ufileos', 'jdcsww']):
                        try:
                            # 下载
                            ext = os.path.splitext(img_url.split('?')[0])[1] or '.jpg'
                            filename = f"{bh}_{vehicle_name}_{idx}{ext}"
                            filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
                            filepath = os.path.join(self.image_dir, filename)

                            req = urllib.request.Request(img_url, headers=self.headers)
                            with urllib.request.urlopen(req, timeout=10) as response:
                                with open(filepath, 'wb') as f:
                                    f.write(response.read())

                            images.append(filepath)
                            print(f"    ✓ 图片 {idx}: {filename}")

                        except Exception as e:
                            print(f"    ✗ 图片 {idx} 下载失败")

                except Exception:
                    continue

        except Exception as e:
            print(f"  ✗ 图片下载出错: {e}")

        return images

    def save_json(self, data: List[Dict], filename: str):
        """保存JSON"""
        os.makedirs('data', exist_ok=True)
        filepath = os.path.join('data', filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"✓ 数据已保存到: {filepath}")
        return filepath

    def run(self, batch: int = 403, detail_limit: int = 2):
        """运行爬虫"""
        print("=" * 70)
        print("详情页爬虫 - 使用 undetected-chromedriver")
        print("=" * 70)

        # 1. 获取列表
        print(f"\n正在获取批次 {batch} 的列表...")
        html = self.get_list_page(batch)
        if not html:
            print("✗ 获取列表失败")
            return

        vehicles = self.parse_list_page(html, batch)
        print(f"✓ 找到 {len(vehicles)} 条车辆信息")

        # 2. 获取详情
        print(f"\n开始获取详情页和图片（前 {detail_limit} 条）...")
        full_data = []

        for idx, vehicle in enumerate(vehicles[:detail_limit], 1):
            print(f"\n{'='*60}")
            print(f"[{idx}/{detail_limit}] {vehicle['车辆名称']}")
            print(f"{'='*60}")
            print(f"公告编号: {vehicle.get('公告编号', 'N/A')}")
            print(f"公告型号: {vehicle.get('公告型号', 'N/A')}")

            if vehicle.get('详情链接'):
                detail_data = self.get_detail_with_undetected(
                    vehicle['详情链接'],
                    vehicle
                )
                if detail_data:
                    full_data.append(detail_data)

                    # 显示部分详情数据
                    print(f"\n📊 详情数据预览:")
                    for key in list(detail_data.keys())[:10]:
                        if key not in ['序号', '批次', '车辆名称', '详情链接', '详情页URL']:
                            print(f"  {key}: {detail_data[key]}")

            # 延迟
            if idx < detail_limit:
                print(f"\n⏱️  等待 8 秒...")
                time.sleep(8)

        # 3. 保存数据
        if full_data:
            self.save_json(full_data, f'vehicle_details_complete_batch{batch}.json')

            print("\n" + "=" * 70)
            print(f"✅ 爬取完成！")
            print(f"✓ 列表数据: {len(vehicles)} 条")
            print(f"✓ 详情数据: {len(full_data)} 条")

            total_images = sum(len(v.get('车辆图片', [])) for v in full_data)
            print(f"✓ 车辆图片: {total_images} 张")
            print(f"✓ 图片目录: {self.image_dir}/")
            print("=" * 70)

            # 统计
            print(f"\n📈 数据统计:")
            for vehicle in full_data:
                print(f"\n  {vehicle['车辆名称']}:")
                print(f"    - 详情字段数: {len([k for k in vehicle.keys() if k not in ['序号', '批次', '车辆名称', '详情链接']])}")
                print(f"    - 图片数量: {len(vehicle.get('车辆图片', []))}")

        return full_data


def main():
    """主函数"""
    crawler = UndetectedCrawler()

    crawler.run(
        batch=403,
        detail_limit=2  # 先测试2条
    )


if __name__ == "__main__":
    main()
