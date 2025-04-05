<template>
    <div class="login-container">
        <h1>CMS 登录</h1>
        <form @submit.prevent="handleLogin">
            <div class="form-group">
                <label>用户名</label>
                <input v-model="username" type="text" required>
            </div>
            <div class="form-group">
                <label>密码</label>
                <input v-model="password" type="password" required>
            </div>
            <button type="submit">登录</button>
        </form>
        <div class="register-link">
            没有账户？<router-link to="/register">立即注册</router-link>
        </div>
    </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth.js'

export default {
    setup() {
        const username = ref('')
        const password = ref('')
        const router = useRouter()
        const authStore = useAuthStore()
        const handleLogin = async () => {
            try {
                await authStore.login({
                    username: username.value,
                    password: password.value
                })
                router.push('/dashboard')
            } catch (error) {
                alert('登录失败: ' + error.message)
            }
        }

        return { username, password, handleLogin }
    }
}
</script>

<style>
.login-container {
    max-width: 300px;
    min-width: 200px;
    margin: 50px auto;
    padding: 20px;
    border: 1px solid #ddd;
    border-radius: 5px;
}

.form-group {
    margin-bottom: 15px;
}

.form-group label {
    display: block;
    margin-bottom: 5px;
}

.form-group input {
    width: 100%;
    padding: 8px;
    box-sizing: border-box;
}

button {
    width: 100%;
    padding: 10px;
    background-color: #42b983;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

.register-link {
    margin-top: 16px;
    text-align: center;
    color: #666;
}

.register-link a {
    color: #1890ff;
    text-decoration: none;
}

.register-link a:hover {
    text-decoration: underline;
}
</style>