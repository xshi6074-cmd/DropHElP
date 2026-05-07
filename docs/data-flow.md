# 快帮 - 数据流通流程图

## 1. 认证流程

### 学生登录 (教育邮箱验证)
```
前端                                        后端                                    数据库/Redis
 |                                          |                                            |
 | POST /auth/student/login                 |                                            |
 | {email: "xxx@edu.cn"}                   |                                            |
 |─────────────────────────────────────────>|                                            |
 |                                          | 1. 校验邮箱格式(.edu.cn)                   |
 |                                          | 2. 防爆破检查(Redis)                       |
 |                                          | 3. 生成6位数字验证码                        |
 |                                          | 4. 存储Redis: kuaibang:auth:student:{email}|
 |                                          |    TTL=300s (5分钟)                       |
 |                                          |    发送邮件(或DEBUG打印)                   |
 |                                          |───────────────────────────────────────────>|
 |                                          |                                            |
 |                                          |<───────────────────────────────────────────|
 |  {message: "验证码已发送", debug_code?}   |                                            |
 |<─────────────────────────────────────────|                                            |
 |                                          |                                            |
 | POST /auth/student/verify                |                                            |
 | {email, code, idempotency_key?}         |                                            |
 |─────────────────────────────────────────>|                                            |
 |                                          | 1. 幂等性检查(防止重复提交)               |
 |                                          | 2. 防爆破检查(IP维度)                      |
 |                                          | 3. Redis获取验证码对比                     |
 |                                          |    ├─ 不匹配: 记录失败次数                 |
 |                                          |    └─ 匹配: 清除失败记录                   |
 |                                          | 4. DB查询或创建用户                        |
 |                                          |───────────────────────────────────────────>|
 |                                          |                                            |
 |                                          |<───────────────────────────────────────────|
 |                                          | 5. 删除Redis验证码(用后即焚)               |
 |                                          | 6. 生成JWT Token (sub=用户ID, role=student)|
 |                                          |───────────────────────────────────────────>|
 |                                          |                                            |
 |<─────────────────────────────────────────|                                            |
 |  {access_token, token_type, user}        |                                            |
```

### 老人登录 (社区预生成一次性码)
```
社区管理员                                    后端                                      数据库
     |                                       |                                         |
     | POST /auth/elderly/init               |                                         |
     | (需要Admin Token)                     |                                         |
     |──────────────────────────────────────>|                                         |
     |                                       | 1. 生成8位字母数字混合码                 |
     |                                       | 2. 生成hash_id                          |
     |                                       | 3. 创建User记录                          |
     |                                       |    role=elderly                         |
     |                                       |    verification_code_hash=验证码哈希      |
     |                                       |─────────────────────────────────────────>|
     |                                       |                                          |
     |<──────────────────────────────────────|                                          |
     | {id, hash_id, plaintext_code}        |                                          |
     |                                       |                                          |
     |======= 告知老人 plaintext_code =======|                                          |

老人                                         后端                                      数据库/Redis
 |                                          |                                          |
 | POST /auth/elderly/login                 |                                          |
 | {code: "ABC12345"}                      |                                          |
 |─────────────────────────────────────────>|                                          |
 |                                          | 1. 防爆破检查                            |
 |                                          | 2. 计算验证码哈希                        |
 |                                          | 3. DB查询匹配                            |
 |                                          |──────────────────────────────────────────>|
 |                                          |                                          |
 |                                          |<──────────────────────────────────────────|
 |                                          | 4. 验证码置NULL(用后即焚)                |
 |                                          |──────────────────────────────────────────>|
 |                                          |                                          |
 |                                          | 5. 生成JWT Token                        |
 |<─────────────────────────────────────────|                                          |
 | {access_token, user}                    |                                          |
```

---

## 2. 任务生命周期流程

### 状态机
```
[created/waiting_accept] ──老人发布──┐
                                    ▼
                           [accepted] ──学生接单──┐
                                    ▲              │
                                    │              ▼
                                    │       [in_progress] ──验证码输入──┐
                                    │              │                   │
                                    │              │                   ▼
                                    │              │              [completed]
                                    │              │           (双方确认完成)
                                    └──────────────┘
                                            │
                                            ▼
                                    [abnormal_ended]
                                    (异常中断)
```

### 发布任务
```
老人端                      后端                                           数据库
   |                         |                                              |
   | POST /tasks             |                                              |
   | {type, location_fuzzy}  |                                              |
   | X-Idempotency-Key: xxx  |                                              |
   |────────────────────────>|                                              |
   |                         | 1. 认证检查(必须elderly角色)                 |
   |                         | 2. 幂等性检查(防止重复发布)                  |
   |                         | 3. 检查是否有进行中任务                      |
   |                         |    ├─ 有: 返回错误                           |
   |                         |    └─ 无: 继续                               |
   |                         | 4. 生成6位对接验证码(数字)                   |
   |                         | 5. 计算哈希存储                              |
   |                         |─────────────────────────────────────────────>|
   |                         |                                              |
   |                         |<─────────────────────────────────────────────|
   |                         | 6. 记录TaskLog                              |
   |                         |─────────────────────────────────────────────>|
   |                         |                                              |
   |<────────────────────────|                                              |
   | {id, meet_code, ...}   |                                              |
   |                         |                                              |
   |=== 大屏显示 meet_code ==|                                              |
   |   (例如: 123456)        |                                              |
```

