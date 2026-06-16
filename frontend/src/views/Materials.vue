<script setup>
import { ref, onMounted, computed, h, nextTick } from 'vue'
import {
  NCard, NGrid, NGridItem, NTag, NIcon, NSpace, NButton, NInput, NSelect,
  NSwitch, NDataTable, NPagination, NModal, NForm, NFormItem, NInputNumber,
  NDatePicker, NUpload, NPopconfirm, NImage, useMessage, useDialog,
  NFormItemGi
} from 'naive-ui'
import {
  Flower, FlowerOutline, Add, Search, Refresh, CreateOutline, TrashOutline,
  Ban, CheckmarkCircle, CloseCircle, CloudUploadOutline, Sparkles, Leaf
} from '@vicons/ionicons5'
import { materialsApi, uploadApi } from '@/api'
import dayjs from 'dayjs'

const message = useMessage()
const dialog = useDialog()
const formRef = ref(null)
console.log('=== Materials.vue v2 LOADED ===', Date.now())

const loading = ref(false)
const modalLoading = ref(false)
const showModal = ref(false)
const isEdit = ref(false)
const editId = ref(null)
const uploadLoading = ref(false)

const filters = ref({
  keyword: null,
  category: null,
  color: null,
  is_available: true
})

const pagination = ref({
  page: 1,
  pageSize: 10,
  total: 0
})

const dataList = ref([])
const categoryOptions = ref([])
const colorOptions = ref([])

const summary = ref({
  total_types: 0,
  total_quantity: 0,
  active_types: 0
})

const formValues = ref({
  name: '',
  scientific_name: '',
  category: null,
  color: '',
  origin: '',
  quantity: 0,
  unit: '',
  purchase_date: null,
  supplier: '',
  freshness: null,
  storage_method: '',
  image_url: '',
  remark: ''
})

const formRules = {
  name: {
    required: true,
    message: '请输入原料名称',
    trigger: 'blur'
  }
}

const freshnessOptions = [
  { label: 'A 级 - 极佳', value: 'A' },
  { label: 'B 级 - 良好', value: 'B' },
  { label: 'C 级 - 一般', value: 'C' }
]

