<script setup>
import { ref, onMounted, computed, h, reactive } from 'vue'
import { useRouter } from 'vue-router'
import {
  NCard, NGrid, NGridItem, NTag, NIcon, NSpace, NButton, NTabs, NTabPane,
  NInput, NInputNumber, NSelect, NSwitch, NDataTable, NModal, NForm, NFormItem,
  NDatePicker, NUpload, NUploadDragger, NImage, NEllipsis, NDynamicTags,
  useMessage, useDialog, NEmpty, NPagination, NSkeleton
} from 'naive-ui'
import {
  FlowerOutline, Add, Search, Heart, Eye, TrashOutline,
  CreateOutline, EyeOutline, ShareSocialOutline, Sparkles,
  Close, LocationOutline, ImagesOutline, CheckmarkCircleOutline
} from '@vicons/ionicons5'
import { specimensApi, uploadApi, shareApi, dryingApi } from '@/api'
import ImageUploader from '@/components/ImageUploader.vue'

const router = useRouter()
const message = useMessage()
const dialog = useDialog()

const loading = ref(false)
const list = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(12)

const viewMode = ref('card')
const keyword = ref('')
const filterCategory = ref(null)
const filterFrameStyle = ref(null)
const filterStatus = ref(null)
const filterFeatured = ref(null)
const filterShared = ref(null)

const categoryOptions = ref([])
const statusOptions = ref([])
const frameStyleOptions = ref([])
const dryingOptions = ref([])

const showFormModal = ref(false)
const formMode = ref('create')
const formRef = ref(null)
const formData = reactive({
  id: null,
  name: '',
  category: null,
  drying_process_id: null,
  display_code: '',
  production_date: null,
  shelf_life_months: null,
  preservation_method: '',
  frame_size: '',
  frame_style: null,
  description: '',
  tags: [],
  image_url: '',
  gallery_images: [],
  is_featured: false,
  is_shared: false,
  location: '',
  status: '完好'
})

const formRules = {
  name: { required: true, message: '请输入标本名称', trigger: 'blur' }
}



const showShareModal = ref(false)
const shareFormRef = ref(null)
const shareTarget = ref(null)
const shareForm = reactive({
  title: '',
  content: '',
  author: '花艺爱好者'
})

const shareRules = {
  title: { required: true, message: '请输入分享标题', trigger: 'blur' }
}

const showDetailModal = ref(false)
const detailData = ref(null)

const categoryTagColors = {
  '单枝': { bg: 'rgba(212,165,165,0.18)', text: '#C08990' },
  '花束': { bg: 'rgba(232,180,184,0.22)', text: '#C08990' },
  '压花': { bg: 'rgba(245,230,163,0.22)', text: '#C49B3A' },
  '香薰': { bg: 'rgba(168,195,160,0.18)', text: '#8BA888' },
  '摆件': { bg: 'rgba(184,200,212,0.2)', text: '#8BA8C3' },
  '礼盒': { bg: 'rgba(212,160,107,0.2)', text: '#C49050' },
  '其他': { bg: 'rgba(184,168,166,0.2)', text: '#8B7D7B' }
}

const statusTagColors = {
  '完好': { bg: 'rgba(168,195,160,0.2)', text: '#8BA888' },
  '微损': { bg: 'rgba(245,200,107,0.22)', text: '#C49B3A' },
  '已赠出': { bg: 'rgba(184,200,212,0.22)', text: '#8BA8C3' },
  '售出': { bg: 'rgba(184,168,166,0.2)', text: '#8B7D7B' }
}

function getCategoryColor(cat) {
  return categoryTagColors[cat] || categoryTagColors['其他']
}

function getStatusColor(status) {
  return statusTagColors[status] || statusTagColors['完好']
}

async function loadOptions() {
  try {
    const [catRes, statusRes, frameRes] = await Promise.all([
      specimensApi.categories(),
      specimensApi.statuses(),
      specimensApi.frameStyles()
    ])
    if (catRes?.data?.categories) {
      categoryOptions.value = catRes.data.categories.map(c => ({ label: c, value: c }))
    }
    if (statusRes?.data?.statuses) {
      statusOptions.value = statusRes.data.statuses.map(s => ({ label: s, value: s }))
    }
    if (frameRes?.data?.frame_styles) {
      frameStyleOptions.value = frameRes.data.frame_styles.map(f => ({ label: f, value: f }))
    }
  } catch (e) {
    message.error('加载选项失败')
  }
}

async function loadDryingOptions() {
  try {
    const res = await dryingApi.list({ page: 1, page_size: 100 })
    const items = res?.data?.items || res?.data || []
    dryingOptions.value = items.map(d => ({
      label: `${d.process_name}${d.material?.name ? ' · ' + d.material.name : ''}`,
      value: d.id
    }))
  } catch (e) {
  }
}