### 接单流程
```
学生端                      后端                                           数据库/Redis
   |                         |                                              |
   | POST /tasks/accept      |                                              |
   | {types?, location?}     |                                              |
   | X-Idempotency-Key: xxx  |                                              |
   |────────────────────────>|                                              |
   |                         | 1. 认证检查(必须student角色)                 |
   |                         | 2. 幂等性检查                               |
   |                         | 3. 检查账号状态                             |
   |                         |    ├─ is_frozen=true: 拒绝                  |
   |                         |    ├─ cooldown_until>now: 拒绝              |
   |                         |    └─ 正常: 继续                            |
   |                         | 4. 检查是否已有进行中任务                    |
   |                         |    ├─ 有: 返回错误                           |
   |                         |    └─ 无: 继续                               |
   |                         | 5. SELECT ... FOR UPDATE SKIP LOCKED        |
   |                         |    (随机取一个waiting_accept任务)            |
   |                         |─────────────────────────────────────────────>|
   |                         |                                              |
   |                         |<─────────────────────────────────────────────|
   |                         | 6. 更新状态为accepted                       |
   |                         |    设置accepted_by, accepted_at             |
   |                         |─────────────────────────────────────────────>|
   |                         |                                              |
   |                         | 7. Redis: 设置超时监控键                     |
   |                         |    kuaibang:task:timeout:{task_id}          |
   |                         |    TTL=10800s (3小时)                       |
   |                         |─────────────────────────────────────────────>|
   |                         |                                              |
   |<────────────────────────|                                              |
   | {id, status, ...}      |                                              |
```

### 验证码验证 (进入in_progress)
```
学生端                      后端                                           数据库/Redis
   |                         |                                              |
   | POST /tasks/verify      |                                              |
   | {task_id, code}         |                                              |
   | X-Idempotency-Key: xxx  |                                              |
   |────────────────────────>|                                              |
   |                         | 1. 查询任务                                  |
   |                         | 2. 校验: 是当前学生的任务?                   |
   |                         |    状态是accepted?                          |
   |                         | 3. 计算输入验证码的哈希                     |
   |                         |    对比 meet_code_hash                      |
   |                         |    ├─ 不匹配: 返回错误                       |
   |                         |    └─ 匹配: 继续                             |
   |                         | 4. 更新状态为in_progress                    |
   |                         |    记录verification_code_used               |
   |                         |─────────────────────────────────────────────>|
   |                         |                                              |
   |                         | 5. Redis: 删除超时监控键                     |
   |                         |    (任务已进入下一阶段)                     |
   |                         |─────────────────────────────────────────────>|
   |<────────────────────────|                                              |
   | {message: "任务开始"}  |                                              |
```

### 双方确认完成
```
老人端/学生端               后端                                           数据库
   |                         |                                              |
   | POST /tasks/{id}/confirm|                                              |
   | X-Idempotency-Key: xxx  |                                              |
   |────────────────────────>|                                              |
   |                         | 1. 认证检查                                  |
   |                         | 2. 查询任务                                  |
   |                         | 3. 状态检查: 必须是in_progress              |
   |                         | 4. 权限检查:                                 |
   |                         |    ├─ 老人: elder_id匹配?                   |
   |                         |    └─ 学生: accepted_by匹配?                |
   |                         | 5. 设置对应confirmed标志                    |
   |                         |    elder_confirmed=true 或                  |
   |                         |    student_confirmed=true                   |
   |                         |─────────────────────────────────────────────>|
   |                         |                                              |
   |                         | 6. 如果双方都confirmed:                     |
   |                         |    ├─ 状态改为completed                     |
   |                         |    ├─ 学生stats.completed++                 |
   |                         |    └─ 记录completed日志                     |
   |                         |─────────────────────────────────────────────>|
   |<────────────────────────|                                              |
   | {message, status}       |                                              |
```

---

## 3. 异常处理流程