const columns = [
  {
    title: '缩略图',
    key: 'image_url',
    width: 80,
    render: (row) => h(
      'div',
      { class: 'thumb-wrap' },
      row.image_url
        ? h(NImage, {
            src: row.image_url,
            width: 44,
            height: 44,
            objectFit: 'cover',
            round: true,
            fallbackSrc: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDQiIGhlaWdodD0iNDQiIHZpZXdCb3g9IjAgMCA0NCA0NCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iNDQiIGhlaWdodD0iNDQiIHJ4PSIyMiIgZmlsbD0iI0ZBRjZFRSIvPjx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBkb21pbmFudC1iYXNlbGluZT0ibWlkZGxlIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmaWxsPSIjRDRCOEIwIiBmb250LXNpemU9IjE4Ij7wn5SzPC90ZXh0Pjwvc3ZnPg=='
          })
        : h('div', { class: 'thumb-placeholder' },
            h(NIcon, { size: 20, color: '#D4B8B0' }, { default: () => h(FlowerOutline) })
          )
    )
  },
  {
    title: '名称',
    key: 'name',
    minWidth: 140,
    render: (row) => h('div', { class: 'cell-name' }, [
      h('div', { class: 'name-main' }, row.name),
      row.scientific_name && h('div', { class: 'name-sci' }, row.scientific_name)
    ])
  },
  {
    title: '分类',
    key: 'category',
    width: 110,
    render: (row) => row.category && h(
      NTag,
      {
        round: true,
        size: 'small',
        style: 'background: rgba(212,165,165,0.15); color: #C08990; border: none;'
      },
      { default: () => row.category }
    )
  },
  {
    title: '花色',
    key: 'color',
    width: 110,
    render: (row) => row.color && h(
      NTag,
      {
        round: true,
        size: 'small',
        style: 'background: rgba(245,230,163,0.3); color: #B8962F; border: none;'
      },
      { default: () => row.color }
    )
  },
  {
    title: '数量',
    key: 'quantity',
    width: 110,
    render: (row) => h('div', { class: 'cell-quantity' }, [
      h('span', { class: 'qty-num' }, row.quantity ?? 0),
      row.unit && h('span', { class: 'qty-unit' }, ` ${row.unit}`)
    ])
  },
  {
    title: '新鲜度',
    key: 'freshness',
    width: 100,
    render: (row) => {
      const map = {
        'A': { bg: 'rgba(168,195,160,0.2)', text: '#8BA888', label: 'A 级' },
        'B': { bg: 'rgba(245,230,163,0.3)', text: '#B8962F', label: 'B 级' },
        'C': { bg: 'rgba(212,165,165,0.18)', text: '#C08990', label: 'C 级' }
      }
      const cfg = map[row.freshness]
      return cfg ? h(
        NTag,
        { round: true, size: 'small', style: `background: ${cfg.bg}; color: ${cfg.text}; border: none;` },
        { default: () => cfg.label }
      ) : h('span', { style: 'color: #B8A8A6; font-size: 12px;' }, '-')
    }
  },
  {
    title: '采购日期',
    key: 'purchase_date',
    width: 120,
    render: (row) => row.purchase_date
      ? h('span', { class: 'cell-date' }, dayjs(row.purchase_date).format('YYYY-MM-DD'))
      : h('span', { style: 'color: #B8A8A6; font-size: 12px;' }, '-')
  },
  {
    title: '状态',
    key: 'is_available',
    width: 100,
    render: (row) => row.is_available
      ? h(NTag, {
          round: true,
          size: 'small',
          style: 'background: rgba(168,195,160,0.2); color: #8BA888; border: none;'
        }, {
          default: () => [
            h(NIcon, { size: 12, style: 'margin-right: 4px;' }, { default: () => h(CheckmarkCircle) }),
            '可用'
          ]
        })
      : h(NTag, {
          round: true,
          size: 'small',
          style: 'background: rgba(184,168,166,0.2); color: #8B7D7B; border: none;'
        }, {
          default: () => [
            h(NIcon, { size: 12, style: 'margin-right: 4px;' }, { default: () => h(CloseCircle) }),
            '禁用'
          ]
        })
  },
  {
    title: '操作',
    key: 'actions',
    width: 140,
    fixed: 'right',
    render: (row) => h(NSpace, { size: 'small' }, {
      default: () => [
        h(NButton, {
          size: 'small',
          type: 'primary',
          quaternary: true,
          onClick: () => openEdit(row)
        }, {
          default: () => [
            h(NIcon, { size: 14 }, { default: () => h(CreateOutline) }),
            ' 编辑'
          ]
        }),
        h(NPopconfirm, {
          positiveText: '删除',
          negativeText: '取消',
          onPositiveClick: () => handleDelete(row.id)
        }, {
          trigger: () => h(NButton, {
            size: 'small',
            type: 'error',
            quaternary: true
          }, {
            default: () => [
              h(NIcon, { size: 14 }, { default: () => h(TrashOutline) }),
              ' 删除'
            ]
          }),
          default: () => `确定要删除原料「${row.name}」吗？`
        })
      ]
    })
  }
]

const statCards = computed(() => [
  {
    title: '总种类数',
    key: 'total_types',
    icon: Flower,
    gradient: 'linear-gradient(135deg, rgba(212,165,165,0.15), rgba(245,230,163,0.2))',
    accent: '#D4A5A5'
  },
  {
    title: '总数量',
    key: 'total_quantity',
    icon: Sparkles,
    gradient: 'linear-gradient(135deg, rgba(245,230,163,0.2), rgba(168,195,160,0.15))',
    accent: '#F5C86B'
  },
  {
    title: '可用种类数',
    key: 'active_types',
    icon: Leaf,
    gradient: 'linear-gradient(135deg, rgba(168,195,160,0.18), rgba(212,165,165,0.15))',
    accent: '#A8C3A0'
  }
])

