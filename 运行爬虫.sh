#!/bin/bash
# 一键运行爬虫脚本（Mac/Linux版本）

cd "$(dirname "$0")"

echo "========================================"
echo "   机动车环保网数据爬虫"
echo "========================================"
echo ""
echo "启动时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到Python3"
    echo "请先安装Python3: https://www.python.org/downloads/"
    exit 1
fi

echo "✅ Python版本: $(python3 --version)"
echo ""

# 检查爬虫文件
if [ ! -f "crawl_production_enhanced.py" ]; then
    echo "❌ 错误: 未找到爬虫文件 crawl_production_enhanced.py"
    exit 1
fi

# 运行爬虫
python3 crawl_production_enhanced.py

# 检查运行结果
if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "✅ 爬虫运行完成！"
    echo "========================================"
    echo "数据保存在: data/production_enhanced/"
else
    echo ""
    echo "========================================"
    echo "❌ 爬虫运行出错"
    echo "========================================"
fi

echo ""
echo "结束时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""
read -p "按回车键关闭窗口..."
