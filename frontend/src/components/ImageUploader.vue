<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
import {
  NUpload, NUploadDragger, NImage, NButton, NIcon, NProgress,
  NTooltip, useMessage, useDialog, NEmpty, NGrid, NGridItem, NSpace
} from 'naive-ui'
import {
  AddOutline, TrashOutline, ReloadOutline, Close,
  ArrowUpOutline, ArrowDownOutline, ImageOutline
} from '@vicons/ionicons5'
import { uploadApi } from '@/api'
import { validateImage, compressImage } from '@/utils/imageCompressor'

const props = defineProps({
  modelValue: {
    type: [Array, String],
    default: () => []
  },
  folder: {
    type: String,
    default: 'general'
  },
  maxCount: {
    type: Number,
    default: 9
  },
  multiple: {
    type: Boolean,
    default: true
  },
  listType: {
    type: String,
    default: 'image-card'
  },
  disabled: {
    type: Boolean,
    default: false
  },
  compress: {
    type: Boolean,
    default: true
  },
  maxWidth: {
    type: Number,
    default: 1920
  },
  quality: {
    type: Number,
    default: 0.8
  }
})

const emit = defineEmits(['update:modelValue', 'change', 'success', 'error'])

const message = useMessage()
const dialog = useDialog()

const fileList = ref([])
const dragIndex = ref(null)
const dragOverIndex = ref(null)
const dragDom = ref(null)

const showAddButton = computed(() => {
  return !props.disabled && fileList.value.filter(f => f.status !== 'error').length < props.maxCount
})

function generateId() {
  return Date.now().toString(36) + Math.random().toString(36).substr(2)
}

function formatFileSize(bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
}

function getPreviewUrl(file) {
  if (file.url) return file.url
  if (file.preview) return file.preview
  if (file.file) return URL.createObjectURL(file.file)
  return ''
}

async function handleBeforeUpload({ file, fileList: _fileList }) {
  const validation = validateImage(file)
  if (!validation.valid) {
    message.error(validation.error)
    return false
  }
  return true
}

async function handleChange({ file, fileList: _fileList, event }) {
  if (!file) return

  if (file.status === 'added') {
    const validation = validateImage(file.file)
    if (!validation.valid) {
      fileList.value = fileList.value.filter(f => f.id !== file.id)
      message.error(validation.error)
      return
    }

    const fileItem = {
      id: generateId(),
      name: file.name,
      size: file.size,
      status: 'pending',
      progress: 0,
      file: file.file,
      preview: URL.createObjectURL(file.file),
      url: '',
      error: '',
      retryCount: 0
    }
    fileList.value.push(fileItem)
    uploadFile(fileItem)
  }
}

async function uploadFile(fileItem) {
  fileItem.status = 'uploading'
  fileItem.progress = 0

  try {
    let uploadFileData = fileItem.file

    if (props.compress) {
      try {
        const result = await compressImage(fileItem.file, {
          maxWidth: props.maxWidth,
          quality: props.quality
        })
        uploadFileData = result.file
        fileItem.compressedSize = result.compressedSize
        fileItem.originalSize = result.originalSize
      } catch (e) {
        console.warn('图片压缩失败，使用原图上传:', e)
      }
    }

    const res = await uploadApi.uploadImage(
      uploadFileData,
      props.folder,
      (progressEvent) => {
        if (progressEvent.lengthComputable) {
          fileItem.progress = Math.round((progressEvent.loaded / progressEvent.total) * 100)
        }
      }
    )

    if (res?.data?.url) {
      fileItem.url = res.data.url
      fileItem.status = 'finished'
      fileItem.progress = 100
      emitChange()
      emit('success', fileItem)
    } else {
      throw new Error('上传失败，返回数据无效')
    }
  } catch (error) {
    fileItem.status = 'error'
    fileItem.error = error?.message || error || '上传失败'
    fileItem.progress = 0
    emit('error', { file: fileItem, error })
  }
}

function handleRemove(index) {
  const item = fileList.value[index]
  if (item?.preview) {
    URL.revokeObjectURL(item.preview)
  }
  fileList.value.splice(index, 1)
  emitChange()
}

function handleRetry(index) {
  const item = fileList.value[index]
  if (!item || item.status !== 'error') return
  item.retryCount = (item.retryCount || 0) + 1
  item.error = ''
  uploadFile(item)
}

function moveUp(index) {
  if (index <= 0) return
  const temp = fileList.value[index]
  fileList.value[index] = fileList.value[index - 1]
  fileList.value[index - 1] = temp
  emitChange()
}

function moveDown(index) {
  if (index >= fileList.value.length - 1) return
  const temp = fileList.value[index]
  fileList.value[index] = fileList.value[index + 1]
  fileList.value[index + 1] = temp
  emitChange()
}