async function loadOptions() {
  try {
    const [catRes, colorRes] = await Promise.all([
      materialsApi.categories(),
      materialsApi.colors()
    ])
    if (catRes?.data) {
      const data = Array.isArray(catRes.data) ? catRes.data : (catRes.data.categories || catRes.data.list || [])
      categoryOptions.value = data.map(item => ({
        label: item.name || item.label || item,
        value: item.value ?? item.id ?? item.name ?? item
      }))
    }
    if (colorRes?.data) {
      const data = Array.isArray(colorRes.data) ? colorRes.data : (colorRes.data.colors || colorRes.data.list || [])
      colorOptions.value = data.map(item => ({
        label: item.name || item.label || item,
        value: item.value ?? item.id ?? item.name ?? item
      }))
    }
  } catch (e) {
    console.warn('加载选项失败', e)
  }
}

async function loadData() {
  loading.value = true
  try {
    const params = {
      page: pagination.value.page,
      page_size: pagination.value.pageSize,
      keyword: filters.value.keyword || undefined,
      category: filters.value.category || undefined,
      color: filters.value.color || undefined,
      is_active: filters.value.is_active
    }
    const res = await materialsApi.list(params)
    if (res?.data) {
      if (res.data.items !== undefined) {
        dataList.value = res.data.items
        pagination.value.total = res.data.total ?? res.data.items.length
        summary.value = {
          total_types: res.data.total_types ?? res.data.total ?? 0,
          total_quantity: res.data.total_quantity ?? 0,
          active_types: res.data.active_types ?? 0
        }
      } else {
        dataList.value = Array.isArray(res.data) ? res.data : []
        pagination.value.total = dataList.value.length
        summary.value = {
          total_types: dataList.value.length,
          total_quantity: dataList.value.reduce((sum, i) => sum + (Number(i.quantity) || 0), 0),
          active_types: dataList.value.filter(i => i.is_active).length
        }
      }
    }
  } catch (e) {
    message.error('加载原料列表失败')
  } finally {
    loading.value = false
  }
}

function resetFilters() {
  filters.value = {
    keyword: null,
    category: null,
    color: null,
    is_available: true
  }
  pagination.value.page = 1
  loadData()
}

function onSearch() {
  pagination.value.page = 1
  loadData()
}

function handlePageChange(page) {
  pagination.value.page = page
  loadData()
}

function handlePageSizeChange(pageSize) {
  pagination.value.pageSize = pageSize
  pagination.value.page = 1
  loadData()
}

function openCreate() {
  isEdit.value = false
  editId.value = null
  formValues.value = {
    name: '',
    scientific_name: '',
    category: null,
    color: '',
    origin: '',
    quantity: 0,
    unit: '',
    purchase_date: null,
    supplier: '',
    freshness: null,
    storage_method: '',
    image_url: '',
    remark: ''
  }
  showModal.value = true
  nextTick(() => {
    formRef.value?.restoreValidation()
  })
}

async function openEdit(row) {
  isEdit.value = true
  editId.value = row.id
  modalLoading.value = true
  showModal.value = true
  try {
    const res = await materialsApi.get(row.id)
    if (res?.data) {
      const d = res.data
      formValues.value = {
        name: d.name ?? '',
        scientific_name: d.scientific_name ?? '',
        category: d.category ?? null,
        color: d.color ?? '',
        origin: d.origin ?? '',
        quantity: d.quantity ?? 0,
        unit: d.unit ?? '',
        purchase_date: d.purchase_date ? dayjs(d.purchase_date).valueOf() : null,
        supplier: d.supplier ?? '',
        freshness: d.freshness ?? null,
        storage_method: d.storage_method ?? '',
        image_url: d.image_url ?? '',
        remark: d.remark ?? ''
      }
    }
  } catch (e) {
    message.error('加载详情失败')
    showModal.value = false
  } finally {
    modalLoading.value = false
    nextTick(() => {
      formRef.value?.restoreValidation()
    })
  }
}

