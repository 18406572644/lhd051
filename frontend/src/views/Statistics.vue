<script setup>
import { ref, onMounted, computed, h, reactive } from 'vue'
import {
  NCard, NGrid, NGridItem, NTag, NIcon, NSpace, NButton,
  NInput, NSelect, NSwitch, NModal, NForm, NFormItem,
  NInputNumber, NDataTable, useMessage, useDialog,
  NEmpty, NPagination, NSkeleton, NStatistic
} from 'naive-ui'
import { use } from 'echarts/core'
import VChart from 'vue-echarts'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, BarChart, PieChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DataZoomComponent
} from 'echarts/components'
import {
  Time, Cash, Sparkles, TrendingUp, Library,
  Add, Search, CreateOutline, TrashOutline,
  CheckmarkCircleOutline, Calendar
} from '@vicons/ionicons5'
import { statisticsApi, consumptionsApi, dryingApi, materialsApi } from '@/api'

use([
  CanvasRenderer,
  LineChart,
  BarChart,
  PieChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DataZoomComponent
])

const message = useMessage()
const dialog = useDialog()

const loading = ref(false)
const mainStatsLoading = ref(false)
const tableLoading = ref(false)
const consumptionList = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)

const mainStats = ref({
  total_production_hours: 0,
  total_consumption_cost: 0,
  avg_unit_cost: 0,
  avg_production_time: 0
})

const trendData = ref([])
const consumptionSummary = ref([])
const dryingMethodStats = ref([])
const monthlyData = ref([])

const showAddModal = ref(false)
const formRef = ref(null)
const formMode = ref('create')

const consumptionCategories = ref([])
const dryingOptions = ref([])
const materialOptions = ref([])

const formData = reactive({
  id: null,
  name: '',
  category: null,
  quantity: 1,
  unit: '',
  unit_price: 0,
  drying_process_id: null,
  material_id: null,
  remark: ''
})

const formRules = {
  name: { required: true, message: '请输入耗材名称', trigger: 'blur' }
}

async function loadMainStats() {
  mainStatsLoading.value = true
  try {
    const [mainRes, trendRes] = await Promise.all([
      statisticsApi.main(),
      statisticsApi.trend()
    ])
    if (mainRes?.data) {
      mainStats.value = {
        total_production_hours: mainRes.data.total_production_hours ?? mainRes.data.total_hours ?? 0,
        total_consumption_cost: mainRes.data.total_consumption_cost ?? mainRes.data.total_cost ?? 0,
        avg_unit_cost: mainRes.data.avg_unit_cost ?? 0,
        avg_production_time: mainRes.data.avg_production_time ?? 0
      }
    }
    if (trendRes?.data) {
      trendData.value = trendRes.data.daily_trend || trendRes.data.trend || []
      dryingMethodStats.value = trendRes.data.drying_methods || []
      monthlyData.value = trendRes.data.monthly || []
    }
  } catch (e) {
    message.error('加载统计数据失败')
  } finally {
    mainStatsLoading.value = false
  }
}

async function loadConsumptionSummary() {
  try {
    const res = await consumptionsApi.summary()
    if (res?.data) {
      consumptionSummary.value = res.data.categories || res.data || []
    }
  } catch (e) {}
}

async function loadOptions() {
  try {
    const [catRes] = await Promise.all([
      consumptionsApi.categories()
    ])
    if (catRes?.data?.categories) {
      consumptionCategories.value = catRes.data.categories.map(c => ({ label: c, value: c }))
    }
  } catch (e) {}
  try {
    const dryRes = await dryingApi.list({ page: 1, page_size: 100 })
    const items = dryRes?.data?.items || dryRes?.data || []
    dryingOptions.value = items.map(d => ({
      label: d.process_name || '未命名',
      value: d.id
    }))
  } catch (e) {}
  try {
    const matRes = await materialsApi.list({ page: 1, page_size: 100 })
    const mats = matRes?.data?.items || matRes?.data || []
    materialOptions.value = mats.map(m => ({
      label: m.name || '未命名',
      value: m.id
    }))
  } catch (e) {}
}

async function loadConsumptionList() {
  tableLoading.value = true
  try {
    const res = await consumptionsApi.list({
      page: page.value,
      page_size: pageSize.value
    })
    if (res?.data?.items) {
      consumptionList.value = res.data.items
      total.value = res.data.total || 0
    } else if (res?.data) {
      consumptionList.value = Array.isArray(res.data) ? res.data : []
      total.value = consumptionList.value.length
    }
  } catch (e) {
    message.error('加载耗材记录失败')
  } finally {
    tableLoading.value = false
  }
}

