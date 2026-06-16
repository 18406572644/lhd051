<script setup>
import { ref, onMounted, computed, h } from 'vue'
import {
  NCard, NGrid, NGridItem, NTag, NIcon, NSpace, NList, NListItem,
  NAvatar, useMessage, NEllipsis
} from 'naive-ui'
import { use } from 'echarts/core'
import VChart from 'vue-echarts'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart, PieChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components'
import {
  Flower, Sparkles, FlowerOutline, Book, ColorPalette, Heart,
  Eye, Calendar
} from '@vicons/ionicons5'
import { statisticsApi, specimensApi, notesApi } from '@/api'

use([
  CanvasRenderer,
  BarChart,
  PieChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
])

const message = useMessage()

const statsLoading = ref(false)
const specimensLoading = ref(false)
const notesLoading = ref(false)

const stats = ref({
  total_materials: 0,
  total_drying: 0,
  total_specimens: 0,
  total_notes: 0,
  total_plans: 0,
  total_likes: 0
})

const trendData = ref({
  material_categories: [],
  specimen_categories: [],
  monthly_trend: [],
  drying_methods: []
})

const featuredSpecimens = ref([])
const latestNotes = ref([])

const statCards = computed(() => [
  {
    title: '原料总数',
    key: 'total_materials',
    icon: Flower,
    gradient: 'linear-gradient(135deg, rgba(212,165,165,0.15), rgba(245,230,163,0.25))',
    accent: '#D4A5A5'
  },
  {
    title: '制作总数',
    key: 'total_processes',
    icon: Sparkles,
    gradient: 'linear-gradient(135deg, rgba(245,230,163,0.2), rgba(168,195,160,0.15))',
    accent: '#F5C86B'
  },
  {
    title: '标本总数',
    key: 'total_specimens',
    icon: FlowerOutline,
    gradient: 'linear-gradient(135deg, rgba(168,195,160,0.18), rgba(212,165,165,0.15))',
    accent: '#A8C3A0'
  },
  {
    title: '笔记数',
    key: 'total_notes',
    icon: Book,
    gradient: 'linear-gradient(135deg, rgba(212,165,165,0.18), rgba(245,230,163,0.2))',
    accent: '#C08990'
  },
  {
    title: '设计方案',
    key: 'total_plans',
    icon: ColorPalette,
    gradient: 'linear-gradient(135deg, rgba(245,230,163,0.22), rgba(212,165,165,0.18))',
    accent: '#D4A06B'
  },
  {
    title: '总点赞',
    key: 'total_likes',
    icon: Heart,
    gradient: 'linear-gradient(135deg, rgba(212,165,165,0.22), rgba(245,230,163,0.18))',
    accent: '#E88A9A'
  }
])

const materialPieOption = computed(() => ({
  title: {
    text: '原料分类占比',
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
    formatter: '{b}: {c} ({d}%)'
  },
  legend: {
    bottom: 10,
    left: 'center',
    textStyle: { color: '#8B7D7B' }
  },
  series: [
    {
      type: 'pie',
      radius: ['35%', '65%'],
      center: ['50%', '50%'],
      avoidLabelOverlap: true,
      itemStyle: {
        borderRadius: 8,
        borderColor: '#FFFDF6',
        borderWidth: 2
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
          shadowColor: 'rgba(212,165,165,0.4)'
        }
      },
      data: trendData.value.material_categories.length > 0
        ? trendData.value.material_categories.map((item, index) => ({
            value: item.count,
            name: item.name,
            itemStyle: { color: pieColors[index % pieColors.length] }
          }))
        : [{ value: 1, name: '暂无数据', itemStyle: { color: '#E8E0DC' } }]
    }
  ]
}))

const specimenPieOption = computed(() => ({
  title: {
    text: '标本分类分布',
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
    formatter: '{b}: {c} ({d}%)'
  },
  legend: {
    bottom: 10,
    left: 'center',
    textStyle: { color: '#8B7D7B' }
  },
  series: [
    {
      type: 'pie',
      radius: '60%',
      center: ['50%', '50%'],
      roseType: 'radius',
      itemStyle: {
        borderRadius: 6,
        borderColor: '#FFFDF6',
        borderWidth: 2
      },
      label: {
        show: true,
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
          shadowColor: 'rgba(168,195,160,0.4)'
        }
      },
      data: trendData.value.specimen_categories.length > 0
        ? trendData.value.specimen_categories.map((item, index) => ({
            value: item.count,
            name: item.name,
            itemStyle: { color: pieColors2[index % pieColors2.length] }
          }))
        : [{ value: 1, name: '暂无数据', itemStyle: { color: '#E8E0DC' } }]
    }
  ]
}))