async function handleSubmit() {
  try {
    await formRef.value?.validate()
  } catch (e) {
    message.warning('请完善表单内容')
    return
  }
  modalLoading.value = true
  try {
    const data = {
      ...formValues.value,
      fresh_level: formValues.value.freshness ?? formValues.value.fresh_level,
      purchase_date: formValues.value.purchase_date
        ? dayjs(formValues.value.purchase_date).format('YYYY-MM-DD')
        : null
    }
    delete data.freshness
    if (isEdit.value) {
      await materialsApi.update(editId.value, data)
      message.success('更新成功')
    } else {
      await materialsApi.create(data)
      message.success('创建成功')
    }
    showModal.value = false
    loadData()
    loadOptions()
  } catch (e) {
    message.error(isEdit.value ? '更新失败' : '创建失败')
  } finally {
    modalLoading.value = false
  }
}

async function handleDelete(id) {
  try {
    await materialsApi.delete(id)
    message.success('删除成功')
    loadData()
  } catch (e) {
    message.error('删除失败')
  }
}

async function handleUpload({ file, onFinish, onError }) {
  uploadLoading.value = true
  try {
    const res = await uploadApi.uploadImage(file.file, 'materials')
    if (res?.data?.url || res?.data?.file_url || res?.data?.path) {
      formValues.value.image_url = res.data.url || res.data.file_url || res.data.path
      message.success('上传成功')
      onFinish()
    } else {
      throw new Error('上传失败')
    }
  } catch (e) {
    message.error('上传失败')
    onError()
  } finally {
    uploadLoading.value = false
  }
}

function onUpdateValue(val) {
  formValues.value.image_url = val
}

onMounted(() => {
  loadOptions()
  loadData()
})
</script>

