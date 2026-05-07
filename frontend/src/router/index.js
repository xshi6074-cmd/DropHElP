import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/elderly/login'
  },
  // 老人端路由
  {
    path: '/elderly/login',
    name: 'ElderlyLogin',
    component: () => import('../views/elderly/Login.vue'),
    meta: { elderlyMode: true }
  },
  {
    path: '/elderly/tasks',
    name: 'ElderlyTasks',
    component: () => import('../views/elderly/Tasks.vue'),
    meta: { elderlyMode: true, requiresAuth: true, role: 'elderly' }
  },
  {
    path: '/elderly/create',
    name: 'ElderlyCreate',
    component: () => import('../views/elderly/CreateTask.vue'),
    meta: { elderlyMode: true, requiresAuth: true, role: 'elderly' }
  },
  // 学生端路由
  {
    path: '/student/login',
    name: 'StudentLogin',
    component: () => import('../views/student/Login.vue')
  },
  {
    path: '/student',
    name: 'StudentDashboard',
    component: () => import('../views/student/Dashboard.vue'),
    meta: { requiresAuth: true, role: 'student' }
  },
  {
    path: '/student/hall',
    name: 'StudentHall',
    component: () => import('../views/student/Hall.vue'),
    meta: { requiresAuth: true, role: 'student' }
  },
  {
    path: '/student/task',
    name: 'StudentTask',
    component: () => import('../views/student/CurrentTask.vue'),
    meta: { requiresAuth: true, role: 'student' }
  },
  {
    path: '/student/profile',
    name: 'StudentProfile',
    component: () => import('../views/student/Profile.vue'),
    meta: { requiresAuth: true, role: 'student' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 老人模式样式
  if (to.meta.elderlyMode) {
    document.body.classList.add('elderly-mode')
  } else {
    document.body.classList.remove('elderly-mode')
  }

  // 认证检查
  if (to.meta.requiresAuth) {
    const token = localStorage.getItem('token')
    const role = localStorage.getItem('role')

    if (!token) {
      const loginPath = to.meta.role === 'elderly' ? '/elderly/login' : '/student/login'
      next(loginPath)
      return
    }

    if (to.meta.role && to.meta.role !== role) {
      const correctPath = role === 'elderly' ? '/elderly/tasks' : '/student'
      next(correctPath)
      return
    }
  }

  next()
})

export default router
