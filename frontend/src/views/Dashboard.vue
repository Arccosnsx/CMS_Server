<template>
    <div class="dashboard">
        <!-- 顶部导航栏 -->
        <div class="top-bar">
            <div class="app-title">古协文件仓库</div>
            <div class="user-info">
                <span class="username">{{ authStore.user?.username }}</span>
                <span class="user-role">{{ roleDisplay }}</span>
                <button @click="handleLogout" class="logout-btn">退出</button>
            </div>
        </div>

        <div class="action-bar">
            <!-- 上传按钮 -->
            <button class="upload-btn" @click="showUploadModal" >
                <span>📤 上传</span>
            </button>

            <!-- 其他路径导航等内容... -->
        </div>

        <UploadModal :currentParentId="filesStore.currentParentId" :visible="showUploadModalFlag" :currentPath="filesStore.currentPath" @close="hideUploadModal" />


        <!-- 路径导航 -->
        <div class="path-navigation">
            <span v-for="(path, index) in filesStore.pathStack" :key="index" class="path-segment"
                @click="navigateTo(index)">
                <span v-if="index > 0" class="path-separator">/</span>
                {{ path.displayName || path.name }}
            </span>
        </div>

        <!-- 文件加载状态 -->
        <div v-if="filesStore.isLoading" class="loading-indicator">
            <span class="loading-spinner"></span>
            加载中...
        </div>

        <!-- 错误提示 -->
        <div v-if="filesStore.error" class="error-message">
            {{ filesStore.error }}
            <button @click="retryLoad" class="retry-btn">重试</button>
        </div>

        <!-- 文件网格 -->
        <div v-if="!filesStore.isLoading && !filesStore.error" class="file-grid">
            <FileCard v-for="file in filesStore.currentFiles" :key="file.id" :item="file" @click="handleFileClick" @menu-action="handleMenuAction"/>
        </div>

        <!-- 空状态提示 -->
        <div v-if="!filesStore.isLoading && !filesStore.error && filesStore.currentFiles.length === 0"
            class="empty-state">
            <div class="empty-icon">📁</div>
            <div class="empty-text">当前文件夹为空</div>
        </div>
    </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useFilesStore } from '../stores/files'
import FileCard from '../components/FileCard.vue'
import UploadModal from '../components/UploadModal.vue'

export default {
    components: {
        FileCard,
        UploadModal
     },
    setup() {
        const router = useRouter()
        const authStore = useAuthStore()
        const filesStore = useFilesStore()

        const roleDisplay = computed(() => {
            const roles = {
                'admin': '管理员',
                'member': '成员',
                'user': '用户'
            }
            return roles[authStore.user?.role] || authStore.user?.role
        })

        const showUploadModalFlag = ref(false)

        const showUploadModal = () => {
            showUploadModalFlag.value = true
        }

        const hideUploadModal = () => {
            showUploadModalFlag.value = false
        }

        const handleFileClick = async (file) => {
            if (file.is_folder) {
                //console.log("handleFileClick is Called")
                filesStore.pushPath({
                    id: file.id,
                    name: file.name,
                    displayName: file.displayName || file.name
                })
                await filesStore.loadFiles(file.id)
            } else {
                // 处理文件点击（如下载或预览）
                //console.log('打开文件:', file.name)
                // 实际项目中可以调用下载API或打开预览
            }
        }

        const navigateTo = (index) => {
            if (index === filesStore.pathStack.length - 1) return
            filesStore.navigateTo(index)
        }

        const handleLogout = () => {
            authStore.logout()
            router.push('/login')
        }

        const retryLoad = () => {
            filesStore.loadFiles(filesStore.currentParentId)
        }

        onMounted(() => {
            filesStore.loadFiles(null) // 初始加载根目录
        })

        const handleMenuAction=({ action, file }) =>{
      switch(action) {
        case 'download':
          this.downloadFile(file)
          break
        case 'rename':
          this.renameFile(file)
          break
        case 'move':
          this.moveFile(file)
          break
        case 'properties':
          this.showFileProperties(file)
          break
      }
    }
    
    const downloadFile=(file) =>{
      console.log('下载文件:', file.name)
      // 实现下载逻辑
    }
    
    const renameFile=(file) =>{
      console.log('重命名文件:', file.name)
      // 实现重命名逻辑
    }


        return {
            authStore,
            filesStore,
            roleDisplay,
            handleFileClick,
            navigateTo,
            handleLogout,
            retryLoad,
            showUploadModalFlag,
            showUploadModal,
            hideUploadModal,
            handleMenuAction,
            downloadFile,
            renameFile
        }
    }
}
</script>

<style scoped>
.dashboard {
    padding: 20px;
    font-family: 'Arial', sans-serif;
    max-width: 1200px;
    margin: 0 auto;
    min-height: 100vh;
}

.top-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 1px solid #eaeaea;
}

.app-title {
    font-size: 24px;
    font-weight: bold;
    color: #1890ff;
}

.user-info {
    display: flex;
    align-items: center;
    gap: 15px;
}

.username {
    font-weight: 500;
    color: #333;
}

.user-role {
    background-color: #f0f0f0;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 12px;
    color: #666;
}

.logout-btn {
    padding: 6px 12px;
    background-color: #f5f5f5;
    border: 1px solid #d9d9d9;
    border-radius: 4px;
    cursor: pointer;
    color: #666;
    transition: all 0.2s;
}

.logout-btn:hover {
    background-color: #ff4d4f;
    border-color: #ff4d4f;
    color: white;
}

.path-navigation {
    background-color: #f0f9ff;
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 20px;
    border: 1px solid #d0e8ff;
    font-size: 15px;
}

.path-segment {
    cursor: pointer;
    padding: 4px 6px;
    border-radius: 4px;
    transition: all 0.2s;
}

.path-segment:hover {
    background-color: #e6f7ff;
    color: #1890ff;
}

.path-separator {
    margin: 0 5px;
    color: #999;
}

.file-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 16px;
    margin-top: 16px;
}

.loading-indicator {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20px;
    color: #666;
}

.loading-spinner {
    display: inline-block;
    width: 16px;
    height: 16px;
    border: 2px solid #1890ff;
    border-radius: 50%;
    border-top-color: transparent;
    animation: spin 1s linear infinite;
    margin-right: 8px;
}

@keyframes spin {
    to {
        transform: rotate(360deg);
    }
}

.error-message {
    background-color: #fff2f0;
    border: 1px solid #ffccc7;
    color: #f5222d;
    padding: 12px;
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.retry-btn {
    background-color: #ff4d4f;
    color: white;
    border: none;
    padding: 4px 8px;
    border-radius: 2px;
    cursor: pointer;
    margin-left: 10px;
}

.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 40px 0;
    color: #999;
}

.empty-icon {
    font-size: 48px;
    margin-bottom: 16px;
}

.empty-text {
    font-size: 16px;
}

.action-bar {
    display: flex;
    align-items: center;
    margin-bottom: 16px;
    gap: 8px;
}

.upload-btn {
    padding: 8px 16px;
    background-color: #1890ff;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 4px;
    width: 100px;
}

.upload-btn:hover {
    background-color: #40a9ff;
}
</style>