<template>
  <div class="materials-wrapper">
    <div class="section-header">
      <div>
        <h2 class="page-title">
          <n-icon size="26" color="#D4A5A5"><Flower /></n-icon>
          原料管理
        </h2>
        <p class="page-subtitle">精心挑选每一朵花，珍藏最本真的自然之美</p>
      </div>
      <div class="header-right">
        <span class="flower-icon flower-1">🌸</span>
        <n-button type="primary" size="large" @click="openCreate" class="btn-add">
          <template #icon>
            <n-icon :component="Add" />
          </template>
          新增原料
        </n-button>
        <span class="flower-icon flower-2">🌿</span>
      </div>
    </div>

    <div class="stats-section">
      <n-grid :cols="3" responsive="screen" :x-gap="18" :y-gap="18">
        <n-grid-item v-for="card in statCards" :key="card.key" span="3 s:3 m:3 l:1">
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
                  <span class="stat-num">{{ summary[card.key] || 0 }}</span>
                </div>
              </div>
            </div>
          </div>
        </n-grid-item>
      </n-grid>
    </div>

    <n-card class="filter-card" size="large" :bordered="false">
      <div class="filter-card-decor">
        <span class="decor-flower">❁</span>
      </div>
      <n-grid :cols="5" responsive="screen" :x-gap="16" :y-gap="14" style="align-items: flex-end;">
        <n-grid-item span="5 s:5 m:5 l:1">
          <n-form-item label="关键词" label-placement="left" label-align="left" class="form-inline-item">
            <n-input
              v-model:value="filters.keyword"
              placeholder="搜索名称/产地/供应商"
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
        <n-grid-item span="5 s:5 m:5 l:1">
          <n-form-item label="分类" label-placement="left" label-align="left" class="form-inline-item">
            <n-select
              v-model:value="filters.category"
              :options="categoryOptions"
              placeholder="全部分类"
              clearable
              filterable
            />
          </n-form-item>
        </n-grid-item>
        <n-grid-item span="5 s:5 m:5 l:1">
          <n-form-item label="花色" label-placement="left" label-align="left" class="form-inline-item">
            <n-select
              v-model:value="filters.color"
              :options="colorOptions"
              placeholder="全部花色"
              clearable
              filterable
            />
          </n-form-item>
        </n-grid-item>
        <n-grid-item span="5 s:5 m:5 l:1">
          <n-form-item label="状态" label-placement="left" label-align="left" class="form-inline-item">
            <div class="switch-wrap">
              <n-switch
                v-model:value="filters.is_available"
                round
                size="medium"
                :checked-value="true"
                :unchecked-value="false"
                checked-color="#A8C3A0"
              />
              <span class="switch-label" :class="{ active: filters.is_available }">
                {{ filters.is_available ? '仅显示可用' : '显示全部' }}
              </span>
            </div>
          </n-form-item>
        </n-grid-item>
        <n-grid-item span="5 s:5 m:5 l:1">
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

    <n-card class="table-card" size="large" :bordered="false">
      <div class="table-card-decor">
        <span class="decor-flower decor-left">✿</span>
        <span class="decor-flower decor-right">❀</span>
      </div>
      <n-data-table
        :columns="columns"
        :data="dataList"
        :loading="loading"
        :row-key="row => row.id"
        :pagination="false"
        :bordered="false"
        size="medium"
        class="materials-table"
        striped
      />
      <div class="pagination-wrap">
        <n-pagination
          v-model:page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :item-count="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          show-size-picker
          :show-quick-jump="true"
          @update:page="handlePageChange"
          @update:page-size="handlePageSizeChange"
        />
      </div>
    </n-card>

    <n-modal
      v-model:show="showModal"
      preset="card"
      :title="isEdit ? '编辑原料' : '新增原料'"
      :style="{ width: '680px' }"
      :mask-closable="false"
      class="materials-modal"
      :scrollable="true"
    >
      <n-form
        ref="formRef"
        :model="formValues"
        :rules="formRules"
        label-placement="left"
        label-align="left"
        require-mark-placement="right-hanging"
        size="medium"
        style="--n-label-width: 90px;"
      >
        <n-grid :cols="2" responsive="screen" :x-gap="16" :y-gap="4">
          <n-grid-item span="2 s:2 m:1">
            <n-form-item label="名称" path="name">
              <n-input v-model:value="formValues.name" placeholder="请输入原料名称" :input-props="{ autocomplete: 'off' }" />
            </n-form-item>
          </n-grid-item>
          <n-grid-item span="2 s:2 m:1">
            <n-form-item label="学名">
              <n-input v-model:value="formValues.scientific_name" placeholder="拉丁学名" :input-props="{ autocomplete: 'off' }" />
            </n-form-item>
          </n-grid-item>
          <n-grid-item span="2 s:2 m:1">
            <n-form-item label="分类">
              <n-select
                v-model:value="formValues.category"
                :options="categoryOptions"
                placeholder="请选择分类"
                clearable
                filterable
              />
            </n-form-item>
          </n-grid-item>
          <n-grid-item span="2 s:2 m:1">
            <n-form-item label="花色">
              <n-select
                v-model:value="formValues.color"
                :options="colorOptions"
                placeholder="请选择花色"
                clearable
                filterable
                allow-input
              />
            </n-form-item>
          </n-grid-item>
          <n-grid-item span="2 s:2 m:1">
            <n-form-item label="产地">
              <n-input v-model:value="formValues.origin" placeholder="产地来源" :input-props="{ autocomplete: 'off' }" />
            </n-form-item>
          </n-grid-item>
          <n-grid-item span="2 s:2 m:1">
            <n-form-item label="供应商">
              <n-input v-model:value="formValues.supplier" placeholder="供应商名称" :input-props="{ autocomplete: 'off' }" />
            </n-form-item>
          </n-grid-item>
          <n-grid-item span="2 s:2 m:1">
            <n-form-item label="数量">
              <n-input-number
                v-model:value="formValues.quantity"
                :min="0"
                :precision="0"
                placeholder="0"
                style="width: 100%;"
              />
            </n-form-item>
          </n-grid-item>
          <n-grid-item span="2 s:2 m:1">
            <n-form-item label="单位">
              <n-input v-model:value="formValues.unit" placeholder="如：g、朵、枝" :input-props="{ autocomplete: 'off' }" />
            </n-form-item>
          </n-grid-item>
          <n-grid-item span="2 s:2 m:1">
            <n-form-item label="采购日期">
              <n-date-picker
                v-model:value="formValues.purchase_date"
                type="date"
                value-format="timestamp"
                placeholder="选择日期"
                clearable
                style="width: 100%;"
              />
            </n-form-item>
          </n-grid-item>
          <n-grid-item span="2 s:2 m:1">
            <n-form-item label="新鲜度">
              <n-select
                v-model:value="formValues.freshness"
                :options="freshnessOptions"
                placeholder="选择新鲜度等级"
                clearable
              />
            </n-form-item>
          </n-grid-item>
          <n-grid-item span="2">
            <n-form-item label="储存方式" style="--n-label-width: 90px;">
              <n-input
                v-model:value="formValues.storage_method"
                type="textarea"
                placeholder="详细描述储存条件和方法"
                :autosize="{ minRows: 2, maxRows: 4 }"
              />
            </n-form-item>
          </n-grid-item>
          <n-grid-item span="2">
            <n-form-item label="图片" style="--n-label-width: 90px;">
              <div class="upload-wrapper">
                <n-upload
                  :show-file-list="false"
                  :custom-request="handleUpload"
                  accept="image/*"
                  :disabled="uploadLoading"
                  class="upload-btn"
                >
                  <div class="upload-trigger" :class="{ hasImage: formValues.image_url }">
                    <img v-if="formValues.image_url" :src="formValues.image_url" class="upload-preview" />
                    <div v-else class="upload-placeholder">
                      <n-icon size="28" color="#D4B8B0"><CloudUploadOutline /></n-icon>
                      <span class="upload-text">{{ uploadLoading ? '上传中...' : '点击上传图片' }}</span>
                      <span class="upload-hint">支持 JPG、PNG 格式</span>
                    </div>
                  </div>
                </n-upload>
                <n-button
                  v-if="formValues.image_url"
                  text
                  size="tiny"
                  type="error"
                  style="margin-top: 8px;"
                  @click="formValues.image_url = ''"
                >
                  <template #icon>
                    <n-icon :component="Ban" size="12" />
                  </template>
                  移除图片
                </n-button>
              </div>
            </n-form-item>
          </n-grid-item>
          <n-grid-item span="2">
            <n-form-item label="备注" style="--n-label-width: 90px;">
              <n-input
                v-model:value="formValues.remark"
                type="textarea"
                placeholder="其他补充信息..."
                :autosize="{ minRows: 2, maxRows: 4 }"
              />
            </n-form-item>
          </n-grid-item>
        </n-grid>
      </n-form>
      <template #footer>
        <n-space justify="end">
          <n-button round :disabled="modalLoading" @click="showModal = false">取消</n-button>
          <n-button type="primary" round :loading="modalLoading" @click="handleSubmit">
            {{ isEdit ? '保存修改' : '确认创建' }}
          </n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<style lang="scss" scoped>
