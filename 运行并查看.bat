@echo off
REM 运行爬虫并自动打开结果文件（Windows版本）

cd /d "%~dp0"

echo ========================================
echo    机动车环保网数据爬虫
echo ========================================
echo.

REM 运行爬虫
python crawl_production_enhanced.py

REM 爬虫运行完成后，打开Excel文件
echo.
echo ========================================
echo 正在打开数据文件...
echo ========================================

set EXCEL_FILE=data\production_enhanced\vehicles_complete_all.xlsx

if exist "%EXCEL_FILE%" (
    start "" "%EXCEL_FILE%"
    echo ✅ Excel文件已打开
    echo 文件位置: %EXCEL_FILE%
) else (
    echo ⚠️  未找到Excel文件: %EXCEL_FILE%
    echo 可能爬虫未完成或使用的是快速模式
)

echo.
pause
