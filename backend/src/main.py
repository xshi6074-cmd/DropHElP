from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from contextlib import asynccontextmanager
import time
import uuid
import logging
import sys
import os

# 添加当前目录到路径（用于直接运行）
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from config import settings
    from database import engine, check_db_health
    from utils.redis_client import get_redis, check_redis_health, close_redis_pool
    from utils.response import api_response, api_error
except ImportError:
    from .config import settings
    from .database import engine, check_db_health
    from .utils.redis_client import get_redis, check_redis_health, close_redis_pool
    from .utils.response import api_response, api_error

# 配置结构化日志
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("kuaibang")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("=" * 50)
    logger.info(f"[{settings.app_name}] 启动中...")
    logger.info("=" * 50)

    db_ok = await check_db_health()
    redis_ok = await check_redis_health()

    if not db_ok:
        logger.error("数据库连接失败，请检查配置")
    if not redis_ok:
        logger.error("Redis连接失败，请检查配置")

    if db_ok and redis_ok:
        logger.info("所有服务连接正常")
    logger.info("=" * 50)

    yield

    # 关闭时清理
    await engine.dispose()
    await close_redis_pool()
    logger.info(f"[{settings.app_name}] 服务已关闭")


app = FastAPI(
    title=settings.app_name,
    description="助老服务平台MVP",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS配置
if settings.debug:
    # 开发环境允许localhost
    origins = ["http://localhost:5173", "http://127.0.0.1:5173"]
else:
    # 生产环境必须从环境变量读取
    origins = []  # 生产环境应在配置中明确指定
    logger.warning("生产环境CORS未配置，请设置允许的域名")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Idempotency-Key", "X-Request-ID"],
)


@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """请求日志中间件"""
    request_id = str(uuid.uuid4())[:8]
    request.state.request_id = request_id

    start_time = time.time()

    # DEBUG模式打印请求信息
    logger.debug(f"[{request_id}] {request.method} {request.url.path}")

    try:
        response = await call_next(request)
    except Exception as e:
        logger.exception(f"[{request_id}] 请求处理异常")
        raise

    process_time = (time.time() - start_time) * 1000
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Response-Time"] = f"{process_time:.2f}ms"

    logger.info(
        f"[{request_id}] {request.method} {request.url.path} - {response.status_code} - {process_time:.2f}ms"
    )

    return response


# 全局异常处理
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.warning(f"HTTP异常: {exc.status_code} - {exc.detail}")
    return api_error(
        message=exc.detail,
        code=getattr(exc, 'code', 1000),
        status_code=exc.status_code
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    logger.warning(f"参数验证失败: {errors}")
    return api_error(
        message=f"参数验证失败: {errors[0]['msg'] if errors else 'Unknown'}",
        code=1001,
        status_code=422
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.exception("未处理的异常")
    return api_error(
        message="服务器内部错误" if not settings.debug else str(exc),
        code=1000,
        status_code=500
    )


# 路由挂载
try:
    from routers import auth, tasks
except ImportError:
    from .routers import auth, tasks

app.include_router(auth.router)
app.include_router(tasks.router)


@app.get("/health")
async def health_check():
    """健康检查端点"""
    db_ok = await check_db_health()
    redis_ok = await check_redis_health()
    status_code = 200 if (db_ok and redis_ok) else 503
    return api_response(data={
        "status": "healthy" if db_ok and redis_ok else "degraded",
        "database": "ok" if db_ok else "error",
        "redis": "ok" if redis_ok else "error"
    })


@app.get("/")
async def root():
    return api_response(data={
        "name": settings.app_name,
        "version": "0.1.0",
        "docs": "/docs",
        "debug": settings.debug
    })
