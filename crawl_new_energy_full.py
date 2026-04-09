#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全量新能源汽车爬虫 - 34种类型 × 403批次
任务：爬取所有新能源汽车子类型的完整数据
作者：Claude Code
日期：2026-04-09
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

class FullNewEnergyCrawler:
    """全量新能源汽车爬虫"""

    # ==================== 34种新能源汽车类型 ====================
    NEW_ENERGY_VEHICLE_TYPES = [
        # 纯电动系列（15种）
        {'code': '1', 'name': '纯电动汽车', 'category': '纯电动'},
        {'code': '294', 'name': '纯电动客车', 'category': '纯电动'},
        {'code': '295', 'name': '纯电动救护车', 'category': '纯电动'},
        {'code': '296', 'name': '纯电动载货车', 'category': '纯电动'},
        {'code': '297', 'name': '纯电动洒水车', 'category': '纯电动'},
        {'code': '300', 'name': '纯电动教练车', 'category': '纯电动'},
        {'code': '284', 'name': '换电式纯电动轿车', 'category': '换电式纯电动'},
        {'code': '285', 'name': '换电式纯电动自卸汽车', 'category': '换电式纯电动'},
        {'code': '286', 'name': '换电式纯电动厢式运输车', 'category': '换电式纯电动'},
        {'code': '287', 'name': '换电式纯电动多用途乘用车', 'category': '换电式纯电动'},
        {'code': '288', 'name': '换电式纯电动自卸式垃圾车', 'category': '换电式纯电动'},
        {'code': '289', 'name': '换电式纯电动半挂牵引车', 'category': '换电式纯电动'},
        {'code': '290', 'name': '换电式纯电动混凝土搅拌运输车', 'category': '换电式纯电动'},
        {'code': '291', 'name': '换电式纯电动福祉多用途乘用车', 'category': '换电式纯电动'},
        {'code': '182', 'name': '两用燃料汽车', 'category': '其他新能源'},

        # 混合动力系列（4种）
        {'code': '2', 'name': '混合动力电动汽车', 'category': '混合动力'},
        {'code': '3', 'name': '插电式混合动力汽车', 'category': '混合动力'},
        {'code': '4', 'name': '增程式混合动力汽车', 'category': '混合动力'},
        {'code': '5', 'name': '燃料式电池汽车', 'category': '其他新能源'},

        # 插电式混合动力专用车型（14种）
        {'code': '301', 'name': '插电式混合动力冷藏车', 'category': '插电式混合动力'},
        {'code': '302', 'name': '插电式混合动力宣传车', 'category': '插电式混合动力'},
        {'code': '303', 'name': '插电式混合动力清障车', 'category': '插电式混合动力'},
        {'code': '304', 'name': '插电式混合动力扫路车', 'category': '插电式混合动力'},
        {'code': '305', 'name': '插电式混合动力检测车', 'category': '插电式混合动力'},
        {'code': '306', 'name': '插电式混合动力救护车', 'category': '插电式混合动力'},
        {'code': '307', 'name': '插电式混合动力运钞车', 'category': '插电式混合动力'},
        {'code': '308', 'name': '插电式混合动力房车', 'category': '插电式混合动力'},
        {'code': '309', 'name': '插电式混合动力城市客车', 'category': '插电式混合动力'},
        {'code': '317', 'name': '插电式混合动力垃圾车', 'category': '插电式混合动力'},
        {'code': '318', 'name': '插电式混合动力牵引车', 'category': '插电式混合动力'},
        {'code': '319', 'name': '插电式混合动力载货车', 'category': '插电式混合动力'},
        {'code': '320', 'name': '插电式混合动力汽车起重机', 'category': '插电式混合动力'},
        {'code': '321', 'name': '插电式混合动力厢式运输车', 'category': '插电式混合动力'},
        {'code': '322', 'name': '插电式混合动力混凝土泵车', 'category': '插电式混合动力'},
        {'code': '323', 'name': '插电式混合动力绿化喷洒车', 'category': '插电式混合动力'},
        {'code': '324', 'name': '插电式混合动力多用途乘用车', 'category': '插电式混合动力'},
        {'code': '325', 'name': '甲醇插电式增程混合动力车', 'category': '插电式混合动力'},
        {'code': '326', 'name': '插电式混合动力仓栅式运输车', 'category': '插电式混合动力'},
        {'code': '327', 'name': '插电式混合动力混凝土搅拌运输车', 'category': '插电式混合动力'},
        {'code': '329', 'name': '插电式混合动力自卸汽车', 'category': '插电式混合动力'},
    ]

    def __init__(self):
        """初始化"""
        self.base_url = "https://www.jdcsww.com"
        self.data_dir = "data/full_new_energy_34types"
        self.state_file = os.path.join(self.data_dir, "crawler_state.json")

        # 创建数据目录
        os.makedirs(self.data_dir, exist_ok=True)

        # 设置日志
        self._setup_logging()

        # 初始化状态
        self.state = self._load_state()

        self.logger.info("=" * 70)
        self.logger.info("🚗 全量新能源汽车爬虫启动")
        self.logger.info("=" * 70)
        self.logger.info(f"📊 任务规模:")
        self.logger.info(f"   - 车辆类型: {len(self.NEW_ENERGY_VEHICLE_TYPES)} 种")
        self.logger.info(f"   - 批次范围: 1-403")
        self.logger.info(f"   - 总任务数: {len(self.NEW_ENERGY_VEHICLE_TYPES) * 403}")
        self.logger.info(f"   - 预计时间: ~76 小时（3.2天）")
        self.logger.info("=" * 70)

    def _setup_logging(self):
        """设置日志"""
        log_file = os.path.join(self.data_dir, f"crawler_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def _load_state(self) -> Dict:
        """加载爬取状态"""
        default_state = {
            'completed_tasks': [],  # 已完成的任务 ['batch-clmc', ...]
            'failed_tasks': [],      # 失败的任务
            'start_time': None,
            'last_update': None,
            'total_vehicles': 0,
            'current_batch': 0,
            'current_type_index': 0,
        }

        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                    self.logger.info(f"✅ 加载状态成功 - 已完成: {len(state['completed_tasks'])} 个任务")
                    return state
            except Exception as e:
                self.logger.warning(f"⚠️  加载状态失败: {e}，使用默认状态")

        return default_state

    def _save_state(self):
        """保存爬取状态"""
        self.state['last_update'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"❌ 保存状态失败: {e}")

    def _is_task_completed(self, batch: int, clmc_code: str) -> bool:
        """检查任务是否已完成"""
        task_key = f"{batch}-{clmc_code}"
        return task_key in self.state['completed_tasks']

    def _mark_task_completed(self, batch: int, clmc_code: str):
        """标记任务为已完成"""
        task_key = f"{batch}-{clmc_code}"
        if task_key not in self.state['completed_tasks']:
            self.state['completed_tasks'].append(task_key)
            self._save_state()

    def _mark_task_failed(self, batch: int, clmc_code: str, error: str):
        """标记任务为失败"""
        task_key = f"{batch}-{clmc_code}"
        if task_key not in self.state['failed_tasks']:
            self.state['failed_tasks'].append({
                'task': task_key,
                'error': error,
                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            self._save_state()

    def crawl_single_task(self, batch: int, vehicle_type: Dict) -> List[Dict]:
        """爬取单个任务（一个批次 + 一个车辆类型）"""
        clmc_code = vehicle_type['code']
        clmc_name = vehicle_type['name']
        task_key = f"{batch}-{clmc_code}"

        self.logger.info(f"🔍 开始任务: 批次{batch} - {clmc_name} ({clmc_code})")

        # 构建请求参数
        params = {
            'ggxh': '',
            'ggpc': str(batch),
            'zwpp': '',
            'clmc': clmc_code,     # 车辆类型代码
            'fdjxh': '',
            'qymc': '',
            'cph': '',
            'rylx': '',            # 燃料类型留空
            'viewtype': '0'
        }

        url = f"{self.base_url}/qcggs?{urllib.parse.urlencode(params)}"

        try:
            # 发送请求
            req = urllib.request.Request(
                url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                }
            )

            with urllib.request.urlopen(req, timeout=30) as response:
                html = response.read().decode('utf-8', errors='ignore')

                # 检查是否被拦截
                if '非正常访问' in html or '爬取数据嫌疑' in html:
                    self.logger.error(f"❌ 被拦截: {task_key}")
                    self._mark_task_failed(batch, clmc_code, "被拦截")
                    return []

                # 解析列表页
                vehicles = self._parse_list_page(html, batch, clmc_name)

                # 标记任务完成
                self._mark_task_completed(batch, clmc_code)

                self.logger.info(f"✅ 完成: {task_key} - 找到 {len(vehicles)} 辆车")
                return vehicles

        except Exception as e:
            self.logger.error(f"❌ 失败: {task_key} - {str(e)}")
            self._mark_task_failed(batch, clmc_code, str(e))
            return []

    def _parse_list_page(self, html: str, batch: int, fuel_type_name: str) -> List[Dict]:
        """解析列表页 - 提取基本信息"""
        vehicles = []

        # 提取车辆块
        vehicle_pattern = r'<li[^>]*>.*?<span class="car_name"><a href="([^"]+)"[^>]*>([^<]+)</a></span>.*?</li>'
        vehicle_matches = re.findall(vehicle_pattern, html, re.DOTALL)

        for idx, (detail_link, car_name) in enumerate(vehicle_matches, 1):
            vehicle = {
                '批次': batch,
                '车辆类型': fuel_type_name,
                '车辆名称': car_name.strip(),
                '详情链接': f"{self.base_url}{detail_link}",
            }

            # 提取公告编号
            bh_match = re.search(r'bh=([^&"\']+)', detail_link)
            if bh_match:
                vehicle['公告编号'] = bh_match.group(1)

            vehicles.append(vehicle)

        return vehicles

    def crawl_all(self, start_batch: int = 1, end_batch: int = 403, resume: bool = True):
        """爬取所有任务"""

        total_tasks = len(self.NEW_ENERGY_VEHICLE_TYPES) * (end_batch - start_batch + 1)
        completed_tasks = len(self.state['completed_tasks'])

        self.logger.info("=" * 70)
        self.logger.info(f"🚀 开始全量爬取")
        self.logger.info(f"📊 任务统计:")
        self.logger.info(f"   - 总任务数: {total_tasks}")
        self.logger.info(f"   - 已完成: {completed_tasks}")
        self.logger.info(f"   - 待完成: {total_tasks - completed_tasks}")
        self.logger.info(f"   - 进度: {(completed_tasks/total_tasks)*100:.2f}%")
        self.logger.info("=" * 70)

        all_vehicles = []

        # 遍历所有车辆类型
        for type_idx, vehicle_type in enumerate(self.NEW_ENERGY_VEHICLE_TYPES):
            clmc_code = vehicle_type['code']
            clmc_name = vehicle_type['name']

            self.logger.info(f"\n{'=' * 70}")
            self.logger.info(f"📂 车辆类型 [{type_idx+1}/{len(self.NEW_ENERGY_VEHICLE_TYPES)}]: {clmc_name}")
            self.logger.info(f"{'=' * 70}")

            # 遍历所有批次
            for batch in range(start_batch, end_batch + 1):

                # 检查是否已完成（断点续传）
                if resume and self._is_task_completed(batch, clmc_code):
                    self.logger.debug(f"⏭️  跳过已完成: 批次{batch} - {clmc_name}")
                    continue

                # 爬取单个任务
                vehicles = self.crawl_single_task(batch, vehicle_type)
                all_vehicles.extend(vehicles)

                # 随机延迟（避免被封禁）
                delay = random.uniform(2, 5)
                time.sleep(delay)

                # 每10个任务报告一次进度
                current_completed = len(self.state['completed_tasks'])
                if current_completed % 10 == 0 and current_completed > 0:
                    self.logger.info(f"📊 进度: {current_completed}/{total_tasks} ({(current_completed/total_tasks)*100:.1f}%) - 已采集: {len(all_vehicles)} 辆")

        # 保存最终结果
        self._save_final_data(all_vehicles)

        self.logger.info("=" * 70)
        self.logger.info(f"🎉 全量爬取完成!")
        self.logger.info(f"📊 最终统计:")
        self.logger.info(f"   - 总车辆数: {len(all_vehicles)}")
        self.logger.info(f"   - 成功任务: {len(self.state['completed_tasks'])}")
        self.logger.info(f"   - 失败任务: {len(self.state['failed_tasks'])}")
        self.logger.info("=" * 70)

    def _save_final_data(self, vehicles: List[Dict]):
        """保存最终数据"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        json_file = os.path.join(self.data_dir, f"vehicles_{timestamp}.json")

        try:
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(vehicles, f, ensure_ascii=False, indent=2)

            self.logger.info(f"💾 数据已保存: {json_file}")
            self.logger.info(f"📊 文件大小: {os.path.getsize(json_file) / 1024 / 1024:.2f} MB")

        except Exception as e:
            self.logger.error(f"❌ 保存数据失败: {e}")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='全量新能源汽车爬虫 - 34种类型 × 403批次')
    parser.add_argument('--start-batch', type=int, default=1, help='起始批次')
    parser.add_argument('--end-batch', type=int, default=403, help='结束批次')
    parser.add_argument('--no-resume', action='store_true', help='不使用断点续传（从头开始）')

    args = parser.parse_args()

    # 创建爬虫实例
    crawler = FullNewEnergyCrawler()

    # 开始爬取
    crawler.crawl_all(
        start_batch=args.start_batch,
        end_batch=args.end_batch,
        resume=not args.no_resume
    )


if __name__ == "__main__":
    main()
