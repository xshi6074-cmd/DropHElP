import random
import hashlib
from datetime import datetime, timezone, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
import logging

try:
    from database import get_db
    from models.models import User, Task, TaskLog, AbnormalFlag, TaskStatusEnum, TaskTypeEnum, RoleEnum
    from schemas.schemas import TaskCreate, TaskResponse, TaskCompleteVerify, AbnormalReport, TaskElderlyResponse, TaskStudentResponse, TaskAcceptRequest
    from utils.helpers import get_salted_hash, generate_random_code
    from utils.idempotency import require_idempotency
    from utils.redis_client import get_redis, RedisKey
    from deps import get_current_user, get_current_student, get_current_elderly, require_admin
except ImportError:
    from ..database import get_db
    from ..models.models import User, Task, TaskLog, AbnormalFlag, TaskStatusEnum, TaskTypeEnum, RoleEnum
    from ..schemas.schemas import TaskCreate, TaskResponse, TaskCompleteVerify, AbnormalReport, TaskElderlyResponse, TaskStudentResponse, TaskAcceptRequest
    from ..utils.helpers import get_salted_hash, generate_random_code
    from ..utils.idempotency import require_idempotency
    from ..utils.redis_client import get_redis, RedisKey
    from ..deps import get_current_user, get_current_student, get_current_elderly, require_admin

logger = logging.getLogger("kuaibang")
router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.get("/me", summary="查询我的当前任务")
async def get_my_tasks(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    if user.role == RoleEnum.elderly:
        query = select(Task).where(
            Task.elder_id == user.id,
            Task.status.in_([TaskStatusEnum.waiting_accept, TaskStatusEnum.accepted, TaskStatusEnum.in_progress])
        )
        task = (await db.execute(query)).scalars().first()
        if not task:
            return None
        return task

    elif user.role == RoleEnum.student:
        query = select(Task).where(
            Task.accepted_by == user.id,
            Task.status.in_([TaskStatusEnum.accepted, TaskStatusEnum.in_progress])
        )
        task = (await db.execute(query)).scalars().first()
        if not task:
            return None
        return TaskStudentResponse.model_validate(task)

@router.get("/types", summary="获取任务类型枚举")
async def get_task_types():
    return [{"value": t.name, "label": t.value} for t in TaskTypeEnum]

@router.post("", response_model=TaskElderlyResponse, summary="老人发布任务")
async def create_task(
    data: TaskCreate,
    idempotency_key: str = Header(None, alias="X-Idempotency-Key"),
    db: AsyncSession = Depends(get_db),
    elder: User = Depends(get_current_elderly)
):
    # 幂等性检查
    if idempotency_key:
        await require_idempotency(idempotency_key, "create_task")

    logger.info(f"老人 {elder.id} 尝试发布任务", extra={"elder_id": str(elder.id), "task_type": data.type.value})

    # 检查是否已有同类型的未完成任务（防止误触多发）
    query = select(Task).where(
        Task.elder_id == elder.id,
        Task.status.in_([TaskStatusEnum.waiting_accept, TaskStatusEnum.accepted, TaskStatusEnum.in_progress])
    )
    result = await db.execute(query)
    if result.scalars().first():
        logger.warning(f"老人 {elder.id} 已有进行中任务，拒绝重复发布")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="您当前已有进行中的任务，请完成后再发布新的任务。"
        )

    plaintext_meet_code = generate_random_code(6, numeric_only=True)
    task = Task(
        type=data.type,
        urgency=data.urgency,
        location_fuzzy=data.location_fuzzy,
        elder_id=elder.id,
        meet_code_hash=get_salted_hash(plaintext_meet_code)
    )
    db.add(task)
    await db.flush() # flush to get task.id

    # 记录日志
    log = TaskLog(
        task_id=task.id,
        action="created",
        actor_id=elder.id
    )
    db.add(log)

    await db.commit()
    await db.refresh(task)

    logger.info(f"任务 {task.id} 创建成功", extra={"task_id": str(task.id), "elder_id": str(elder.id)})

    resp = TaskElderlyResponse.model_validate(task)
    resp.meet_code = plaintext_meet_code
    return resp

from ..utils.redis_client import get_redis, RedisKey

