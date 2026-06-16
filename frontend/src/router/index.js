import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Dashboard.vue'),
    meta: { title: '花语集 · 首页', icon: 'home' }
  },
  {
    path: '/materials',
    name: 'Materials',
    component: () => import('@/views/Materials.vue'),
    meta: { title: '鲜花原料入库', icon: 'flower' }
  },
  {
    path: '/drying',
    name: 'Drying',
    component: () => import('@/views/DryingProcesses.vue'),
    meta: { title: '脱水制作记录', icon: 'flask' }
  },
  {
    path: '/specimens',
    name: 'Specimens',
    component: () => import('@/views/Specimens.vue'),
    meta: { title: '成品标本陈列', icon: 'flower2' }
  },
  {
    path: '/specimens/:id',
    name: 'SpecimenDetail',
    component: () => import('@/views/SpecimenDetail.vue'),
    meta: { title: '标本详情', hidden: true }
  },
  {
    path: '/notes',
    name: 'Notes',
    component: () => import('@/views/TechniqueNotes.vue'),
    meta: { title: '制作手法笔记', icon: 'book' }
  },
  {
    path: '/plans',
    name: 'Plans',
    component: () => import('@/views/DesignPlans.vue'),
    meta: { title: '设计方案存档', icon: 'palette' }
  },
  {
    path: '/gallery',
    name: 'Gallery',
    component: () => import('@/views/Gallery.vue'),
    meta: { title: '实拍图片管理', icon: 'camera' }
  },
  {
    path: '/statistics',
    name: 'Statistics',
    component: () => import('@/views/Statistics.vue'),
    meta: { title: '时长与耗材统计', icon: 'chart' }
  },
  {
    path: '/share',
    name: 'Share',
    component: () => import('@/views/Share.vue'),
    meta: { title: '作品分享广场', icon: 'heart' }
  },
  {
    path: '/favorites',
    name: 'Favorites',
    component: () => import('@/views/Favorites.vue'),
    meta: { title: '我的收藏夹', icon: 'star' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  }
})

router.beforeEach((to, from, next) => {
  document.title = to.meta?.title || '花语集 · 干花标本管理系统'
  next()
})

export default router