.materials-wrapper {
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

  &.flower-1 {
    animation-delay: 0s;
  }
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

.stats-section {
  margin-bottom: 22px;
}

.stat-card {
  position: relative;
  border-radius: 16px;
  padding: 20px;
  border: 1px solid rgba(240, 230, 222, 0.8);
  overflow: hidden;
  transition: all 0.3s ease;
  box-shadow: 0 4px 20px rgba(212, 165, 165, 0.1);
  min-height: 108px;

  &:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 32px rgba(212, 165, 165, 0.2);
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
  font-size: 50px;
  opacity: 0.06;
  color: #C08990;

  &.bg-flower-1 {
    top: -8px;
    right: -4px;
    transform: rotate(25deg);
  }
  &.bg-flower-2 {
    bottom: -12px;
    left: -6px;
    transform: rotate(-15deg);
    font-size: 40px;
  }
}

.stat-card-inner {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  gap: 14px;
}

.stat-icon-wrap {
  width: 46px;
  height: 46px;
  border-radius: 13px;
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
  margin-bottom: 5px;
  font-weight: 500;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  line-height: 1.1;
  font-family: 'Segoe UI', -apple-system, sans-serif;
  letter-spacing: -0.5px;
}

.filter-card,
.table-card {
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
    background: linear-gradient(180deg, #D4A5A5, #F5E6A3);
    border-radius: 16px 0 0 16px;
    opacity: 0.5;
    z-index: 1;
  }
}

.filter-card-decor,
.table-card-decor {
  position: absolute;
  top: 0;
  right: 0;
  pointer-events: none;
  overflow: hidden;
  z-index: 0;
}

.decor-flower {
  font-size: 56px;
  opacity: 0.05;
  color: #D4A5A5;

  &.decor-left {
    position: absolute;
    top: -10px;
    left: -8px;
    font-size: 48px;
    color: #F5E6A3;
  }
  &.decor-right {
    position: absolute;
    bottom: -10px;
    right: -6px;
    transform: rotate(30deg);
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

.switch-wrap {
  display: flex;
  align-items: center;
  gap: 10px;
  min-height: 34px;
}

.switch-label {
  font-size: 13px;
  color: #B8A8A6;
  transition: all 0.25s ease;

  &.active {
    color: #8BA888;
    font-weight: 500;
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

.table-card :deep(.n-card__content) {
  position: relative;
  z-index: 1;
  padding: 8px 16px 16px;
}

.materials-table {
  background: transparent;

  :deep(.n-data-table-th) {
    background: linear-gradient(180deg, rgba(255, 253, 246, 1), rgba(250, 246, 238, 0.95)) !important;
    color: #5C4A4A !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    border-bottom: 2px solid rgba(240, 230, 222, 0.8) !important;
  }

  :deep(.n-data-table-td) {
    border-bottom: 1px solid rgba(240, 230, 222, 0.5) !important;
    font-size: 13px;
    color: #5C4A4A;
  }

  :deep(.n-data-table-tr:hover .n-data-table-td) {
    background: rgba(250, 246, 238, 0.7) !important;
  }

  :deep(.n-data-table .n-data-table-td) {
    padding-top: 14px;
    padding-bottom: 14px;
  }
}

.thumb-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
}

.thumb-placeholder {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: linear-gradient(135deg, #FAF6EE, #F5EEE8);
  display: flex;
  align-items: center;
  justify-content: center;
}

.cell-name {
  min-width: 0;
}

.name-main {
  font-size: 14px;
  font-weight: 600;
  color: #5C4A4A;
  line-height: 1.4;
}

.name-sci {
  font-size: 11px;
  color: #B8A8A6;
  font-style: italic;
  margin-top: 3px;
}

.cell-quantity {
  display: flex;
  align-items: baseline;
}

.qty-num {
  font-size: 18px;
  font-weight: 700;
  color: #C08990;
  font-family: 'Segoe UI', sans-serif;
}

.qty-unit {
  font-size: 12px;
  color: #8B7D7B;
}

.cell-date {
  font-size: 13px;
  color: #8B7D7B;
  font-family: 'Segoe UI', sans-serif;
}

.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  padding-top: 18px;
  margin-top: 4px;
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

.materials-modal {
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
      content: '🌸';
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

.modal-flower-1,
.modal-flower-2 {
  position: absolute;
  font-size: 70px;
  opacity: 0.04;
  color: #D4A5A5;
}

.modal-flower-1 {
  top: 30px;
  right: -10px;
  transform: rotate(15deg);
}

.modal-flower-2 {
  bottom: -20px;
  left: -15px;
  font-size: 90px;
  color: #F5E6A3;
  transform: rotate(-25deg);
}

.upload-wrapper {
  width: 100%;
}

.upload-trigger {
  width: 100%;
  min-height: 130px;
  border: 2px dashed rgba(212, 165, 165, 0.35);
  border-radius: 14px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  background: linear-gradient(135deg, rgba(250, 246, 238, 0.8), rgba(255, 253, 246, 1));

  &:hover {
    border-color: rgba(212, 165, 165, 0.6);
    background: linear-gradient(135deg, rgba(250, 246, 238, 1), rgba(255, 248, 238, 1));

    .upload-text {
      color: #C08990;
    }
  }

  &.hasImage {
    border-style: solid;
    border-color: rgba(212, 165, 165, 0.2);
    min-height: 160px;
  }
}

.upload-placeholder {
  width: 100%;
  min-height: 130px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 20px;
}

.upload-text {
  font-size: 13px;
  color: #8B7D7B;
  font-weight: 500;
  transition: color 0.25s ease;
}

.upload-hint {
  font-size: 11px;
  color: #B8A8A6;
}

.upload-preview {
  width: 100%;
  height: 160px;
  object-fit: contain;
  background: rgba(250, 246, 238, 0.6);
  display: block;
}

.upload-btn {
  width: 100%;
}
</style>
