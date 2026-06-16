<script setup>
import { ref, reactive, computed, onMounted, h } from 'vue'
import {
  NCard, NGrid, NGridItem, NTag, NIcon, NSpace, NButton, NInput,
  NSelect, NSwitch, NModal, NForm, NFormItem, NImage, NEmpty,
  NPopconfirm, useMessage, useDialog, NEllipsis, NDivider,
  NDynamicTags, NUpload, NPagination, NSkeleton
} from 'naive-ui'
import {
  BookOutline, Add, Search, Refresh, CreateOutline, TrashOutline,
  Star, StarOutline, CloseCircle, CloudUploadOutline, Ban,
  BulbOutline, AlertCircleOutline, LinkOutline, EyeOutline,
  FlowerOutline, Sparkles, DocumentTextOutline, BookmarkOutline
} from '@vicons/ionicons5'
import { notesApi, uploadApi } from '@/api'

const message = useMessage()
const dialog = useDialog()

const loading = ref(false)
const modalLoading = ref(false)
const uploadLoading = ref(false)

const showDetailModal = ref(false)
const showFormModal = ref(false)
const isEdit = ref(false)
const editingId = ref(null)
const currentDetail = ref(null)

const filters = reactive({
  keyword: '',
  category: null,
  difficulty: null,
  is_favorite: false
})

const pagination = reactive({
  page: 1,
  pageSize: 12,
  total: 0
})

const dataList = ref([])
const categoryOptions = ref([])
const difficultyOptions = ref([])

const defaultCategoryOptions = [
  { label: '采花', value: '采花' },
  { label: '预处理', value: '预处理' },
  { label: '风干', value: '风干' },
  { label: '保色', value: '保色' },
  { label: '装裱', value: '装裱' },
  { label: '搭配', value: '搭配' },
  { label: '其他', value: '其他' }
]

const defaultDifficultyOptions = [
  { label: '入门', value: '入门' },
  { label: '进阶', value: '进阶' },
  { label: '精通', value: '精通' }
]

const getDifficultyStyle = (diff) => {
  const map = {
    '入门': {
      bg: 'linear-gradient(135deg, rgba(168,195,160,0.85), rgba(139,168,136,0.9))',
      color: '#fff',
      shadow: '0 2px 8px rgba(168,195,160,0.35)'
    },
    '进阶': {
      bg: 'linear-gradient(135deg, rgba(139,168,195,0.85), rgba(118,140,163,0.9))',
      color: '#fff',
      shadow: '0 2px 8px rgba(139,168,195,0.35)'
    },
    '精通': {
      bg: 'linear-gradient(135deg, rgba(232,120,130,0.9), rgba(192,100,110,0.95))',
      color: '#fff',
      shadow: '0 2px 8px rgba(232,120,130,0.35)'
    }
  }
  return map[diff] || {
    bg: 'rgba(184,168,166,0.2)',
    color: '#8B7D7B',
    shadow: 'none'
  }
}

const getCategoryTagStyle = (cat) => {
  const map = {
    '采花': { bg: 'rgba(212,165,165,0.18)', color: '#C08990' },
    '预处理': { bg: 'rgba(245,200,107,0.22)', color: '#C49B3A' },
    '风干': { bg: 'rgba(168,195,160,0.22)', color: '#8BA888' },
    '保色': { bg: 'rgba(139,168,195,0.22)', color: '#768CA3' },
    '装裱': { bg: 'rgba(212,160,107,0.22)', color: '#B8824A' },
    '搭配': { bg: 'rgba(200,165,212,0.22)', color: '#9B76A8' },
    '其他': { bg: 'rgba(184,168,166,0.22)', color: '#8B7D7B' }
  }
  return map[cat] || { bg: 'rgba(184,168,166,0.18)', color: '#8B7D7B' }
}

const formValues = reactive({
  title: '',
  category: null,
  difficulty: null,
  content: '',
  tips: [],
  warnings: [],
  reference_links: [],
  image_url: '',
  is_favorite: false
})

const formRules = {
  title: {
    required: true,
    message: '请输入笔记标题',
    trigger: 'blur'
  },
  content: {
    required: true,
    message: '请输入笔记内容',
    trigger: 'blur'
  }
}

const getContentPreview = (content) => {
  if (!content) return ''
  const plain = content.replace(/<[^>]*>/g, '')
  return plain.length > 100 ? plain.substring(0, 100) + '...' : plain
}

async function loadOptions() {
  try {
    const [catRes, diffRes] = await Promise.all([
      notesApi.categories(),
      notesApi.difficulties()
    ])
    if (catRes?.data) {
      const data = Array.isArray(catRes.data) ? catRes.data : (catRes.data.list || [])
      categoryOptions.value = data.length > 0
        ? data.map(item => ({
            label: item.name || item.label || item,
            value: item.value ?? item.id ?? item.name ?? item
          }))
        : defaultCategoryOptions
    } else {
      categoryOptions.value = defaultCategoryOptions
    }
    if (diffRes?.data) {
      const data = Array.isArray(diffRes.data) ? diffRes.data : (diffRes.data.list || [])
      difficultyOptions.value = data.length > 0
        ? data.map(item => ({
            label: item.name || item.label || item,
            value: item.value ?? item.id ?? item.name ?? item
          }))
        : defaultDifficultyOptions
    } else {
      difficultyOptions.value = defaultDifficultyOptions
    }
  } catch (e) {
    categoryOptions.value = defaultCategoryOptions
    difficultyOptions.value = defaultDifficultyOptions
    console.warn('加载选项失败', e)
  }
}

