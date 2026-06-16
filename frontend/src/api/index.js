import http from '@/utils/request'

export const materialsApi = {
  list: (params) => http.get('/api/materials', params),
  get: (id) => http.get(`/api/materials/${id}`),
  create: (data) => http.post('/api/materials', data),
  update: (id, data) => http.put(`/api/materials/${id}`, data),
  delete: (id) => http.delete(`/api/materials/${id}`),
  categories: () => http.get('/api/materials/options/categories'),
  colors: () => http.get('/api/materials/options/colors')
}

export const dryingApi = {
  list: (params) => http.get('/api/drying-processes', params),
  get: (id) => http.get(`/api/drying-processes/${id}`),
  create: (data) => http.post('/api/drying-processes', data),
  update: (id, data) => http.put(`/api/drying-processes/${id}`, data),
  delete: (id) => http.delete(`/api/drying-processes/${id}`),
  methods: () => http.get('/api/drying-processes/options/methods'),
  statuses: () => http.get('/api/drying-processes/options/statuses')
}

export const specimensApi = {
  list: (params) => http.get('/api/specimens', params),
  get: (id) => http.get(`/api/specimens/${id}`),
  create: (data) => http.post('/api/specimens', data),
  update: (id, data) => http.put(`/api/specimens/${id}`, data),
  delete: (id) => http.delete(`/api/specimens/${id}`),
  like: (id) => http.post(`/api/specimens/${id}/like`),
  categories: () => http.get('/api/specimens/options/categories'),
  statuses: () => http.get('/api/specimens/options/statuses'),
  frameStyles: () => http.get('/api/specimens/options/frame-styles')
}

export const notesApi = {
  list: (params) => http.get('/api/technique-notes', params),
  get: (id) => http.get(`/api/technique-notes/${id}`),
  create: (data) => http.post('/api/technique-notes', data),
  update: (id, data) => http.put(`/api/technique-notes/${id}`, data),
  delete: (id) => http.delete(`/api/technique-notes/${id}`),
  categories: () => http.get('/api/technique-notes/options/categories'),
  difficulties: () => http.get('/api/technique-notes/options/difficulties')
}

export const plansApi = {
  list: (params) => http.get('/api/design-plans', params),
  get: (id) => http.get(`/api/design-plans/${id}`),
  create: (data) => http.post('/api/design-plans', data),
  update: (id, data) => http.put(`/api/design-plans/${id}`, data),
  delete: (id) => http.delete(`/api/design-plans/${id}`),
  styles: () => http.get('/api/design-plans/options/styles'),
  scenes: () => http.get('/api/design-plans/options/scenes'),
  statuses: () => http.get('/api/design-plans/options/statuses')
}

export const imagesApi = {
  list: (params) => http.get('/api/product-images', params),
  get: (id) => http.get(`/api/product-images/${id}`),
  create: (data) => http.post('/api/product-images', data),
  update: (id, data) => http.put(`/api/product-images/${id}`, data),
  delete: (id) => http.delete(`/api/product-images/${id}`),
  shotAngles: () => http.get('/api/product-images/options/shot-angles'),
  lightings: () => http.get('/api/product-images/options/lightings'),
  backgrounds: () => http.get('/api/product-images/options/backgrounds')
}

export const shareApi = {
  list: (params) => http.get('/api/share-posts', params),
  get: (id) => http.get(`/api/share-posts/${id}`),
  create: (data) => http.post('/api/share-posts', data),
  update: (id, data) => http.put(`/api/share-posts/${id}`, data),
  delete: (id) => http.delete(`/api/share-posts/${id}`),
  like: (id, data) => http.post(`/api/share-posts/${id}/like`, data),
  share: (id) => http.post(`/api/share-posts/${id}/share`)
}

export const favoritesApi = {
  list: (params) => http.get('/api/favorites', params),
  create: (data) => http.post('/api/favorites', data),
  delete: (id) => http.delete(`/api/favorites/${id}`),
  folders: () => http.get('/api/favorites/folders')
}

export const consumptionsApi = {
  list: (params) => http.get('/api/consumptions', params),
  get: (id) => http.get(`/api/consumptions/${id}`),
  create: (data) => http.post('/api/consumptions', data),
  update: (id, data) => http.put(`/api/consumptions/${id}`, data),
  delete: (id) => http.delete(`/api/consumptions/${id}`),
  categories: () => http.get('/api/consumptions/options/categories'),
  summary: () => http.get('/api/consumptions/summary')
}

export const statisticsApi = {
  main: () => http.get('/api/statistics'),
  trend: () => http.get('/api/statistics/trend')
}

const MAX_RETRY_COUNT = 2

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

async function uploadWithRetry(uploadFn, retries = MAX_RETRY_COUNT) {
  let lastError
  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      const result = await uploadFn()
      return result
    } catch (error) {
      lastError = error
      if (attempt < retries) {
        await delay(500 * (attempt + 1))
      }
    }
  }
  throw lastError
}

export const uploadApi = {
  uploadImage: (file, folder = 'general', onProgress) => {
    const form = new FormData()
    form.append('file', file)
    form.append('folder', folder)
    return uploadWithRetry(() => http.upload('/api/uploads', form, onProgress))
  },
  uploadBatch: (files, folder = 'general') => {
    const form = new FormData()
    files.forEach((f) => form.append('files', f))
    form.append('folder', folder)
    return uploadWithRetry(() => http.upload('/api/uploads/batch', form))
  },
  deleteImage: (path) => http.delete('/api/uploads', { file_path: path })
}
