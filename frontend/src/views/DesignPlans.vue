<script setup>
import { ref, reactive, computed, onMounted, h, nextTick } from 'vue'
import {
  NCard, NGrid, NGridItem, NTag, NIcon, NSpace, NButton, NInput,
  NSelect, NModal, NForm, NFormItem, NImage, NEmpty, NPopconfirm,
  useMessage, useDialog, NEllipsis, NDivider, NDynamicTags, NUpload,
  NPagination, NSkeleton, NInputNumber, NCarousel, NDataTable,
  NBadge
} from 'naive-ui'
import {
  ColorPalette, Add, Search, Refresh, CreateOutline, TrashOutline,
  CloudUploadOutline, Ban, TimeOutline, CashOutline, FlagOutline,
  EyeOutline, FlowerOutline, Sparkles, ColorFilter,
  Home, HeartCircleOutline, Briefcase, Gift, Trophy, CutOutline, HammerOutline,
  DocumentTextOutline, LayersOutline, ArrowUpOutline, ArrowDownOutline,
  AddOutline, RemoveOutline, HeartOutline, SparklesOutline
} from '@vicons/ionicons5'
import { plansApi, uploadApi } from '@/api'

const message = useMessage()
const dialog = useDialog()

const loading = ref(false)
const modalLoading = ref(false)
const uploadLoading = ref(false)
const sketchUploadLoading = ref(false)
const refsUploadLoading = ref(false)

const showDetailModal = ref(false)
const showFormModal = ref(false)
const isEdit = ref(false)
const editingId = ref(null)
const currentDetail = ref(null)

const filters = reactive({
  keyword: '',
  style: null,
  scene: null,
  status: null
})

const pagination = reactive({
  page: 1,
  pageSize: 9,
  total: 0
})

const dataList = ref([])
const styleOptions = ref([])
const sceneOptions = ref([])
const statusOptions = ref([])

const defaultStyleOptions = [
  { label: '复古', value: '复古' },
  { label: '清新', value: '清新' },
  { label: '森系', value: '森系' },
  { label: '极简', value: '极简' },
  { label: '浪漫', value: '浪漫' },
  { label: '田园', value: '田园' }
]

const defaultSceneOptions = [
  { label: '家居', value: '家居' },
  { label: '婚礼', value: '婚礼' },
  { label: '办公', value: '办公' },
  { label: '礼品', value: '礼品' },
  { label: '展览', value: '展览' }
]

const defaultStatusOptions = [
  { label: '草稿', value: '草稿' },
  { label: '进行中', value: '进行中' },
  { label: '已完成', value: '已完成' }
]

const priorityOptions = [
  { label: '0 - 无优先级', value: 0 },
  { label: '1 - 最低', value: 1 },
  { label: '2 - 较低', value: 2 },
  { label: '3 - 普通', value: 3 },
  { label: '4 - 较高', value: 4 },
  { label: '5 - 最高', value: 5 }
]

const sceneIconMap = {
  '家居': Home,
  '婚礼': HeartCircleOutline,
  '办公': Briefcase,
  '礼品': Gift,
  '展览': Trophy
}

const getStyleTagStyle = (style) => {
  const map = {
    '复古': { bg: 'rgba(184,140,93,0.2)', color: '#A07A4F' },
    '清新': { bg: 'rgba(168,195,160,0.22)', color: '#8BA888' },
    '森系': { bg: 'rgba(107,142,95,0.22)', color: '#6B8E5F' },
    '极简': { bg: 'rgba(139,125,123,0.22)', color: '#8B7D7B' },
    '浪漫': { bg: 'rgba(212,165,165,0.22)', color: '#C08990' },
    '田园': { bg: 'rgba(245,200,107,0.25)', color: '#C49B3A' }
  }
  return map[style] || { bg: 'rgba(184,168,166,0.22)', color: '#8B7D7B' }
}

const getSceneTagStyle = (scene) => {
  const map = {
    '家居': { bg: 'rgba(168,195,160,0.2)', color: '#8BA888' },
    '婚礼': { bg: 'rgba(232,180,184,0.22)', color: '#C08990' },
    '办公': { bg: 'rgba(139,168,195,0.22)', color: '#768CA3' },
    '礼品': { bg: 'rgba(245,200,107,0.25)', color: '#C49B3A' },
    '展览': { bg: 'rgba(200,165,212,0.22)', color: '#9B76A8' }
  }
  return map[scene] || { bg: 'rgba(184,168,166,0.22)', color: '#8B7D7B' }
}

const getStatusTagStyle = (status) => {
  const map = {
    '草稿': { bg: 'rgba(184,168,166,0.25)', color: '#8B7D7B', type: 'default' },
    '进行中': { bg: 'rgba(245,200,107,0.28)', color: '#C49B3A', type: 'warning' },
    '已完成': { bg: 'rgba(168,195,160,0.28)', color: '#8BA888', type: 'success' }
  }
  return map[status] || { bg: 'rgba(184,168,166,0.2)', color: '#8B7D7B', type: 'default' }
}

const getPriorityBadgeColor = (p) => {
  const map = {
    0: { bg: '#B8A8A6', label: '无' },
    1: { bg: '#A8C3A0', label: '1' },
    2: { bg: '#8BA888', label: '2' },
    3: { bg: '#F5C86B', label: '3' },
    4: { bg: '#E8B460', label: '4' },
    5: { bg: '#E87882', label: '5' }
  }
  return map[p] || map[0]
}

const defaultColorPalette = [
  { name: '豆沙粉', color: '#D4A5A5' },
  { name: '奶黄', color: '#F5E6A3' },
  { name: '鼠尾草绿', color: '#A8C3A0' },
  { name: '雾霾蓝', color: '#8BA8C3' },
  { name: '暖棕', color: '#A68C6D' },
  { name: '薰衣草紫', color: '#C8A5D4' }
]

const colorPaletteOptions = defaultColorPalette.map(c => ({
  label: c.name,
  value: c.name
}))

const formValues = reactive({
  name: '',
  style: null,
  scene: null,
  color_theme: null,
  estimated_hours: null,
  estimated_cost: null,
  priority: 0,
  materials_needed: [],
  tools_needed: [],
  design_sketch_url: '',
  reference_images: [],
  steps: [],
  layout_description: '',
  collocation_advice: '',
  status: '草稿',
  notes: ''
})

const formRules = {
  name: {
    required: true,
    message: '请输入方案名称',
    trigger: 'blur'
  }
}

function createMaterialRow() {
  return { name: '', quantity: null, unit: '' }
}

function createStepRow() {
  return { description: '' }
}

function addMaterialRow() {
  formValues.materials_needed.push(createMaterialRow())
}

function removeMaterialRow(idx) {
  formValues.materials_needed.splice(idx, 1)
}

