// /frontend/src/api/axios.ts
import axios from 'axios';
import { useAuthStore } from '../store/authStore';

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL === '/' ? '' : (import.meta.env.VITE_API_URL || 'http://localhost:8000'),
    withCredentials: true,
});

// 1. Request Interceptor
api.interceptors.request.use(
    (config) => {
        const token = useAuthStore.getState().accessToken;
        if (token && config.headers) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// --- Concurrency / Queue Management Variables ---
let isRefreshing = false;
let failedQueue: Array<{ resolve: (token: string) => void; reject: (error: any) => void }> = [];

const processQueue = (error: any, token: string | null = null) => {
    failedQueue.forEach(prom => {
        if (error) prom.reject(error);
        else if (token) prom.resolve(token);
    });
    failedQueue = [];
};

// 2. Response Interceptor
api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {

            // If another request is already fetching a new token, queue this one up!
            if (isRefreshing) {
                return new Promise(function(resolve, reject) {
                    failedQueue.push({ resolve, reject });
                }).then(token => {
                    // Explicitly mark this queued request as a retry
                    // so it doesn't trigger another refresh if it fails again.
                    originalRequest._retry = true;
                    originalRequest.headers.Authorization = `Bearer ${token}`;
                    return api(originalRequest);
                }).catch(err => {
                    return Promise.reject(err);
                });
            }

            // Lock the refresh process
            originalRequest._retry = true;
            isRefreshing = true;

            try {
                // Use raw axios to hit the refresh endpoint,
                // Let Axios safely resolve the path using the baseURL config
                const refreshResponse = await axios.post(
                    '/api/auth/refresh',
                    {},
                    {
                        baseURL: api.defaults.baseURL,
                        withCredentials: true
                    }
                );

                const newAccessToken = refreshResponse.data.access_token;
                const user = refreshResponse.data.user;

                // Update global state
                useAuthStore.getState().setAccessToken(newAccessToken, user);

                // Release the queue and let pending requests proceed with the new token
                processQueue(null, newAccessToken);

                // Retry the original request
                originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
                return api(originalRequest);

            } catch (refreshError) {
                // If refresh fails, reject all queued requests and log the user out
                processQueue(refreshError, null);
                useAuthStore.getState().clearAuth();
                return Promise.reject(refreshError);
            } finally {
                // Unlock the process
                isRefreshing = false;
            }
        }
        return Promise.reject(error);
    }
);

export default api;