function openCreate() {
  formMode.value = 'create'
  Object.assign(formData, {
    id: null,
    name: '',
    category: null,
    quantity: 1,
    unit: '',
    unit_price: 0,
    drying_process_id: null,
    material_id: null,
    remark: ''
  })
  showAddModal.value = true
}

function openEdit(item) {
  formMode.value = 'edit'
  Object.assign(formData, {
    id: item.id,
    name: item.name || '',
    category: item.category || null,
    quantity: item.quantity || 1,
    unit: item.unit || '',
    unit_price: item.unit_price || 0,
    drying_process_id: item.drying_process_id || null,
    material_id: item.material_id || null,
    remark: item.remark || ''
  })
  showAddModal.value = true
}

function handleFormSubmit() {
  formRef.value?.validate(async (errors) => {
    if (errors) return
    try {
      const payload = { ...formData }
      delete payload.id
      if (formMode.value === 'create') {
        await consumptionsApi.create(payload)
        message.success('添加成功')
      } else {
        await consumptionsApi.update(formData.id, payload)
        message.success('更新成功')
      }
      showAddModal.value = false
      loadConsumptionList()
      loadMainStats()
      loadConsumptionSummary()
    } catch (e) {
      message.error(formMode.value === 'create' ? '添加失败' : '更新失败')
    }
  })
}

function handleDelete(item) {
  dialog.warning({
    title: '确认删除',
    content: `确定要删除耗材记录「${item.name}」吗？`,
    positiveText: '删除',
    negativeText: '取消',
    positiveButtonProps: { color: '#E88A9A' },
    onPositiveClick: async () => {
      try {
        await consumptionsApi.delete(item.id)
        message.success('删除成功')
        loadConsumptionList()
        loadMainStats()
        loadConsumptionSummary()
      } catch (e) {
        message.error('删除失败')
      }
    }
  })
}

function handlePageChange(p) {
  page.value = p
  loadConsumptionList()
}

function formatMoney(val) {
  return '¥' + Number(val || 0).toFixed(2)
}

function formatNumber(val, decimals = 0) {
  return Number(val || 0).toFixed(decimals)
}

const pieColors = ['#E8B4B8', '#F5E6A3', '#A8C3A0', '#D4A06B', '#B8C8D4', '#F5C86B']

const statCards = computed(() => [
  {
    title: '总制作时长',
    key: 'total_production_hours',
    suffix: ' 小时',
    icon: Time,
    gradient: "linear-gradient(135deg, rgba(232, 180, 184, 0.18), rgba(212, 165, 165, 0.12))",
    accent: '#E88A9A'
  },
  {
    title: '总耗材成本',
    key: 'total_consumption_cost',
    prefix: '¥',
    icon: Cash,
    gradient: "linear-gradient(135deg, rgba(245, 230, 163, 0.22), rgba(245, 200, 107, 0.15))",
    accent: '#E8B460'
  },
  {
    title: '平均单件成本',
    key: 'avg_unit_cost',
    prefix: '¥',
    icon: Sparkles,
    gradient: "linear-gradient(135deg, rgba(168, 195, 160, 0.18), rgba(139, 168, 136, 0.12))",
    accent: '#8BA888'
  },
  {
    title: '平均制作时长',
    key: 'avg_production_time',
    suffix: ' 小时',
    icon: TrendingUp,
    gradient: "linear-gradient(135deg, rgba(212, 160, 107, 0.18), rgba(184, 200, 212, 0.15))",
    accent: '#8BA8C3'
  }
])

