#!/bin/bash
# 一键修复并推送GitHub Actions

echo "========================================"
echo "  GitHub Actions 修复工具"
echo "========================================"
echo ""

# 检查git状态
echo "1️⃣  检查Git状态..."
if git rev-parse --git-dir > /dev/null 2>&1; then
    echo "✅ Git仓库已初始化"
else
    echo "❌ Git仓库未初始化"
    echo "请先执行: git init"
    exit 1
fi

echo ""
echo "2️⃣  添加修复后的文件..."
git add .github/workflows/build.yml
git add GitHub_Actions修复指南.md

echo ""
echo "3️⃣  提交修复..."
git commit -m "fix: 修复GitHub Actions打包问题

- 修改文件路径问题（README.txt）
- 使用PowerShell压缩替代7z
- 添加调试信息
- 降低PyInstaller日志级别"

echo ""
echo "4️⃣  推送到GitHub..."
git push

echo ""
echo "========================================"
echo "✅ 修复已推送到GitHub！"
echo "========================================"
echo ""
echo "下一步："
echo "1. 访问你的GitHub仓库"
echo "2. 点击 'Actions' 标签"
echo "3. 点击 'Run workflow' 手动触发打包"
echo "4. 等待5-10分钟"
echo "5. 下载打包好的文件"
echo ""
