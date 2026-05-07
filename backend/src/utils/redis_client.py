import redis.asyncio as redis

try:
    from config import settings
except ImportError:
    from ..config import settings

import logging

logger = logging.getLogger("kuaibang")
import logging

logger = logging.getLogger("kuaibang")

# Redis连接池（全局单例）
_redis_pool = None


async def get_redis_pool():
    """获取Redis连接池（懒加载）"""
    global _redis_pool
    if _redis_pool is None:
        _redis_pool = redis.ConnectionPool.from_url(
            settings.redis_url,
            decode_responses=True,
            max_connections=20,
            retry_on_timeout=True
        )
        logger.info("Redis连接池已创建")
    return _redis_pool


async def get_redis():
    """获取Redis连接（从连接池）"""
    pool = await get_redis_pool()
    return redis.Redis(connection_pool=pool)


async def close_redis_pool():
    """关闭Redis连接池"""
    global _redis_pool
    if _redis_pool:
        await _redis_pool.disconnect()
        _redis_pool = None
        logger.info("Redis连接池已关闭")


async def check_redis_health():
    """Redis健康检查"""
    try:
        r = await get_redis()
        await r.ping()
        return True
    except Exception as e:
        logger.error(f"Redis健康检查失败: {e}")
        return False


class RedisKey:
    """Redis Key命名规范"""

    @staticmethod
    def student_code(email: str) -> str:
        return f"kuaibang:auth:student:{email}"

    @staticmethod
    def elderly_code(phone: str) -> str:
        return f"kuaibang:auth:elderly:{phone}"

    @staticmethod
    def code_used(code: str) -> str:
        return f"kuaibang:auth:used:{code}"

    @staticmethod
    def rate_limit(ip: str, action: str) -> str:
        return f"kuaibang:ratelimit:{action}:{ip}"

    @staticmethod
    def task_lock(task_id: str) -> str:
        return f"kuaibang:task:lock:{task_id}"

    @staticmethod
    def current_task(user_id: str) -> str:
        return f"kuaibang:user:task:{user_id}"

    @staticmethod
    def task_timeout(task_id: str) -> str:
        """任务超时监控键（3小时）"""
        return f"kuaibang:task:timeout:{task_id}"

    @staticmethod
    def idempotency_key(key: str) -> str:
        """幂等性键（10分钟有效期）"""
        return f"kuaibang:idempotency:{key}"
