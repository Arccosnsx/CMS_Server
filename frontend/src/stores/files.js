import { defineStore } from 'pinia'
import filesApi from '../api/files.js'

export const useFilesStore = defineStore('files', {
  state: () => ({
    currentSpace: 'user',
    currentPath: null,
    files: []
  }),
  actions: {
    async uploadFile(file, parentId = null) {
      return filesApi.upload(this.currentSpace, file, parentId)
    },
    async fetchFiles(parentId = null) {
      this.files = await filesApi.list(this.currentSpace, parentId)
    },
    async createFolder(name) {
      const folderData = {
        name,
        is_folder: true,
        owner_type: this.currentSpace
      }
      return filesApi.createFolder(folderData)
    }
  }
})