async function loadList() {
  loading.value = true
  try {
    const params = {
      page: page.value,
      page_size: pageSize.value
    }
    if (keyword.value) params.keyword = keyword.value
    if (filterCategory.value) params.category = filterCategory.value
    if (filterFrameStyle.value) params.frame_style = filterFrameStyle.value
    if (filterStatus.value) params.status = filterStatus.value
    if (filterFeatured.value !== null && filterFeatured.value !== undefined) {
      params.is_featured = filterFeatured.value
    }
    if (filterShared.value !== null && filterShared.value !== undefined) {
      params.is_shared = filterShared.value
    }
    const res = await specimensApi.list(params)
    if (res?.data?.items) {
      list.value = res.data.items
      total.value = res.data.total || 0
    } else if (res?.data) {
      list.value = Array.isArray(res.data) ? res.data : []
      total.value = list.value.length
    }
  } catch (e) {
    message.error('加载标本列表失败')
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  page.value = 1
  loadList()
}

function handleFilterChange() {
  page.value = 1
  loadList()
}

function handlePageChange(p) {
  page.value = p
  loadList()
}

function handlePageSizeChange(ps) {
  pageSize.value = ps
  page.value = 1
  loadList()
}

function openCreate() {
  formMode.value = 'create'
  Object.assign(formData, {
    id: null,
    name: '',
    category: null,
    drying_process_id: null,
    display_code: '',
    production_date: null,
    shelf_life_months: null,
    preservation_method: '',
    frame_size: '',
    frame_style: null,
    description: '',
    tags: [],
    image_url: '',
    gallery_images: [],
    is_featured: false,
    is_shared: false,
    location: '',
    status: '完好'
  })
  loadDryingOptions()
  showFormModal.value = true
}

async function openEdit(item) {
  formMode.value = 'edit'
  Object.assign(formData, {
    id: item.id,
    name: item.name || '',
    category: item.category || null,
    drying_process_id: item.drying_process_id || null,
    display_code: item.display_code || '',
    production_date: item.production_date || null,
    shelf_life_months: item.shelf_life_months || null,
    preservation_method: item.preservation_method || '',
    frame_size: item.frame_size || '',
    frame_style: item.frame_style || null,
    description: item.description || '',
    tags: item.tags || [],
    image_url: item.image_url || '',
    gallery_images: item.gallery_images || [],
    is_featured: item.is_featured || false,
    is_shared: item.is_shared || false,
    location: item.location || '',
    status: item.status || '完好'
  })
  await loadDryingOptions()
  showFormModal.value = true
}

function handleFormSubmit() {
  formRef.value?.validate(async (errors) => {
    if (errors) return
    try {
      const payload = { ...formData }
      delete payload.id
      if (formMode.value === 'create') {
        await specimensApi.create(payload)
        message.success('标本创建成功')
      } else {
        await specimensApi.update(formData.id, payload)
        message.success('标本更新成功')
      }
      showFormModal.value = false
      loadList()
    } catch (e) {
      message.error(formMode.value === 'create' ? '创建失败' : '更新失败')
    }
  })
}

function handleDelete(item) {
  dialog.warning({
    title: '确认删除',
    content: `确定要删除标本「${item.name}」吗？此操作不可恢复。`,
    positiveText: '删除',
    negativeText: '取消',
    positiveButtonProps: { color: '#E88A9A' },
    onPositiveClick: async () => {
      try {
        await specimensApi.delete(item.id)
        message.success('删除成功')
        loadList()
      } catch (e) {
        message.error('删除失败')
      }
    }
  })
}

async function handleLike(item) {
  try {
    const res = await specimensApi.like(item.id)
    if (res?.data?.like_count !== undefined) {
      item.like_count = res.data.like_count
    }
    message.success('点赞成功')
  } catch (e) {
    message.error('点赞失败')
  }
}

async function openDetail(item) {
  try {
    const res = await specimensApi.get(item.id)
    if (res?.data) {
      detailData.value = res.data
      showDetailModal.value = true
    }
  } catch (e) {
    message.info('详情页开发中，敬请期待')
  }
}

function openShare(item) {
  shareTarget.value = item
  shareForm.title = item.name || ''
  shareForm.content = item.description || ''
  shareForm.author = '花艺爱好者'
  showShareModal.value = true
}

function handleShareSubmit() {
  shareFormRef.value?.validate(async (errors) => {
    if (errors) return
    try {
      const payload = {
        specimen_id: shareTarget.value.id,
        title: shareForm.title,
        content: shareForm.content,
        author: shareForm.author,
        is_published: true,
        tags: shareTarget.value.tags || []
      }
      await shareApi.create(payload)
      message.success('分享成功，已发布到广场')
      showShareModal.value = false
      loadList()
    } catch (e) {
      message.error('分享失败')
    }
  })
}



const tableColumns = computed(() => [
  {
    title: '图',
    key: 'image',
    width: 90,
    render: (row) => h('div', {
      style: 'width: 60px; height: 60px; border-radius: 10px; overflow: hidden; background: linear-gradient(135deg, #FAF6EE, #F5EEE8); display: flex; align-items: center; justify-content: center;'
    }, [
      row.image_url
        ? h('img', {
            src: row.image_url,
            style: 'width: 100%; height: 100%; object-fit: cover;'
          })
        : h(NIcon, { size: 22, color: '#D4B8B0' }, { default: () => h(FlowerOutline) })
    ])
  },
  {
    title: '名称',
    key: 'name',
    minWidth: 140,
    render: (row) => h('div', { style: 'font-weight: 600; color: #5C4A4A;' }, row.name || '-')
  },
  {
    title: '编号',
    key: 'display_code',
    width: 130,
    render: (row) => h('span', { style: 'color: #8B7D7B; font-size: 12px; font-family: monospace;' }, row.display_code || '-')
  },
  {
    title: '分类',
    key: 'category',
    width: 90,
    render: (row) => {
      if (!row.category) return h('span', { style: 'color: #B8A8A6;' }, '-')
      const c = getCategoryColor(row.category)
      return h(NTag, { round: true, size: 'small', style: { background: c.bg, color: c.text, border: 'none' } }, { default: () => row.category })
    }
  },
  {
    title: '装裱',
    key: 'frame_style',
    width: 110,
    render: (row) => h('span', { style: 'color: #8B7D7B; font-size: 13px;' }, row.frame_style || row.frame_size || '-')
  },
  {
    title: '位置',
    key: 'location',
    width: 110,
    render: (row) => {
      if (!row.location) return h('span', { style: 'color: #B8A8A6;' }, '-')
      return h(NSpace, { size: 4, align: 'center' }, {
        default: () => [
          h(NIcon, { size: 13, color: '#B8A8A6' }, { default: () => h(LocationOutline) }),
          h('span', { style: 'color: #8B7D7B; font-size: 13px;' }, row.location)
        ]
      })
    }
  },
  {
    title: '状态',
    key: 'status',
    width: 90,
    render: (row) => {
      if (!row.status) return h('span', { style: 'color: #B8A8A6;' }, '-' )
      const c = getStatusColor(row.status)
      return h(NTag, { round: true, size: 'small', style: { background: c.bg, color: c.text, border: 'none' } }, { default: () => row.status })
    }
  },
  {
    title: '点赞/浏览',
    key: 'stats',
    width: 110,
    render: (row) => h(NSpace, { size: 12, align: 'center' }, {
      default: () => [
        h(NSpace, { size: 4, align: 'center' }, {
          default: () => [
            h(NIcon, { size: 13, color: '#E88A9A' }, { default: () => h(Heart) }),
            h('span', { style: 'color: #8B7D7B; font-size: 12px;' }, row.like_count ?? 0)
          ]
        }),
        h(NSpace, { size: 4, align: 'center' }, {
          default: () => [
            h(NIcon, { size: 13, color: '#8BA8C3' }, { default: () => h(Eye) }),
            h('span', { style: 'color: #8B7D7B; font-size: 12px;' }, row.view_count ?? 0)
          ]
        })
      ]
    })
  },
  {
    title: '操作',
    key: 'actions',
    width: 200,
    render: (row) => h(NSpace, { size: 6 }, {
      default: () => [
        h(NButton, {
          text: true, size: 'small', type: 'info', onClick: () => openDetail(row)
        }, { default: () => '查看' }),
        h(NButton, {
          text: true, size: 'small', type: 'primary', onClick: () => openEdit(row)
        }, { default: () => '编辑' }),
        h(NButton, {
          text: true, size: 'small', type: 'success', onClick: () => openShare(row)
        }, { default: () => '分享' }),
        h(NButton, {
          text: true, size: 'small', type: 'error', onClick: () => handleDelete(row)
        }, { default: () => '删除' })
      ]
    })
  }
])

onMounted(() => {
  loadOptions()
  loadList()
})
</script>

<template>
  <div class="specimens-wrapper">
    <div class="section-header">
      <div>
        <h2 class="page-title">
          <n-icon size="26" color="#D4A5A5"><FlowerOutline /></n-icon>
          成品标本陈列
        </h2>
        <p class="page-subtitle">收纳每一份精心制作的标本，记录时光凝固的永恒之美</p>
      </div>
      <n-button type="primary" size="large" :loading="loading" @click="openCreate">
        <template #icon><n-icon :component="Add" /></template>
        新增标本
      </n-button>
    </div>

    <n-card class="filter-card" size="large" :bordered="false">
      <n-space vertical :size="16" style="width: 100%;">
        <div class="filter-row-top">
          <div class="filter-search-wrap">
            <n-input
              v-model:value="keyword"
              placeholder="搜索名称、编号、描述..."
              clearable
              size="large"
              style="width: 280px;"
              @keyup.enter="handleSearch"
            >
              <template #prefix><n-icon :component="Search" /></template>
            </n-input>
          </div>
          <n-space :size="12" wrap>
            <n-select
              v-model:value="filterCategory"
              placeholder="分类"
              :options="categoryOptions"
              clearable
              size="medium"
              style="width: 130px;"
              @update:value="handleFilterChange"
            />
            <n-select
              v-model:value="filterFrameStyle"
              placeholder="装裱风格"
              :options="frameStyleOptions"
              clearable
              size="medium"
              style="width: 140px;"
              @update:value="handleFilterChange"
            />
            <n-select
              v-model:value="filterStatus"
              placeholder="状态"
              :options="statusOptions"
              clearable
              size="medium"
              style="width: 120px;"
              @update:value="handleFilterChange"
            />
            <div class="filter-switch-item">
              <span class="filter-switch-label">精选</span>
              <n-switch v-model:value="filterFeatured" @update:value="handleFilterChange" />
            </div>
            <div class="filter-switch-item">
              <span class="filter-switch-label">已分享</span>
              <n-switch v-model:value="filterShared" @update:value="handleFilterChange" />
            </div>
          </n-space>
        </div>
        <n-tabs v-model:value="viewMode" type="line" size="medium" class="view-tabs">
          <n-tab-pane name="card" tab="卡片视图" />
          <n-tab-pane name="table" tab="表格视图" />
        </n-tabs>
      </n-space>
    </n-card>

    <div v-if="loading" class="list-loading">
      <n-skeleton :repeat="4" text :row="3" style="max-width: 800px; margin: 0 auto;" />
    </div>

    <div v-else-if="list.length === 0" class="empty-state">
      <n-empty description="暂无标本，点击右上角新增第一个标本吧" :show-icon="false">
        <template #image>
          <div class="empty-icon-wrap">
            <span class="empty-emoji">🌸</span>
            <span class="empty-emoji empty-emoji-2">🌿</span>
          </div>
        </template>
        <n-button type="primary" @click="openCreate">
          <template #icon><n-icon :component="Add" /></template>
          新增标本
        </n-button>
      </n-empty>
    </div>

    <template v-else>
      <div v-show="viewMode === 'card'" class="card-section">
        <n-grid :cols="4" responsive="screen" :x-gap="16" :y-gap="16">
          <n-grid-item v-for="item in list" :key="item.id" span="4 s:2 m:2 l:2 xl:1">
            <div class="specimen-card">
              <div class="specimen-image-wrap">
                <img
                  v-if="item.image_url"
                  :src="item.image_url"
                  :alt="item.name"
                  class="specimen-image"
                />
                <div v-else class="specimen-image-placeholder">
                  <n-icon :component="FlowerOutline" size="40" color="#D4B8B0" />
                </div>
                <div class="specimen-overlay">
                  <div class="overlay-code" v-if="item.display_code">{{ item.display_code }}</div>
                  <n-ellipsis :line-clamp="2" class="overlay-desc">
                    {{ item.description || '暂无描述' }}
                  </n-ellipsis>
                </div>
                <div v-if="item.is_featured" class="specimen-badge-featured">
                  <n-icon size="12" style="margin-right: 2px;"><Sparkles /></n-icon>
                  精选
                </div>
              </div>
              <div class="specimen-body">
                <div class="specimen-name-row">
                  <div class="specimen-name">
                    <n-ellipsis :line-clamp="1">{{ item.name }}</n-ellipsis>
                  </div>
                </div>
                <div class="specimen-category-row" v-if="item.category">
                  <n-tag
                    round
                    size="tiny"
                    :style="{ background: getCategoryColor(item.category).bg, color: getCategoryColor(item.category).text, border: 'none' }"
                  >
                    {{ item.category }}
                  </n-tag>
                </div>
                <div class="specimen-meta-line">
                  <span v-if="item.frame_style" class="meta-pill">
                    <n-icon size="11" color="#B8A8A6"><ImagesOutline /></n-icon>
                    {{ item.frame_style }}
                  </span>
                  <span v-if="item.location" class="meta-pill">
                    <n-icon size="11" color="#B8A8A6"><LocationOutline /></n-icon>
                    {{ item.location }}
                  </span>
                </div>
                <div class="specimen-stats-line">
                  <span class="stat-btn" @click.stop="handleLike(item)">
                    <n-icon size="14" color="#E88A9A"><Heart /></n-icon>
                    <span>{{ item.like_count ?? 0 }}</span>
                  </span>
                  <span class="stat-item">
                    <n-icon size="14" color="#8BA8C3"><Eye /></n-icon>
                    <span>{{ item.view_count ?? 0 }}</span>
                  </span>
                </div>
                <div class="specimen-footer">
                  <n-tag
                    v-if="item.status"
                    round
                    size="tiny"
                    :style="{ background: getStatusColor(item.status).bg, color: getStatusColor(item.status).text, border: 'none' }"
                  >
                    {{ item.status }}
                  </n-tag>
                  <div class="action-btns">
                    <n-button quaternary size="tiny" @click="openDetail(item)">
                      <template #icon><n-icon :component="EyeOutline" /></template>
                    </n-button>
                    <n-button quaternary size="tiny" @click="openEdit(item)">
                      <template #icon><n-icon :component="CreateOutline" /></template>
                    </n-button>
                    <n-button quaternary size="tiny" @click="openShare(item)">
                      <template #icon><n-icon :component="ShareSocialOutline" /></template>
                    </n-button>
                    <n-button quaternary size="tiny" @click="handleDelete(item)">
                      <template #icon><n-icon :component="TrashOutline" /></template>
                    </n-button>
                  </div>
                </div>
              </div>
            </div>
          </n-grid-item>
        </n-grid>
      </div>

      <n-card v-show="viewMode === 'table'" class="table-card" size="large" :bordered="false">
        <n-data-table
          :columns="tableColumns"
          :data="list"
          :bordered="false"
          size="medium"
          :pagination="false"
          style="background: transparent;"
        />
      </n-card>

      <div class="pagination-wrap">
        <n-pagination
          v-model:page="page"
          v-model:page-size="pageSize"
          :item-count="total"
          :page-sizes="[8, 12, 20, 40]"
          show-size-picker
          show-quick-jumper
          @update:page="handlePageChange"
          @update:page-size="handlePageSizeChange"
        />
      </div>
    </template>

    <n-modal
      v-model:show="showFormModal"
      preset="card"
      :title="formMode === 'create' ? '新增标本' : '编辑标本'"
      style="width: 720px; max-width: 92vw;"
      :mask-closable="false"
      class="form-modal"
    >
      <n-form ref="formRef" :model="formData" :rules="formRules" label-placement="left" label-width="100px">
        <n-grid :cols="2" :x-gap="16" :y-gap="4">
          <n-grid-item span="2 s:2 m:1">
            <n-form-item label="名称" path="name">
              <n-input v-model:value="formData.name" placeholder="请输入标本名称" maxlength="100" />
            </n-form-item>
          </n-grid-item>
          <n-grid-item span="2 s:2 m:1">
            <n-form-item label="分类">
              <n-select v-model:value="formData.category" :options="categoryOptions" placeholder="选择分类" clearable />
            </n-form-item>
          </n-grid-item>
          <n-grid-item span="2 s:2 m:1">
            <n-form-item label="关联制作">
              <n-select
                v-model:value="formData.drying_process_id"
                :options="dryingOptions"
                placeholder="关联脱水制作记录"
                clearable
                filterable
              />
            </n-form-item>
          </n-grid-item>
          <n-grid-item span="2 s:2 m:1">
            <n-form-item label="陈列编号">
              <n-input v-model:value="formData.display_code" placeholder="留空自动生成" maxlength="50" />
            </n-form-item>
          </n-grid-item>
          <n-grid-item span="2 s:2 m:1">
            <n-form-item label="制作日期">
              <n-date-picker v-model:value="formData.production_date" type="date" placeholder="选择日期" style="width: 100%;" />
            </n-form-item>
          </n-grid-item>
          <n-grid-item span="2 s:2 m:1">
            <n-form-item label="保存期限">
              <n-input-number v-model:value="formData.shelf_life_months" placeholder="月" :min="0" style="width: 100%;">
                <template #suffix>个月</template>
              </n-input-number>
            </n-form-item>
          </n-grid-item>
          <n-grid-item span="2 s:2 m:1">
            <n-form-item label="保存方式">
              <n-input v-model:value="formData.preservation_method" placeholder="如：避光、干燥密封..." maxlength="100" />
            </n-form-item>
          </n-grid-item>
          <n-grid-item span="2 s:2 m:1">
            <n-form-item label="装裱尺寸">
              <n-input v-model:value="formData.frame_size" placeholder="如：A4、30x40cm..." maxlength="50" />
            </n-form-item>
          </n-grid-item>
          <n-grid-item span="2 s:2 m:1">
            <n-form-item label="装裱风格">
              <n-select v-model:value="formData.frame_style" :options="frameStyleOptions" placeholder="选择风格" clearable />
            </n-form-item>
          </n-grid-item>
          <n-grid-item span="2 s:2 m:1">
            <n-form-item label="存放位置">
              <n-input v-model:value="formData.location" placeholder="如：客厅陈列柜第二层..." maxlength="100" />
            </n-form-item>
          </n-grid-item>
          <n-grid-item span="2 s:2 m:1">
            <n-form-item label="状态">
              <n-select v-model:value="formData.status" :options="statusOptions" placeholder="选择状态" clearable />
            </n-form-item>
          </n-grid-item>
        </n-grid>
        <n-form-item label="作品描述" label-placement="top" style="margin-top: 4px;">
          <n-input v-model:value="formData.description" type="textarea" :rows="3" placeholder="记录这件作品的故事..." maxlength="1000" />
        </n-form-item>
        <n-form-item label="标签" label-placement="top">
          <n-dynamic-tags v-model:value="formData.tags" closable round placeholder="输入标签后回车添加" input-style="width: 100%;" />
        </n-form-item>
        <n-form-item label="主图" label-placement="top">
          <ImageUploader
            v-model="formData.image_url"
            folder="specimens"
            :max-count="1"
            :compress="true"
            :multiple="false"
          />
        </n-form-item>
        <n-form-item label="图集" label-placement="top">
          <ImageUploader
            v-model="formData.gallery_images"
            folder="specimens"
            :max-count="9"
            :compress="true"
          />
        </n-form-item>
        <n-grid :cols="2" :x-gap="16" style="margin-top: 12px;">
          <n-grid-item span="2 s:2 m:1">
            <n-form-item label="是否精选" label-placement="left" label-width="100px">
              <n-switch v-model:value="formData.is_featured" />
            </n-form-item>
          </n-grid-item>
          <n-grid-item span="2 s:2 m:1">
            <n-form-item label="是否分享" label-placement="left" label-width="100px">
              <n-switch v-model:value="formData.is_shared" />
            </n-form-item>
          </n-grid-item>
        </n-grid>
      </n-form>
      <template #footer>
        <NSpace justify="end">
          <n-button @click="showFormModal = false">取消</n-button>
          <n-button type="primary" @click="handleFormSubmit">
            <template #icon><n-icon :component="CheckmarkCircleOutline" /></template>
            {{ formMode === 'create' ? '创建' : '保存' }}
          </n-button>
        </NSpace>
      </template>
    </n-modal>

    <n-modal
      v-model:show="showShareModal"
      preset="card"
      title="分享到广场"
      style="width: 520px; max-width: 92vw;"
      :mask-closable="false"
      class="share-modal"
    >
      <n-form ref="shareFormRef" :model="shareForm" :rules="shareRules" label-placement="top">
        <n-form-item label="分享标题" path="title">
          <n-input v-model:value="shareForm.title" placeholder="给分享取个吸引眼球的标题" maxlength="100" />
        </n-form-item>
        <n-form-item label="分享内容">
          <n-input v-model:value="shareForm.content" type="textarea" :rows="5" placeholder="讲讲这件作品的故事、灵感、制作心得..." maxlength="2000" />
        </n-form-item>
        <n-form-item label="作者署名">
          <n-input v-model:value="shareForm.author" placeholder="你的名字或昵称" maxlength="50" />
        </n-form-item>
        <div v-if="shareTarget?.image_url" class="share-preview">
          <div class="share-preview-label">预览图</div>
          <img :src="shareTarget.image_url" class="share-preview-img" />
        </div>
      </n-form>
      <template #footer>
        <NSpace justify="end">
          <n-button @click="showShareModal = false">取消</n-button>
          <n-button type="primary" @click="handleShareSubmit">
            <template #icon><n-icon :component="ShareSocialOutline" /></template>
            发布到广场
          </n-button>
        </NSpace>
      </template>
    </n-modal>

    <n-modal
      v-model:show="showDetailModal"
      preset="card"
      :title="detailData?.name || '标本详情'"
      style="width: 640px; max-width: 92vw;"
      class="detail-modal"
    >
      <div v-if="detailData" class="detail-content">
        <div v-if="detailData.image_url" class="detail-hero-image">
          <img :src="detailData.image_url" />
        </div>
        <div class="detail-meta-row">
          <n-tag
            v-if="detailData.category"
            round
            :style="{ background: getCategoryColor(detailData.category).bg, color: getCategoryColor(detailData.category).text, border: 'none' }"
          >
            {{ detailData.category }}
          </n-tag>
          <n-tag
            v-if="detailData.status"
            round
            :style="{ background: getStatusColor(detailData.status).bg, color: getStatusColor(detailData.status).text, border: 'none' }"
          >
            {{ detailData.status }}
          </n-tag>
          <span v-if="detailData.display_code" class="detail-code">#{{ detailData.display_code }}</span>
          <n-tag
            v-if="detailData.is_featured"
            round
            size="small"
            style="background: linear-gradient(135deg, rgba(212,165,165,0.9), rgba(192,137,144,0.9)); color: #FFFDF6; border: none;"
          >
            <template #icon><n-icon size="12"><Sparkles /></n-icon></template>
            精选
          </n-tag>
        </div>
        <n-grid :cols="2" :x-gap="16" :y-gap="10" style="margin-top: 16px;">
          <n-grid-item span="2 s:2 m:1" class="info-item">
            <span class="info-label">装裱风格</span>
            <span class="info-value">{{ detailData.frame_style || '-' }}</span>
          </n-grid-item>
          <n-grid-item span="2 s:2 m:1" class="info-item">
            <span class="info-label">装裱尺寸</span>
            <span class="info-value">{{ detailData.frame_size || '-' }}</span>
          </n-grid-item>
          <n-grid-item span="2 s:2 m:1" class="info-item">
            <span class="info-label">存放位置</span>
            <span class="info-value">{{ detailData.location || '-' }}</span>
          </n-grid-item>
          <n-grid-item span="2 s:2 m:1" class="info-item">
            <span class="info-label">制作日期</span>
            <span class="info-value">{{ detailData.production_date || '-' }}</span>
          </n-grid-item>
          <n-grid-item span="2 s:2 m:1" class="info-item">
            <span class="info-label">保存期限</span>
            <span class="info-value">{{ detailData.shelf_life_months ? detailData.shelf_life_months + ' 个月' : '-' }}</span>
          </n-grid-item>
          <n-grid-item span="2 s:2 m:1" class="info-item">
            <span class="info-label">保存方式</span>
            <span class="info-value">{{ detailData.preservation_method || '-' }}</span>
          </n-grid-item>
        </n-grid>
        <div v-if="detailData.tags?.length" class="detail-tags">
          <n-tag
            v-for="tag in detailData.tags"
            :key="tag"
            round
            size="small"
            style="background: rgba(245,230,163,0.22); color: #C49B3A; border: none;"
          >
            #{{ tag }}
          </n-tag>
        </div>
        <div v-if="detailData.description" class="detail-desc">
          <div class="info-label" style="margin-bottom: 8px;">作品描述</div>
          <p>{{ detailData.description }}</p>
        </div>
        <div v-if="detailData.gallery_images?.length" class="detail-gallery">
          <div class="info-label" style="margin-bottom: 10px;">作品图集</div>
          <div class="detail-gallery-grid">
            <img v-for="(url, i) in detailData.gallery_images" :key="i" :src="url" class="gallery-thumb" />
          </div>
        </div>
        <div class="detail-stats">
          <span class="stat-item">
            <n-icon size="16" color="#E88A9A"><Heart /></n-icon>
            <span>{{ detailData.like_count ?? 0 }}</span>
          </span>
          <span class="stat-item">
            <n-icon size="16" color="#8BA8C3"><Eye /></n-icon>
            <span>{{ detailData.view_count ?? 0 }}</span>
          </span>
        </div>
      </div>
      <template #footer>
        <NSpace justify="end">
          <n-button type="primary" @click="showDetailModal = false">
            <template #icon><n-icon :component="CheckmarkCircleOutline" /></template>
            关闭
          </n-button>
        </NSpace>
      </template>
    </n-modal>
  </div>
</template>

<style lang="scss" scoped>
.specimens-wrapper {
  background: transparent;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 24px;
  padding-bottom: 18px;
  border-bottom: 1px solid rgba(240, 230, 222, 0.6);
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

.filter-card {
  background: #FFFDF6;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(212, 165, 165, 0.1);
  border: 1px solid rgba(240, 230, 222, 0.8) !important;
  margin-bottom: 20px;
  position: relative;

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
  }
}

.filter-row-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.filter-switch-item {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 0 4px;
}

.filter-switch-label {
  font-size: 13px;
  color: #8B7D7B;
}

.view-tabs {
  margin-top: 4px;
}

.list-loading {
  padding: 60px 20px;
}

.empty-state {
  padding: 60px 20px;
}

.empty-icon-wrap {
  position: relative;
  width: 100px;
  height: 80px;
  margin: 0 auto 10px;

  .empty-emoji {
    position: absolute;
    font-size: 48px;
    opacity: 0.7;
  }
  .empty-emoji-2 {
    right: 0;
    bottom: 0;
    font-size: 36px;
    opacity: 0.5;
  }
}

.card-section {
  margin-bottom: 16px;
}

.specimen-card {
  background: linear-gradient(135deg, rgba(255, 253, 246, 1), rgba(250, 246, 238, 0.9));
  border-radius: 16px;
  border: 1px solid rgba(240, 230, 222, 0.9);
  overflow: hidden;
  transition: all 0.35s ease;
  cursor: pointer;
  position: relative;

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 14px 36px rgba(212, 165, 165, 0.22);
    border-color: rgba(212, 165, 165, 0.35);

    .specimen-image {
      transform: scale(1.08);
    }
    .specimen-overlay {
      opacity: 1;
    }
  }
}

