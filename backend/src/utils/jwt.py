from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone

try:
    from config import settings
except ImportError:
    from ..config import settings


def create_access_token(data: dict, expires_delta: timedelta = None, long_term: bool = False) -> str:
    """
    创建JWT Token

    Args:
        data: 要编码的数据
        expires_delta: 自定义过期时间
        long_term: 是否使用长期有效期（老人端3个月）
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    elif long_term:
        # 老人端长期Token：90天
        expire = datetime.now(timezone.utc) + timedelta(days=settings.long_term_token_expire_days)
    else:
        # 默认短期Token：2小时
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def verify_token(token: str) -> dict:
    """验证JWT Token"""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except jwt.ExpiredSignatureError:
        return {"error": "token_expired", "message": "Token已过期"}
    except JWTError as e:
        return {"error": "token_invalid", "message": f"Token无效: {str(e)}"}
