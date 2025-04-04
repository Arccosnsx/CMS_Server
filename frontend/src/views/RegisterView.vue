<template>
    <div class="register-container">
        <h1>注册新账户</h1>
        <form @submit.prevent="handleRegister">
            <div class="form-group">
                <label for="username">用户名</label>
                <input id="username" v-model="form.username" type="text" required minlength="3" maxlength="20"
                    :class="{ 'input-error': errors.username }">
                <span v-if="errors.username" class="error-message">{{ errors.username }}</span>
            </div>

            <div class="form-group">
                <label for="email">电子邮箱</label>
                <input id="email" v-model="form.email" type="email" required :class="{ 'input-error': errors.email }">
                <span v-if="errors.email" class="error-message">{{ errors.email }}</span>
            </div>

            <div class="form-group">
                <label for="password">密码</label>
                <input id="password" v-model="form.password" type="password" required minlength="8"
                    :class="{ 'input-error': errors.password }">
                <span v-if="errors.password" class="error-message">{{ errors.password }}</span>
            </div>

            <div class="form-group">
                <label for="confirmPassword">确认密码</label>
                <input id="confirmPassword" v-model="form.confirmPassword" type="password" required
                    :class="{ 'input-error': errors.confirmPassword }">
                <span v-if="errors.confirmPassword" class="error-message">{{ errors.confirmPassword }}</span>
            </div>

            <button type="submit" :disabled="isSubmitting">
                {{ isSubmitting ? '注册中...' : '注册' }}
            </button>

            <div class="login-link">
                已有账户？<router-link to="/login">立即登录</router-link>
            </div>
        </form>
    </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import authApi from '../api/auth'

export default {
    setup() {
        const router = useRouter()
        const authStore = useAuthStore()

        const form = ref({
            username: '',
            email: '',
            password: '',
            confirmPassword: ''
        })

        const errors = ref({
            username: '',
            email: '',
            password: '',
            confirmPassword: ''
        })

        const isSubmitting = ref(false)

        const validateForm = () => {
            let isValid = true
            errors.value = { username: '', email: '', password: '', confirmPassword: '' }

            // 用户名验证
            if (form.value.username.length < 3) {
                errors.value.username = '用户名至少需要3个字符'
                isValid = false
            }

            // 邮箱验证
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
            if (!emailRegex.test(form.value.email)) {
                errors.value.email = '请输入有效的邮箱地址'
                isValid = false
            }

            // 密码验证
            if (form.value.password.length < 8) {
                errors.value.password = '密码至少需要8个字符'
                isValid = false
            }

            // 确认密码验证
            if (form.value.password !== form.value.confirmPassword) {
                errors.value.confirmPassword = '两次输入的密码不一致'
                isValid = false
            }

            return isValid
        }

        const handleRegister = async () => {
            if (!validateForm()) return

            isSubmitting.value = true

            try {
                await authApi.register({
                    username: form.value.username,
                    email: form.value.email,
                    password: form.value.password
                })

                // 注册成功后自动登录
                await authStore.login({
                    username: form.value.username,
                    password: form.value.password
                })

                router.push('/dashboard')
            } catch (error) {
                if (error.response) {
                    const { data } = error.response
                    if (data.detail === 'Username already registered') {
                        errors.value.username = '该用户名已被注册'
                    } else if (data.detail === 'Email already registered') {
                        errors.value.email = '该邮箱已被注册'
                    } else {
                        alert('注册失败: ' + (data.detail || '未知错误'))
                    }
                } else {
                    alert('网络错误，请稍后重试')
                }
            } finally {
                isSubmitting.value = false
            }
        }

        return { form, errors, isSubmitting, handleRegister }
    }
}
</script>

<style scoped>
.register-container {
    max-width: 400px;
    margin: 50px auto;
    padding: 30px;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    background-color: white;
}

h1 {
    text-align: center;
    margin-bottom: 24px;
    color: #333;
}

.form-group {
    margin-bottom: 16px;
}

label {
    display: block;
    margin-bottom: 6px;
    font-weight: 500;
    color: #555;
}

input {
    width: 100%;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 14px;
    box-sizing: border-box;
}

.input-error {
    border-color: #ff4d4f;
}

.error-message {
    display: block;
    margin-top: 4px;
    color: #ff4d4f;
    font-size: 12px;
}

button {
    width: 100%;
    padding: 12px;
    margin-top: 10px;
    background-color: #1890ff;
    color: white;
    border: none;
    border-radius: 4px;
    font-size: 16px;
    cursor: pointer;
    transition: background-color 0.3s;
}

button:hover {
    background-color: #40a9ff;
}

button:disabled {
    background-color: #d9d9d9;
    cursor: not-allowed;
}

.login-link {
    margin-top: 16px;
    text-align: center;
    color: #666;
}

.login-link a {
    color: #1890ff;
    text-decoration: none;
}

.login-link a:hover {
    text-decoration: underline;
}
</style>