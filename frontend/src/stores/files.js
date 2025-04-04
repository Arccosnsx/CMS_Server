import { defineStore } from 'pinia'
import filesApi from '../api/files'

export const useFilesStore = defineStore('files', {
  state: () => ({
    currentPath: [],
    currentFiles: [],
    currentSpace: 'personal'
  }),
  actions: {
    async loadFiles(spaceType, parentId = null) {
      const response = await filesApi.listFiles(spaceType, parentId)
      this.currentFiles = response.data
      this.currentSpace = spaceType
    }
  }
})