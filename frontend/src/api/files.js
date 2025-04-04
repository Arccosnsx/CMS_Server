import axios from 'axios'

const API_URL = 'http://localhost:8000'

export default {
    listFiles: (spaceType, parentId = null) => {
        return axios.get(`${API_URL}/files/list/${spaceType}`, {
            params: { parent_id: parentId },
            headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        })
    },
    uploadFile: (spaceType, file, parentId = null) => {
        const formData = new FormData()
        formData.append('file', file)
        return axios.post(`${API_URL}/files/upload/${spaceType}`, formData, {
            params: { parent_id: parentId },
            headers: {
                Authorization: `Bearer ${localStorage.getItem('token')}`,
                'Content-Type': 'multipart/form-data'
            }
        })
    }
}