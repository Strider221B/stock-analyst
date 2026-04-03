import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { StockCard } from '../components/portfolios/StockCard';
import { MemoryRouter } from 'react-router-dom';
import userEvent from '@testing-library/user-event';

// Define mocks early
const mockFetchPriceHistory = vi.fn();
const mockRemoveTicker = vi.fn();
const mockNavigate = vi.fn();
const mockOnRemove = vi.fn();

// Mock axios globally
vi.mock('axios', () => ({
    default: {
        create: vi.fn(() => ({
            interceptors: { request: { use: vi.fn() }, response: { use: vi.fn() } },
            get: vi.fn(() => Promise.resolve({ data: [] })),
            post: vi.fn(() => Promise.resolve({ data: {} })),
            delete: vi.fn(() => Promise.resolve({ data: {} })),
            defaults: { baseURL: 'http://localhost:8000' }
        })),
        post: vi.fn(() => Promise.resolve({ data: {} })),
        get: vi.fn(() => Promise.resolve({ data: {} })),
        isAxiosError: vi.fn(() => false),
    },
}));

vi.mock('../api/axios', () => ({
    default: {
        get: vi.fn(),
        interceptors: { request: { use: vi.fn() }, response: { use: vi.fn() } },
    }
}));

vi.mock('../store/authStore', () => ({
    useAuthStore: Object.assign(
        vi.fn(() => ({ accessToken: 'fake' })),
        { getState: () => ({ accessToken: 'fake' }), setState: vi.fn(), subscribe: vi.fn() }
    )
}));

vi.mock('../store/portfolioStore', () => ({
    usePortfolioStore: vi.fn(() => ({
        priceHistory: {},
        fetchPriceHistory: mockFetchPriceHistory,
        removeTicker: mockRemoveTicker,
    })),
}));

vi.mock('react-router-dom', async (importOriginal) => {
    const actual = await importOriginal<typeof import('react-router-dom')>();
    return {
        ...actual,
        useNavigate: () => mockNavigate,
    };
});

// Mock Recharts
vi.mock('recharts', () => ({
    ResponsiveContainer: ({ children }: any) => <div data-testid="chart-container">{children}</div>,
    LineChart: ({ children }: any) => <div data-testid="line-chart">{children}</div>,
    Line: () => <div data-testid="chart-line" />,
    YAxis: () => null,
    Tooltip: () => null,
}));

describe('StockCard', () => {
    const props = {
        ticker: 'AAPL',
        portfolioName: 'Tech Stocks',
        addedAt: '2023-01-01T00:00:00Z',
        onRemove: mockOnRemove,
    };

    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('renders ticker and labels', () => {
        render(
            <MemoryRouter>
                <StockCard {...props} />
            </MemoryRouter>
        );
        expect(screen.getByText('AAPL')).toBeDefined();
        expect(screen.getByText(/Added on/i)).toBeDefined();
    });

    it('fetches price history on mount if not in cache', async () => {
        render(
            <MemoryRouter>
                <StockCard {...props} />
            </MemoryRouter>
        );
        expect(mockFetchPriceHistory).toHaveBeenCalledWith('AAPL');
    });

    it('calls onRemove when remove button is clicked', async () => {
        const user = userEvent.setup();
        render(
            <MemoryRouter>
                <StockCard {...props} />
            </MemoryRouter>
        );
        
        const removeButton = screen.getByLabelText(/Remove AAPL from Tech Stocks/i);
        await user.click(removeButton);
        
        expect(mockOnRemove).toHaveBeenCalled();
    });

    it('navigates to analyze page when Analyze Stock button is clicked', async () => {
        const user = userEvent.setup();
        render(
            <MemoryRouter>
                <StockCard {...props} />
            </MemoryRouter>
        );
        
        const analyzeButton = screen.getByText('Analyze Stock');
        await user.click(analyzeButton);
        
        expect(mockNavigate).toHaveBeenCalledWith('/analyze/AAPL');
    });

    it('shows empty state when no historical data is returned', async () => {
        const { usePortfolioStore } = await import('../store/portfolioStore');
        (usePortfolioStore as any).mockReturnValue({
            priceHistory: { 'AAPL': [] },
            fetchPriceHistory: vi.fn().mockResolvedValue(true),
            removeTicker: vi.fn(),
        });

        render(
            <MemoryRouter>
                <StockCard {...props} />
            </MemoryRouter>
        );
        
        await waitFor(() => {
            expect(screen.getByText(/No historical data/i)).toBeDefined();
        });
    });

    it('displays price and change percentage when data is available', async () => {
        const { usePortfolioStore } = await import('../store/portfolioStore');
        (usePortfolioStore as any).mockReturnValue({
            priceHistory: { 
                'AAPL': [
                    { date: '2023-01-01', price: 100 },
                    { date: '2023-01-02', price: 110 }
                ] 
            },
            fetchPriceHistory: vi.fn().mockResolvedValue(true),
            removeTicker: vi.fn(),
        });

        render(
            <MemoryRouter>
                <StockCard {...props} />
            </MemoryRouter>
        );
        
        expect(screen.getByText('$110.00')).toBeDefined();
        expect(screen.getByText('+10.00%')).toBeDefined();
    });
});
