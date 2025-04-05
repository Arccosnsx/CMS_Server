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
    }
  }),

  actions: {
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

    // 进入新文件夹
    async pushPath(folder) {
      //console.log('尝试添加路径:', folder.name, '当前路径栈:', this.pathStack)
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
        await filesApi.createFolder(name, parentId || this.currentParentId)
        await this.loadFiles(parentId || this.currentParentId)
      } catch (err) {
        console.error('创建文件夹失败:', err)
        throw err
      }
    },

    // 上传文件
    async uploadFile(file, parentId = null) {
      try {
        await filesApi.uploadFile(file, parentId || this.currentParentId)
        await this.loadFiles(parentId || this.currentParentId)
      } catch (err) {
        console.error('上传文件失败:', err)
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
      if (state.pathStack.length > 0) {
        console.log(state.pathStack[1])
        return state.pathStack[1].name
      }
      else
        return null
    },
  }
})