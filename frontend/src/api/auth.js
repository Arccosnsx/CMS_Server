import axios from 'axios'

const API_URL = 'http://localhost:8000'

export default {
    login: async (credentials) => {
        const params = new URLSearchParams();
        params.append('username', credentials.username);
        params.append('password', credentials.password);
        //console.log('Sending login request with:', params.toString());
        try {
            const response = await axios.post(`${API_URL}/login`, params, {
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            });
            return response.data;
        } catch (error) {
            console.error('Login error:', error.response?.data);
            throw error;
        }
    },
    register: async (userData) => {
        const response = await axios.post(`${API_URL}/auth/register`, {
            username: userData.username,
            email: userData.email,
            password: userData.password
        })
        return response.data
    },
    logout: () => {
        return axios.post(`${API_URL}/auth/logout`)
    }
}