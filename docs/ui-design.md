# 快帮 UI 设计规范

## 1. 设计语言：双轨制

### 老人端 - "温暖导向"
**核心原则**：降低认知负担，增强行动信心

| 元素 | 规范 |
|------|------|
| **主色** | 微信绿 `#07C160` - 熟悉、安全、可点击 |
| **背景** | 米黄色 `#FFFDF5` - 护眼、温暖 |
| **文字** | 深灰 `#2D2D2D` - 高对比 |
| **强调** | 暖橙 `#FF9500` - 重要提示 |
| **圆角** | 大圆角 `16px-24px` - 友好 |
| **字体** | 系统字体，最小 18px |

**引导原则**：
- 每个可交互元素都要有明确的文字标签
- 使用"点这里"、"按这个"等口语化引导
- 操作成功后大声朗读确认

### 学生端 - "Linear 极简"
**核心原则**：高效、信任、专业

| 元素 | 规范 |
|------|------|
| **主色** | 靛蓝 `#6366F1` - 现代、专业 |
| **背景** | 米白 `#FAFAF8` - 不刺眼 |
| **文字** | 墨黑 `#18181B` / 灰 `#71717A` |
| **强调** | 翠绿 `#10B981` - 成功状态 |
| **圆角** | 适中 `8px-12px` - 现代但不冰冷 |
| **动效** | Linear 风格：微弹、流畅、有质感 |

**动效规范**：
- 入场：从下方 20px 滑入，opacity 0→1，duration 300ms，ease-out
- 按钮：hover scale 1.02，active scale 0.98
- 页面切换：fade + slide，200ms

---

## 2. 页面清单

### 老人端 (Elderly)
```
/elderly/login     - 登录页（6位验证码输入）
/elderly/tasks     - 任务列表（我的任务）
/elderly/create    - 发布任务
/elderly/verify    - 验证码展示页（大字体）
```

### 学生端 (Student)
```
/student/login     - 邮箱验证码登录
/student/hall      - 任务大厅（列表）
/student/task      - 当前任务（进行中的）
/student/profile   - 个人中心（统计）
```

---

## 3. 组件设计

### 按钮

**老人端 Button**:
```
- 高度: 56px
- 圆角: 16px
- 背景: #07C160
- 文字: 白色 20px bold
- 阴影: 0 4px 12px rgba(7, 193, 96, 0.3)
- 点击反馈: scale 0.97 + 阴影加深
```

**学生端 Button**:
```
- 高度: 44px
- 圆角: 10px
- 背景: #6366F1
- 文字: 白色 15px medium
- hover: scale 1.02 + brightness 1.05
- active: scale 0.98
```

### 卡片

**老人端 Card**:
```
- 背景: 白色
- 边框: 2px solid #E8E8E8
- 圆角: 20px
- 内边距: 24px
- 阴影: 0 2px 8px rgba(0,0,0,0.06)
```

**学生端 Card**:
```
- 背景: 白色
- 边框: 1px solid #E4E4E7
- 圆角: 12px
- hover: 阴影加深 + translateY(-2px)
- transition: all 200ms ease
```

---

## 4. Linear 动效参考

### 入场动画
```css
@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px) scale(0.98);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* duration: 300ms */
/* timing-function: cubic-bezier(0.16, 1, 0.3, 1) */
```

### 按钮微交互
```css
.button {
  transition: transform 150ms ease, box-shadow 150ms ease;
}
.button:hover {
  transform: scale(1.02);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.25);
}
.button:active {
  transform: scale(0.98);
}
```

### 页面切换
```css
.page-enter {
  animation: slideUp 300ms cubic-bezier(0.16, 1, 0.3, 1);
}
```

---

## 5. 颜色系统

### 老人端
```javascript
const elderlyColors = {
  primary: '#07C160',      // 微信绿
  primaryDark: '#06AD56',
  background: '#FFFDF5',   // 米黄
  surface: '#FFFFFF',
  text: '#2D2D2D',        // 正文
  textSecondary: '#666666', // 次要文字
  accent: '#FF9500',      // 强调/警告
  border: '#E8E8E8',
  success: '#07C160',
  warning: '#FF9500',
  error: '#FF3B30',
}
```

### 学生端
```javascript
const studentColors = {
  primary: '#6366F1',      // 靛蓝
  primaryDark: '#4F46E5',
  background: '#FAFAF8',   // 米白
  surface: '#FFFFFF',
  surfaceHover: '#F4F4F5',
  text: '#18181B',        // 墨黑
  textSecondary: '#71717A', // 次要
  textMuted: '#A1A1AA',   // 更淡
  accent: '#10B981',      // 翠绿
  border: '#E4E4E7',
  success: '#10B981',
  warning: '#F59E0B',
  error: '#EF4444',
}
```

---

## 6. 字体规范

### 老人端
```
标题: 28px / 32px / 36px (bold)
正文: 18px / 20px (regular)
引导文字: 20px (medium, 带背景高亮)
按钮: 20px (bold)
验证码: 48px (bold, 等宽)
```

### 学生端
```
标题: 24px / 20px / 18px (semibold)
正文: 15px / 14px (regular)
标签: 12px (medium, uppercase)
按钮: 15px (medium)
数据: 32px (semibold)
```

---

## 7. 特殊组件

### 老人端 - 大按钮带引导
```vue
<button class="elderly-btn">
  <span class="label">点这里</span>
  <span class="action">发布任务</span>
</button>
```

### 老人端 - 验证码展示
```vue
<div class="code-display">
  <div class="code-label">请把这个数字念给学生听</div>
  <div class="code-number">1 2 3 4 5 6</div>
</div>
```

### 学生端 - 任务卡片
```vue
<Motion :initial="{ opacity: 0, y: 20 }" :enter="{ opacity: 1, y: 0 }">
  <div class="task-card">
    <div class="task-type">代买物品</div>
    <div class="task-desc">需要买一盒降压药</div>
    <div class="task-meta">距您 500m · 刚刚</div>
  </div>
</Motion>
```
