import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import re
import logging

try:
    from database import get_db
    from deps import require_admin
    from models.models import User, RoleEnum
    from schemas.schemas import StudentLogin, StudentVerify, ElderlyLogin, UserResponse, ElderlyInitResponse
    from utils.redis_client import get_redis, RedisKey
    from utils.jwt import create_access_token
    from utils.helpers import get_salted_hash, generate_random_code
    from config import settings
except ImportError:
    from ..database import get_db
    from ..deps import require_admin
    from ..models.models import User, RoleEnum
    from ..schemas.schemas import StudentLogin, StudentVerify, ElderlyLogin, UserResponse, ElderlyInitResponse
    from ..utils.redis_client import get_redis, RedisKey
    from ..utils.jwt import create_access_token
    from ..utils.helpers import get_salted_hash, generate_random_code
    from ..config import settings

logger = logging.getLogger("kuaibang")
router = APIRouter(prefix="/auth", tags=["Authentication"])

async def check_brute_force(redis, action: str, identifier: str, max_attempts: int = 5, window_sec: int = 600):
    """防爆破拦截器：比如 10分钟内最多错 5 次"""
    key = RedisKey.rate_limit(identifier, action)
    attempts = await redis.get(key)
    if attempts and int(attempts) >= max_attempts:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS, 
            detail="尝试次数过多，请稍后再试"
        )

async def record_failed_attempt(redis, action: str, identifier: str, window_sec: int = 600):
    key = RedisKey.rate_limit(identifier, action)
    await redis.incr(key)
    await redis.expire(key, window_sec)

async def clear_failed_attempt(redis, action: str, identifier: str):
    key = RedisKey.rate_limit(identifier, action)
    await redis.delete(key)

@router.post("/elderly/init", response_model=ElderlyInitResponse, summary="初始化老人账号(由社区调用)")
async def init_elderly(db: AsyncSession = Depends(get_db), _: bool = Depends(require_admin)):
    """生成一个老人账号，产生一次性随机登录码，用后作废。需要 Admin 权限"""
    plaintext_code = generate_random_code(8, numeric_only=False)
    code_hash = get_salted_hash(plaintext_code)

    hash_id = get_salted_hash(uuid.uuid4().hex)[:10]

    user = User(
        role=RoleEnum.elderly,
        hash_id=hash_id,
        verification_code_hash=code_hash
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    logger.info(f"创建老人账号 {user.id}", extra={"user_id": str(user.id), "hash_id": hash_id})

    return {
        "id": user.id,
        "hash_id": user.hash_id,
        "plaintext_code": plaintext_code
    }

@router.post("/student/login", summary="学生请求发送验证码")
async def student_login_request(data: StudentLogin):
    email = data.email.strip().lower()
    if not re.match(r"^[a-zA-Z0-9_.+-]+@mails\.tsinghua\.edu\.cn$", email):
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="必须使用清华大学邮箱 (@mails.tsinghua.edu.cn)")

    redis = await get_redis()

    # 防止乱发验证码
    await check_brute_force(redis, "send_email", email, max_attempts=5, window_sec=600)

    key = RedisKey.student_code(email)

    # Check if already sent recently
    ttl = await redis.ttl(key)
    if ttl > 0 and ttl > 240: # If remaining time > 4 mins (sent within 1 min)
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="验证码发送太频繁，请稍后再试")

    code = generate_random_code(6, numeric_only=True)
    await redis.setex(key, 300, code) # 5 minutes expiry
    await record_failed_attempt(redis, "send_email", email) # 记录发送次数

    if settings.debug:
        logger.info(f"[DEBUG] 验证码发送给 {email}: {code}", extra={"email": email})
        # In real app, call SMTP service here
    else:
        logger.info(f"验证码已发送至邮箱 {email}", extra={"email": email})

    return {"message": "验证码已发送至邮箱，有效时间5分钟", "debug_code": code if settings.debug else None}


@router.post("/student/verify", summary="学生验证登录")
async def student_verify(request: Request, data: StudentVerify, db: AsyncSession = Depends(get_db)):
    email = data.email.strip().lower()
    code = data.code.strip()
    client_ip = request.client.host if request.client else "unknown"

    redis = await get_redis()
    await check_brute_force(redis, "student_verify", client_ip, max_attempts=5, window_sec=300)

    key = RedisKey.student_code(email)
    saved_code = await redis.get(key)

    if not saved_code or saved_code != code:
        await record_failed_attempt(redis, "student_verify", client_ip)
        logger.warning(f"学生验证码错误: {email} from {client_ip}", extra={"email": email, "ip": client_ip})
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="验证码错误或已过期")

    await clear_failed_attempt(redis, "student_verify", client_ip)

    # Email is valid, find or create user
    email_hash = get_salted_hash(email)

    query = select(User).where(User.edu_email_hash == email_hash, User.role == RoleEnum.student)
    result = await db.execute(query)
    user = result.scalars().first()

    if not user:
        user = User(
            role=RoleEnum.student,
            edu_email_hash=email_hash,
            hash_id=email_hash[:10]  # Simplified hash id string for student
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        logger.info(f"创建学生账号 {user.id}", extra={"user_id": str(user.id), "email": email})

    await redis.delete(key) # consume the code

    token = create_access_token({"sub": str(user.id), "role": user.role.value})
    logger.info(f"学生 {user.id} 登录成功", extra={"user_id": str(user.id)})
    return {"access_token": token, "token_type": "bearer", "user": {"id": user.id, "role": user.role}}


@router.post("/elderly/login", summary="老人使用一次性验证码登录")
async def elderly_login(request: Request, data: ElderlyLogin, db: AsyncSession = Depends(get_db)):
    code = data.code.strip().upper()
    client_ip = request.client.host if request.client else "unknown"

    if not code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="验证码不能为空")

    redis = await get_redis()
    await check_brute_force(redis, "elderly_login", client_ip, max_attempts=5, window_sec=300)

    code_hash = get_salted_hash(code)
    query = select(User).where(User.verification_code_hash == code_hash, User.role == RoleEnum.elderly)
    result = await db.execute(query)
    user = result.scalars().first()

    if not user:
        await record_failed_attempt(redis, "elderly_login", client_ip)
        logger.warning(f"老人验证码错误 from {client_ip}", extra={"ip": client_ip})
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="验证码无效或已使用过")

    await clear_failed_attempt(redis, "elderly_login", client_ip)

    # 用后即焚
    user.verification_code_hash = None
    await db.commit()

    token = create_access_token({"sub": str(user.id), "role": user.role.value}, long_term=True)
    logger.info(f"老人 {user.id} 登录成功", extra={"user_id": str(user.id)})
    return {"access_token": token, "token_type": "bearer", "expires_in_days": settings.long_term_token_expire_days, "user": {"id": user.id, "role": user.role}}
