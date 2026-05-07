from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

try:
    from models.models import RoleEnum, TaskTypeEnum, TaskStatusEnum
except ImportError:
    from ..models.models import RoleEnum, TaskTypeEnum, TaskStatusEnum

class UserBase(BaseModel):
    role: RoleEnum

class UserResponse(UserBase):
    id: UUID
    hash_id: Optional[str]
    monthly_stats: Optional[Dict[str, Any]]

    model_config = ConfigDict(from_attributes=True)

class TaskCreate(BaseModel):
    type: TaskTypeEnum
    urgency: str = Field(default="normal", max_length=20)
    location_fuzzy: str = Field(..., max_length=100, min_length=2)

class TaskResponse(BaseModel):
    id: UUID
    type: TaskTypeEnum
    urgency: str
    location_fuzzy: str
    status: TaskStatusEnum
    created_at: datetime
    accepted_at: Optional[datetime] = None
    elder_confirmed: bool = False
    student_confirmed: bool = False

    model_config = ConfigDict(from_attributes=True)

class TaskElderlyResponse(TaskResponse):
    meet_code: Optional[str] = None # 只在刚创建时或老人端展示

class TaskStudentResponse(TaskResponse):
    # 排除了 elder_id 和 meet_code
    pass

class TaskAcceptRequest(BaseModel):
    types: Optional[List[TaskTypeEnum]] = None
    location_fuzzy: Optional[str] = Field(default=None, max_length=100)

# Auth Schemas
class StudentLogin(BaseModel):
    email: str = Field(..., max_length=100)

class StudentVerify(BaseModel):
    email: str = Field(..., max_length=100)
    code: str = Field(..., max_length=10)

class ElderlyLogin(BaseModel):
    code: str = Field(..., max_length=20)

class ElderlyInitResponse(BaseModel):
    id: UUID
    hash_id: str
    plaintext_code: str

# Verification Schemas
class TaskCompleteVerify(BaseModel):
    task_id: UUID
    verification_code: str = Field(..., max_length=10)

class AbnormalReport(BaseModel):
    task_id: UUID
    reason: Optional[str] = Field(default=None, max_length=500)

# 幂等性请求基类
class IdempotentRequest(BaseModel):
    idempotency_key: Optional[str] = Field(default=None, max_length=64)

