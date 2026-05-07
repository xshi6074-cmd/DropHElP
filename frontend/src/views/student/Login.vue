<template>
  <div class="student-app">
    <main class="min-h-screen flex items-center justify-center p-4">
      <div v-motion-slide-bottom class="w-full max-w-sm">
        <!-- Logo区 -->
        <div class="text-center mb-10">
          <div class="w-16 h-16 rounded-2xl bg-gradient-to-br from-student-primary to-student-primary-dark
                      mx-auto mb-4 flex items-center justify-center shadow-student-lg">
            <svg class="w-8 h-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
          </div>
          <h1 class="text-2xl font-semibold text-student-text mb-1">
            快帮
          </h1>
          <p class="text-student-text-secondary">
            志愿者服务平台
          </p>
        </div>

        <!-- 登录卡片 -->
        <div class="bg-student-surface rounded-2xl border border-student-border p-6 shadow-student">
          <h2 class="text-lg font-semibold text-student-text mb-6">
            学生登录
          </h2>

          <form @submit.prevent="handleSendCode" class="space-y-4">
            <!-- 邮箱输入 -->
            <div v-if="!codeSent">
              <label class="block text-sm font-medium text-student-text mb-2">
                教育邮箱
              </label>
              <div class="flex">
                <input
                  v-model="emailPrefix"
                  type="text"
                  placeholder="学号"
                  class="flex-1 px-4 py-2.5 bg-student-bg border border-student-border rounded-l-lg
                         text-sm text-student-text placeholder-student-text-muted
                         focus:border-student-primary focus:ring-2 focus:ring-student-primary/20
                         focus:outline-none transition-all"
                  :disabled="sending"
                />
                <span class="px-3 py-2.5 bg-student-surface-hover border border-l-0 border-student-border
                           rounded-r-lg text-sm text-student-text-secondary">
                  @mails.tsinghua.edu.cn
                </span>
              </div>
              <p class="mt-1.5 text-xs text-student-text-muted">
                验证码将发送到您的邮箱
              </p>
            </div>

            <!-- 验证码输入 -->
            <div v-else>
              <label class="block text-sm font-medium text-student-text mb-2">
                验证码
              </label>
              <div class="flex gap-1.5">
                <input
                  v-for="(_, index) in codeDigits"
                  :key="index"
                  v-model="codeDigits[index]"
                  type="text"
                  maxlength="1"
                  class="w-10 h-12 text-center text-lg font-medium rounded-lg border border-student-border
                         focus:border-student-primary focus:ring-2 focus:ring-student-primary/20
                         focus:outline-none transition-all"
                  @input="handleCodeInput($event, index)"
                  @keydown="handleCodeKeydown($event, index)"
                  :ref="el => codeInputs[index] = el"
                />
              </div>
              <div class="mt-3 flex items-center justify-between text-xs">
                <span class="text-student-text-muted">
                  未收到？检查垃圾箱
                </span>
                <button
                  type="button"
                  @click="resendCode"
                  :disabled="resendCooldown > 0"
                  class="text-student-primary hover:text-student-primary-dark disabled:text-student-text-muted
                         disabled:cursor-not-allowed transition-colors"
                >
                  {{ resendCooldown > 0 ? `${resendCooldown}s后重发` : '重新发送' }}
                </button>
              </div>
            </div>

            <!-- 主按钮 -->
            <button
              type="submit"
              :disabled="!canSubmit || sending"
              class="w-full student-btn py-3"
              :class="{ 'opacity-50 cursor-not-allowed': !canSubmit || sending }"
            >
              <span v-if="sending">发送中...</span>
              <span v-else-if="!codeSent">获取验证码</span>
              <span v-else>登录</span>
            </button>
          </form>

          <!-- 开发模式提示 -->
          <div v-if="devCode" class="mt-4 p-3 bg-blue-50 rounded-lg">
            <p class="text-xs text-blue-600">
              [开发模式] 验证码: <span class="font-mono font-semibold">{{ devCode }}</span>
            </p>
          </div>

          <!-- 错误提示 -->
          <Transition name="fade">
            <div v-if="error" class="mt-4 p-3 bg-red-50 rounded-lg">
              <p class="text-sm text-red-600">{{ error }}</p>
            </div>
          </Transition>
        </div>

        <!-- 底部信息 -->
        <p class="text-center text-xs text-student-text-muted mt-8">
          仅支持 @mails.tsinghua.edu.cn 登录
        </p>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import client from '../../api/client.js'

const router = useRouter()
const emailPrefix = ref('')
const codeSent = ref(false)
const codeDigits = ref(['', '', '', '', '', ''])
const codeInputs = ref([])
const sending = ref(false)
const error = ref('')
const devCode = ref('')
const resendCooldown = ref(0)

const canSubmit = computed(() => {
  if (!codeSent.value) {
    return emailPrefix.value.trim().length > 0
  }
  return codeDigits.value.every(d => d && /\d/.test(d))
})

const handleSendCode = async () => {
  if (!canSubmit.value) return

  sending.value = true
  error.value = ''

  try {
    const email = `${emailPrefix.value.trim()}@xx.edu.cn`
    const res = await client.post('/auth/student/login', { email })
    codeSent.value = true
    devCode.value = res.debug_code || ''
    startResendCooldown()

    // 自动聚焦第一个输入框
    setTimeout(() => codeInputs.value[0]?.focus(), 100)
  } catch (e) {
    error.value = e.message || '发送失败，请重试'
  } finally {
    sending.value = false
  }
}

const handleCodeInput = (e, index) => {
  const value = e.target.value
  if (/\d/.test(value)) {
    codeDigits.value[index] = value
    if (index < 5) {
      codeInputs.value[index + 1]?.focus()
    } else {
      // 最后一位输入完成，自动提交
      handleVerify()
    }
  } else {
    codeDigits.value[index] = ''
  }
}

const handleCodeKeydown = (e, index) => {
  if (e.key === 'Backspace' && !codeDigits.value[index] && index > 0) {
    codeInputs.value[index - 1]?.focus()
  }
}

const handleVerify = async () => {
  if (!canSubmit.value) return

  sending.value = true
  try {
    const email = `${emailPrefix.value.trim()}@xx.edu.cn`
    const code = codeDigits.value.join('')
    const res = await client.post('/auth/student/verify', { email, code })

    localStorage.setItem('token', res.access_token)
    localStorage.setItem('role', 'student')

    router.push('/student')
  } catch (e) {
    error.value = e.message || '验证码错误'
    codeDigits.value = ['', '', '', '', '', '']
    codeInputs.value[0]?.focus()
  } finally {
    sending.value = false
  }
}

const resendCode = () => {
  if (resendCooldown.value > 0) return
  codeSent.value = false
  codeDigits.value = ['', '', '', '', '', '']
  error.value = ''
  handleSendCode()
}

const startResendCooldown = () => {
  resendCooldown.value = 60
  const timer = setInterval(() => {
    resendCooldown.value--
    if (resendCooldown.value <= 0) {
      clearInterval(timer)
    }
  }, 1000)
}

onMounted(() => {
  // 检查是否已登录
  const token = localStorage.getItem('token')
  const role = localStorage.getItem('role')
  if (token && role === 'student') {
    router.push('/student')
  }
})
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
