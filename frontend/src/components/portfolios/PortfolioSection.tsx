// /frontend/src/components/portfolios/PortfolioSection.tsx
import { Plus } from "lucide-react";
import type { Portfolio } from "../../store/portfolioStore";
import { usePortfolioStore } from "../../store/portfolioStore";
import { 
    AlertDialog,
    AlertDialogAction,
    AlertDialogCancel,
    AlertDialogContent,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogTitle,
} from "../ui/alert-dialog";
import { Badge } from "../ui/badge";
import { Button } from "../ui/button";
import { AddTickerModal } from "./AddTickerModal";
import { StockCard } from "./StockCard";
import { useState } from "react";
import { formatAccountType } from "../../lib/utils";
import { toast } from "sonner";


interface PortfolioSectionProps {
    portfolio: Portfolio;
}

export function PortfolioSection({ portfolio }: PortfolioSectionProps) {
    const [isAddModalOpen, setIsAddModalOpen] = useState(false);
    const [tickerToRemove, setTickerToRemove] = useState<string | null>(null);
    const { removeTicker } = usePortfolioStore();

    const handleRemoveTicker = async () => {
        if (!tickerToRemove) return;
        try {
            await removeTicker(portfolio.id, tickerToRemove);
            setTickerToRemove(null);
            toast.success(`Removed ${tickerToRemove} from ${portfolio.name}`);
        } catch (error) {
            console.error("Failed to remove ticker:", error);
            toast.error("Failed to remove ticker. Please try again.");
            setTickerToRemove(null);
        }
    };

    return (
        <section className="space-y-6">
            <div className="flex items-center justify-between border-b pb-4">
                <div className="flex items-center gap-3">
                    <h2 className="text-2xl font-bold tracking-tight">{portfolio.name}</h2>
                    <Badge variant="outline">
                        {formatAccountType(portfolio.account_type)}
                    </Badge>
                </div>
                <Button onClick={() => setIsAddModalOpen(true)} size="sm" variant="secondary" className="gap-2">
                    <Plus className="h-4 w-4" />
                    Add Ticker
                </Button>
            </div>

            {portfolio.items.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-12 px-4 border-2 border-dashed rounded-xl bg-accent/20">
                    <p className="text-muted-foreground text-center">This portfolio is empty.</p>
                    <Button variant="link" onClick={() => setIsAddModalOpen(true)} className="mt-2">
                        Add your first ticker symbol
                    </Button>
                </div>
            ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                    {portfolio.items.map((item) => (
                        <StockCard 
                            key={`${portfolio.id}-${item.ticker}`}
                            ticker={item.ticker}
                            portfolioName={portfolio.name}
                            addedAt={item.added_at}
                            // We can still trigger removeTicker from StockCard
                            // but for confirmation UI we'll use a hack or just pass a callback
                            onRemove={() => setTickerToRemove(item.ticker)}
                        />
                    ))}
                </div>
            )}

            <AddTickerModal 
                portfolioId={portfolio.id}
                portfolioName={portfolio.name}
                open={isAddModalOpen}
                onOpenChange={setIsAddModalOpen}
            />

            <AlertDialog open={!!tickerToRemove} onOpenChange={(open) => !open && setTickerToRemove(null)}>
                <AlertDialogContent>
                    <AlertDialogHeader>
                        <AlertDialogTitle>Are you sure?</AlertDialogTitle>
                        <AlertDialogDescription>
                            This will remove <strong>{tickerToRemove}</strong> from the <strong>{portfolio.name}</strong> watchlist.
                        </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                        <AlertDialogCancel>Cancel</AlertDialogCancel>
                        <AlertDialogAction 
                            onClick={handleRemoveTicker}
                            className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                        >
                            Remove
                        </AlertDialogAction>
                    </AlertDialogFooter>
                </AlertDialogContent>
            </AlertDialog>
        </section>
    );
}