function addStepRow() {
  formValues.steps.push(createStepRow())
}

function removeStepRow(idx) {
  if (formValues.steps.length > 1) {
    formValues.steps.splice(idx, 1)
  }
}

function moveStepUp(idx) {
  if (idx > 0) {
    const tmp = formValues.steps[idx]
    formValues.steps[idx] = formValues.steps[idx - 1]
    formValues.steps[idx - 1] = tmp
  }
}

function moveStepDown(idx) {
  if (idx < formValues.steps.length - 1) {
    const tmp = formValues.steps[idx]
    formValues.steps[idx] = formValues.steps[idx + 1]
    formValues.steps[idx + 1] = tmp
  }
}

function getColorByName(name) {
  const found = defaultColorPalette.find(c => c.name === name)
  return found?.color || '#D4A5A5'
}

async function loadOptions() {
  try {
    const [styleRes, sceneRes, statusRes] = await Promise.all([
      plansApi.styles(),
      plansApi.scenes(),
      plansApi.statuses()
    ])
    const processOptions = (res, defaults) => {
      if (res?.data) {
        const data = Array.isArray(res.data) ? res.data : (res.data.items || [])
        return data.length > 0
          ? data.map(item => ({
              label: item.name || item.label || item,
              value: item.value ?? item.id ?? item.name ?? item
            }))
          : defaults
      }
      return defaults
    }
    styleOptions.value = processOptions(styleRes, defaultStyleOptions)
    sceneOptions.value = processOptions(sceneRes, defaultSceneOptions)
    statusOptions.value = processOptions(statusRes, defaultStatusOptions)
  } catch (e) {
    styleOptions.value = defaultStyleOptions
    sceneOptions.value = defaultSceneOptions
    statusOptions.value = defaultStatusOptions
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
      style: filters.style || undefined,
      scene: filters.scene || undefined,
      status: filters.status || undefined
    }
    const res = await plansApi.list(params)
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
    message.error('加载方案列表失败')
  } finally {
    loading.value = false
  }
}

function resetFilters() {
  filters.keyword = ''
  filters.style = null
  filters.scene = null
  filters.status = null
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

async function openDetail(item) {
  try {
    const res = await plansApi.get(item.id)
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
    name: '',
    style: null,
    scene: null,
    color_theme: null,
    estimated_hours: null,
    estimated_cost: null,
    priority: 0,
    materials_needed: [createMaterialRow()],
    tools_needed: [],
    design_sketch_url: '',
    reference_images: [],
    steps: [createStepRow()],
    layout_description: '',
    collocation_advice: '',
    status: '草稿',
    notes: ''
  })
  showFormModal.value = true
}