@router.post("/accept", response_model=TaskStudentResponse, summary="学生随机接单")
async def accept_task(
    data: TaskAcceptRequest,
    idempotency_key: str = Header(None, alias="X-Idempotency-Key"),
    db: AsyncSession = Depends(get_db),
    student: User = Depends(get_current_student)
):
    # 幂等性检查
    if idempotency_key:
        await require_idempotency(idempotency_key, "accept_task")

    logger.info(f"学生 {student.id} 尝试接单", extra={"student_id": str(student.id)})

    if student.is_frozen:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="您的账号已被冻结，无法接单")

    if student.cooldown_until and student.cooldown_until > datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="您处于冷却期，暂不能接单")

    # 检查学生是否已有正在进行的任务（限制单线）
    current_task_q = select(Task).where(
        Task.accepted_by == student.id,
        Task.status.in_([TaskStatusEnum.accepted, TaskStatusEnum.in_progress])
    )
    if (await db.execute(current_task_q)).scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="您当前已有正在进行中的订单，请先完成或作异常处理。"
        )

    # 随机捞取一个待接单的任务, 加入 with_for_update 解决并发抢单
    query = select(Task).where(
        Task.status == TaskStatusEnum.waiting_accept
    )
    if data.types:
        query = query.where(Task.type.in_(data.types))
    if data.location_fuzzy:
        # 使用参数化查询防止SQL注入
        query = query.where(Task.location_fuzzy.ilike(f"%{data.location_fuzzy}%"))

    query = query.order_by(func.random()).limit(1).with_for_update(skip_locked=True)

    result = await db.execute(query)
    task = result.scalars().first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="当前区域暂无符合条件的待接受请求，请稍后刷新重试。"
        )

    task.status = TaskStatusEnum.accepted
    task.accepted_by = student.id
    task.accepted_at = datetime.now(timezone.utc)

    log = TaskLog(
        task_id=task.id,
        action="accepted",
        actor_id=student.id
    )
    db.add(log)
    await db.commit()
    await db.refresh(task)

    # 设置Redis超时监控（3小时）
    redis = await get_redis()
    timeout_key = RedisKey.task_timeout(str(task.id))
    await redis.setex(timeout_key, 10800, str(student.id))  # 3小时 = 10800秒

    logger.info(f"学生 {student.id} 接单成功，任务 {task.id}",
                extra={"task_id": str(task.id), "student_id": str(student.id)})

    return task

@router.post("/verify", summary="学生输入对接码完成任务")
async def verify_task(
    data: TaskCompleteVerify,
    idempotency_key: str = Header(None, alias="X-Idempotency-Key"),
    db: AsyncSession = Depends(get_db),
    student: User = Depends(get_current_student)
):
    # 幂等性检查
    if idempotency_key:
        await require_idempotency(idempotency_key, f"verify_task:{data.task_id}")

    query = select(Task).where(Task.id == data.task_id)
    result = await db.execute(query)
    task = result.scalars().first()

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="任务不存在")

    if task.accepted_by != student.id or task.status != TaskStatusEnum.accepted:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权操作或任务状态错误")

    if task.meet_code_hash != get_salted_hash(data.verification_code):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="对接码验证失败")

    # 输入验证码后，任务正式进入进行中状态
    task.status = TaskStatusEnum.in_progress
    task.verification_code_used = data.verification_code

    log = TaskLog(
        task_id=task.id,
        action="in_progress",
        actor_id=student.id
    )
    db.add(log)

    await db.commit()

    # 清除Redis超时监控（任务已进入下一阶段）
    redis = await get_redis()
    timeout_key = RedisKey.task_timeout(str(task.id))
    await redis.delete(timeout_key)

    logger.info(f"学生 {student.id} 验证任务 {task.id} 成功，进入进行中状态",
                extra={"task_id": str(task.id), "student_id": str(student.id)})

    return {"message": "校验码验证通过，任务正式开始！"}

@router.post("/{task_id}/confirm", summary="双方确认完成任务")
async def confirm_task(
    task_id: UUID,
    idempotency_key: str = Header(None, alias="X-Idempotency-Key"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    # 幂等性检查
    if idempotency_key:
        await require_idempotency(idempotency_key, f"confirm_task:{task_id}")

    query = select(Task).where(Task.id == task_id)
    result = await db.execute(query)
    task = result.scalars().first()

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="任务不存在")

    if task.status != TaskStatusEnum.in_progress:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="任务不在进行中状态，无法确认完成")

    # 记录该用户的确认
    if user.role == RoleEnum.elderly and task.elder_id == user.id:
        task.elder_confirmed = True
        logger.info(f"老人 {user.id} 确认任务 {task_id} 完成", extra={"task_id": str(task_id), "elder_id": str(user.id)})
    elif user.role == RoleEnum.student and task.accepted_by == user.id:
        task.student_confirmed = True
        logger.info(f"学生 {user.id} 确认任务 {task_id} 完成", extra={"task_id": str(task_id), "student_id": str(user.id)})
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权操作此任务")

    log = TaskLog(
        task_id=task.id,
        action=f"{user.role.value}_confirmed",
        actor_id=user.id
    )
    db.add(log)

    # 如果双方都确认，真正完结该单
    if task.elder_confirmed and task.student_confirmed:
        task.status = TaskStatusEnum.completed

        complete_log = TaskLog(
            task_id=task.id,
            action="completed",
            actor_id=user.id # 最后一个点击确认的人
        )
        db.add(complete_log)

        # 为学生增加完成结算
        student_query = select(User).where(User.id == task.accepted_by)
        student = (await db.execute(student_query)).scalars().first()
        if student:
            stats = student.monthly_stats or {"completed": 0, "abnormal": 0, "no_show": 0}
            stats["completed"] = stats.get("completed", 0) + 1
            student.monthly_stats = dict(stats)

        logger.info(f"任务 {task_id} 双方确认完成", extra={"task_id": str(task_id)})

    await db.commit()
    return {"message": "确认成功", "status": task.status}

