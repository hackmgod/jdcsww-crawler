#!/bin/bash
# 安装 Selenium 和 ChromeDriver

echo "================================"
echo "Selenium 安装指南"
echo "================================"
echo ""

# 1. 安装 Python 包
echo "[1/3] 安装 Python 包..."
pip3 install selenium webdriver-manager --user

# 2. 检查 Chrome
echo ""
echo "[2/3] 检查 Chrome 浏览器..."
if [ -f "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" ]; then
    echo "✓ Chrome 已安装"
else
    echo "✗ Chrome 未安装"
    echo "请从 https://www.google.com/chrome/ 下载安装"
fi

# 3. 检查 ChromeDriver
echo ""
echo "[3/3] 检查 ChromeDriver..."
if command -v chromedriver &> /dev/null; then
    echo "✓ ChromeDriver 已安装"
    chromedriver --version
else
    echo "✗ ChromeDriver 未安装"
    echo ""
    echo "安装方法（选择一种）："
    echo ""
    echo "方法1: 使用 Homebrew（推荐）"
    echo "  brew install chromedriver"
    echo ""
    echo "方法2: 手动下载"
    echo "  1. 访问 https://chromedriver.chromium.org/"
    echo "  2. 下载对应版本"
    echo "  3. 移动到 /usr/local/bin/chromedriver"
    echo "  4. 添加执行权限: chmod +x /usr/local/bin/chromedriver"
    echo ""
fi

echo ""
echo "================================"
echo "安装完成后，运行爬虫："
echo "  python3 selenium_crawler.py"
echo "================================"
