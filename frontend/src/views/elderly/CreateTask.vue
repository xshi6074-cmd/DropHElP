<template>
  <div class="elderly-app">
    <!-- 顶部导航 -->
    <header class="bg-elderly-surface border-b-2 border-elderly-border sticky top-0 z-10">
      <div class="page-container py-4 flex items-center">
        <button
          @click="$router.back()"
          class="w-10 h-10 flex items-center justify-center rounded-lg hover:bg-gray-100"
        >
          <svg class="w-6 h-6 text-elderly-text" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        <h1 class="text-elderly-xl font-bold text-elderly-text flex-1 text-center mr-10">
          发布任务
        </h1>
      </div>
    </header>

    <main class="page-container py-6">
      <form @submit.prevent="handleSubmit" class="space-y-6">
        <!-- 任务类型 -->
        <div v-motion-slide-bottom>
          <label class="block text-elderly-lg font-bold text-elderly-text mb-4">
            需要什么帮助？
          </label>
          <div class="grid grid-cols-2 gap-3">
            <button
              v-for="type in taskTypes"
              :key="type.id"
              @click="form.type = type.id"
              type="button"
              :class="[
                'elderly-card p-4 text-center transition-all',
                form.type === type.id
                  ? 'border-elderly-primary bg-elderly-primary/5'
                  : 'hover:bg-gray-50'
              ]"
            >
              <span class="text-2xl mb-2 block">{{ type.icon }}</span>
              <span class="text-elderly-base font-medium">{{ type.name }}</span>
            </button>
          </div>
          <p v-if="!form.type && showError" class="mt-2 text-elderly-sm text-red-500">
            请选择一个类型
          </p>
        </div>

        <!-- 位置 -->
        <div v-motion-slide-bottom :delay="100">
          <label class="block text-elderly-lg font-bold text-elderly-text mb-3">
            在哪里？
          </label>
          <input
            v-model="form.location"
            type="text"
            placeholder="例如：阳光小区3号楼"
            class="elderly-input"
            :disabled="submitting"
          />
          <p class="mt-2 text-elderly-sm text-elderly-text-secondary">
            只需要大概位置，保护隐私
          </p>
        </div>

        <!-- 描述 -->
        <div v-motion-slide-bottom :delay="200">
          <label class="block text-elderly-lg font-bold text-elderly-text mb-3">
            具体需要什么？
          </label>
          <textarea
            v-model="form.description"
            rows="4"
            placeholder="简单描述您的需求"
            class="elderly-input resize-none"
            :disabled="submitting"
          />
        </div>

        <!-- 提交按钮 -->
        <div v-motion-slide-bottom :delay="300">
          <button
            type="submit"
            :disabled="!canSubmit || submitting"
            class="elderly-btn"
          >
            <span v-if="submitting">发布中...</span>
            <span v-else>
              <span class="text-elderly-base opacity-90">点这里</span>
              <span class="ml-1">发布任务</span>
            </span>
          </button>
        </div>
      </form>

      <!-- 提示 -->
      <div v-motion-slide-bottom :delay="400" class="mt-8 elderly-card bg-yellow-50 border-yellow-200">
        <p class="text-elderly-base text-elderly-text">
          <span class="font-bold">温馨提示：</span>
          发布后请保持手机畅通，学生接单后会联系您
        </p>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import client from '../../api/client.js'

const router = useRouter()
const submitting = ref(false)
const showError = ref(false)

const taskTypes = [
  { id: 'buy_medicine', name: '代买物品', icon: '💊' },
  { id: 'phone_guide', name: '手机指导', icon: '📱' },
  { id: 'heavy_lifting', name: '重物搬运', icon: '📦' },
  { id: 'other', name: '其他帮助', icon: '🤝' }
]

const form = ref({
  type: '',
  location: '',
  description: ''
})

const canSubmit = computed(() => {
  return form.value.type && form.value.location.trim()
})

const handleSubmit = async () => {
  if (!canSubmit.value) {
    showError.value = true
    return
  }

  submitting.value = true

  try {
    await client.post('/tasks', {
      type: form.value.type,
      location_fuzzy: form.value.location,
      description: form.value.description
    })

    router.push('/elderly/tasks')
  } catch (e) {
    alert(e.message || '发布失败，请重试')
  } finally {
    submitting.value = false
  }
}
</script>
