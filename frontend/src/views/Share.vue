<script setup>
import { ref, onMounted, computed, h, reactive } from 'vue'
import {
  NCard, NGrid, NGridItem, NTag, NIcon, NSpace, NButton,
  NInput, NSelect, NSwitch, NModal, NForm, NFormItem,
  NImage, NEllipsis, NDynamicTags, NCarousel, NAvatar,
  NDivider, useMessage, useDialog, NEmpty, NPagination, NSkeleton,
  NScrollbar, NTooltip
} from 'naive-ui'
import {
  ShareSocial, Add, Search, Heart, Eye,
  CreateOutline, Sparkles, Repeat, BookmarkOutline,
  CheckmarkCircleOutline, Calendar, People, Time,
  Flame, Ribbon, Star, Flower
} from '@vicons/ionicons5'
import { shareApi, specimensApi } from '@/api'

const message = useMessage()
const dialog = useDialog()

const loading = ref(false)
const hotLoading = ref(false)
const list = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(9)
const hotList = ref([])

const keyword = ref('')
const filterTags = ref([])
const sortBy = ref('latest')

const showDetailModal = ref(false)
const showCreateModal = ref(false)
const detailData = ref(null)
const createFormRef = ref(null)

const unsharedSpecimenOptions = ref([])

const createForm = reactive({
  specimen_id: null,
  title: '',
  content: '',
  author: '花艺爱好者',
  tags: [],
  is_published: true
})

const createRules = {
  title: { required: true, message: '请输入标题', trigger: 'blur' },
  content: { required: true, message: '请输入内容', trigger: 'blur' }
}

const sortOptions = [
  { label: '最新发布', value: 'latest' },
  { label: '最受欢迎', value: 'hot' }
]

async function loadHotList() {
  hotLoading.value = true
  try {
    const res = await shareApi.list({
      order_by: 'like_count',
      order: 'desc',
      page_size: 5
    })
    if (res?.data?.items) {
      hotList.value = res.data.items
    } else if (res?.data) {
      hotList.value = Array.isArray(res.data) ? res.data.slice(0, 5) : []
    }
  } catch (e) {
    message.error('加载热榜失败')
  } finally {
    hotLoading.value = false
  }
}

async function loadUnsharedSpecimens() {
  try {
    const res = await specimensApi.list({ page_size: 100, is_shared: false })
    const items = res?.data?.items || res?.data || []
    unsharedSpecimenOptions.value = items.map(s => ({
      label: s.name || '未命名',
      value: s.id,
      image: s.image_url || ''
    }))
  } catch (e) {}
}

