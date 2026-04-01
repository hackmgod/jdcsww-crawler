# 🚀 爬虫打包使用指南

## 方案一：PyInstaller打包（推荐）

### 特点
- ✅ 单个可执行文件
- ✅ 无需安装Python
- ✅ 双击即运行
- ✅ 适合分发给任何人

### 打包步骤

#### 1. 安装PyInstaller
```bash
pip3 install pyinstaller --break-system-packages
```

#### 2. 打包成可执行文件
```bash
cd tram-inspection/jdcsww-crawler

# 方法1: 使用spec文件（推荐）
pyinstaller JDCCrawler.spec

# 方法2: 使用Python脚本
python3 build_exe.py

# 方法3: 直接命令
pyinstaller --onefile --name=JDCCrawler --console crawl_production_enhanced.py
```

#### 3. 查看输出
打包完成后，可执行文件在 `dist/` 目录：
- Windows: `dist/JDCCrawler.exe`
- Mac/Linux: `dist/JDCCrawler`

#### 4. 分发使用
1. 将 `dist/JDCCrawler` (或 `JDCCrawler.exe`) 复制到任何电脑
2. 直接运行即可
3. 数据保存在程序同目录的 `data/production_enhanced/` 文件夹

---

## 方案二：虚拟环境（技术人员）

### 特点
- ✅ 标准Python方案
- ✅ 易于更新维护
- ✅ 适合技术人员

### 步骤

#### 1. 创建依赖文件
```bash
cd tram-inspection/jdcsww-crawler
cat > requirements.txt << EOF
urllib3>=1.26.0
openpyxl>=3.0.0
EOF
```

#### 2. 创建虚拟环境
```bash
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
# 或 venv\Scripts\activate  # Windows
```

#### 3. 安装依赖
```bash
pip install -r requirements.txt
```

#### 4. 运行爬虫
```bash
python crawl_production_enhanced.py
```

---

## 方案三：一键脚本（最简单）

### Windows版本
```batch
@echo off
echo ========================================
echo 机动车环保网数据爬虫
echo ========================================
echo.

python3 crawl_production_enhanced.py

pause
```

保存为 `运行爬虫.bat`，双击运行。

### Mac/Linux版本
```bash
#!/bin/bash
echo "========================================"
echo "机动车环保网数据爬虫"
echo "========================================"
echo ""

python3 crawl_production_enhanced.py
```

保存为 `运行爬虫.sh`，添加执行权限：
```bash
chmod +x 运行爬虫.sh
./运行爬虫.sh
```

---

## 📦 打包文件清单

打包后分发的文件：
```
JDCCrawler/
├── JDCCrawler          # 可执行文件
├── 使用说明.txt         # 使用说明
└── data/               # 数据输出目录（自动创建）
    ├── production_enhanced/
    │   ├── vehicles_complete_all.xlsx
    │   └── all_vehicles_complete.json
    └── images/
```

---

## 🎯 推荐方案选择

| 使用场景 | 推荐方案 |
|---------|---------|
| **分发给非技术人员** | PyInstaller打包 |
| **技术人员使用** | 虚拟环境 |
| **临时使用** | 一键脚本 |
| **服务器部署** | Docker |

---

## ⚠️ 注意事项

1. **首次打包**：第一次打包可能需要下载PyInstaller引导程序，需要联网
2. **文件大小**：打包后的可执行文件约30-50MB
3. **杀毒软件**：某些杀毒软件可能误报，需要添加信任
4. **依赖库**：如果爬虫使用了openpyxl导出Excel，打包时已包含
5. **数据存储**：程序运行会在当前目录生成data文件夹

---

## 🔧 故障排除

### 问题1: PyInstaller安装失败
```bash
# 尝试使用用户模式安装
pip install pyinstaller --user
```

### 问题2: 打包后无法运行
```bash
# 使用--debug模式查看详细信息
pyinstaller --onefile --debug=all crawl_production_enhanced.py
```

### 问题3: 缺少模块
在spec文件的hiddenimports中添加缺少的模块

---

## 📞 需要帮助？

如果遇到问题，请检查：
1. Python版本 >= 3.8
2. PyInstaller版本 >= 5.0
3. 爬虫脚本无语法错误
4. 所有依赖已正确安装
