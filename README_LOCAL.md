# 本地使用指南

## 📥 下载项目

### 方式一：克隆Git仓库
```bash
git clone https://github.com/bugchengxuyuan/Procurement-Management-System.git
cd Procurement-Management-System
```

### 方式二：下载ZIP压缩包
1. 从GitHub下载ZIP文件
2. 解压到本地目录
3. 进入项目目录
```bash
cd Procurement-Management-System
```

---

## 🚀 快速开始（3步完成）

### 第一步：准备Excel数据

将您的采购表Excel文件放在项目根目录：

```bash
# 项目目录结构
Procurement-Management-System/
├── 采购表-2（最新版.xlsx  ← 将您的Excel文件放这里
├── api/
├── web/
├── import_data.sh
└── start.sh
```

**重要提示：**
- Excel文件名可以不同，但需要修改 `import_data.sh` 第16行的文件名
- 或者直接重命名您的Excel文件为 `采购表-2（最新版.xlsx`

### 第二步：导入数据

```bash
# 在项目根目录运行
bash import_data.sh
```

**这个脚本会：**
- ✅ 自动检测项目路径
- ✅ 检查Excel文件
- ✅ 备份现有数据
- ✅ 导入800条订单
- ✅ 自动生成缺失的订单编号
- ✅ 验证导入结果

### 第三步：启动系统

```bash
# 在项目根目录运行
bash start.sh
```

**然后访问：**
- 前端应用：http://localhost:3000
- 后端API：http://localhost:8000
- API文档：http://localhost:8000/docs

---

## 📋 详细步骤

### 1. 环境要求

**必需：**
- Python 3.11+ （推荐3.11）
- Node.js 18+ （推荐18或20）
- npm 或 yarn

**检查环境：**
```bash
# 检查Python版本
python3 --version

# 检查Node.js版本
node --version

# 检查npm版本
npm --version
```

### 2. 安装Python依赖

```bash
cd api
pip install -r requirements.txt
cd ..
```

**或使用虚拟环境（推荐）：**
```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 安装依赖
cd api
pip install -r requirements.txt
cd ..
```

### 3. 安装前端依赖

```bash
cd web
npm install
cd ..
```

### 4. 导入数据

```bash
# 确保在项目根目录
bash import_data.sh
```

### 5. 启动服务

#### 方式一：使用启动脚本（推荐）
```bash
bash start.sh
```

#### 方式二：手动启动

**启动后端：**
```bash
cd api
python3 run.py
```

**启动前端（新终端）：**
```bash
cd web
npm run dev
```

---

## 🗂️ 数据文件位置

所有数据都存储在您的本地项目目录中：

```
Procurement-Management-System/
├── data/
│   └── procurement.db          ← SQLite数据库（导入后自动创建）
├── 采购表-2（最新版.xlsx         ← 您的Excel源文件
└── api/
    └── migrate_data.py         ← 数据导入脚本
```

**数据库文件：** `data/procurement.db`
- 所有订单和产品数据都存储在这里
- 可以用任何SQLite工具查看
- 备份此文件即可备份所有数据

---

## 💻 不同操作系统使用说明

### Windows 用户

#### 使用Git Bash（推荐）
```bash
# 安装Git for Windows后，使用Git Bash运行
bash import_data.sh
bash start.sh
```

#### 使用PowerShell
```powershell
# 导入数据
python api/migrate_data.py

# 启动后端
cd api
python run.py

# 启动前端（新PowerShell窗口）
cd web
npm run dev
```

### macOS 用户

```bash
# 完全一样
bash import_data.sh
bash start.sh
```

### Linux 用户

```bash
# 完全一样
bash import_data.sh
bash start.sh
```

---

## 📝 自定义配置

### 修改Excel文件名

编辑 `import_data.sh` 第16行：

```bash
# 修改前
if [ ! -f "采购表-2（最新版.xlsx" ]; then

# 修改后（改成您的文件名）
if [ ! -f "您的Excel文件名.xlsx" ]; then
```

### 修改端口号

#### 后端端口（默认8000）
编辑 `api/run.py` 第8行：
```python
port=8000,  # 改成您想要的端口
```

