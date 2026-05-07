# 快帮 (Kuaibang) - 部署指南

## 方案对比

| 方案 | 复杂度 | 适用场景 |
|------|--------|----------|
| **A. 开发环境** (推荐) | ⭐ 低 | 本地开发、调试 |
| **B. 生产环境** | ⭐⭐⭐ 高 | 正式上线 |

---

## 方案A：开发环境（推荐）

**架构**: Docker 运行 PostgreSQL + Redis，本地 Python 运行后端

**优势**:
- 简单易懂，只需2个容器
- 后端热重载，改代码自动生效
- 调试方便，日志直接输出到控制台

### 前置要求

1. **Docker Desktop** 已安装并运行
   - Windows/Mac: [下载](https://www.docker.com/products/docker-desktop)
   - Linux: `sudo apt install docker.io docker-compose`

2. **Python 3.12+** 已安装
   - 检查: `python --version`

### 快速启动（Windows）

```bash
# 1. 进入项目目录
cd kuaibang

# 2. 双击运行启动脚本
start-dev.bat
```

脚本会自动：
1. ✅ 启动 PostgreSQL 和 Redis 容器
2. ✅ 等待数据库就绪
3. ✅ 初始化数据库表
4. ✅ 启动后端服务（带热重载）

### 快速启动（Linux/Mac）

```bash
cd kuaibang
chmod +x start-dev.sh
./start-dev.sh
```

### 手动启动（如果脚本失败）

```bash
# 1. 启动数据库
docker-compose up -d

# 2. 等待几秒，确认数据库就绪
# Windows: docker exec kuaibang-db pg_isready -U postgres
# Linux/Mac: 脚本会自动等待

# 3. 初始化数据库表
cd backend
python scripts/init_db.py

# 4. 启动后端
cd backend
python -m uvicorn src.main:app --reload
```

### 验证启动

浏览器打开: http://localhost:8000/docs

看到 Swagger UI 即表示成功！

### 常用命令

```bash
# 查看数据库日志
docker logs kuaibang-db -f

# 查看Redis日志
docker logs kuaibang-redis -f

# 重启数据库
docker-compose restart postgres redis

# 停止所有服务
docker-compose down

# 完全重置（删除所有数据）
docker-compose down -v

# 进入PostgreSQL命令行
docker exec -it kuaibang-db psql -U postgres -d kuaibang

# 进入Redis命令行
docker exec -it kuaibang-redis redis-cli
```

---

## 方案B：生产环境（全部Docker化）

**架构**: 所有服务都运行在Docker中

**适用**: 云服务器部署

### 步骤

1. **修改环境变量**

```bash
cp backend/.env.example backend/.env
# 编辑 backend/.env，修改:
# - SECRET_KEY (生产环境必须修改！)
# - DEBUG=false
```

2. **使用生产版Docker Compose**

```bash
# 使用完整版配置（包含后端和Nginx）
docker-compose -f docker-compose.prod.yml up -d
```

3. **初始化数据库**

```bash
docker exec kuaibang-api python scripts/init_db.py
```

---

## 故障排查

### 问题1: "docker: command not found"

**原因**: Docker未安装或未添加到PATH

**解决**: 安装Docker Desktop，重启终端

### 问题2: "端口被占用"

**原因**: 5432(PostgreSQL)或6379(Redis)端口已被占用

**解决**: 
```bash
# 查看占用端口的进程
netstat -ano | findstr 5432  # Windows
lsof -i :5432                # Mac/Linux

# 停止占用端口的程序，或修改docker-compose.yml中的端口映射
# 例如改为 "5433:5432"
```

### 问题3: "ModuleNotFoundError"

**原因**: Python依赖未安装

**解决**:
```bash
cd backend
pip install -r requirements.txt
```

### 问题4: "数据库连接失败"

**检查**:
1. Docker容器是否运行: `docker ps`
2. 环境变量是否正确: `cat backend/.env`
3. 数据库URL是否为: `postgresql+asyncpg://postgres:postgres@localhost:5432/kuaibang`

---

## 下一步

部署成功后，可以：
1. 访问 http://localhost:8000/docs 测试API
2. 启动前端: `cd frontend && npm install && npm run dev`
3. 联调测试认证和任务流程