const trendLineOption = computed(() => ({
  title: {
    text: '近14天入库与制作趋势',
    left: 'center',
    top: 10,
    textStyle: {
      color: '#5C4A4A',
      fontSize: 15,
      fontWeight: 600
    }
  },
  tooltip: {
    trigger: 'axis',
    axisPointer: { type: 'cross' }
  },
  legend: {
    bottom: 10,
    data: ['入库数量',
    '制作数量'],
    textStyle: { color: '#8B7D7B' }
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '18%',
    top: '18%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    boundaryGap: false,
    data: trendData.value.length > 0
      ? trendData.value.map(d => d.date?.slice(5) || d.label || '')
      : ['暂无数据'],
    axisLine: { lineStyle: { color: '#F0E6DE' } },
    axisLabel: { color: '#8B7D7B', fontSize: 11 },
    axisTick: { show: false }
  },
  yAxis: {
    type: 'value',
    axisLine: { show: false },
    axisLabel: { color: '#8B7D7B', fontSize: 11 },
    splitLine: { lineStyle: { color: '#F5EEE8', type: 'dashed' } }
  },
  series: [
    {
      name: '入库数量',
      type: 'line',
      smooth: true,
      symbol: 'circle',
      symbolSize: 6,
      lineStyle: { width: 3,
        color: '#D4A5A5'
      },
      itemStyle: { color: '#D4A5A5' },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: "rgba(212, 165, 165, 0.45)" },
            { offset: 1, color: "rgba(212, 165, 165, 0.05)" }
          ]
        }
      },
      data: trendData.value.length > 0
        ? trendData.value.map(d => d.material_count || d.in_count || 0)
        : [0]
    },
    {
      name: '制作数量',
      type: 'line',
      smooth: true,
      symbol: 'circle',
      symbolSize: 6,
      lineStyle: { width: 3, color: '#A8C3A0' },
      itemStyle: { color: '#A8C3A0' },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: "rgba(168, 195, 160, 0.45)" },
            { offset: 1, color: "rgba(168, 195, 160, 0.05)" }
          ]
        }
      },
      data: trendData.value.length > 0
        ? trendData.value.map(d => d.drying_count || d.make_count || 0)
        : [0]
    }
  ]
}))

const consumptionBarOption = computed(() => ({
  title: {
    text: '耗材成本按分类',
    left: 'center',
    top: 10,
    textStyle: {
      color: '#5C4A4A',
      fontSize: 15,
      fontWeight: 600
    }
  },
  tooltip: {
    trigger: 'axis',
    axisPointer: { type: 'shadow' }
  },
  legend: {
    bottom: 10,
    data: ['成本'],
    textStyle: { color: '#8B7D7B' }
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '18%',
    top: '18%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    data: consumptionSummary.value.length > 0
      ? consumptionSummary.value.map(s => s.name || s.category || '')
      : ['暂无数据'],
    axisLine: { lineStyle: { color: '#F0E6DE' } },
    axisLabel: { color: '#8B7D7B', fontSize: 11 },
    axisTick: { show: false }
  },
  yAxis: {
    type: 'value',
    axisLine: { show: false },
    axisLabel: { color: '#8B7D7B', fontSize: 11 },
    splitLine: { lineStyle: { color: '#F5EEE8', type: 'dashed' } }
  },
  series: [
    {
      name: '成本',
      type: 'bar',
      barWidth: '55%',
      itemStyle: {
        borderRadius: [8, 8, 0, 0],
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: '#F5C86B' },
            { offset: 1, color: '#F5E6A3' }
          ]
        }
      },
      emphasis: {
        itemStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: '#E8B460' },
              { offset: 1, color: '#F0D680' }
            ]
          }
        }
      },
      data: consumptionSummary.value.length > 0
        ? consumptionSummary.value.map(s => s.total_cost || s.cost || s.value || 0)
        : [0]
    }
  ]
}))

const methodPieOption = computed(() => ({
  title: {
    text: '制作时长按方法分布',
    left: 'center',
    top: 10,
    textStyle: {
      color: '#5C4A4A',
      fontSize: 15,
      fontWeight: 600
    }
  },
  tooltip: {
    trigger: 'item',
    formatter: '{b}: {c}小时 ({d}%)'
  },
  legend: {
    bottom: 10,
    left: 'center',
    textStyle: { color: '#8B7D7B' }
  },
  series: [
    {
      type: 'pie',
      radius: ['38%', '68%'],
      center: ['50%', '50%'],
      avoidLabelOverlap: true,
      itemStyle: {
        borderRadius: 10,
        borderColor: '#FFFDF6',
        borderWidth: 3
      },
      label: {
        show: true,
        formatter: '{b}\n{d}%',
        color: '#5C4A4A',
        fontSize: 11
      },
      labelLine: {
        lineStyle: { color: '#D4B8B0' }
      },
      emphasis: {
        scale: true,
        scaleSize: 6,
        itemStyle: {
          shadowBlur: 20,
          shadowOffsetX: 0,
          shadowColor: "rgba(212, 165, 165, 0.4)"
        }
      },
      data: dryingMethodStats.value.length > 0
        ? dryingMethodStats.value.map((item, index) => ({
          value: item.total_hours || item.hours || item.count || 0,
          name: item.name || item.method || '未知',
          itemStyle: { color: pieColors[index % pieColors.length] }
        }))
        : [{ value: 1, name: '暂无数据', itemStyle: { color: '#E8E0DC' } }]
    }
  ]
}))

