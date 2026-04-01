#!/bin/bash
# 运行爬虫并自动打开结果文件

cd "$(dirname "$0")"

echo "========================================"
echo "   机动车环保网数据爬虫"
echo "========================================"
echo ""

# 运行爬虫
python3 crawl_production_enhanced.py

# 爬虫运行完成后，打开Excel文件
echo ""
echo "========================================"
echo "正在打开数据文件..."
echo "========================================"

EXCEL_FILE="data/production_enhanced/vehicles_complete_all.xlsx"

if [ -f "$EXCEL_FILE" ]; then
    # Mac系统
    if [[ "$OSTYPE" == "darwin"* ]]; then
        open "$EXCEL_FILE"
    # Linux系统
    else
        xdg-open "$EXCEL_FILE" 2>/dev/null || echo "请手动打开: $EXCEL_FILE"
    fi

    echo "✅ Excel文件已打开"
    echo "文件位置: $EXCEL_FILE"
else
    echo "⚠️  未找到Excel文件: $EXCEL_FILE"
    echo "可能爬虫未完成或使用的是快速模式"
fi

echo ""
read -p "按回车键关闭窗口..."
