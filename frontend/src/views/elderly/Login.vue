<template>
  <div class="elderly-app">
    <main class="page-container">
      <!-- 标题区 - 带入场动画 -->
      <div v-motion-slide-bottom class="text-center mb-8 pt-8">
        <h1 class="text-elderly-2xl font-bold text-elderly-text mb-2">
          快帮
        </h1>
        <p class="text-elderly-base text-elderly-text-secondary">
          互助服务平台
        </p>
      </div>

      <!-- 登录卡片 -->
      <div v-motion-slide-bottom :delay="100" class="elderly-card">
        <div class="text-center mb-6">
          <h2 class="text-elderly-xl font-bold text-elderly-text">
            老人登录
          </h2>
        </div>

        <form @submit.prevent="handleSubmit" class="space-y-5">
          <!-- 验证码输入 -->
          <div>
            <label class="block text-elderly-base font-medium text-elderly-text mb-3">
              请输入验证码
            </label>
            <input
              v-model="code"
              type="text"
              maxlength="8"
              placeholder="社区给的8位数字"
              class="elderly-input text-center tracking-widest"
              :disabled="loading"
            />
            <p class="mt-2 text-elderly-sm text-elderly-text-secondary">
              验证码在社区服务中心领取
            </p>
          </div>

          <!-- 登录按钮 -->
          <button
            type="submit"
            :disabled="!isValid || loading"
            class="elderly-btn"
          >
            <span v-if="loading">登录中...</span>
            <span v-else>
              <span class="text-elderly-base opacity-90">点这里</span>
              <span class="ml-1">登录</span>
            </span>
          </button>
        </form>

        <!-- 错误提示 -->
        <div v-if="error" class="mt-4 p-3 bg-red-50 rounded-lg text-elderly-sm text-red-600 text-center">
          {{ error }}
        </div>
      </div>

      <!-- 帮助信息 -->
      <div v-motion-slide-bottom :delay="200" class="mt-8 text-center">
        <p class="text-elderly-sm text-elderly-text-secondary">
          不会操作？
        </p>
        <p class="text-elderly-base text-elderly-text mt-1">
          请找社区志愿者帮忙
        </p>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useMotion } from '@vueuse/motion'
import client from '../../api/client.js'

const router = useRouter()
const code = ref('')
const loading = ref(false)
const error = ref('')

const isValid = computed(() => code.value.length >= 6)

const handleSubmit = async () => {
  if (!isValid.value) return

  loading.value = true
  error.value = ''

  try {
    const res = await client.post('/auth/elderly/login', {
      code: code.value.trim()
    })

    localStorage.setItem('token', res.access_token)
    localStorage.setItem('role', 'elderly')

    router.push('/elderly/tasks')
  } catch (e) {
    error.value = e.message || '登录失败，请检查验证码'
  } finally {
    loading.value = false
  }
}
</script>
