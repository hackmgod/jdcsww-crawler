#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置文件
"""

# 爬取配置
CRAWL_CONFIG = {
    # 起始批次
    'start_batch': 403,

    # 结束批次（None表示只爬取start_batch）
    'end_batch': None,

    # 车辆类型 (1=纯电动)
    'vehicle_type': 1,

    # 燃料类型 (C=纯电动)
    'fuel_type': 'C',

    # 是否获取详情页
    'fetch_detail': True,

    # 详情页爬取数量（None表示全部，数字表示前N条）
    'detail_limit': 5,

    # 请求延迟范围（秒）
    'delay_min': 2,
    'delay_max': 5,

    # 重试次数
    'max_retries': 3,
}

# 输出配置
OUTPUT_CONFIG = {
    # 数据保存目录
    'data_dir': 'data',

    # 是否保存列表数据
    'save_list': True,

    # 是否保存详情数据
    'save_detail': True,

    # 文件名前缀
    'file_prefix': 'jdcsww',
}
