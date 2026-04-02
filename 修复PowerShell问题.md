# 🔧 Windows PowerShell 命令兼容性修复

## ❌ 问题

```
ls -la dist/
```

这是 **macOS/Linux** 命令，在 **Windows PowerShell** 中不支持！

## ✅ 修复

已经修改 `.github/workflows/build.yml`，添加平台特定的命令：

**Windows (PowerShell):**
```yaml
shell: pwsh
run: |
  dir dist\
  if (Test-Path dist) { echo "YES" } else { echo "NO" }
```

**macOS/Linux:**
```yaml
run: |
  ls -la dist/
  test -d dist && echo "YES" || echo "NO"
```

---

## 🚀 推送到GitHub

### 步骤1：提交修复

```bash
cd tram-inspection/jdcsww-crawler

git add .github/workflows/build.yml
git commit -m "fix: 修复Windows PowerShell命令兼容性问题"
git push
```

### 步骤2：手动触发工作流

1. 访问你的GitHub仓库
2. 点击 "Actions" 标签
3. 选择 "Build Executable" 工作流
4. 点击 "Run workflow" 按钮
5. 等待5-10分钟

---

## 📦 如果还失败

GitHub Actions 确实不太稳定，建议使用**其他方案**：

### 🎯 推荐：云Windows服务器（30分钟完成）

**Azure 免费版：**
1. 注册：https://azure.microsoft.com/free/
2. 创建 Windows 虚拟机
3. 远程桌面连接
4. 运行打包命令：
   ```cmd
   pip install pyinstaller openpyxl
   pyinstaller --onefile --name=JDCCrawler --console crawl_production_enhanced.py
   ```
5. 下载 `dist/JDCCrawler.exe`

**100% 成功，而且免费！**

---

## 📞 需要帮助？

如果 GitHub Actions 还是不行，我可以：
1. 给你准备详细的 Azure 使用教程
2. 或者帮你准备借用朋友电脑的打包脚本

**告诉我你想用哪个方案？** 🚀