const monthlyComboOption = computed(() => ({
  title: {
    text: '每月成本与工时',
    left: 'center',
    top: 10,
    textStyle: {
      color: '#5C4A4A',
      fontSize: 15,
      fontWeight: 600
    }
  },
  tooltip: {
    trigger: 'axis',
    axisPointer: { type: 'cross' }
  },
  legend: {
    bottom: 10,
    data: ['耗材成本', '制作时长'],
    textStyle: { color: '#8B7D7B' }
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '18%',
    top: '18%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    data: monthlyData.value.length > 0
      ? monthlyData.value.map(d => d.month || d.label || '')
      : ['暂无数据'],
    axisLine: { lineStyle: { color: '#F0E6DE' } },
    axisLabel: { color: '#8B7D7B', fontSize: 11 },
    axisTick: { show: false }
  },
  yAxis: [
    {
      type: 'value',
      name: '成本(元)',
      axisLine: { show: false },
      axisLabel: { color: '#8B7D7B', fontSize: 11 },
      splitLine: { lineStyle: { color: '#F5EEE8', type: 'dashed' } }
    },
    {
      type: 'value',
      name: '时长(h)',
      axisLine: { show: false },
      axisLabel: { color: '#8B7D7B', fontSize: 11 },
      splitLine: { show: false }
    }
  ],
  series: [
    {
      name: '耗材成本',
      type: 'bar',
      barWidth: '45%',
      itemStyle: {
        borderRadius: [8, 8, 0, 0],
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: '#E8B4B8' },
            { offset: 1, color: '#F5E6A3' }
          ]
        }
      },
      data: monthlyData.value.length > 0
        ? monthlyData.value.map(d => d.cost || d.total_cost || 0)
        : [0]
    },
    {
      name: '制作时长',
      type: 'line',
      yAxisIndex: 1,
      smooth: true,
      symbol: 'circle',
      symbolSize: 7,
      lineStyle: { width: 3, color: '#A8C3A0' },
      itemStyle: { color: '#A8C3A0' },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: "rgba(168, 195, 160, 0.35)" },
            { offset: 1, color: "rgba(168, 195, 160, 0.02)" }
          ]
        }
      },
      data: monthlyData.value.length > 0
        ? monthlyData.value.map(d => d.hours || d.total_hours || 0)
        : [0]
    }
  ]
}))

const tableColumns = computed(() => [
  {
    title: '名称',
    key: 'name',
    minWidth: 130,
    render: (row) => h('div', { style: 'font-weight: 600; color: #5C4A4A;' }, row.name || '-')
  },
  {
    title: '分类',
    key: 'category',
    width: 110,
    render: (row) => {
      if (!row.category) return h('span', { style: 'color: #B8A8A6;' }, '-')
      return h(NTag, { round: true, size: 'small', style: "background: rgba(212, 165, 165, 0.18); color: #C08990; border: none;" }, { default: () => row.category })
    }
  },
  {
    title: '数量',
    key: 'quantity',
    width: 110,
    render: (row) => h('div', { style: 'color: #5C4A4A;' }, `${row.quantity || 0} ${row.unit || ''}`)
  },
  {
    title: '单价',
    key: 'unit_price',
    width: 100,
    render: (row) => h('div', { style: 'color: #C49B3A; font-weight: 600;' }, formatMoney(row.unit_price))
  },
  {
    title: '小计',
    key: 'total',
    width: 110,
    render: (row) => h('div', { style: 'color: #E88A9A; font-weight: 600;' }, formatMoney((row.quantity || 0) * (row.unit_price || 0)))
  },
  {
    title: '关联制作',
    key: 'drying_process_id',
    width: 140,
    ellipsis: { tooltip: true },
    render: (row) => h('span', { style: 'color: #8B7D7B; font-size: 13px;' }, row.drying_process_name || '-')
  },
  {
    title: '关联原料',
    key: 'material_id',
    width: 140,
    ellipsis: { tooltip: true },
    render: (row) => h('span', { style: 'color: #8B7D7B; font-size: 13px;' }, row.material_name || '-')
  },
  {
    title: '备注',
    key: 'remark',
    minWidth: 140,
    ellipsis: { tooltip: true },
    render: (row) => h('span', { style: 'color: #8B7D7B; font-size: 13px;' }, row.remark || '-')
  },
  {
    title: '操作',
    key: 'actions',
    width: 140,
    fixed: 'right',
    render: (row) => h(NSpace, { size: 6 }, {
      default: () => [
        h(NButton, { text: true, size: 'small', type: 'primary', onClick: () => openEdit(row) }, { default: () => '编辑' }),
        h(NButton, { text: true, size: 'small', type: 'error', onClick: () => handleDelete(row) }, { default: () => '删除' })
      ]
    })
  }
])

