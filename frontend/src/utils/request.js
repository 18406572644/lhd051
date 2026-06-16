import axios from 'axios'
import { useMessage } from 'naive-ui'

const message = useMessage ? null : null

const api = axios.create({
  baseURL: '/',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

api.interceptors.request.use(
  (config) => {
    return config
  },
  (error) => Promise.reject(error)
)

api.interceptors.response.use(
  (response) => {
    return { data: response.data }
  },
  (error) => {
    const status = error.response?.status
    const data = error.response?.data
    console.error('[API Error]', status, data?.detail || error.message)
    return Promise.reject(data?.detail || error.message || '请求失败')
  }
)

export const http = {
  get: (url, params) => api.get(url, { params }),
  post: (url, data) => api.post(url, data),
  put: (url, data) => api.put(url, data),
  delete: (url, params) => api.delete(url, { params }),
  upload: (url, formData, onProgress) =>
    api.post(url, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: onProgress
    })
}

export default http
