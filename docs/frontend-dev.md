# 快帮前端开发总结

## 安装依赖

```bash
cd kuaibang/frontend
npm install
```

或使用国内镜像加速：
```bash
npm install --registry=https://registry.npmmirror.com
```

## 启动开发服务器

```bash
npm run dev
```

访问：
- 老人端：`http://localhost:5173/elderly/login`
- 学生端：`http://localhost:5173/student/login`

## 设计系统

### 老人端（温暖导向）

**设计理念**：降低认知负担，增强行动信心

| 元素 | 规格 |
|------|------|
| 主色 | 微信绿 `#07C160` |
| 背景 | 米黄 `#FFFDF5` |
| 文字 | 深灰 `#2D2D2D`，最小 18px |
| 按钮 | 大圆角（16-20px），高 56px |
| 引导 | "点这里" 等口语化提示 |

**关键交互**：
- 大按钮 + 明确文字标签
- 验证码超大字体显示（48px）
- 每步都有确认和提示

### 学生端（Linear极简）

**设计理念**：高效、专业、有质感

| 元素 | 规格 |
|------|------|
| 主色 | 靛蓝 `#6366F1` |
| 背景 | 米白 `#FAFAF8` |
| 圆角 | 适中（10-12px） |
| 动效 | 弹簧曲线 cubic-bezier(0.16, 1, 0.3, 1) |

**动效规范**：
- 入场：从下方滑入 20px，opacity 0→1，300ms
- 按钮：hover scale 1.02，active scale 0.98
- 卡片：hover translateY(-2px) + 阴影加深

## 页面清单

### 老人端
| 路由 | 页面 | 功能 |
|------|------|------|
| `/elderly/login` | 登录 | 8位验证码输入 |
| `/elderly/tasks` | 任务列表 | 查看当前任务、验证码展示 |
| `/elderly/create` | 发布任务 | 选择类型、填写位置描述 |

### 学生端
| 路由 | 页面 | 功能 |
|------|------|------|
| `/student/login` | 登录 | 教育邮箱 + 6位验证码 |
| `/student` | 首页 | 统计、快捷入口 |
| `/student/hall` | 任务大厅 | 浏览待接任务 |
| `/student/task` | 当前任务 | 验证码输入、异常标记 |
| `/student/profile` | 个人中心 | 统计、菜单、退出 |

## 组件规范

### 老人端按钮
```vue
<button class="elderly-btn">
  <span class="text-elderly-base opacity-90">点这里</span>
  <span class="ml-1">发布任务</span>
</button>
```

### 学生端卡片
```vue
<div class="student-card">
  <!-- 内容 -->
</div>
```

### 验证码输入（学生端）
```vue
<div class="flex gap-1.5">
  <input v-for="n in 6" class="w-10 h-12 text-center rounded-lg border-2" />
</div>
```

## API 集成

所有 API 调用通过 `src/api/client.js`：

```javascript
import client from './api/client.js'

// GET
const data = await client.get('/tasks/me')

// POST
await client.post('/tasks/accept', { task_id: id })
```

## 状态管理

使用 Vue 3 Composition API + 本地存储：

```javascript
// 登录状态
localStorage.setItem('token', res.access_token)
localStorage.setItem('role', 'student')

// 读取
const token = localStorage.getItem('token')
```

## 响应式设计

Tailwind 断点：
- 移动端优先设计
- 容器最大宽度 `max-w-lg`（512px）
- 安全区域适配（iOS notch）

## 下一步

1. 安装依赖
2. 启动后端（确保 API 可用）
3. 启动前端
4. 测试完整流程
