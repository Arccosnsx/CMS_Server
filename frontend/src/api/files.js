// ../api/files.js
import axios from 'axios'

const API_URL = 'http://localhost:8000'

const createHeaders = () => ({
    Authorization: `Bearer ${localStorage.getItem('token')}`,
    'Content-Type': 'application/json'
})

export default {
    // 列出文件
    listFiles: (parentId = null) => {
        return axios.get(`${API_URL}/files/list`, {
            params: { parent_id: parentId },
            headers: createHeaders()
        })
    },

    // 下载文件
    downloadFile: (fileId, onProgress) => {
        return axios.get(`${API_URL}/files/download/${fileId}`, {
            headers: createHeaders(),
            responseType: 'blob',
            onDownloadProgress: (progressEvent) => {
                if (onProgress && progressEvent.total) {
                    const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total)
                    onProgress(percent)
                }
            }
        })
    },

    // 重命名文件
    renameFile: (fileId, newName) => {
        return axios.patch(`${API_URL}/files/${fileId}/rename`,
            { newName },
            { headers: createHeaders() }
        )
    },

    // 删除文件
    deleteFile: (fileId) => {
        return axios.delete(`${API_URL}/files/${fileId}`, {
            headers: createHeaders()
        })
    },

    // 创建文件夹
    createFolder: (folderData) => {
        return axios.post(`${API_URL}/files/create-folder`,
            folderData,
            { headers: createHeaders() }
        )
    },

    // 移动文件
    moveFile: (fileId, targetParentId) => {
        return axios.post(`${API_URL}/files/move/${fileId}`,
            { target_parent_id: targetParentId },
            { headers: createHeaders() }
        )
    }
}