async function loadData() {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      keyword: filters.keyword || undefined,
      category: filters.category || undefined,
      difficulty: filters.difficulty || undefined,
      is_favorite: filters.is_favorite || undefined
    }
    const res = await notesApi.list(params)
    if (res?.data) {
      if (res.data.items !== undefined) {
        dataList.value = res.data.items
        pagination.total = res.data.total ?? res.data.items.length
      } else if (Array.isArray(res.data)) {
        dataList.value = res.data
        pagination.total = res.data.length
      } else {
        dataList.value = []
        pagination.total = 0
      }
    }
  } catch (e) {
    message.error('加载笔记列表失败')
  } finally {
    loading.value = false
  }
}

function resetFilters() {
  filters.keyword = ''
  filters.category = null
  filters.difficulty = null
  filters.is_favorite = false
  pagination.page = 1
  loadData()
}

function onSearch() {
  pagination.page = 1
  loadData()
}

function handlePageChange(p) {
  pagination.page = p
  loadData()
}

function handlePageSizeChange(sz) {
  pagination.pageSize = sz
  pagination.page = 1
  loadData()
}

async function toggleFavorite(item) {
  try {
    const newValue = !item.is_favorite
    await notesApi.update(item.id, { is_favorite: newValue })
    item.is_favorite = newValue
    message.success(newValue ? '已加入收藏' : '已取消收藏')
  } catch (e) {
    message.error('操作失败')
  }
}

async function openDetail(item) {
  try {
    const res = await notesApi.get(item.id)
    if (res?.data) {
      currentDetail.value = res.data
      showDetailModal.value = true
    }
  } catch (e) {
    message.error('加载详情失败')
  }
}

function openCreate() {
  isEdit.value = false
  editingId.value = null
  Object.assign(formValues, {
    title: '',
    category: null,
    difficulty: null,
    content: '',
    tips: [],
    warnings: [],
    reference_links: [],
    image_url: '',
    is_favorite: false
  })
  showFormModal.value = true
}

async function openEdit(item) {
  isEdit.value = true
  editingId.value = item.id
  modalLoading.value = true
  showFormModal.value = true
  try {
    const res = await notesApi.get(item.id)
    if (res?.data) {
      const d = res.data
      Object.assign(formValues, {
        title: d.title ?? '',
        category: d.category ?? null,
        difficulty: d.difficulty ?? null,
        content: d.content ?? '',
        tips: Array.isArray(d.tips) ? [...d.tips] : [],
        warnings: Array.isArray(d.warnings) ? [...d.warnings] : [],
        reference_links: Array.isArray(d.reference_links) ? [...d.reference_links] : [],
        image_url: d.image_url ?? '',
        is_favorite: !!d.is_favorite
      })
    }
  } catch (e) {
    message.error('加载详情失败')
    showFormModal.value = false
  } finally {
    modalLoading.value = false
  }
}

async function handleSubmit() {
  modalLoading.value = true
  try {
    const data = {
      ...formValues,
      tips: formValues.tips?.filter(t => t && t.trim()) || [],
      warnings: formValues.warnings?.filter(w => w && w.trim()) || [],
      reference_links: formValues.reference_links?.filter(l => l && l.trim()) || []
    }
    if (isEdit.value) {
      await notesApi.update(editingId.value, data)
      message.success('更新成功')
    } else {
      await notesApi.create(data)
      message.success('创建成功')
    }
    showFormModal.value = false
    loadData()
  } catch (e) {
    message.error(isEdit.value ? '更新失败' : '创建失败')
  } finally {
    modalLoading.value = false
  }
}

async function handleDelete(item) {
  dialog.warning({
    title: '确认删除',
    content: `确定要删除笔记「${item.title}」吗？此操作不可撤销。`,
    positiveText: '删除',
    negativeText: '取消',
    positiveButtonProps: { type: 'error' },
    onPositiveClick: async () => {
      try {
        await notesApi.delete(item.id)
        message.success('删除成功')
        loadData()
      } catch (e) {
        message.error('删除失败')
      }
    }
  })
}

async function handleUpload({ file, onFinish, onError }) {
  uploadLoading.value = true
  try {
    const res = await uploadApi.uploadImage(file.file, 'notes')
    if (res?.data?.url || res?.data?.file_url || res?.data?.path) {
      formValues.image_url = res.data.url || res.data.file_url || res.data.path
      message.success('上传成功')
      onFinish()
    } else {
      throw new Error('上传失败')
    }
  } catch (e) {
    message.error('上传失败')
    onError()
  } finally {
    uploadLoading.value = false
  }
}

function openLink(url) {
  if (!url) return
  const href = url.startsWith('http') ? url : `https://${url}`
  window.open(href, '_blank')
}

onMounted(async () => {
  await loadOptions()
  await loadData()
})
</script>