onMounted(() => {
  loadMainStats()
  loadConsumptionSummary()
  loadOptions()
  loadConsumptionList()
})
</script>

<template>
  <div class="statistics-wrapper">
    <div class="section-header">
      <div>
        <h2 class="page-title">
          <n-icon size="26" color="#D4A5A5"><TrendingUp /></n-icon>
          时长与耗材统计
        </h2>
        <p class="page-subtitle">记录每一份用心，让时光与成本都清晰可见</p>
      </div>
      <div class="header-decor">
        <span class="flower-icon flower-1">🌿</span>
        <span class="flower-icon flower-2">📊</span>
      </div>
    </div>

    <div class="stats-section">
      <n-grid :cols="4" responsive="screen" :x-gap="18" :y-gap="18">
        <n-grid-item v-for="card in statCards" :key="card.key" span="4 m:2 l:1">
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
                  <template v-if="!mainStatsLoading">
                    {{ card.prefix || '' }}
                    <span class="stat-num">{{ formatNumber(mainStats[card.key] || 0, card.key.includes('cost') ? 2 : 1) }}</span>
                    {{ card.suffix || '' }}
                  </template>
                  <template v-else>
                    <span style="font-size: 20px;">--</span>
                  </template>
                </div>
              </div>
            </div>
          </div>
        </n-grid-item>
      </n-grid>
    </div>

    <div class="charts-section">
      <n-grid :cols="2" responsive="screen" :x-gap="18" :y-gap="18">
        <n-grid-item span="2 m:2 l:1">
          <n-card class="chart-card" size="large" :bordered="false">
            <v-chart :option="trendLineOption" style="height: 340px;" autoresize />
          </n-card>
        </n-grid-item>
        <n-grid-item span="2 m:2 l:1">
          <n-card class="chart-card" size="large" :bordered="false">
            <v-chart :option="consumptionBarOption" style="height: 340px;" autoresize />
          </n-card>
        </n-grid-item>
        <n-grid-item span="2 m:2 l:1">
          <n-card class="chart-card" size="large" :bordered="false">
            <v-chart :option="methodPieOption" style="height: 340px;" autoresize />
          </n-card>
        </n-grid-item>
        <n-grid-item span="2 m:2 l:1">
          <n-card class="chart-card" size="large" :bordered="false">
            <v-chart :option="monthlyComboOption" style="height: 340px;" autoresize />
          </n-card>
        </n-grid-item>
      </n-grid>
    </div>

    <n-card class="table-section" size="large" :bordered="false">
      <template #header>
        <div class="table-header">
          <div class="card-title-wrap">
            <span class="title-bar"></span>
            <span class="card-title">
              <n-icon size="18" color="#F5C86B"><Library /></n-icon>
              耗材记录
            </span>
          </div>
          <n-button type="primary" size="medium" @click="openCreate">
            <template #icon><n-icon :component="Add" /></template>
            新增记录
          </n-button>
        </div>
      </template>

      <div v-if="tableLoading" class="empty-state">
        <n-skeleton :repeat="3" text :row="2" style="max-width: 800px; margin: 0 auto;" />
      </div>

      <n-data-table
        v-else
        :columns="tableColumns"
        :data="consumptionList"
        :bordered="false"
        size="medium"
        :pagination="false"
        style="background: transparent;"
      />

      <div class="pagination-wrap">
        <n-pagination
          v-model:page="page"
          v-model:page-size="pageSize"
          :item-count="total"
          :page-sizes="[10, 20, 50, 100]"
          show-size-picker
          show-quick-jumper
          @update:page="handlePageChange"
        />
      </div>
    </n-card>

    <n-modal
      v-model:show="showAddModal"
      preset="card"
      :title="formMode === 'create' ? '新增耗材记录' : '编辑耗材记录'"
      style="width: 640px; max-width: 92vw;"
      :mask-closable="false"
      class="form-modal"
    >
      <n-form ref="formRef" :model="formData" :rules="formRules" label-placement="left" label-width="100px">
        <n-grid :cols="2" :x-gap="16" :y-gap="4">
          <n-grid-item span="2 s:2 m:1">
            <n-form-item label="名称" path="name">
              <n-input v-model:value="formData.name" placeholder="请输入耗材名称" maxlength="100" />
            </n-form-item>
          </n-grid-item>
          <n-grid-item span="2 s:2 m:1">
            <n-form-item label="分类">
              <n-select
                v-model:value="formData.category"
                :options="consumptionCategories"
                placeholder="选择分类"
                clearable
              />
            </n-form-item>
          </n-grid-item>
          <n-grid-item span="2 s:2 m:1">
            <n-form-item label="数量">
              <n-input-number v-model:value="formData.quantity" :min="0" :precision="2" style="width: 100%;" />
            </n-form-item>
          </n-grid-item>
          <n-grid-item span="2 s:2 m:1">
            <n-form-item label="单位">
              <n-input v-model:value="formData.unit" placeholder="如：个、ml、g" maxlength="20" />
            </n-form-item>
          </n-grid-item>
          <n-grid-item span="2 s:2 m:1">
            <n-form-item label="单价">
              <n-input-number v-model:value="formData.unit_price" :min="0" :precision="2" style="width: 100%;" />
            </n-form-item>
          </n-grid-item>
          <n-grid-item span="2 s:2 m:1">
            <n-form-item label="关联制作">
              <n-select
                v-model:value="formData.drying_process_id"
                :options="dryingOptions"
                placeholder="选择制作记录"
                clearable
                filterable
              />
            </n-form-item>
          </n-grid-item>
          <n-grid-item span="2 s:2 m:2">
            <n-form-item label="关联原料">
              <n-select
                v-model:value="formData.material_id"
                :options="materialOptions"
                placeholder="选择原料"
                clearable
                filterable
              />
            </n-form-item>
          </n-grid-item>
        </n-grid>
        <n-form-item label="备注" label-placement="top" style="margin-top: 4px;">
          <n-input v-model:value="formData.remark" type="textarea" :rows="3" placeholder="填写备注信息..." maxlength="500" />
        </n-form-item>
      </n-form>
      <template #footer>
        <NSpace justify="end">
          <n-button @click="showAddModal = false">取消</n-button>
          <n-button type="primary" @click="handleFormSubmit">
            <template #icon><n-icon :component="CheckmarkCircleOutline" /></template>
            {{ formMode === 'create' ? '添加' : '保存' }}
          </n-button>
        </NSpace>
      </template>
    </n-modal>
  </div>
