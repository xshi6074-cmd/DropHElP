import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, Enum, ForeignKey, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class RoleEnum(str, enum.Enum):
    elderly = "elderly"
    student = "student"

class TaskTypeEnum(str, enum.Enum):
    buy_medicine = "代买药品/生活用品"
    phone_guide = "手机操作指导"
    heavy_lifting = "重物搬运"
    other = "其他"

class TaskStatusEnum(str, enum.Enum):
    waiting_accept = "waiting_accept"
    accepted = "accepted"
    in_progress = "in_progress"
    completed = "completed"
    abnormal_ended = "abnormal_ended"

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role = Column(Enum(RoleEnum), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # 信用追踪(所有角色共用)
    hash_id = Column(String, unique=True, index=True, nullable=True) 
    
    # 学生特有字段
    edu_email_hash = Column(String, unique=True, index=True, nullable=True)
    monthly_stats = Column(JSON, default={"completed": 0, "abnormal": 0, "no_show": 0})
    is_frozen = Column(Boolean, default=False)
    cooldown_until = Column(DateTime, nullable=True)
    
    # 老人特有字段 (复杂的验证码哈希)
    verification_code_hash = Column(String, unique=True, index=True, nullable=True)

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = Column(Enum(TaskTypeEnum), nullable=False)
    urgency = Column(String, default="normal") # normal, urgent
    location_fuzzy = Column(String, nullable=False)
    
    elder_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    status = Column(Enum(TaskStatusEnum), default=TaskStatusEnum.waiting_accept, index=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime, nullable=True)
    
    accepted_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    accepted_at = Column(DateTime, nullable=True)
    
    # 双方确认结束机制
    elder_confirmed = Column(Boolean, default=False)
    student_confirmed = Column(Boolean, default=False)
    
    # 线下对接校验码的哈希值
    meet_code_hash = Column(String, nullable=False)
    verification_code_used = Column(String(6), nullable=True)

class TaskLog(Base):
    __tablename__ = "task_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=False)
    action = Column(String, nullable=False) # e.g., 'created', 'accepted', 'completed', 'abnormal'
    actor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    metadata_ = Column("metadata", JSON, nullable=True) # 避免和SQLAlchemy保留字冲突

class AbnormalFlag(Base):
    __tablename__ = "abnormal_flags"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=False)
    flagger_role = Column(Enum(RoleEnum), nullable=False)
    reason_text = Column(String, nullable=True)
    flagged_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class BlindBox(Base):
    # 依据需求，MVP仅建表
    __tablename__ = "blind_boxes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = Column(String, nullable=False)
    content_ref = Column(String, nullable=False)
    rarity = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))