<template>
  <div class="notes-wrapper">
    <div class="section-header">
      <div>
        <h2 class="page-title">
          <n-icon size="26" color="#D4A5A5"><BookOutline /></n-icon>
          制作手法笔记
        </h2>
        <p class="page-subtitle">记录每一次匠心独运的灵感，沉淀属于你的花艺智慧</p>
      </div>
      <div class="header-right">
        <span class="flower-icon flower-1">🌺</span>
        <n-button type="primary" size="large" @click="openCreate" class="btn-add">
          <template #icon>
            <n-icon :component="Add" />
          </template>
          记录笔记
        </n-button>
        <span class="flower-icon flower-2">🍃</span>
      </div>
    </div>

    <n-card class="filter-card" size="large" :bordered="false">
      <div class="filter-card-decor">
        <span class="decor-flower">❁</span>
      </div>
      <n-grid :cols="6" responsive="screen" :x-gap="14" :y-gap="14" style="align-items: flex-end;">
        <n-grid-item span="6 s:6 m:6 l:2">
          <n-form-item label="关键词" label-placement="left" label-align="left" class="form-inline-item">
            <n-input
              v-model:value="filters.keyword"
              placeholder="搜索标题/内容/标签..."
              clearable
              :input-props="{ autocomplete: 'off' }"
              @keyup.enter="onSearch"
            >
              <template #prefix>
                <n-icon :component="Search" />
              </template>
            </n-input>
          </n-form-item>
        </n-grid-item>
        <n-grid-item span="6 s:3 m:3 l:1">
          <n-form-item label="分类" label-placement="left" label-align="left" class="form-inline-item">
            <n-select
              v-model:value="filters.category"
              :options="categoryOptions"
              placeholder="全部分类"
              clearable
              filterable
            />
          </n-form-item>
        </n-grid-item>
        <n-grid-item span="6 s:3 m:3 l:1">
          <n-form-item label="难度" label-placement="left" label-align="left" class="form-inline-item">
            <n-select
              v-model:value="filters.difficulty"
              :options="difficultyOptions"
              placeholder="全部难度"
              clearable
            />
          </n-form-item>
        </n-grid-item>
        <n-grid-item span="6 s:6 m:6 l:1">
          <n-form-item label="收藏" label-placement="left" label-align="left" class="form-inline-item">
            <div class="switch-wrap">
              <n-switch
                v-model:value="filters.is_favorite"
                round
                size="medium"
                checked-color="#D4A5A5"
              />
              <span class="switch-label" :class="{ active: filters.is_favorite }">
                {{ filters.is_favorite ? '仅看收藏' : '全部笔记' }}
              </span>
            </div>
          </n-form-item>
        </n-grid-item>
        <n-grid-item span="6 s:6 m:6 l:1">
          <div class="filter-actions">
            <n-button type="primary" @click="onSearch" class="btn-search">
              <template #icon>
                <n-icon :component="Search" />
              </template>
              查询
            </n-button>
            <n-button @click="resetFilters" quaternary>
              <template #icon>
                <n-icon :component="Refresh" />
              </template>
              重置
            </n-button>
          </div>
        </n-grid-item>
      </n-grid>
    </n-card>

    <div class="list-section">
      <div v-if="loading" class="loading-wrap">
        <n-grid :cols="3" responsive="screen" :x-gap="18" :y-gap="18">
          <n-grid-item v-for="i in 6" :key="i" span="3 s:3 m:3 l:2 xl:2">
            <n-card class="note-card skeleton-card" size="large" :bordered="false">
              <div class="skeleton-header">
                <n-skeleton text :repeat="1" width="60px" />
                <n-skeleton circle size="28" />
              </div>
              <n-skeleton text style="margin-top: 12px;" :repeat="1" width="80%" />
              <n-skeleton text style="margin-top: 8px;" :repeat="3" />
              <n-skeleton text style="margin-top: 16px;" :repeat="1" width="40%" />
            </n-card>
          </n-grid-item>
        </n-grid>
      </div>
      <template v-else-if="dataList.length === 0">
        <n-card class="empty-card" :bordered="false">
          <n-empty description="暂无笔记，点击右上角记录下你的第一条灵感吧～">
            <template #extra>
              <n-button type="primary" @click="openCreate">
                <template #icon><n-icon :component="Add" /></template>
                记录笔记
              </n-button>
            </template>
          </n-empty>
        </n-card>
      </template>
      <n-grid v-else :cols="3" responsive="screen" :x-gap="18" :y-gap="18">
        <n-grid-item v-for="item in dataList" :key="item.id" span="3 s:3 m:3 l:2 xl:2">
          <n-card class="note-card" size="large" :bordered="false" hoverable>
            <div class="note-card-decor">
              <span class="note-flower">✿</span>
            </div>
            <div class="note-header">
              <n-tag
                v-if="item.difficulty"
                round
                size="small"
                :style="{
                  background: getDifficultyStyle(item.difficulty).bg,
                  color: getDifficultyStyle(item.difficulty).color,
                  boxShadow: getDifficultyStyle(item.difficulty).shadow,
                  border: 'none',
                  fontWeight: 600
                }"
              >
                {{ item.difficulty }}
              </n-tag>
              <n-button
                quaternary
                circle
                size="small"
                class="fav-btn"
                :class="{ active: item.is_favorite }"
                @click.stop="toggleFavorite(item)"
              >
                <n-icon :component="item.is_favorite ? Star : StarOutline" :size="18" />
              </n-button>
            </div>
            <h3 class="note-title">
              <n-ellipsis :line-clamp="2">{{ item.title }}</n-ellipsis>
            </h3>
            <div class="note-category" v-if="item.category">
              <n-tag
                round
                size="tiny"
                :style="{
                  background: getCategoryTagStyle(item.category).bg,
                  color: getCategoryTagStyle(item.category).color,
                  border: 'none'
                }"
              >
                <n-icon size="12" style="margin-right: 3px;"><BookmarkOutline /></n-icon>
                {{ item.category }}
              </n-tag>
            </div>
            <div class="note-content-preview">
              <div class="preview-text">{{ getContentPreview(item.content) }}</div>
              <div class="preview-mask"></div>
            </div>
            <div class="note-tips" v-if="item.tips && item.tips.length > 0">
              <n-space wrap :size="6">
                <n-tag
                  v-for="(tip, idx) in item.tips.slice(0, 3)"
                  :key="idx"
                  round
                  size="tiny"
                  class="tip-tag"
                >
                  <n-icon size="11" color="#8BA888"><BulbOutline /></n-icon>
                  {{ tip.length > 12 ? tip.substring(0, 12) + '...' : tip }}
                </n-tag>
                <n-tag
                  v-if="item.tips.length > 3"
                  round
                  size="tiny"
                  class="tip-tag"
                >
                  +{{ item.tips.length - 3 }}
                </n-tag>
              </n-space>
            </div>
            <div class="note-footer">
              <div class="footer-meta">
                <n-icon size="12" color="#B8A8A6"><DocumentTextOutline /></n-icon>
                <span>{{ item.content?.length || 0 }} 字</span>
              </div>
              <n-space :size="6">
                <n-button size="small" quaternary @click="openEdit(item)">
                  <template #icon><n-icon :component="CreateOutline" size="14" /></template>
                  编辑
                </n-button>
                <n-popconfirm @positive-click="handleDelete(item)">
                  <template #trigger>
                    <n-button size="small" quaternary type="error" style="color: #C08990;">
                      <template #icon><n-icon :component="TrashOutline" size="14" /></template>
                      删除
                    </n-button>
                  </template>
                  确认删除该笔记？
                </n-popconfirm>
                <n-button size="small" type="primary" class="btn-detail" @click="openDetail(item)">
                  <template #icon><n-icon :component="EyeOutline" size="14" /></template>
                  查看详情
                </n-button>
              </n-space>
            </div>
          </n-card>
        </n-grid-item>
      </n-grid>

      <div v-if="pagination.total > 0" class="pagination-wrap">
        <n-pagination
          v-model:page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :item-count="pagination.total"
          :page-sizes="[12, 24, 48, 96]"
          show-size-picker
          show-quick-jumper
          @update:page="handlePageChange"
          @update:page-size="handlePageSizeChange"
        />
      </div>
    </div>

    <n-modal
      v-model:show="showDetailModal"
      preset="card"
      title="笔记详情"
      :style="{ width: '800px', maxWidth: '94vw' }"
      :mask-closable="true"
      class="detail-modal"
      :scrollable="true"
    >
      <template v-if="currentDetail">
        <div class="detail-decor">
          <span class="detail-flower detail-flower-1">❀</span>
          <span class="detail-flower detail-flower-2">✿</span>
          <span class="detail-flower detail-flower-3">❁</span>
        </div>
        <div class="detail-header">
          <h2 class="detail-title">{{ currentDetail.title }}</h2>
          <div class="detail-tags">
            <n-tag
              v-if="currentDetail.difficulty"
              round
              size="medium"
              :style="{
                background: getDifficultyStyle(currentDetail.difficulty).bg,
                color: getDifficultyStyle(currentDetail.difficulty).color,
                boxShadow: getDifficultyStyle(currentDetail.difficulty).shadow,
                border: 'none',
                fontWeight: 600
              }"
            >
              {{ currentDetail.difficulty }}
            </n-tag>
            <n-tag
              v-if="currentDetail.category"
              round
              size="medium"
              :style="{
                background: getCategoryTagStyle(currentDetail.category).bg,
                color: getCategoryTagStyle(currentDetail.category).color,
                border: 'none'
              }"
            >
              <n-icon size="13" style="margin-right: 4px;"><BookmarkOutline /></n-icon>
              {{ currentDetail.category }}
            </n-tag>
            <n-button
              quaternary
              class="detail-fav-btn"
              :class="{ active: currentDetail.is_favorite }"
              @click="toggleFavorite(currentDetail)"
            >
              <n-icon :component="currentDetail.is_favorite ? Star : StarOutline" :size="16" />
              {{ currentDetail.is_favorite ? '已收藏' : '收藏' }}
            </n-button>
          </div>
        </div>

        <n-divider class="detail-divider" />

        <div class="detail-content">
          <div class="content-section">
            <div class="content-text" v-html="currentDetail.content"></div>
          </div>

          <n-image
            v-if="currentDetail.image_url"
            :src="currentDetail.image_url"
            class="detail-image"
            object-fit="cover"
            :preview-disabled="false"
          />

          <div v-if="currentDetail.tips && currentDetail.tips.length > 0" class="tips-card">
            <div class="tips-header">
              <n-icon size="20" color="#8BA888"><BulbOutline /></n-icon>
              <span>技巧提示 TIPS</span>
            </div>
            <ul class="tips-list">
              <li v-for="(tip, idx) in currentDetail.tips" :key="idx">
                <span class="tip-dot"></span>
                {{ tip }}
              </li>
            </ul>
          </div>

          <div v-if="currentDetail.warnings && currentDetail.warnings.length > 0" class="warnings-card">
            <div class="warnings-header">
              <n-icon size="20" color="#C08990"><AlertCircleOutline /></n-icon>
              <span>注意事项 WARNING</span>
            </div>
            <ul class="warnings-list">
              <li v-for="(warn, idx) in currentDetail.warnings" :key="idx">
                <span class="warn-dot"></span>
                {{ warn }}
              </li>
            </ul>
          </div>

          <div v-if="currentDetail.reference_links && currentDetail.reference_links.length > 0" class="references-section">
            <div class="references-header">
              <n-icon size="18" color="#8B7D7B"><LinkOutline /></n-icon>
              <span>参考链接</span>
            </div>
            <div class="references-list">
              <a
                v-for="(link, idx) in currentDetail.reference_links"
                :key="idx"
                class="reference-item"
                @click="openLink(link)"
              >
                <n-icon size="14" color="#D4A5A5"><LinkOutline /></n-icon>
                <span class="reference-text">{{ link }}</span>
              </a>
            </div>
          </div>
        </div>
      </template>
      <template #footer>
        <n-space justify="end">
          <n-button type="primary" @click="showDetailModal = false">关闭</n-button>
        </n-space>
      </template>
    </n-modal>

    <n-modal
      v-model:show="showFormModal"
      preset="card"
      :title="isEdit ? '编辑笔记' : '新建笔记'"
      :style="{ width: '720px', maxWidth: '94vw' }"
      :mask-closable="false"
      class="form-modal"
      :loading="modalLoading"
      :scrollable="true"
      positive-text="保存"
      negative-text="取消"
      @positive-click="handleSubmit"
      @negative-click="showFormModal = false"
    >
      <div class="modal-body-decor">
        <span class="modal-flower-1">🌸</span>
        <span class="modal-flower-2">🌿</span>
      </div>
      <n-form
        ref="formRef"
        :model="formValues"
        :rules="formRules"
        label-placement="left"
        label-align="left"
        label-width="100px"
        require-mark-placement="right-hanging"
        size="medium"
      >
        <n-grid :cols="2" responsive="screen" :x-gap="16" :y-gap="4">
          <n-grid-item span="2 s:2 m:2 l:2">
            <n-form-item label="标题" path="title">
              <n-input v-model:value="formValues.title" placeholder="请输入笔记标题" :input-props="{ autocomplete: 'off' }" />
            </n-form-item>
          </n-grid-item>
          <n-grid-item span="2 s:2 m:2 l:1">
            <n-form-item label="分类">
              <n-select
                v-model:value="formValues.category"
                :options="categoryOptions"
                placeholder="请选择分类"
                clearable
                filterable
              />
            </n-form-item>
          </n-grid-item>
          <n-grid-item span="2 s:2 m:2 l:1">
            <n-form-item label="难度">
              <n-select
                v-model:value="formValues.difficulty"
                :options="difficultyOptions"
                placeholder="请选择难度"
                clearable
              />
            </n-form-item>
          </n-grid-item>
          <n-grid-item span="2 s:2 m:2 l:2">
            <n-form-item label="内容" path="content">
              <n-input
                v-model:value="formValues.content"
                type="textarea"
                placeholder="详细记录制作手法、心得和细节..."
                :autosize="{ minRows: 8, maxRows: 12 }"
              />
            </n-form-item>
          </n-grid-item>
          <n-grid-item span="2 s:2 m:2 l:2">
            <n-form-item label="技巧提示">
              <n-dynamic-tags
                v-model:value="formValues.tips"
                placeholder="输入技巧提示后按回车添加"
                round
                size="medium"
              />
            </n-form-item>
          </n-grid-item>
          <n-grid-item span="2 s:2 m:2 l:2">
            <n-form-item label="注意事项">
              <n-dynamic-tags
                v-model:value="formValues.warnings"
                placeholder="输入注意事项后按回车添加"
                round
                size="medium"
              />
            </n-form-item>
          </n-grid-item>
          <n-grid-item span="2 s:2 m:2 l:2">
            <n-form-item label="参考链接">
              <n-dynamic-tags
                v-model:value="formValues.reference_links"
                placeholder="输入URL后按回车添加，如 https://..."
                round
                size="medium"
              />
            </n-form-item>
          </n-grid-item>
          <n-grid-item span="2 s:2 m:2 l:2">
            <n-form-item label="配图">
              <div class="upload-wrapper">
                <n-upload
                  :show-file-list="false"
                  :custom-request="handleUpload"
                  accept="image/*"
                  :disabled="uploadLoading"
                  class="upload-btn"
                >
                  <div class="upload-trigger" :class="{ hasImage: formValues.image_url }">
                    <img v-if="formValues.image_url" :src="formValues.image_url" class="upload-preview" />
                    <div v-else class="upload-placeholder">
                      <n-icon size="28" color="#D4B8B0"><CloudUploadOutline /></n-icon>
                      <span class="upload-text">{{ uploadLoading ? '上传中...' : '点击上传配图' }}</span>
                      <span class="upload-hint">支持 JPG、PNG 格式</span>
                    </div>
                  </div>
                </n-upload>
                <n-button
                  v-if="formValues.image_url"
                  text
                  size="tiny"
                  type="error"
                  style="margin-top: 8px;"
                  @click="formValues.image_url = ''"
                >
                  <template #icon>
                    <n-icon :component="Ban" size="12" />
                  </template>
                  移除图片
                </n-button>
              </div>
            </n-form-item>
          </n-grid-item>
          <n-grid-item span="2 s:2 m:2 l:2">
            <n-form-item label="收藏">
              <div class="switch-wrap">
                <n-switch
                  v-model:value="formValues.is_favorite"
                  round
                  size="medium"
                  checked-color="#D4A5A5"
                />
                <span class="switch-label" :class="{ active: formValues.is_favorite }">
                  {{ formValues.is_favorite ? '加入收藏' : '不收藏' }}
                </span>
              </div>
            </n-form-item>
          </n-grid-item>
        </n-grid>
      </n-form>
    </n-modal>
  </div>
