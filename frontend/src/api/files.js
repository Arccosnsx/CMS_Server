// ../api/files.js
import axios from 'axios'

const API_URL = 'http://localhost:8000'

const createHeaders = () => ({
    Authorization: `Bearer ${localStorage.getItem('token')}`
})


export default {
    listFiles: (parentId = null) => {
        return axios.get(`${API_URL}/files/list`, {
            params: { parent_id: parentId },
            headers: createHeaders()
        })
    },

    uploadFile: (file, parentId = null) => {
        const formData = new FormData()
        formData.append('file', file)
        return axios.post(`${API_URL}/files/upload`, formData, {
            params: { parent_id: parentId },
            headers: {
                ...createHeaders(),
                'Content-Type': 'multipart/form-data'
            }
        })
    }
}