.specimen-image-wrap {
  position: relative;
  width: 100%;
  padding-top: 100%;
  background: linear-gradient(135deg, #FAF6EE, #F5EEE8);
  overflow: hidden;
}

.specimen-image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
}

.specimen-image-placeholder {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.specimen-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(92, 74, 74, 0.35) 0%, rgba(92, 74, 74, 0.75) 100%);
  padding: 14px;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  opacity: 0;
  transition: opacity 0.3s ease;
  backdrop-filter: blur(2px);
}

.overlay-code {
  position: absolute;
  top: 12px;
  left: 12px;
  background: rgba(255, 253, 246, 0.85);
  color: #C08990;
  font-size: 11px;
  font-weight: 600;
  padding: 3px 9px;
  border-radius: 6px;
  font-family: monospace;
}

.overlay-desc {
  color: #FFFDF6;
  font-size: 12px;
  line-height: 1.5;
}

.specimen-badge-featured {
  position: absolute;
  top: 10px;
  right: 10px;
  padding: 4px 10px;
  background: linear-gradient(135deg, rgba(212, 165, 165, 0.95), rgba(192, 137, 144, 0.95));
  color: #FFFDF6;
  font-size: 11px;
  font-weight: 600;
  border-radius: 8px;
  backdrop-filter: blur(4px);
  box-shadow: 0 2px 8px rgba(212, 165, 165, 0.35);
  display: inline-flex;
  align-items: center;
}

