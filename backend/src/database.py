from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import text

# 支持直接导入（用于脚本）和包导入（用于应用）
try:
    from config import settings
except ImportError:
    from .config import settings

# 延迟初始化引擎，避免导入时立即创建
_engine = None

def get_engine():
    """获取数据库引擎（延迟初始化）"""
    global _engine
    if _engine is None:
        _engine = create_async_engine(
            settings.database_url,
            echo=settings.debug,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
        )
    return _engine

# 引擎实例（向后兼容）
engine = property(get_engine)

# 异步会话工厂
def get_session_factory():
    return async_sessionmaker(
        get_engine(),
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

AsyncSessionLocal = property(get_session_factory)

Base = declarative_base()


async def get_db():
    """依赖注入用数据库会话"""
    async with get_session_factory()() as session:
        try:
            yield session
        finally:
            await session.close()


async def check_db_health():
    """健康检查"""
    try:
        async with get_session_factory()() as session:
            await session.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"[DB Health Check Failed] {e}")
        return False
