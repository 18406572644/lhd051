<script setup>
import { ref, onMounted, computed, h, reactive } from 'vue'
import {
  NCard, NGrid, NGridItem, NTag, NIcon, NSpace, NButton,
  NInput, NSelect, NSwitch, NModal, NForm, NFormItem,
  NUpload, NUploadDragger, NImage, NEllipsis, NInputNumber,
  NDatePicker, useMessage, useDialog, NEmpty, NPagination, NSkeleton,
  NGallery
} from 'naive-ui'
import {
  Images, Add, Search, CreateOutline, TrashOutline,
  ImagesOutline, CheckmarkCircleOutline, Close, Star,
  Sparkles, SwapHorizontal
} from '@vicons/ionicons5'
import { imagesApi, uploadApi, specimensApi } from '@/api'

const message = useMessage()
const dialog = useDialog()

const loading = ref(false)
const list = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(12)

const keyword = ref('')
const filterAngle = ref(null)
const filterLighting = ref(null)
const filterBackground = ref(null)
const filterCover = ref(null)
const filterSpecimen = ref(null)

const angleOptions = ref([])
const lightingOptions = ref([])
const backgroundOptions = ref([])
const specimenOptions = ref([])

const showUploadModal = ref(false)
const showEditModal = ref(false)
const formRef = ref(null)
const editRef = ref(null)
const formMode = ref('create')

const batchUploading = ref(false)
const batchFiles = reactive([])
const batchUploads = reactive([])

const editData = reactive({
  id: null,
  title: '',
  specimen_id: null,
  shot_angle: null,
  lighting: null,
  background: null,
  description: '',
  resolution: '',
  shot_date: null,
  photographer: '',
  is_cover: false,
  sort_order: 0
})

const editFormRules = {
  title: { required: true, message: '请输入标题', trigger: 'blur' }
}

async function loadOptions() {
  try {
    const [angleRes, lightingRes, bgRes] = await Promise.all([
      imagesApi.shotAngles(),
      imagesApi.lightings(),
      imagesApi.backgrounds()
    ])
    if (angleRes?.data?.shot_angles) {
      angleOptions.value = angleRes.data.shot_angles.map(a => ({ label: a, value: a }))
    }
    if (lightingRes?.data?.lightings) {
      lightingOptions.value = lightingRes.data.lightings.map(l => ({ label: l, value: l }))
    }
    if (bgRes?.data?.backgrounds) {
      backgroundOptions.value = bgRes.data.backgrounds.map(b => ({ label: b, value: b }))
    }
  } catch (e) {
    message.error('加载选项失败')
  }
}

