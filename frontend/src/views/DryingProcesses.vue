<script setup>
import { ref, reactive, computed, onMounted, h } from 'vue'
import {
  NCard, NGrid, NGridItem, NTag, NIcon, NSpace, NButton, NInput,
  NSelect, NDatePicker, NInputNumber, NModal, NForm, NFormItem,
  NProgress, NPagination, NText, NPopconfirm, useMessage, useDialog,
  NEllipsis, NDivider, NDynamicTags, NEmpty
} from 'naive-ui'
import {
  Sparkles, PlayOutline, CheckmarkCircle, CloseCircle, TimeOutline,
  Thermometer, Water, Add, Search, Reload, EyeOutline, CreateOutline,
  TrashOutline, FlowerOutline, PricetagsOutline, BuildOutline,
  HammerOutline, ColorPalette, CheckboxOutline, LayersOutline,
  DocumentTextOutline, AddOutline, RemoveOutline, CalendarOutline,
  FlaskOutline
} from '@vicons/ionicons5'
import { dryingApi, materialsApi } from '@/api'

const message = useMessage()
const dialog = useDialog()

const loading = ref(false)
const statLoading = ref(false)
const modalLoading = ref(false)
const showModal = ref(false)
const modalTitle = ref('新增制作记录')
const editingId = ref(null)

const queryParams = reactive({
  keyword: '',
  method: null,
  status: null,
  material_id: null,
  page: 1,
  page_size: 12
})

const pagination = reactive({
  page: 1,
  pageSize: 12,
  total: 0
})

const list = ref([])
const methodOptions = ref([])
const statusOptions = ref([])
const materialOptions = ref([])
const materialCaching = ref({})

const stats = ref({
  in_progress: 0,
  completed: 0,
  failed: 0,
  avg_duration: '0h'
})

const statCards = computed(() => [
  {
    title: '进行中',
    key: 'in_progress',
    icon: PlayOutline,
    gradient: 'linear-gradient(135deg, rgba(245,230,163,0.25), rgba(245,200,107,0.18))',
    accent: '#F5C86B'
  },
  {
    title: '已完成',
    key: 'completed',
    icon: CheckmarkCircle,
    gradient: 'linear-gradient(135deg, rgba(168,195,160,0.22), rgba(139,168,136,0.16))',
    accent: '#8BA888'
  },
  {
    title: '失败',
    key: 'failed',
    icon: CloseCircle,
    gradient: 'linear-gradient(135deg, rgba(232,180,184,0.25), rgba(192,137,144,0.2))',
    accent: '#C08990'
  },
  {
    title: '平均时长',
    key: 'avg_duration',
    icon: TimeOutline,
    gradient: 'linear-gradient(135deg, rgba(212,165,165,0.18), rgba(245,230,163,0.2))',
    accent: '#D4A5A5',
    isText: true
  }
])

const formDefaults = () => ({
  name: '',
  material_id: null,
  method: null,
  status: 'in_progress',
  start_time: null,
  end_time: null,
  temperature: null,
  humidity: null,
  pressure: null,
  desiccant_weight: null,
  pretreatment: '',
  steps: [''],
  color_retention: null,
  shape_retention: null,
  yield_rate: null,
  output_quantity: null,
  notes: ''
})

const form = reactive(formDefaults())
const formRules = {
  name: {
    required: true,
    message: '请输入制作名称',
    trigger: 'blur'
  },
  material_id: {
    required: true,
    message: '请选择原料',
    trigger: 'change'
  },
  method: {
    required: true,
    message: '请选择制作方法',
    trigger: 'change'
  },
  status: {
    required: true,
    message: '请选择状态',
    trigger: 'change'
  }
}

const effectOptions = [
  { label: '优', value: 'excellent' },
  { label: '良', value: 'good' },
  { label: '中', value: 'fair' },
  { label: '差', value: 'poor' }
]

const effectTagStyle = (val) => {
  const map = {
    excellent: { bg: 'rgba(168,195,160,0.25)', color: '#8BA888' },
    good: { bg: 'rgba(245,200,107,0.25)', color: '#C49B3A' },
    fair: { bg: 'rgba(212,165,165,0.2)', color: '#C08990' },
    poor: { bg: 'rgba(192,137,144,0.3)', color: '#A85F68' }
  }
  return map[val] || { bg: 'rgba(212,165,165,0.15)', color: '#8B7D7B' }
}

const effectLabel = (val) => {
  const map = { excellent: '优', good: '良', fair: '中', poor: '差' }
  return map[val] || '-'
}

const statusTagStyle = (val) => {
  const map = {
    in_progress: { bg: 'rgba(245,200,107,0.22)', color: '#C49B3A', type: 'warning' },
    completed: { bg: 'rgba(168,195,160,0.22)', color: '#8BA888', type: 'success' },
    failed: { bg: 'rgba(192,137,144,0.25)', color: '#A85F68', type: 'error' }
  }
  return map[val] || { bg: 'rgba(212,165,165,0.15)', color: '#8B7D7B', type: 'default' }
}

const statusLabel = (val) => {
  const map = { in_progress: '进行中', completed: '已完成', failed: '失败' }
  return map[val] || val
}

const getMaterialName = (id) => {
  if (!id) return '-'
  if (materialCaching.value[id]) return materialCaching.value[id]
  const found = materialOptions.value.find(m => m.value === id)
  if (found) {
    materialCaching.value[id] = found.label
    return found.label
  }
  return '-'
}

