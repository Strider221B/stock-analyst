import { create } from 'zustand';
import api from '../api/axios';
import axios from 'axios';

export type AccountType = 'DOMESTIC' | 'INTERNATIONAL' | 'EMPLOYEE_EQUITY';

export interface PortfolioItem {
    id: string;
    ticker: string;
    added_at: string;
}

export interface Portfolio {
    id: string;
    name: string;
    account_type: AccountType;
    items: PortfolioItem[];
    created_at: string;
    updated_at: string;
}

interface PortfolioState {
    portfolios: Portfolio[];
    isLoading: boolean;
    error: string | null;

    fetchPortfolios: () => Promise<void>;
    createPortfolio: (name: string, account_type: AccountType) => Promise<void>;
    addTickerToPortfolio: (portfolioId: string, ticker: string) => Promise<void>;
    removeTicker: (portfolioId: string, ticker: string) => Promise<void>;
}

export const usePortfolioStore = create<PortfolioState>((set, get) => ({
    portfolios: [],
    isLoading: false,
    error: null,

    fetchPortfolios: async () => {
        set({ isLoading: true, error: null });
        try {
            const response = await api.get<Portfolio[]>('/api/portfolios');
            set({ portfolios: response.data, isLoading: false });
        } catch (error: unknown) {
            let errorMessage = 'Failed to fetch portfolios';
            if (axios.isAxiosError(error)) {
                errorMessage = error.response?.data?.detail || errorMessage;
            }
            set({ error: errorMessage, isLoading: false });
        }
    },

    createPortfolio: async (name: string, account_type: AccountType) => {
        set({ isLoading: true, error: null });
        try {
            // Backend returns MessageResponse, not the new Portfolio object
            await api.post('/api/portfolios', { name, account_type });
            // Refresh the list to get the new portfolio (with its server-side ID)
            await get().fetchPortfolios();
        } catch (error: unknown) {
            let errorMessage = 'Failed to create portfolio';
            if (axios.isAxiosError(error)) {
                errorMessage = error.response?.data?.detail || errorMessage;
            }
            set({ error: errorMessage, isLoading: false });
            throw error;
        }
    },

    addTickerToPortfolio: async (portfolioId: string, ticker: string) => {
        set({ isLoading: true, error: null });
        try {
            // Backend returns MessageResponse, not the new PortfolioItem object
            await api.post(`/api/portfolios/${portfolioId}/items`, { ticker });
            // Refresh the list to get the updated portfolio containing the new item
            await get().fetchPortfolios();
        } catch (error: unknown) {
            let errorMessage = 'Failed to add ticker to portfolio';
            if (axios.isAxiosError(error)) {
                errorMessage = error.response?.data?.detail || errorMessage;
            }
            set({ error: errorMessage, isLoading: false });
            throw error;
        }
    },

    removeTicker: async (portfolioId: string, ticker: string) => {
        set({ isLoading: true, error: null });
        try {
            // Backend expects ticker as path parameter, not itemId (UUID)
            await api.delete(`/api/portfolios/${portfolioId}/items/${ticker}`);
            // Switching to authoritative refresh for consistency with other mutations
            await get().fetchPortfolios();
        } catch (error: unknown) {
            let errorMessage = 'Failed to remove ticker from portfolio';
            if (axios.isAxiosError(error)) {
                errorMessage = error.response?.data?.detail || errorMessage;
            }
            set({ error: errorMessage, isLoading: false });
            throw error;
        }
    }
}));
