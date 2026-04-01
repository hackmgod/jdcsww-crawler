#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
支持代理的爬虫版本
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
from typing import List, Dict, Optional
from http.cookiejar import CookieJar


class ProxyCrawler:
    """支持代理IP的爬虫"""

    def __init__(self, use_proxy=False):
        self.base_url = "https://www.jdcsww.com"
        self.output_dir = 'data/production'
        os.makedirs(self.output_dir, exist_ok=True)

        # 代理配置
        self.use_proxy = use_proxy
        self.proxies = []

        # 代理池（如果使用）
        if use_proxy:
            self.setup_proxies()

        # Cookie管理
        self.cookie_jars = {}  # 每个代理独立的cookie
        self.openers = {}      # 每个代理独立的opener

        self._setup_logger()

    def setup_proxies(self):
        """配置代理池"""
        print("\n" + "=" * 70)
        print("代理IP配置")
        print("=" * 70)

        # 方案1: 免费代理（不稳定）
        print("\n选择代理来源:")
        print("1. 手动输入代理")
        print("2. 从文件读取")
        print("3. 不使用代理")

        choice = input("\n请选择 (1-3): ").strip()

        if choice == '1':
            print("\n输入代理地址（格式: http://ip:port 或 socks5://ip:port）")
            print("输入空行结束\n")
            while True:
                proxy = input("代理地址: ").strip()
                if not proxy:
                    break
                if self.test_proxy(proxy):
                    self.proxies.append(proxy)
                    print(f"  ✓ {proxy}")
                else:
                    print(f"  ✗ {proxy} - 无效")

        elif choice == '2':
            proxy_file = input("代理文件路径: ").strip()
            if os.path.exists(proxy_file):
                with open(proxy_file, 'r') as f:
                    for line in f:
                        proxy = line.strip()
                        if proxy and self.test_proxy(proxy):
                            self.proxies.append(proxy)

        print(f"\n✓ 加载了 {len(self.proxies)} 个代理")

        if not self.proxies:
            print("⚠️  未配置代理，将直接连接")
            self.use_proxy = False

    def test_proxy(self, proxy_url):
        """测试代理是否可用"""
        try:
            proxy_handler = urllib.request.ProxyHandler({'http': proxy_url, 'https': proxy_url})
            opener = urllib.request.build_opener(proxy_handler)
            req = urllib.request.Request('https://www.jdcsww.com', timeout=10)
            with opener.open(req, timeout=10) as response:
                return True
        except:
            return False

    def get_opener(self, proxy=None):
        """获取opener（每个代理独立）"""
        if proxy and proxy in self.openers:
            return self.openers[proxy], self.cookie_jars[proxy]

        cookie_jar = CookieJar()

        if proxy:
            proxy_handler = urllib.request.ProxyHandler({'http': proxy, 'https': proxy})
            opener = urllib.request.build_opener(
                proxy_handler,
                urllib.request.HTTPCookieProcessor(cookie_jar)
            )
        else:
            opener = urllib.request.build_opener(
                urllib.request.HTTPCookieProcessor(cookie_jar)
            )

        if proxy:
            self.openers[proxy] = opener
            self.cookie_jars[proxy] = cookie_jar

        return opener, cookie_jar

    def _setup_logger(self):
        """配置日志"""
        self.logger = logging.getLogger('ProxyCrawler')
        self.logger.setLevel(logging.INFO)

        if self.logger.handlers:
            self.logger.handlers.clear()

        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        log_file = os.path.join(self.output_dir, f'crawler_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

        self.log_file = log_file

    def fetch_with_session(self, url, referer=None, proxy=None):
        """使用会话获取页面"""
        opener, cookie_jar = self.get_opener(proxy)

        for attempt in range(3):
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'zh-CN,zh;q=0.9',
                }

                if referer:
                    headers['Referer'] = referer

                req = urllib.request.Request(url, headers=headers)
                with opener.open(req, timeout=30) as response:
                    html = response.read().decode('utf-8', errors='ignore')

                    if '非正常访问' in html or '爬取数据嫌疑' in html:
                        if attempt < 2:
                            time.sleep(5)
                            continue
                        else:
                            return None

                    return html

            except Exception as e:
                if attempt < 2:
                    time.sleep(3)
                else:
                    return None

        return None

    def crawl_single_batch(self, batch, fuel_type_code, fuel_type_name):
        """爬取单个批次"""
        url = f"{self.base_url}/qcggs"
        params = {
            'ggxh': '',
            'ggpc': str(batch),
            'zwpp': '',
            'clmc': '1',
            'fdjxh': '',
            'qymc': '',
            'cph': '',
            'rylx': fuel_type_code,
            'viewtype': '0'
        }
        list_url = f"{url}?{urllib.parse.urlencode(params)}"

        # 选择代理（轮换）
        proxy = None
        if self.use_proxy and self.proxies:
            proxy = random.choice(self.proxies)

        proxy_info = f" [代理: {proxy}] " if proxy else " "
        print(f"  批次{batch} [{fuel_type_name}]{proxy_info}...")

        html = self.fetch_with_session(list_url, proxy=proxy)

        if not html:
            return []

        # 解析（省略，与之前相同）
        # ...

        return []  # 简化示例


def main():
    """主函数"""
    print("=" * 70)
    print("代理IP爬虫")
    print("=" * 70)

    print("\n是否使用代理IP？")
    print("1. 是，使用代理")
    print("2. 否，直接连接")

    choice = input("\n请选择 (1-2): ").strip()

    use_proxy = (choice == '1')

    crawler = ProxyCrawler(use_proxy=use_proxy)

    # ... 继续爬取逻辑


if __name__ == "__main__":
    main()
