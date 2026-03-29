import { create } from 'zustand';
import api from '../api/axios';

export interface PortfolioItem {
    id: string;
    ticker: string;
    added_at: string;
}

export interface Portfolio {
    id: string;
    name: string;
    account_type: string;
    items: PortfolioItem[];
    created_at: string;
    updated_at: string;
}

interface PortfolioState {
    portfolios: Portfolio[];
    isLoading: boolean;
    error: string | null;

    fetchPortfolios: () => Promise<void>;
    createPortfolio: (name: string, account_type: string) => Promise<void>;
    addTickerToPortfolio: (portfolioId: string, ticker: string) => Promise<void>;
    removeTicker: (portfolioId: string, itemId: string) => Promise<void>;
}

export const usePortfolioStore = create<PortfolioState>((set) => ({
    portfolios: [],
    isLoading: false,
    error: null,

    fetchPortfolios: async () => {
        set({ isLoading: true, error: null });
        try {
            const response = await api.get<Portfolio[]>('/api/portfolios');
            set({ portfolios: response.data, isLoading: false });
        } catch (error: any) {
            set({ 
                error: error.response?.data?.detail || 'Failed to fetch portfolios', 
                isLoading: false 
            });
        }
    },

    createPortfolio: async (name: string, account_type: string) => {
        set({ isLoading: true, error: null });
        try {
            const response = await api.post<Portfolio>('/api/portfolios', { name, account_type });
            set((state) => ({
                portfolios: [...state.portfolios, response.data],
                isLoading: false
            }));
        } catch (error: any) {
            set({ 
                error: error.response?.data?.detail || 'Failed to create portfolio', 
                isLoading: false 
            });
            throw error;
        }
    },

    addTickerToPortfolio: async (portfolioId: string, ticker: string) => {
        set({ isLoading: true, error: null });
        try {
            const response = await api.post<PortfolioItem>(`/api/portfolios/${portfolioId}/items`, { ticker });
            set((state) => ({
                portfolios: state.portfolios.map(portfolio => {
                    if (portfolio.id === portfolioId) {
                        return {
                            ...portfolio,
                            items: [...portfolio.items, response.data]
                        };
                    }
                    return portfolio;
                }),
                isLoading: false
            }));
        } catch (error: any) {
            set({ 
                error: error.response?.data?.detail || 'Failed to add ticker to portfolio', 
                isLoading: false 
            });
            throw error;
        }
    },

    removeTicker: async (portfolioId: string, itemId: string) => {
        set({ isLoading: true, error: null });
        try {
            await api.delete(`/api/portfolios/${portfolioId}/items/${itemId}`);
            set((state) => ({
                portfolios: state.portfolios.map(portfolio => {
                    if (portfolio.id === portfolioId) {
                        return {
                            ...portfolio,
                            items: portfolio.items.filter(item => item.id !== itemId)
                        };
                    }
                    return portfolio;
                }),
                isLoading: false
            }));
        } catch (error: any) {
            set({ 
                error: error.response?.data?.detail || 'Failed to remove ticker from portfolio', 
                isLoading: false 
            });
            throw error;
        }
    }
}));