const monthlyBarOption = computed(() => ({
  title: {
    text: '月度制作趋势',
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
    data: ['制作数量'],
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
    data: trendData.value.monthly_trend.length > 0
      ? trendData.value.monthly_trend.map(item => item.month)
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
      name: '制作数量',
      type: 'bar',
      barWidth: '50%',
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
      emphasis: {
        itemStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: '#D4A5A5' },
              { offset: 1, color: '#F0D680' }
            ]
          }
        }
      },
      data: trendData.value.monthly_trend.length > 0
        ? trendData.value.monthly_trend.map(item => item.count)
        : [0]
    }
  ]
}))

const methodDonutOption = computed(() => ({
  title: {
    text: '制作方法占比',
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
    formatter: '{b}: {c} ({d}%)'
  },
  legend: {
    bottom: 10,
    left: 'center',
    textStyle: { color: '#8B7D7B' }
  },
  series: [
    {
      type: 'pie',
      radius: ['45%', '70%'],
      center: ['50%', '50%'],
      avoidLabelOverlap: true,
      itemStyle: {
        borderRadius: 10,
        borderColor: '#FFFDF6',
        borderWidth: 3
      },
      label: {
        show: true,
        position: 'outside',
        formatter: '{b}\n{d}%',
        color: '#5C4A4A',
        fontSize: 11
      },
      labelLine: {
        lineStyle: { color: '#D4B8B0' },
        length: 10,
        length2: 8
      },
      emphasis: {
        scale: true,
        scaleSize: 5,
        itemStyle: {
          shadowBlur: 20,
          shadowOffsetX: 0,
          shadowColor: 'rgba(245,200,107,0.4)'
        }
      },
      data: trendData.value.drying_methods.length > 0
        ? trendData.value.drying_methods.map((item, index) => ({
            value: item.count,
            name: item.name,
            itemStyle: { color: donutColors[index % donutColors.length] }
          }))
        : [{ value: 1, name: '暂无数据', itemStyle: { color: '#E8E0DC' } }]
    }
  ]
}))

const pieColors = ['#D4A5A5', '#F5E6A3', '#A8C3A0', '#E8B4B8', '#D4A06B', '#B8C8D4']
const pieColors2 = ['#A8C3A0', '#F5C86B', '#D4A5A5', '#8BA888', '#C08990', '#E8D4A0']
const donutColors = ['#F5C86B', '#D4A5A5', '#A8C3A0', '#8BA8C3', '#C08990', '#D4A06B']

function getDifficultyColor(level) {
  const map = {
    '入门': { bg: 'rgba(168,195,160,0.2)', text: '#8BA888' },
    '简单': { bg: 'rgba(245,200,107,0.2)', text: '#C49B3A' },
    '中等': { bg: 'rgba(232,180,184,0.25)', text: '#C08990' },
    '困难': { bg: 'rgba(192,137,144,0.25)', text: '#A85F68' },
    '大师': { bg: 'rgba(166,140,109,0.25)', text: '#8B6E50' }
  }
  return map[level] || { bg: 'rgba(212,165,165,0.15)', text: '#8B7D7B' }
}

async function loadStats() {
  statsLoading.value = true
  try {
    const [mainRes, trendRes] = await Promise.all([
      statisticsApi.main(),
      statisticsApi.trend()
    ])
    if (mainRes?.data) {
      stats.value = { ...stats.value, ...mainRes.data }
    }
    if (trendRes?.data) {
      trendData.value = { ...trendData.value, ...trendRes.data }
    }
  } catch (e) {
    message.error('加载统计数据失败')
  } finally {
    statsLoading.value = false
  }
}