const getMaterialCategory = (id) => {
  if (!id) return null
  const found = materialOptions.value.find(m => m.value === id)
  return found?.category || null
}

const getMethodLabel = (val) => {
  const found = methodOptions.value.find(m => m.value === val)
  return found?.label || val || '-'
}

function formatDuration(item) {
  if (item.duration_hours != null) {
    const h = Math.floor(item.duration_hours)
    const m = Math.round((item.duration_hours - h) * 60)
    if (h > 0 && m > 0) return `${h}h ${m}m`
    if (h > 0) return `${h}h`
    return `${m}m`
  }
  if (item.start_time && item.end_time) {
    const diff = (new Date(item.end_time) - new Date(item.start_time)) / 3600000
    if (diff > 0) {
      const h = Math.floor(diff)
      const m = Math.round((diff - h) * 60)
      if (h > 0 && m > 0) return `${h}h ${m}m`
      if (h > 0) return `${h}h`
      return `${m}m`
    }
  }
  return '-'
}

const yieldRatePercent = computed(() => (item) => {
  if (item.yield_rate != null) {
    const n = Number(item.yield_rate)
    return n > 1 ? Math.min(100, n) : Math.min(100, n * 100)
  }
  return 0
})

async function loadOptions() {
  try {
    const [methodsRes, statusesRes, materialsRes] = await Promise.all([
      dryingApi.methods(),
      dryingApi.statuses(),
      materialsApi.list({ page_size: 100 })
    ])
    if (methodsRes?.data) {
      methodOptions.value = Array.isArray(methodsRes.data)
        ? methodsRes.data.map(m => ({ label: m.label || m.name || m, value: m.value ?? m.id ?? m }))
        : Object.entries(methodsRes.data).map(([k, v]) => ({ label: v, value: k }))
    }
    if (statusesRes?.data) {
      statusOptions.value = Array.isArray(statusesRes.data)
        ? statusesRes.data.map(s => ({ label: s.label || s.name || s, value: s.value ?? s.id ?? s }))
        : Object.entries(statusesRes.data).map(([k, v]) => ({ label: v, value: k }))
    }
    let matList = []
    if (materialsRes?.data?.items) matList = materialsRes.data.items
    else if (materialsRes?.data && Array.isArray(materialsRes.data)) matList = materialsRes.data
    materialOptions.value = matList.map(m => ({
      label: m.name || m.label || m.title || '-',
      value: m.id,
      category: m.category
    }))
    materialOptions.value.forEach(m => { materialCaching.value[m.value] = m.label })
  } catch (e) {
    console.error('加载选项失败', e)
  }
}

async function loadList() {
  loading.value = true
  try {
    const params = { ...queryParams }
    if (!params.keyword) delete params.keyword
    if (!params.method) delete params.method
    if (!params.status) delete params.status
    if (!params.material_id) delete params.material_id
    params.page = pagination.page
    params.page_size = pagination.pageSize

    const res = await dryingApi.list(params)
    if (res?.data?.list) {
      list.value = res.data.items
      pagination.total = res.data.total ?? 0
    } else if (res?.data && Array.isArray(res.data)) {
      list.value = res.data
      pagination.total = res.data.length
    } else {
      list.value = []
      pagination.total = 0
    }
  } catch (e) {
    message.error('加载列表失败')
  } finally {
    loading.value = false
  }
}

async function loadStats() {
  statLoading.value = true
  try {
    const res = await dryingApi.list({ page_size: 100 })
    let all = []
    if (res?.data?.items) all = res.data.items
    else if (res?.data && Array.isArray(res.data)) all = res.data

    let totalDuration = 0
    let countWithDuration = 0
    let inProgress = 0, completed = 0, failed = 0

    all.forEach(item => {
      if (item.status === 'in_progress') inProgress++
      else if (item.status === 'completed') completed++
      else if (item.status === 'failed') failed++

      let hours = null
      if (item.duration_hours != null) hours = Number(item.duration_hours)
      else if (item.start_time && item.end_time) {
        hours = (new Date(item.end_time) - new Date(item.start_time)) / 3600000
      }
      if (hours != null && hours > 0) {
        totalDuration += hours
        countWithDuration++
      }
    })

    stats.value = {
      in_progress: inProgress,
      completed: completed,
      failed: failed,
      avg_duration: countWithDuration > 0 ? formatHours(totalDuration / countWithDuration) : '0h'
    }
  } catch (e) {
    console.error('统计加载失败', e)
  } finally {
    statLoading.value = false
  }
}

function formatHours(h) {
  const hours = Math.floor(h)
  const mins = Math.round((h - hours) * 60)
  if (hours >= 24) {
    const d = Math.floor(hours / 24)
    const rh = hours % 24
    if (rh > 0) return `${d}天${rh}h`
    return `${d}天`
  }
  if (hours > 0 && mins > 0) return `${hours}h${mins}m`
  if (hours > 0) return `${hours}h`
  return `${mins}m`
}

function resetQuery() {
  queryParams.keyword = ''
  queryParams.method = null
  queryParams.status = null
  queryParams.material_id = null
  pagination.page = 1
  loadList()
}

function handleSearch() {
  pagination.page = 1
  loadList()
}

