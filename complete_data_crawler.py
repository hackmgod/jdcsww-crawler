#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整数据爬虫 - 包含基本信息、三电参数和图片
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


class CompleteDataCrawler:
    """完整数据爬虫"""

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
        print(f"[1/2] 访问列表页...")
        return self.fetch_with_session(list_url)

    def parse_list_page(self, html: str, batch: int) -> List[Dict]:
        """解析列表页"""
        vehicles = []

        # 提取车辆块
        vehicle_pattern = r'<li[^>]*>.*?<span class="car_name"><a href="([^"]+)"[^>]*>([^<]+)</a></span>.*?</li>'
        vehicle_matches = re.findall(vehicle_pattern, html, re.DOTALL)

        for idx, (detail_link, car_name) in enumerate(vehicle_matches, 1):
            vehicle = {
                '序号': idx,
                '批次': batch,
                '车辆名称': car_name.strip(),
                '详情链接': f"{self.base_url}{detail_link}",
            }

            # 提取公告编号
            bh_match = re.search(r'bh=([^&"\']+)', detail_link)
            if bh_match:
                vehicle['公告编号'] = bh_match.group(1)

            # 从列表页提取更多信息
            detail_link_escaped = re.escape(detail_link)
            vehicle_block_pattern = rf'<li[^>]*>.*?<a href="{detail_link_escaped}".*?</li>'
            vehicle_block_match = re.search(vehicle_block_pattern, html, re.DOTALL)

            if vehicle_block_match:
                block = vehicle_block_match.group(0)

                # 提取型号
                model_pattern = r'<span class="car_model">([^<]+?)</span>'
                model_match = re.search(model_pattern, block)
                if model_match:
                    vehicle['公告型号'] = model_match.group(1).strip()

                # 提取发布时间
                publish_pattern = r'<span class="car_publish">发布时间：(\d{4}-\d{2}-\d{2})</span>'
                publish_match = re.search(publish_pattern, block)
                if publish_match:
                    vehicle['发布时间'] = publish_match.group(1)

                # 提取label信息
                label_pattern = r'<label>([^<]+?)：([^<]+?)</label>'
                for label_match in re.finditer(label_pattern, block):
                    key = label_match.group(1).strip()
                    value = label_match.group(2).strip()
                    if value:
                        vehicle[key] = value

                # 提取生产企业
                company_pattern = r'车辆生产企业名称：([^<\n]+?)(?:<|$)'
                company_match = re.search(company_pattern, block)
                if company_match:
                    vehicle['生产企业'] = company_match.group(1).strip()

            vehicles.append(vehicle)

        return vehicles

    def get_detail_complete(self, detail_url: str, list_url: str, vehicle_info: Dict) -> Optional[Dict]:
        """获取完整详情数据"""
        print(f"[2/2] 访问详情页...")

        html = self.fetch_with_session(detail_url, referer=list_url)

        if not html or '非正常访问' in html or '爬取数据嫌疑' in html:
            print(f"      ✗ 被拦截")
            return None

        print(f"      ✓ 访问成功！")

        # 解析所有数据
        basic_info = self.parse_basic_info(html)
        three_electric = self.parse_three_electric(html)
        images = self.download_images(html, detail_url, vehicle_info)

        # 合并所有数据
        complete_data = {
            **vehicle_info,
            **basic_info,
            **three_electric,
        }

        if images:
            complete_data['车辆图片'] = images

        complete_data['详情页URL'] = detail_url
        complete_data['爬取时间'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        print(f"      ✓ 解析完成（基本信息: {len(basic_info)}, 三电参数: {len(three_electric)}, 图片: {len(images)}）")

        return complete_data

    def parse_basic_info(self, html: str) -> Dict:
        """解析基本信息"""
        info = {}

        # 基本信息 - 第一个表格
        # 格式: <td width="20%">键</td><td>值</td>
        basic_pattern = r'<td[^>]*width="20%"[^>]*>([^<]+)</td>\s*<td[^>]*>([^<]+?)(?:<span|</td|<br)'
        for match in re.finditer(basic_pattern, html, re.IGNORECASE):
            key = match.group(1).strip().rstrip('：')
            value = match.group(2).strip()

            # 清理
            value = re.sub(r'<[^>]+>', '', value)
            value = value.replace('&nbsp;', '').strip()

            if key and value and value not in ['-', '', '/']:
                info[key] = value

        # 提取更多信息（可能在不同位置）
        # 车辆型号
        model_pattern = r'<span[^>]*class="[^"]*clxh[^"]*"[^>]*>([^<]+)</span>'
        model_match = re.search(model_pattern, html)
        if model_match:
            info['车辆型号'] = model_match.group(1).strip()

        # 公告批次
        batch_pattern = r'公告批次[：:]\s*([0-9]+)'
        batch_match = re.search(batch_pattern, html)
        if batch_match:
            info['公告批次'] = batch_match.group(1)

        return info

    def parse_three_electric(self, html: str) -> Dict:
        """解析三电参数"""
        three_electric = {}

        sections = ['电芯参数', '电池信息', '电机信息', '电控系统']

        for section_name in sections:
            # 找到section开始
            section_start = html.find(section_name)
            if section_start == -1:
                continue

            # 找到section结束
            section_end = len(html)
            for next_section in sections:
                if next_section != section_name:
                    pos = html.find(next_section, section_start + 1)
                    if pos != -1 and pos < section_end:
                        section_end = pos

            # 或者到表格结束
            table_end = html.find('</table>', section_start)
            if table_end != -1 and table_end < section_end:
                section_end = table_end

            section_html = html[section_start:section_end]

            # 解析该section的表格行
            # 格式: <tr><th>键：</th><td>值</td>...</tr>
            tr_pattern = r'<tr[^>]*>\s*<th[^>]*>([^<]+)</th>\s*<td[^>]*>([^<]+)</td>'
            for tr_match in re.finditer(tr_pattern, section_html):
                key = tr_match.group(1).strip().rstrip('：')
                value = tr_match.group(2).strip()

                if key and value and value not in ['&nbsp;', '-', '', '/']:
                    full_key = f"{section_name}_{key}"
                    three_electric[full_key] = value

            # 也尝试匹配<td>格式
            td_pattern = r'<tr[^>]*>\s*<td[^>]*>([^<]+)</td>\s*<td[^>]*>([^<]+)</td>'
            for td_match in re.finditer(td_pattern, section_html):
                key = td_match.group(1).strip().rstrip('：')
                value = td_match.group(2).strip()

                if key and value and value not in ['&nbsp;', '-', '', '/']:
                    full_key = f"{section_name}_{key}"
                    three_electric[full_key] = value

        return three_electric

    def download_images(self, html: str, detail_url: str, vehicle_info: Dict) -> List[str]:
        """下载车辆图片"""
        images = []

        try:
            # 查找所有图片
            img_pattern = r'<img[^>]+src="([^"]+)"'
            img_matches = re.findall(img_pattern, html)

            bh = vehicle_info.get('公告编号', 'unknown')
            vehicle_name = vehicle_info.get('车辆名称', 'unknown')
            # 清理文件名
            vehicle_name = re.sub(r'[<>:"/\\|?*]', '_', vehicle_name)[:30]

            downloaded = set()  # 避免重复下载

            for idx, img_url in enumerate(img_matches, 1):
                # 过滤：只下载车辆图片
                if not any(x in img_url.lower() for x in ['ufileos', 'vehicle', 'car', 'photo']):
                    continue

                # 构造完整URL
                if img_url.startswith('//'):
                    img_url = 'https:' + img_url
                elif img_url.startswith('/'):
                    img_url = self.base_url + img_url

                # 去掉URL参数
                img_url_clean = img_url.split('?')[0]

                # 检查是否已下载
                if img_url_clean in downloaded:
                    continue
                downloaded.add(img_url_clean)

                try:
                    # 构造文件名
                    ext = os.path.splitext(img_url_clean)[1] or '.jpg'
                    filename = f"{bh}_{vehicle_name}_{idx}{ext}"
                    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
                    filepath = os.path.join(self.image_dir, filename)

                    # 下载图片
                    req = urllib.request.Request(img_url, headers={
                        'User-Agent': 'Mozilla/5.0',
                        'Referer': detail_url
                    })

                    with urllib.request.urlopen(req, timeout=15) as response:
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

        # 也保存一份带时间戳的
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filepath_backup = os.path.join('data', f'complete_data_{timestamp}.json')
        with open(filepath_backup, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✓ 备份已保存: {filepath_backup}")

    def run(self, batch: int = 385, detail_limit: int = 3):
        """运行爬虫"""
        print("=" * 70)
        print("完整数据爬虫 - 基本信息 + 三电参数 + 图片")
        print("=" * 70)

        list_url = f"{self.base_url}/qcggs?ggpc={batch}&clmc=1&rylx=C&viewtype=0"

        print(f"\n📋 批次: {batch}")
        print(f"🎯 目标: 获取前 {detail_limit} 条完整数据\n")

        # 访问列表页
        list_html = self.get_list_page(batch)
        if not list_html:
            print("✗ 列表页失败")
            return

        # 解析列表
        vehicles = self.parse_list_page(list_html, batch)
        print(f"      ✓ 找到 {len(vehicles)} 条车辆\n")

        # 获取详情
        print("开始获取完整详情...")
        complete_data = []

        for idx, vehicle in enumerate(vehicles[:detail_limit], 1):
            print(f"\n{'='*70}")
            print(f"[{idx}/{detail_limit}] {vehicle['车辆名称']}")
            print(f"{'='*70}")
            print(f"📌 公告编号: {vehicle.get('公告编号', 'N/A')}")
            print(f"🏭 生产企业: {vehicle.get('生产企业', 'N/A')}")

            if vehicle.get('详情链接'):
                detail_data = self.get_detail_complete(
                    vehicle['详情链接'],
                    list_url,
                    vehicle
                )
                if detail_data:
                    complete_data.append(detail_data)

                    # 显示数据摘要
                    print(f"\n📊 数据摘要:")
                    print(f"   基本信息: {len([k for k in detail_data.keys() if not any(x in k for x in ['电芯', '电池', '电机', '电控', '图片', 'URL', '时间'])])} 项")
                    print(f"   三电参数: {len([k for k in detail_data.keys() if any(x in k for x in ['电芯', '电池', '电机', '电控'])])} 项")
                    print(f"   车辆图片: {len(detail_data.get('车辆图片', []))} 张")

            # 延迟
            if idx < detail_limit:
                print(f"\n⏱️  等待 4 秒...")
                time.sleep(4)

        # 保存数据
        if complete_data:
            self.save_json(complete_data, f'vehicle_complete_data_batch{batch}.json')

            print("\n" + "=" * 70)
            print(f"✅ 爬取完成！")
            print(f"✓ 完整数据: {len(complete_data)} 条")

            total_images = sum(len(v.get('车辆图片', [])) for v in complete_data)
            print(f"✓ 车辆图片: {total_images} 张")
            print(f"✓ 图片目录: {self.image_dir}/")
            print("=" * 70)

            # 显示第一辆车的完整数据结构
            if complete_data:
                print(f"\n📋 数据示例（第1辆车）:")
                first_vehicle = complete_data[0]
                for key in sorted(first_vehicle.keys()):
                    if key not in ['详情页URL', '爬取时间']:
                        value = first_vehicle[key]
                        if isinstance(value, list) and value:
                            print(f"   {key}: [{len(value)} 项]")
                        elif isinstance(value, str) and len(value) > 50:
                            print(f"   {key}: {value[:50]}...")
                        else:
                            print(f"   {key}: {value}")

        return complete_data


def main():
    crawler = CompleteDataCrawler()
    crawler.run(batch=385, detail_limit=10)  # 改为10辆


if __name__ == "__main__":
    main()
