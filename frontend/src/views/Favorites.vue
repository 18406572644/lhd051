<script setup>
import { ref, onMounted, computed, h, reactive } from 'vue'
import {
  NCard, NGrid, NGridItem, NTag, NIcon, NSpace, NButton,
  NInput, NSelect, NModal, NForm, NFormItem,
  NImage, NEllipsis, NList, NListItem,
  useMessage, useDialog, NEmpty, NSkeleton,
  NDivider, NAvatar, NTooltip
} from 'naive-ui'
import {
  Bookmark, Add, Search, TrashOutline, Star,
  FlowerOutline, Book, ColorPalette, ImagesOutline,
  CheckmarkCircleOutline, Calendar, CreateOutline,
  Close, FolderOpen, Folder, Heart
} from '@vicons/ionicons5'
import { favoritesApi, specimensApi, notesApi, plansApi, imagesApi } from '@/api'

const message = useMessage()
const dialog = useDialog()

const loading = ref(false)
const foldersLoading = ref(false)
const list = ref([])
const folders = ref([])
const activeFolder = ref('all')
const filterType = ref(null)

const showFolderModal = ref(false)
const folderFormRef = ref(null)
const folderName = ref('')
const folderRules = {
  name: { required: true, message: '请输入收藏夹名称', trigger: 'blur' }
}

const typeOptions = [
  { label: '全部类型', value: null },
  { label: '标本', value: 'specimen' },
  { label: '笔记', value: 'note' },
  { label: '方案', value: 'plan' },
  { label: '图片', value: 'image' }
]

const typeIcons = {
  specimen: FlowerOutline,
  note: Book,
  plan: ColorPalette,
  image: ImagesOutline
}

const typeLabels = {
  specimen: '标本',
  note: '笔记',
  plan: '方案',
  image: '图片'
}

async function loadFolders() {
  foldersLoading.value = true
  try {
    const res = await favoritesApi.folders()
    const folderList = res?.data?.folders || res?.data || []
    folders.value = folderList.map(f => ({
      id: f.id,
      name: f.name,
      count: f.count || 0
    }))
  } catch (e) {
    folders.value = [{ id: 'default', name: '默认收藏夹', count: 0 }]
  } finally {
    foldersLoading.value = false
  }
}

async function loadList() {
  loading.value = true
  try {
    const params = {}
    if (activeFolder.value !== 'all') {
      params.folder_id = activeFolder.value
    }
    if (filterType.value) {
      params.item_type = filterType.value
    }
    const res = await favoritesApi.list(params)
    if (res?.data?.items) {
      list.value = res.data.items
    } else if (res?.data) {
      list.value = Array.isArray(res.data) ? res.data : []
    }
  } catch (e) {
    message.error('加载收藏列表失败')
  } finally {
    loading.value = false
  }
}

function allFolders() {
  return [
    { id: 'all', name: '全部收藏', count: totalCount.value },
    ...folders.value
  ]
}

const totalCount = computed(() => list.value.length)

const filteredList = computed(() => {
  if (!filterType.value) return list.value
  return list.value.filter(i => i.item_type === filterType.value)
})

const typeStats = computed(() => {
  const stats = {
    specimen: 0,
    note: 0,
    plan: 0,
    image: 0
  }
  list.value.forEach(i => {
    if (stats[i.item_type] !== undefined) {
      stats[i.item_type]++
    }
  })
  return stats
})

function openCreateFolder() {
  folderName.value = ''
  showFolderModal.value = true
}

function handleFolderSubmit() {
  folderFormRef.value?.validate(async (errors) => {
    if (errors) return
    try {
      await favoritesApi.create({ folder_name: folderName.value, action: 'create_folder' })
      message.success(`收藏夹「${folderName.value}」创建成功`)
      showFolderModal.value = false
      loadFolders()
    } catch (e) {
      message.error('创建失败')
    }
  })
}

function handleSelectFolder(folderId) {
  activeFolder.value = folderId
  loadList()
}

