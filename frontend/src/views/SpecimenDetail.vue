<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NCard, NButton, NSpace, NIcon, useMessage, NSkeleton, NTag, NGrid, NGridItem } from 'naive-ui'
import { ArrowBack, FlowerOutline, Sparkles, Heart, Eye } from '@vicons/ionicons5'
import { specimensApi } from '@/api'

const route = useRoute()
const router = useRouter()
const message = useMessage()

const loading = ref(false)
const data = ref(null)

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

async function loadDetail() {
  loading.value = true
  try {
    const id = route.params.id
    const res = await specimensApi.get(id)
    if (res?.data) {
      data.value = res.data
    }
  } catch (e) {
    message.error('加载标本详情失败')
  } finally {
    loading.value = false
  }
}

function goBack() {
  router.push('/specimens')
}

onMounted(() => {
  loadDetail()
})
</script>

<template>
  <div class="detail-wrapper">
    <div class="nav-back">
      <n-button quaternary @click="goBack">
        <template #icon><n-icon :component="ArrowBack" /></template>
        返回标本列表
      </n-button>
    </div>

    <n-skeleton v-if="loading" text :repeat="6" style="max-width: 900px; margin: 0 auto;" />

    <n-card v-else-if="data" class="detail-card" size="large" :bordered="false">
      <div class="detail-hero">
        <div v-if="data.image_url" class="detail-hero-image">
          <img :src="data.image_url" :alt="data.name" />
        </div>
        <div v-else class="detail-hero-placeholder">
          <n-icon :component="FlowerOutline" size="72" color="#D4B8B0" />
        </div>
      </div>

      <div class="detail-body" style="padding: 0 8px;">
        <h1 class="detail-name">{{ data.name }}</h1>

        <div class="detail-tags-row" style="margin: 14px 0 22px;">
          <n-tag
            v-if="data.category"
            round
            size="small"
            :style="{ background: getCategoryColor(data.category).bg, color: getCategoryColor(data.category).text, border: 'none' }"
          >
            {{ data.category }}
          </n-tag>
          <n-tag
            v-if="data.status"
            round
            size="small"
            :style="{ background: getStatusColor(data.status).bg, color: getStatusColor(data.status).text, border: 'none' }"
          >
            {{ data.status }}
          </n-tag>
          <span v-if="data.display_code" class="detail-code">#{{ data.display_code }}</span>
          <n-tag
            v-if="data.is_featured"
            round
            size="small"
            style="background: linear-gradient(135deg, rgba(212,165,165,0.9), rgba(192,137,144,0.9)); color: #FFFDF6; border: none;"
          >
            <template #icon><n-icon size="12"><Sparkles /></n-icon></template>
            精选
          </n-tag>
        </div>

        <div class="detail-stats" style="margin-bottom: 24px;">
          <span class="stat-item">
            <n-icon size="18" color="#E88A9A"><Heart /></n-icon>
            <span>{{ data.like_count ?? 0 }} 点赞</span>
          </span>
          <span class="stat-item">
            <n-icon size="18" color="#8BA8C3"><Eye /></n-icon>
            <span>{{ data.view_count ?? 0 }} 浏览</span>
          </span>
        </div>

        <n-grid :cols="2" :x-gap="20" :y-gap="16" style="margin-bottom: 24px;">
          <n-grid-item span="2 s:2 m:1" class="info-item">
            <span class="info-label">装裱风格</span>
            <span class="info-value">{{ data.frame_style || '-' }}</span>
          </n-grid-item>
          <n-grid-item span="2 s:2 m:1" class="info-item">
            <span class="info-label">装裱尺寸</span>
            <span class="info-value">{{ data.frame_size || '-' }}</span>
          </n-grid-item>
          <n-grid-item span="2 s:2 m:1" class="info-item">
            <span class="info-label">存放位置</span>
            <span class="info-value">{{ data.location || '-' }}</span>
          </n-grid-item>
          <n-grid-item span="2 s:2 m:1" class="info-item">
            <span class="info-label">制作日期</span>
            <span class="info-value">{{ data.production_date || '-' }}</span>
          </n-grid-item>
          <n-grid-item span="2 s:2 m:1" class="info-item">
            <span class="info-label">保存期限</span>
            <span class="info-value">{{ data.shelf_life_months ? data.shelf_life_months + ' 个月' : '-' }}</span>
          </n-grid-item>
          <n-grid-item span="2 s:2 m:1" class="info-item">
            <span class="info-label">保存方式</span>
            <span class="info-value">{{ data.preservation_method || '-' }}</span>
          </n-grid-item>
        </n-grid>

        <div v-if="data.tags?.length" class="detail-section" style="margin-bottom: 24px;">
          <div class="section-label">标签</div>
          <div style="display: flex; gap: 8px; flex-wrap: wrap;">
            <n-tag
              v-for="tag in data.tags"
              :key="tag"
              round
              size="small"
              style="background: rgba(245,230,163,0.22); color: #C49B3A; border: none;"
            >
              #{{ tag }}
            </n-tag>
          </div>
        </div>

        <div v-if="data.description" class="detail-section" style="margin-bottom: 24px;">
          <div class="section-label">作品描述</div>
          <p class="detail-desc-text">{{ data.description }}</p>
        </div>

        <div v-if="data.gallery_images?.length" class="detail-section">
          <div class="section-label">作品图集</div>
          <div class="gallery-grid">
            <div v-for="(url, i) in data.gallery_images" :key="i" class="gallery-item">
              <img :src="url" />
            </div>
          </div>
        </div>
      </div>
    </n-card>
  </div>
