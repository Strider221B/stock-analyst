import { useEffect, useState } from "react";
import { 
    Card, 
    CardContent, 
    CardHeader, 
    CardTitle, 
    CardDescription 
} from "../ui/card";
import { Button } from "../ui/button";
import { Trash2, LineChart, Loader2 } from "lucide-react";
import { 
    LineChart as RechartsLineChart, 
    Line, 
    ResponsiveContainer, 
    Tooltip, 
    YAxis 
} from "recharts";
import { usePortfolioStore } from "../../store/portfolioStore";
import { useNavigate } from "react-router-dom";

interface StockCardProps {
    ticker: string;
    portfolioName: string;
    addedAt: string;
    onRemove: () => void; // Required for consistency
}

export function StockCard({ ticker, portfolioName, addedAt, onRemove }: StockCardProps) {
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const { priceHistory, fetchPriceHistory } = usePortfolioStore();
    const navigate = useNavigate();

    const history = priceHistory[ticker] || [];

    useEffect(() => {
        const loadData = async () => {
            if (history.length > 0) return;
            
            setIsLoading(true);
            const success = await fetchPriceHistory(ticker);
            if (!success) {
                setError("Failed to load chart");
            } else {
                setError(null);
            }
            setIsLoading(false);
        };

        loadData();
    }, [ticker, fetchPriceHistory, history.length]);

    const handleAnalyze = () => {
        navigate(`/analyze/${ticker}`);
    };

    const latestPrice = history.length > 0 ? history[history.length - 1].price : null;
    const previousPrice = history.length > 1 ? history[history.length - 2].price : null;
    const priceChange = latestPrice !== null && previousPrice !== null ? latestPrice - previousPrice : 0;
    const priceChangePercent = latestPrice !== null && previousPrice !== null ? (priceChange / previousPrice) * 100 : 0;
    const isPositive = priceChange >= 0;

    return (
        <Card className="group relative transition-all duration-300 hover:shadow-xl hover:border-primary/30 bg-card/50 backdrop-blur-sm overflow-hidden flex flex-col h-full">
            <CardHeader className="pb-3 space-y-0">
                <div className="flex justify-between items-start">
                    <div className="space-y-1">
                        <CardTitle className="text-2xl font-black tracking-tighter flex items-baseline gap-2">
                            {ticker}
                            {latestPrice && (
                                <div className="flex items-baseline gap-1.5 min-w-0">
                                    <span className="text-sm font-medium text-muted-foreground whitespace-nowrap">
                                        ${latestPrice.toFixed(2)}
                                    </span>
                                    {previousPrice !== null && (
                                        <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded-full ${
                                            isPositive 
                                            ? "text-emerald-500 bg-emerald-500/10" 
                                            : "text-rose-500 bg-rose-500/10"
                                        }`}>
                                            {isPositive ? "+" : ""}{priceChangePercent.toFixed(2)}%
                                        </span>
                                    )}
                                </div>
                            )}
                        </CardTitle>
                        <CardDescription className="text-[10px] uppercase font-bold tracking-widest text-muted-foreground/70">
                            Added on {new Date(addedAt).toLocaleDateString()}
                        </CardDescription>
                    </div>
                    <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-all duration-200">
                        <Button 
                            variant="ghost" 
                            size="icon" 
                            aria-label={`Remove ${ticker} from ${portfolioName}`}
                            className="h-8 w-8 text-muted-foreground hover:text-destructive hover:bg-destructive/10 rounded-full"
                            onClick={(e) => {
                                e.stopPropagation();
                                onRemove();
                            }}
                        >
                            <Trash2 className="h-4 w-4" />
                        </Button>
                    </div>
                </div>
            </CardHeader>
            <CardContent className="flex-grow flex flex-col gap-4">
                <div className="h-24 w-full -mx-2">
                    {isLoading ? (
                        <div className="h-full w-full flex items-center justify-center">
                            <Loader2 className="h-6 w-6 animate-spin text-primary/20" />
                        </div>
                    ) : error ? (
                        <div className="h-full w-full flex items-center justify-center text-[10px] text-muted-foreground font-medium uppercase tracking-tighter">
                            {error}
                        </div>
                    ) : history.length === 0 ? (
                        <div className="h-full w-full flex items-center justify-center text-[10px] text-muted-foreground font-medium uppercase tracking-tighter">
                            No historical data
                        </div>
                    ) : (
                        <ResponsiveContainer width="100%" height="100%">
                            <RechartsLineChart data={history}>
                                <YAxis hide domain={['auto', 'auto']} />
                                <Tooltip 
                                    content={({ active, payload }) => {
                                        if (active && payload && payload.length) {
                                            return (
                                                <div className="bg-background/95 backdrop-blur-md border border-border shadow-2xl rounded-lg p-2 text-xs font-bold animate-in fade-in zoom-in duration-200">
                                                    <p className="text-muted-foreground mb-0.5">{payload[0].payload.date}</p>
                                                    <p className="text-primary">${(payload[0].value as number).toFixed(2)}</p>
                                                </div>
                                            );
                                        }
                                        return null;
                                    }}
                                />
                                <Line 
                                    type="monotone" 
                                    dataKey="price" 
                                    stroke={isPositive ? "#10b981" : "#ef4444"} 
                                    strokeWidth={2.5} 
                                    dot={false}
                                    activeDot={{ r: 4, strokeWidth: 0, fill: isPositive ? "#10b981" : "#ef4444" }}
                                />
                            </RechartsLineChart>
                        </ResponsiveContainer>
                    )}
                </div>
                
                <div className="mt-auto">
                    <Button 
                        variant="secondary" 
                        size="sm" 
                        className="w-full gap-2 text-xs font-bold py-1 h-9 bg-primary/5 hover:bg-primary/10 border-transparent hover:border-primary/20 transition-all duration-300"
                        onClick={handleAnalyze}
                    >
                        <LineChart className="h-3.5 w-3.5" />
                        Analyze Stock
                    </Button>
                </div>
            </CardContent>
        </Card>
    );
}
