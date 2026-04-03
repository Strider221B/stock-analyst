import { useParams, Link } from "react-router-dom";
import { Button } from "../components/ui/button";
import { ChevronLeft, LineChart } from "lucide-react";

export default function Analyze() {
    const { ticker } = useParams<{ ticker: string }>();

    return (
        <div className="container mx-auto p-8 space-y-8 animate-in fade-in duration-500">
            <div className="flex items-center gap-4">
                <Button variant="ghost" size="icon" asChild>
                    <Link to="/dashboard">
                        <ChevronLeft className="h-5 w-5" />
                    </Link>
                </Button>
                <div className="flex items-center gap-2">
                    <LineChart className="h-6 w-6 text-primary" />
                    <h1 className="text-3xl font-black tracking-tighter">
                        Analyze {ticker}
                    </h1>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                <div className="md:col-span-2 space-y-6">
                    <div className="h-[400px] border-2 border-dashed rounded-[3rem] flex flex-col items-center justify-center bg-accent/5 p-12 text-center relative overflow-hidden group">
                        <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                        
                        <div className="relative space-y-6">
                            <div className="flex justify-center gap-4">
                                <div className="h-12 w-12 rounded-2xl bg-primary/10 flex items-center justify-center animate-pulse">
                                    <LineChart className="h-6 w-6 text-primary" />
                                </div>
                            </div>
                            
                            <div className="space-y-2">
                                <h2 className="text-2xl font-black tracking-tighter">AI Analysis in Progress</h2>
                                <p className="text-muted-foreground text-sm max-w-md mx-auto leading-relaxed">
                                    We're initializing Gemini to perform deep technical analysis and sentiment scoring for <span className="font-bold text-foreground">{ticker}</span>.
                                </p>
                            </div>

                            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-4">
                                {[
                                    { label: "Fetching News", delay: "delay-0" },
                                    { label: "Analyzing Trends", delay: "delay-150" },
                                    { label: "Generating Report", delay: "delay-300" }
                                ].map((step) => (
                                    <div key={step.label} className="flex items-center gap-2 px-4 py-2 rounded-xl bg-secondary/50 border border-border/50">
                                        <div className="h-1.5 w-1.5 rounded-full bg-primary animate-ping" />
                                        <span className="text-[10px] font-bold uppercase tracking-wider opacity-70">{step.label}</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>

                <div className="space-y-6">
                    <div className="p-6 rounded-3xl bg-secondary/30 border border-border/50">
                        <h3 className="text-lg font-bold mb-4">Stock Insights</h3>
                        <div className="space-y-4">
                            <div className="flex justify-between items-center text-sm border-b border-border pb-2">
                                <span className="text-muted-foreground">Ticker Symbol</span>
                                <span className="font-bold">{ticker}</span>
                            </div>
                            <div className="flex justify-between items-center text-sm border-b border-border pb-2">
                                <span className="text-muted-foreground">AI Rating</span>
                                <span className="font-bold text-primary">N/A</span>
                            </div>
                            <div className="flex justify-between items-center text-sm border-b border-border pb-2">
                                <span className="text-muted-foreground">Sentiment</span>
                                <span className="font-bold">Neutral</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