#### 前端端口（默认3000）
编辑 `web/vite.config.ts` 第12行：
```typescript
port: 3000,  // 改成您想要的端口
```

---

## 🔧 常见问题

### Q1: 找不到Excel文件
```bash
# 检查文件是否在项目根目录
ls -lh *.xlsx

# 或在Windows上
dir *.xlsx
```

**解决方案：**
- 确保Excel文件在项目根目录
- 或修改 `import_data.sh` 中的文件名

### Q2: Python命令不存在
```bash
# 尝试使用python3
python3 --version

# 如果还不行，安装Python
```

**Windows用户：** 从 https://www.python.org/downloads/ 下载安装

### Q3: npm install 失败
```bash
# 清除缓存重试
npm cache clean --force
npm install
```

### Q4: 端口被占用
```bash
# 找出占用端口的进程
# Linux/Mac:
lsof -i :8000
lsof -i :3000

# Windows:
netstat -ano | findstr :8000
netstat -ano | findstr :3000

# 修改端口号（见上面"修改端口号"部分）
```

### Q5: 权限错误（Linux/Mac）
```bash
# 给脚本添加执行权限
chmod +x import_data.sh
chmod +x start.sh
```

---

## 🎯 完整示例（从零开始）

```bash
# 1. 下载项目
git clone https://github.com/bugchengxuyuan/Procurement-Management-System.git
cd Procurement-Management-System

# 2. 放置Excel文件
# 将您的Excel文件复制到当前目录

# 3. 安装Python依赖
cd api
pip install -r requirements.txt
cd ..

# 4. 安装前端依赖
cd web
npm install
cd ..

# 5. 导入数据
bash import_data.sh

# 6. 启动系统
bash start.sh

# 7. 打开浏览器访问
# http://localhost:3000
```

---

## 📊 验证系统运行

### 检查后端
```bash
curl http://localhost:8000/health
# 应该返回: {"status":"healthy"}
```

### 检查数据
```bash
curl http://localhost:8000/api/statistics/dashboard
# 应该返回JSON格式的统计数据
```

### 检查前端
在浏览器访问：http://localhost:3000
- 应该看到"采购管理系统"页面
- 可以看到数据总览、订单列表等

---

## 🔄 日常使用

### 每次启动系统
```bash
cd Procurement-Management-System
bash start.sh
```

### 停止系统
```bash
# 按 Ctrl+C 停止当前运行的服务

# 或者找到进程ID并终止
ps aux | grep "python.*run.py"
ps aux | grep "vite"
kill <PID>
```

### 备份数据
```bash
# 备份数据库文件
cp data/procurement.db data/procurement.db.backup.$(date +%Y%m%d)
```

### 重新导入数据
```bash
# 会提示是否清空现有数据
bash import_data.sh
```

---

## 📁 项目文件说明

```
Procurement-Management-System/
├── api/                    # 后端代码
│   ├── app/               # 应用代码
│   ├── requirements.txt   # Python依赖
│   ├── run.py            # 启动文件
│   └── migrate_data.py   # 数据导入脚本
├── web/                   # 前端代码
│   ├── src/              # 源代码
│   ├── package.json      # 前端依赖
│   └── vite.config.ts    # 构建配置
├── data/                  # 数据目录（自动创建）
│   └── procurement.db    # 数据库文件
├── import_data.sh        # 数据导入脚本 ⭐
├── start.sh              # 系统启动脚本 ⭐
├── README.md             # 项目说明
├── DATA_IMPORT.md        # 数据导入详细说明
└── README_LOCAL.md       # 本地使用指南（本文件）⭐
```

---

## 🆘 获取帮助

1. **查看日志**
   ```bash
   # 后端日志
   tail -f data/api.log

   # 前端日志
   tail -f data/web.log
   ```

2. **检查进程**
   ```bash
   ps aux | grep python
   ps aux | grep vite
   ```

3. **重置环境**
   ```bash
   # 删除所有数据
   rm -rf data/
   rm -rf web/node_modules/

   # 重新开始
   bash import_data.sh
   bash start.sh
   ```

---

## ✨ 享受使用！

现在您可以在本地环境中完全独立运行采购管理系统了！

所有数据都保存在您的本地计算机上，完全私密安全。