.specimen-body {
  padding: 14px 14px 12px;
}

.specimen-name-row {
  margin-bottom: 8px;
}

.specimen-name {
  font-size: 15px;
  font-weight: 600;
  color: #5C4A4A;
  line-height: 1.35;
}

.specimen-category-row {
  margin-bottom: 10px;
}

.specimen-meta-line {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 10px;
  min-height: 20px;
}

.meta-pill {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: #8B7D7B;
  padding: 2px 0;
}

.specimen-stats-line {
  display: flex;
  gap: 18px;
  padding: 10px 0;
  border-top: 1px dashed rgba(240, 230, 222, 0.9);
  margin-bottom: 10px;
}

.stat-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  color: #8B7D7B;
  font-weight: 500;
  cursor: pointer;
  transition: color 0.2s;

  &:hover {
    color: #E88A9A;
  }
}

.stat-item {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  color: #8B7D7B;
  font-weight: 500;
}

.specimen-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}

.action-btns {
  display: flex;
  gap: 2px;
}

.table-card {
  background: #FFFDF6;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(212, 165, 165, 0.1);
  border: 1px solid rgba(240, 230, 222, 0.8) !important;
  margin-bottom: 16px;
  overflow: hidden;
}

.pagination-wrap {
  display: flex;
  justify-content: center;
  padding: 8px 0 16px;
}