async function loadSpecimenOptions(query) {
  try {
    const res = await specimensApi.list({ keyword: query || '', page_size: 100 })
    const items = res?.data?.items || res?.data || []
    specimenOptions.value = items.map(s => ({ label: s.name || '未命名', value: s.id }))
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
    if (filterAngle.value) params.shot_angle = filterAngle.value
    if (filterLighting.value) params.lighting = filterLighting.value
    if (filterBackground.value) params.background = filterBackground.value
    if (filterCover.value !== null && filterCover.value !== undefined) {
      params.is_cover = filterCover.value
    }
    if (filterSpecimen.value) params.specimen_id = filterSpecimen.value
    const res = await imagesApi.list(params)
    if (res?.data?.items) {
      list.value = res.data.items
      total.value = res.data.total || 0
    } else if (res?.data) {
      list.value = Array.isArray(res.data) ? res.data : []
      total.value = list.value.length
    }
  } catch (e) {
    message.error('加载图片列表失败')
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

function openUpload() {
  batchFiles.length = 0
  batchUploads.length = 0
  showUploadModal.value = true
}

function handleBatchBeforeUpload({ file }) {
  batchFiles.push(file)
  batchUploads.push({
    file: file.file,
    title: file.name?.replace(/\.[^/.]+$/, '') || '未命名',
    shot_angle: null,
    specimen_id: null,
    url: ''
  })
  return false
}

async function handleBatchSubmit() {
  if (batchUploads.length === 0) {
    message.warning('请先选择图片')
    return
  }
  batchUploading.value = true
  try {
    const files = batchUploads.map(b => b.file)
    const uploadRes = await uploadApi.uploadBatch(files, 'gallery')
    const urls = uploadRes?.data?.urls || uploadRes?.data || []
    for (let i = 0; i < batchUploads.length; i++) {
      const item = batchUploads[i]
      const url = Array.isArray(urls) ? (urls[i] || urls[0]) : ''
      try {
        await imagesApi.create({
          title: item.title || '未命名',
          image_url: item.url || url,
          shot_angle: item.shot_angle,
          specimen_id: item.specimen_id
        })
      } catch (e) {}
    }
    message.success('批量上传成功')
    showUploadModal.value = false
    loadList()
  } catch (e) {
    message.error('上传失败')
  } finally {
    batchUploading.value = false
  }
}

function openEdit(item) {
  formMode.value = 'edit'
  Object.assign(editData, {
    id: item.id,
    title: item.title || '',
    specimen_id: item.specimen_id || null,
    shot_angle: item.shot_angle || null,
    lighting: item.lighting || null,
    background: item.background || null,
    description: item.description || '',
    resolution: item.resolution || '',
    shot_date: item.shot_date || null,
    photographer: item.photographer || '',
    is_cover: item.is_cover || false,
    sort_order: item.sort_order || 0
  })
  loadSpecimenOptions()
  showEditModal.value = true
}

function handleEditSubmit() {
  editRef.value?.validate(async (errors) => {
    if (errors) return
    try {
      const payload = { ...editData }
      delete payload.id
      await imagesApi.update(editData.id, payload)
      message.success('保存成功')
      showEditModal.value = false
      loadList()
    } catch (e) {
      message.error('保存失败')
    }
  })
}

async function handleSetCover(item) {
  try {
    await imagesApi.update(item.id, { is_cover: true })
    message.success('已设为封面')
    loadList()
  } catch (e) {
    message.error('操作失败')
  }
}

function handleDelete(item) {
  dialog.warning({
    title: '确认删除',
    content: `确定要删除图片「${item.title || '未命名'}」吗？`,
    positiveText: '删除',
    negativeText: '取消',
    positiveButtonProps: { color: '#E88A9A' },
    onPositiveClick: async () => {
      try {
        await imagesApi.delete(item.id)
        message.success('删除成功')
        loadList()
      } catch (e) {
        message.error('删除失败')
      }
    }
  })
}

const imageUrls = computed(() => list.value.map(i => i.image_url).filter(Boolean))

onMounted(() => {
  loadOptions()
  loadSpecimenOptions()
  loadList()
})
</script>

<template>
  <div class="gallery-wrapper">
    <n-gallery :images="imageUrls" />
    <div class="section-header">
      <div>
        <h2 class="page-title">
          <n-icon size="26" color="#D4A5A5"><Images /></n-icon>
          实拍图片管理
        </h2>
        <p class="page-subtitle">用镜头定格每一件作品的动人瞬间</p>
      </div>
      <n-button type="primary" size="large" @click="openUpload">
        <template #icon><n-icon :component="Add" /></template>
        上传图片
      </n-button>
    </div>

    <n-card class="filter-card" size="large" :bordered="false">
      <n-space vertical :size="16" style="width: 100%;">
        <div class="filter-row">
          <div class="filter-search-wrap">
            <n-input
              v-model:value="keyword"
              placeholder="搜索标题、描述..."
              clearable
              size="large"
              style="width: 260px;"
              @keyup.enter="handleSearch"
            >
              <template #prefix><n-icon :component="Search" /></template>
            </n-input>
          </div>
          <n-space :size="12" wrap>
            <n-select
              v-model:value="filterAngle"
              placeholder="拍摄角度"
              :options="angleOptions"
              clearable
              size="medium"
              style="width: 130px;"
              @update:value="handleFilterChange"
            />
            <n-select
              v-model:value="filterLighting"
              placeholder="光线"
              :options="lightingOptions"
              clearable
              size="medium"
              style="width: 120px;"
              @update:value="handleFilterChange"
            />
            <n-select
              v-model:value="filterBackground"
              placeholder="背景"
              :options="backgroundOptions"
              clearable
              style="width: 120px;"
              @update:value="handleFilterChange"
            />
            <n-select
              v-model:value="filterSpecimen"
              placeholder="关联标本"
              :options="specimenOptions"
              clearable
              filterable
              remote
              :on-search="loadSpecimenOptions"
              size="medium"
              style="width: 160px;"
              @update:value="handleFilterChange"
            />
            <div class="filter-switch-item">
              <span class="filter-switch-label">仅看封面</span>
              <n-switch v-model:value="filterCover" @update:value="handleFilterChange" />
            </div>
          </n-space>
        </div>
      </n-space>
    </n-card>

    <div v-if="loading" class="list-loading">
      <n-skeleton :repeat="4" text :row="3" style="max-width: 800px; margin: 0 auto;" />
    </div>

    <div v-else-if="list.length === 0" class="empty-state">
      <n-empty description="暂无图片，点击右上角上传第一张吧" :show-icon="false">
        <template #image>
          <div class="empty-icon-wrap">
            <span class="empty-emoji">📷</span>
          </div>
        </template>
        <n-button type="primary" @click="openUpload">
          <template #icon><n-icon :component="Add" /></template>
          上传图片
        </n-button>
      </n-empty>
    </div>

    <template v-else>
      <div class="gallery-grid-section">
        <n-grid :cols="4" responsive="screen" :x-gap="16" :y-gap="16">
          <n-grid-item v-for="item in list" :key="item.id" span="4 s:2 m:2 l:2 xl:1">
            <div class="image-card">
              <div class="image-wrap">
                <n-image
                  v-if="item.image_url"
                  :src="item.image_url"
                  :alt="item.title"
                  group-name="gallery"
                  object-fit="cover"
                  class="gallery-image"
                />
                <div v-else class="image-placeholder">
                  <n-icon :component="ImagesOutline" size="40" color="#D4B8B0" />
                </div>
                <div class="image-overlay">
                  <n-ellipsis :line-clamp="1" class="overlay-title">{{ item.title || '未命名' }}</n-ellipsis>
                  <div class="overlay-meta">
                    <span v-if="item.shot_angle" class="meta-chip">{{ item.shot_angle }}</span>
                    <span v-if="item.lighting" class="meta-chip">{{ item.lighting }}</span>
                  </div>
                  <span v-if="item.resolution" class="meta-resolution">{{ item.resolution }}</span>
                </div>
                <div v-if="item.is_cover" class="cover-badge">
                  <n-icon size="12"><Star /></n-icon>
                  封面
                </div>
                <div class="image-actions">
                  <n-button
                    quaternary size="tiny" @click.stop="openEdit(item)">
                    <template #icon><n-icon :component="CreateOutline" /></template>
                  </n-button>
                  <n-button
                    quaternary size="tiny"
                    :disabled="item.is_cover"
                    @click.stop="handleSetCover(item)">
                    <template #icon><n-icon :component="Star" /></template>
                  </n-button>
                  <n-button
                    quaternary size="tiny" @click.stop="handleDelete(item)">
                    <template #icon><n-icon :component="TrashOutline" /></template>
                  </n-button>
                </div>
              </div>
              <div class="image-info">
                <div class="image-title">
                  <n-ellipsis :line-clamp="1">{{ item.title || '未命名' }}</n-ellipsis>
                </div>
                <div class="image-tags">
                  <n-tag v-if="item.shot_angle" round size="tiny" class="info-tag">
                    {{ item.shot_angle }}
                  </n-tag>
                  <n-tag v-if="item.background" round size="tiny" class="info-tag-bg">
                    {{ item.background }}
                  </n-tag>
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
          :page-sizes="[8, 12, 24, 48]"
          show-size-picker
          show-quick-jumper
          @update:page="handlePageChange"
        />
      </div>
    </template>

    <n-modal
      v-model:show="showUploadModal"
      preset="card"
      title="批量上传图片"
      style="width: 720px; max-width: 92vw;"
      :mask-closable="false"
      class="upload-modal"
    >
      <div class="upload-zone">
        <n-upload
          :show-file-list="false"
          multiple
          drag
          accept="image/*"
          @before-upload="handleBatchBeforeUpload"
        >
          <n-upload-dragger style="padding: 24px;">
            <div style="margin-bottom: 12px;">
              <n-icon size="36" color="#D4A5A5"><ImagesOutline /></n-icon>
            </div>
            <div style="color: #5C4A4A; font-weight: 600; margin-bottom: 6px; font-size: 15px;">
              点击或拖拽图片到此区域
            </div>
            <div style="color: #B8A6A6; font-size: 12px;">
              支持 JPG / PNG / WEBP，可多选
            </div>
          </n-upload-dragger>
        </n-upload>
      </div>

      <div v-if="batchUploads.length > 0" class="batch-list">
        <div class="batch-list-header">待上传 ({{ batchUploads.length }})</div>
        <div
          v-for="(item, idx) in batchUploads" :key="idx" class="batch-item">
          <div class="batch-thumb">
            <img :src="URL.createObjectURL(item.file)" />
          </div>
          <div class="batch-fields">
            <n-input v-model:value="item.title" placeholder="图片标题" size="small" />
            <div class="batch-fields-row">
              <n-select
                v-model:value="item.shot_angle"
                :options="angleOptions"
                placeholder="拍摄角度"
                clearable
                size="small"
                style="width: 140px;"
              />
              <n-select
                v-model:value="item.specimen_id"
                :options="specimenOptions"
                placeholder="关联标本"
                clearable
                filterable
                size="small"
                style="width: 180px;"
              />
            </div>
          </div>
          <n-button
            quaternary size="tiny" type="error" @click="batchUploads.splice(idx, 1)">
            <template #icon><n-icon :component="Close" /></template>
          </n-button>
        </div>
      </div>

      <template #footer>
        <NSpace justify="end">
          <n-button @click="showUploadModal = false">取消</n-button>
          <n-button type="primary" :loading="batchUploading" @click="handleBatchSubmit">
            <template #icon><n-icon :component="CheckmarkCircleOutline" /></template>
            确认上传
          </n-button>
        </NSpace>
      </template>
    </n-modal>

    <n-modal
      v-model:show="showEditModal"
      preset="card"
      title="编辑图片信息"
      style="width: 640px; max-width: 92vw;"
      :mask-closable="false"
      class="edit-modal"
    >
      <n-form ref="editRef" :model="editData" :rules="editFormRules" label-placement="left" label-width="100px">
        <n-grid :cols="2" :x-gap="16" :y-gap="4">
          <n-grid-item span="2 s:2 m:2">
            <n-form-item label="标题" path="title">
              <n-input v-model:value="editData.title" placeholder="请输入图片标题" maxlength="100" />
            </n-form-item>
          </n-grid-item>
          <n-grid-item span="2 s:2 m:1">
            <n-form-item label="关联标本">
              <n-select
                v-model:value="editData.specimen_id"
                :options="specimenOptions"
                placeholder="选择关联标本"
                clearable
                filterable
              />
            </n-form-item>
          </n-grid-item>
          <n-grid-item span="2 s:2 m:1">
            <n-form-item label="拍摄角度">
              <n-select
                v-model:value="editData.shot_angle"
                :options="angleOptions"
                placeholder="选择角度"
                clearable
              />
            </n-form-item>
          </n-grid-item>
          <n-grid-item span="2 s:2 m:1">
            <n-form-item label="光线">
              <n-select
                v-model:value="editData.lighting"
                :options="lightingOptions"
                placeholder="选择光线"
                clearable
              />
            </n-form-item>
          </n-grid-item>
          <n-grid-item span="2 s:2 m:1">
            <n-form-item label="背景">
              <n-select
                v-model:value="editData.background"
                :options="backgroundOptions"
                placeholder="选择背景"
                clearable
              />
            </n-form-item>
          </n-grid-item>
          <n-grid-item span="2 s:2 m:1">
            <n-form-item label="分辨率">
              <n-input v-model:value="editData.resolution" placeholder="如 1920x1080" maxlength="50" />
            </n-form-item>
          </n-grid-item>
          <n-grid-item span="2 s:2 m:1">
            <n-form-item label="拍摄日期">
              <n-date-picker v-model:value="editData.shot_date" type="date" placeholder="选择日期" style="width: 100%;" />
            </n-form-item>
          </n-grid-item>
          <n-grid-item span="2 s:2 m:1">
            <n-form-item label="拍摄者">
              <n-input v-model:value="editData.photographer" placeholder="拍摄者姓名" maxlength="50" />
            </n-form-item>
          </n-grid-item>
          <n-grid-item span="2 s:2 m:1">
            <n-form-item label="排序">
              <n-input-number v-model:value="editData.sort_order" :min="0" style="width: 100%;" />
            </n-form-item>
          </n-grid-item>
          <n-grid-item span="2 s:2 m:1">
            <n-form-item label="设为封面">
              <n-switch v-model:value="editData.is_cover" />
            </n-form-item>
          </n-grid-item>
        </n-grid>
        <n-form-item label="描述" label-placement="top" style="margin-top: 4px;">
          <n-input v-model:value="editData.description" type="textarea" :rows="3" placeholder="添加图片描述..." maxlength="500" />
        </n-form-item>
      </n-form>
      <template #footer>
        <NSpace justify="end">
          <n-button @click="showEditModal = false">取消</n-button>
          <n-button type="primary" @click="handleEditSubmit">
            <template #icon><n-icon :component="CheckmarkCircleOutline" /></template>
            保存
          </n-button>
        </NSpace>
      </template>
    </n-modal>
  </div>
</template>

<style lang="scss" scoped>
.gallery-wrapper { background: transparent; }

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

.list-loading { padding: 60px 20px; }

.empty-state { padding: 60px 20px; }

.empty-icon-wrap {
  position: relative;
  width: 100px;
  height: 80px;
  margin: 0 auto 10px;
  .empty-emoji {
    font-size: 48px;
    opacity: 0.7;
  }
}

.gallery-grid-section { margin-bottom: 16px; }

.image-card {
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

    .image-overlay {
      opacity: 1;
    }
    .image-actions {
      opacity: 1;
      transform: translateY(0);
    }
  }
}

.image-wrap {
  position: relative;
  width: 100%;
  padding-top: 100%;
  background: linear-gradient(135deg, #FAF6EE, #F5EEE8);
  overflow: hidden;
}

.gallery-image {
  position: absolute;
  top: 0; left: 0;
  width: 100%; height: 100%;
}

.image-placeholder {
  position: absolute;
  top: 0; left: 0;
  width: 100%; height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.image-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, transparent 30%, rgba(92, 74, 74, 0.8) 100%);
  padding: 14px;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  opacity: 0;
  transition: opacity 0.3s ease;
  backdrop-filter: blur(2px);
}

.overlay-title {
  color: #FFFDF6;
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 6px;
}

.overlay-meta {
  display: flex;
  gap: 6px;
  margin-bottom: 4px;
  flex-wrap: wrap;
}

.meta-chip {
  display: inline-block;
  padding: 2px 8px;
  background: rgba(255, 253, 246, 0.2);
  border-radius: 6px;
  font-size: 11px;
  color: #FFFDF6;
  backdrop-filter: blur(4px);
}

.meta-resolution {
  font-size: 11px;
  color: rgba(255, 253, 246, 0.7);
}

.cover-badge {
  position: absolute;
  top: 10px;
  left: 10px;
  padding: 4px 10px;
  background: linear-gradient(135deg, rgba(245, 200, 107, 0.95), rgba(232, 180, 96, 0.95));
  color: #5C4A4A;
  font-size: 11px;
  font-weight: 600;
  border-radius: 8px;
  backdrop-filter: blur(4px);
  box-shadow: 0 2px 8px rgba(245, 200, 107, 0.3);
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.image-actions {
  position: absolute;
  right: 8px;
  bottom: 8px;
  display: flex;
  gap: 4px;
  opacity: 0;
  transform: translateY(10px);
  transition: all 0.3s ease;
}

.image-info {
  padding: 12px 14px;
}

.image-title {
  font-size: 14px;
  font-weight: 600;
  color: #5C4A4A;
  margin-bottom: 8px;
  line-height: 1.4;
}

.image-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.info-tag {
  background: rgba(212, 165, 165, 0.18);
  color: #C08990;
  border: none;
}

.info-tag-bg {
  background: rgba(168, 195, 160, 0.18);
  color: #8BA888;
  border: none;
}

.pagination-wrap {
  display: flex;
  justify-content: center;
  padding: 8px 0 16px;
}

.upload-modal {
  :deep(.n-card) {
    border-radius: 18px !important;
    background: linear-gradient(180deg, #FFFDF6 0%, #FAF6EE 100%);
  }
  :deep(.n-card-header) {
    border-bottom: 1px solid rgba(240, 230, 222, 0.7) !important;
  }
}

.upload-zone {
  margin-bottom: 20px;
}

.batch-list {
  max-height: 360px;
  overflow-y: auto;
}

.batch-list-header {
  font-size: 13px;
  font-weight: 600;
  color: #5C4A4A;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px dashed rgba(240, 230, 222, 0.8);
}

.batch-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px;
  background: rgba(250, 246, 238, 0.6);
  border-radius: 12px;
  margin-bottom: 10px;
  border: 1px solid rgba(240, 230, 222, 0.8);
}

.batch-thumb {
  width: 64px;
  height: 64px;
  border-radius: 10px;
  overflow: hidden;
  flex-shrink: 0;
  border: 2px solid rgba(240, 230, 222, 0.9);

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
}

.batch-fields {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.batch-fields-row {
  display: flex;
  gap: 8px;
}

.edit-modal {
  :deep(.n-card) {
    border-radius: 18px !important;
    background: linear-gradient(180deg, #FFFDF6 0%, #FAF6EE 100%);
  }
  :deep(.n-card-header) {
    border-bottom: 1px solid rgba(240, 230, 222, 0.7) !important;
  }
}
</style>