async function openEdit(item) {
  isEdit.value = true
  editingId.value = item.id
  modalLoading.value = true
  showFormModal.value = true
  try {
    const res = await plansApi.get(item.id)
    if (res?.data) {
      const d = res.data
      Object.assign(formValues, {
        name: d.name ?? '',
        style: d.style ?? null,
        scene: d.scene ?? null,
        color_theme: d.color_theme ?? null,
        estimated_hours: d.estimated_hours ?? null,
        estimated_cost: d.estimated_cost ?? null,
        priority: d.priority ?? 0,
        materials_needed: Array.isArray(d.materials_needed) && d.materials_needed.length > 0
          ? d.materials_needed.map(m => ({
              name: m.name || '',
              quantity: m.quantity ?? null,
              unit: m.unit || ''
            }))
          : [createMaterialRow()],
        tools_needed: Array.isArray(d.tools_needed) ? [...d.tools_needed] : [],
        design_sketch_url: d.design_sketch_url ?? '',
        reference_images: Array.isArray(d.reference_images) ? [...d.reference_images] : [],
        steps: Array.isArray(d.steps) && d.steps.length > 0
          ? d.steps.map(s => ({
              description: typeof s === 'string' ? s : (s.description || s.desc || '')
            }))
          : [createStepRow()],
        layout_description: d.layout_description ?? '',
        collocation_advice: d.collocation_advice ?? '',
        status: d.status ?? '草稿',
        notes: d.notes ?? ''
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
      materials_needed: formValues.materials_needed
        ?.filter(m => m && m.name && m.name.trim())
        .map(m => ({
          name: m.name,
          quantity: m.quantity,
          unit: m.unit
        })) || [],
      tools_needed: formValues.tools_needed?.filter(t => t && t.trim()) || [],
      reference_images: formValues.reference_images?.filter(r => r && r.trim()) || [],
      steps: formValues.steps
        ?.filter(s => s && s.description && s.description.trim())
        .map((s, idx) => ({
          step: idx + 1,
          description: s.description
        })) || []
    }
    if (isEdit.value) {
      await plansApi.update(editingId.value, data)
      message.success('更新成功')
    } else {
      await plansApi.create(data)
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
    content: `确定要删除方案「${item.name}」吗？此操作不可撤销。`,
    positiveText: '删除',
    negativeText: '取消',
    positiveButtonProps: { type: 'error' },
    onPositiveClick: async () => {
      try {
        await plansApi.delete(item.id)
        message.success('删除成功')
        loadData()
      } catch (e) {
        message.error('删除失败')
      }
    }
  })
}

async function handleSketchUpload({ file, onFinish, onError }) {
  sketchUploadLoading.value = true
  try {
    const res = await uploadApi.uploadImage(file.file, 'plans/sketch')
    if (res?.data?.url || res?.data?.file_url || res?.data?.path) {
      formValues.design_sketch_url = res.data.url || res.data.file_url || res.data.path
      message.success('上传成功')
      onFinish()
    } else {
      throw new Error('上传失败')
    }
  } catch (e) {
    message.error('上传失败')
    onError()
  } finally {
    sketchUploadLoading.value = false
  }
}

async function handleRefImagesUpload({ file, onFinish, onError }) {
  refsUploadLoading.value = true
  try {
    const res = await uploadApi.uploadImage(file.file, 'plans/references')
    if (res?.data?.url || res?.data?.file_url || res?.data?.path) {
      const url = res.data.url || res.data.file_url || res.data.path
      formValues.reference_images.push(url)
      onFinish()
    } else {
      throw new Error('上传失败')
    }
  } catch (e) {
    message.error('上传失败')
    onError()
  } finally {
    refsUploadLoading.value = false
  }
}

function removeRefImage(idx) {
  formValues.reference_images.splice(idx, 1)
}

const materialsColumns = computed(() => [
  {
    title: '名称',
    key: 'name',
    render: (_, index) => h(NInput, {
      value: formValues.materials_needed[index].name,
      placeholder: '材料名称',
      onUpdateValue: (val) => { formValues.materials_needed[index].name = val }
    })
  },
  {
    title: '数量',
    key: 'quantity',
    width: 110,
    render: (_, index) => h(NInputNumber, {
      value: formValues.materials_needed[index].quantity,
      placeholder: '数量',
      min: 0,
      style: 'width: 100%',
      onUpdateValue: (val) => { formValues.materials_needed[index].quantity = val }
    })
  },
  {
    title: '单位',
    key: 'unit',
    width: 100,
    render: (_, index) => h(NInput, {
      value: formValues.materials_needed[index].unit,
      placeholder: '如g/枝/朵',
      onUpdateValue: (val) => { formValues.materials_needed[index].unit = val }
    })
  },
  {
    title: '操作',
    key: 'action',
    width: 60,
    render: (_, index) => h(NButton, {
      quaternary: true,
      circle: true,
      size: 'small',
      type: 'error',
      onClick: () => removeMaterialRow(index)
    }, {
      default: () => h(NIcon, { size: 14 }, { default: () => h(RemoveOutline) })
    })
  }
])

const detailMaterialsColumns = computed(() => [
  { title: '材料名称', key: 'name', ellipsis: true },
  { title: '数量', key: 'quantity', width: 100, render: (row) => row.quantity ?? '-' },
  { title: '单位', key: 'unit', width: 80, render: (row) => row.unit || '-' }
])

onMounted(async () => {
  await loadOptions()
  await loadData()
})
</script>

<template>
  <div class="plans-wrapper">
    <div class="section-header">
      <div>
        <h2 class="page-title">
          <n-icon size="26" color="#D4A5A5"><ColorPalette /></n-icon>
          设计方案存档
        </h2>
        <p class="page-subtitle">灵感在这里生根，创意在这里绽放，记录每一份花艺蓝图</p>
      </div>
      <div class="header-right">
        <span class="flower-icon flower-1">🌷</span>
        <n-button type="primary" size="large" @click="openCreate" class="btn-add">
          <template #icon>
            <n-icon :component="Add" />
          </template>
          新建方案
        </n-button>
        <span class="flower-icon flower-2">💐</span>
      </div>
    </div>

    <n-card class="filter-card" size="large" :bordered="false">
      <div class="filter-card-decor">
        <span class="decor-icon">✦</span>
        <span class="decor-flower">✿</span>
      </div>
      <n-grid :cols="6" responsive="screen" :x-gap="14" :y-gap="14" style="align-items: flex-end;">
        <n-grid-item span="6 s:6 m:6 l:2">
          <n-form-item label="关键词" label-placement="left" label-align="left" class="form-inline-item">
            <n-input
              v-model:value="filters.keyword"
              placeholder="搜索方案名称/描述..."
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
          <n-form-item label="风格" label-placement="left" label-align="left" class="form-inline-item">
            <n-select
              v-model:value="filters.style"
              :options="styleOptions"
              placeholder="全部风格"
              clearable
              filterable
            />
          </n-form-item>
        </n-grid-item>
        <n-grid-item span="6 s:3 m:3 l:1">
          <n-form-item label="场景" label-placement="left" label-align="left" class="form-inline-item">
            <n-select
              v-model:value="filters.scene"
              :options="sceneOptions"
              placeholder="全部场景"
              clearable
              filterable
            />
          </n-form-item>
        </n-grid-item>
        <n-grid-item span="6 s:6 m:6 l:1">
          <n-form-item label="状态" label-placement="left" label-align="left" class="form-inline-item">
            <n-select
              v-model:value="filters.status"
              :options="statusOptions"
              placeholder="全部状态"
              clearable
            />
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
          <n-grid-item v-for="i in 6" :key="i" span="3 s:3 m:3 l:1">
            <n-card class="plan-card skeleton-card" size="large" :bordered="false">
              <n-skeleton :height="180" rounded style="border-radius: 12px;" />
              <n-skeleton text style="margin-top: 14px;" :repeat="1" width="70%" />
              <n-skeleton text style="margin-top: 8px;" :repeat="2" />
              <n-skeleton text style="margin-top: 14px;" :repeat="1" width="50%" />
            </n-card>
          </n-grid-item>
        </n-grid>
      </div>
      <template v-else-if="dataList.length === 0">
        <n-card class="empty-card" :bordered="false">
          <n-empty description="暂无设计方案，点击右上角开启你的创意之旅吧～">
            <template #extra>
              <n-button type="primary" @click="openCreate">
                <template #icon><n-icon :component="Add" /></template>
                新建方案
              </n-button>
            </template>
          </n-empty>
        </n-card>
      </template>
      <n-grid v-else :cols="3" responsive="screen" :x-gap="18" :y-gap="18">
        <n-grid-item v-for="item in dataList" :key="item.id" span="3 s:3 m:3 l:1">
          <n-card class="plan-card" size="large" :bordered="false" hoverable>
            <div class="plan-card-decor">
              <span class="card-icon-1">✦</span>
              <span class="card-icon-2">❀</span>
            </div>
            <div class="sketch-wrap">
              <n-image
                v-if="item.design_sketch_url"
                :src="item.design_sketch_url"
                class="sketch-image"
                object-fit="cover"
                :preview-disabled="false"
              />
              <div v-else class="sketch-placeholder">
                <n-icon size="46" color="#D4B8B0"><ColorFilter /></n-icon>
                <span class="sketch-placeholder-text">暂无设计图</span>
              </div>
              <div
                v-if="item.priority && item.priority > 0"
                class="priority-badge"
                :style="{ background: getPriorityBadgeColor(item.priority).bg }"
              >
                P{{ getPriorityBadgeColor(item.priority).label }}
              </div>
            </div>
            <div class="plan-info">
              <h3 class="plan-name">
                <n-ellipsis :line-clamp="1">{{ item.name }}</n-ellipsis>
              </h3>
              <div class="tags-row" v-if="item.style || item.scene">
                <n-tag
                  v-if="item.style"
                  round
                  size="tiny"
                  :style="{
                    background: getStyleTagStyle(item.style).bg,
                    color: getStyleTagStyle(item.style).color,
                    border: 'none'
                  }"
                >
                  <n-icon size="11" style="margin-right: 3px;"><SparklesOutline /></n-icon>
                  {{ item.style }}
                </n-tag>
                <n-tag
                  v-if="item.scene"
                  round
                  size="tiny"
                  :style="{
                    background: getSceneTagStyle(item.scene).bg,
                    color: getSceneTagStyle(item.scene).color,
                    border: 'none'
                  }"
                >
                  <n-icon size="11" style="margin-right: 3px;">
                    <component :is="sceneIconMap[item.scene] || FlowerOutline" />
                  </n-icon>
                  {{ item.scene }}
                </n-tag>
              </div>
              <div class="color-row" v-if="item.color_theme">
                <div
                  class="color-dot"
                  :style="{ background: getColorByName(item.color_theme) }"
                  :title="item.color_theme"
                ></div>
                <span class="color-name">{{ item.color_theme }}</span>
              </div>
              <div class="estimate-row">
                <div class="estimate-item">
                  <n-icon size="14" color="#8BA8C3"><TimeOutline /></n-icon>
                  <span class="estimate-label">工时</span>
                  <span class="estimate-value">{{ item.estimated_hours ?? '-' }}<span class="estimate-unit">h</span></span>
                </div>
                <div class="estimate-item">
                  <n-icon size="14" color="#D4A06B"><CashOutline /></n-icon>
                  <span class="estimate-label">成本</span>
                  <span class="estimate-value">¥{{ item.estimated_cost ?? '-' }}</span>
                </div>
              </div>
              <div class="status-row">
                <n-tag
                  round
                  size="small"
                  :type="getStatusTagStyle(item.status).type"
                  :style="{
                    background: getStatusTagStyle(item.status).bg,
                    color: getStatusTagStyle(item.status).color,
                    border: 'none',
                    fontWeight: 500
                  }"
                >
                  {{ item.status }}
                </n-tag>
              </div>
            </div>
            <div class="card-actions">
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
                确认删除该方案？
              </n-popconfirm>
              <n-button size="small" type="primary" class="btn-detail" @click="openDetail(item)">
                <template #icon><n-icon :component="EyeOutline" size="14" /></template>
                查看详情
              </n-button>
            </div>
          </n-card>
        </n-grid-item>
      </n-grid>

      <div v-if="pagination.total > 0" class="pagination-wrap">
        <n-pagination
          v-model:page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :item-count="pagination.total"
          :page-sizes="[9, 18, 36, 72]"
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
      title="方案详情"
      :style="{ width: '900px', maxWidth: '94vw' }"
      :mask-closable="true"
      class="detail-modal"
      :scrollable="true"
    >
      <template v-if="currentDetail">
        <div class="detail-decor">
          <span class="detail-icon-1">✦</span>
          <span class="detail-icon-2">✿</span>
          <span class="detail-icon-3">❁</span>
        </div>
        <n-grid :cols="2" responsive="screen" :x-gap="24" class="detail-grid">
          <n-grid-item span="2 s:2 m:2 l:1">
            <div class="left-section">
              <div class="section-label">
                <n-icon size="15" color="#D4A5A5"><ColorFilter /></n-icon>
                设计草图
              </div>
              <div class="sketch-display">
                <n-image
                  v-if="currentDetail.design_sketch_url"
                  :src="currentDetail.design_sketch_url"
                  class="sketch-display-img"
                  object-fit="cover"
                />
                <div v-else class="sketch-empty">
                  <n-icon size="40" color="#D4B8B0"><ColorFilter /></n-icon>
                  <span>暂无设计草图</span>
                </div>
              </div>

              <div class="section-label" style="margin-top: 20px;">
                <n-icon size="15" color="#F5C86B"><LayersOutline /></n-icon>
                参考图集
                <span class="section-count">{{ (currentDetail.reference_images || []).length }} 张</span>
              </div>
              <div v-if="currentDetail.reference_images && currentDetail.reference_images.length > 0" class="ref-carousel-wrap">
                <n-carousel
                  :interval="5000"
                  :dot-type="'line'"
                  :show-arrow="'hover'"
                  dot-placement="bottom"
                >
                  <div
                    v-for="(img, idx) in currentDetail.reference_images"
                    :key="idx"
                    class="carousel-item"
                  >
                    <n-image
                      :src="img"
                      class="carousel-img"
                      object-fit="cover"
                    />
                  </div>
                </n-carousel>
              </div>
              <div v-else class="ref-empty">
                <n-icon size="28" color="#B8A8A6"><LayersOutline /></n-icon>
                <span>暂无参考图片</span>
              </div>
            </div>
          </n-grid-item>

          <n-grid-item span="2 s:2 m:2 l:1">
            <div class="right-section">
              <h2 class="detail-plan-name">
                <n-ellipsis :line-clamp="2">{{ currentDetail.name }}</n-ellipsis>
              </h2>
              <div class="detail-tags">
                <n-tag
                  v-if="currentDetail.style"
                  round
                  size="medium"
                  :style="{
                    background: getStyleTagStyle(currentDetail.style).bg,
                    color: getStyleTagStyle(currentDetail.style).color,
                    border: 'none'
                  }"
                >
                  <n-icon size="12" style="margin-right: 4px;"><SparklesOutline /></n-icon>
                  {{ currentDetail.style }}
                </n-tag>
                <n-tag
                  v-if="currentDetail.scene"
                  round
                  size="medium"
                  :style="{
                    background: getSceneTagStyle(currentDetail.scene).bg,
                    color: getSceneTagStyle(currentDetail.scene).color,
                    border: 'none'
                  }"
                >
                  <n-icon size="12" style="margin-right: 4px;">
                    <component :is="sceneIconMap[currentDetail.scene] || FlowerOutline" />
                  </n-icon>
                  {{ currentDetail.scene }}
                </n-tag>
                <div v-if="currentDetail.color_theme" class="detail-color-row">
                  <div
                    class="color-dot color-dot-lg"
                    :style="{ background: getColorByName(currentDetail.color_theme) }"
                  ></div>
                  <span class="detail-color-name">{{ currentDetail.color_theme }}</span>
                </div>
              </div>

              <div class="detail-estimate-row">
                <div class="detail-estimate-card">
                  <n-icon size="18" color="#8BA8C3"><TimeOutline /></n-icon>
                  <div class="estimate-info">
                    <div class="estimate-text">{{ currentDetail.estimated_hours ?? '-' }}<span class="unit"> 小时</span></div>
                    <div class="estimate-label">预估工时</div>
                  </div>
                </div>
                <div class="detail-estimate-card">
                  <n-icon size="18" color="#D4A06B"><CashOutline /></n-icon>
                  <div class="estimate-info">
                    <div class="estimate-text">¥{{ currentDetail.estimated_cost ?? '-' }}</div>
                    <div class="estimate-label">预估成本</div>
                  </div>
                </div>
                <div class="detail-estimate-card">
                  <div
                    class="priority-circle"
                    :style="{ background: getPriorityBadgeColor(currentDetail.priority).bg }"
                  >
                    {{ getPriorityBadgeColor(currentDetail.priority).label }}
                  </div>
                  <div class="estimate-info">
                    <div class="estimate-text">{{ currentDetail.priority ?? 0 }} / 5</div>
                    <div class="estimate-label">优先级</div>
                  </div>
                </div>
              </div>

              <div class="detail-section" v-if="currentDetail.materials_needed && currentDetail.materials_needed.length > 0">
                <div class="section-label">
                  <n-icon size="15" color="#A8C3A0"><FlowerOutline /></n-icon>
                  所需材料
                </div>
                <n-data-table
                  :columns="detailMaterialsColumns"
                  :data="currentDetail.materials_needed"
                  :bordered="false"
                  size="small"
                  class="detail-table"
                  :pagination="false"
                />
              </div>

              <div class="detail-section" v-if="currentDetail.tools_needed && currentDetail.tools_needed.length > 0">
                <div class="section-label">
                  <n-icon size="15" color="#B8926A"><CutOutline /></n-icon>
                  工具清单
                </div>
                <n-space wrap :size="8">
                  <n-tag
                    v-for="(tool, idx) in currentDetail.tools_needed"
                    :key="idx"
                    round
                    class="tool-tag"
                  >
                    <n-icon size="11" color="#B8926A" style="margin-right: 3px;"><HammerOutline /></n-icon>
                    {{ tool }}
                  </n-tag>
                </n-space>
              </div>

              <div class="detail-section" v-if="currentDetail.steps && currentDetail.steps.length > 0">
                <div class="section-label">
                  <n-icon size="15" color="#C08990"><DocumentTextOutline /></n-icon>
                  制作步骤
                </div>
                <div class="steps-list">
                  <div
                    v-for="(step, idx) in currentDetail.steps"
                    :key="idx"
                    class="step-item"
                  >
                    <div class="step-badge">{{ typeof step === 'object' ? (step.step ?? idx + 1) : idx + 1 }}</div>
                    <div class="step-desc">
                      {{ typeof step === 'object' ? (step.description || step.desc || '') : step }}
                    </div>
                  </div>
                </div>
              </div>

              <div class="detail-section" v-if="currentDetail.layout_description">
                <div class="section-label">
                  <n-icon size="15" color="#9B76A8"><LayersOutline /></n-icon>
                  布局说明
                </div>
                <div class="desc-block">{{ currentDetail.layout_description }}</div>
              </div>

              <div class="detail-section" v-if="currentDetail.collocation_advice">
                <div class="section-label">
                  <n-icon size="15" color="#8BA888"><HeartOutline /></n-icon>
                  搭配建议
                </div>
                <div class="desc-block">{{ currentDetail.collocation_advice }}</div>
              </div>

              <div class="detail-bottom-row">
                <div class="status-row">
                  <span class="status-label">状态：</span>
                  <n-tag
                    round
                    size="medium"
                    :type="getStatusTagStyle(currentDetail.status).type"
                    :style="{
                      background: getStatusTagStyle(currentDetail.status).bg,
                      color: getStatusTagStyle(currentDetail.status).color,
                      border: 'none',
                      fontWeight: 600
                    }"
                  >
                    {{ currentDetail.status }}
                  </n-tag>
                </div>
                <div v-if="currentDetail.notes" class="notes-row">
                  <span class="notes-label">备注：</span>
                  <span class="notes-text">{{ currentDetail.notes }}</span>
                </div>
              </div>
            </div>
          </n-grid-item>
        </n-grid>
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
      :title="isEdit ? '编辑方案' : '新建方案'"
      :style="{ width: '860px', maxWidth: '94vw' }"
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
        <span class="modal-icon-1">✦</span>
        <span class="modal-flower">🌸</span>
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
        <n-divider class="modal-divider"><span class="divider-label">基础信息</span></n-divider>
        <n-grid :cols="2" responsive="screen" :x-gap="16" :y-gap="4">
          <n-grid-item span="2 s:2 m:2 l:2">
            <n-form-item label="方案名称" path="name">
              <n-input v-model:value="formValues.name" placeholder="请输入方案名称" :input-props="{ autocomplete: 'off' }" />
            </n-form-item>
          </n-grid-item>
          <n-grid-item span="2 s:2 m:2 l:1">
            <n-form-item label="风格">
              <n-select
                v-model:value="formValues.style"
                :options="styleOptions"
                placeholder="请选择风格"
                clearable
                filterable
              />
            </n-form-item>
          </n-grid-item>
          <n-grid-item span="2 s:2 m:2 l:1">
            <n-form-item label="场景">
              <n-select
                v-model:value="formValues.scene"
                :options="sceneOptions"
                placeholder="请选择场景"
                clearable
                filterable
              />
            </n-form-item>
          </n-grid-item>
          <n-grid-item span="2 s:2 m:2 l:2">
            <n-form-item label="色彩主题">
              <div class="color-picker-row">
                <n-select
                  v-model:value="formValues.color_theme"
                  :options="colorPaletteOptions"
                  placeholder="选择或输入"
                  clearable
                  filterable
                  allow-input
                  style="flex: 1;"
                />
                <div
                  v-if="formValues.color_theme"
                  class="selected-color-dot"
                  :style="{ background: getColorByName(formValues.color_theme) }"
                ></div>
              </div>
            </n-form-item>
          </n-grid-item>
        </n-grid>

        <n-divider class="modal-divider"><span class="divider-label">预估信息</span></n-divider>
        <n-grid :cols="3" responsive="screen" :x-gap="16" :y-gap="4">
          <n-grid-item span="3 s:3 m:3 l:1">
            <n-form-item label="工时(小时)">
              <n-input-number
                v-model:value="formValues.estimated_hours"
                :min="0"
                :precision="1"
                placeholder="预估工时"
                style="width: 100%;"
              />
            </n-form-item>
          </n-grid-item>
          <n-grid-item span="3 s:3 m:3 l:1">
            <n-form-item label="成本(元)">
              <n-input-number
                v-model:value="formValues.estimated_cost"
                :min="0"
                :precision="2"
                placeholder="预估成本"
                style="width: 100%;"
              />
            </n-form-item>
          </n-grid-item>
          <n-grid-item span="3 s:3 m:3 l:1">
            <n-form-item label="优先级">
              <n-select
                v-model:value="formValues.priority"
                :options="priorityOptions"
                placeholder="选择优先级"
              />
            </n-form-item>
          </n-grid-item>
        </n-grid>

        <n-divider class="modal-divider"><span class="divider-label">材料与工具</span></n-divider>
        <n-form-item label="材料清单" :show-label="false">
          <div class="materials-table-wrap">
            <div class="table-label">
              <n-icon size="13" color="#8BA888"><FlowerOutline /></n-icon>
              所需材料
            </div>
            <n-data-table
              :columns="materialsColumns"
              :data="formValues.materials_needed"
              :bordered="false"
              size="small"
              class="materials-table"
              :pagination="false"
            />
            <n-button
              dashed
              block
              size="small"
              class="add-row-btn"
              @click="addMaterialRow"
            >
              <template #icon><n-icon :component="AddOutline" size="13" /></template>
              添加材料
            </n-button>
          </div>
        </n-form-item>
        <n-form-item label="工具清单">
          <n-dynamic-tags
            v-model:value="formValues.tools_needed"
            placeholder="输入工具名称后按回车添加，如：剪刀、热胶枪..."
            round
            size="medium"
          />
        </n-form-item>

        <n-divider class="modal-divider"><span class="divider-label">设计图与参考</span></n-divider>
        <n-grid :cols="2" responsive="screen" :x-gap="16" :y-gap="4">
          <n-grid-item span="2 s:2 m:2 l:1">
            <n-form-item label="设计草图">
              <div class="upload-wrapper">
                <n-upload
                  :show-file-list="false"
                  :custom-request="handleSketchUpload"
                  accept="image/*"
                  :disabled="sketchUploadLoading"
                  class="upload-btn"
                >
                  <div class="upload-trigger" :class="{ hasImage: formValues.design_sketch_url }">
                    <img v-if="formValues.design_sketch_url" :src="formValues.design_sketch_url" class="upload-preview" />
                    <div v-else class="upload-placeholder">
                      <n-icon size="26" color="#D4B8B0"><CloudUploadOutline /></n-icon>
                      <span class="upload-text">{{ sketchUploadLoading ? '上传中...' : '点击上传设计图' }}</span>
                      <span class="upload-hint">JPG / PNG</span>
                    </div>
                  </div>
                </n-upload>
                <n-button
                  v-if="formValues.design_sketch_url"
                  text
                  size="tiny"
                  type="error"
                  style="margin-top: 8px;"
                  @click="formValues.design_sketch_url = ''"
                >
                  <template #icon><n-icon :component="Ban" size="12" /></template>
                  移除图片
                </n-button>
              </div>
            </n-form-item>
          </n-grid-item>
          <n-grid-item span="2 s:2 m:2 l:1">
            <n-form-item label="参考图集">
              <div class="refs-wrapper">
                <div class="refs-grid">
                  <div
                    v-for="(img, idx) in formValues.reference_images"
                    :key="idx"
                    class="ref-image-item"
                  >
                    <img :src="img" class="ref-image" />
                    <n-button
                      text
                      circle
                      size="tiny"
                      type="error"
                      class="ref-remove-btn"
                      @click="removeRefImage(idx)"
                    >
                      <template #icon><n-icon :component="Ban" size="12" /></template>
                    </n-button>
                  </div>
                  <n-upload
                    :show-file-list="false"
                    :custom-request="handleRefImagesUpload"
                    accept="image/*"
                    :disabled="refsUploadLoading"
                    class="ref-upload-btn"
                  >
                    <div class="ref-upload-trigger">
                      <n-icon size="22" color="#D4B8B0"><AddOutline /></n-icon>
                      <span>{{ refsUploadLoading ? '...' : '添加' }}</span>
                    </div>
                  </n-upload>
                </div>
              </div>
            </n-form-item>
          </n-grid-item>
        </n-grid>

        <n-divider class="modal-divider"><span class="divider-label">制作步骤</span></n-divider>
        <n-form-item label="步骤列表" :show-label="false">
          <div class="steps-editor">
            <div
              v-for="(step, idx) in formValues.steps"
              :key="idx"
              class="step-editor-item"
            >
              <div class="step-editor-badge">{{ idx + 1 }}</div>
              <n-input
                v-model:value="step.description"
                type="textarea"
                :placeholder="`第 ${idx + 1} 步的详细描述...`"
                :autosize="{ minRows: 2, maxRows: 4 }"
                style="flex: 1;"
              />
              <div class="step-editor-actions">
                <n-button
                  quaternary
                  circle
                  size="small"
                  :disabled="idx === 0"
                  @click="moveStepUp(idx)"
                >
                  <template #icon><n-icon :component="ArrowUpOutline" size="14" /></template>
                </n-button>
                <n-button
                  quaternary
                  circle
                  size="small"
                  :disabled="idx === formValues.steps.length - 1"
                  @click="moveStepDown(idx)"
                >
                  <template #icon><n-icon :component="ArrowDownOutline" size="14" /></template>
                </n-button>
                <n-button
                  quaternary
                  circle
                  size="small"
                  type="error"
                  :disabled="formValues.steps.length <= 1"
                  @click="removeStepRow(idx)"
                >
                  <template #icon><n-icon :component="RemoveOutline" size="14" /></template>
                </n-button>
              </div>
            </div>
            <n-button
              dashed
              block
              size="small"
              class="add-row-btn"
              @click="addStepRow"
            >
              <template #icon><n-icon :component="AddOutline" size="13" /></template>
              添加步骤
            </n-button>
          </div>
        </n-form-item>

        <n-divider class="modal-divider"><span class="divider-label">说明与备注</span></n-divider>
        <n-form-item label="布局说明">
          <n-input
            v-model:value="formValues.layout_description"
            type="textarea"
            placeholder="描述整体布局结构、空间规划等..."
            :autosize="{ minRows: 3, maxRows: 6 }"
          />
        </n-form-item>
        <n-form-item label="搭配建议">
          <n-input
            v-model:value="formValues.collocation_advice"
            type="textarea"
            placeholder="花材搭配、色彩搭配、风格搭配建议..."
            :autosize="{ minRows: 3, maxRows: 6 }"
          />
        </n-form-item>
        <n-grid :cols="2" responsive="screen" :x-gap="16" :y-gap="4">
          <n-grid-item span="2 s:2 m:2 l:1">
            <n-form-item label="状态">
              <n-select
                v-model:value="formValues.status"
                :options="statusOptions"
                placeholder="请选择状态"
              />
            </n-form-item>
          </n-grid-item>
          <n-grid-item span="2 s:2 m:2 l:1">
            <n-form-item label="备注">
              <n-input v-model:value="formValues.notes" placeholder="其他补充信息..." :input-props="{ autocomplete: 'off' }" />
            </n-form-item>
          </n-grid-item>
        </n-grid>
      </n-form>
    </n-modal>
  </div>
