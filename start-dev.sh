#!/bin/bash
# 快帮 (Kuaibang) - 开发环境启动脚本 (Linux/Mac)

set -e

echo "========================================"
echo "  快帮 (Kuaibang) - 开发环境启动脚本"
echo "========================================"
echo

# 检查Docker
if ! command -v docker &> /dev/null; then
    echo "[错误] Docker未安装，请先安装Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "[错误] Docker Compose未安装"
    exit 1
fi

echo "[1/4] 启动 PostgreSQL 和 Redis..."
docker-compose up -d postgres redis
if [ $? -ne 0 ]; then
    echo "[错误] 启动数据库失败"
    exit 1
fi
echo "[✓] 数据库容器已启动"

echo
echo "[2/4] 等待数据库就绪..."
until docker exec kuaibang-db pg_isready -U postgres > /dev/null 2>&1; do
    echo "    等待数据库..."
    sleep 2
done
echo "[✓] PostgreSQL 已就绪"

echo
echo "[3/4] 初始化数据库表..."
cd backend
python -c "import sys; sys.path.insert(0, 'src'); from scripts.init_db import init_database; import asyncio; asyncio.run(init_database())"
cd ..
echo "[✓] 数据库初始化完成"

echo
echo "[4/4] 启动后端服务..."
cd backend
echo "启动FastAPI服务..."
python -m uvicorn src.main:app --reload &
UVICORN_PID=$!
cd ..

echo
echo "========================================"
echo "  服务启动完成！"
echo "========================================"
echo
echo "后端API: http://localhost:8000"
echo "API文档: http://localhost:8000/docs"
echo "健康检查: http://localhost:8000/health"
echo
echo "数据库连接:"
echo "  PostgreSQL: localhost:5432 (postgres/postgres)"
echo "  Redis:      localhost:6379"
echo
echo "按 Ctrl+C 停止服务"
wait $UVICORN_PID
