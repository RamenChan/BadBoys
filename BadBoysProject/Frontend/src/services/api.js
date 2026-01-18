import axios from 'axios';

const API_BASE_URL = "http://localhost:8000";

const api = axios.create({
    baseURL: API_BASE_URL,
    timeout: 10000,
    headers: { 'Content-Type': 'application/json' },
    withCredentials: true,
});

const getCSRFTokenFromCookie = () => {
    return document.cookie
        .split('; ')
        .find(row => row.startsWith('csrf_token='))
        ?.split('=')[1];
};

api.interceptors.request.use((config) => {
    if (['post', 'put', 'delete', 'patch'].includes(config.method)) {
        const csrfToken = getCSRFTokenFromCookie();
        if (csrfToken) {
            config.headers['X-CSRF-Token'] = csrfToken;
        }
    }
    return config;
});

export const fetchCSRFToken = async () => {
    await api.get('/csrf-token');
};

export const authAPI = {
    login: async (username, password) => {
        const { data } = await api.post('/user_check', { username, password });
        return data;
    },

    register: async (username, password, confirmPassword, email) => {
        const { data } = await api.post('/user_add', { username, password, confirmPassword, email });
        return data;
    },

    logout: async () => {
        const { data } = await api.post('/logout');
        return data;
    },
};

export const storiesAPI = {
    getStories: (source = 'api') =>
        api.get(`/api/stories?source=${source}`),
};

export default api;