function handlePageChange(p) {
  pagination.page = p
  loadList()
}

function handlePageSizeChange(sz) {
  pagination.pageSize = sz
  pagination.page = 1
  loadList()
}

function openCreate() {
  modalTitle.value = '新增制作记录'
  editingId.value = null
  Object.assign(form, formDefaults())
  showModal.value = true
}

function openEdit(item) {
  modalTitle.value = '编辑制作记录'
  editingId.value = item.id
  Object.assign(form, formDefaults())

  const fields = ['name', 'material_id', 'method', 'status', 'start_time',
    'end_time', 'temperature', 'humidity', 'pressure', 'desiccant_weight',
    'pretreatment', 'steps', 'color_retention', 'shape_retention',
    'yield_rate', 'output_quantity', 'notes']
  fields.forEach(k => {
    if (item[k] !== undefined && item[k] !== null) {
      if (k === 'steps') {
        form[k] = Array.isArray(item[k]) && item[k].length > 0 ? [...item[k]] : ['']
      } else if (k === 'start_time' || k === 'end_time') {
        form[k] = item[k] ? new Date(item[k]).getTime() : null
      } else {
        form[k] = item[k]
      }
    }
  })
  showModal.value = true
}

function addStep() {
  form.steps.push('')
}

function removeStep(index) {
  if (form.steps.length > 1) {
    form.steps.splice(index, 1)
  }
}

async function handleSubmit() {
  modalLoading.value = true
  try {
    const payload = {
      name: form.name,
      material_id: form.material_id,
      method: form.method,
      status: form.status,
      start_time: form.start_time ? new Date(form.start_time).toISOString() : null,
      end_time: form.end_time ? new Date(form.end_time).toISOString() : null,
      temperature: form.temperature,
      humidity: form.humidity,
      pressure: form.pressure,
      desiccant_weight: form.desiccant_weight,
      pretreatment: form.pretreatment || null,
      steps: form.steps.filter(s => s && s.trim()) || null,
      color_retention: form.color_retention,
      shape_retention: form.shape_retention,
      yield_rate: form.yield_rate,
      output_quantity: form.output_quantity,
      notes: form.notes || null
    }
    if (editingId.value) {
      await dryingApi.update(editingId.value, payload)
      message.success('更新成功')
    } else {
      await dryingApi.create(payload)
      message.success('创建成功')
    }
    showModal.value = false
    await Promise.all([loadList(), loadStats()])
  } catch (e) {
    message.error(editingId.value ? '更新失败' : '创建失败')
  } finally {
    modalLoading.value = false
  }
}

function handleDelete(item) {
  dialog.warning({
    title: '确认删除',
    content: `确定要删除制作记录「${item.name}」吗？此操作不可撤销。`,
    positiveText: '删除',
    negativeText: '取消',
    positiveButtonProps: { type: 'error' },
    onPositiveClick: async () => {
      try {
        await dryingApi.delete(item.id)
        message.success('删除成功')
        await Promise.all([loadList(), loadStats()])
      } catch (e) {
        message.error('删除失败')
      }
    }
  })
}

function handleView(item) {
  const metaInfo = [
    { label: '原料', value: getMaterialName(item.material_id) },
    { label: '分类', value: getMaterialCategory(item.material_id) || '-' },
    { label: '方法', value: getMethodLabel(item.method) },
    { label: '状态', value: statusLabel(item.status) },
    { label: '时长', value: formatDuration(item) },
    { label: '温度', value: item.temperature != null ? `${item.temperature}°C` : '-' },
    { label: '湿度', value: item.humidity != null ? `${item.humidity}%` : '-' },
    { label: '压力', value: item.pressure != null ? `${item.pressure} kPa` : '-' },
    { label: '干燥剂', value: item.desiccant_weight != null ? `${item.desiccant_weight}g` : '-' },
    { label: '保色效果', value: effectLabel(item.color_retention) },
    { label: '保型效果', value: effectLabel(item.shape_retention) },
    { label: '成品率', value: item.yield_rate != null ? `${yieldRatePercent.value(item)}%` : '-' },
    { label: '产出数量', value: item.output_quantity != null ? item.output_quantity : '-' }
  ]
  const content = h('div', { style: 'padding: 4px 0; line-height: 1.9; color: #5C4A4A;' }, [
    h('div', { style: 'margin-bottom: 16px;' }, [
      h('div', { style: 'font-weight: 600; color: #5C4A4A; margin-bottom: 6px;' }, '基础信息'),
      ...metaInfo.map(m => h('div', { style: 'display: flex; font-size: 13px; padding: 3px 0;' }, [
        h('span', { style: 'color: #8B7D7B; width: 80px; flex-shrink: 0;' }, m.label + '：'),
        h('span', { style: 'color: #5C4A4A; flex: 1;' }, m.value)
      ]))
    ]),
    item.pretreatment ? h('div', { style: 'margin-bottom: 16px;' }, [
      h('div', { style: 'font-weight: 600; color: #5C4A4A; margin-bottom: 6px;' }, '预处理'),
      h('div', { style: 'font-size: 13px; background: #FAF6EE; padding: 10px 12px; border-radius: 8px; white-space: pre-wrap;' }, item.pretreatment)
    ]) : null,
    (item.steps && item.steps.length) ? h('div', { style: 'margin-bottom: 16px;' }, [
      h('div', { style: 'font-weight: 600; color: #5C4A4A; margin-bottom: 6px;' }, '制作步骤'),
      ...item.steps.map((s, i) => h('div', { style: 'display: flex; font-size: 13px; padding: 4px 0; gap: 8px;' }, [
        h('span', { style: 'background: rgba(212,165,165,0.2); color: #C08990; width: 22px; height: 22px; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-size: 11px; flex-shrink: 0; font-weight: 600;' }, i + 1),
        h('span', { style: 'flex: 1; color: #5C4A4A; line-height: 22px;' }, s)
      ]))
    ]) : null,
    item.notes ? h('div', {}, [
      h('div', { style: 'font-weight: 600; color: #5C4A4A; margin-bottom: 6px;' }, '备注'),
      h('div', { style: 'font-size: 13px; background: #FAF6EE; padding: 10px 12px; border-radius: 8px; white-space: pre-wrap;' }, item.notes)
    ]) : null
  ].filter(Boolean))
  dialog.info({
    title: item.name,
    content,
    positiveText: '关闭',
    style: 'width: 560px;'
  })
}