async function loadFeaturedSpecimens() {
  specimensLoading.value = true
  try {
    const res = await specimensApi.list({ is_featured: true, page_size: 8 })
    if (res?.data?.list) {
      featuredSpecimens.value = res.data.items
    } else if (res?.data) {
      featuredSpecimens.value = Array.isArray(res.data) ? res.data : []
    }
  } catch (e) {
    message.error('加载精选标本失败')
  } finally {
    specimensLoading.value = false
  }
}

async function loadLatestNotes() {
  notesLoading.value = true
  try {
    const res = await notesApi.list({ page: 1, page_size: 5, order_by: 'created_at', order: 'desc' })
    if (res?.data?.list) {
      latestNotes.value = res.data.items
    } else if (res?.data) {
      latestNotes.value = Array.isArray(res.data) ? res.data.slice(0, 5) : []
    }
  } catch (e) {
    message.error('加载最新笔记失败')
  } finally {
    notesLoading.value = false
  }
}

onMounted(() => {
  loadStats()
  loadFeaturedSpecimens()
  loadLatestNotes()
})
</script>

<template>
  <div class="dashboard-wrapper">
    <div class="section-header">
      <div>
        <h2 class="page-title">
          <n-icon size="26" color="#D4A5A5"><Sparkles /></n-icon>
          数据概览
        </h2>
        <p class="page-subtitle">记录每一片花瓣的故事，见证时光与美的沉淀</p>
      </div>
      <div class="header-decor">
        <span class="flower-icon flower-1">🌸</span>
        <span class="flower-icon flower-2">🌿</span>
        <span class="flower-icon flower-3">✨</span>
      </div>
    </div>

    <div class="stats-section">
      <n-grid :cols="6" responsive="screen" :x-gap="18" :y-gap="18">
        <n-grid-item v-for="card in statCards" :key="card.key" span="6 m:3 l:2">
          <div class="stat-card" :style="{ background: card.gradient }">
            <div class="stat-card-bg">
              <span class="bg-flower bg-flower-1">❀</span>
              <span class="bg-flower bg-flower-2">✿</span>
              <span class="bg-flower bg-flower-3">❁</span>
            </div>
            <div class="stat-card-inner">
              <div class="stat-icon-wrap" :style="{ background: `linear-gradient(135deg, ${card.accent}33, ${card.accent}22)` }">
                <n-icon :component="card.icon" :size="22" :color="card.accent" />
              </div>
              <div class="stat-info">
                <div class="stat-title">{{ card.title }}</div>
                <div class="stat-value" :style="{ color: card.accent }">
                  <span class="stat-num">{{ stats[card.key] || 0 }}</span>
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
            <v-chart :option="materialPieOption" style="height: 340px;" autoresize />
          </n-card>
        </n-grid-item>
        <n-grid-item span="2 m:2 l:1">
          <n-card class="chart-card" size="large" :bordered="false">
            <v-chart :option="specimenPieOption" style="height: 340px;" autoresize />
          </n-card>
        </n-grid-item>
        <n-grid-item span="2 m:2 l:1">
          <n-card class="chart-card" size="large" :bordered="false">
            <v-chart :option="monthlyBarOption" style="height: 340px;" autoresize />
          </n-card>
        </n-grid-item>
        <n-grid-item span="2 m:2 l:1">
          <n-card class="chart-card" size="large" :bordered="false">
            <v-chart :option="methodDonutOption" style="height: 340px;" autoresize />
          </n-card>
        </n-grid-item>
      </n-grid>
    </div>

    <div class="content-section">
      <n-grid :cols="3" responsive="screen" :x-gap="18" :y-gap="18">
        <n-grid-item span="3 m:3 l:2">
          <n-card class="section-card" size="large" :bordered="false">
            <template #header>
              <div class="card-header">
                <div class="card-title-wrap">
                  <span class="title-bar"></span>
                  <span class="card-title">
                    <n-icon size="18" color="#C08990"><FlowerOutline /></n-icon>
                    精选标本
                  </span>
                </div>
                <n-tag round size="small" style="background: rgba(212,165,165,0.15); color: #C08990; border: none;">
                  {{ featuredSpecimens.length }} 件
                </n-tag>
              </div>
            </template>

            <div v-if="specimensLoading" class="empty-state">
              <div class="loading-spinner"></div>
              <span>加载中...</span>
            </div>
            <div v-else-if="featuredSpecimens.length === 0" class="empty-state">
              <span class="empty-icon">🌸</span>
              <span>暂无精选标本</span>
            </div>
            <n-grid v-else :cols="4" responsive="screen" :x-gap="14" :y-gap="14">
              <n-grid-item v-for="item in featuredSpecimens" :key="item.id" span="4 s:2 m:2 l:4 xl:2">
                <div class="specimen-card">
                  <div class="specimen-image-wrap">
                    <img
                      v-if="item.image_url"
                      :src="item.image_url"
                      :alt="item.name"
                      class="specimen-image"
                    />
                    <div v-else class="specimen-image-placeholder">
                      <n-icon :component="FlowerOutline" size="36" color="#D4B8B0" />
                    </div>
                    <div class="specimen-badge">精选</div>
                  </div>
                  <div class="specimen-info">
                    <div class="specimen-name">
                      <n-ellipsis :line-clamp="1">{{ item.name }}</n-ellipsis>
                    </div>
                    <div class="specimen-meta">
                      <n-tag
                        v-if="item.category"
                        round
                        size="tiny"
                        style="background: rgba(168,195,160,0.18); color: #8BA888; border: none;"
                      >
                        {{ item.category }}
                      </n-tag>
                    </div>
                    <div class="specimen-stats">
                      <span class="stat-item">
                        <n-icon size="14" color="#E88A9A"><Heart /></n-icon>
                        <span>{{ item.like_count ?? item.likes ?? 0 }}</span>
                      </span>
                      <span class="stat-item">
                        <n-icon size="14" color="#8BA8C3"><Eye /></n-icon>
                        <span>{{ item.view_count ?? item.views ?? 0 }}</span>
                      </span>
                    </div>
                  </div>
                </div>
              </n-grid-item>
            </n-grid>
          </n-card>
        </n-grid-item>

        <n-grid-item span="3 m:3 l:1">
          <n-card class="section-card" size="large" :bordered="false">
            <template #header>
              <div class="card-header">
                <div class="card-title-wrap">
                  <span class="title-bar"></span>
                  <span class="card-title">
                    <n-icon size="18" color="#F5C86B"><Book /></n-icon>
                    最新笔记
                  </span>
                </div>
                <n-tag round size="small" style="background: rgba(245,200,107,0.2); color: #C49B3A; border: none;">
                  {{ latestNotes.length }} 篇
                </n-tag>
              </div>
            </template>

            <div v-if="notesLoading" class="empty-state">
              <div class="loading-spinner"></div>
              <span>加载中...</span>
            </div>
            <div v-else-if="latestNotes.length === 0" class="empty-state">
              <span class="empty-icon">📝</span>
              <span>暂无笔记</span>
            </div>
            <n-list v-else size="large" style="padding: 0;">
              <n-list-item
                v-for="(note, index) in latestNotes"
                :key="note.id"
                class="note-item"
                :style="{ animationDelay: `${index * 60}ms` }"
              >
                <div class="note-content">
                  <div class="note-header">
                    <div class="note-index" :class="'note-index-' + (index + 1)">{{ index + 1 }}</div>
                    <div class="note-title">
                      <n-ellipsis :line-clamp="1">{{ note.title }}</n-ellipsis>
                    </div>
                  </div>
                  <div class="note-tags">
                    <n-tag
                      v-if="note.category"
                      round
                      size="tiny"
                      style="background: rgba(212,165,165,0.15); color: #C08990; border: none;"
                    >
                      {{ note.category }}
                    </n-tag>
                    <n-tag
                      v-if="note.difficulty"
                      round
                      size="tiny"
                      :style="{ background: getDifficultyColor(note.difficulty).bg, color: getDifficultyColor(note.difficulty).text, border: 'none' }"
                    >
                      {{ note.difficulty }}
                    </n-tag>
                    <span v-if="note.created_at" class="note-date">
                      <n-icon size="12" color="#B8A8A6"><Calendar /></n-icon>
                      {{ note.created_at.slice(0, 10) }}
                    </span>
                  </div>
                </div>
              </n-list-item>
            </n-list>
          </n-card>
        </n-grid-item>
      </n-grid>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.dashboard-wrapper {
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
  width: 100px;
  height: 60px;
}

