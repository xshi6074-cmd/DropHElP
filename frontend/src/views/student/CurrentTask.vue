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
            当前任务
          </h1>
        </div>
      </div>
    </header>

    <main class="page-container py-6">
      <!-- 无任务状态 -->
      <div v-if="!task" class="empty-state">
        <svg class="w-12 h-12 text-student-text-muted mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
        </svg>
        <p class="text-student-text-secondary">暂无进行中的任务</p>
        <router-link
          to="/student/hall"
          class="student-btn mt-4"
        >
          去大厅接单
        </router-link>
      </div>

      <!-- 任务详情 -->
      <div v-else v-motion-slide-bottom class="space-y-4">
        <!-- 任务卡片 -->
        <div class="student-card">
          <div class="flex items-center justify-between mb-3">
            <span class="student-tag">
              {{ taskTypeName(task.type) }}
            </span>
            <span class="text-xs text-student-text-secondary">
              {{ timeAgo(task.accepted_at) }}
            </span>
          </div>

          <h2 class="font-medium text-student-text mb-2">
            {{ task.description || '需要帮助' }}
          </h2>

          <div class="flex items-center gap-1 text-sm text-student-text-secondary mb-4">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            <span>{{ task.location_fuzzy }}</span>
          </div>

          <!-- 倒计时 -->
          <div class="bg-student-primary/5 rounded-lg p-3 flex items-center gap-3">
            <svg class="w-5 h-5 text-student-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <p class="text-sm font-medium text-student-text">
                请在 <span class="text-student-primary">{{ countdown }}</span> 内完成
              </p>
              <p class="text-xs text-student-text-secondary">
                超时未验证将视为爽约
              </p>
            </div>
          </div>
        </div>

        <!-- 验证码输入 -->
        <div v-motion-slide-bottom :delay="100" class="student-card">
          <h3 class="font-medium text-student-text mb-2">
            完成任务
          </h3>
          <p class="text-sm text-student-text-secondary mb-4">
            请向老人询问6位验证码，输入后任务开始
          </p>

          <div class="flex gap-2 mb-4">
            <input
              v-for="(_, index) in codeDigits"
              :key="index"
              v-model="codeDigits[index]"
              type="text"
              maxlength="1"
              class="w-12 h-14 text-center text-xl font-medium rounded-lg border-2 border-student-border
                     focus:border-student-primary focus:ring-2 focus:ring-student-primary/20 focus:outline-none
                     transition-all"
              @input="handleInput($event, index)"
              @keydown="handleKeydown($event, index)"
              :ref="el => codeInputs[index] = el"
            />
          </div>

          <button
            @click="submitVerify"
            :disabled="!isCodeComplete || verifying"
            class="student-btn w-full"
            :class="{ 'opacity-50 cursor-not-allowed': !isCodeComplete }"
          >
            <span v-if="verifying">验证中...</span>
            <span v-else>确认完成</span>
          </button>
        </div>

        <!-- 异常标记 -->
        <button
          @click="showAbnormalModal = true"
          class="w-full py-3 text-sm text-student-text-secondary hover:text-red-500 transition-colors"
        >
          遇到异常情况？
        </button>
      </div>
    </main>

    <!-- 异常弹窗 -->
    <Transition name="fade">
      <div
        v-if="showAbnormalModal"
        class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4"
        @click.self="showAbnormalModal = false"
      >
        <div v-motion-scale class="bg-student-surface rounded-xl p-6 max-w-sm w-full">
          <h3 class="font-semibold text-student-text mb-4">标记异常</h3>

          <div class="space-y-2 mb-4">
            <button
              v-for="reason in abnormalReasons"
              :key="reason"
              @click="selectedReason = reason"
              :class="[
                'w-full text-left px-4 py-3 rounded-lg text-sm transition-colors',
                selectedReason === reason
                  ? 'bg-student-primary text-white'
                  : 'bg-student-surface-hover text-student-text hover:bg-student-border'
              ]"
            >
              {{ reason }}
            </button>
          </div>

          <textarea
            v-if="selectedReason === '其他原因'"
            v-model="customReason"
            rows="3"
            placeholder="请简要说明情况"
            class="student-input mb-4 resize-none"
          />

          <div class="flex gap-3">
            <button
              @click="showAbnormalModal = false"
              class="flex-1 student-btn-secondary"
            >
              取消
            </button>
            <button
              @click="submitAbnormal"
              :disabled="!canSubmitAbnormal"
              class="flex-1 bg-red-500 text-white py-2.5 rounded-lg font-medium
                     hover:bg-red-600 disabled:opacity-50 disabled:cursor-not-allowed
                     transition-colors"
            >
              提交
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import client from '../../api/client.js'

