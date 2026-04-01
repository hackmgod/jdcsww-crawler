@echo off
REM 一键运行爬虫脚本（Windows版本）

cd /d "%~dp0"

echo ========================================
echo    机动车环保网数据爬虫
echo ========================================
echo.

REM 检查Python
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ 错误: 未找到Python
    echo 请先安装Python: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python版本:
python --version
echo.

REM 检查爬虫文件
if not exist "crawl_production_enhanced.py" (
    echo ❌ 错误: 未找到爬虫文件 crawl_production_enhanced.py
    pause
    exit /b 1
)

REM 运行爬虫
python crawl_production_enhanced.py

REM 检查运行结果
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo ✅ 爬虫运行完成！
    echo ========================================
    echo 数据保存在: data\production_enhanced\
) else (
    echo.
    echo ========================================
    echo ❌ 爬虫运行出错
    echo ========================================
)

echo.
pause
