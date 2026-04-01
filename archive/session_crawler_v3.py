#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
会话式爬虫 v3 - 完整版
正确解析三电参数
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


class SessionCrawlerV3:
    """会话式爬虫 v3 - 完整版"""

    def __init__(self):
        self.base_url = "https://www.jdcsww.com"
        self.cookie_jar = CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.cookie_jar)
        )
        self.image_dir = 'data/vehicle_images'
        os.makedirs(self.image_dir, exist_ok=True)

    def fetch_with_session(self, url: str, referer: str = None) -> Optional[str]:
        """使用会话获取页面"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Accept-Encoding': 'identity',
                'Connection': 'keep-alive',
            }

            if referer:
                headers['Referer'] = referer

            req = urllib.request.Request(url, headers=headers)

            with self.opener.open(req, timeout=30) as response:
                return response.read().decode('utf-8', errors='ignore')

        except Exception as e:
            print(f"    ✗ 获取失败: {e}")
            return None

    def get_list_page(self, batch: int = 385) -> Optional[str]:
        """访问列表页"""
        url = f"{self.base_url}/qcggs"
        params = {
            'ggxh': '', 'ggpc': str(batch), 'zwpp': '', 'clmc': '1',
            'fdjxh': '', 'qymc': '', 'cph': '', 'rylx': 'C', 'viewtype': '0'
        }

        list_url = f"{url}?{urllib.parse.urlencode(params)}"
        print(f"[1/2] 访问列表页建立会话...")
        print(f"      {list_url}")

        html = self.fetch_with_session(list_url)
        if html:
            print(f"      ✓ 列表页成功（{len(self.cookie_jar)} cookies）")

        return html

    def parse_list_page(self, html: str, batch: int) -> List[Dict]:
        """解析列表页"""
        vehicles = []
        pattern = r'<span class="car_name"><a href="([^"]+)"[^>]*>([^<]+)</a></span>'
        matches = re.findall(pattern, html)

        for idx, (link, name) in enumerate(matches, 1):
            vehicle = {
                '序号': idx,
                '批次': batch,
                '车辆名称': name.strip(),
                '详情链接': f"{self.base_url}{link}",
            }

            bh_match = re.search(r'bh=([^&"\']+)', link)
            if bh_match:
                vehicle['公告编号'] = bh_match.group(1)

            vehicles.append(vehicle)

        return vehicles

    def get_detail_page(self, detail_url: str, list_url: str, vehicle_info: Dict) -> Optional[Dict]:
        """访问详情页"""
        print(f"[2/2] 访问详情页...")

        html = self.fetch_with_session(detail_url, referer=list_url)

        if not html or '非正常访问' in html or '爬取数据嫌疑' in html:
            print(f"      ✗ 被拦截")
            return None

        print(f"      ✓ 访问成功！")

        # 解析详情页
        detail = self.parse_detail_page(html)

        # 下载图片
        images = self.download_images(html, detail_url, vehicle_info)
        if images:
            detail['车辆图片'] = images

        # 合并数据
        detail['详情页URL'] = detail_url
        detail['爬取时间'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        full_data = {**vehicle_info, **detail}
        print(f"      ✓ 解析完成（{len(detail)}个字段，{len(images)}张图片）")

        return full_data

    def parse_detail_page(self, html: str) -> Dict:
        """解析详情页 - 重点解析三电参数"""
        detail = {}

        # 保存HTML
        with open('data/detail_page_sample.html', 'w', encoding='utf-8') as f:
            f.write(html)

        # === 解析三电参数 ===
        sections = {
            '电芯参数': '电芯参数',
            '电池信息': '电池信息',
            '电机信息': '电机信息',
            '电控系统': '电控系统'
        }

        for section_name, section_key in sections.items():
            # 找到section开始
            section_start = html.find(section_name)
            if section_start == -1:
                continue

            # 找到section结束（下一个section或</table>）
            section_end = len(html)
            for next_section in sections.values():
                if next_section != section_name:
                    pos = html.find(next_section, section_start + 1)
                    if pos != -1 and pos < section_end:
                        section_end = pos

            table_end = html.find('</table>', section_start)
            if table_end != -1 and table_end < section_end:
                section_end = table_end

            section_html = html[section_start:section_end]

            # 解析该section的键值对
            # 格式: <th>键名：</th><td>值</td>
            tr_pattern = r'<tr[^>]*>.*?<th>([^<]+)</th>\s*<td[^>]*>([^<]+)</td>.*?</tr>'
            for tr_match in re.finditer(tr_pattern, section_html, re.DOTALL):
                key = tr_match.group(1).strip().rstrip('：')
                value = tr_match.group(2).strip()

                if key and value and value not in ['&nbsp;', '-', '', '/']:
                    full_key = f"{section_key}_{key}"
                    detail[full_key] = value

        # === 解析基本信息表格 ===
        # 格式: <td width="20%">键</td><td>值</td>
        basic_pattern = r'<td[^>]*width="20%"[^>]*>([^<]+)</td>\s*<td[^>]*>([^<]+?)(?:<span|</td)'
        for match in re.finditer(basic_pattern, html, re.IGNORECASE):
            key = match.group(1).strip().rstrip('：')
            value = match.group(2).strip()

            if value and value not in ['&nbsp;', '', '-']:
                detail[key] = value

        return detail

    def download_images(self, html: str, detail_url: str, vehicle_info: Dict) -> List[str]:
        """下载车辆图片"""
        images = []

        try:
            # 查找图片URL
            img_pattern = r'<img[^>]+src="([^"]+)"'
            img_matches = re.findall(img_pattern, html)

            bh = vehicle_info.get('公告编号', 'unknown')
            vehicle_name = vehicle_info.get('车辆名称', 'unknown')
            vehicle_name = re.sub(r'[<>:"/\\|?*]', '_', vehicle_name)[:30]

            for idx, img_url in enumerate(img_matches, 1):
                # 过滤：只下载车辆相关图片
                if not any(x in img_url.lower() for x in ['ufileos', 'vehicle', 'car']):
                    continue

                try:
                    # 构造完整URL
                    if img_url.startswith('//'):
                        img_url = 'https:' + img_url
                    elif img_url.startswith('/'):
                        img_url = self.base_url + img_url

                    # 下载
                    ext = os.path.splitext(img_url.split('?')[0])[1] or '.jpg'
                    filename = f"{bh}_{vehicle_name}_{idx}{ext}"
                    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
                    filepath = os.path.join(self.image_dir, filename)

                    req = urllib.request.Request(img_url, headers={
                        'User-Agent': 'Mozilla/5.0',
                        'Referer': detail_url
                    })

                    with urllib.request.urlopen(req, timeout=10) as response:
                        with open(filepath, 'wb') as f:
                            f.write(response.read())

                    images.append(filepath)
                    print(f"      ✓ 图片: {filename}")

                except Exception as e:
                    continue

        except Exception as e:
            pass

        return images

    def save_json(self, data: List[Dict], filename: str):
        """保存JSON"""
        os.makedirs('data', exist_ok=True)
        filepath = os.path.join('data', filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"\n✓ 数据已保存: {filepath}")

    def run(self, batch: int = 385, detail_limit: int = 3):
        """运行爬虫"""
        print("=" * 70)
        print("会话式爬虫 v3 - 完整三电参数获取")
        print("=" * 70)

        list_url = f"{self.base_url}/qcggs?ggpc={batch}&clmc=1&rylx=C&viewtype=0"

        print(f"\n批次: {batch}")
        print(f"目标: 获取前 {detail_limit} 条完整详情\n")

        # 访问列表页
        list_html = self.get_list_page(batch)
        if not list_html:
            print("✗ 列表页失败")
            return

        # 解析列表
        vehicles = self.parse_list_page(list_html, batch)
        print(f"      找到 {len(vehicles)} 条车辆\n")

        # 访问详情页
        print("开始获取详情页和图片...")
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

                    # 显示三电参数
                    print(f"\n  📊 三电参数:")
                    for key in sorted(detail_data.keys()):
                        if any(x in key for x in ['电芯参数', '电池信息', '电机信息', '电控系统']):
                            print(f"    {key}: {detail_data[key]}")

            # 延迟
            if idx < detail_limit:
                print(f"\n⏱️  等待 3 秒...")
                time.sleep(3)

        # 保存数据
        if full_data:
            self.save_json(full_data, f'vehicle_details_complete_batch{batch}.json')

            print("\n" + "=" * 70)
            print(f"✅ 爬取完成！")
            print(f"✓ 详情数据: {len(full_data)} 条")

            total_images = sum(len(v.get('车辆图片', [])) for v in full_data)
            print(f"✓ 车辆图片: {total_images} 张")
            print("=" * 70)

        return full_data


def main():
    crawler = SessionCrawlerV3()
    crawler.run(batch=385, detail_limit=3)


if __name__ == "__main__":
    main()