function handleRemoveFavorite(item) {
  dialog.warning({
    title: '取消收藏',
    content: `确定要取消收藏「${item.title || item.item_name || '该内容'}」吗？`,
    positiveText: '取消收藏',
    negativeText: '再想想',
    positiveButtonProps: { color: '#E88A9A' },
    onPositiveClick: async () => {
      try {
        await favoritesApi.delete(item.id)
        message.success('已取消收藏')
        loadList()
        loadFolders()
      } catch (e) {
        message.error('操作失败')
      }
    }
  })
}

function getTypeColor(type) {
  const colors = {
    specimen: { bg: 'rgba(212, 165, 165, 0.22)', text: '#C08990', icon: '#D4A5A5' },
    note: { bg: 'rgba(245, 230, 163, 0.28)', text: '#C49B3A', icon: '#E8B460' },
    plan: { bg: 'rgba(168, 195, 160, 0.22)', text: '#8BA888', icon: '#A8C3A0' },
    image: { bg: 'rgba(184, 200, 212, 0.25)', text: '#8BA8C3', icon: '#B8C8D4' }
  }
  return colors[type] || colors.specimen
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  return dateStr.slice(0, 10)
}

onMounted(() => {
  loadFolders()
  loadList()
})
</script>

<template>
  <div class="favorites-wrapper">
    <div class="section-header">
      <div>
        <h2 class="page-title">
          <n-icon size="26" color="#D4A5A5"><Bookmark /></n-icon>
          我的收藏夹
        </h2>
        <p class="page-subtitle">珍藏每一份喜欢与感动，让美好随时可以回顾</p>
      </div>
      <n-button type="primary" size="large" @click="openCreateFolder">
        <template #icon><n-icon :component="Add" /></template>
        新建收藏夹
      </n-button>
    </div>

    <div class="main-layout">
      <div class="left-sidebar">
        <n-card class="sidebar-card" size="large" :bordered="false">
          <template #header>
            <div class="sidebar-header">
              <span class="sidebar-title">
                <n-icon size="18" color="#D4A5A5"><FolderOpen /></n-icon>
                收藏夹
              </span>
              <span class="decor-star">⭐</span>
            </div>
          </template>

          <n-list size="large" style="padding: 0;" class="folder-list">
            <n-list-item
              v-for="folder in allFolders()"
              :key="folder.id"
              :class="{ 'folder-active': activeFolder === folder.id }"
              @click="handleSelectFolder(folder.id)"
            >
              <div class="folder-item">
                <div class="folder-left">
                  <n-icon
                    :component="activeFolder === folder.id ? FolderOpen : Folder"
                    :size="18"
                    :color="activeFolder === folder.id ? '#D4A5A5' : '#B8A8A6'"
                  />
                  <span class="folder-name">{{ folder.name }}</span>
                </div>
                <n-tag
                  round
                  size="tiny"
                  :style="{
                    background: activeFolder === folder.id ? 'rgba(212, 165, 165, 0.25)' : 'rgba(240, 230, 222, 0.6)',
                    color: activeFolder === folder.id ? '#C08990' : '#8B7D7B',
                    border: 'none'
                  }"
                >
                  {{ folder.count ?? 0 }}
                </n-tag>
              </div>
            </n-list-item>
          </n-list>

          <n-divider style="margin: 16px 0;" />

          <div class="type-filter-section">
            <div class="filter-label">
              <n-icon size="15" color="#F5C86B"><Star /></n-icon>
              按类型筛选
            </div>
            <n-select
              v-model:value="filterType"
              :options="typeOptions"
              size="medium"
              clearable
              style="width: 100%; margin-top: 8px;"
              @update:value="() => {}"
            />
          </div>

          <n-divider style="margin: 16px 0;" />

          <div class="summary-section">
            <div class="summary-title">
              <n-icon size="15" color="#E88A9A"><Heart /></n-icon>
              收藏统计
            </div>
            <div class="summary-total">
              <span class="total-num">{{ totalCount }}</span>
              <span class="total-label">件收藏</span>
            </div>
            <div class="type-breakdown">
              <div
                v-for="(label, key) in typeLabels"
                :key="key"
                class="type-item"
              >
                <div class="type-icon-wrap" :style="{ background: getTypeColor(key).bg }">
                  <n-icon :component="typeIcons[key]" :size="14" :color="getTypeColor(key).icon" />
                </div>
                <span class="type-label-text">{{ label }}</span>
                <span class="type-count">{{ typeStats[key] || 0 }}</span>
              </div>
            </div>
          </div>
        </n-card>
      </div>

      <div class="right-content">
        <div v-if="loading" class="list-loading">
          <n-skeleton :repeat="3" text :row="3" style="max-width: 800px; margin: 0 auto;" />
        </div>

        <div v-else-if="filteredList.length === 0" class="empty-state">
          <n-empty description="这里还空空如也，去收藏一些喜爱的内容吧" :show-icon="false">
            <template #image>
              <div class="empty-icon-wrap">
                <span class="empty-emoji">📔</span>
                <span class="empty-decor-star star-1">⭐</span>
                <span class="empty-decor-star star-2">✨</span>
                <span class="empty-decor-star star-3">🌟</span>
              </div>
            </template>
          </n-empty>
        </div>

        <template v-else>
          <div class="favorites-grid-section">
            <n-grid :cols="3" responsive="screen" :x-gap="16" :y-gap="16">
              <n-grid-item
                v-for="item in filteredList"
                :key="item.id"
                span="3 s:3 m:2 l:2 xl:1"
              >
                <div class="favorite-card" :class="'card-' + item.item_type">
                  <div class="card-decor">
                    <span class="decor-star-mini star-a">⭐</span>
                    <span class="decor-star-mini star-b">✦</span>
                  </div>

                  <n-button
                    class="remove-btn"
                    quaternary
                    size="tiny"
                    circle
                    @click="handleRemoveFavorite(item)"
                  >
                    <template #icon><n-icon :component="Close" /></template>
                  </n-button>

                  <div class="type-badge" :style="{ background: getTypeColor(item.item_type).bg, color: getTypeColor(item.item_type).text }">
                    <n-icon :component="typeIcons[item.item_type] || Star" :size="12" />
                    {{ typeLabels[item.item_type] || '其他' }}
                  </div>

                  <template v-if="item.item_type === 'specimen'">
                    <div class="card-image-wrap">
                      <n-image
                        v-if="item.specimen?.image_url || item.image_url"
                        :src="item.specimen?.image_url || item.image_url"
                        object-fit="cover"
                        class="card-image"
                      />
                      <div v-else class="card-image-placeholder">
                        <n-icon :component="FlowerOutline" size="38" color="#D4B8B0" />
                      </div>
                    </div>
                    <div class="card-body">
                      <div class="card-title">
                        <n-ellipsis :line-clamp="1">{{ item.specimen?.name || item.item_name || item.title || '未命名标本' }}</n-ellipsis>
                      </div>
                      <div class="card-meta-row">
                        <n-tag v-if="item.specimen?.category" round size="tiny" class="meta-tag">
                          {{ item.specimen.category }}
                        </n-tag>
                      </div>
                    </div>
                  </template>

                  <template v-else-if="item.item_type === 'note'">
                    <div class="card-note-header">
                      <div class="note-icon-wrap">
                        <n-icon :component="Book" :size="24" color="#E8B460" />
                      </div>
                      <div class="note-category-tag">
                        {{ item.note?.category || '技术笔记' }}
                      </div>
                    </div>
                    <div class="card-body">
                      <div class="card-title note-title">
                        <n-ellipsis :line-clamp="1">{{ item.note?.title || item.item_name || item.title || '未命名笔记' }}</n-ellipsis>
                      </div>
                      <div class="card-summary">
                        <n-ellipsis :line-clamp="3">{{ item.note?.content || item.item_description || item.description || '暂无内容' }}</n-ellipsis>
                      </div>
                    </div>
                  </template>

                  <template v-else-if="item.item_type === 'plan'">
                    <div class="card-image-wrap plan-wrap">
                      <n-image
                        v-if="item.plan?.sketch_url || item.plan?.image_url || item.image_url"
                        :src="item.plan?.sketch_url || item.plan?.image_url || item.image_url"
                        object-fit="cover"
                        class="card-image"
                      />
                      <div v-else class="card-image-placeholder plan-placeholder">
                        <n-icon :component="ColorPalette" size="38" color="#A8C3A0" />
                      </div>
                    </div>
                    <div class="card-body">
                      <div class="card-title">
                        <n-ellipsis :line-clamp="1">{{ item.plan?.name || item.item_name || item.title || '未命名方案' }}</n-ellipsis>
                      </div>
                      <div class="card-meta-row">
                        <n-tag v-if="item.plan?.style" round size="tiny" class="meta-tag-green">
                          {{ item.plan.style }}
                        </n-tag>
                        <n-tag v-if="item.plan?.scene" round size="tiny" class="meta-tag-blue">
                          {{ item.plan.scene }}
                        </n-tag>
                      </div>
                    </div>
                  </template>

                  <template v-else-if="item.item_type === 'image'">
                    <div class="card-image-wrap image-wrap">
                      <n-image
                        v-if="item.image?.image_url || item.image_url"
                        :src="item.image?.image_url || item.image_url"
                        object-fit="cover"
                        class="card-image"
                      />
                      <div v-else class="card-image-placeholder">
                        <n-icon :component="ImagesOutline" size="38" color="#B8A8A6" />
                      </div>
                    </div>
                    <div class="card-body">
                      <div class="card-title">
                        <n-ellipsis :line-clamp="1">{{ item.image?.title || item.item_name || item.title || '未命名图片' }}</n-ellipsis>
                      </div>
                    </div>
                  </template>

                  <template v-else>
                    <div class="card-body">
                      <div class="card-title">
                        <n-ellipsis :line-clamp="2">{{ item.item_name || item.title || '未命名' }}</n-ellipsis>
                      </div>
                    </div>
                  </template>

                  <div class="card-footer">
                    <span class="fav-time">
                      <n-icon size="11" color="#B8A8A6"><Calendar /></n-icon>
                      {{ formatDate(item.created_at || item.favorited_at) }}
                    </span>
                    <span v-if="item.folder_name" class="fav-folder">
                      <n-icon size="11" color="#B8A8A6"><Folder /></n-icon>
                      {{ item.folder_name }}
                    </span>
                  </div>

                  <div v-if="item.remark || item.note" class="fav-remark">
                    <n-tooltip :trigger="'hover'" :content="item.remark || item.note">
                      <div class="remark-inner">
                        <n-icon size="11" color="#F5C86B"><CreateOutline /></n-icon>
                        <n-ellipsis :line-clamp="1">{{ item.remark || item.note }}</n-ellipsis>
                      </div>
                    </n-tooltip>
                  </div>
                </div>
              </n-grid-item>
            </n-grid>
          </div>

          <div class="bottom-summary-card">
            <n-card size="large" :bordered="false" class="summary-card-inner">
              <div class="summary-inner-wrap">
                <div class="summary-left">
                  <span class="summary-main-icon">
                    <n-icon size="28" color="#D4A5A5"><Bookmark /></n-icon>
                  </span>
                  <div>
                    <div class="summary-big-num">{{ totalCount }}</div>
                    <div class="summary-big-label">件珍贵收藏</div>
                  </div>
                </div>
                <div class="summary-divider" />
                <div class="summary-right">
                  <div
                    v-for="(label, key) in typeLabels"
                    :key="key"
                    class="mini-stat"
                  >
                    <div class="mini-num" :style="{ color: getTypeColor(key).icon }">
                      {{ typeStats[key] || 0 }}
                    </div>
                    <div class="mini-label">{{ label }}</div>
                  </div>
                </div>
                <div class="corner-decor corner-1">❀</div>
                <div class="corner-decor corner-2">✿</div>
              </div>
            </n-card>
          </div>
        </template>
      </div>
    </div>

    <n-modal
      v-model:show="showFolderModal"
      preset="card"
      title="新建收藏夹"
      style="width: 440px; max-width: 92vw;"
      :mask-closable="false"
      class="folder-modal"
    >
      <n-form ref="folderFormRef" :model="{ name: folderName }" :rules="folderRules" label-placement="top">
        <n-form-item label="收藏夹名称" path="name">
          <n-input v-model:value="folderName" placeholder="给收藏夹起个温馨的名字" maxlength="30" />
        </n-form-item>
      </n-form>
      <div class="folder-tips">
        <n-icon size="13" color="#F5C86B"><Star /></n-icon>
        <span>收藏夹可以帮助你更好地分类整理喜爱的内容~</span>
      </div>
      <template #footer>
        <NSpace justify="end">
          <n-button @click="showFolderModal = false">取消</n-button>
          <n-button type="primary" @click="handleFolderSubmit">
            <template #icon><n-icon :component="CheckmarkCircleOutline" /></template>
            创建
          </n-button>
        </NSpace>
      </template>
    </n-modal>
  </div>