.form-modal {
  :deep(.n-card) {
    border-radius: 18px !important;
    background: linear-gradient(180deg, #FFFDF6 0%, #FAF6EE 100%);
  }
  :deep(.n-card-header) {
    border-bottom: 1px solid rgba(240, 230, 222, 0.7) !important;
  }
}

.upload-main-wrap {
  max-width: 200px;
}

.main-image-preview {
  position: relative;
  width: 180px;
  height: 180px;
  border-radius: 12px;
  overflow: hidden;
  border: 2px solid rgba(240, 230, 222, 0.9);
}

.main-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.remove-main-img {
  position: absolute !important;
  top: 6px !important;
  right: 6px !important;
}

.upload-gallery-wrap {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.gallery-item {
  position: relative;
  width: 90px;
  height: 90px;
  border-radius: 10px;
  overflow: hidden;
  border: 2px solid rgba(240, 230, 222, 0.9);
}

.gallery-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.remove-gallery-img {
  position: absolute !important;
  top: 4px !important;
  right: 4px !important;
}

.gallery-add-btn {
  width: 90px;
  height: 90px;
  border-radius: 10px;
  border: 2px dashed rgba(212, 165, 165, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  background: rgba(250, 246, 238, 0.6);
  transition: all 0.2s;

  &:hover {
    border-color: rgba(212, 165, 165, 0.75);
    background: rgba(255, 253, 246, 0.9);
  }
}

.share-modal {
  :deep(.n-card) {
    border-radius: 18px !important;
    background: linear-gradient(180deg, #FFFDF6 0%, #FAF6EE 100%);
  }
  :deep(.n-card-header) {
    border-bottom: 1px solid rgba(240, 230, 222, 0.7) !important;
  }
}

.share-preview {
  margin-top: 6px;
  padding: 14px;
  background: rgba(250, 246, 238, 0.7);
  border-radius: 12px;
  border: 1px solid rgba(240, 230, 222, 0.8);
}

.share-preview-label {
  font-size: 12px;
  color: #8B7D7B;
  margin-bottom: 8px;
}

.share-preview-img {
  width: 100%;
  max-height: 200px;
  object-fit: cover;
  border-radius: 10px;
}

.detail-modal {
  :deep(.n-card) {
    border-radius: 18px !important;
    background: linear-gradient(180deg, #FFFDF6 0%, #FAF6EE 100%);
  }
  :deep(.n-card-header) {
    border-bottom: 1px solid rgba(240, 230, 222, 0.7) !important;
  }
}

.detail-content {
  max-height: 68vh;
  overflow-y: auto;
  padding-right: 4px;
}

.detail-hero-image {
  width: 100%;
  border-radius: 14px;
  overflow: hidden;
  margin-bottom: 16px;
  max-height: 320px;
  background: linear-gradient(135deg, #FAF6EE, #F5EEE8);

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
  }
}

.detail-meta-row {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
}

.detail-code {
  font-size: 12px;
  color: #B8A8A6;
  font-family: monospace;
  background: rgba(240, 230, 222, 0.6);
  padding: 3px 10px;
  border-radius: 6px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-label {
  font-size: 12px;
  color: #B8A8A6;
}

.info-value {
  font-size: 14px;
  color: #5C4A4A;
  font-weight: 500;
}

.detail-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 18px;
  padding-top: 16px;
  border-top: 1px dashed rgba(240, 230, 222, 0.9);
}

.detail-desc {
  margin-top: 18px;
  padding-top: 16px;
  border-top: 1px dashed rgba(240, 230, 222, 0.9);

  p {
    margin: 0;
    color: #5C4A4A;
    line-height: 1.75;
    font-size: 14px;
    white-space: pre-wrap;
  }
}

.detail-gallery {
  margin-top: 18px;
  padding-top: 16px;
  border-top: 1px dashed rgba(240, 230, 222, 0.9);
}

.detail-gallery-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(110px, 1fr));
  gap: 10px;
}

.gallery-thumb {
  width: 100%;
  aspect-ratio: 1;
  object-fit: cover;
  border-radius: 10px;
  cursor: pointer;
  transition: transform 0.2s;
  border: 2px solid rgba(240, 230, 222, 0.9);

  &:hover {
    transform: scale(1.04);
  }
}

.detail-stats {
  display: flex;
  gap: 24px;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid rgba(240, 230, 222, 0.7);

  .stat-item {
    font-size: 14px;
    gap: 7px;
  }
}
</style>