</template>

<style lang="scss" scoped>
.notes-wrapper {
  background: transparent;
  padding-bottom: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 18px;
  border-bottom: 1px solid rgba(240, 230, 222, 0.6);
  position: relative;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  color: #5C4A4A;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 10px;
  letter-spacing: 1px;
}

.page-subtitle {
  font-size: 13px;
  color: #8B7D7B;
  margin: 8px 0 0;
  font-style: italic;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
  position: relative;
}

.flower-icon {
  font-size: 26px;
  opacity: 0.55;
  animation: float 4s ease-in-out infinite;

  &.flower-1 {
    animation-delay: 0s;
  }
  &.flower-2 {
    animation-delay: 0.8s;
    font-size: 20px;
  }
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-5px); }
}

.btn-add {
  background: linear-gradient(135deg, #D4A5A5, #C08990) !important;
  box-shadow: 0 4px 14px rgba(212, 165, 165, 0.4) !important;
  border: none !important;
  padding: 0 22px !important;
  height: 40px !important;
  font-weight: 600 !important;
  transition: all 0.3s ease !important;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(212, 165, 165, 0.5) !important;
  }
}

.filter-card {
  background: #FFFDF6;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(212, 165, 165, 0.1);
  border: 1px solid rgba(240, 230, 222, 0.8) !important;
  position: relative;
  margin-bottom: 22px;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 4px;
    height: 100%;
    background: linear-gradient(180deg, #D4A5A5, #F5E6A3);
    border-radius: 16px 0 0 16px;
    opacity: 0.5;
    z-index: 1;
  }
}