@router.post("/abnormal", summary="异常标志中断")
async def report_abnormal(
    data: AbnormalReport,
    idempotency_key: str = Header(None, alias="X-Idempotency-Key"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    # 幂等性检查
    if idempotency_key:
        await require_idempotency(idempotency_key, f"abnormal:{data.task_id}")

    query = select(Task).where(Task.id == data.task_id)
    result = await db.execute(query)
    task = result.scalars().first()

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="任务不存在")

    if task.status not in [TaskStatusEnum.waiting_accept, TaskStatusEnum.accepted, TaskStatusEnum.in_progress]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="当前任务状态无法标记异常")

    # 鉴权：只有发布的老人、或者接单的学生可以中断
    is_owner = (user.role == RoleEnum.elderly and task.elder_id == user.id)
    is_worker = (user.role == RoleEnum.student and task.accepted_by == user.id)

    if not (is_owner or is_worker):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权操作此任务")

    # 设置异常结束(即时双方任何一方发起，均作为异常终止且不再设直接惩罚)
    task.status = TaskStatusEnum.abnormal_ended

    log = TaskLog(
        task_id=task.id,
        action="abnormal",
        actor_id=user.id,
        metadata_={"reason": data.reason}
    )
    db.add(log)

    flag = AbnormalFlag(
        task_id=task.id,
        flagger_role=user.role,
        reason_text=data.reason
    )
    db.add(flag)

    if user.role == RoleEnum.student:
        # 学生端增加异常次数统计（仅存档）
        stats = user.monthly_stats or {"completed": 0, "abnormal": 0, "no_show": 0}
        stats["abnormal"] = stats.get("abnormal", 0) + 1
        user.monthly_stats = dict(stats)

    await db.commit()

    # 清除Redis超时监控
    redis = await get_redis()
    timeout_key = RedisKey.task_timeout(str(task.id))
    await redis.delete(timeout_key)

    logger.info(f"用户 {user.id} 标记任务 {data.task_id} 异常",
                extra={"task_id": str(data.task_id), "user_id": str(user.id), "role": user.role.value})

    return {"message": "异常已记录，相关状态已关闭"}

@router.post("/maintenance/release-timeouts", summary="释放超时的任务(供Cron定时触发)")
async def release_timeout_tasks(db: AsyncSession = Depends(get_db), _: bool = Depends(require_admin)):
    """接单后3h内未输入验证码并碰面，判定为学生爽约
    同时检查Redis和数据库，防止Cron漏执行
    """
    three_hours_ago = datetime.now(timezone.utc) - timedelta(hours=3)

    # 从Redis获取已超时的任务（作为数据库查询的补充）
    redis = await get_redis()
    # 检查所有任务超时键
    timeout_pattern = "kuaibang:task:timeout:*"
    timeout_keys = await redis.keys(timeout_pattern)

    timeout_task_ids = []
    for key in timeout_keys:
        ttl = await redis.ttl(key)
        if ttl <= 0:  # 已过期或不存在
            task_id = key.replace("kuaibang:task:timeout:", "")
            timeout_task_ids.append(task_id)
            await redis.delete(key)

    # 查询数据库：3小时前接单且未验证的任务
    query = select(Task).where(
        Task.status == TaskStatusEnum.accepted,
        Task.accepted_at <= three_hours_ago
    )
    result = await db.execute(query)
    tasks = result.scalars().all()

    count = 0
    for task in tasks:
        student_id = task.accepted_by

        # 惩罚：记录爽约
        if student_id:
            student_query = select(User).where(User.id == student_id)
            student = (await db.execute(student_query)).scalars().first()
            if student:
                stats = student.monthly_stats or {"completed": 0, "abnormal": 0, "no_show": 0}
                stats["no_show"] = stats.get("no_show", 0) + 1
                student.monthly_stats = dict(stats)

                # 爽约达到3次，账户冻结
                if stats["no_show"] >= 3:
                    student.is_frozen = True
                    logger.warning(f"学生 {student_id} 爽约3次，账户已冻结",
                                   extra={"student_id": str(student_id)})

        # 释放重置任务
        task.status = TaskStatusEnum.waiting_accept
        task.accepted_by = None
        task.accepted_at = None
        count += 1

        log = TaskLog(
            task_id=task.id,
            action="no_show_released",
            actor_id=student_id if student_id else task.elder_id
        )
        db.add(log)

        # 清理Redis超时键
        await redis.delete(RedisKey.task_timeout(str(task.id)))

        logger.info(f"任务 {task.id} 因超时释放",
                    extra={"task_id": str(task.id), "student_id": str(student_id) if student_id else None})

    await db.commit()
    logger.info(f"超时任务清理完成，共释放 {count} 个任务", extra={"released_count": count})
    return {"released_count": count}
