import logging
from typing import Optional
from fastapi import HTTPException, status

try:
    from redis_client import get_redis, RedisKey
except ImportError:
    from .redis_client import get_redis, RedisKey

import logging

logger = logging.getLogger("kuaibang")

logger = logging.getLogger("kuaibang")


async def check_idempotency(key: Optional[str], action: str = "default") -> bool:
    """
    幂等性检查
    如果key已存在，返回False表示重复请求
    如果key不存在，设置key并返回True
    有效期10分钟
    """
    if not key:
        return True  # 没有提供幂等性键，跳过检查

    redis = await get_redis()
    idem_key = RedisKey.idempotency_key(f"{action}:{key}")

    # 使用SET NX（只有当key不存在时才设置）
    result = await redis.set(idem_key, "1", nx=True, ex=600)  # 10分钟过期

    if result is None:
        # Key已存在，是重复请求
        logger.warning(f"幂等性检查失败: {action} - {key[:8]}...")
        return False

    return True


async def require_idempotency(key: Optional[str], action: str = "default"):
    """
    FastAPI依赖：强制幂等性检查
    重复请求会抛出429错误
    """
    if not await check_idempotency(key, action):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="重复请求，请稍后再试"
        )