async function loadList() {
  loading.value = true
  try {
    const params = {
      page: page.value,
      page_size: pageSize.value
    }
    if (keyword.value) params.keyword = keyword.value
    if (filterTags.value.length > 0) params.tags = filterTags.value.join(',')
    if (sortBy.value === 'hot') {
      params.order_by = 'like_count'
      params.order = 'desc'
    } else {
      params.order_by = 'created_at'
      params.order = 'desc'
    }
    const res = await shareApi.list(params)
    if (res?.data?.items) {
      list.value = res.data.items
      total.value = res.data.total || 0
    } else if (res?.data) {
      list.value = Array.isArray(res.data) ? res.data : []
      total.value = list.value.length
    }
  } catch (e) {
    message.error('加载分享列表失败')
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  page.value = 1
  loadList()
}

function handleSortChange() {
  page.value = 1
  loadList()
}

function handlePageChange(p) {
  page.value = p
  loadList()
}

function openCreate() {
  Object.assign(createForm, {
    specimen_id: null,
    title: '',
    content: '',
    author: '花艺爱好者',
    tags: [],
    is_published: true
  })
  loadUnsharedSpecimens()
  showCreateModal.value = true
}

function handleCreateSubmit() {
  createFormRef.value?.validate(async (errors) => {
    if (errors) return
    try {
      const payload = { ...createForm }
      await shareApi.create(payload)
      message.success('分享发布成功')
      showCreateModal.value = false
      loadList()
      loadHotList()
    } catch (e) {
      message.error('发布失败')
    }
  })
}

async function openDetail(item) {
  try {
    const res = await shareApi.get(item.id)
    if (res?.data) {
      detailData.value = res.data
      showDetailModal.value = true
    }
  } catch (e) {
    message.error('加载详情失败')
  }
}

async function handleLike(item) {
  try {
    const res = await shareApi.like(item.id, { like: !item.is_liked })
    if (res?.data?.like_count !== undefined) {
      item.like_count = res.data.like_count
      item.is_liked = !item.is_liked
    }
    if (!item.is_liked) {
      message.success('已取消点赞')
    } else {
      message.success('点赞成功')
    }
  } catch (e) {
    message.error('操作失败')
  }
}

async function handleShare(item) {
  try {
    const res = await shareApi.share(item.id)
    if (res?.data?.share_count !== undefined) {
      item.share_count = res.data.share_count
    }
    const shareUrl = window.location.href + '/share/' + item.id
    try {
      await navigator.clipboard.writeText(shareUrl)
      message.success('链接已复制到剪贴板')
    } catch (e) {
      message.success('分享成功')
    }
  } catch (e) {
    message.error('分享失败')
  }
}

function handleFavorite(item) {
  if (item.is_favorited) {
    message.info('已收藏')
  } else {
    item.is_favorited = true
    message.success('已加入收藏')
  }
}

function getTagColor() {
  const colors = [
    { bg: 'rgba(212, 165, 165, 0.2)', text: '#C08990' },
    { bg: 'rgba(245, 230, 163, 0.25)', text: '#C49B3A' },
    { bg: 'rgba(168, 195, 160, 0.2)', text: '#8BA888' },
    { bg: 'rgba(184, 200, 212, 0.22)', text: '#8BA8C3' },
    { bg: 'rgba(212, 160, 107, 0.2)', text: '#C49050' }
  ]
  return colors[Math.floor(Math.random() * colors.length)]
}

const detailImages = computed(() => {
  if (!detailData.value) return []
  const images = []
  if (detailData.value.specimen?.image_url) {
    images.push(detailData.value.specimen.image_url)
  }
  if (detailData.value.specimen?.gallery_images?.length) {
    images.push(...detailData.value.specimen.gallery_images)
  }
  if (detailData.value.images?.length) {
    images.push(...detailData.value.images)
  }
  return images.filter(Boolean)
})

onMounted(() => {
  loadHotList()
  loadList()
})
</script>

<template>
  <div class="share-wrapper">
    <div class="section-header">
      <div>
        <h2 class="page-title">
          <n-icon size="26" color="#D4A5A5"><ShareSocial /></n-icon>
          作品分享广场
        </h2>
        <p class="page-subtitle">与同好共赏花艺之美，分享每一份创作的喜悦</p>
      </div>
      <n-button type="primary" size="large" @click="openCreate">
        <template #icon><n-icon :component="Add" /></template>
        发布分享
      </n-button>
    </div>

    <n-card v-if="hotList.length > 0" class="hot-card" size="large" :bordered="false">
      <template #header>
        <div class="hot-header">
          <div class="card-title-wrap">
            <span class="title-bar"></span>
            <span class="card-title">
              <n-icon size="18" color="#E88A9A"><Flame /></n-icon>
              点赞热榜 TOP5
            </span>
          </div>
          <n-tag round size="small" class="hot-badge">
            <template #icon><n-icon size="12"><Sparkles /></n-icon></template>
            实时热度
          </n-tag>
        </div>
      </template>

      <n-scrollbar x-scrollable>
        <div class="hot-scroll-wrap">
          <div
            v-for="(item, index) in hotList"
            :key="'hot-' + item.id"
            class="hot-item"
            @click="openDetail(item)"
          >
            <div class="hot-rank" :class="'hot-rank-' + (index + 1)">
              {{ index + 1 }}
            </div>
            <div class="hot-image">
              <img
                :src="item.specimen?.image_url || item.image_url || ''"
                :alt="item.title"
              />
            </div>
            <div class="hot-info">
              <n-ellipsis :line-clamp="1" class="hot-title">{{ item.title }}</n-ellipsis>
              <div class="hot-stats">
                <span class="hot-stat">
                  <n-icon size="12" color="#E88A9A"><Heart /></n-icon>
                  {{ item.like_count ?? 0 }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </n-scrollbar>
    </n-card>

    <n-card class="filter-card" size="large" :bordered="false">
      <n-space vertical :size="16" style="width: 100%;">
        <div class="filter-row">
          <div class="filter-search-wrap">
            <n-input
              v-model:value="keyword"
              placeholder="搜索标题、内容、作者..."
              clearable
              size="large"
              style="width: 280px;"
              @keyup.enter="handleSearch"
            >
              <template #prefix><n-icon :component="Search" /></template>
            </n-input>
          </div>
          <n-space :size="12" wrap>
            <div class="filter-tags-wrap">
              <span class="filter-tags-label">标签：</span>
              <n-dynamic-tags
                v-model:value="filterTags"
                closable
                round
                placeholder="添加标签筛选"
                input-style="width: 140px;"
                @change="handleSearch"
              />
            </div>
            <n-select
              v-model:value="sortBy"
              :options="sortOptions"
              size="medium"
              style="width: 140px;"
              @update:value="handleSortChange"
            />
          </n-space>
        </div>
      </n-space>
    </n-card>

    <div v-if="loading" class="list-loading">
      <n-skeleton :repeat="3" text :row="3" style="max-width: 900px; margin: 0 auto;" />
    </div>

    <div v-else-if="list.length === 0" class="empty-state">
      <n-empty description="暂无分享，快来发布第一篇吧" :show-icon="false">
        <template #image>
          <div class="empty-icon-wrap">
            <span class="empty-emoji">💐</span>
            <span class="empty-emoji empty-emoji-2">🌸</span>
          </div>
        </template>
        <n-button type="primary" @click="openCreate">
          <template #icon><n-icon :component="Add" /></template>
          发布分享
        </n-button>
      </n-empty>
    </div>

    <template v-else>
      <div class="posts-section">
        <n-grid :cols="3" responsive="screen" :x-gap="16" :y-gap="16">
          <n-grid-item v-for="item in list" :key="item.id" span="3 m:3 l:3 xl:1">
            <div class="post-card" @click="openDetail(item)">
              <div class="post-image-wrap">
                <n-image
                  v-if="item.specimen?.image_url || item.image_url"
                  :src="item.specimen?.image_url || item.image_url"
                  :alt="item.title"
                  object-fit="cover"
                  class="post-image"
                />
                <div v-else class="post-image-placeholder">
                  <n-icon :component="Flower" size="44" color="#D4B8B0" />
                </div>
                <div class="post-overlay-stats">
                  <span class="overlay-stat">
                    <n-icon size="14" color="#FFFDF6"><Heart /></n-icon>
                    <span>{{ item.like_count ?? 0 }}</span>
                  </span>
                  <span class="overlay-stat">
                    <n-icon size="14" color="#FFFDF6"><Eye /></n-icon>
                    <span>{{ item.view_count ?? 0 }}</span>
                  </span>
                </div>
              </div>

              <div class="post-body">
                <div class="post-author-row">
                  <n-avatar round size="32" class="author-avatar">
                    <template #default>
                      <n-icon :component="People" :size="18" />
                    </template>
                  </n-avatar>
                  <div class="author-info">
                    <span class="author-name">{{ item.author || '匿名' }}</span>
                    <span class="post-time">
                      <n-icon size="11" color="#B8A8A6"><Time /></n-icon>
                      {{ item.created_at?.slice(0, 10) || '刚刚' }}
                    </span>
                  </div>
                </div>

                <div class="post-title">
                  <n-ellipsis :line-clamp="1">{{ item.title }}</n-ellipsis>
                </div>

                <div class="post-summary">
                  <n-ellipsis :line-clamp="2">{{ item.content }}</n-ellipsis>
                </div>

                <div class="post-tags" v-if="item.tags?.length">
                  <n-tag
                    v-for="tag in item.tags.slice(0, 4)"
                    :key="tag"
                    round
                    size="tiny"
                    class="post-tag"
                  >
                    #{{ tag }}
                  </n-tag>
                </div>

                <n-divider class="post-divider" />

                <div class="post-footer">
                  <div class="footer-stats">
                    <span
                      class="footer-action"
                      :class="{ 'action-liked': item.is_liked }"
                      @click.stop="handleLike(item)"
                    >
                      <n-icon :component="Heart" />
                      <span>{{ item.like_count ?? 0 }}</span>
                    </span>
                    <span class="footer-stat">
                      <n-icon :component="Eye" />
                      <span>{{ item.view_count ?? 0 }}</span>
                    </span>
                    <span
                      class="footer-action"
                      @click.stop="handleShare(item)"
                    >
                      <n-icon :component="Repeat" />
                      <span>{{ item.share_count ?? 0 }}</span>
                    </span>
                  </div>
                  <n-button
                    quaternary
                    size="tiny"
                    :class="{ 'action-favorited': item.is_favorited }"
                    @click.stop="handleFavorite(item)"
                  >
                    <template #icon><n-icon :component="BookmarkOutline" /></template>
                  </n-button>
                </div>
              </div>
            </div>
          </n-grid-item>
        </n-grid>
      </div>

      <div class="pagination-wrap">
        <n-pagination
          v-model:page="page"
          v-model:page-size="pageSize"
          :item-count="total"
          :page-sizes="[9, 18, 27, 45]"
          show-size-picker
          show-quick-jumper
          @update:page="handlePageChange"
        />
      </div>
    </template>

    <n-modal
      v-model:show="showDetailModal"
      preset="card"
      :title="detailData?.title || '分享详情'"
      style="width: 900px; max-width: 92vw;"
      :mask-closable="true"
      class="detail-modal"
    >
      <div v-if="detailData" class="detail-content">
        <div v-if="detailImages.length > 0" class="detail-carousel-wrap">
          <n-carousel :show-dots="detailImages.length > 1" dot-type="line" effect="fade">
            <div v-for="(img, idx) in detailImages" :key="idx">
              <img :src="img" class="detail-carousel-img" />
            </div>
          </n-carousel>
        </div>

        <div class="detail-meta-row">
          <div class="detail-author-info">
            <n-avatar round size="44" class="detail-avatar">
              <template #default>
                <n-icon :component="People" :size="24" />
              </template>
            </n-avatar>
            <div>
              <div class="detail-author">{{ detailData.author || '匿名作者' }}</div>
              <div class="detail-date">
                <n-icon size="12" color="#B8A8A6"><Calendar /></n-icon>
                {{ detailData.created_at?.slice(0, 16)?.replace('T', ' ') || '刚刚发布' }}
              </div>
            </div>
          </div>
          <div class="detail-main-stats">
            <span class="main-stat">
              <n-icon size="16" color="#E88A9A"><Heart /></n-icon>
              <span>{{ detailData.like_count ?? 0 }}</span>
            </span>
            <span class="main-stat">
              <n-icon size="16" color="#8BA8C3"><Eye /></n-icon>
              <span>{{ detailData.view_count ?? 0 }}</span>
            </span>
            <span class="main-stat">
              <n-icon size="16" color="#A8C3A0"><Repeat /></n-icon>
              <span>{{ detailData.share_count ?? 0 }}</span>
            </span>
            <span class="main-stat">
              <n-icon size="16" color="#F5C86B"><CreateOutline /></n-icon>
              <span>{{ detailData.comment_count ?? 0 }}</span>
            </span>
          </div>
        </div>

        <n-divider style="margin: 18px 0;" />

        <div class="detail-title">{{ detailData.title }}</div>

        <div v-if="detailData.tags?.length" class="detail-tags">
          <n-tag
            v-for="tag in detailData.tags"
            :key="tag"
            round
            size="small"
            class="detail-tag"
          >
            #{{ tag }}
          </n-tag>
        </div>

        <div class="detail-body-text">
          <p>{{ detailData.content }}</p>
        </div>

        <div v-if="detailData.specimen" class="detail-specimen-link">
          <n-tag round size="small" class="specimen-link-tag">
            <template #icon><n-icon size="12"><Ribbon /></n-icon></template>
            关联标本：{{ detailData.specimen.name || '未命名' }}
          </n-tag>
        </div>
      </div>
      <template #footer>
        <NSpace justify="end">
          <n-button @click="showDetailModal = false">关闭</n-button>
          <n-button @click="handleLike(detailData)">
            <template #icon><n-icon :component="Heart" /></template>
            点赞
          </n-button>
          <n-button type="primary" @click="handleShare(detailData)">
            <template #icon><n-icon :component="ShareSocial" /></template>
            转发
          </n-button>
        </NSpace>
      </template>
    </n-modal>

    <n-modal
      v-model:show="showCreateModal"
      preset="card"
      title="发布新分享"
      style="width: 640px; max-width: 92vw;"
      :mask-closable="false"
      class="create-modal"
    >
      <n-form ref="createFormRef" :model="createForm" :rules="createRules" label-placement="top">
        <n-form-item label="关联标本" path="specimen_id">
          <n-select
            v-model:value="createForm.specimen_id"
            :options="unsharedSpecimenOptions"
            placeholder="选择未分享的标本（可选）"
            clearable
            filterable
            :render-label="(option) => h('div', { style: 'display:flex;align-items:center;gap:8px;' }, [
              option.image ? h('img', { src: option.image, style: 'width:24px;height:24px;border-radius:6px;object-fit:cover;' }) : null,
              option.label
            ])"
          />
        </n-form-item>
        <n-form-item label="标题" path="title">
          <n-input v-model:value="createForm.title" placeholder="给分享起一个吸引人的标题" maxlength="100" />
        </n-form-item>
        <n-form-item label="内容" path="content">
          <n-input
            v-model:value="createForm.content"
            type="textarea"
            :rows="6"
            placeholder="讲讲这件作品的故事、灵感、制作心得..."
            maxlength="2000"
          />
        </n-form-item>
        <n-form-item label="作者署名">
          <n-input v-model:value="createForm.author" placeholder="你的名字或昵称" maxlength="50" />
        </n-form-item>
        <n-form-item label="标签">
          <n-dynamic-tags
            v-model:value="createForm.tags"
            closable
            round
            placeholder="输入标签后回车添加，建议 2-5 个"
            input-style="width: 100%;"
          />
        </n-form-item>
        <n-form-item label="是否立即发布">
          <n-switch v-model:value="createForm.is_published" />
          <span v-if="!createForm.is_published" style="color: #B8A8A6; margin-left: 10px; font-size: 12px;">
            （暂不发布则保存为草稿）
          </span>
        </n-form-item>
      </n-form>
      <template #footer>
        <NSpace justify="end">
          <n-button @click="showCreateModal = false">取消</n-button>
          <n-button type="primary" @click="handleCreateSubmit">
            <template #icon><n-icon :component="CheckmarkCircleOutline" /></template>
            发布分享
          </n-button>
        </NSpace>
      </template>
    </n-modal>
  </div>
