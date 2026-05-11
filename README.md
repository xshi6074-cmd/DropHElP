# DropHelp - 社区互助平台

DropHelp（快帮）是一个连接社区长者与青年志愿者的高效互助平台。长者可以发布日常协助需求（如陪伴就医、代购物品、电子设备使用指导等），学生志愿者通过平台接单提供上门服务。

## MVP 预期功能

### 长者端
- **简单登录**: 使用短信/邮件验证码快速登录
- **发布需求**: 选择服务类型（就医陪同、代买代办、设备指导等），填写时间与地点
- **查看任务**: 实时追踪任务状态，与服务者安全确认

### 志愿者端
- **教育邮箱认证**: 使用校园邮箱注册，确保志愿者身份真实
- **浏览任务大厅**: 按距离/时间筛选附近需求
- **接单服务**: 一键接单，验证码确认服务完成
- **个人中心**: 查看服务记录与统计数据

### 核心机制
- **双向确认**: 服务完成后双方验证码确认，保障权益
- **状态流转**: 发布 → 待接单 → 服务中 → 待确认 → 完成

## 设计说明

### 双端差异化设计

| 维度 | 长者端 | 志愿者端 |
|------|--------|----------|
| **设计目标** | 降低认知负担，增强行动信心 | 高效、专业、有质感 |
| **主色调** | 微信绿 `#07C160` | 靛蓝 `#6366F1` |
| **背景色** | 米黄 `#FFFDF5` | 米白 `#FAFAF8` |
| **字体** | 最小 18px，清晰易读 | 适中 14-16px，现代简洁 |
| **按钮** | 大圆角（16-20px），高 56px，口语化标签（"点这里"） | 适中圆角（10-12px），hover 动效 |
| **交互** | 每步确认，大字体验证码（48px） | 流畅动画，弹簧曲线过渡 |

### 设计原则
- **长者端**: 大触控区域、高对比度、明确指引、减少输入
- **志愿者端**: 信息密度高、操作快捷、视觉反馈及时

## 技术架构

### 项目结构

```
kuaibang/
├── backend/              # FastAPI 后端
│   ├── src/
│   │   ├── main.py       # 入口
│   │   ├── config.py     # 配置
│   │   ├── database.py   # 数据库连接
│   │   ├── routers/      # API 路由
│   │   ├── models/       # ORM 模型
│   │   ├── schemas/      # Pydantic 模型
│   │   └── utils/        # 工具函数
│   └── requirements.txt
├── frontend/             # Vue 3 + TailwindCSS 前端
│   ├── src/
│   │   ├── views/
│   │   │   ├── elderly/  # 长者端页面
│   │   │   └── student/  # 志愿者端页面
│   │   ├── api/          # API 客户端
│   │   └── router/       # 路由配置
│   └── package.json
├── docker-compose.yml    # 开发环境
├── docker-compose.prod.yml # 生产环境
└── DEPLOY.md             # 部署指南
```

### 技术栈

- **后端**: Python 3.12 + FastAPI + SQLAlchemy 2.0 + PostgreSQL + Redis
- **前端**: Vue 3 + Vite + TailwindCSS + VueUse Motion
- **部署**: Docker Compose + Nginx

### 安全特性

- JWT 认证（长者长期会话 / 志愿者短期会话）
- 接口限流防爆破
- 幂等性保护（防止重复提交）
- 验证码时效控制

## 快速启动

### 环境要求

- Python 3.12+
- Docker Desktop
- Node.js 18+ (前端开发)

### 开发环境启动

Windows:
```bash
cd kuaibang
start-dev.bat
```

Linux/Mac:
```bash
cd kuaibang
./start-dev.sh
```

服务启动后访问：
- API 文档: http://localhost:8000/docs
- 长者端: http://localhost:5173/elderly/login
- 志愿者端: http://localhost:5173/student/login

## 部署说明

详见 [DEPLOY.md](DEPLOY.md)

### 生产环境注意

1. 修改 `backend/.env` 中的 `SECRET_KEY`（至少 32 字符）
2. 设置 `DEBUG=false`
3. 配置 SSL 证书
4. 配置 SMTP 邮件服务

## 文档索引

- [部署指南](DEPLOY.md)
- [API 文档](docs/api.md)
- [数据流程](docs/data-flow.md)

## 许可

MIT License
