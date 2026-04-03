// /frontend/src/pages/Dashboard.tsx
import { useEffect, useState } from 'react';
import { usePortfolioStore } from '../store/portfolioStore';
import { Button } from '../components/ui/button';
import { CreatePortfolioModal } from '../components/portfolios/CreatePortfolioModal';
import { PortfolioSection } from '../components/portfolios/PortfolioSection';
import { Plus } from 'lucide-react';

export default function Dashboard() {
    const portfolios = usePortfolioStore((state) => state.portfolios);
    const fetchPortfolios = usePortfolioStore((state) => state.fetchPortfolios);
    const isLoading = usePortfolioStore((state) => state.isLoading);
    const error = usePortfolioStore((state) => state.error);
    
    const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);

    useEffect(() => {
        fetchPortfolios();
    }, [fetchPortfolios]);

    return (
        <div className="container mx-auto py-8 px-4">
            <div className="flex justify-between items-center mb-8">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
                    <p className="text-muted-foreground mt-1">Manage your stock portfolios and watchlists.</p>
                </div>
                <Button onClick={() => setIsCreateModalOpen(true)} className="gap-2">
                    <Plus className="h-4 w-4" />
                    Create Watchlist
                </Button>
            </div>

            {error && (
                <div className="bg-destructive/10 border border-destructive/20 text-destructive px-4 py-3 rounded-lg mb-8 text-center">
                    <p className="font-medium">Error loading portfolios</p>
                    <p className="text-sm opacity-90">{error}</p>
                    <Button variant="outline" size="sm" onClick={() => fetchPortfolios()} className="mt-2 text-destructive border-destructive/40 hover:bg-destructive/10">
                        Retry
                    </Button>
                </div>
            )}

            {isLoading && portfolios.length === 0 ? (
                <div className="flex items-center justify-center h-64">
                    <div role="status" aria-label="Loading portfolios" className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                </div>
            ) : !error && portfolios.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-64 border-2 border-dashed rounded-lg">
                    <p className="text-muted-foreground">You don't have any portfolios yet.</p>
                    <Button variant="link" onClick={() => setIsCreateModalOpen(true)}>
                        Create your first one
                    </Button>
                </div>
            ) : (
                <div className="space-y-12">
                    {portfolios.map((portfolio) => (
                        <PortfolioSection key={portfolio.id} portfolio={portfolio} />
                    ))}
                </div>
            )}

            <CreatePortfolioModal 
                open={isCreateModalOpen} 
                onOpenChange={setIsCreateModalOpen} 
            />
        </div>
    );
}