onMounted(async () => {
  await loadOptions()
  await Promise.all([loadList(), loadStats()])
})
</script>

<template>
  <div class="drying-wrapper">
    <div class="section-header">
      <div>
        <h2 class="page-title">
          <n-icon size="26" color="#D4A5A5"><FlowerOutline /></n-icon>
          干燥工艺
        </h2>
        <p class="page-subtitle">精准把控每一个参数，让花朵在时光中绽放最美姿态</p>
      </div>
      <n-button
        type="primary"
        size="large"
        round
        class="create-btn"
        @click="openCreate"
      >
        <template #icon>
          <n-icon :component="Add" />
        </template>
        开始制作
      </n-button>
    </div>

    <div class="stats-section">
      <n-grid :cols="4" responsive="screen" :x-gap="18" :y-gap="18">
        <n-grid-item v-for="card in statCards" :key="card.key" span="4 s:2 m:2 l:1">
          <div class="stat-card" :style="{ background: card.gradient }">
            <div class="stat-card-bg">
              <span class="bg-flower bg-flower-1">❀</span>
              <span class="bg-flower bg-flower-2">✿</span>
            </div>
            <div class="stat-card-inner">
              <div class="stat-icon-wrap" :style="{ background: `linear-gradient(135deg, ${card.accent}33, ${card.accent}22)` }">
                <n-icon :component="card.icon" :size="22" :color="card.accent" />
              </div>
              <div class="stat-info">
                <div class="stat-title">{{ card.title }}</div>
                <div class="stat-value" :style="{ color: card.accent }">
                  <template v-if="card.isText">{{ stats[card.key] }}</template>
                  <template v-else>
                    <span class="stat-num">{{ stats[card.key] || 0 }}</span>
                  </template>
                </div>
              </div>
            </div>
          </div>
        </n-grid-item>
      </n-grid>
    </div>

    <n-card class="filter-card" size="large" :bordered="false">
      <n-grid :cols="6" responsive="screen" :x-gap="14" :y-gap="14" style="align-items: center;">
        <n-grid-item span="6 s:6 m:6 l:2">
          <n-input
            v-model:value="queryParams.keyword"
            placeholder="搜索制作名称 / 备注..."
            clearable
            size="large"
            round
            @keyup.enter="handleSearch"
          >
            <template #prefix>
              <n-icon :component="Search" />
            </template>
          </n-input>
        </n-grid-item>
        <n-grid-item span="6 s:3 m:3 l:1">
          <n-select
            v-model:value="queryParams.method"
            placeholder="制作方法"
            :options="methodOptions"
            clearable
            size="large"
          />
        </n-grid-item>
        <n-grid-item span="6 s:3 m:3 l:1">
          <n-select
            v-model:value="queryParams.status"
            placeholder="状态"
            :options="statusOptions"
            clearable
            size="large"
          />
        </n-grid-item>
        <n-grid-item span="6 s:6 m:6 l:2">
          <n-select
            v-model:value="queryParams.material_id"
            placeholder="选择原料"
            :options="materialOptions"
            clearable
            filterable
            size="large"
          />
        </n-grid-item>
        <n-grid-item span="6 s:6 m:6 l:2">
          <n-space justify="end">
            <n-button size="large" round @click="resetQuery">
              <template #icon><n-icon :component="Reload" /></template>
              重置
            </n-button>
            <n-button type="primary" size="large" round @click="handleSearch">
              <template #icon><n-icon :component="Search" /></template>
              查询
            </n-button>
          </n-space>
        </n-grid-item>
      </n-grid>
    </n-card>

    <div class="list-section">
      <div v-if="loading" class="empty-state">
        <div class="loading-spinner"></div>
        <span>加载中...</span>
      </div>
      <template v-else-if="list.length === 0">
        <n-card class="empty-card" :bordered="false">
          <n-empty description="暂无制作记录，点击右上角开始制作吧～">
            <template #extra>
              <n-button type="primary" round @click="openCreate">
                <template #icon><n-icon :component="AddOutline" /></template>
                开始制作
              </n-button>
            </template>
          </n-empty>
        </n-card>
      </template>
      <n-grid v-else :cols="3" responsive="screen" :x-gap="18" :y-gap="18">
        <n-grid-item v-for="item in list" :key="item.id" span="3 s:3 m:3 l:3 xl:3 xxl:2">
          <n-card class="process-card" size="large" :bordered="false" hoverable>
            <div class="card-header-row">
              <div class="card-title-row">
                <n-icon size="20" color="#D4A5A5"><Sparkles /></n-icon>
                <span class="process-name">
                  <n-ellipsis :line-clamp="1">{{ item.name }}</n-ellipsis>
                </span>
              </div>
              <n-tag
                round
                size="small"
                :type="statusTagStyle(item.status).type"
                :style="{
                  background: statusTagStyle(item.status).bg,
                  color: statusTagStyle(item.status).color,
                  border: 'none'
                }"
              >
                {{ statusLabel(item.status) }}
              </n-tag>
            </div>

            <n-divider class="card-divider" />

            <div class="info-block">
              <div class="info-row">
                <div class="info-item">
                  <n-icon size="14" color="#D4A5A5"><FlowerOutline /></n-icon>
                  <span class="info-label">原料</span>
                  <n-tag round size="tiny" class="soft-tag tag-pink">
                    {{ getMaterialName(item.material_id) }}
                  </n-tag>
                </div>
                <div v-if="getMaterialCategory(item.material_id)" class="info-item">
                  <n-icon size="14" color="#F5C86B"><PricetagsOutline /></n-icon>
                  <span class="info-label">分类</span>
                  <n-tag round size="tiny" class="soft-tag tag-yellow">
                    {{ getMaterialCategory(item.material_id) }}
                  </n-tag>
                </div>
              </div>

              <div class="info-row">
                <div class="info-item">
                  <n-icon size="14" color="#8BA888"><BuildOutline /></n-icon>
                  <span class="info-label">方法</span>
                  <n-tag round size="tiny" class="soft-tag tag-green">
                    {{ getMethodLabel(item.method) }}
                  </n-tag>
                </div>
              </div>
            </div>

            <div class="params-row">
              <div class="param-item" v-if="item.temperature != null">
                <n-icon size="16" color="#E88A9A"><Thermometer /></n-icon>
                <span class="param-value">{{ item.temperature }}°C</span>
              </div>
              <div class="param-item" v-if="item.humidity != null">
                <n-icon size="16" color="#8BA8C3"><Water /></n-icon>
                <span class="param-value">{{ item.humidity }}%</span>
              </div>
              <div class="param-item">
                <n-icon size="16" color="#C08990"><TimeOutline /></n-icon>
                <span class="param-value">{{ formatDuration(item) }}</span>
              </div>
              <div class="param-item" v-if="item.pressure != null">
                <n-icon size="16" color="#D4A06B"><FlaskOutline /></n-icon>
                <span class="param-value">{{ item.pressure }} kPa</span>
              </div>
              <div class="param-item" v-if="item.desiccant_weight != null">
                <n-icon size="16" color="#A8C3A0"><LayersOutline /></n-icon>
                <span class="param-value">{{ item.desiccant_weight }}g</span>
              </div>
            </div>

            <div class="effect-block">
              <div class="effect-row">
                <div class="effect-item">
                  <span class="effect-label">
                    <n-icon size="14" color="#E8B460"><ColorPalette /></n-icon>
                    保色
                  </span>
                  <n-tag
                    v-if="item.color_retention"
                    round
                    size="small"
                    :style="{
                      background: effectTagStyle(item.color_retention).bg,
                      color: effectTagStyle(item.color_retention).color,
                      border: 'none'
                    }"
                  >
                    {{ effectLabel(item.color_retention) }}
                  </n-tag>
                  <span v-else class="empty-val">-</span>
                </div>
                <div class="effect-item">
                  <span class="effect-label">
                    <n-icon size="14" color="#8BA8C3"><CheckboxOutline /></n-icon>
                    保型
                  </span>
                  <n-tag
                    v-if="item.shape_retention"
                    round
                    size="small"
                    :style="{
                      background: effectTagStyle(item.shape_retention).bg,
                      color: effectTagStyle(item.shape_retention).color,
                      border: 'none'
                    }"
                  >
                    {{ effectLabel(item.shape_retention) }}
                  </n-tag>
                  <span v-else class="empty-val">-</span>
                </div>
              </div>

              <div class="yield-section" v-if="item.yield_rate != null">
                <div class="yield-header">
                  <span class="yield-label">
                    <n-icon size="14" color="#A8C3A0"><HammerOutline /></n-icon>
                    成品率
                  </span>
                  <span class="yield-value" :style="{ color: '#8BA888' }">
                    {{ yieldRatePercent(item) }}%
                  </span>
                </div>
                <n-progress
                  type="line"
                  :percentage="yieldRatePercent(item)"
                  :show-indicator="false"
                  :height="6"
                  :rail-style="{ background: '#F5EEE8' }"
                  :fill-style="'linear-gradient(90deg, #A8C3A0, #D4A5A5)'"
                />
              </div>

              <div class="output-row" v-if="item.output_quantity != null">
                <n-icon size="14" color="#D4A5A5"><LayersOutline /></n-icon>
                <span class="output-label">产出数量</span>
                <span class="output-value">{{ item.output_quantity }}</span>
              </div>
            </div>

            <div class="card-footer">
              <n-button
                size="small"
                quaternary
                round
                @click="handleView(item)"
              >
                <template #icon><n-icon :component="EyeOutline" /></template>
                详情
              </n-button>
              <n-button
                size="small"
                quaternary
                round
                @click="openEdit(item)"
              >
                <template #icon><n-icon :component="CreateOutline" /></template>
                编辑
              </n-button>
              <n-popconfirm @positive-click="handleDelete(item)">
                <template #trigger>
                  <n-button
                    size="small"
                    quaternary
                    round
                    style="color: #C08990;"
                  >
                    <template #icon><n-icon :component="TrashOutline" /></template>
                    删除
                  </n-button>
                </template>
                确认删除该记录？
              </n-popconfirm>
            </div>
          </n-card>
        </n-grid-item>
      </n-grid>

      <div v-if="pagination.total > 0" class="pagination-wrap">
        <n-pagination
          v-model:page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[12, 24, 48, 96]"
          show-size-picker
          show-quick-jumper
          round
          size="large"
          @update:page="handlePageChange"
          @update:page-size="handlePageSizeChange"
        />
      </div>
    </div>

    <n-modal
      v-model:show="showModal"
      preset="card"
      :title="modalTitle"
      :mask-closable="false"
      class="form-modal"
      style="width: 760px; max-width: 94vw;"
      :scrollable="true"
    >
      <n-form
        :model="form"
        :rules="formRules"
        label-placement="left"
        label-width="110px"
        size="large"
        require-mark-placement="right-hanging"
      >
        <n-divider class="modal-divider"><span class="divider-label">基础信息</span></n-divider>
        <n-grid :cols="2" responsive="screen" :x-gap="16" :y-gap="6">
          <n-grid-item span="2 s:2 m:2 l:2">
            <n-form-item label="制作名称" path="name">
              <n-input v-model:value="form.name" placeholder="请输入制作名称" />
            </n-form-item>
          </n-grid-item>
          <n-grid-item span="2 s:2 m:2 l:1">
            <n-form-item label="原料" path="material_id">
              <n-select
                v-model:value="form.material_id"
                :options="materialOptions"
                filterable
                clearable
                placeholder="请选择原料"
              />
            </n-form-item>
          </n-grid-item>
          <n-grid-item span="2 s:2 m:2 l:1">
            <n-form-item label="制作方法" path="method">
              <n-select
                v-model:value="form.method"
                :options="methodOptions"
                clearable
                placeholder="请选择制作方法"
              />
            </n-form-item>
          </n-grid-item>
          <n-grid-item span="2 s:2 m:2 l:1">
            <n-form-item label="状态" path="status">
              <n-select
                v-model:value="form.status"
                :options="statusOptions"
                placeholder="请选择状态"
              />
            </n-form-item>
          </n-grid-item>
          <n-grid-item span="2 s:2 m:2 l:1">
            <n-form-item label="产出数量">
              <n-input-number
                v-model:value="form.output_quantity"
                :min="0"
                placeholder="产出数量"
                style="width: 100%;"
              />
            </n-form-item>
          </n-grid-item>
        </n-grid>

        <n-divider class="modal-divider"><span class="divider-label">时间安排</span></n-divider>
        <n-grid :cols="2" responsive="screen" :x-gap="16" :y-gap="6">
          <n-grid-item span="2 s:2 m:2 l:1">
            <n-form-item label="开始时间">
              <n-date-picker
                v-model:value="form.start_time"
                type="datetime"
                clearable
                placeholder="选择开始时间"
                value-format="timestamp"
                style="width: 100%;"
              />
            </n-form-item>
          </n-grid-item>
          <n-grid-item span="2 s:2 m:2 l:1">
            <n-form-item label="结束时间">
              <n-date-picker
                v-model:value="form.end_time"
                type="datetime"
                clearable
                placeholder="选择结束时间"
                value-format="timestamp"
                style="width: 100%;"
              />
            </n-form-item>
          </n-grid-item>
        </n-grid>

        <n-divider class="modal-divider"><span class="divider-label">参数设置</span></n-divider>
        <n-grid :cols="4" responsive="screen" :x-gap="16" :y-gap="6">
          <n-grid-item span="4 s:4 m:2 l:2 xl:1">
            <n-form-item label="温度(°C)">
              <n-input-number
                v-model:value="form.temperature"
                :min="-50"
                :max="200"
                placeholder="温度"
                style="width: 100%;"
              />
            </n-form-item>
          </n-grid-item>
          <n-grid-item span="4 s:4 m:2 l:2 xl:1">
            <n-form-item label="湿度(%)">
              <n-input-number
                v-model:value="form.humidity"
                :min="0"
                :max="100"
                placeholder="湿度"
                style="width: 100%;"
              />
            </n-form-item>
          </n-grid-item>
          <n-grid-item span="4 s:4 m:2 l:2 xl:1">
            <n-form-item label="压力(kPa)">
              <n-input-number
                v-model:value="form.pressure"
                :min="0"
                placeholder="压力"
                style="width: 100%;"
              />
            </n-form-item>
          </n-grid-item>
          <n-grid-item span="4 s:4 m:2 l:2 xl:1">
            <n-form-item label="干燥剂(g)">
              <n-input-number
                v-model:value="form.desiccant_weight"
                :min="0"
                placeholder="干燥剂重量"
                style="width: 100%;"
              />
            </n-form-item>
          </n-grid-item>
        </n-grid>

        <n-divider class="modal-divider"><span class="divider-label">工艺流程</span></n-divider>
        <n-form-item label="预处理">
          <n-input
            v-model:value="form.pretreatment"
            type="textarea"
            placeholder="描述预处理方法，如花材挑选、脱色、固定等..."
            :autosize="{ minRows: 3, maxRows: 6 }"
          />
        </n-form-item>
        <n-form-item label="制作步骤">
          <div class="steps-list">
            <div v-for="(step, idx) in form.steps" :key="idx" class="step-item">
              <span class="step-index">{{ idx + 1 }}</span>
              <n-input
                v-model:value="form.steps[idx]"
                :placeholder="`第${idx + 1}步...`"
                round
                clearable
              />
              <n-button
                v-if="form.steps.length > 1"
                quaternary
                circle
                size="small"
                @click="removeStep(idx)"
                style="color: #C08990;"
              >
                <template #icon><n-icon :component="RemoveOutline" /></template>
              </n-button>
            </div>
            <n-button
              dashed
              round
              style="width: 100%; color: #D4A5A5;"
              @click="addStep"
            >
              <template #icon><n-icon :component="AddOutline" /></template>
              添加步骤
            </n-button>
          </div>
        </n-form-item>

        <n-divider class="modal-divider"><span class="divider-label">效果评估</span></n-divider>
        <n-grid :cols="4" responsive="screen" :x-gap="16" :y-gap="6">
          <n-grid-item span="4 s:4 m:2 l:2 xl:1">
            <n-form-item label="保色效果">
              <n-select
                v-model:value="form.color_retention"
                :options="effectOptions"
                clearable
                placeholder="选择等级"
              />
            </n-form-item>
          </n-grid-item>
          <n-grid-item span="4 s:4 m:2 l:2 xl:1">
            <n-form-item label="保型效果">
              <n-select
                v-model:value="form.shape_retention"
                :options="effectOptions"
                clearable
                placeholder="选择等级"
              />
            </n-form-item>
          </n-grid-item>
          <n-grid-item span="4 s:4 m:4 l:2 xl:2">
            <n-form-item label="成品率(%)">
              <n-input-number
                v-model:value="form.yield_rate"
                :min="0"
                :max="100"
                placeholder="0-100之间"
                style="width: 100%;"
              />
            </n-form-item>
          </n-grid-item>
        </n-grid>

        <n-divider class="modal-divider"><span class="divider-label">其他</span></n-divider>
        <n-form-item label="备注">
          <n-input
            v-model:value="form.notes"
            type="textarea"
            placeholder="补充记录、注意事项、心得..."
            :autosize="{ minRows: 3, maxRows: 5 }"
          />
        </n-form-item>
      </n-form>

      <template #footer>
        <n-space justify="end">
          <n-button round :disabled="modalLoading" @click="showModal = false">取消</n-button>
          <n-button
            type="primary"
            round
            :loading="modalLoading"
            @click="handleSubmit"
          >
            {{ editingId ? '保存修改' : '确认创建' }}
          </n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<style lang="scss" scoped>