.flower-icon {
  position: absolute;
  font-size: 28px;
  opacity: 0.6;
  animation: float 4s ease-in-out infinite;

  &.flower-1 {
    top: 0;
    right: 60px;
    animation-delay: 0s;
  }

  &.flower-2 {
    top: 20px;
    right: 20px;
    animation-delay: 0.8s;
    font-size: 22px;
  }

  &.flower-3 {
    top: 5px;
    right: 0;
    animation-delay: 1.6s;
    font-size: 18px;
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

  &.bg-flower-3 {
    top: 50%;
    right: 30%;
    font-size: 36px;
    transform: translateY(-50%) rotate(45deg);
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
  font-size: 30px;
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

.content-section {
  margin-bottom: 20px;
}

.section-card {
  background: #FFFDF6;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(212, 165, 165, 0.1);
  border: 1px solid rgba(240, 230, 222, 0.8) !important;
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

.card-header {
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
  padding: 50px 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  color: #B8A8A6;
  font-size: 13px;
}

.empty-icon {
  font-size: 42px;
  opacity: 0.5;
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

.specimen-card {
  background: linear-gradient(135deg, rgba(255, 253, 246, 1), rgba(250, 246, 238, 0.9));
  border-radius: 14px;
  border: 1px solid rgba(240, 230, 222, 0.9);
  overflow: hidden;
  transition: all 0.3s ease;
  cursor: pointer;

  &:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 28px rgba(212, 165, 165, 0.2);
    border-color: rgba(212, 165, 165, 0.3);
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
  transition: transform 0.4s ease;
}

.specimen-card:hover .specimen-image {
  transform: scale(1.06);
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

.specimen-badge {
  position: absolute;
  top: 10px;
  left: 10px;
  padding: 4px 10px;
  background: linear-gradient(135deg, rgba(212, 165, 165, 0.95), rgba(192, 137, 144, 0.95));
  color: #FFFDF6;
  font-size: 11px;
  font-weight: 600;
  border-radius: 8px;
  backdrop-filter: blur(4px);
  box-shadow: 0 2px 8px rgba(212, 165, 165, 0.3);
}

.specimen-info {
  padding: 14px;
}

.specimen-name {
  font-size: 14px;
  font-weight: 600;
  color: #5C4A4A;
  margin-bottom: 8px;
  line-height: 1.4;
}

.specimen-meta {
  margin-bottom: 10px;
}

.specimen-stats {
  display: flex;
  gap: 14px;
  padding-top: 10px;
  border-top: 1px dashed rgba(240, 230, 222, 0.9);
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  color: #8B7D7B;
  font-weight: 500;
}

.note-item {
  padding: 14px 0 !important;
  border-bottom: 1px dashed rgba(240, 230, 222, 0.8);
  animation: fadeSlideIn 0.5s ease both;

  &:last-child {
    border-bottom: none;
    padding-bottom: 0;
  }

  &:first-child {
    padding-top: 0;
  }
}

@keyframes fadeSlideIn {
  from {
    opacity: 0;
    transform: translateX(-10px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.note-content {
  width: 100%;
}

.note-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.note-index {
  width: 22px;
  height: 22px;
  border-radius: 7px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 700;
  flex-shrink: 0;
  color: #FFFDF6;

  &.note-index-1 {
    background: linear-gradient(135deg, #E88A9A, #D4A5A5);
  }
  &.note-index-2 {
    background: linear-gradient(135deg, #F5C86B, #E8B460);
  }
  &.note-index-3 {
    background: linear-gradient(135deg, #A8C3A0, #8BA888);
  }
  &.note-index-4 {
    background: linear-gradient(135deg, #B8C8D4, #8BA8C3);
  }
  &.note-index-5 {
    background: linear-gradient(135deg, #D4A06B, #C49050);
  }
}

.note-title {
  flex: 1;
  font-size: 14px;
  font-weight: 600;
  color: #5C4A4A;
  line-height: 1.4;
  min-width: 0;
}

.note-tags {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  margin-left: 32px;
}

.note-date {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: #B8A8A6;
}
</style>
