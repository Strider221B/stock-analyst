import { create } from 'zustand';
import api from '../api/axios';
import axios from 'axios';

export type AccountType = 'DOMESTIC' | 'INTERNATIONAL' | 'EMPLOYEE_EQUITY';

export interface PortfolioItem {
    id: string;
    ticker: string;
    added_at: string;
}

/** 
 * Represents a single day of historical price data.
 */
export interface PricePoint {
    /** ISO 8601 formatted date string (YYYY-MM-DD) */
    date: string;
    /** Closing price for the given date */
    price: number;
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
    priceHistory: Record<string, PricePoint[]>;
    fetchPriceHistory: (ticker: string) => Promise<boolean>;
}

export const usePortfolioStore = create<PortfolioState>((set, get) => ({
    portfolios: [],
    isLoading: false,
    error: null,

    /**
     * Fetches all portfolios for the current user.
     */
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

    /**
     * Creates a new portfolio.
     */
    createPortfolio: async (name: string, account_type: AccountType) => {
        set({ error: null });
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
            set({ error: errorMessage });
            throw error;
        }
    },

    /**
     * Adds a stock ticker to a specific portfolio.
     */
    addTickerToPortfolio: async (portfolioId: string, ticker: string) => {
        set({ error: null });
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
            set({ error: errorMessage });
            throw error;
        }
    },

    /**
     * Removes a stock ticker from a portfolio.
     */
    removeTicker: async (portfolioId: string, ticker: string) => {
        set({ error: null });
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
            set({ error: errorMessage });
            throw error;
        }
    },

    priceHistory: {},
    /**
     * Fetches and caches historical price data for a ticker.
     * @returns boolean indicating success or failure.
     */
    fetchPriceHistory: async (ticker: string): Promise<boolean> => {
        // Return true if already in cache
        if (get().priceHistory[ticker]) return true;

        try {
            const response = await api.get<PricePoint[]>(`/api/marketdata/${ticker}/history`);
            set((state) => ({
                priceHistory: {
                    ...state.priceHistory,
                    [ticker]: response.data
                }
            }));
            return true;
        } catch (error: unknown) {
            console.error(`Failed to fetch history for ${ticker}:`, error);
            // Don't set global error here to avoid blocking UI; component handles its own error
            return false;
        }
    }
}));
