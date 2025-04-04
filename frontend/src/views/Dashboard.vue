<template>
    <div class="dashboard">
        <header>
            <h1>CMS 文件管理系统</h1>
            <button @click="handleLogout">退出登录</button>
        </header>

        <nav>
            <button v-for="space in spaces" :key="space.id" @click="switchSpace(space.id)"
                :class="{ active: currentSpace === space.id }">
                {{ space.name }}
            </button>
        </nav>

        <main>
            <FileBrowser />
        </main>
    </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth.js'
import { useFilesStore } from '../stores/files.js'
import FileBrowser from '../components/FileBrowser.vue'

export default {
    components: { FileBrowser },
    setup() {
        const router = useRouter()
        const authStore = useAuthStore()
        const filesStore = useFilesStore()

        const spaces = [
            { id: 'personal', name: '个人空间' },
            { id: 'group', name: '社团空间' },
            { id: 'public', name: '公共空间' }
        ]

        const currentSpace = ref('personal')

        const switchSpace = (space) => {
            currentSpace.value = space
            filesStore.loadFiles(space)
        }

        const handleLogout = () => {
            authStore.logout()
            router.push('/login')
        }

        return { spaces, currentSpace, switchSpace, handleLogout }
    }
}
</script>

<style>
.dashboard {
    display: grid;
    grid-template-rows: auto auto 1fr;
    height: 100vh;
}

header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px;
    background-color: #f0f0f0;
    border-bottom: 1px solid #ddd;
}

nav {
    display: flex;
    padding: 10px;
    background-color: #f8f8f8;
    border-bottom: 1px solid #ddd;
}

nav button {
    margin-right: 10px;
    padding: 8px 15px;
    background: none;
    border: 1px solid #ddd;
    border-radius: 4px;
    cursor: pointer;
}

nav button.active {
    background-color: #42b983;
    color: white;
    border-color: #42b983;
}

main {
    padding: 20px;
    overflow: auto;
}
</style>