from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

try:
    from database import AsyncSessionLocal, get_db
    from utils.jwt import verify_token
    from utils.response import ErrorCode
    from models.models import User, RoleEnum
    from config import settings
except ImportError:
    from .database import AsyncSessionLocal, get_db
    from .utils.jwt import verify_token
    from .utils.response import ErrorCode
    from .models.models import User, RoleEnum
    from .config import settings

security = HTTPBearer(auto_error=False)
admin_header = APIKeyHeader(name="X-Admin-Token", auto_error=False)

async def require_admin(admin_token: str = Depends(admin_header)):
    if not admin_token or admin_token != settings.admin_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问，需要管理凭证"
        )
    return True

async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """获取当前登录用户并在DB中查询"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="缺少认证信息",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    payload = verify_token(token)

    if "error" in payload:
        error_code = payload["error"]
        if error_code == "token_expired":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token已过期")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token无效")
        
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的凭证格式")
        
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在")
        
    return user


async def get_current_student(user: User = Depends(get_current_user)) -> User:
    if user.role != RoleEnum.student:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权访问，需要学生权限")
    return user

async def get_current_elderly(user: User = Depends(get_current_user)) -> User:
    if user.role != RoleEnum.elderly:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权访问，需要老人权限")
    return user
