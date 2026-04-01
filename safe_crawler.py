#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安全爬虫 - 专门用于避免IP封禁
特点：大延迟、随机化、智能调度
"""

import urllib.request
import json
import time
import random
import os
from datetime import datetime
from typing import List, Dict, Optional
from http.cookiejar import CookieJar


class SafeCrawler:
    """安全爬虫 - 避免IP封禁"""

    def __init__(self):
        self.base_url = "https://www.jdcsww.com"
        self.cookie_jar = CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.cookie_jar)
        )

        # 配置参数（保守策略）
        self.min_delay = 8.0      # 最小延迟（秒）
        self.max_delay = 15.0     # 最大延迟（秒）
        self.retry_delay = 20.0   # 重试延迟（秒）
        self.batch_rest = 50      # 每N批次休息
        self.rest_time = 30       # 休息时间（秒）

        # 统计
        self.request_count = 0
        self.batch_count = 0
        self.block_count = 0

    def random_delay(self, min_val=None, max_val=None):
        """随机延迟"""
        min_val = min_val or self.min_delay
        max_val = max_val or self.max_delay
        delay = random.uniform(min_val, max_val)

        print(f"⏱️  等待 {delay:.1f} 秒...")
        time.sleep(delay)
        return delay

    def check_if_blocked(self, html):
        """检查是否被封禁"""
        if not html:
            return True

        if '非正常访问' in html or '爬取数据嫌疑' in html:
            return True

        return False

    def fetch_with_retry(self, url, referer=None, max_retry=3):
        """带重试的请求"""
        for attempt in range(max_retry):
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                    'Accept-Encoding': 'identity',
                    'Connection': 'keep-alive',
                }

                if referer:
                    headers['Referer'] = referer

                req = urllib.request.Request(url, headers=headers)

                with self.opener.open(req, timeout=30) as response:
                    html = response.read().decode('utf-8', errors='ignore')

                    # 检查是否被封禁
                    if self.check_if_blocked(html):
                        self.block_count += 1
                        print(f"  ⚠️  检测到封禁提示 (尝试 {attempt + 1}/{max_retry})")

                        if attempt < max_retry - 1:
                            print(f"  🔄 等待 {self.retry_delay} 秒后重试...")
                            time.sleep(self.retry_delay)
                            continue
                        else:
                            print("  ❌ 重试失败，IP可能被封禁")
                            return None

                    return html

            except Exception as e:
                print(f"  ⚠️  请求异常: {e}")
                if attempt < max_retry - 1:
                    print(f"  🔄 等待 {self.retry_delay} 秒后重试...")
                    time.sleep(self.retry_delay)
                else:
                    return None

        return None

    def smart_rest(self):
        """智能休息"""
        self.batch_count += 1

        if self.batch_count % self.batch_rest == 0:
            print(f"\n{'='*70}")
            print(f"💤 已完成 {self.batch_count} 个批次，休息 {self.rest_time} 秒...")
            print(f"{'='*70}\n")
            time.sleep(self.rest_time)

    def crawl_batch(self, batch, fuel_type_code, fuel_type_name):
        """爬取单个批次"""
        print(f"\n{'='*70}")
        print(f"📋 批次 {batch} - {fuel_type_name}")
        print(f"{'='*70}")

        # 请求前延迟
        if self.request_count > 0:
            self.random_delay()

        url = f"{self.base_url}/qcggs?ggpc={batch}&clmc=1&rylx={fuel_type_code}&viewtype=0"

        print(f"🔗 URL: {url}")
        html = self.fetch_with_retry(url, referer=f"{self.base_url}/qcggs")

        if not html:
            print("  ❌ 获取失败")
            return []

        self.request_count += 1

        # 解析数据（简化版）
        import re
        vehicles = []
        pattern = r'<span class="car_name"><a href="([^"]+)"[^>]*>([^<]+)</a></span>'
        matches = re.findall(pattern, html)

        for idx, (link, name) in enumerate(matches[:5], 1):  # 只取前5个
            print(f"  ✓ {idx}. {name}")
            vehicles.append({
                'name': name,
                'link': f"{self.base_url}{link}"
            })

        print(f"  ✅ 找到 {len(vehicles)} 条数据")

        # 智能休息
        self.smart_rest()

        return vehicles

    def run(self, batches):
        """运行爬虫"""
        print("=" * 70)
        print("🛡️  安全爬虫 - 避免IP封禁模式")
        print("=" * 70)
        print(f"\n⚙️  配置:")
        print(f"  - 延迟范围: {self.min_delay}-{self.max_delay} 秒")
        print(f"  - 重试延迟: {self.retry_delay} 秒")
        print(f"  - 休息策略: 每 {self.batch_rest} 批次休息 {self.rest_time} 秒")
        print(f"  - 目标批次: {len(batches)} 个\n")

        all_data = []

        for idx, (batch, fuel_code, fuel_name) in enumerate(batches, 1):
            print(f"\n[进度: {idx}/{len(batches)}]")

            data = self.crawl_batch(batch, fuel_code, fuel_name)
            if data:
                all_data.extend(data)

        # 保存数据
        if all_data:
            os.makedirs('data', exist_ok=True)
            filename = f"data/safe_crawl_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(all_data, f, ensure_ascii=False, indent=2)

            print(f"\n{'='*70}")
            print(f"✅ 爬取完成")
            print(f"{'='*70}")
            print(f"  ✓ 总请求数: {self.request_count}")
            print(f"  ✓ 总数据数: {len(all_data)}")
            print(f"  ✓ 封禁次数: {self.block_count}")
            print(f"  ✓ 保存路径: {filename}")
            print(f"{'='*70}")


def main():
    """主函数"""
    crawler = SafeCrawler()

    # 测试：爬取3个批次
    test_batches = [
        (385, 'C', '新能源'),
        (384, 'C', '新能源'),
        (383, 'C', '新能源'),
    ]

    crawler.run(test_batches)


if __name__ == "__main__":
    main()
