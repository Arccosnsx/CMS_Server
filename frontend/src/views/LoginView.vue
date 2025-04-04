<template>
    <div>
        <!-- 登录表单 -->
        <div v-if="!isAuthenticated">
            <h2>登录</h2>
            <form @submit.prevent="handleLogin">
                <input v-model="loginForm.username" placeholder="用户名" required>
                <input v-model="loginForm.password" type="password" placeholder="密码" required>
                <button type="submit">登录</button>
            </form>

            <!-- 注册表单 -->
            <h2>注册</h2>
            <form @submit.prevent="handleRegister">
                <input v-model="registerForm.username" placeholder="用户名" required>
                <input v-model="registerForm.email" type="email" placeholder="邮箱" required>
                <input v-model="registerForm.password" type="password" placeholder="密码" required>
                <button type="submit">注册</button>
            </form>
        </div>

        <!-- 登录后显示 -->
        <div v-else>
            <p>欢迎, {{ currentUser.username }}!</p>
            <button @click="handleLogout">注销</button>
        </div>

        <!-- 显示消息 -->
        <div v-if="message" :class="['message', messageType]">
            {{ message }}
        </div>
    </div>
</template>

<script>
import authApi from '../api/auth.js'

export default {
    data() {
        return {
            loginForm: {
                username: '',
                password: ''
            },
            registerForm: {
                username: '',
                email: '',
                password: ''
            },
            currentUser: null,
            isAuthenticated: false,
            message: '',
            messageType: ''
        }
    },
    async created() {
        await this.checkAuth()
    },
    methods: {
        async checkAuth() {
            this.currentUser = await authApi.getCurrentUser()
            this.isAuthenticated = !!this.currentUser
        },

        async handleLogin() {
            try {
                await authApi.login(this.loginForm.username, this.loginForm.password)
                await this.checkAuth()
                this.showMessage('登录成功', 'success')
            } catch (error) {
                this.showMessage(error.message, 'error')
            }
        },

        async handleRegister() {
            try {
                await authApi.register(this.registerForm)
                this.showMessage('注册成功，请等待管理员审核', 'success')
                this.registerForm = { username: '', email: '', password: '' }
            } catch (error) {
                this.showMessage(error.message, 'error')
            }
        },

        async handleLogout() {
            try {
                await authApi.logout()
                await this.checkAuth()
                this.showMessage('注销成功', 'success')
            } catch (error) {
                this.showMessage(error.message, 'error')
            }
        },

        showMessage(msg, type) {
            this.message = msg
            this.messageType = type
            setTimeout(() => {
                this.message = ''
                this.messageType = ''
            }, 3000)
        }
    }
}
</script>

<style>
.message {
    padding: 10px;
    margin: 10px 0;
    border-radius: 4px;
}

.message.success {
    background-color: #d4edda;
    color: #155724;
}

.message.error {
    background-color: #f8d7da;
    color: #721c24;
}
</style>