.filter-card-decor {
  position: absolute;
  top: 0;
  right: 0;
  pointer-events: none;
  overflow: hidden;
  z-index: 0;
}

.decor-flower {
  font-size: 56px;
  opacity: 0.05;
  color: #D4A5A5;
}

.filter-card :deep(.n-card__content) {
  position: relative;
  z-index: 1;
}

.form-inline-item {
  margin-bottom: 0 !important;
  width: 100%;

  :deep(.n-form-item-label) {
    font-size: 13px;
    color: #8B7D7B;
    font-weight: 500;
    padding-right: 8px;
  }
}

.switch-wrap {
  display: flex;
  align-items: center;
  gap: 10px;
  min-height: 34px;
}

.switch-label {
  font-size: 13px;
  color: #B8A8A6;
  transition: all 0.25s ease;

  &.active {
    color: #C08990;
    font-weight: 500;
  }
}

.filter-actions {
  display: flex;
  gap: 10px;
  min-height: 34px;
  align-items: center;
}

.btn-search {
  background: linear-gradient(135deg, #D4A5A5, #E8B4B8) !important;
  border: none !important;
  box-shadow: 0 3px 10px rgba(212, 165, 165, 0.3) !important;

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 5px 16px rgba(212, 165, 165, 0.4) !important;
  }
}

