#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量测试爬虫 - 爬取所有车辆
"""

import sys
sys.path.append('/Users/hackm/Applications/2026-jhoo/tram-inspection/jdcsww-crawler')

from complete_data_crawler import CompleteDataCrawler


def main():
    crawler = CompleteDataCrawler()

    # 爬取385批次的所有30辆车
    print("=" * 70)
    print("批量测试 - 爬取385批次所有车辆")
    print("=" * 70)

    crawler.run(
        batch=385,
        detail_limit=30  # 爬取所有30辆车
    )


if __name__ == "__main__":
    main()