function handleDragStart(e, index) {
  if (props.disabled) return
  dragIndex.value = index
  e.dataTransfer.effectAllowed = 'move'
  dragDom.value = e.target
  try {
    e.dataTransfer.setData('text/plain', index.toString())
  } catch (e) {}
}

function handleDragEnd() {
  dragIndex.value = null
  dragOverIndex.value = null
  dragDom.value = null
}

function handleDragOver(e, index) {
  e.preventDefault()
  if (dragIndex.value === null || dragIndex.value === index) return
  dragOverIndex.value = index
}

function handleDragLeave() {
  dragOverIndex.value = null
}

function handleDrop(e, index) {
  e.preventDefault()
  if (dragIndex.value === null || dragIndex.value === index) {
    dragIndex.value = null
    dragOverIndex.value = null
    return
  }

  const list = [...fileList.value]
  const [removed] = list.splice(dragIndex.value, 1)
  list.splice(index, 0, removed)
  fileList.value = list

  dragIndex.value = null
  dragOverIndex.value = null
  emitChange()
}

const isSingleMode = computed(() => props.maxCount === 1)

function emitChange() {
  const urls = fileList.value
    .filter(f => f.status === 'finished' && f.url)
    .map(f => f.url)
  
  if (isSingleMode.value) {
    emit('update:modelValue', urls[0] || '')
  } else {
    emit('update:modelValue', urls)
  }
  emit('change', { fileList: fileList.value, urls })
}

watch(
  () => props.modelValue,
  (newVal) => {
    if (fileList.value.length > 0) return
    
    let urls = []
    if (Array.isArray(newVal)) {
      urls = newVal
    } else if (typeof newVal === 'string' && newVal) {
      urls = [newVal]
    }
    
    if (urls.length > 0) {
      fileList.value = urls.map((url, index) => ({
        id: generateId(),
        name: `图片${index + 1}`,
        size: 0,
        status: 'finished',
        progress: 100,
        file: null,
        preview: '',
        url: url,
        error: '',
        retryCount: 0
      }))
    }
  },
  { immediate: true }
)

onBeforeUnmount(() => {
  fileList.value.forEach(item => {
    if (item.preview) {
      URL.revokeObjectURL(item.preview)
    }
  })
})
</script>

<template>
  <div class="image-uploader">
    <NGrid :cols="3" :x-gap="12" :y-gap="12">
      <NGridItem
        v-for="(item, index) in fileList"
        :key="item.id"
        class="image-uploader__item"
        :class="{
          'is-dragging': dragIndex === index,
          'is-drag-over': dragOverIndex === index && dragIndex !== index
        }"
        draggable="true"
        @dragstart="handleDragStart($event, index)"
        @dragend="handleDragEnd"
        @dragover="handleDragOver($event, index)"
        @dragleave="handleDragLeave"
        @drop="handleDrop($event, index)"
      >
        <div class="image-uploader__item-inner">
          <div class="image-uploader__image-wrapper">
            <NImage
              :src="getPreviewUrl(item)"
              object-fit="cover"
              width="100%"
              height="100%"
              class="image-uploader__image"
            />

            <div v-if="item.status === 'uploading'" class="image-uploader__overlay">
              <div class="image-uploader__progress-wrapper">
                <NProgress
                  type="circle"
                  :percentage="item.progress"
                  :show-indicator="false"
                  stroke-width="4"
                  color="#fff"
                  rail-color="rgba(255,255,255,0.3)"
                  style="width: 48px; height: 48px;"
                />
                <span class="image-uploader__progress-text">{{ item.progress }}%</span>
              </div>
            </div>

            <div v-if="item.status === 'error'" class="image-uploader__overlay is-error">
              <div class="image-uploader__error-info">
                <NIcon size="24" color="#E88A9A">
                  <Close />
                </NIcon>
                <span class="image-uploader__error-text">上传失败</span>
                <span class="image-uploader__error-detail">{{ item.error }}</span>
              </div>
            </div>

            <div v-if="item.status === 'finished'" class="image-uploader__actions">
              <NTooltip trigger="hover" content="上移">
                <NButton
                  size="small"
                  type="default"
                  quaternary
                  @click.stop="moveUp(index)"
                  :disabled="index === 0"
                >
                  <NIcon><ArrowUpOutline /></NIcon>
                </NButton>
              </NTooltip>
              <NTooltip trigger="hover" content="下移">
                <NButton
                  size="small"
                  type="default"
                  quaternary
                  @click.stop="moveDown(index)"
                  :disabled="index === fileList.length - 1"
                >
                  <NIcon><ArrowDownOutline /></NIcon>
                </NButton>
              </NTooltip>
              <NTooltip trigger="hover" content="删除">
                <NButton
                  size="small"
                  type="error"
                  quaternary
                  @click.stop="handleRemove(index)"
                >
                  <NIcon><TrashOutline /></NIcon>
                </NButton>
              </NTooltip>
            </div>
          </div>

          <div class="image-uploader__info">
            <span class="image-uploader__name" :title="item.name">{{ item.name }}</span>
            <span class="image-uploader__size">
              {{ item.compressedSize ? formatFileSize(item.compressedSize) : formatFileSize(item.size) }}
              <template v-if="item.compressedSize && item.originalSize > item.compressedSize">
                (已压缩 {{ Math.round((1 - item.compressedSize / item.originalSize) * 100) }}%)
              </template>
            </span>
          </div>

          <div v-if="item.status === 'error'" class="image-uploader__retry-bar">
            <NButton size="tiny" type="primary" block @click="handleRetry(index)">
              <NIcon><ReloadOutline /></NIcon>
              重试 ({{ item.retryCount || 0 }}/2)
            </NButton>
          </div>
        </div>
      </NGridItem>

      <NGridItem v-if="showAddButton" class="image-uploader__item is-add">
        <NUpload
          :show-file-list="false"
          :multiple="multiple"
          accept="image/jpeg,image/jpg,image/png,image/webp"
          :max="maxCount"
          :disabled="disabled"
          @before-upload="handleBeforeUpload"
          @change="handleChange"
        >
          <NUploadDragger class="image-uploader__add-btn">
            <div class="image-uploader__add-inner">
              <NIcon size="32" color="#999">
                <AddOutline />
              </NIcon>
              <span class="image-uploader__add-text">上传图片</span>
              <span class="image-uploader__add-hint">
                支持 JPG/PNG/WebP，单张≤5MB
              </span>
            </div>
          </NUploadDragger>
        </NUpload>
      </NGridItem>
    </NGrid>

    <div v-if="fileList.length > 0" class="image-uploader__footer">
      <span class="image-uploader__count">
        已选 {{ fileList.filter(f => f.status !== 'error').length }} / {{ maxCount }} 张
      </span>
      <span class="image-uploader__hint">拖拽图片可调整顺序</span>
    </div>
  </div>
