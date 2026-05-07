import axios from 'axios'

const client = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器：自动附加Token
client.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    // DEBUG模式打印请求
    if (import.meta.env.DEV) {
      console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`)
    }

    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截器：统一错误处理
client.interceptors.response.use(
  (response) => {
    const data = response.data

    // 统一响应格式处理
    if (data.code !== 0) {
      const error = new Error(data.message || '请求失败')
      error.code = data.code
      error.response = response
      throw error
    }

    return data.data
  },
  (error) => {
    // 网络错误或服务器错误
    if (!error.response) {
      console.error('[API Error] 网络连接失败，请检查后端服务是否启动')
      throw new Error('网络连接失败，请检查后端服务')
    }

    // HTTP错误
    if (error.response.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/'
      throw new Error('登录已过期，请重新登录')
    }

    const message = error.response?.data?.message || '服务器错误'
    console.error(`[API Error] ${message}`)
    throw new Error(message)
  }
)

export default client
