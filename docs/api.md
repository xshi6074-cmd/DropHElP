# API接口文档

## 基础信息

- **Base URL**: `http://localhost:8000`
- **文档地址**: `http://localhost:8000/docs`
- **认证方式**: Bearer Token

## 响应格式

```json
{
  "code": 0,           // 0成功，非0错误码
  "data": {},          // 业务数据
  "message": "success", // 消息
  "requestId": "abc123" // 请求ID
}
```

## 认证相关

### 学生 - 发送验证码
```http
POST /auth/student/login
Content-Type: application/json

{
  "email": "xxx@edu.cn"
}
```

### 学生 - 验证登录
```http
POST /auth/student/verify
Content-Type: application/json

{
  "email": "xxx@edu.cn",
  "code": "AB1234"
}
```

**响应:**
```json
{
  "code": 0,
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "role": "student",
    "stats": {
      "completed_count": 5
    }
  }
}
```

### 老人 - 验证码登录
```http
POST /auth/elderly/login
Content-Type: application/json

{
  "phone": "13800138000"
}
```

```http
POST /auth/elderly/verify
Content-Type: application/json

{
  "phone": "13800138000",
  "code": "123456"
}
```

## 任务相关

### 获取任务类型
```http
GET /tasks/types
Authorization: Bearer {token}
```

**响应:**
```json
{
  "code": 0,
  "data": [
    {"id": "shopping", "name": "代买物品", "icon": "cart"},
    {"id": "accompany", "name": "陪同就医", "icon": "hospital"},
    {"id": "tech_help", "name": "手机/APP教学", "icon": "phone"}
  ]
}
```

### 发布任务
```http
POST /tasks
Authorization: Bearer {token}
Content-Type: application/json

{
  "type": "shopping",
  "description": "需要买一盒降压药",
  "location_text": "XX小区东门"
}
```

### 接单
```http
POST /tasks/accept
Authorization: Bearer {token}
Content-Type: application/json

{
  "task_id": 123
}
```

### 完成任务（验证码）
```http
POST /tasks/verify
Authorization: Bearer {token}
Content-Type: application/json

{
  "task_id": 123,
  "code": "654321"
}
```

### 标记异常
```http
POST /tasks/abnormal
Authorization: Bearer {token}
Content-Type: application/json

{
  "task_id": 123,
  "reason": "老人未出现"
}
```

## 个人中心

### 获取进行中的任务
```http
GET /me/tasks
Authorization: Bearer {token}
```

### 获取统计信息
```http
GET /me/stats
Authorization: Bearer {token}
```

## 错误码

| 错误码 | 说明 |
|--------|------|
| 0 | 成功 |
| 1000 | 未知错误 |
| 1001 | 参数验证失败 |
| 2000 | 认证失败 |
| 2001 | Token过期 |
| 2002 | Token无效 |
| 2003 | 验证码过期 |
| 2004 | 验证码错误 |
| 2005 | 请求过于频繁 |
| 3000 | 任务不存在 |
| 3001 | 任务已被接 |
| 3002 | 任务已过期 |
| 3003 | 已有进行中的任务 |