.drying-wrapper {
  background: transparent;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
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

.create-btn {
  background: linear-gradient(135deg, #D4A5A5, #E8B4B8);
  border: none;
  box-shadow: 0 4px 16px rgba(212, 165, 165, 0.35);

  &:hover {
    background: linear-gradient(135deg, #C08990, #D4A5A5);
    box-shadow: 0 6px 22px rgba(192, 137, 144, 0.4);
  }
}

.stats-section {
  margin-bottom: 24px;
}

.stat-card {
  position: relative;
  border-radius: 16px;
  padding: 20px;
  border: 1px solid rgba(240, 230, 222, 0.8);
  overflow: hidden;
  transition: all 0.3s ease;
  box-shadow: 0 4px 20px rgba(212, 165, 165, 0.1);
  min-height: 112px;

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 10px 32px rgba(212, 165, 165, 0.22);
  }
}

.stat-card-bg {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
}

.bg-flower {
  position: absolute;
  font-size: 52px;
  opacity: 0.07;
  color: #C08990;

  &.bg-flower-1 {
    top: -10px;
    right: -5px;
    transform: rotate(20deg);
  }

  &.bg-flower-2 {
    bottom: -15px;
    left: -8px;
    transform: rotate(-15deg);
    font-size: 42px;
  }
}

.stat-card-inner {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon-wrap {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-info {
  flex: 1;
  min-width: 0;
}

.stat-title {
  font-size: 13px;
  color: #8B7D7B;
  margin-bottom: 6px;
  font-weight: 500;
}

.stat-value {
  font-size: 30px;
  font-weight: 700;
  line-height: 1.1;
  font-family: 'Segoe UI', -apple-system, sans-serif;
  letter-spacing: -0.5px;
}

.filter-card {
  background: #FFFDF6;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(212, 165, 165, 0.1);
  border: 1px solid rgba(240, 230, 222, 0.8) !important;
  margin-bottom: 24px;
  position: relative;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 3px;
    background: linear-gradient(90deg, #D4A5A5, #F5E6A3, #A8C3A0);
    opacity: 0.5;
    border-radius: 16px 16px 0 0;
  }
}

.list-section {
  margin-bottom: 20px;
}

.empty-state {
  padding: 80px 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
  color: #B8A8A6;
  font-size: 14px;
}

.empty-card {
  background: #FFFDF6;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(212, 165, 165, 0.08);
  border: 1px solid rgba(240, 230, 222, 0.8) !important;
  padding: 30px;
}

.loading-spinner {
  width: 28px;
  height: 28px;
  border: 3px solid rgba(212, 165, 165, 0.2);
  border-top-color: #D4A5A5;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.process-card {
  background: linear-gradient(145deg, #FFFDF6 0%, #FFFBF0 100%);
  border-radius: 18px;
  box-shadow: 0 4px 20px rgba(212, 165, 165, 0.1);
  border: 1px solid rgba(240, 230, 222, 0.8) !important;
  position: relative;
  overflow: hidden;
  height: 100%;
  display: flex;
  flex-direction: column;

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
    border-color: rgba(212, 165, 165, 0.35) !important;
  }

  :deep(.n-card__content) {
    padding: 20px !important;
    height: 100%;
    display: flex;
    flex-direction: column;
  }
}

.card-header-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}

.card-title-row {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
  min-width: 0;
}

.process-name {
  font-size: 17px;
  font-weight: 700;
  color: #5C4A4A;
  line-height: 1.4;
  flex: 1;
  min-width: 0;
}

.card-divider {
  margin: 14px 0 !important;
  border-color: rgba(240, 230, 222, 0.6) !important;
}

.info-block {
  margin-bottom: 14px;
}

.info-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 8px;

  &:last-child {
    margin-bottom: 0;
  }
}

.info-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
}

.info-label {
  color: #8B7D7B;
  font-weight: 500;
}

.soft-tag {
  border: none !important;
  font-size: 11px !important;

  &.tag-pink {
    background: rgba(212, 165, 165, 0.18);
    color: #C08990;
  }

  &.tag-yellow {
    background: rgba(245, 200, 107, 0.2);
    color: #C49B3A;
  }

  &.tag-green {
    background: rgba(168, 195, 160, 0.2);
    color: #8BA888;
  }

  &.tag-blue {
    background: rgba(139, 168, 195, 0.2);
    color: #768CA3;
  }
}

.params-row {
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
  padding: 12px 14px;
  background: linear-gradient(135deg, rgba(250, 246, 238, 0.8), rgba(255, 248, 227, 0.6));
  border-radius: 12px;
  margin-bottom: 14px;
  border: 1px solid rgba(240, 230, 222, 0.5);
}

.param-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.param-value {
  font-size: 13px;
  font-weight: 600;
  color: #5C4A4A;
}

.effect-block {
  flex: 1;
  margin-bottom: 14px;
  padding: 14px;
  background: #FFFBF4;
  border-radius: 12px;
  border: 1px dashed rgba(240, 230, 222, 0.7);
}

.effect-row {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 12px;
}

.effect-item {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 100px;
}

.effect-label {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  color: #8B7D7B;
  font-weight: 500;
}

.empty-val {
  color: #B8A8A6;
  font-size: 13px;
}

.yield-section {
  margin-bottom: 10px;
  padding: 10px 12px;
  background: rgba(168, 195, 160, 0.1);
  border-radius: 10px;
}

.yield-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.yield-label {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  color: #8B7D7B;
  font-weight: 500;
}

.yield-value {
  font-size: 14px;
  font-weight: 700;
}

.output-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: rgba(212, 165, 165, 0.1);
  border-radius: 10px;
}

