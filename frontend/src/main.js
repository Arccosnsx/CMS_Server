import { createApp } from 'vue'
import { createPinia } from 'pinia'

import 'vue-simple-uploader/dist/style.css'

import App from './App.vue'
import router from './router'
import uploader from 'vue-simple-uploader'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(uploader)
app.mount('#app')