.list-section {
  position: relative;
}

.loading-wrap {
  padding: 10px 0;
}

.skeleton-card {
  background: #FFFDF6;
  border-radius: 16px;
  border: 1px solid rgba(240, 230, 222, 0.8) !important;
}

.skeleton-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.empty-card {
  background: #FFFDF6;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(212, 165, 165, 0.08);
  border: 1px solid rgba(240, 230, 222, 0.8) !important;
  padding: 30px;
}

.note-card {
  background: linear-gradient(145deg, #FFFDF6 0%, #FFFBF0 100%);
  border-radius: 18px;
  box-shadow: 0 4px 20px rgba(212, 165, 165, 0.1);
  border: 1px solid rgba(240, 230, 222, 0.8) !important;
  position: relative;
  overflow: hidden;
  height: 100%;
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 3px;
    background: linear-gradient(90deg, #D4A5A5, #F5E6A3, #A8C3A0);
    opacity: 0.6;
  }

  &:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 32px rgba(212, 165, 165, 0.22);
    border-color: rgba(212, 165, 165, 0.3) !important;
  }

  :deep(.n-card__content) {
    padding: 18px 18px 16px !important;
    height: 100%;
    display: flex;
    flex-direction: column;
  }
}

.note-card-decor {
  position: absolute;
  top: 12px;
  right: 12px;
  pointer-events: none;
  z-index: 0;
}

.note-flower {
  font-size: 40px;
  opacity: 0.04;
  color: #D4A5A5;
  transform: rotate(15deg);
}

.note-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  position: relative;
  z-index: 1;
}

.fav-btn {
  color: #B8A8A6;
  transition: all 0.25s ease;

  &:hover {
    color: #F5C86B !important;
    background: rgba(245, 200, 107, 0.1) !important;
  }

  &.active {
    color: #F5C86B !important;
    background: rgba(245, 200, 107, 0.15) !important;

    :deep(.n-icon) {
      animation: starPop 0.4s ease;
    }
  }
}

