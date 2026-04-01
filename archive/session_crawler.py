#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
会话式爬虫 - 模拟真实用户访问流程
先访问列表页，再访问详情页
"""

import urllib.request
import urllib.parse
import json
import time
import re
import os
from datetime import datetime
from typing import List, Dict, Optional
from http.cookiejar import CookieJar


class SessionCrawler:
    """会话式爬虫 - 保持 Cookie 和 Referer"""

    def __init__(self):
        self.base_url = "https://www.jdcsww.com"

        # 创建 CookieJar 来保存 cookies
        self.cookie_jar = CookieJar()

        # 使用 opener 来自动处理 cookies
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.cookie_jar)
        )

        self.image_dir = 'data/vehicle_images'
        os.makedirs(self.image_dir, exist_ok=True)

    def fetch_with_session(self, url: str, referer: str = None) -> Optional[str]:
        """使用会话获取页面（保持 Cookie 和 Referer）"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'identity',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }

            # 添加 Referer
            if referer:
                headers['Referer'] = referer

            req = urllib.request.Request(url, headers=headers)

            with self.opener.open(req, timeout=30) as response:
                return response.read().decode('utf-8', errors='ignore')

        except Exception as e:
            print(f"    ✗ 获取失败: {e}")
            return None

    def get_list_page(self, batch: int = 385) -> Optional[str]:
        """第一步：访问列表页，建立会话"""
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

        list_url = f"{url}?{urllib.parse.urlencode(params)}"
        print(f"[1/2] 访问列表页建立会话...")
        print(f"      URL: {list_url}")

        html = self.fetch_with_session(list_url)

        if html:
            print(f"      ✓ 列表页访问成功，获取了 {len(self.cookie_jar)} 个 cookies")

        return html

    def parse_list_page(self, html: str, batch: int) -> List[Dict]:
        """解析列表页，提取车辆信息和详情链接"""
        vehicles = []

        vehicle_pattern = r'<li[^>]*>.*?<span class="car_name"><a href="([^"]+)"[^>]*>([^<]+)</a></span>.*?</li>'
        vehicle_matches = re.findall(vehicle_pattern, html, re.DOTALL)

        print(f"      ✓ 找到 {len(vehicle_matches)} 条车辆信息")

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

    def get_detail_page(self, detail_url: str, list_url: str, vehicle_info: Dict) -> Optional[Dict]:
        """第二步：使用列表页的会话访问详情页"""
        print(f"[2/2] 访问详情页...")

        # 使用列表页作为 Referer
        html = self.fetch_with_session(detail_url, referer=list_url)

        if not html:
            return None

        # 检查是否被拦截
        if '非正常访问' in html or '爬取数据嫌疑' in html:
            print(f"      ✗ 详情页被拦截")
            return None

        print(f"      ✓ 详情页访问成功！")

        # 解析详情页
        detail = self.parse_detail_page(html)

        # 下载图片
        images = self.download_images(detail_url, vehicle_info)
        if images:
            detail['车辆图片'] = images

        # 合并数据
        detail['详情页URL'] = detail_url
        detail['爬取时间'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        full_data = {**vehicle_info, **detail}

        print(f"      ✓ 数据解析成功（{len(detail)}个字段，{len(images)}张图片）")

        return full_data

    def parse_detail_page(self, html: str) -> Dict:
        """解析详情页HTML"""
        detail = {}

        # 保存HTML用于分析
        with open('data/detail_page_sample.html', 'w', encoding='utf-8') as f:
            f.write(html)

        # 提取基本信息表格
        table_pattern = r'<tr[^>]*>.*?<td[^>]*width="20%"[^>]*>([^<]+?)</td>.*?<td[^>]*>([^<]+?)(?:<span|</td|</tr)'
        for match in re.finditer(table_pattern, html, re.DOTALL):
            key = match.group(1).strip().rstrip('：')
            value = match.group(2).strip()

            if value and value not in ['&nbsp;', '', '-']:
                detail[key] = value

        # 提取三电参数
        sections = ['电芯参数', '电池信息', '电机信息', '电控系统']

        for section in sections:
            # 查找该部分
            section_start = html.find(section)
            if section_start == -1:
                continue

            # 找到该部分的结束位置（下一个section或表格结束）
            section_end = len(html)
            for next_section in sections:
                if next_section != section:
                    pos = html.find(next_section, section_start + 1)
                    if pos != -1 and pos < section_end:
                        section_end = pos

            section_text = html[section_start:section_end]

            # 提取键值对
            kv_pattern = r'([^<>：\t\n]+?)[:：]\s*([^\t\n<]+?)(?=\n|<br|<|$)'
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

    def download_images(self, detail_url: str, vehicle_info: Dict) -> List[str]:
        """下载车辆图片"""
        images = []

        try:
            # 重新获取详情页来查找图片（使用已建立的会话）
            html = self.fetch_with_session(detail_url, referer=detail_url.replace('qcggdetail', 'qcggs'))

            if not html:
                return images

            # 查找所有图片URL
            img_pattern = r'<img[^>]+src="([^"]+)"'
            img_matches = re.findall(img_pattern, html)

            bh = vehicle_info.get('公告编号', 'unknown')
            vehicle_name = vehicle_info.get('车辆名称', 'unknown')
            vehicle_name = re.sub(r'[<>:"/\\|?*]', '_', vehicle_name)[:30]

            for idx, img_url in enumerate(img_matches, 1):
                # 过滤车辆相关图片
                if not any(x in img_url.lower() for x in ['ufileos', 'jdcsww']):
                    continue

                try:
                    # 下载图片
                    ext = os.path.splitext(img_url.split('?')[0])[1] or '.jpg'
                    filename = f"{bh}_{vehicle_name}_{idx}{ext}"
                    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
                    filepath = os.path.join(self.image_dir, filename)

                    img_data = self.fetch_with_session(img_url, referer=detail_url)

                    if img_data:
                        # 从HTML中提取实际图片URL（可能需要二次请求）
                        # 这里简化处理，直接保存
                        with open(filepath, 'wb') as f:
                            # 尝试下载图片
                            try:
                                req = urllib.request.Request(img_url, headers={
                                    'User-Agent': 'Mozilla/5.0',
                                    'Referer': detail_url
                                })
                                with urllib.request.urlopen(req, timeout=10) as response:
                                    f.write(response.read())
                                images.append(filepath)
                                print(f"      ✓ 图片 {idx}: {filename}")
                            except:
                                pass

                except Exception:
                    continue

        except Exception as e:
            print(f"      ✗ 图片下载出错: {e}")

        return images

    def save_json(self, data: List[Dict], filename: str):
        """保存JSON"""
        os.makedirs('data', exist_ok=True)
        filepath = os.path.join('data', filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"\n✓ 数据已保存到: {filepath}")
        return filepath

    def run(self, batch: int = 385, detail_limit: int = 2):
        """运行爬虫"""
        print("=" * 70)
        print("会话式爬虫 - 模拟真实用户访问流程")
        print("=" * 70)

        # 构造列表页URL
        list_url = f"{self.base_url}/qcggs?ggpc={batch}&clmc=1&rylx=C&viewtype=0"

        print(f"\n批次: {batch}")
        print(f"目标: 获取前 {detail_limit} 条详情数据\n")

        # 第一步：访问列表页
        list_html = self.get_list_page(batch)
        if not list_html:
            print("✗ 列表页访问失败")
            return

        # 解析列表
        vehicles = self.parse_list_page(list_html, batch)
        if not vehicles:
            print("✗ 未找到车辆信息")
            return

        # 第二步：访问详情页
        print(f"\n开始获取详情页...")
        full_data = []

        for idx, vehicle in enumerate(vehicles[:detail_limit], 1):
            print(f"\n{'='*60}")
            print(f"[{idx}/{detail_limit}] {vehicle['车辆名称']}")
            print(f"{'='*60}")
            print(f"公告编号: {vehicle.get('公告编号', 'N/A')}")

            if vehicle.get('详情链接'):
                detail_data = self.get_detail_page(
                    vehicle['详情链接'],
                    list_url,
                    vehicle
                )
                if detail_data:
                    full_data.append(detail_data)

                    # 显示部分数据
                    print(f"\n📊 详情数据:")
                    for key in list(detail_data.keys())[:8]:
                        if key not in ['序号', '批次', '车辆名称', '详情链接', '详情页URL', '爬取时间']:
                            print(f"  {key}: {detail_data[key]}")

            # 延迟
            if idx < detail_limit:
                print(f"\n⏱️  等待 3 秒...")
                time.sleep(3)

        # 保存数据
        if full_data:
            self.save_json(full_data, f'vehicle_details_batch{batch}.json')

            print("\n" + "=" * 70)
            print(f"✅ 爬取完成！")
            print(f"✓ 详情数据: {len(full_data)} 条")

            total_images = sum(len(v.get('车辆图片', [])) for v in full_data)
            print(f"✓ 车辆图片: {total_images} 张")
            print("=" * 70)

        return full_data


def main():
    """主函数"""
    crawler = SessionCrawler()

    # 先用385批次测试
    crawler.run(
        batch=385,
        detail_limit=2
    )


if __name__ == "__main__":
    main()
