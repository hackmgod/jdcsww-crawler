#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生产环境增强爬虫 - 完整版
功能:
1. 爬取所有批次(1-403)的新能源车辆完整数据
2. 包含83个完整字段（基本信息+三电参数+图片）
3. 支持增量保存和断点续传
4. 导出为Excel格式
5. 下载车辆图片
"""

import urllib.request
import urllib.parse
import json
import time
import re
import os
import logging
import random
from datetime import datetime
from typing import List, Dict, Optional, Set
from http.cookiejar import CookieJar


class EnhancedProductionCrawler:
    """生产环境增强爬虫 - 安全版"""

    def __init__(self):
        self.base_url = "https://www.jdcsww.com"
        self.cookie_jar = CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.cookie_jar)
        )
        self.output_dir = 'data/production_enhanced'
        self.image_dir = os.path.join(self.output_dir, 'images')
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.image_dir, exist_ok=True)

        # 状态跟踪
        self.state_file = os.path.join(self.output_dir, 'crawler_state.json')
        self.data_file = os.path.join(self.output_dir, 'all_vehicles_complete.json')
        self.excel_file = os.path.join(self.output_dir, 'vehicles_complete_all.xlsx')

        # ⚡ 反爬虫延迟配置（安全版）
        self.detail_delay_min = 10.0      # 详情页之间最小延迟（秒）
        self.detail_delay_max = 20.0      # 详情页之间最大延迟（秒）
        self.batch_delay_min = 15.0       # 批次间最小延迟（秒）
        self.batch_delay_max = 30.0       # 批次间最大延迟（秒）
        self.rest_interval = 20           # 每N个批次休息
        self.rest_duration = 60           # 休息时长（秒）

        # 统计信息
        self.request_count = 0
        self.blocked_count = 0

        # 配置日志
        self._setup_logger()

    def _setup_logger(self):
        """配置日志系统"""
        self.logger = logging.getLogger('EnhancedCrawler')
        self.logger.setLevel(logging.INFO)

        if self.logger.handlers:
            self.logger.handlers.clear()

        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        log_file = os.path.join(self.output_dir, f'crawler_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        self.log_file = log_file

        self.logger.info("=" * 70)
        self.logger.info("增强版爬虫启动")
        self.logger.info(f"日志文件: {log_file}")
        self.logger.info("=" * 70)

    def _get_chrome_headers(self) -> Dict[str, str]:
        """生成真实Chrome浏览器的完整请求头"""
        return {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'identity',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Sec-Ch-Ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"macOS"',
            'Cache-Control': 'max-age=0',
        }

    def warm_up(self):
        """预热机制 - 仅访问首页，避免触发反爬"""
        self.logger.info("=" * 70)
        self.logger.info("🔥 预热中 - 模拟真实用户访问模式")
        self.logger.info("=" * 70)

        try:
            # 1. 访问首页获取初始Cookie
            self.logger.info("📍 [1/2] 访问首页获取Cookie...")
            homepage = self.fetch_with_session(self.base_url, referer=None, max_retries=2)
            if homepage:
                warm_delay = random.uniform(3, 6)
                self.logger.info(f"✓ 首页访问成功，等待 {warm_delay:.1f} 秒...")
                time.sleep(warm_delay)
            else:
                self.logger.warning("✗ 首页访问失败，继续尝试")

            # 2. 最终停留（不访问空白查询页，避免触发封禁）
            final_delay = random.uniform(2, 5)
            self.logger.info(f"📍 [2/2] 预热完成，最终等待 {final_delay:.1f} 秒...")
            time.sleep(final_delay)

            self.logger.info("✅ 预热完成！开始爬取...")
            self.logger.info("💡 跳过空白查询页，直接访问带参数的URL")
            self.logger.info("=" * 70)
            print()

        except Exception as e:
            self.logger.warning(f"⚠️ 预热过程出现异常: {e}")
            self.logger.info("继续尝试爬取...")

    def is_blocked(self, html: str) -> bool:
        """检测是否被封禁/拦截"""
        if not html:
            return True

        block_indicators = [
            '非正常访问',
            '爬取数据嫌疑',
            '访问过于频繁',
            '您的访问已被限制',
            '请稍后再试',
            '系统检测到异常',
            'Anti-Spam',
            '验证码',
            'captcha',
        ]

        for indicator in block_indicators:
            if indicator in html:
                self.logger.warning(f"🚫 检测到封禁指示: '{indicator}'")
                return True

        return False

    def load_state(self) -> Dict:
        """加载爬虫状态"""
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            'completed_batches': [],
            'failed_batches': [],
            'last_update': None,
            'total_vehicles': 0
        }

    def save_state(self, state: Dict):
        """保存爬虫状态"""
        state['last_update'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

    def load_data(self) -> List[Dict]:
        """加载已有数据"""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def save_data(self, vehicles: List[Dict]):
        """保存所有数据"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(vehicles, f, ensure_ascii=False, indent=2)

    def fetch_with_session(self, url: str, referer: str = None, max_retries: int = 3) -> Optional[str]:
        """使用会话获取页面 - 增强版（完整请求头+封禁检测）"""
        for attempt in range(max_retries):
            try:
                # 使用完整的Chrome请求头
                headers = self._get_chrome_headers()

                if referer:
                    headers['Referer'] = referer

                req = urllib.request.Request(url, headers=headers)
                with self.opener.open(req, timeout=30) as response:
                    html = response.read().decode('utf-8', errors='ignore')

                    # 检测是否被封禁
                    if self.is_blocked(html):
                        self.blocked_count += 1
                        if attempt < max_retries - 1:
                            retry_delay = 20 + (attempt * 10)
                            self.logger.warning(f"🚫 被拦截，{retry_delay}秒后重试 ({attempt + 1}/{max_retries})")
                            time.sleep(retry_delay)
                            continue
                        else:
                            self.logger.error("❌ 多次重试失败，IP可能已被封禁")
                            self.logger.error("💡 建议：等待15-30分钟后重试，或更换网络")
                            return None

                    self.request_count += 1
                    return html

            except Exception as e:
                if attempt < max_retries - 1:
                    retry_delay = 10 + (attempt * 10)
                    self.logger.warning(f"⚠️ 网络错误，{retry_delay}秒后重试: {e}")
                    time.sleep(retry_delay)
                else:
                    self.logger.error(f"❌ 获取失败: {e}")
                    return None

        return None

    def parse_list_page(self, html: str, batch: int, fuel_type_name: str) -> List[Dict]:
        """解析列表页 - 提取基本信息"""
        vehicles = []

        # 提取车辆块
        vehicle_pattern = r'<li[^>]*>.*?<span class="car_name"><a href="([^"]+)"[^>]*>([^<]+)</a></span>.*?</li>'
        vehicle_matches = re.findall(vehicle_pattern, html, re.DOTALL)

        for idx, (detail_link, car_name) in enumerate(vehicle_matches, 1):
            vehicle = {
                '批次': batch,
                '燃料类型': fuel_type_name,
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

                # 提取公告型号
                model_pattern = r'<span class="car_model">([^<]+?)</span>'
                model_match = re.search(model_pattern, block)
                if model_match:
                    vehicle['公告型号'] = model_match.group(1).strip()

                # 提取生产企业
                company_patterns = [
                    r'车辆生产企业名称[：:]([^<\n]+?)(?:<|$)',
                    r'<label>生产企业[：:]([^<]+?)</label>',
                    r'<label>qymc[：:]([^<]+?)</label>',
                ]

                for pattern in company_patterns:
                    company_match = re.search(pattern, block)
                    if company_match:
                        vehicle['生产企业'] = company_match.group(1).strip()
                        break

            vehicles.append(vehicle)

        return vehicles

    def parse_detail_page_complete(self, html: str) -> Dict:
        """解析详情页 - 完整的83个字段"""
        detail_data = {}

        # 1. 解析生产企业信息表格（第一个表格）
        detail_data.update(self._parse_company_info(html))

        # 2. 解析车辆燃料参数
        detail_data.update(self._parse_fuel_params(html))

        # 3. 解析车辆参数（左右两列表格）
        detail_data.update(self._parse_vehicle_params(html))

        # 4. 解析三电参数
        detail_data.update(self._parse_three_electric_params(html))

        return detail_data

    def _parse_company_info(self, html: str) -> Dict:
        """解析生产企业信息"""
        info = {}
        prefix = "生产企业信息_"

        # 找到生产企业信息的开始和结束位置
        section_start = html.find('生产企业信息')

        if section_start == -1:
            return info

        # 找到section结束（下一个section开始）
        next_sections = ['车辆燃料参数', '车辆参数', '电芯信息', '电池信息', '电机信息', '电控系统']
        section_end = len(html)
        for next_section in next_sections:
            pos = html.find(next_section, section_start + 1)
            if pos != -1 and pos < section_end:
                section_end = pos

        # 或者到表格结束
        table_end = html.find('</table>', section_start)
        if table_end != -1 and table_end < section_end:
            section_end = table_end

        section_html = html[section_start:section_end]

        # 在该section内匹配字段
        # 匹配 <th>字段名</th><td>值</td> 格式
        th_td_pattern = r'<th[^>]*>([^<]+?)</th>\s*<td[^>]*>([^<]+?)(?:<span|</td>|<br)'

        for match in re.finditer(th_td_pattern, section_html, re.IGNORECASE):
            key = match.group(1).strip().rstrip('：:')
            value = match.group(2).strip()

            # 清理HTML标签和空格
            value = re.sub(r'<[^>]+>', '', value)
            value = value.replace('&nbsp;', '').strip()

            # 跳过section标题本身
            if key in ['生产企业信息', '企业信息']:
                continue

            if key and value:
                info[prefix + key] = value

        return info

    def _parse_fuel_params(self, html: str) -> Dict:
        """解析车辆燃料参数"""
        info = {}
        prefix = "车辆燃料参数_"
        section_start = html.find('车辆燃料参数')

        if section_start == -1:
            return info

        # 找到该section的结束位置（下一个表格或section开始）
        section_end = html.find('车辆参数', section_start)
        if section_end == -1:
            section_end = len(html)

        section_html = html[section_start:section_end]

        # 匹配键值对
        patterns = [
            r'<th[^>]*>([^<]+?)</th>\s*<td[^>]*>([^<]+?)(?:<|</td>)',
            r'<td[^>]*width="30%"[^>]*>([^<]+?)</td>\s*<td[^>]*>([^<]+?)(?:<|</td>)',
        ]

        for pattern in patterns:
            for match in re.finditer(pattern, section_html, re.IGNORECASE):
                key = match.group(1).strip().rstrip('：:')
                value = match.group(2).strip()
                value = re.sub(r'<[^>]+>', '', value).replace('&nbsp;', '').strip()

                # 跳过section标题本身
                if key in ['车辆燃料参数', '燃料参数']:
                    continue

                if key and value:
                    info[prefix + key] = value

        return info

    def _parse_vehicle_params(self, html: str) -> Dict:
        """解析车辆参数（左右两列的表格）"""
        info = {}
        prefix = "车辆参数_"
        section_start = html.find('车辆参数')

        if section_start == -1:
            return info

        # 找到表格结束
        table_end = html.find('</table>', section_start)
        if table_end == -1:
            table_end = len(html)

        section_html = html[section_start:table_end]

        # 匹配左右两列的参数
        # 格式: <tr><td>参数名</td><td>值</td><td>参数名2</td><td>值2</td></tr>
        tr_pattern = r'<tr[^>]*>.*?</tr>'
        for tr_match in re.finditer(tr_pattern, section_html, re.DOTALL):
            row_html = tr_match.group(0)

            # 提取所有td中的内容
            td_pattern = r'<td[^>]*>([^<]+)</td>'
            tds = re.findall(td_pattern, row_html)

            # 每两个td为一组键值对
            for i in range(0, len(tds) - 1, 2):
                key = tds[i].strip().rstrip('：:')
                value = tds[i + 1].strip()

                # 清理
                value = value.replace('&nbsp;', '').strip()

                # 跳过section标题本身和非参数字段
                if key in ['车辆参数', '法律法规'] or not key or key == '法律法规':
                    continue

                if key and value and value not in ['-', '', '/']:
                    info[prefix + key] = value

        return info

    def _parse_three_electric_params(self, html: str) -> Dict:
        """解析三电参数（电芯、电池、电机、电控）"""
        three_electric = {}

        # 定义section及其可能的关键词
        sections = [
            ('电芯参数', '电芯信息_'),  # 网页中是"电芯参数"，输出为"电芯信息_"
            ('电池信息', '电池信息_'),
            ('电机信息', '电机信息_'),
            ('电控系统', '电控系统_')
        ]

        for section_name_cn, prefix in sections:
            # 尝试找到section标题（可能在<th>或普通文本中）
            section_patterns = [
                f'<th[^>]*>{section_name_cn}</th>',
                f'<th[^>]*>{section_name_cn}（',
                f'<td[^>]*>{section_name_cn}</td>',
                f'<td[^>]*>{section_name_cn}（',
                f'<b[^>]*>{section_name_cn}</b>',
                f'<strong[^>]*>{section_name_cn}</strong>',
                section_name_cn  # 纯文本匹配
            ]

            section_start = -1
            for pattern in section_patterns:
                pos = html.find(pattern.replace('<th[^>*</th>]', '<th>'))
                if pos != -1:
                    section_start = pos
                    break

            if section_start == -1:
                continue

            # 找到section结束（下一个section开始或表格结束）
            section_end = len(html)

            # 查找下一个section
            for next_section, _ in sections:
                if next_section != section_name_cn:
                    # 尝试多种模式
                    for pattern in [
                        f'<th[^>]*>{next_section}</th>',
                        f'<th[^>]*>{next_section}（',
                        f'<td[^>]*>{next_section}</td>',
                        f'<td[^>]*>{next_section}（',
                        next_section
                    ]:
                        pos = html.find(pattern.replace('<th[^>*</th>]', '<th>'), section_start + 1)
                        if pos != -1 and pos < section_end:
                            section_end = pos
                            break

            # 或者到表格结束
            table_end = html.find('</table>', section_start)
            if table_end != -1 and table_end < section_end:
                section_end = table_end

            section_html = html[section_start:section_end]

            # 解析该section的键值对
            # 格式: <tr><th>键：</th><td>值</td></tr> 或 <tr><td>键：</td><td>值</td></tr>
            tr_pattern = r'<tr[^>]*>.*?</tr>'
            for tr_match in re.finditer(tr_pattern, section_html, re.DOTALL):
                row_html = tr_match.group(0)

                # 提取th和td（优先使用th）
                th_match = re.search(r'<th[^>]*>([^<]+?)</th>', row_html)
                td_pattern = r'<td[^>]*>([^<]+?)(?:<span|</td>|<br)'
                td_matches = re.findall(td_pattern, row_html)

                if th_match and len(td_matches) >= 1:
                    key = th_match.group(1).strip().rstrip('：:')
                    value = td_matches[0].strip()

                    # 清理
                    value = re.sub(r'<[^>]+>', '', value)
                    value = value.replace('&nbsp;', '').strip()

                    # 跳过section标题本身和无关字段
                    skip_keywords = ['电芯信息', '电池信息', '电机信息', '电控系统',
                                   '非公告数据', '仅供参考', '下面的三电参']
                    if any(keyword in key for keyword in skip_keywords):
                        continue

                    if key and value and value not in ['&nbsp;', '-', '', '/']:
                        # 使用完整前缀区分不同section
                        full_key = f"{prefix}{key}"
                        three_electric[full_key] = value

        return three_electric

    def download_vehicle_images(self, html: str, detail_url: str, vehicle_info: Dict) -> List[str]:
        """下载车辆图片"""
        images = []

        try:
            img_pattern = r'<img[^>]+src="([^"]+)"'
            img_matches = re.findall(img_pattern, html)

            bh = vehicle_info.get('公告编号', 'unknown')
            vehicle_name = vehicle_info.get('车辆名称', 'unknown')
            vehicle_name = re.sub(r'[<>:"/\\|?*]', '_', vehicle_name)[:30]

            downloaded = set()

            for idx, img_url in enumerate(img_matches, 1):
                # 过滤车辆图片
                if not any(x in img_url.lower() for x in ['ufileos', 'vehicle', 'car', 'photo']):
                    continue

                # 构造完整URL
                if img_url.startswith('//'):
                    img_url = 'https:' + img_url
                elif img_url.startswith('/'):
                    img_url = self.base_url + img_url

                img_url_clean = img_url.split('?')[0]

                if img_url_clean in downloaded:
                    continue
                downloaded.add(img_url_clean)

                try:
                    ext = os.path.splitext(img_url_clean)[1] or '.jpg'
                    filename = f"{bh}_{vehicle_name}_{idx}{ext}"
                    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
                    filepath = os.path.join(self.image_dir, filename)

                    req = urllib.request.Request(img_url, headers={
                        'User-Agent': 'Mozilla/5.0',
                        'Referer': detail_url
                    })

                    with urllib.request.urlopen(req, timeout=15) as response:
                        with open(filepath, 'wb') as f:
                            f.write(response.read())

                    images.append(filepath)
                    self.logger.debug(f"下载图片: {filename}")

                except Exception as e:
                    self.logger.warning(f"图片下载失败 {img_url}: {e}")
                    continue

        except Exception as e:
            self.logger.warning(f"图片处理失败: {e}")

        return images

    def crawl_single_batch_list(self, batch: int, fuel_type_code: str, fuel_type_name: str) -> List[Dict]:
        """爬取单个批次的列表页"""
        url = f"{self.base_url}/qcggs"
        params = {
            'ggxh': '',
            'ggpc': str(batch),
            'zwpp': '',
            'clmc': '1',  # 车辆类型分类码（一个l）
            'fdjxh': '',
            'qymc': '',
            'cph': '',
            'rylx': fuel_type_code,
            'viewtype': '0'
        }
        list_url = f"{url}?{urllib.parse.urlencode(params)}"

        self.logger.info(f"爬取列表页: 批次{batch} [{fuel_type_name}]")

        html = self.fetch_with_session(list_url)

        if not html:
            self.logger.warning(f"批次{batch} [{fuel_type_name}] - 获取列表页失败")
            return []

        vehicles = self.parse_list_page(html, batch, fuel_type_name)
        self.logger.info(f"批次{batch} [{fuel_type_name}] - 找到 {len(vehicles)} 辆")

        return vehicles

    def crawl_vehicle_detail(self, vehicle: Dict) -> Optional[Dict]:
        """爬取单个车辆的详情页"""
        detail_url = vehicle.get('详情链接')

        if not detail_url:
            return None

        try:
            # 使用列表页URL作为referer
            list_url = f"{self.base_url}/qcggs"
            html = self.fetch_with_session(detail_url, referer=list_url)

            if not html:
                self.logger.warning(f"详情页获取失败: {vehicle.get('公告编号', 'unknown')}")
                return None

            # 解析详情页
            detail_data = self.parse_detail_page_complete(html)

            # 下载图片
            images = self.download_vehicle_images(html, detail_url, vehicle)
            if images:
                detail_data['车辆图片'] = images

            # 合并列表页数据和详情页数据
            complete_data = {**vehicle, **detail_data}
            complete_data['详情页URL'] = detail_url
            complete_data['爬取时间'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            self.logger.debug(f"详情页解析完成: {vehicle.get('公告编号', 'unknown')}, 字段数: {len(detail_data)}")

            return complete_data

        except Exception as e:
            self.logger.error(f"详情页爬取失败 {vehicle.get('公告编号', 'unknown')}: {e}")
            return None

    def run_full_crawl(self, start_batch: int = 1, end_batch: int = 403, crawl_detail: bool = True):
        """执行全量爬取"""
        self.logger.info("=" * 70)
        self.logger.info(f"开始全量爬取: 批次 {start_batch}-{end_batch}")
        self.logger.info(f"详情页爬取: {'启用' if crawl_detail else '禁用'}")
        self.logger.info("=" * 70)

        print("=" * 70)
        print("🛡️ 增强版生产环境爬虫 - 安全模式")
        print("=" * 70)
        print(f"批次范围: {start_batch} - {end_batch}")
        print(f"爬取详情: {'是 (完整83字段)' if crawl_detail else '否 (仅列表页6字段)'}")
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"日志文件: {self.log_file}")
        print()
        print("⚙️ 安全配置:")
        print(f"  - 详情页延迟: {self.detail_delay_min}-{self.detail_delay_max} 秒")
        print(f"  - 批次间延迟: {self.batch_delay_min}-{self.batch_delay_max} 秒")
        print(f"  - 休息策略: 每 {self.rest_interval} 批次休息 {self.rest_duration} 秒")
        print("=" * 70)
        print()

        # 🔥 预热：先访问首页建立会话
        self.warm_up()

        # 加载状态
        state = self.load_state()
        all_vehicles = self.load_data()

        self.logger.info(f"已有数据: {len(all_vehicles)} 辆")
        self.logger.info(f"已完成批次: {len(state['completed_batches'])}")

        print(f"📊 已有数据: {len(all_vehicles)} 辆")
        print(f"✓ 已完成批次: {len(state['completed_batches'])}")

        # 燃料类型
        fuel_types = [
            {'code': 'C', 'name': '纯电动'},
            {'code': 'O', 'name': '混合动力'},
        ]

        total_tasks = (end_batch - start_batch + 1) * len(fuel_types)
        completed_tasks = len(state['completed_batches'])

        # 开始爬取
        for batch in range(start_batch, end_batch + 1):
            for fuel_type in fuel_types:
                task_key = f"{batch}-{fuel_type['code']}"

                # 跳过已完成
                if task_key in state['completed_batches']:
                    continue

                try:
                    # 1. 爬取列表页
                    vehicles = self.crawl_single_batch_list(batch, fuel_type['code'], fuel_type['name'])

                    if not vehicles:
                        state['failed_batches'].append(task_key)
                        continue

                    # 2. 爬取详情页（可选）
                    if crawl_detail:
                        batch_vehicles_complete = []
                        for idx, vehicle in enumerate(vehicles, 1):
                            print(f"    [{idx}/{len(vehicles)}] {vehicle.get('车辆名称', 'unknown')} - {vehicle.get('公告编号', 'unknown')}")

                            detail_data = self.crawl_vehicle_detail(vehicle)
                            if detail_data:
                                batch_vehicles_complete.append(detail_data)

                            # 详情页之间延迟（更长，避免被封）
                            if idx < len(vehicles):
                                delay = random.uniform(self.detail_delay_min, self.detail_delay_max)
                                print(f"    ⏱️ 等待 {delay:.1f} 秒...")
                                time.sleep(delay)

                        if batch_vehicles_complete:
                            all_vehicles.extend(batch_vehicles_complete)

                            # 更新状态
                            state['completed_batches'].append(task_key)
                            completed_tasks += 1

                            # 保存
                            self.save_data(all_vehicles)
                            state['total_vehicles'] = len(all_vehicles)
                            self.save_state(state)

                            progress = (completed_tasks / total_tasks) * 100
                            print(f"    进度: {completed_tasks}/{total_tasks} ({progress:.1f}%) | 累计: {len(all_vehicles)} 辆")
                        else:
                            state['failed_batches'].append(task_key)
                    else:
                        # 不爬详情页，直接保存列表页数据
                        all_vehicles.extend(vehicles)
                        state['completed_batches'].append(task_key)
                        completed_tasks += 1

                        self.save_data(all_vehicles)
                        state['total_vehicles'] = len(all_vehicles)
                        self.save_state(state)

                        progress = (completed_tasks / total_tasks) * 100
                        print(f"    进度: {completed_tasks}/{total_tasks} ({progress:.1f}%) | 累计: {len(all_vehicles)} 辆")

                    # 批次间延迟（更长，更随机）
                    base_delay = random.uniform(self.batch_delay_min, self.batch_delay_max)
                    print(f"  ⏱️ 批次间延迟 {base_delay:.1f} 秒...")
                    time.sleep(base_delay)

                    # 定期休息（更频繁，更长时间）
                    if completed_tasks > 0 and completed_tasks % self.rest_interval == 0:
                        self.logger.info(f"已爬取{completed_tasks}个任务，休息{self.rest_duration}秒...")
                        print(f"\n{'='*70}")
                        print(f"💦 已爬取 {completed_tasks} 个任务")
                        print(f"⏸️  休息 {self.rest_duration} 秒（避免触发反爬）")
                        print(f"{'='*70}\n")
                        time.sleep(self.rest_duration)
                        print(f"✓ 休息完成，继续爬取\n")

                except KeyboardInterrupt:
                    print("\n\n⚠️  用户中断！保存当前进度...")
                    self.save_data(all_vehicles)
                    state['total_vehicles'] = len(all_vehicles)
                    self.save_state(state)
                    print("✓ 进度已保存")
                    return

                except Exception as e:
                    print(f"    ✗ 错误: {e}")
                    self.logger.error(f"批次{batch}错误: {e}")
                    state['failed_batches'].append(task_key)

        # 完成
        self.logger.info("=" * 70)
        self.logger.info("爬取完成")
        self.logger.info(f"总计: {len(all_vehicles)} 辆车")
        self.logger.info(f"成功: {len(state['completed_batches'])} 个任务")
        self.logger.info(f"失败: {len(state['failed_batches'])} 个任务")
        self.logger.info("=" * 70)

        print("=" * 70)
        print("✅ 爬取完成！")
        print(f"✓ 总计: {len(all_vehicles)} 辆车")
        print(f"✓ 成功: {len(state['completed_batches'])} 个任务")
        print(f"✗ 失败: {len(state['failed_batches'])} 个任务")
        print(f"完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        print()

        # 导出Excel
        if all_vehicles:
            self.export_to_excel(all_vehicles)

        return all_vehicles

    def export_to_excel(self, vehicles: List[Dict]):
        """导出到Excel"""
        try:
            import openpyxl
            from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
        except ImportError:
            print("⚠️  需要安装 openpyxl: pip3 install openpyxl --break-system-packages")
            return

        filename = os.path.basename(self.excel_file)
        print(f"📊 正在导出Excel: {filename}")

        # 收集所有可能的字段
        all_fields = set()
        for vehicle in vehicles:
            all_fields.update(vehicle.keys())

        # 排序字段（重要字段在前）
        field_priority = [
            '批次', '燃料类型', '公告编号', '公告型号', '车辆名称', '生产企业',
            '产品号', '中文品牌', '企业名称', '发布日期', '车型',
            '车辆燃料种类', '是否新能源汽车',
            '车辆总质量', '车辆整备质量', '额定载客', '最高车速',
            '外形尺寸', '车辆识别代码'
        ]

        sorted_fields = []
        for field in field_priority:
            if field in all_fields:
                sorted_fields.append(field)
                all_fields.remove(field)

        # 添加剩余字段
        sorted_fields.extend(sorted(all_fields))

        # 创建工作簿
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "车辆完整数据"

        # 写入表头
        for col_idx, field_name in enumerate(sorted_fields, 1):
            cell = ws.cell(row=1, column=col_idx, value=field_name)
            cell.font = Font(bold=True, color='FFFFFF', size=11)
            cell.fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
            cell.alignment = Alignment(horizontal='center', vertical='center')

        # 写入数据
        for row_idx, vehicle in enumerate(vehicles, 2):
            for col_idx, field_name in enumerate(sorted_fields, 1):
                value = vehicle.get(field_name, '')

                # 处理列表类型（如图片路径）
                if isinstance(value, list):
                    value = ', '.join(str(v) for v in value)
                elif value is None:
                    value = ''

                cell = ws.cell(row=row_idx, column=col_idx, value=value)
                cell.alignment = Alignment(horizontal='left', vertical='center')

        # 冻结首行
        ws.freeze_panes = 'A2'

        # 保存
        wb.save(self.excel_file)
        file_size = os.path.getsize(self.excel_file) / 1024 / 1024
        print(f"✓ Excel已保存: {self.excel_file}")
        print(f"  文件大小: {file_size:.2f} MB")
        print(f"  记录数: {len(vehicles)}")
        print(f"  字段数: {len(sorted_fields)}")


def main():
    """主函数"""
    crawler = EnhancedProductionCrawler()

    print("\n" + "=" * 70)
    print("增强版全量数据爬取")
    print("=" * 70)
    print("\n选项:")
    print("1. 完整模式 - 爬取所有批次+详情页 (83个字段，非常慢)")
    print("2. 快速模式 - 仅爬取列表页 (6个字段，快速)")
    print("3. 测试模式 - 爬取单个批次测试 (385批次)")
    print("4. 继续上次中断的任务")
    print("5. 仅导出已有数据为Excel")
    print()

    choice = input("请选择 (1-5): ").strip()

    if choice == '1':
        print("\n⚠️  完整模式将访问每个车辆的详情页，预计需要数天时间！")
        confirm = input("确认继续? (yes/no): ").strip().lower()
        if confirm == 'yes':
            crawler.run_full_crawl(start_batch=1, end_batch=403, crawl_detail=True)
        else:
            print("已取消")
    elif choice == '2':
        crawler.run_full_crawl(start_batch=1, end_batch=403, crawl_detail=False)
    elif choice == '3':
        print("\n测试模式: 批次385，爬取详情页")
        crawler.run_full_crawl(start_batch=385, end_batch=385, crawl_detail=True)
    elif choice == '4':
        print("\n继续上次任务，默认启用详情页爬取")
        crawler.run_full_crawl(start_batch=1, end_batch=403, crawl_detail=True)
    elif choice == '5':
        all_vehicles = crawler.load_data()
        if all_vehicles:
            crawler.export_to_excel(all_vehicles)
        else:
            print("没有数据可导出")
    else:
        print("无效选择")


if __name__ == "__main__":
    main()
