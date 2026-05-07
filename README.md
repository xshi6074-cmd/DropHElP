# 快帮 (Kuaibang) - 助老服务平台 MVP

## 快速启动（Windows）

```bash
# 1. 进入项目目录
cd kuaibang

# 2. 双击运行启动脚本
start-dev.bat
```

**会自动完成**:
- ✅ 启动 PostgreSQL 和 Redis (Docker)
- ✅ 初始化数据库表
- ✅ 启动后端服务 (Python + FastAPI)

**访问**:
- API文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health

详细部署说明: [DEPLOY.md](DEPLOY.md)

---

## 项目结构

```
kuaibang/
├── backend/              # FastAPI后端
│   ├── src/
│   │   ├── main.py      # 入口
│   │   ├── config.py    # 配置
│   │   ├── database.py  # 数据库连接
│   │   ├── deps.py      # 依赖注入
│   │   ├── routers/     # API路由
│   │   ├── models/      # ORM模型
│   │   ├── schemas/     # Pydantic模型
│   │   └── utils/       # 工具函数
│   ├── scripts/
│   │   └── init_db.py   # 数据库初始化
│   └── requirements.txt
├── frontend/             # Vue3+Tailwind前端
├── docker-compose.yml    # 开发环境 (PG+Redis)
├── docker-compose.prod.yml  # 生产环境
├── start-dev.bat         # Windows启动脚本
├── start-dev.sh          # Linux/Mac启动脚本
├── DEPLOY.md             # 详细部署指南
└── docs/
    ├── api.md            # API文档
    ├── data-flow.md      # 数据流程图
    └── backend-fix-summary.md  # 后端修复记录
```

## 核心功能

- **老人端**: 社区预生成一次性登录码，任务发布，验证码展示
- **学生端**: 教育邮箱认证，随机接单，验证码验证
- **状态机**: waiting_accept → accepted → in_progress → completed
- **安全**: JWT认证（老人90天/学生2小时），防爆破限流，幂等性保护

## 技术栈

- **后端**: Python 3.12 + FastAPI + SQLAlchemy + PostgreSQL + Redis
- **前端**: Vue 3 + Vite + TailwindCSS
- **部署**: Docker Compose

## 环境要求

- Python 3.12+
- Docker Desktop
- Node.js 18+ (前端开发)

## 开发模式特性

- FastAPI热重载 (`--reload`)
- SQL语句自动打印 (`DEBUG=true`)
- 详细错误堆栈
- 验证码控制台输出

## 生产环境注意

1. 修改 `backend/.env` 中的 `SECRET_KEY`（至少32字符）
2. 设置 `DEBUG=false`
3. 使用 `docker-compose.prod.yml`
4. 配置SSL证书

## 文档

- [部署指南](DEPLOY.md)
- [API文档](docs/api.md)
- [数据流程](docs/data-flow.md)
- [后端修复记录](docs/backend-fix-summary.md)

## 调试

```bash
# 查看数据库日志
docker logs kuaibang-db

# 进入PostgreSQL
docker exec -it kuaibang-db psql -U postgres -d kuaibang

# 进入Redis
docker exec -it kuaibang-redis redis-cli
```
