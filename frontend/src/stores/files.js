// ../stores/files.js
import { defineStore } from 'pinia'
import filesApi from '../api/files'

export const useFilesStore = defineStore('files', {
  state: () => ({
    currentFiles: [],
    pathStack: [{ id: null, name: '/', displayName: '根目录' }], // 初始化根目录
    isLoading: false,
    error: null,
    folderNameMap: { // 文件夹显示名称映射
      'public': '公共空间',
      'group': '社团空间',
      'users': '我的空间'
    },
    currentOperation: null // 当前正在执行的操作：'downloading'|'renaming'|'deleting'|'moving'
  }),

  actions: {
    // 加载文件列表
    async loadFiles(parentId = null) {
      this.isLoading = true
      this.error = null
      try {
        const response = await filesApi.listFiles(parentId)
        this.currentFiles = response.data

        // 根目录特殊处理 - 显示友好名称
        if (parentId === null) {
          this.currentFiles = this.currentFiles.map(file => ({
            ...file,
            displayName: this.getFolderDisplayName(file.name)
          }))
        }
      } catch (err) {
        this.error = err.response?.data?.message || err.message || '加载文件失败'
        console.error('加载文件失败:', err)
        throw err
      } finally {
        this.isLoading = false
      }
    },

    // 下载文件
    async downloadFile(file) {
      this.currentOperation = 'downloading'
      try {
        const response = await filesApi.downloadFile(file.id)

        // 创建下载链接
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', file.name)
        document.body.appendChild(link)
        link.click()

        // 清理
        window.URL.revokeObjectURL(url)
        document.body.removeChild(link)

      } catch (err) {
        const errorMsg = err.response?.data?.message || err.message || '下载失败'
        console.error('下载文件失败:', err)
        throw err
      } finally {
        this.currentOperation = null
      }
    },

    // 重命名文件/文件夹
    async renameFile(file, newName) {
      this.currentOperation = 'renaming'

      try {
        const response = await filesApi.renameFile(file.id, newName)

        // 更新当前文件列表
        const index = this.currentFiles.findIndex(f => f.id === file.id)
        if (index !== -1) {
          this.currentFiles[index] = response.data
        }

        return response.data
      } catch (err) {
        const errorMsg = err.response?.data?.message || err.message || '重命名失败'
        console.error('重命名文件失败:', err)
        throw err
      } finally {
        this.currentOperation = null
      }
    },

    // 删除文件/文件夹
    async deleteFile(file) {
      this.currentOperation = 'deleting'
      const toast = useToast()
      try {
        await filesApi.deleteFile(file.id)

        // 从当前文件列表中移除
        this.currentFiles = this.currentFiles.filter(f => f.id !== file.id)

        return true
      } catch (err) {
        const errorMsg = err.response?.data?.message || err.message || '删除失败'
        console.error('删除文件失败:', err)
        throw err
      } finally {
        this.currentOperation = null
      }
    },

    // 移动文件/文件夹
    async moveFile(file, targetParentId) {
      this.currentOperation = 'moving'
      try {
        const response = await filesApi.moveFile(file.id, targetParentId)

        // 从当前文件列表中移除（因为已经移动到其他位置）
        this.currentFiles = this.currentFiles.filter(f => f.id !== file.id)

        return response.data
      } catch (err) {
        const errorMsg = err.response?.data?.message || err.message || '移动失败'
        console.error('移动文件失败:', err)
        throw err
      } finally {
        this.currentOperation = null
      }
    },

    // 进入新文件夹
    async pushPath(folder) {
      this.pathStack.push({
        id: folder.id,
        name: folder.name,
        displayName: this.getFolderDisplayName(folder.name)
      })
      await this.loadFiles(folder.id)
    },

    // 返回上一级
    async popPath() {
      if (this.pathStack.length > 1) {
        this.pathStack.pop()
        const parentId = this.currentParentId
        await this.loadFiles(parentId)
      }
    },

    // 导航到指定路径层级
    async navigateTo(index) {
      if (index >= 0 && index < this.pathStack.length - 1) {
        this.pathStack = this.pathStack.slice(0, index + 1)
        await this.loadFiles(this.currentParentId)
      }
    },

    // 重置到根目录
    async resetToRoot() {
      this.pathStack = [{ id: null, name: '/', displayName: '根目录' }]
      await this.loadFiles(null)
    },

    getFolderDisplayName(originalName) {
      return this.folderNameMap[originalName] || originalName
    },

    // 创建新文件夹
    async createFolder(name, parentId = null) {
      try {
        const response = await filesApi.createFolder({
          name,
          is_folder: true,
          parent_id: parentId || this.currentParentId
        })

        // 添加到当前文件列表
        this.currentFiles.push(response.data)

        const toast = useToast()
        toast.success(`文件夹 "${name}" 创建成功`)
        return response.data
      } catch (err) {
        const errorMsg = err.response?.data?.message || err.message || '创建文件夹失败'
        const toast = useToast()
        toast.error(`创建文件夹失败: ${errorMsg}`)
        console.error('创建文件夹失败:', err)
        throw err
      }
    }
  },

  getters: {
    currentParentId: (state) => {
      return state.pathStack.length > 0
        ? state.pathStack[state.pathStack.length - 1].id
        : null
    },

    currentPath: (state) => {
      return state.pathStack.map(p => p.displayName || p.name).join(' / ')
    },

    isRoot: (state) => {
      return state.pathStack.length === 1 && state.pathStack[0].id === null
    },

    currentFolderName: (state) => {
      return state.pathStack.length > 0
        ? state.pathStack[state.pathStack.length - 1].displayName
        : '根目录'
    },

    currentSpace: (state) => {
      return state.pathStack.length > 1
        ? state.pathStack[1].name
        : null
    },

    // 是否正在执行操作
    isOperating: (state) => {
      return state.currentOperation !== null
    },

    // 获取当前操作类型
    operationType: (state) => {
      return state.currentOperation
    }
  }
})