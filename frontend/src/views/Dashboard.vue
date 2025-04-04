<template>
    <div class="dashboard">
        <header>
            <div class="header-left">
                <img src="../assets/logo.png" alt="Logo" class="logo">
                <h1>古协的小仓库</h1>
            </div>
            <div class="header-right">
                <span class="username">{{ authStore.user?.username }}</span>
                <button @click="handleLogout" class="logout-btn">退出登录</button>
            </div>
        </header>

        <div class="path-display">
            <span v-for="(part, index) in pathParts" :key="index" @click="navigateTo(index)">
                <span class="path-separator" v-if="index > 0">/</span>
                <span class="path-part">{{ part }}</span>
            </span>
        </div>

        <nav>
            <button v-for="space in spaces" :key="space.id" @click="switchSpace(space.id)"
                :class="{ active: currentSpace === space.id }">
                {{ space.name }}
            </button>
        </nav>

        <main>
            <FileBrowser :files="files" @navigate="handleNavigate" />
        </main>
    </div>
</template>

<script>
import { ref, computed } from 'vue'
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
            {id: 'public', name: '公共空间' }
    ]

    const currentSpace = ref('personal')
    const currentPath = ref('/')

    const pathParts = computed(() => {
        return currentPath.value.split('/').filter(part => part !== '')
    })

    const files = ref([
        { id: 1, name: '文档', type: 'folder', size: '-', modified: '2023-05-15' },
        { id: 2, name: '图片', type: 'folder', size: '-', modified: '2023-05-10' },
        { id: 3, name: '报告.pdf', type: 'file', size: '2.5MB', modified: '2023-05-01' },
        { id: 4, name: '资料.zip', type: 'file', size: '15.2MB', modified: '2023-04-28' }
    ])

    const switchSpace = (space) => {
        currentSpace.value = space
        currentPath.value = '/'
        filesStore.loadFiles(space, '/')
    }

    const handleLogout = () => {
        authStore.logout()
        router.push('/login')
    }

    const navigateTo = (index) => {
        const newPath = '/' + pathParts.value.slice(0, index + 1).join('/')
        currentPath.value = newPath
        filesStore.loadFiles(currentSpace.value, newPath)
    }

    const handleNavigate = (folder) => {
        const newPath = currentPath.value === '/' ? `/${folder}` : `${currentPath.value}/${folder}`
        currentPath.value = newPath
        filesStore.loadFiles(currentSpace.value, newPath)
    }

    return {
        authStore,
        spaces,
        currentSpace,
        currentPath,
        pathParts,
        files,
        switchSpace,
        handleLogout,
        navigateTo,
        handleNavigate
    }
}
}
</script>

<style scoped>
.dashboard {
    display: grid;
    grid-template-rows: auto auto auto 1fr;
    height: 100vh;
    font-family: 'Arial', sans-serif;
}

header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 20px;
    background-color: #e6f7ff;
    border-bottom: 1px solid #b3e0ff;
    height: 60px;
}

.header-left {
    display: flex;
    align-items: center;
    gap: 15px;
}

.logo {
    height: 40px;
    width: auto;
}

h1 {
    margin: 0;
    color: #1890ff;
    font-size: 20px;
}

.header-right {
    display: flex;
    align-items: center;
    gap: 15px;
}

.username {
    font-weight: 500;
    color: #333;
}

.logout-btn {
    padding: 6px 12px;
    background-color: #f5f5f5;
    border: 1px solid #d9d9d9;
    border-radius: 4px;
    cursor: pointer;
    color: #666;
}

.logout-btn:hover {
    background-color: #e6f7ff;
    border-color: #1890ff;
    color: #1890ff;
}

.path-display {
    padding: 10px 20px;
    background-color: #f0f9f4;
    border-bottom: 1px solid #d9f7be;
    font-size: 14px;
}

.path-part {
    padding: 4px 8px;
    border-radius: 4px;
    cursor: pointer;
}

.path-part:hover {
    background-color: #d9f7be;
    color: #389e0d;
}

.path-separator {
    margin: 0 5px;
    color: #999;
}

nav {
    display: flex;
    padding: 10px 20px;
    background-color: #f6ffed;
    border-bottom: 1px solid #d9f7be;
    gap: 10px;
}

nav button {
    padding: 8px 15px;
    background: none;
    border: 1px solid #b7eb8f;
    border-radius: 4px;
    cursor: pointer;
    color: #389e0d;
    transition: all 0.3s;
}

nav button:hover {
    background-color: #d9f7be;
}

nav button.active {
    background-color: #389e0d;
    color: white;
    border-color: #389e0d;
}

main {
    padding: 20px;
    overflow: auto;
    background-color: #fafafa;
}
</style>