<script setup>
import { NConfigProvider, NMessageProvider, NDialogProvider, NNotificationProvider, NLoadingBarProvider } from 'naive-ui'
import { computed } from 'vue'
import LayoutMain from '@/components/LayoutMain.vue'

const themeOverrides = computed(() => ({
  common: {
    primaryColor: '#D4A5A5',
    primaryColorHover: '#E8B4B8',
    primaryColorPressed: '#C08990',
    primaryColorSuppl: '#D4A5A5',
    infoColor: '#A8C3A0',
    infoColorHover: '#B8D3B0',
    infoColorPressed: '#8BA888',
    warningColor: '#F5E6A3',
    warningColorHover: '#FFF5D4',
    warningColorPressed: '#E6D793',
    successColor: '#8BA888',
    successColorHover: '#A8C3A0',
    errorColor: '#E8868E',
    borderRadius: '12px',
    borderRadiusSmall: '8px',
    textColorBase: '#5C4A4A',
    textColor1: '#5C4A4A',
    textColor2: '#8B7D7B',
    textColor3: '#B8A8A6',
    borderColor: '#F0E6DE',
    dividerColor: '#F5ECE4',
    bodyColor: '#FFFDF6',
    cardColor: '#FFFDF6',
    modalColor: '#FFFDF6'
  },
  Button: {
    colorPrimary: '#D4A5A5',
    colorHoverPrimary: '#E8B4B8',
    colorPressedPrimary: '#C08990',
    colorFocusPrimary: '#E8B4B8',
    colorInfo: '#A8C3A0',
    colorHoverInfo: '#B8D3B0',
    colorWarning: '#F5E6A3',
    colorSuccess: '#8BA888',
    textColorTextPrimary: '#D4A5A5',
    textColorHoverTextPrimary: '#E8B4B8',
    textColorPressedTextPrimary: '#C08990',
    textColorPrimary: '#FFFDF6',
    textColorWarning: '#5C4A4A',
    borderRadius: '10px',
    paddingSmall: '6px 14px',
    paddingMedium: '8px 20px',
    paddingLarge: '10px 24px'
  },
  Card: {
    color: '#FFFDF6',
    colorEmbedded: '#FAF6EE',
    borderRadius: '16px',
    padding: '20px'
  },
  Input: {
    color: '#FFFDF6',
    colorFocus: '#FFFFFF',
    colorDisabled: '#F5ECE4',
    border: '1px solid #F0E6DE',
    borderHover: '1px solid #E8B4B8',
    borderFocus: '1px solid #D4A5A5',
    borderRadius: '10px'
  },
  Select: {
    color: '#FFFDF6',
    colorFocus: '#FFFFFF',
    border: '1px solid #F0E6DE',
    borderHover: '1px solid #E8B4B8',
    borderFocus: '1px solid #D4A5A5',
    borderRadius: '10px'
  },
  DatePicker: {
    color: '#FFFDF6',
    border: '1px solid #F0E6DE',
    borderHover: '1px solid #E8B4B8',
    borderRadius: '10px'
  },
  Table: {
    tdColor: '#FFFDF6',
    thColor: '#FAF6EE',
    thTextColor: '#5C4A4A',
    tdTextColor: '#5C4A4A',
    borderRadius: '12px',
    borderColor: '#F5ECE4'
  },
  Tabs: {
    tabTextColor: '#8B7D7B',
    tabTextColorActive: '#D4A5A5',
    tabTextColorHover: '#E8B4B8',
    barColor: '#D4A5A5',
    tabBorderColor: '#F0E6DE'
  },
  Menu: {
    itemColor: 'transparent',
    itemColorActive: 'rgba(232, 180, 184, 0.15)',
    itemColorActiveHover: 'rgba(232, 180, 184, 0.2)',
    itemColorHover: 'rgba(232, 180, 184, 0.08)',
    itemTextColor: '#8B7D7B',
    itemTextColorHover: '#D4A5A5',
    itemTextColorActive: '#D4A5A5',
    borderRadius: '10px',
    groupTextColor: '#B8A8A6'
  },
  Tag: {
    borderRadius: '20px',
    padding: '3px 12px'
  },
  Modal: {
    color: '#FFFDF6',
    borderRadius: '16px',
    padding: '24px'
  },
  Drawer: {
    color: '#FFFDF6',
    borderRadius: '16px 0 0 16px'
  },
  Pagination: {
    itemTextColor: '#8B7D7B',
    itemTextColorActive: '#FFFDF6',
    itemColorActive: '#D4A5A5',
    itemColorHover: 'rgba(232, 180, 184, 0.15)',
    borderRadius: '10px'
  },
  Form: {
    labelTextColor: '#5C4A4A',
    asteriskColor: '#E8868E',
    feedbackTextColorError: '#E8868E'
  },
  DataTable: {
    thColor: '#FAF6EE',
    tdColor: '#FFFDF6',
    tdColorHover: '#FAF6EE',
    borderColor: '#F5ECE4',
    borderRadius: '12px'
  },
  List: {
    color: '#FFFDF6',
    borderColor: '#F5ECE4'
  },
  Upload: {
    borderColor: '#F0E6DE',
    hoverColor: 'rgba(232, 180, 184, 0.08)',
    borderRadius: '12px'
  }
}))
</script>

<template>
  <NConfigProvider :theme-overrides="themeOverrides">
    <NMessageProvider>
      <NDialogProvider>
        <NNotificationProvider>
          <NLoadingBarProvider>
            <LayoutMain />
          </NLoadingBarProvider>
        </NNotificationProvider>
      </NDialogProvider>
    </NMessageProvider>
  </NConfigProvider>
</template>
