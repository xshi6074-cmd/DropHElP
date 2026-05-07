<template>
  <div class="student-app">
    <!-- 顶部导航 -->
    <header class="bg-student-surface/80 backdrop-blur-md border-b border-student-border sticky top-0 z-10">
      <div class="page-container py-4">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-xl font-semibold text-student-text">
              快帮
            </h1>
            <p class="text-sm text-student-text-secondary">
              志愿者服务平台
            </p>
          </div>
          <router-link
            to="/student/profile"
            class="w-10 h-10 rounded-full bg-student-surface-hover flex items-center justify-center
                   hover:bg-student-border transition-colors"
          >
            <svg class="w-5 h-5 text-student-text-secondary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          </router-link>
        </div>
      </div>
    </header>

    <main class="page-container py-8">
      <!-- 欢迎语 -->
      <div v-motion-slide-bottom class="mb-8">
        <h2 class="text-2xl font-semibold text-student-text mb-2">
          你好，志愿者
        </h2>
        <p class="text-student-text-secondary">
          帮助社区老人，积累志愿时长
        </p>
      </div>

      <!-- 统计卡片 -->
      <div v-motion-slide-bottom :delay="100" class="grid grid-cols-2 gap-3 mb-8">
        <div class="student-card text-center py-5">
          <div class="text-2xl font-semibold text-student-primary mb-1">
            {{ stats.completed || 0 }}
          </div>
          <div class="text-xs text-student-text-secondary uppercase tracking-wide">
            已完成
          </div>
        </div>
        <div class="student-card text-center py-5">
          <div class="text-2xl font-semibold text-student-accent mb-1">
            {{ stats.no_show || 0 }}
          </div>
          <div class="text-xs text-student-text-secondary uppercase tracking-wide">
            爽约次数
          </div>
        </div>
      </div>

      <!-- 任务大厅入口 -->
      <div v-motion-slide-bottom :delay="200">
        <router-link
          to="/student/hall"
          class="student-card flex items-center justify-between p-5 group"
        >
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 rounded-xl bg-student-primary/10 flex items-center justify-center
                        group-hover:bg-student-primary/20 transition-colors">
              <svg class="w-6 h-6 text-student-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <div>
              <h3 class="font-medium text-student-text">
                任务大厅
              </h3>
              <p class="text-sm text-student-text-secondary">
                查看待接任务
              </p>
            </div>
          </div>
          <svg class="w-5 h-5 text-student-text-muted group-hover:text-student-primary transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </router-link>
      </div>

      <!-- 当前任务提醒 -->
      <div v-if="currentTask" v-motion-slide-bottom :delay="300" class="mt-6">
        <router-link
          to="/student/task"
          class="student-card p-5 border-l-4 border-student-primary bg-student-primary/5"
        >
          <div class="flex items-center justify-between mb-2">
            <span class="student-tag">进行中</span>
            <span class="text-xs text-student-text-secondary">
              {{ timeAgo(currentTask.accepted_at) }}
            </span>
          </div>
          <h3 class="font-medium text-student-text mb-1">
            {{ taskTypeName(currentTask.type) }}
          </h3>
          <p class="text-sm text-student-text-secondary line-clamp-1">
            {{ currentTask.description }}
          </p>
        </router-link>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import client from '../../api/client.js'

const stats = ref({ completed: 0, no_show: 0 })
const currentTask = ref(null)

const taskTypes = {
  buy_medicine: '代买药品',
  phone_guide: '手机指导',
  heavy_lifting: '重物搬运',
  other: '其他帮助'
}

const taskTypeName = (type) => taskTypes[type] || type

const timeAgo = (date) => {
  if (!date) return ''
  const minutes = Math.floor((new Date() - new Date(date)) / 60000)
  if (minutes < 60) return `${minutes}分钟前`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}小时前`
  return `${Math.floor(hours / 24)}天前`
}

const fetchData = async () => {
  try {
    const res = await client.get('/me/stats')
    stats.value = res

    const taskRes = await client.get('/tasks/me')
    if (taskRes) {
      currentTask.value = taskRes
    }
  } catch (e) {
    console.error(e)
  }
}

onMounted(fetchData)
</script>