</template>

<style lang="scss" scoped>
.plans-wrapper {
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
  flex-wrap: wrap;
  gap: 14px;
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

  &.flower-1 { animation-delay: 0s; }
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
    background: linear-gradient(180deg, #D4A5A5, #F5E6A3, #A8C3A0);
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

.decor-icon, .decor-flower {
  font-size: 48px;
  opacity: 0.05;
  color: #D4A5A5;
  position: absolute;
  top: -6px;
  right: 8px;

  &.decor-flower {
    color: #F5E6A3;
    top: auto;
    right: -6px;
    bottom: -10px;
    font-size: 56px;
  }
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

.loading-wrap { padding: 10px 0; }

.skeleton-card {
  background: #FFFDF6;
  border-radius: 18px;
  border: 1px solid rgba(240, 230, 222, 0.8) !important;
}

.empty-card {
  background: #FFFDF6;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(212, 165, 165, 0.08);
  border: 1px solid rgba(240, 230, 222, 0.8) !important;
  padding: 30px;
}

.plan-card {
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
    background: linear-gradient(90deg, #D4A5A5, #F5E6A3, #A8C3A0, #C8A5D4);
    opacity: 0.6;
  }

  &:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 32px rgba(212, 165, 165, 0.22);
    border-color: rgba(212, 165, 165, 0.3) !important;
  }

  :deep(.n-card__content) {
    padding: 0 !important;
    height: 100%;
    display: flex;
    flex-direction: column;
  }
}

.plan-card-decor {
  position: absolute;
  pointer-events: none;
  z-index: 0;

  .card-icon-1 {
    position: absolute;
    top: 10px;
    left: 10px;
    font-size: 30px;
    opacity: 0.06;
    color: #D4A5A5;
  }
  .card-icon-2 {
    position: absolute;
    bottom: 50px;
    right: -10px;
    font-size: 50px;
    opacity: 0.05;
    color: #F5E6A3;
    transform: rotate(-10deg);
  }
}

.sketch-wrap {
  position: relative;
  width: 100%;
  padding-top: 72%;
  overflow: hidden;
  z-index: 1;
}

.sketch-image {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.sketch-placeholder {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  background: linear-gradient(135deg, rgba(250, 246, 238, 0.9), rgba(255, 248, 227, 0.7));
}

.sketch-placeholder-text {
  font-size: 13px;
  color: #B8A8A6;
}

.priority-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  padding: 4px 10px;
  border-radius: 14px;
  font-size: 11px;
  font-weight: 700;
  color: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  backdrop-filter: blur(4px);
}

.plan-info {
  padding: 16px 18px 12px;
  position: relative;
  z-index: 1;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.plan-name {
  font-size: 16px;
  font-weight: 700;
  color: #5C4A4A;
  line-height: 1.45;
  margin: 0 0 10px;
}

.tags-row {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 10px;
}

.color-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.color-dot {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 2px solid #fff;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
}

.color-dot-lg {
  width: 22px;
  height: 22px;
}

.color-name {
  font-size: 12px;
  color: #8B7D7B;
}

.estimate-row {
  display: flex;
  gap: 16px;
  padding: 10px 12px;
  background: linear-gradient(135deg, rgba(250, 246, 238, 0.8), rgba(255, 248, 227, 0.6));
  border-radius: 10px;
  margin-bottom: 12px;
  border: 1px solid rgba(240, 230, 222, 0.5);
}

.estimate-item {
  display: flex;
  align-items: center;
  gap: 5px;
  flex: 1;
}

.estimate-label {
  font-size: 11px;
  color: #8B7D7B;
}

.estimate-value {
  font-size: 14px;
  font-weight: 700;
  color: #5C4A4A;
}

.estimate-unit {
  font-size: 11px;
  font-weight: 500;
  color: #8B7D7B;
  margin-left: 1px;
}

.status-row {
  margin-top: auto;
}

.card-actions {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 6px;
  padding: 12px 18px 16px;
  border-top: 1px dashed rgba(240, 230, 222, 0.7);
  flex-wrap: wrap;
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
      content: '🎨';
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

.detail-icon-1, .detail-icon-2, .detail-icon-3 {
  position: absolute;
  opacity: 0.05;
  color: #D4A5A5;

  &.detail-icon-1 {
    font-size: 60px;
    top: 10px;
    right: 20px;
    transform: rotate(20deg);
  }
  &.detail-icon-2 {
    font-size: 70px;
    bottom: 60px;
    left: -10px;
    transform: rotate(-15deg);
    color: #F5E6A3;
  }
  &.detail-icon-3 {
    font-size: 50px;
    top: 40%;
    right: -5px;
    color: #C8A5D4;
    transform: rotate(35deg);
  }
}

.detail-grid {
  position: relative;
  z-index: 1;
}

.left-section {
  height: 100%;
}

.section-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 600;
  color: #5C4A4A;
  margin-bottom: 10px;
}

.section-count {
  font-size: 11px;
  font-weight: 500;
  color: #B8A8A6;
  margin-left: 4px;
}

.sketch-display {
  width: 100%;
  border-radius: 14px;
  overflow: hidden;
  border: 1px solid rgba(240, 230, 222, 0.6);
  box-shadow: 0 4px 16px rgba(212, 165, 165, 0.1);
}

.sketch-display-img {
  width: 100%;
  max-height: 280px;
  object-fit: cover;
  display: block;
}

.sketch-empty {
  width: 100%;
  height: 240px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  background: linear-gradient(135deg, rgba(250, 246, 238, 0.9), rgba(255, 248, 227, 0.7));
  color: #B8A8A6;
  font-size: 13px;
}

.ref-carousel-wrap {
  border-radius: 14px;
  overflow: hidden;
  border: 1px solid rgba(240, 230, 222, 0.6);
  box-shadow: 0 4px 16px rgba(212, 165, 165, 0.08);
}

.carousel-item {
  width: 100%;
  height: 220px;
}

.carousel-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.ref-empty {
  padding: 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background: linear-gradient(135deg, rgba(250, 246, 238, 0.6), rgba(255, 248, 227, 0.5));
  border-radius: 14px;
  border: 1px dashed rgba(240, 230, 222, 0.6);
  color: #B8A8A6;
  font-size: 13px;
}

.right-section {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.detail-plan-name {
  font-size: 20px;
  font-weight: 700;
  color: #5C4A4A;
  line-height: 1.45;
  margin: 0 0 12px;
}

.detail-tags {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
}

.detail-color-row {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-left: 4px;
}

.detail-color-name {
  font-size: 12px;
  color: #8B7D7B;
  font-weight: 500;
}

.detail-estimate-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  margin-bottom: 18px;
}

.detail-estimate-card {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 14px;
  background: linear-gradient(135deg, rgba(250, 246, 238, 0.9), rgba(255, 248, 227, 0.7));
  border-radius: 12px;
  border: 1px solid rgba(240, 230, 222, 0.6);
}

.estimate-info {
  flex: 1;
  min-width: 0;
}

.estimate-text {
  font-size: 16px;
  font-weight: 700;
  color: #5C4A4A;
  line-height: 1.2;

  .unit {
    font-size: 12px;
    font-weight: 500;
    color: #8B7D7B;
  }
}

.estimate-label {
  font-size: 11px;
  color: #8B7D7B;
  margin-top: 4px;
}

.priority-circle {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 13px;
  font-weight: 700;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
  flex-shrink: 0;
}

.detail-section {
  margin-bottom: 16px;
}

.detail-table {
  background: transparent;
  border-radius: 10px;
  overflow: hidden;
  border: 1px solid rgba(240, 230, 222, 0.5);

  :deep(.n-data-table-th) {
    background: rgba(250, 246, 238, 0.9) !important;
    color: #5C4A4A !important;
    font-weight: 600 !important;
    font-size: 12px !important;
    border-bottom: 1px solid rgba(240, 230, 222, 0.6) !important;
  }

  :deep(.n-data-table-td) {
    border-bottom: 1px solid rgba(240, 230, 222, 0.4) !important;
    font-size: 12px;
    color: #5C4A4A;
  }

  :deep(.n-data-table-tr:last-child .n-data-table-td) {
    border-bottom: none !important;
  }
}

.tool-tag {
  background: rgba(184, 146, 106, 0.15) !important;
  color: #A07A4F !important;
  border: none !important;
}

.steps-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.step-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 10px 12px;
  background: linear-gradient(135deg, rgba(250, 246, 238, 0.7), rgba(255, 248, 227, 0.5));
  border-radius: 10px;
  border: 1px solid rgba(240, 230, 222, 0.5);
}

.step-badge {
  width: 26px;
  height: 26px;
  border-radius: 8px;
  background: linear-gradient(135deg, #D4A5A5, #C08990);
  color: #fff;
  font-size: 12px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 2px 6px rgba(212, 165, 165, 0.3);
}

.step-desc {
  font-size: 13px;
  color: #5C4A4A;
  line-height: 1.7;
  flex: 1;
  white-space: pre-wrap;
  word-break: break-word;
}

.desc-block {
  padding: 12px 14px;
  background: linear-gradient(135deg, rgba(250, 246, 238, 0.8), rgba(255, 248, 227, 0.6));
  border-radius: 10px;
  border: 1px solid rgba(240, 230, 222, 0.5);
  font-size: 13px;
  color: #5C4A4A;
  line-height: 1.8;
  white-space: pre-wrap;
  word-break: break-word;
}

.detail-bottom-row {
  margin-top: auto;
  padding-top: 14px;
  border-top: 1px dashed rgba(240, 230, 222, 0.6);
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
}

.status-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-label {
  font-size: 13px;
  color: #8B7D7B;
  font-weight: 500;
}

.notes-row {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  flex: 1;
  min-width: 200px;
}

.notes-label {
  font-size: 13px;
  color: #8B7D7B;
  font-weight: 500;
  flex-shrink: 0;
}

.notes-text {
  font-size: 13px;
  color: #5C4A4A;
  line-height: 1.6;
  flex: 1;
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
      content: '💐';
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

.modal-icon-1, .modal-flower {
  position: absolute;
  font-size: 60px;
  opacity: 0.04;
  color: #D4A5A5;
}

.modal-icon-1 {
  top: 30px;
  right: -10px;
  transform: rotate(15deg);
}

.modal-flower {
  bottom: -20px;
  left: -15px;
  font-size: 80px;
  color: #F5E6A3;
  transform: rotate(-25deg);
}

.modal-divider {
  margin: 8px 0 16px !important;
  border-color: rgba(240, 230, 222, 0.6) !important;
}

.divider-label {
  font-size: 13px;
  font-weight: 600;
  color: #C08990;
  padding: 0 12px;
}

.color-picker-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.selected-color-dot {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: 3px solid #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
  flex-shrink: 0;
}

.materials-table-wrap {
  width: 100%;
}

.table-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 500;
  color: #8B7D7B;
  margin-bottom: 8px;
}

.materials-table {
  background: rgba(255, 253, 246, 0.5);
  border-radius: 10px;
  overflow: hidden;
  border: 1px solid rgba(240, 230, 222, 0.5);
  margin-bottom: 10px;

  :deep(.n-data-table-th) {
    background: rgba(250, 246, 238, 0.8) !important;
    color: #5C4A4A !important;
    font-weight: 600 !important;
    font-size: 12px !important;
    border-bottom: 1px solid rgba(240, 230, 222, 0.6) !important;
  }

  :deep(.n-data-table-td) {
    border-bottom: 1px solid rgba(240, 230, 222, 0.4) !important;
    padding: 6px 8px !important;
  }

  :deep(.n-data-table-tr:last-child .n-data-table-td) {
    border-bottom: none !important;
  }
}

.add-row-btn {
  color: #C08990 !important;
  border-color: rgba(212, 165, 165, 0.35) !important;

  &:hover {
    background: rgba(212, 165, 165, 0.08) !important;
  }
}

.upload-wrapper {
  width: 100%;
}

.upload-trigger {
  width: 100%;
  min-height: 120px;
  border: 2px dashed rgba(212, 165, 165, 0.35);
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  background: linear-gradient(135deg, rgba(250, 246, 238, 0.8), rgba(255, 253, 246, 1));

  &:hover {
    border-color: rgba(212, 165, 165, 0.6);

    .upload-text { color: #C08990; }
  }

  &.hasImage {
    border-style: solid;
    border-color: rgba(212, 165, 165, 0.2);
    min-height: 140px;
  }
}

.upload-placeholder {
  width: 100%;
  min-height: 120px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 16px;
}

.upload-text {
  font-size: 12px;
  color: #8B7D7B;
  font-weight: 500;
  transition: color 0.25s ease;
}

.upload-hint {
  font-size: 10px;
  color: #B8A8A6;
}

.upload-preview {
  width: 100%;
  height: 140px;
  object-fit: contain;
  background: rgba(250, 246, 238, 0.6);
  display: block;
}

.upload-btn {
  width: 100%;
}

.refs-wrapper {
  width: 100%;
}

.refs-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
  gap: 8px;
}

.ref-image-item {
  position: relative;
  width: 100%;
  padding-top: 100%;
  border-radius: 10px;
  overflow: hidden;
  border: 1px solid rgba(240, 230, 222, 0.6);
}

.ref-image {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.ref-remove-btn {
  position: absolute;
  top: 2px;
  right: 2px;
  background: rgba(255, 253, 246, 0.95) !important;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
}

.ref-upload-btn {
  width: 100%;
  height: 100%;
}

.ref-upload-trigger {
  width: 100%;
  height: 100%;
  min-height: 80px;
  border: 2px dashed rgba(212, 165, 165, 0.3);
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: rgba(250, 246, 238, 0.6);
  color: #8B7D7B;
  font-size: 11px;

  &:hover {
    border-color: rgba(212, 165, 165, 0.55);
    color: #C08990;
    background: rgba(250, 246, 238, 0.9);
  }
}

.steps-editor {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.step-editor-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
}

.step-editor-badge {
  width: 28px;
  height: 28px;
  border-radius: 9px;
  background: linear-gradient(135deg, rgba(212, 165, 165, 0.9), rgba(192, 137, 144, 0.9));
  color: #FFFDF6;
  font-size: 13px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(212, 165, 165, 0.3);
  margin-top: 4px;
}

.step-editor-actions {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex-shrink: 0;
  margin-top: 4px;
}
</style>
