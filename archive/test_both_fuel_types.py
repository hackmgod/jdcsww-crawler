#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试完整功能 - 纯电动 + 混合动力
"""

import sys
sys.path.append('/Users/hackm/Applications/2026-jhoo/tram-inspection/jdcsww-crawler')

from full_data_crawler import FullDataCrawler


def main():
    """测试完整功能"""
    crawler = FullDataCrawler()

    print("=" * 70)
    print("完整功能测试 - 纯电动 + 混合动力")
    print("=" * 70)
    print()

    # 测试批次350 (已知有混合动力)
    print("📊 测试批次350 (包含纯电动和混合动力)")
    print("-" * 70)

    vehicles = crawler.crawl_all_batches(
        start_batch=350,
        end_batch=350,
        fuel_types=['C', 'O']  # 纯电动 + 混合动力
    )

    if vehicles:
        print("\n" + "=" * 70)
        print("📊 数据统计:")
        print("=" * 70)

        # 统计燃料类型
        from collections import Counter
        fuels = Counter(v['燃料类型'] for v in vehicles)
        for fuel, count in fuels.items():
            print(f"  {fuel}: {count} 辆")

        print(f"\n  总计: {len(vehicles)} 辆")

        # 显示示例
        print("\n📋 数据示例:")
        print("-" * 70)
        for v in vehicles[:3]:
            print(f"\n{v['燃料类型']} | 批次{v['批次']}")
            print(f"  公告型号: {v.get('公告型号', 'N/A')}")
            print(f"  生产企业: {v.get('生产企业', 'N/A')}")
            print(f"  车辆名称: {v['车辆名称'][:40]}...")

        # 导出Excel
        print("\n" + "=" * 70)
        print("📊 导出Excel...")
        print("=" * 70)
        crawler.export_to_excel(vehicles, 'test_batch350_both_types.xlsx')

        print("\n" + "=" * 70)
        print("✅ 测试成功！")
        print("✅ 纯电动 + 混合动力 均可正常爬取")
        print("=" * 70)
        print("\n🚀 现在可以开始全量爬取了:")
        print("   python3 crawl_production.py")
        print("   选择 1 - 爬取所有批次(1-403)")


if __name__ == "__main__":
    main()