</template>

<style lang="scss" scoped>
.favorites-wrapper { background: transparent; }

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

.main-layout {
  display: grid;
  grid-template-columns: 260px 1fr;
  gap: 20px;
  align-items: flex-start;

  @media (max-width: 900px) {
    grid-template-columns: 1fr;
  }
}

.left-sidebar {
  position: sticky;
  top: 20px;
}

.sidebar-card {
  background: linear-gradient(180deg, #FFFDF6 0%, #FFF9EA 100%);
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(212, 165, 165, 0.1);
  border: 1px solid rgba(240, 230, 222, 0.8) !important;
  position: relative;

  &::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 4px; height: 100%;
    background: linear-gradient(180deg, #D4A5A5, #F5E6A3);
    border-radius: 16px 0 0 16px;
    opacity: 0.55;
  }
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sidebar-title {
  font-size: 15px;
  font-weight: 700;
  color: #5C4A4A;
  display: flex;
  align-items: center;
  gap: 8px;
}

.decor-star {
  font-size: 16px;
  animation: twinkle 2s ease-in-out infinite;
}

@keyframes twinkle {
  0%, 100% { opacity: 0.6; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.15); }
}

.folder-list {
  :deep(.n-list-item) {
    padding: 8px 10px !important;
    border-radius: 10px;
    margin-bottom: 4px;
    transition: all 0.25s ease;

    &:hover {
      background: rgba(245, 230, 163, 0.2);
    }

    &.folder-active {
      background: linear-gradient(135deg, rgba(212, 165, 165, 0.18), rgba(245, 230, 163, 0.15));
    }
  }
}

.folder-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.folder-left {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
  min-width: 0;
}

.folder-name {
  font-size: 14px;
  font-weight: 500;
  color: #5C4A4A;
}

.folder-active .folder-name {
  font-weight: 700;
  color: #C08990;
}

.filter-label {
  font-size: 13px;
  font-weight: 600;
  color: #5C4A4A;
  display: flex;
  align-items: center;
  gap: 6px;
}

.summary-title {
  font-size: 13px;
  font-weight: 600;
  color: #5C4A4A;
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 10px;
}

.summary-total {
  display: flex;
  align-items: baseline;
  gap: 6px;
  padding: 12px;
  background: linear-gradient(135deg, rgba(212, 165, 165, 0.12), rgba(245, 230, 163, 0.18));
  border-radius: 12px;
  margin-bottom: 14px;
}

.total-num {
  font-size: 28px;
  font-weight: 700;
  color: #E88A9A;
  font-family: 'Segoe UI', sans-serif;
}

.total-label {
  font-size: 13px;
  color: #8B7D7B;
  font-weight: 500;
}

.type-breakdown {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.type-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 8px;
  border-radius: 8px;
  transition: background 0.2s;

  &:hover {
    background: rgba(250, 246, 238, 0.6);
  }
}

.type-icon-wrap {
  width: 26px;
  height: 26px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.type-label-text {
  flex: 1;
  font-size: 13px;
  color: #5C4A4A;
  font-weight: 500;
}

.type-count {
  font-size: 14px;
  font-weight: 700;
  color: #8B7D7B;
  font-family: 'Segoe UI', sans-serif;
}

.list-loading { padding: 60px 20px; }

.empty-state { padding: 60px 20px; }

.empty-icon-wrap {
  position: relative;
  width: 100px;
  height: 100px;
  margin: 0 auto 10px;
  .empty-emoji {
    font-size: 52px;
    opacity: 0.75;
  }
}

.empty-decor-star {
  position: absolute;
  animation: twinkle 2s ease-in-out infinite;

  &.star-1 {
    top: 0; right: 0;
    font-size: 18px;
    animation-delay: 0s;
  }
  &.star-2 {
    bottom: 10px; right: -6px;
    font-size: 14px;
    animation-delay: 0.6s;
  }
  &.star-3 {
    top: 20px; left: -10px;
    font-size: 16px;
    animation-delay: 1.2s;
  }
}

.favorites-grid-section { margin-bottom: 20px; }

.favorite-card {
  background: linear-gradient(135deg, rgba(255, 253, 246, 1), rgba(255, 249, 234, 0.8));
  border-radius: 16px;
  border: 1px solid rgba(240, 230, 222, 0.9);
  overflow: hidden;
  transition: all 0.35s ease;
  position: relative;
  padding: 14px;
  padding-top: 38px;

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 14px 36px rgba(212, 165, 165, 0.22);
    border-color: rgba(245, 230, 163, 0.55);
  }

  &.card-note {
    background: linear-gradient(135deg, rgba(255, 253, 246, 1), rgba(255, 250, 235, 0.85));
  }
  &.card-plan {
    background: linear-gradient(135deg, rgba(255, 253, 246, 1), rgba(245, 250, 243, 0.75));
  }
  &.card-image {
    background: linear-gradient(135deg, rgba(255, 253, 246, 1), rgba(245, 248, 250, 0.75));
  }
}

.card-decor {
  position: absolute;
  pointer-events: none;
}

.decor-star-mini {
  position: absolute;
  opacity: 0.45;
  animation: twinkle 2.5s ease-in-out infinite;

  &.star-a {
    top: 8px;
    left: 14px;
    font-size: 12px;
    animation-delay: 0s;
  }
  &.star-b {
    top: 18px;
    right: 54px;
    font-size: 10px;
    color: #F5C86B;
    animation-delay: 1s;
  }
}

.remove-btn {
  position: absolute !important;
  top: 8px !important;
  right: 10px !important;
  z-index: 3;
  opacity: 0;
  transform: scale(0.8);
  transition: all 0.25s ease;
}

.favorite-card:hover .remove-btn {
  opacity: 1;
  transform: scale(1);
}

.type-badge {
  position: absolute;
  top: 10px;
  left: 36px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 10px;
  border-radius: 8px;
  font-size: 11px;
  font-weight: 600;
  z-index: 2;
}

.card-image-wrap {
  width: 100%;
  padding-top: 72%;
  position: relative;
  border-radius: 12px;
  overflow: hidden;
  background: linear-gradient(135deg, #FAF6EE, #F5EEE8);
  margin-bottom: 12px;

  &.plan-wrap {
    background: linear-gradient(135deg, #EEF6EE, #F0F5EE);
  }
  &.image-wrap {
    background: linear-gradient(135deg, #EEF2F5, #F0F4F5);
  }
}

.card-image {
  position: absolute;
  top: 0; left: 0;
  width: 100%; height: 100%;
}

.card-image-placeholder {
  position: absolute;
  top: 0; left: 0;
  width: 100%; height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;

  &.plan-placeholder {
    background: linear-gradient(135deg, #EEF6EE, #F0F5EE);
  }
}

.card-note-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 14px 0;
  margin: -14px -14px 10px;
  background: linear-gradient(135deg, rgba(245, 230, 163, 0.2), rgba(255, 249, 234, 0.3));
  border-radius: 14px 14px 0 0;
  padding-bottom: 14px;
}

.note-icon-wrap {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: rgba(245, 230, 163, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
}

.note-category-tag {
  padding: 4px 10px;
  background: rgba(245, 230, 163, 0.3);
  color: #C49B3A;
  border-radius: 8px;
  font-size: 11px;
  font-weight: 600;
}

.card-body { margin-bottom: 10px; }

.card-title {
  font-size: 15px;
  font-weight: 700;
  color: #5C4A4A;
  line-height: 1.4;
  margin-bottom: 8px;

  &.note-title {
    padding-left: 4px;
  }
}

.card-summary {
  font-size: 13px;
  color: #8B7D7B;
  line-height: 1.65;
  padding: 0 4px;
}

.card-meta-row {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.meta-tag {
  background: rgba(212, 165, 165, 0.2);
  color: #C08990;
  border: none;
}

.meta-tag-green {
  background: rgba(168, 195, 160, 0.22);
  color: #8BA888;
  border: none;
}

.meta-tag-blue {
  background: rgba(184, 200, 212, 0.25);
  color: #8BA8C3;
  border: none;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 10px;
  border-top: 1px dashed rgba(240, 230, 222, 0.85);
}

.fav-time,
.fav-folder {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: #B8A8A6;
}

.fav-remark {
  margin-top: 10px;
  padding: 8px 10px;
  background: linear-gradient(135deg, rgba(255, 249, 234, 0.95), rgba(250, 246, 238, 0.85));
  border-radius: 10px;
  border: 1px dashed rgba(245, 230, 163, 0.5);
}

.remark-inner {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  font-size: 12px;
  color: #8B7D7B;
  line-height: 1.5;
}

.bottom-summary-card {
  margin-top: 8px;
}

.summary-card-inner {
  background: linear-gradient(135deg, rgba(212, 165, 165, 0.12), rgba(245, 230, 163, 0.18)) !important;
  border-radius: 18px !important;
  border: 1px dashed rgba(212, 165, 165, 0.35) !important;
  box-shadow: 0 4px 20px rgba(212, 165, 165, 0.08) !important;
  overflow: hidden;
  padding: 8px 16px;
}

.summary-inner-wrap {
  display: flex;
  align-items: center;
  position: relative;
  padding: 8px 0;
}

.summary-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.summary-main-icon {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  background: linear-gradient(135deg, rgba(212, 165, 165, 0.25), rgba(245, 230, 163, 0.3));
  display: flex;
  align-items: center;
  justify-content: center;
}

.summary-big-num {
  font-size: 32px;
  font-weight: 800;
  color: #E88A9A;
  font-family: 'Segoe UI', sans-serif;
  line-height: 1;
  letter-spacing: -1px;
}

.summary-big-label {
  font-size: 13px;
  color: #8B7D7B;
  font-weight: 600;
  margin-top: 2px;
}

.summary-divider {
  width: 1px;
  height: 48px;
  background: linear-gradient(180deg, transparent, rgba(212, 165, 165, 0.25), transparent);
  margin: 0 32px;
}

.summary-right {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.mini-stat {
  text-align: center;
}

.mini-num {
  font-size: 22px;
  font-weight: 700;
  font-family: 'Segoe UI', sans-serif;
  line-height: 1;
  margin-bottom: 4px;
}

.mini-label {
  font-size: 12px;
  color: #8B7D7B;
  font-weight: 500;
}

.corner-decor {
  position: absolute;
  font-size: 28px;
  opacity: 0.1;
  color: #C08990;
  pointer-events: none;

  &.corner-1 {
    top: -4px;
    right: 16px;
    transform: rotate(15deg);
  }
  &.corner-2 {
    bottom: -6px;
    left: 30%;
    transform: rotate(-20deg);
    font-size: 24px;
    color: #E8B460;
  }
}

.folder-modal {
  :deep(.n-card) {
    border-radius: 18px !important;
    background: linear-gradient(180deg, #FFFDF6 0%, #FFF9EA 100%);
  }
  :deep(.n-card-header) {
    border-bottom: 1px solid rgba(240, 230, 222, 0.7) !important;
  }
}

.folder-tips {
  margin-top: 8px;
  padding: 10px 12px;
  background: rgba(255, 249, 234, 0.8);
  border-radius: 10px;
  border: 1px dashed rgba(245, 230, 163, 0.6);
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #8B7D7B;
}
</style>