@keyframes starPop {
  0% { transform: scale(1); }
  50% { transform: scale(1.3); }
  100% { transform: scale(1); }
}

.note-title {
  font-size: 17px;
  font-weight: 700;
  color: #5C4A4A;
  line-height: 1.5;
  margin: 0 0 10px;
  position: relative;
  z-index: 1;
}

.note-category {
  margin-bottom: 12px;
  position: relative;
  z-index: 1;
}

.note-content-preview {
  position: relative;
  margin-bottom: 14px;
  flex: 1;
  z-index: 1;
}

.preview-text {
  font-size: 13px;
  color: #8B7D7B;
  line-height: 1.75;
  white-space: pre-wrap;
  max-height: 84px;
  overflow: hidden;
}

.preview-mask {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 30px;
  background: linear-gradient(180deg, transparent, #FFFBF0);
  pointer-events: none;
}

.note-tips {
  margin-bottom: 14px;
  position: relative;
  z-index: 1;
}

.tip-tag {
  background: rgba(168, 195, 160, 0.15) !important;
  color: #8BA888 !important;
  border: none !important;
  font-size: 11px !important;
}

.note-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px dashed rgba(240, 230, 222, 0.7);
  flex-wrap: wrap;
  gap: 10px;
  position: relative;
  z-index: 1;
}

.footer-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #B8A8A6;
}

.btn-detail {
  background: linear-gradient(135deg, #F5C86B, #E8B460) !important;
  border: none !important;
  box-shadow: 0 2px 8px rgba(245, 200, 107, 0.3) !important;

  &:hover {
    box-shadow: 0 4px 14px rgba(245, 200, 107, 0.4) !important;
  }
}

.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  padding-top: 24px;
  margin-top: 10px;
  border-top: 1px solid rgba(240, 230, 222, 0.5);

  :deep(.n-pagination) {
    --n-prefix-color: #8B7D7B;
    --n-item-text-color: #8B7D7B;
    --n-item-text-color-hover: #C08990;
    --n-item-color-active: #D4A5A5;
    --n-item-color-active-hover: #C08990;
    --n-border-color: rgba(240, 230, 222, 0.8);
    --n-border-color-hover: rgba(212, 165, 165, 0.4);
  }
}

.detail-modal {
  :deep(.n-card) {
    background: #FFFDF6;
    border-radius: 20px !important;
    overflow: hidden;
    border: 1px solid rgba(240, 230, 222, 0.8);
  }

  :deep(.n-card-header) {
    background: linear-gradient(135deg, rgba(212, 165, 165, 0.08), rgba(245, 230, 163, 0.1));
    border-bottom: 1px solid rgba(240, 230, 222, 0.6);
    position: relative;

    &::before {
      content: '📝';
      font-size: 18px;
      margin-right: 8px;
    }
  }

  :deep(.n-card-header__main) {
    font-size: 17px;
    font-weight: 700;
    color: #5C4A4A;
    display: flex;
    align-items: center;
  }

  :deep(.n-card-actions) {
    border-top: 1px solid rgba(240, 230, 222, 0.6);
    padding-top: 16px;
  }

  :deep(.n-button--primary-type) {
    background: linear-gradient(135deg, #D4A5A5, #C08990) !important;
    box-shadow: 0 3px 12px rgba(212, 165, 165, 0.35) !important;
    border: none !important;
  }
}

.detail-decor {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
  z-index: 0;
}

.detail-flower {
  position: absolute;
  opacity: 0.04;
  color: #D4A5A5;

  &.detail-flower-1 {
    font-size: 80px;
    top: 20px;
    right: -10px;
    transform: rotate(20deg);
  }

  &.detail-flower-2 {
    font-size: 60px;
    bottom: 40px;
    left: -5px;
    transform: rotate(-15deg);
    color: #F5E6A3;
  }

  &.detail-flower-3 {
    font-size: 50px;
    top: 50%;
    right: 20px;
    transform: rotate(35deg);
    color: #A8C3A0;
  }
}

.detail-header {
  position: relative;
  z-index: 1;
}

.detail-title {
  font-size: 22px;
  font-weight: 700;
  color: #5C4A4A;
  margin: 0 0 14px;
  line-height: 1.4;
}

.detail-tags {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.detail-fav-btn {
  color: #B8A8A6;
  border: 1px solid rgba(240, 230, 222, 0.8);
  background: #FFFDF6;

  &:hover {
    color: #F5C86B !important;
    border-color: rgba(245, 200, 107, 0.4) !important;
  }

  &.active {
    color: #F5C86B !important;
    background: rgba(245, 200, 107, 0.12) !important;
    border-color: rgba(245, 200, 107, 0.3) !important;
  }
}

.detail-divider {
  margin: 18px 0 !important;
  border-color: rgba(240, 230, 222, 0.6) !important;
}

.detail-content {
  position: relative;
  z-index: 1;
}

.content-section {
  margin-bottom: 20px;
}

.content-text {
  font-size: 14px;
  color: #5C4A4A;
  line-height: 1.9;
  white-space: pre-wrap;
  word-break: break-word;
}

.detail-image {
  width: 100%;
  border-radius: 14px;
  margin-bottom: 20px;
  max-height: 320px;
  border: 1px solid rgba(240, 230, 222, 0.7);
  box-shadow: 0 4px 18px rgba(212, 165, 165, 0.12);
}

.tips-card {
  background: linear-gradient(135deg, rgba(168, 195, 160, 0.12), rgba(139, 168, 136, 0.08));
  border: 1px solid rgba(168, 195, 160, 0.3);
  border-radius: 14px;
  padding: 16px 18px;
  margin-bottom: 16px;
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 4px;
    height: 100%;
    background: linear-gradient(180deg, #A8C3A0, #8BA888);
    border-radius: 14px 0 0 14px;
    opacity: 0.7;
  }
}

.tips-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 700;
  color: #8BA888;
  margin-bottom: 12px;
}

.tips-list {
  list-style: none;
  margin: 0;
  padding: 0 0 0 6px;

  li {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 6px 0;
    font-size: 13px;
    color: #5C4A4A;
    line-height: 1.7;
  }
}

.tip-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #8BA888;
  margin-top: 8px;
  flex-shrink: 0;
}

