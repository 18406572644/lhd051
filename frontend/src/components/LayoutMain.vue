<script setup>
import { ref, computed, onMounted, h } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  NLayout, NLayoutSider, NLayoutHeader, NLayoutContent,
  NMenu, NAvatar, NIcon, NBadge, NDropdown, NSpace, NButton, NTooltip,
  NTag, useDialog, useMessage
} from 'naive-ui'
import {
  HomeOutline, Flower, Flask, FlowerOutline, Book, ColorPalette,
  Camera, BarChart, Heart, Star, LogOutOutline, PersonCircle,
  Sparkles
} from '@vicons/ionicons5'
import { useLoadingBar } from 'naive-ui'

const route = useRoute()
const router = useRouter()
const message = useMessage()
const dialog = useDialog()
const loadingBar = useLoadingBar()

const menuKey = computed(() => route.name)

const menuOptions = [
  { label: '首页概览', key: 'Home', icon: () => h(HomeOutline) },
  { label: '鲜花原料', key: 'Materials', icon: () => h(Flower) },
  { label: '脱水制作', key: 'Drying', icon: () => h(Flask) },
  { label: '标本陈列', key: 'Specimens', icon: () => h(FlowerOutline) },
  { label: '手法笔记', key: 'Notes', icon: () => h(Book) },
  { label: '设计方案', key: 'Plans', icon: () => h(ColorPalette) },
  { label: '实拍图库', key: 'Gallery', icon: () => h(Camera) },
  { label: '数据统计', key: 'Statistics', icon: () => h(BarChart) },
  { label: '分享广场', key: 'Share', icon: () => h(Heart) },
  { label: '我的收藏', key: 'Favorites', icon: () => h(Star) }
]

function handleMenuUpdate(key) {
  loadingBar.start()
  const routeMap = {
    Home: '/',
    Materials: '/materials',
    Drying: '/drying',
    Specimens: '/specimens',
    Notes: '/notes',
    Plans: '/plans',
    Gallery: '/gallery',
    Statistics: '/statistics',
    Share: '/share',
    Favorites: '/favorites'
  }
  const path = routeMap[key]
  if (path) {
    router.push(path).then(() => loadingBar.finish())
  }
}

const userOptions = [
  { label: '个人资料', key: 'profile', icon: () => h(PersonCircle) },
  { label: '退出登录', key: 'logout', icon: () => h(LogOutOutline) }
]

function handleUserSelect(key) {
  if (key === 'logout') {
    dialog.warning({
      title: '确认退出',
      content: '确定要退出登录吗？',
      positiveText: '确定',
      negativeText: '取消',
      onPositiveClick: () => {
        message.info('已退出')
      }
    })
  } else {
    message.info('个人资料页面开发中')
  }
}

const currentTime = ref('')
function updateTime() {
  const now = new Date()
  const opts = { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' }
  currentTime.value = now.toLocaleDateString('zh-CN', opts)
}

onMounted(updateTime)
setInterval(updateTime, 60000)
</script>

<template>
  <NLayout style="min-height: 100vh">
    <NLayoutHeader bordered style="height: 72px; background: #FFFDF6; display: flex; align-items: center; justify-content: space-between; padding: 0 28px; border-bottom: 1px solid rgba(240,230,222,0.8);">
      <div style="display: flex; align-items: center; gap: 14px;">
        <div style="width: 42px; height: 42px; border-radius: 12px; background: linear-gradient(135deg, #E8B4B8, #F5E6A3); display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 14px rgba(212,165,165,0.3);">
          <n-icon size="24" color="#FFFDF6"><Sparkles /></n-icon>
        </div>
        <div>
          <div style="font-size: 20px; font-weight: 700; color: #5C4A4A; letter-spacing: 1px;">花语集</div>
          <div style="font-size: 12px; color: #B8A8A6; margin-top: 2px;">Dried Flower & Specimen Collection</div>
        </div>
      </div>

      <div style="display: flex; align-items: center; gap: 16px;">
        <NTag round type="success" size="small" style="background: rgba(168,195,160,0.2); border: none;">
          <span style="display: inline-block; width: 6px; height: 6px; background: #8BA888; border-radius: 50%; margin-right: 6px;"></span>
          系统正常
        </NTag>
        <span style="font-size: 13px; color: #8B7D7B;">{{ currentTime }}</span>
        <NDropdown :options="userOptions" trigger="click" @select="handleUserSelect">
          <div style="display: flex; align-items: center; gap: 10px; padding: 6px 12px; border-radius: 10px; background: #FAF6EE; cursor: pointer;">
            <NAvatar round size="28" style="background: linear-gradient(135deg, #E8B4B8, #F5E6A3);">
              <n-icon size="18" color="#FFFDF6"><PersonCircle /></n-icon>
            </NAvatar>
            <span style="font-size: 13px; color: #5C4A4A;">花艺师</span>
          </div>
        </NDropdown>
      </div>
    </NLayoutHeader>

    <NLayout has-sider>
      <NLayoutSider bordered width="232" :collapsed-width="64" style="background: #FAF6EE; border-right: 1px solid rgba(240,230,222,0.8); padding: 20px 12px;">
        <NMenu
          :value="menuKey"
          :options="menuOptions"
          @update:value="handleMenuUpdate"
          :expanded-keys="[]"
          :collapsed-icon-size="22"
          :indent="18"
          style="background: transparent; border: none;"
        />
        <div style="margin-top: 30px; padding: 16px; background: linear-gradient(135deg, rgba(232,180,184,0.12), rgba(245,230,163,0.18)); border-radius: 14px; position: relative; overflow: hidden;">
          <div style="position: absolute; top: -10px; right: -10px; font-size: 60px; opacity: 0.08;">🌸</div>
          <div style="font-size: 13px; font-weight: 600; color: #C08990; margin-bottom: 6px;">每日花语</div>
          <div style="font-size: 11px; color: #8B7D7B; line-height: 1.7;">
            花开花落终有时，<br/>留住最美的那瞬间。
          </div>
        </div>
      </NLayoutSider>

      <NLayoutContent :native-scrollbar="false">
        <div style="padding: 24px 28px;">
          <router-view v-slot="{ Component }">
            <transition name="fade" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </div>
      </NLayoutContent>
    </NLayout>
  </NLayout>
</template>

<style lang="scss" scoped>
</style>
