import { render } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import App from '../App';

// Mock everything that might hit the network
vi.mock('../store/authStore', () => ({
    useAuthStore: vi.fn((selector) => {
        const state = {
            checkAuth: vi.fn(),
            accessToken: null,
            user: null,
            isAuthenticated: false,
            isAuthLoading: false
        };
        return selector ? selector(state) : state;
    }),
}));

vi.mock('../store/portfolioStore', () => ({
    usePortfolioStore: vi.fn(() => ({
        portfolios: [],
        isLoading: false,
        error: null,
        fetchPortfolios: vi.fn(),
    })),
}));

describe('App', () => {
    it('renders without crashing', () => {
        const { container } = render(<App />);
        expect(container).toBeDefined();
    });
});
