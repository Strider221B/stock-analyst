// /frontend/src/components/portfolios/PortfolioSection.tsx
import { 
    Card, 
    CardHeader, 
    CardTitle, 
    CardContent, 
    CardDescription 
} from "../ui/card";
import { Button } from "../ui/button";
import { Plus, Trash2, LineChart } from "lucide-react";
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
import { AddTickerModal } from "./AddTickerModal";
import { useState } from "react";
import { formatAccountType } from "../../lib/utils";
import { toast } from "sonner";


interface PortfolioSectionProps {
    portfolio: Portfolio;
}

interface TickerCardProps {
    item: Portfolio["items"][0];
    portfolioName: string;
    onRemove: (ticker: string) => void;
}

function TickerCard({ item, portfolioName, onRemove }: TickerCardProps) {
    return (
        <Card className="group relative transition-all hover:shadow-lg hover:border-primary/20">
            <CardHeader className="pb-3">
                <div className="flex justify-between items-start">
                    <div className="space-y-1">
                        <CardTitle className="text-xl font-bold tracking-tight">{item.ticker}</CardTitle>
                        <CardDescription className="text-xs">Added on {new Date(item.added_at).toLocaleDateString()}</CardDescription>
                    </div>
                     <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        <Button 
                            variant="ghost" 
                            size="icon" 
                            aria-label={`Remove ${item.ticker} from ${portfolioName}`}
                            className="h-8 w-8 text-muted-foreground hover:text-destructive hover:bg-destructive/10"
                            onClick={() => onRemove(item.ticker)}
                        >
                            <Trash2 className="h-4 w-4" />
                        </Button>
                    </div>
                </div>
            </CardHeader>
            <CardContent>
                <div className="flex justify-between items-end">
                    <Button 
                        variant="outline" 
                        size="sm" 
                        className="w-full gap-2 text-xs font-bold py-1 h-8 opacity-50 cursor-not-allowed"
                        disabled
                        title="Coming soon"
                    >
                        <LineChart className="h-3 w-3" />
                        Analyze Stock
                    </Button>
                </div>
            </CardContent>
        </Card>
    );
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
                        <TickerCard 
                            key={`${portfolio.id}-${item.ticker}`}
                            item={item}
                            portfolioName={portfolio.name}
                            onRemove={setTickerToRemove}
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