</template>

<style scoped lang="scss">
.image-uploader {
  &__item {
    aspect-ratio: 1;
    position: relative;
    border-radius: 8px;
    overflow: hidden;
    background: #f5f5f5;
    transition: all 0.2s ease;

    &.is-dragging {
      opacity: 0.5;
      transform: scale(0.95);
    }

    &.is-drag-over {
      border: 2px dashed #18a058;
      background: rgba(24, 160, 88, 0.05);
    }

    &.is-add {
      cursor: pointer;

      &:hover {
        background: #f0f0f0;
      }
    }
  }

  &__item-inner {
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
  }

  &__image-wrapper {
    position: relative;
    flex: 1;
    min-height: 0;
    overflow: hidden;
  }

  &__image {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  &__overlay {
    position: absolute;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(0, 0, 0, 0.5);

    &.is-error {
      background: rgba(232, 138, 154, 0.8);
    }
  }

  &__progress-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
  }

  &__progress-text {
    color: #fff;
    font-size: 12px;
    font-weight: 500;
  }

  &__error-info {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
    color: #fff;
    padding: 0 8px;
  }

  &__error-text {
    font-size: 14px;
    font-weight: 500;
  }

  &__error-detail {
    font-size: 11px;
    opacity: 0.9;
    text-align: center;
    overflow: hidden;
    text-overflow: ellipsis;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
  }

  &__actions {
    position: absolute;
    top: 6px;
    right: 6px;
    display: flex;
    gap: 4px;
    opacity: 0;
    transition: opacity 0.2s ease;
    background: rgba(0, 0, 0, 0.4);
    border-radius: 6px;
    padding: 4px;
  }

  &__item:hover &__actions {
    opacity: 1;
  }

  &__info {
    padding: 8px 10px;
    background: #fff;
    border-top: 1px solid #eee;
  }

  &__name {
    display: block;
    font-size: 12px;
    color: #333;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    font-weight: 500;
  }

  &__size {
    display: block;
    font-size: 11px;
    color: #999;
    margin-top: 2px;
  }

  &__retry-bar {
    padding: 6px 8px;
    background: #fff;
    border-top: 1px solid #f0f0f0;
  }

  &__add-btn {
    width: 100%;
    height: 100%;
    padding: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 2px dashed #d0d0d0;
    border-radius: 8px;
    background: #fafafa;
    transition: all 0.2s ease;

    &:hover {
      border-color: #18a058;
      background: rgba(24, 160, 88, 0.02);
    }
  }

  &__add-inner {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 6px;
    color: #999;
  }

  &__add-text {
    font-size: 14px;
    font-weight: 500;
    color: #666;
  }

  &__add-hint {
    font-size: 11px;
    color: #bbb;
  }

  &__footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 12px;
    padding-top: 12px;
    border-top: 1px solid #f0f0f0;
  }

  &__count {
    font-size: 12px;
    color: #666;
  }

  &__hint {
    font-size: 12px;
    color: #999;
  }
}
</style>
