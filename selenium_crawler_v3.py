#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Selenium爬虫 - 使用真实浏览器，最不容易被封禁
优点：模拟真实用户行为，难以被检测
缺点：速度慢，资源占用大
"""

import time
import random
import json
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class SeleniumCrawler:
    """Selenium爬虫 - 最难被检测"""

    def __init__(self, headless=False):
        self.headless = headless
        self.driver = None
        self.setup_driver()

    def setup_driver(self):
        """配置Chrome驱动"""
        options = Options()

        if self.headless:
            options.add_argument('--headless')  # 无头模式

        # 关键配置：避免被检测为自动化
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        # 设置User-Agent
        options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36')

        # 其他优化
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        # 窗口大小
        options.add_argument('--window-size=1920,1080')

        try:
            self.driver = webdriver.Chrome(options=options)

            # 执行脚本隐藏webdriver特征
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    })
                '''
            })

            print("✅ Chrome驱动启动成功")
        except Exception as e:
            print(f"❌ Chrome驱动启动失败: {e}")
            print("\n💡 请安装ChromeDriver:")
            print("   brew install chromedriver  # macOS")
            print("   或访问: https://chromedriver.chromium.org/")
            raise

    def random_delay(self, min_val=2, max_val=5):
        """随机延迟"""
        delay = random.uniform(min_val, max_val)
        time.sleep(delay)
        return delay

    def human_like_scroll(self):
        """模拟人类滚动"""
        try:
            scroll_pause_time = random.uniform(0.5, 1.5)
            last_height = self.driver.execute_script("return document.body.scrollHeight")

            for i in range(3):  # 滚动3次
                # 随机滚动位置
                scroll_position = random.randint(100, last_height // 3)
                self.driver.execute_script(f"window.scrollTo(0, {scroll_position});")
                time.sleep(scroll_pause_time)
        except:
            pass

    def visit_page(self, url):
        """访问页面"""
        try:
            print(f"🔗 访问: {url}")
            self.driver.get(url)

            # 随机等待页面加载
            self.random_delay(3, 6)

            # 模拟人类滚动
            self.human_like_scroll()

            # 检查是否被封禁
            page_source = self.driver.page_source

            if '非正常访问' in page_source or '爬取数据嫌疑' in page_source:
                print("  ⚠️  检测到封禁提示")
                return None

            print("  ✅ 页面加载成功")
            return page_source

        except TimeoutException:
            print("  ❌ 页面加载超时")
            return None
        except Exception as e:
            print(f"  ❌ 访问失败: {e}")
            return None

    def parse_list_page(self, html):
        """解析列表页"""
        import re
        vehicles = []

        try:
            pattern = r'<span class="car_name"><a href="([^"]+)"[^>]*>([^<]+)</a></span>'
            matches = re.findall(pattern, html)

            for idx, (link, name) in enumerate(matches[:10], 1):
                print(f"  ✓ {idx}. {name}")
                vehicles.append({
                    'name': name.strip(),
                    'link': f"{self.base_url}{link}"
                })

        except Exception as e:
            print(f"  ⚠️  解析失败: {e}")

        return vehicles

    def run(self, batches):
        """运行爬虫"""
        self.base_url = "https://www.jdcsww.com"

        print("=" * 70)
        print("🌐 Selenium爬虫 - 真实浏览器模式")
        print("=" * 70)
        print(f"\n⚙️  模式: {'无头模式' if self.headless else '有头模式'}")
        print(f"  目标批次: {len(batches)} 个\n")

        all_data = []

        try:
            # 先访问首页（建立会话）
            print("[1/2] 访问首页...")
            self.visit_page(self.base_url)
            time.sleep(random.uniform(2, 4))

            # 爬取批次
            print("\n[2/2] 开始爬取批次...")

            for idx, (batch, fuel_code, fuel_name) in enumerate(batches, 1):
                print(f"\n{'='*70}")
                print(f"[进度: {idx}/{len(batches)}] 批次 {batch} - {fuel_name}")
                print(f"{'='*70}")

                url = f"{self.base_url}/qcggs?ggpc={batch}&clmc=1&rylx={fuel_code}&viewtype=0"

                html = self.visit_page(url)
                if html:
                    data = self.parse_list_page(html)
                    all_data.extend(data)

                # 批次之间延迟
                if idx < len(batches):
                    delay = random.uniform(8, 15)
                    print(f"\n⏱️  等待 {delay:.1f} 秒...")
                    time.sleep(delay)

            # 保存数据
            if all_data:
                os.makedirs('data', exist_ok=True)
                filename = f"data/selenium_crawl_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(all_data, f, ensure_ascii=False, indent=2)

                print(f"\n{'='*70}")
                print(f"✅ 爬取完成")
                print(f"{'='*70}")
                print(f"  ✓ 总数据数: {len(all_data)}")
                print(f"  ✓ 保存路径: {filename}")
                print(f"{'='*70}")

        finally:
            # 关闭浏览器
            if self.driver:
                print("\n🔚 关闭浏览器...")
                self.driver.quit()


def main():
    """主函数"""
    import sys

    # 检查命令行参数
    headless = '--headless' in sys.argv

    crawler = SeleniumCrawler(headless=headless)

    # 测试：爬取3个批次
    test_batches = [
        (385, 'C', '新能源'),
        (384, 'C', '新能源'),
        (383, 'C', '新能源'),
    ]

    crawler.run(test_batches)


if __name__ == "__main__":
    main()