const router = useRouter()
const task = ref(null)
const codeDigits = ref(['', '', '', '', '', ''])
const codeInputs = ref([])
const verifying = ref(false)
const countdown = ref('3:00:00')
const showAbnormalModal = ref(false)
const selectedReason = ref('')
const customReason = ref('')

const abnormalReasons = ['老人未出现', '老人取消需求', '地址错误', '其他原因']

const taskTypes = {
  buy_medicine: '代买药品',
  phone_guide: '手机指导',
  heavy_lifting: '重物搬运',
  other: '其他帮助'
}

const taskTypeName = (type) => taskTypes[type] || type

const isCodeComplete = computed(() => codeDigits.value.every(d => d && /\d/.test(d)))

const canSubmitAbnormal = computed(() => {
  if (!selectedReason.value) return false
  if (selectedReason.value === '其他原因') return customReason.value.trim().length > 0
  return true
})

const timeAgo = (date) => {
  if (!date) return ''
  const minutes = Math.floor((new Date() - new Date(date)) / 60000)
  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}小时前`
  return `${Math.floor(hours / 24)}天前`
}

const handleInput = (e, index) => {
  const value = e.target.value
  if (/\d/.test(value)) {
    codeDigits.value[index] = value
    if (index < 5) {
      codeInputs.value[index + 1]?.focus()
    }
  } else {
    codeDigits.value[index] = ''
  }
}

const handleKeydown = (e, index) => {
  if (e.key === 'Backspace' && !codeDigits.value[index] && index > 0) {
    codeInputs.value[index - 1]?.focus()
  }
}

const fetchTask = async () => {
  try {
    const res = await client.get('/tasks/me')
    if (res) {
      task.value = res
      // 计算倒计时
      const acceptedAt = new Date(res.accepted_at)
      const deadline = new Date(acceptedAt.getTime() + 3 * 60 * 60 * 1000)
      updateCountdown(deadline)
      setInterval(() => updateCountdown(deadline), 1000)
    }
  } catch (e) {
    console.error(e)
  }
}

const updateCountdown = (deadline) => {
  const now = new Date()
  const diff = deadline - now
  if (diff <= 0) {
    countdown.value = '已超时'
    return
  }
  const hours = Math.floor(diff / 3600000)
  const minutes = Math.floor((diff % 3600000) / 60000)
  const seconds = Math.floor((diff % 60000) / 1000)
  countdown.value = `${hours}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
}

const submitVerify = async () => {
  if (!isCodeComplete.value) return

  verifying.value = true
  try {
    const code = codeDigits.value.join('')
    await client.post('/tasks/verify', {
      task_id: task.value.id,
      verification_code: code
    })
    router.push('/student/task/progress')
  } catch (e) {
    alert(e.message || '验证码错误')
    codeDigits.value = ['', '', '', '', '', '']
    codeInputs.value[0]?.focus()
  } finally {
    verifying.value = false
  }
}

const submitAbnormal = async () => {
  if (!canSubmitAbnormal.value) return

  const reason = selectedReason.value === '其他原因' ? customReason.value : selectedReason.value
  try {
    await client.post('/tasks/abnormal', {
      task_id: task.value.id,
      reason
    })
    showAbnormalModal.value = false
    router.push('/student')
  } catch (e) {
    alert(e.message)
  }
}

onMounted(fetchTask)
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 200ms ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
