import axios from 'axios';

const API_BASE_URL = "http://localhost:8000";

const api = axios.create({
    baseURL: API_BASE_URL,
    timeout: 10000,
    headers: { 'Content-Type': 'application/json' },
    withCredentials: true,
});

let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
    failedQueue.forEach(prom => {
        if (error) {
            prom.reject(error);
        } else {
            prom.resolve(token);
        }
    });
    failedQueue = [];
};

api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {

            if (
                originalRequest.url === '/refresh' ||
                originalRequest.url === '/user_check'
            ) {
                return Promise.reject(error);
            }

            if (isRefreshing) {
                return new Promise((resolve, reject) => {
                    failedQueue.push({ resolve, reject });
                }).then(() => {
                    return api(originalRequest);
                }).catch(err => {
                    return Promise.reject(err);
                });
            }

            originalRequest._retry = true;
            isRefreshing = true;

            try {
                await api.post('/refresh');

                processQueue(null, null);
                isRefreshing = false;

                return api(originalRequest);
            } catch (refreshError) {
                processQueue(refreshError, null);
                isRefreshing = false;

                return Promise.reject(refreshError);
            }
        }

        return Promise.reject(error);
    }
);

export const authAPI = {
    login: async (username, password) => {
        const { data } = await api.post('/user_check', { username, password });
        return data;
    },

    register: async (username, password, confirmPassword, email) => {
        const { data } = await api.post('/user_add', {
            username,
            password,
            confirmPassword,
            email
        });
        return data;
    },

    logout: async () => {
        const { data } = await api.post('/logout');
        return data;
    },

    getCurrentUser: async () => {
        const { data } = await api.get('/user/me');
        return data;
    },

    refreshToken: async () => {
        const { data } = await api.post('/refresh');
        return data;
    }
};


export const storiesAPI = {
    getStories: async (source = 'api') => {
        const { data } = await api.get(`/api/stories?source=${source}`);
        return data;
    }
};

export default api;