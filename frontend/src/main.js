import { createApp } from 'vue'
import { createPinia } from 'pinia'
import NaiveUI, { create, NConfigProvider, NMessageProvider, NDialogProvider, NNotificationProvider, NLoadingBarProvider } from 'naive-ui'
import router from './router'
import App from './App.vue'
import './styles/global.scss'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(NaiveUI)

app.mount('#app')
