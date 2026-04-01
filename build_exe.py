#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
打包脚本 - 使用PyInstaller将爬虫打包成可执行文件
"""

import os
import sys
import subprocess

def main():
    print("=" * 70)
    print("爬虫打包工具")
    print("=" * 70)

    # 检查PyInstaller是否已安装
    try:
        import PyInstaller
        print(f"✅ PyInstaller已安装: {PyInstaller.__version__}")
    except ImportError:
        print("\n❌ PyInstaller未安装")
        print("正在安装PyInstaller...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "pyinstaller", "--break-system-packages"
        ])
        print("✅ PyInstaller安装完成")

    print("\n" + "=" * 70)
    print("开始打包...")
    print("=" * 70)

    # PyInstaller命令
    pyinstaller_cmd = [
        "pyinstaller",
        "--name=JDCCrawler",                    # 可执行文件名称
        "--onefile",                            # 打包成单个文件
        "--windowed=False",                     # 显示控制台窗口（必须）
        "--icon=icon.ico" if os.path.exists("icon.ico") else "",  # 图标（可选）
        "--add-data=README_ENHANCED.md:.",      # 添加说明文档
        "--clean",                              # 清理临时文件
        "--noconfirm",                          # 覆盖输出
        "crawl_production_enhanced.py"          # 主脚本
    ]

    # 移除空参数
    pyinstaller_cmd = [arg for arg in pyinstaller_cmd if arg]

    print(f"\n执行命令: {' '.join(pyinstaller_cmd)}\n")

    try:
        subprocess.check_call(pyinstaller_cmd)
        print("\n" + "=" * 70)
        print("✅ 打包成功！")
        print("=" * 70)
        print(f"\n可执行文件位置: dist/JDCCrawler{''.exe' if sys.platform == 'win32' else ''}")

        # 显示文件大小
        if sys.platform == "win32":
            exe_path = "dist/JDCCrawler.exe"
        else:
            exe_path = "dist/JDCCrawler"

        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"文件大小: {size_mb:.1f} MB")

        print("\n使用说明:")
        print("1. 将 dist/JDCCrawler 复制到目标电脑")
        print("2. 直接运行即可")
        print("3. 数据将保存在程序同目录的 data/ 文件夹中")

    except subprocess.CalledProcessError as e:
        print(f"\n❌ 打包失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