</template>

<style lang="scss" scoped>
.share-wrapper { background: transparent; }

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

.hot-card {
  background: #FFFDF6;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(212, 165, 165, 0.1);
  border: 1px solid rgba(240, 230, 222, 0.8) !important;
  margin-bottom: 20px;
  position: relative;

  &::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 100%;
    height: 3px;
    background: linear-gradient(90deg, #E88A9A, #F5C86B, #A8C3A0);
    border-radius: 16px 16px 0 0;
    opacity: 0.7;
  }
}

.hot-header {
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
  background: linear-gradient(180deg, #E88A9A, #F5C86B);
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

.hot-badge {
  background: linear-gradient(135deg, rgba(232, 138, 154, 0.18), rgba(245, 200, 107, 0.22));
  color: #E88A9A;
  border: none;
}

.hot-scroll-wrap {
  display: inline-flex;
  gap: 16px;
  padding: 4px 4px 8px;
  min-width: 100%;
}

.hot-item {
  flex-shrink: 0;
  width: 180px;
  background: linear-gradient(135deg, rgba(255, 253, 246, 1), rgba(250, 246, 238, 0.9));
  border-radius: 14px;
  border: 1px solid rgba(240, 230, 222, 0.9);
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;

  &:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 28px rgba(232, 138, 154, 0.2);
    border-color: rgba(232, 138, 154, 0.35);
  }
}

.hot-rank {
  position: absolute;
  top: 8px;
  left: 8px;
  width: 24px;
  height: 24px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  color: #FFFDF6;
  z-index: 2;

  &.hot-rank-1 { background: linear-gradient(135deg, #E88A9A, #D4A5A5); }
  &.hot-rank-2 { background: linear-gradient(135deg, #F5C86B, #E8B460); }
  &.hot-rank-3 { background: linear-gradient(135deg, #A8C3A0, #8BA888); }
  &.hot-rank-4, &.hot-rank-5 { background: linear-gradient(135deg, #B8C8D4, #8BA8C3); }
}

.hot-image {
  width: 100%;
  padding-top: 75%;
  position: relative;
  background: linear-gradient(135deg, #FAF6EE, #F5EEE8);
  overflow: hidden;

  img {
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 100%;
    object-fit: cover;
  }
}

.hot-info {
  padding: 10px 12px;
}

.hot-title {
  font-size: 13px;
  font-weight: 600;
  color: #5C4A4A;
  margin-bottom: 6px;
}

.hot-stats {
  display: flex;
  align-items: center;
}

.hot-stat {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  font-size: 11px;
  color: #8B7D7B;
  font-weight: 600;
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
    top: 0; left: 0;
    width: 4px; height: 100%;
    background: linear-gradient(180deg, #D4A5A5, #F5E6A3);
    border-radius: 16px 0 0 16px;
    opacity: 0.5;
  }
}

.filter-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.filter-tags-wrap {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.filter-tags-label {
  font-size: 13px;
  color: #8B7D7B;
}

.list-loading { padding: 60px 20px; }

.empty-state { padding: 60px 20px; }

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

.posts-section { margin-bottom: 16px; }

.post-card {
  background: linear-gradient(135deg, rgba(255, 253, 246, 1), rgba(250, 246, 238, 0.95));
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
  }
}

.post-image-wrap {
  position: relative;
  width: 100%;
  padding-top: 70%;
  background: linear-gradient(135deg, #FAF6EE, #F5EEE8);
  overflow: hidden;
}

.post-image {
  position: absolute;
  top: 0; left: 0;
  width: 100%; height: 100%;
}

.post-image-placeholder {
  position: absolute;
  top: 0; left: 0;
  width: 100%; height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.post-overlay-stats {
  position: absolute;
  top: 10px;
  right: 10px;
  display: flex;
  gap: 8px;
}

.overlay-stat {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  background: rgba(92, 74, 74, 0.45);
  color: #FFFDF6;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  backdrop-filter: blur(6px);
}

.post-body {
  padding: 14px 16px 12px;
}

.post-author-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}

.author-avatar {
  background: linear-gradient(135deg, #E8B4B8, #D4A5A5) !important;
  color: #FFFDF6 !important;
  --n-color: linear-gradient(135deg, #E8B4B8, #D4A5A5);
}

.author-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.author-name {
  font-size: 13px;
  font-weight: 600;
  color: #5C4A4A;
}

.post-time {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: #B8A8A6;
}

.post-title {
  font-size: 15px;
  font-weight: 700;
  color: #5C4A4A;
  margin-bottom: 8px;
  line-height: 1.4;
}

.post-summary {
  font-size: 13px;
  color: #8B7D7B;
  line-height: 1.6;
  margin-bottom: 10px;
  min-height: 40px;
}

.post-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-bottom: 4px;
}

.post-tag {
  background: rgba(245, 230, 163, 0.25);
  color: #C49B3A;
  border: none;
}

.post-divider {
  margin: 10px 0 8px !important;
  border-color: rgba(240, 230, 222, 0.7) !important;
}

.post-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.footer-stats {
  display: flex;
  gap: 16px;
}

.footer-action,
.footer-stat {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #8B7D7B;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    color: #D4A5A5;
  }

  &.action-liked {
    color: #E88A9A;
  }
}

.action-favorited {
  color: #F5C86B !important;
}

.pagination-wrap {
  display: flex;
  justify-content: center;
  padding: 8px 0 16px;
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
  max-height: 70vh;
  overflow-y: auto;
  padding-right: 4px;
}

.detail-carousel-wrap {
  border-radius: 14px;
  overflow: hidden;
  margin-bottom: 20px;
  background: #FAF6EE;
}

.detail-carousel-img {
  width: 100%;
  max-height: 400px;
  object-fit: cover;
  display: block;
}

.detail-meta-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 14px;
}

.detail-author-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.detail-avatar {
  background: linear-gradient(135deg, #E8B4B8, #D4A5A5) !important;
  color: #FFFDF6 !important;
}

.detail-author {
  font-size: 15px;
  font-weight: 600;
  color: #5C4A4A;
  margin-bottom: 2px;
}

.detail-date {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #B8A8A6;
}

.detail-main-stats {
  display: flex;
  gap: 18px;
}

.main-stat {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 13px;
  font-weight: 600;
  color: #5C4A4A;
}

.detail-title {
  font-size: 20px;
  font-weight: 700;
  color: #5C4A4A;
  line-height: 1.5;
  margin-bottom: 14px;
}

.detail-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 18px;
}

.detail-tag {
  background: rgba(245, 230, 163, 0.25);
  color: #C49B3A;
  border: none;
}

.detail-body-text {
  font-size: 14px;
  color: #5C4A4A;
  line-height: 1.85;
  margin-bottom: 18px;

  p {
    margin: 0;
    white-space: pre-wrap;
  }
}

.detail-specimen-link {
  padding: 12px 14px;
  background: rgba(168, 195, 160, 0.12);
  border-radius: 12px;
  border: 1px dashed rgba(168, 195, 160, 0.35);
}

.specimen-link-tag {
  background: rgba(168, 195, 160, 0.2);
  color: #8BA888;
  border: none;
}

.create-modal {
  :deep(.n-card) {
    border-radius: 18px !important;
    background: linear-gradient(180deg, #FFFDF6 0%, #FAF6EE 100%);
  }
  :deep(.n-card-header) {
    border-bottom: 1px solid rgba(240, 230, 222, 0.7) !important;
  }
}
</style>