### 异常标记
```
任意端                      后端                                           数据库
   |                         |                                              |
   | POST /tasks/abnormal    |                                              |
   | {task_id, reason}       |                                              |
   | X-Idempotency-Key: xxx  |                                              |
   |────────────────────────>|                                              |
   |                         | 1. 认证检查                                  |
   |                         | 2. 查询任务                                  |
   |                         | 3. 状态检查: 必须是可中断状态                |
   |                         |    (waiting_accept/accepted/in_progress)    |
   |                         | 4. 权限检查: 老人或学生本人                  |
   |                         | 5. 状态改为abnormal_ended                   |
   |                         | 6. 创建AbnormalFlag记录                     |
   |                         | 7. 记录TaskLog                              |
   |                         | 8. 学生端: stats.abnormal++                  |
   |                         |    (仅统计, 不惩罚)                         |
   |                         |─────────────────────────────────────────────>|
   |                         |                                              |
   |                         | 9. Redis: 删除超时监控键                     |
   |                         |─────────────────────────────────────────────>|
   |<────────────────────────|                                              |
   | {message}               |                                              |
```

### 超时释放 (Cron或手动触发)
```
Cron/Admin                  后端                                           数据库/Redis
   |                         |                                              |
   | POST /tasks/maintenance/|                                              |
   |   release-timeouts      |                                              |
   | (需要Admin Token)       |                                              |
   |────────────────────────>|                                              |
   |                         | 1. 查询所有accepted状态                     |
   |                         |    且 accepted_at <= 3小时前的任务           |
   |                         |─────────────────────────────────────────────>|
   |                         |                                              |
   |                         | 2. 对每个超时任务:                           |
   |                         |    ├─ 查询学生记录                           |
   |                         |    ├─ 学生stats.no_show++                   |
   |                         |    ├─ no_show>=3: is_frozen=true            |
   |                         |    ├─ 任务状态改回waiting_accept             |
   |                         |    ├─ 清除accepted_by/at                   |
   |                         |    ├─ 记录no_show_released日志             |
   |                         |    └─ Redis删除超时键                        |
   |                         |─────────────────────────────────────────────>|
   |<────────────────────────|                                              |
   | {released_count}       |                                              |
```

---

## 4. 安全机制汇总

| 层面 | 机制 | 实现 |
|------|------|------|
| **请求层** | 幂等性保护 | X-Idempotency-Key Header，Redis去重10分钟 |
| | 限流防爆破 | IP/邮箱维度，5次/5-10分钟 |
| | CORS | 开发环境限定localhost，生产环境需配置 |
| **认证层** | JWT Token | HS256算法，2小时过期 |
| | 验证码 | 学生6位数字(5分钟)，老人8位混合(一次性) |
| | 哈希存储 | 验证码/邮箱/手机号均加盐哈希存储 |
| **业务层** | 并发控制 | SELECT ... FOR UPDATE SKIP LOCKED |
| | 状态机校验 | 每个操作检查当前状态是否允许 |
| | 单线限制 | 学生同时只能接1单，老人同时只能发1单 |
| **数据层** | SQL参数化 | SQLAlchemy ORM自动转义 |
| | 敏感数据 | 邮箱/手机号脱敏显示，原始数据哈希存储 |
| **监控层** | 结构化日志 | 统一logger，含user_id/task_id等上下文 |
| | 请求追踪 | X-Request-ID全程传递 |
| | 健康检查 | /health端点检查DB+Redis连通性 |

---

## 5. 关键Redis Key设计

```
# 验证码存储
kuaibang:auth:student:{email}      -> 验证码, TTL=300s
kuaibang:auth:elderly:{phone}       -> 验证码, TTL=300s

# 防爆破计数
kuaibang:ratelimit:{action}:{ip}    -> 尝试次数, TTL=300-600s

# 幂等性
kuaibang:idempotency:{key}          -> 1, TTL=600s

# 任务超时监控
kuaibang:task:timeout:{task_id}     -> student_id, TTL=10800s

# 用户当前任务缓存(可选)
kuaibang:user:task:{user_id}        -> task_id, TTL=动态
```

---

## 6. 数据库表关系

```
users (用户)
  ├── id (PK, UUID)
  ├── role (enum: elderly/student)
  ├── hash_id (索引, 信用追踪)
  ├── edu_email_hash (学生, unique)
  ├── verification_code_hash (老人, 一次性)
  ├── monthly_stats (JSON)
  ├── is_frozen (bool)
  └── cooldown_until (datetime)

tasks (任务)
  ├── id (PK, UUID)
  ├── type (enum)
  ├── status (enum)
  ├── elder_id (FK -> users)
  ├── accepted_by (FK -> users, nullable)
  ├── meet_code_hash (对接验证码哈希)
  ├── verification_code_used (明文, 6位)
  ├── elder_confirmed (bool)
  └── student_confirmed (bool)
  └── accepted_at, created_at (datetime)

task_logs (审计日志)
  ├── id (PK, auto)
  ├── task_id (FK -> tasks)
  ├── action (enum: created/accepted/in_progress/completed/abnormal/...)
  ├── actor_id (FK -> users)
  ├── timestamp (datetime)
  └── metadata (JSON, 可选)

abnormal_flags (异常标记)
  ├── id (PK, auto)
  ├── task_id (FK -> tasks)
  ├── flagger_role (enum)
  ├── reason_text (string)
  └── flagged_at (datetime)
```