</template>

<style lang="scss" scoped>
.detail-wrapper {
  padding-bottom: 40px;
}

.nav-back {
  margin-bottom: 18px;
}

.detail-card {
  background: linear-gradient(180deg, #FFFDF6 0%, #FAF6EE 100%);
  border-radius: 18px;
  box-shadow: 0 4px 24px rgba(212, 165, 165, 0.12);
  border: 1px solid rgba(240, 230, 222, 0.8) !important;
  max-width: 900px;
  margin: 0 auto;
  overflow: hidden;
}

.detail-hero {
  margin: -24px -24px 24px;
}

.detail-hero-image {
  width: 100%;
  max-height: 380px;
  background: linear-gradient(135deg, #FAF6EE, #F5EEE8);

  img {
    width: 100%;
    height: 100%;
    max-height: 380px;
    object-fit: cover;
    display: block;
  }
}

.detail-hero-placeholder {
  width: 100%;
  height: 280px;
  background: linear-gradient(135deg, #FAF6EE, #F5EEE8);
  display: flex;
  align-items: center;
  justify-content: center;
}

.detail-name {
  font-size: 26px;
  font-weight: 700;
  color: #5C4A4A;
  margin: 0;
  letter-spacing: 0.5px;
}

.detail-tags-row {
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
  padding: 4px 12px;
  border-radius: 6px;
}

.detail-stats {
  display: flex;
  gap: 28px;
  padding: 16px 0;
  border-top: 1px solid rgba(240, 230, 222, 0.7);
  border-bottom: 1px solid rgba(240, 230, 222, 0.7);
}

.stat-item {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #8B7D7B;
  font-weight: 500;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 14px 16px;
  background: rgba(250, 246, 238, 0.6);
  border-radius: 12px;
  border: 1px solid rgba(240, 230, 222, 0.7);
}

.info-label {
  font-size: 12px;
  color: #B8A8A6;
}

.info-value {
  font-size: 15px;
  color: #5C4A4A;
  font-weight: 500;
}

.detail-section {
  .section-label {
    font-size: 13px;
    font-weight: 600;
    color: #8B7D7B;
    margin-bottom: 10px;
    letter-spacing: 0.5px;
  }
}

.detail-desc-text {
  margin: 0;
  color: #5C4A4A;
  line-height: 1.85;
  font-size: 14px;
  white-space: pre-wrap;
  padding: 16px;
  background: rgba(250, 246, 238, 0.55);
  border-radius: 12px;
  border: 1px dashed rgba(240, 230, 222, 0.9);
}

.gallery-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 12px;
}

.gallery-item {
  width: 100%;
  aspect-ratio: 1;
  border-radius: 12px;
  overflow: hidden;
  border: 2px solid rgba(240, 230, 222, 0.9);
  background: linear-gradient(135deg, #FAF6EE, #F5EEE8);

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
}
</style>
