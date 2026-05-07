<template>
  <div class="elderly-app">
    <!-- 顶部导航 -->
    <header class="bg-elderly-surface border-b-2 border-elderly-border sticky top-0 z-10">
      <div class="page-container py-4">
        <h1 class="text-elderly-xl font-bold text-elderly-text text-center">
          我的任务
        </h1>
      </div>
    </header>

    <main class="page-container py-6">
      <!-- 当前任务 -->
      <div v-if="currentTask" v-motion-slide-bottom class="mb-6">
        <div class="flex items-center gap-2 mb-3">
          <span class="elderly-hint">进行中</span>
          <span class="text-elderly-sm text-elderly-text-secondary">
            {{ formatTime(currentTask.created_at) }}
          </span>
        </div>

        <div class="elderly-card">
          <h3 class="text-elderly-lg font-bold text-elderly-text mb-2">
            {{ taskTypeName(currentTask.type) }}
          </h3>
          <p class="text-elderly-base text-elderly-text-secondary mb-6">
            {{ currentTask.description }}
          </p>

          <!-- 验证码展示 - 大字体 -->
          <div class="bg-elderly-primary/5 rounded-elderly p-6 text-center">
            <p class="text-elderly-base text-elderly-text-secondary mb-4">
              请把这个数字念给学生
            </p>
            <div class="elderly-code">
              {{ formatCode(currentTask.meet_code) }}
            </div>
            <p class="mt-4 text-elderly-sm text-elderly-accent">
              学生输入后任务开始
            </p>
          </div>
        </div>
      </div>

      <!-- 没有任务 -->
      <div v-else v-motion-slide-bottom class="elderly-card text-center py-12 mb-6">
        <p class="text-elderly-lg text-elderly-text-secondary mb-2">
          您还没有任务
        </p>
        <p class="text-elderly-base text-elderly-text-muted">
          点击下方按钮发布新任务
        </p>
      </div>

      <!-- 发布按钮 -->
      <div v-motion-slide-bottom :delay="100">
        <button @click="createTask" class="elderly-btn">
          <span class="text-elderly-base opacity-90">点这里</span>
          <span class="ml-1">发布新任务</span>
        </button>
      </div>

      <!-- 历史任务 -->
      <div v-motion-slide-bottom :delay="200" class="mt-10">
        <h2 class="text-elderly-lg font-bold text-elderly-text mb-4">
          已完成
        </h2>

        <div v-if="completedTasks.length === 0" class="text-center py-8">
          <p class="text-elderly-base text-elderly-text-secondary">
            还没有已完成的任务
          </p>
        </div>

        <div v-else class="space-y-3">
          <div
            v-for="task in completedTasks"
            :key="task.id"
            class="elderly-card py-4"
          >
            <div class="flex items-center justify-between">
              <span class="text-elderly-base font-medium">
                {{ taskTypeName(task.type) }}
              </span>
              <span class="text-elderly-sm text-elderly-text-secondary">
                {{ formatTime(task.completed_at) }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import client from '../../api/client.js'

const router = useRouter()
const currentTask = ref(null)
const completedTasks = ref([])

const taskTypes = {
  buy_medicine: '代买药品',
  phone_guide: '手机指导',
  heavy_lifting: '重物搬运',
  other: '其他帮助'
}

const taskTypeName = (type) => taskTypes[type] || type

const formatCode = (code) => {
  if (!code) return ''
  return code.split('').join(' ')
}

const formatTime = (date) => {
  if (!date) return ''
  const d = new Date(date)
  return `${d.getMonth() + 1}月${d.getDate()}日`
}

const fetchTasks = async () => {
  try {
    const res = await client.get('/tasks/me')
    if (res) {
      currentTask.value = res
    }
  } catch (e) {
    console.error(e)
  }
}

const createTask = () => {
  router.push('/elderly/create')
}

onMounted(fetchTasks)
</script>
