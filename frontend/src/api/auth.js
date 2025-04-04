// src/api/auth.js
import axios from 'axios'

const API_URL = 'http://localhost:8000' // 根据你的后端地址调整

export default {
    /**
     * 用户登录
     * @param {string} username - 用户名
     * @param {string} password - 密码
     * @returns {Promise} 包含access_token的响应
     */
    async login(username, password) {
        try {
            // 注意这里使用FormData格式，因为后端使用OAuth2PasswordRequestForm
            const formData = new FormData()
            formData.append('username', username)
            formData.append('password', password)

            const response = await axios.post(`${API_URL}/auth/login`, formData)

            // 存储token到localStorage或vuex
            localStorage.setItem('access_token', response.data.access_token)

            return response.data
        } catch (error) {
            throw new Error(error.response?.data?.detail || '登录失败')
        }
    },

    /**
     * 用户注册
     * @param {Object} userData - 用户数据 {username, email, password}
     * @returns {Promise} 注册成功的用户信息
     */
    async register(userData) {
        try {
            const response = await axios.post(`${API_URL}/auth/register`, userData)
            return response.data
        } catch (error) {
            throw new Error(
                error.response?.data?.detail ||
                (error.response?.status === 400 ? '用户名或邮箱已存在' : '注册失败')
            )
        }
    },

    /**
     * 用户注销
     * @returns {Promise} 注销成功的消息
     */
    async logout() {
        try {
            // 从存储中移除token
            localStorage.removeItem('access_token')

            // 调用后端注销接口
            const response = await axios.post(`${API_URL}/auth/logout`)
            return response.data
        } catch (error) {
            throw new Error(error.response?.data?.detail || '注销失败')
        }
    },

    /**
     * 获取当前用户信息
     * @returns {Promise} 当前用户信息
     */
    async getCurrentUser() {
        try {
            const token = localStorage.getItem('access_token')
            if (!token) return null

            const response = await axios.get(`${API_URL}/users/me`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            })
            return response.data
        } catch (error) {
            localStorage.removeItem('access_token')
            return null
        }
    }
}