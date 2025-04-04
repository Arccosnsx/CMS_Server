import { defineStore } from 'pinia'
import authApi from '../api/auth'

export const useAuthStore = defineStore('auth', {
    state: () => ({
        user: null,
        token: localStorage.getItem('token') || null
    }),
    actions: {
        async login(credentials) {
            const { access_token } = await authApi.login(credentials)
            this.token = access_token
            localStorage.setItem('token', access_token)
        },
        logout() {
            this.user = null
            this.token = null
            localStorage.removeItem('token')
            authApi.logout()
        }
    }
})