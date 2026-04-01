#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证断点续传功能
"""

import json
import os


def verify_resume():
    """验证断点续传功能"""
    state_file = 'data/production/crawler_state.json'
    data_file = 'data/production/all_vehicles.json'

    print("=" * 70)
    print("📊 断点续传状态检查")
    print("=" * 70)
    print()

    # 检查状态文件
    if os.path.exists(state_file):
        with open(state_file, 'r', encoding='utf-8') as f:
            state = json.load(f)

        print("✅ 状态文件存在")
        print(f"   已完成任务: {len(state['completed_batches'])} 个")
        print(f"   失败任务: {len(state['failed_batches'])} 个")
        print(f"   总车辆数: {state.get('total_vehicles', 0)} 辆")
        print(f"   最后更新: {state.get('last_update', '未知')}")

        if state['completed_batches']:
            print(f"\n   📋 已完成的批次 (前5个和后5个):")
            for task in state['completed_batches'][:5]:
                print(f"      ✓ {task}")
            if len(state['completed_batches']) > 10:
                print(f"      ...")
            for task in state['completed_batches'][-5:]:
                print(f"      ✓ {task}")

            # 找出下一个要爬取的批次
            last_completed = state['completed_batches'][-1]
            batch_num = int(last_completed.split('-')[0])
            fuel_type = last_completed.split('-')[1]

            if fuel_type == 'C':
                next_batch = f"{batch_num}-O"
            else:
                next_batch = f"{batch_num + 1}-C"

            print(f"\n   🔄 下一个任务: {next_batch}")

        if state['failed_batches']:
            print(f"\n   ⚠️  失败的任务:")
            for task in state['failed_batches'][:5]:
                print(f"      ✗ {task}")

    else:
        print("❌ 状态文件不存在")
        print("   还没有开始爬取或文件已删除")

    print()

    # 检查数据文件
    if os.path.exists(data_file):
        with open(data_file, 'r', encoding='utf-8') as f:
            vehicles = json.load(f)

        print("✅ 数据文件存在")
        print(f"   车辆总数: {len(vehicles)} 辆")
        print(f"   文件大小: {os.path.getsize(data_file) / 1024:.1f} KB")

        if vehicles:
            print(f"\n   📋 数据示例:")
            for v in vehicles[:3]:
                print(f"      批次{v['批次']} | {v['燃料类型']} | {v.get('公告型号', 'N/A')}")

    else:
        print("❌ 数据文件不存在")
        print("   还没有开始爬取或文件已删除")

    print()
    print("=" * 70)
    print("📋 说明:")
    print("=" * 70)
    print("""
1. 状态文件记录了已完成和失败的批次
2. 数据文件保存了所有爬取的车辆数据
3. 选择"选项3"继续时，会自动跳过已完成的批次
4. 每个批次完成后立即保存，不会丢失数据
5. 随机延迟: 5-15秒，避免被检测
    """)


if __name__ == "__main__":
    verify_resume()