</template>

<style lang="scss" scoped>
.statistics-wrapper { background: transparent; }

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
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

.header-decor {
  position: relative;
  width: 80px;
  height: 50px;
}

.flower-icon {
  position: absolute;
  font-size: 26px;
  opacity: 0.6;
  animation: float 4s ease-in-out infinite;

  &.flower-1 {
    top: 0;
    right: 40px;
    animation-delay: 0s;
  }

  &.flower-2 {
    top: 12px;
    right: 0;
    animation-delay: 0.8s;
    font-size: 22px;
  }
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-6px); }
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
  font-size: 48px;
  opacity: 0.07;
  color: #C08990;

  &.bg-flower-1 {
    top: -8px;
    right: -5px;
    transform: rotate(20deg);
  }

  &.bg-flower-2 {
    bottom: -12px;
    left: -6px;
    transform: rotate(-15deg);
    font-size: 38px;
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
  backdrop-filter: blur(8px);
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
  font-size: 26px;
  font-weight: 700;
  line-height: 1.1;
  font-family: 'Segoe UI', -apple-system, sans-serif;
  letter-spacing: -0.5px;
}

.charts-section {
  margin-bottom: 24px;
}

.chart-card {
  background: #FFFDF6;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(212, 165, 165, 0.1);
  border: 1px solid rgba(240, 230, 222, 0.8) !important;
  position: relative;
  overflow: hidden;

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
}

.table-section {
  background: #FFFDF6;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(212, 165, 165, 0.1);
  border: 1px solid rgba(240, 230, 222, 0.8) !important;
  position: relative;
  margin-bottom: 20px;

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

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title-wrap {
  display: flex;
  align-items: center;
  gap: 10px;
}

.title-bar {
  width: 4px;
  height: 18px;
  background: linear-gradient(180deg, #D4A5A5, #F5E6A3);
  border-radius: 2px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #5C4A4A;
  display: flex;
  align-items: center;
  gap: 8px;
}

.empty-state {
  padding: 40px 20px;
}

.pagination-wrap {
  display: flex;
  justify-content: center;
  padding: 16px 0 8px;
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
</style>
