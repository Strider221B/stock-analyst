// /frontend/src/store/authStore.ts
import { create } from 'zustand';
import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface User {
    id: string;
    email: string;
}

interface AuthState {
    user: User | null;
    isAuthenticated: boolean;
    accessToken: string | null;
    isAuthLoading: boolean;

    setAccessToken: (token: string, user: User) => void;
    clearAuth: () => void;
    checkAuth: () => Promise<void>;
    login: (credentials: any) => Promise<void>;
    logout: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set, get) => ({
    user: null,
    isAuthenticated: false,
    accessToken: null,
    isAuthLoading: true,

    setAccessToken: (token, user) => set({ accessToken: token, user, isAuthenticated: true }),

    clearAuth: () => set({
        accessToken: null,
        user: null,
        isAuthenticated: false,
        isAuthLoading: false // Fixed: Ensure loading ends on clear
    }),

    checkAuth: async () => {
        try {
            const response = await axios.post(
                `${BASE_URL}/api/auth/refresh`,
                {},
                { withCredentials: true }
            );

            set({
                accessToken: response.data.access_token,
                user: response.data.user,
                isAuthenticated: true,
                isAuthLoading: false,
            });
        } catch (error: any) {
            // Check if it's a standard Axios error
            if (axios.isAxiosError(error)) {
                if (error.response?.status === 401) {
                    // EXPECTED: User simply doesn't have a valid cookie. Silently clear.
                    get().clearAuth();
                    return;
                }
            }

            // UNEXPECTED: The server is down (500) or the network is offline.
            // We log this so you aren't flying blind during debugging.
            console.error("Failed to reach backend during auth check:", error);
            get().clearAuth();
        }
    },

    login: async (credentials) => {
        // Fixed: Use raw axios
        const response = await axios.post(
            `${BASE_URL}/api/auth/login`,
            credentials,
            { withCredentials: true }
        );

        set({
            accessToken: response.data.access_token,
            user: response.data.user,
            isAuthenticated: true,
            isAuthLoading: false, // Fixed: Update loading state upon manual login
        });
    },

    logout: async () => {
        try {
            await axios.post(`${BASE_URL}/api/auth/logout`, {}, { withCredentials: true });
        } finally {
            get().clearAuth();
        }
    }
}));
