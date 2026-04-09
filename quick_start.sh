#!/bin/bash
# quick_start.sh - 快速启动脚本

echo "🚗 全量新能源汽车爬虫 - 快速启动"
echo "======================================"

# 检查Python版本
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到 Python3，请先安装"
    exit 1
fi

# 检查数据目录
DATA_DIR="data/full_new_energy_34types"
mkdir -p "$DATA_DIR"

# 显示菜单
echo ""
echo "请选择执行模式："
echo "1️⃣  单次执行全部（不推荐，需要76小时）"
echo "2️⃣  分批执行（推荐，每天一批）"
echo "3️⃣  自定义批次范围"
echo "4️⃣  查看当前进度"
echo "5️⃣  重试失败的任务"
echo ""
read -p "请输入选项 (1-5): " choice

case $choice in
    1)
        echo "⚠️  警告：这将需要76小时连续运行！"
        read -p "确认执行？(y/n): " confirm
        if [ "$confirm" = "y" ]; then
            echo "🚀 开始全量爬取..."
            python3 crawl_new_energy_full.py
        fi
        ;;
    2)
        echo "📅 分批执行模式"
        echo "第1天: 批次 1-150"
        echo "第2天: 批次 151-300"
        echo "第3天: 批次 301-403"
        echo ""
        read -p "请选择天数 (1-3): " day
        case $day in
            1)
                echo "🚀 启动第1天任务（批次 1-150）..."
                python3 crawl_new_energy_full.py --start-batch 1 --end-batch 150
                ;;
            2)
                echo "🚀 启动第2天任务（批次 151-300）..."
                python3 crawl_new_energy_full.py --start-batch 151 --end-batch 300
                ;;
            3)
                echo "🚀 启动第3天任务（批次 301-403）..."
                python3 crawl_new_energy_full.py --start-batch 301 --end-batch 403
                ;;
            *)
                echo "❌ 无效选项"
                exit 1
                ;;
        esac
        ;;
    3)
        read -p "请输入起始批次 (1-403): " start
        read -p "请输入结束批次 (1-403): " end
        echo "🚀 启动自定义任务（批次 $start-$end）..."
        python3 crawl_new_energy_full.py --start-batch "$start" --end-batch "$end"
        ;;
    4)
        if [ -f "$DATA_DIR/crawler_state.json" ]; then
            COMPLETED=$(python3 -c "import json; print(len(json.load(open('$DATA_DIR/crawler_state.json'))['completed_tasks']))")
            TOTAL=13702
            echo "📊 当前进度:"
            echo "   已完成: $COMPLETED/$TOTAL"
            python3 -c "print(f'   进度: {$COMPLETED/$TOTAL*100:.2f}%')"
            echo "   剩余: $((TOTAL - COMPLETED))"
        else
            echo "⚠️  未找到状态文件，尚未开始爬取"
        fi
        ;;
    5)
        echo "🔄 重试失败的任务..."
        python3 retry_failed.py
        ;;
    *)
        echo "❌ 无效选项"
        exit 1
        ;;
esac

echo ""
echo "======================================"
echo "✅ 任务完成"
echo "📁 数据目录: $DATA_DIR"
echo "📝 日志文件: $DATA_DIR/crawler_*.log"
echo "======================================"