.warnings-card {
  background: linear-gradient(135deg, rgba(232, 180, 184, 0.14), rgba(192, 137, 144, 0.08));
  border: 1px solid rgba(232, 180, 184, 0.35);
  border-radius: 14px;
  padding: 16px 18px;
  margin-bottom: 16px;
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 4px;
    height: 100%;
    background: linear-gradient(180deg, #E8B4B8, #C08990);
    border-radius: 14px 0 0 14px;
    opacity: 0.7;
  }
}

.warnings-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 700;
  color: #C08990;
  margin-bottom: 12px;
}

.warnings-list {
  list-style: none;
  margin: 0;
  padding: 0 0 0 6px;

  li {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 6px 0;
    font-size: 13px;
    color: #5C4A4A;
    line-height: 1.7;
  }
}

.warn-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #C08990;
  margin-top: 8px;
  flex-shrink: 0;
}

.references-section {
  margin-bottom: 8px;
}

.references-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #8B7D7B;
  margin-bottom: 10px;
}

.references-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.reference-item {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  background: rgba(212, 165, 165, 0.08);
  border: 1px solid rgba(212, 165, 165, 0.2);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.25s ease;
  width: fit-content;

  &:hover {
    background: rgba(212, 165, 165, 0.15);
    border-color: rgba(212, 165, 165, 0.35);
    transform: translateX(3px);
  }
}

.reference-text {
  font-size: 13px;
  color: #C08990;
  text-decoration: none;
  word-break: break-all;
  max-width: 560px;
}

.form-modal {
  :deep(.n-card) {
    background: #FFFDF6;
    border-radius: 18px !important;
    overflow: hidden;
  }

  :deep(.n-card-header) {
    background: linear-gradient(135deg, rgba(212, 165, 165, 0.08), rgba(245, 230, 163, 0.1));
    border-bottom: 1px solid rgba(240, 230, 222, 0.6);
    position: relative;
  }

  :deep(.n-card-header__main) {
    font-size: 17px;
    font-weight: 700;
    color: #5C4A4A;
    display: flex;
    align-items: center;
    gap: 8px;

    &::before {
      content: '🌸';
      font-size: 18px;
    }
  }

  :deep(.n-card-actions) {
    border-top: 1px solid rgba(240, 230, 222, 0.6);
    padding-top: 16px;
  }

  :deep(.n-button--primary-type) {
    background: linear-gradient(135deg, #D4A5A5, #C08990) !important;
    box-shadow: 0 3px 12px rgba(212, 165, 165, 0.35) !important;
    border: none !important;

    &:hover {
      transform: translateY(-1px);
      box-shadow: 0 5px 18px rgba(212, 165, 165, 0.45) !important;
    }
  }

  :deep(.n-form-item-label) {
    font-size: 13px;
    color: #8B7D7B;
    font-weight: 500;
  }

  :deep(.n-form-item) {
    margin-bottom: 10px;
  }
}

.modal-body-decor {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
  z-index: 0;
}

.modal-flower-1,
.modal-flower-2 {
  position: absolute;
  font-size: 70px;
  opacity: 0.04;
  color: #D4A5A5;
}

.modal-flower-1 {
  top: 30px;
  right: -10px;
  transform: rotate(15deg);
}

.modal-flower-2 {
  bottom: -20px;
  left: -15px;
  font-size: 90px;
  color: #F5E6A3;
  transform: rotate(-25deg);
}

.upload-wrapper {
  width: 100%;
}

.upload-trigger {
  width: 100%;
  min-height: 130px;
  border: 2px dashed rgba(212, 165, 165, 0.35);
  border-radius: 14px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  background: linear-gradient(135deg, rgba(250, 246, 238, 0.8), rgba(255, 253, 246, 1));

  &:hover {
    border-color: rgba(212, 165, 165, 0.6);
    background: linear-gradient(135deg, rgba(250, 246, 238, 1), rgba(255, 248, 238, 1));

    .upload-text {
      color: #C08990;
    }
  }

  &.hasImage {
    border-style: solid;
    border-color: rgba(212, 165, 165, 0.2);
    min-height: 160px;
  }
}

.upload-placeholder {
  width: 100%;
  min-height: 130px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 20px;
}

.upload-text {
  font-size: 13px;
  color: #8B7D7B;
  font-weight: 500;
  transition: color 0.25s ease;
}

.upload-hint {
  font-size: 11px;
  color: #B8A8A6;
}

.upload-preview {
  width: 100%;
  height: 160px;
  object-fit: contain;
  background: rgba(250, 246, 238, 0.6);
  display: block;
}

.upload-btn {
  width: 100%;
}
</style>
