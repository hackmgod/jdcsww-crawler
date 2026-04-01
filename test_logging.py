#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试日志功能
"""

import sys
sys.path.append('/Users/hackm/Applications/2026-jhoo/tram-inspection/jdcsww-crawler')

from crawl_production import ProductionCrawler


def main():
    """测试日志"""
    print("测试日志功能...")
    print()

    # 创建爬虫实例（会自动初始化日志）
    crawler = ProductionCrawler()

    # 测试日志
    crawler.logger.info("这是一条测试信息")
    crawler.logger.warning("这是一条警告信息")
    crawler.logger.error("这是一条错误信息")

    print()
    print("✅ 日志测试完成")
    print(f"📄 日志文件: {crawler.log_file}")
    print()
    print("你可以打开日志文件查看内容:")
    print(f"  cat {crawler.log_file}")


if __name__ == "__main__":
    main()
