<template>
  <div class="student-app">
    <!-- 顶部导航 -->
    <header class="bg-student-surface/80 backdrop-blur-md border-b border-student-border sticky top-0 z-10">
      <div class="page-container py-4">
        <div class="flex items-center">
          <button
            @click="$router.back()"
            class="w-10 h-10 rounded-lg flex items-center justify-center hover:bg-student-surface-hover transition-colors"
          >
            <svg class="w-5 h-5 text-student-text" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <h1 class="text-lg font-semibold text-student-text flex-1 text-center mr-10">
            任务大厅
          </h1>
        </div>
      </div>
    </header>

    <main class="page-container py-6">
      <!-- 筛选栏 -->
      <div v-motion-slide-bottom class="mb-4 flex gap-2">
        <button
          v-for="filter in filters"
          :key="filter.id"
          @click="activeFilter = filter.id"
          :class="[
            'px-3 py-1.5 rounded-lg text-sm font-medium transition-all',
            activeFilter === filter.id
              ? 'bg-student-primary text-white'
              : 'bg-student-surface text-student-text-secondary hover:bg-student-surface-hover'
          ]"
        >
          {{ filter.name }}
        </button>
      </div>

      <!-- 任务列表 -->
      <div v-if="loading" class="py-12 flex justify-center">
        <div class="loading-spinner text-student-primary" />
      </div>

      <div v-else-if="filteredTasks.length === 0" class="empty-state">
        <svg class="w-12 h-12 text-student-text-muted mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
        </svg>
        <p class="text-sm text-student-text-secondary">
          暂无待接任务
        </p>
        <p class="text-xs text-student-text-muted mt-1">
          稍后再来看看
        </p>
      </div>

      <div v-else class="space-y-3">
        <div
          v-for="(task, index) in filteredTasks"
          :key="task.id"
          v-motion-slide-bottom
          :delay="index * 50"
          class="student-card p-4 cursor-pointer group"
          @click="acceptTask(task.id)"
        >
          <div class="flex items-start justify-between mb-2">
            <span class="student-tag">
              {{ taskTypeName(task.type) }}
            </span>
            <span class="text-xs text-student-text-muted">
              {{ timeAgo(task.created_at) }}
            </span>
          </div>

          <p class="text-sm text-student-text mb-2 line-clamp-2">
            {{ task.description || '需要帮助' }}
          </p>

          <div class="flex items-center justify-between">
            <div class="flex items-center gap-1 text-xs text-student-text-secondary">
              <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              <span>{{ task.location_fuzzy }}</span>
            </div>

            <button class="student-btn text-xs py-1.5 px-3 opacity-0 group-hover:opacity-100 transition-opacity">
              接单
            </button>
          </div>
        </div>
      </div>
    </main>

    <!-- 当前任务悬浮提示 -->
    <div
      v-if="hasCurrentTask"
      v-motion-slide-bottom
      class="fixed bottom-6 left-4 right-4 max-w-lg mx-auto"
    >
      <router-link
        to="/student/task"
        class="flex items-center justify-between px-4 py-3 bg-student-primary text-white rounded-xl shadow-student-lg"
      >
        <div>
          <p class="font-medium">您有进行中的任务</p>
          <p class="text-xs opacity-80">点击查看详情</p>
        </div>
        <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
        </svg>
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import client from '../../api/client.js'

const router = useRouter()
const tasks = ref([])
const loading = ref(true)
const hasCurrentTask = ref(false)

const filters = [
  { id: 'all', name: '全部' },
  { id: 'buy_medicine', name: '代购' },
  { id: 'phone_guide', name: '指导' },
  { id: 'heavy_lifting', name: '搬运' }
]
const activeFilter = ref('all')

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
  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}小时前`
  return `${Math.floor(hours / 24)}天前`
}

const filteredTasks = computed(() => {
  if (activeFilter.value === 'all') return tasks.value
  return tasks.value.filter(t => t.type === activeFilter.value)
})

const fetchTasks = async () => {
  loading.value = true
  try {
    // 获取任务列表
    const res = await client.get('/tasks/types')
    // TODO: 实际应该调用获取待接任务列表的API
    tasks.value = []

    // 检查是否有当前任务
    const current = await client.get('/tasks/me')
    hasCurrentTask.value = !!current
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const acceptTask = async (taskId) => {
  if (hasCurrentTask.value) {
    alert('您已有进行中的任务，请先完成')
    return
  }

  try {
    await client.post('/tasks/accept', { task_id: taskId })
    router.push('/student/task')
  } catch (e) {
    alert(e.message || '接单失败')
  }
}

onMounted(fetchTasks)
</script>
