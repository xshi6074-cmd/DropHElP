<template>
  <div class="student-app">
    <!-- 顶部导航 -->
    <header class="bg-student-surface/80 backdrop-blur-md border-b border-student-border sticky top-0 z-10">
      <div class="page-container py-4">
        <div class="flex items-center justify-between">
          <h1 class="text-lg font-semibold text-student-text">
            个人中心
          </h1>
          <button
            @click="logout"
            class="text-sm text-student-text-secondary hover:text-red-500 transition-colors"
          >
            退出登录
          </button>
        </div>
      </div>
    </header>

    <main class="page-container py-6 space-y-4">
      <!-- 用户卡片 -->
      <div v-motion-slide-bottom class="student-card p-5">
        <div class="flex items-center gap-4">
          <div class="w-14 h-14 rounded-full bg-gradient-to-br from-student-primary to-student-primary-dark
                      flex items-center justify-center text-white text-xl font-semibold">
            学
          </div>
          <div>
            <h2 class="font-semibold text-student-text">
              志愿者
            </h2>
            <p class="text-sm text-student-text-secondary">
              学生用户
            </p>
          </div>
        </div>
      </div>

      <!-- 统计 -->
      <div v-motion-slide-bottom :delay="100" class="student-card">
        <h3 class="text-sm font-medium text-student-text mb-4">本月统计</h3>
        <div class="grid grid-cols-3 gap-4">
          <div class="text-center">
            <div class="text-2xl font-semibold text-student-primary mb-1">
              {{ stats.completed || 0 }}
            </div>
            <div class="text-xs text-student-text-secondary">已完成</div>
          </div>
          <div class="text-center">
            <div class="text-2xl font-semibold text-student-accent mb-1">
              {{ stats.abnormal || 0 }}
            </div>
            <div class="text-xs text-student-text-secondary">异常</div>
          </div>
          <div class="text-center">
            <div class="text-2xl font-semibold text-amber-500 mb-1">
              {{ stats.no_show || 0 }}
            </div>
            <div class="text-xs text-student-text-secondary">爽约</div>
          </div>
        </div>
      </div>

      <!-- 菜单 -->
      <div v-motion-slide-bottom :delay="200" class="student-card divide-y">
        <router-link
          to="/student"
          class="flex items-center justify-between py-4 group"
        >
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 rounded-lg bg-student-primary/10 flex items-center justify-center">
              <svg class="w-4 h-4 text-student-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
              </svg>
            </div>
            <span class="text-sm font-medium text-student-text">首页</span>
          </div>
          <svg class="w-4 h-4 text-student-text-muted group-hover:text-student-primary transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </router-link>

        <router-link
          to="/student/hall"
          class="flex items-center justify-between py-4 group"
        >
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 rounded-lg bg-student-accent/10 flex items-center justify-center">
              <svg class="w-4 h-4 text-student-accent" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <span class="text-sm font-medium text-student-text">任务大厅</span>
          </div>
          <svg class="w-4 h-4 text-student-text-muted group-hover:text-student-primary transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </router-link>

        <router-link
          to="/student/task"
          class="flex items-center justify-between py-4 group"
        >
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 rounded-lg bg-amber-500/10 flex items-center justify-center">
              <svg class="w-4 h-4 text-amber-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
            </div>
            <span class="text-sm font-medium text-student-text">当前任务</span>
          </div>
          <svg class="w-4 h-4 text-student-text-muted group-hover:text-student-primary transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </router-link>
      </div>

      <!-- 退出 -->
      <div v-motion-slide-bottom :delay="300">
        <button
          @click="logout"
          class="w-full py-3 text-sm font-medium text-red-500 rounded-lg border border-red-200
                 hover:bg-red-50 transition-colors"
        >
          退出登录
        </button>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import client from '../../api/client.js'

const router = useRouter()
const stats = ref({ completed: 0, abnormal: 0, no_show: 0 })

const fetchStats = async () => {
  try {
    const res = await client.get('/me/stats')
    stats.value = res
  } catch (e) {
    console.error(e)
  }
}

const logout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('role')
  router.push('/student/login')
}

onMounted(fetchStats)
</script>
