#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
会话式爬虫 v2 - 优化版
使用更好的HTML解析
"""

import urllib.request
import urllib.parse
import json
import time
import re
import os
from datetime import datetime
from typing import List, Dict, Optional
from html.parser import HTMLParser
from http.cookiejar import CookieJar


class DetailPageParser(HTMLParser):
    """详情页解析器"""

    def __init__(self):
        super().__init__()
        self.data = {}
        self.current_section = None
        self.in_td = False
        self.current_key = None
        self.skip_scripts = True

    def handle_starttag(self, tag, attrs):
        # 跳过脚本和样式
        if tag in ['script', 'style']:
            self.skip_scripts = True
            return

        if self.skip_scripts:
            return

        # 检测表格单元格
        if tag == 'td':
            self.in_td = True

    def handle_endtag(self, tag):
        if tag in ['script', 'style']:
            self.skip_scripts = False
            return

        if tag == 'td':
            self.in_td = False

    def handle_data(self, data):
        if self.skip_scripts:
            return

        text = data.strip()

        # 检测section标题
        sections = ['电芯参数', '电池信息', '电机信息', '电控系统',
                   '生产企业信息', '免检说明', '公告状态', '主要技术参数']

        for section in sections:
            if section in text and len(text) < len(section) + 10:
                self.current_section = section
                return

        # 如果在表格中，提取键值对
        if self.in_td and text and len(text) < 200:
            # 过滤掉样式和脚本
            if any(x in text.lower() for x in ['style', 'script', 'function', 'var ', 'color:', 'position:', 'display:', 'margin:', 'padding:']):
                return

            # 保存数据
            if self.current_section and text not in ['&nbsp;', '-', '', '/']:
                if ':' in text or '：' in text:
                    parts = re.split(r'[:：]', text, 1)
                    if len(parts) == 2:
                        key = parts[0].strip()
                        value = parts[1].strip()
                        if key and value:
                            full_key = f"{self.current_section}_{key}"
                            self.data[full_key] = value


class SessionCrawlerV2:
    """会话式爬虫 v2"""

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
            return None

    def get_list_page(self, batch: int = 385) -> Optional[str]:
        """访问列表页"""
        url = f"{self.base_url}/qcggs"
        params = {
            'ggxh': '', 'ggpc': str(batch), 'zwpp': '', 'clmc': '1',
            'fdjxh': '', 'qymc': '', 'cph': '', 'rylx': 'C', 'viewtype': '0'
        }

        list_url = f"{url}?{urllib.parse.urlencode(params)}"
        print(f"[1/2] 访问列表页: {list_url}")

        return self.fetch_with_session(list_url)

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

        # 保存HTML
        with open('data/detail_page_sample.html', 'w', encoding='utf-8') as f:
            f.write(html)

        # 解析数据
        detail = self.parse_detail_page(html)
        detail['详情页URL'] = detail_url
        detail['爬取时间'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        full_data = {**vehicle_info, **detail}
        print(f"      ✓ 解析完成（{len(detail)}个字段）")

        return full_data

    def parse_detail_page(self, html: str) -> Dict:
        """解析详情页"""
        detail = {}

        # 方法1: 提取表格数据
        table_pattern = r'<td[^>]*width="20%"[^>]*>([^<]+)</td>\s*<td[^>]*>([^<]+)(?:<span|</td)'
        for match in re.finditer(table_pattern, html, re.IGNORECASE):
            key = match.group(1).strip().rstrip('：')
            value = match.group(2).strip()

            if value and value not in ['&nbsp;', '', '-']:
                detail[key] = value

        # 方法2: 提取三电参数（更精确）
        for section in ['电芯参数', '电池信息', '电机信息', '电控系统']:
            # 找到section开始位置
            section_pos = html.find(section)
            if section_pos == -1:
                continue

            # 提取该section的内容（到下一个section或表格结束）
            end_pos = len(html)
            for next_sec in ['电芯参数', '电池信息', '电机信息', '电控系统']:
                if next_sec != section:
                    pos = html.find(next_sec, section_pos + 1)
                    if pos != -1 and pos < end_pos:
                        end_pos = pos

            section_html = html[section_pos:end_pos]

            # 提取键值对
            # 匹配格式: "动力类型：纯电动" 或 "动力类型:纯电动"
            kv_pattern = r'([^\s<>:：]+?)[:：]\s*([^\s<>]+?)(?=[\n<>]|$)'

            for kv_match in re.finditer(kv_pattern, section_html):
                key = kv_match.group(1).strip()
                value = kv_match.group(2).strip()

                # 过滤
                if (len(key) < 30 and len(value) < 100 and
                    not any(x in key.lower() for x in ['style', 'class', 'id', 'function', 'var']) and
                    not any(x in value.lower() for x in ['style', 'function', 'var', 'color:', 'position:'])):

                    if key and value and value not in ['-', '', '/', '&nbsp;']:
                        full_key = f"{section}_{key}"
                        detail[full_key] = value

        # 清理数据
        detail = {k: v for k, v in detail.items()
                if not any(x in k.lower() for x in ['style', 'function', 'var', 'color'])}

        return detail

    def save_json(self, data: List[Dict], filename: str):
        """保存JSON"""
        os.makedirs('data', exist_ok=True)
        filepath = os.path.join('data', filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"\n✓ 数据已保存: {filepath}")

    def run(self, batch: int = 385, detail_limit: int = 2):
        """运行爬虫"""
        print("=" * 70)
        print("会话式爬虫 v2 - 详情数据获取")
        print("=" * 70)

        list_url = f"{self.base_url}/qcggs?ggpc={batch}&clmc=1&rylx=C&viewtype=0"

        # 访问列表页
        print(f"\n批次: {batch}")
        list_html = self.get_list_page(batch)
        if not list_html:
            print("✗ 列表页失败")
            return

        vehicles = self.parse_list_page(list_html, batch)
        print(f"      找到 {len(vehicles)} 条车辆")

        # 访问详情页
        print(f"\n获取详情页...")
        full_data = []

        for idx, vehicle in enumerate(vehicles[:detail_limit], 1):
            print(f"\n[{idx}/{detail_limit}] {vehicle['车辆名称']}")

            if vehicle.get('详情链接'):
                detail_data = self.get_detail_page(
                    vehicle['详情链接'],
                    list_url,
                    vehicle
                )
                if detail_data:
                    full_data.append(detail_data)

                    # 显示三电参数
                    print(f"\n  三电参数:")
                    for key in sorted(detail_data.keys()):
                        if any(x in key for x in ['电芯', '电池', '电机', '电控']) and ':' not in key:
                            print(f"    {key}: {detail_data[key]}")

            time.sleep(2)

        # 保存
        if full_data:
            self.save_json(full_data, f'vehicle_details_batch{batch}.json')

            print("\n" + "=" * 70)
            print(f"✅ 完成！获取 {len(full_data)} 条详情数据")
            print("=" * 70)

        return full_data


def main():
    crawler = SessionCrawlerV2()
    crawler.run(batch=385, detail_limit=2)


if __name__ == "__main__":
    main()