.output-label {
  font-size: 12px;
  color: #8B7D7B;
  font-weight: 500;
}

.output-value {
  font-size: 14px;
  font-weight: 700;
  color: #C08990;
  margin-left: auto;
}

.card-footer {
  display: flex;
  gap: 8px;
  padding-top: 14px;
  border-top: 1px dashed rgba(240, 230, 222, 0.7);
  margin-top: auto;
  justify-content: flex-end;
  flex-wrap: wrap;
}

.pagination-wrap {
  display: flex;
  justify-content: center;
  padding: 28px 0 10px;
}

.modal-divider {
  margin: 6px 0 16px !important;
  border-color: rgba(240, 230, 222, 0.6) !important;
}

.divider-label {
  font-size: 13px;
  font-weight: 600;
  color: #C08990;
  padding: 0 12px;
}

.form-modal {
  :deep(.n-card) {
    background: #FFFDF6;
    border-radius: 18px;
    box-shadow: 0 12px 50px rgba(212, 165, 165, 0.25);
    border: 1px solid rgba(240, 230, 222, 0.8);
  }

  :deep(.n-card-header) {
    border-bottom: 1px solid rgba(240, 230, 222, 0.7);
    padding: 20px 26px;
  }

  :deep(.n-card__header-title) {
    color: #5C4A4A;
    font-weight: 700;
    font-size: 17px;
    display: flex;
    align-items: center;
    gap: 10px;

    &::before {
      content: '';
      width: 4px;
      height: 18px;
      background: linear-gradient(180deg, #D4A5A5, #F5E6A3);
      border-radius: 2px;
    }
  }

  :deep(.n-card__content) {
    padding: 8px 26px 10px;
  }

  :deep(.n-card-footer) {
    border-top: 1px solid rgba(240, 230, 222, 0.7);
    padding: 16px 26px;
  }

  :deep(.n-form-item-label) {
    color: #8B7D7B !important;
    font-weight: 500;
  }
}

.steps-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  width: 100%;
}

.step-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.step-index {
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
}
</style>
