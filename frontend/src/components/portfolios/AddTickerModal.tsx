// /frontend/src/components/portfolios/AddTickerModal.tsx
import { 
    Dialog, 
    DialogContent, 
    DialogHeader, 
    DialogTitle, 
    DialogDescription,
    DialogFooter
} from "../ui/dialog";
import { Input } from "../ui/input";
import { Button } from "../ui/button";
import { usePortfolioStore } from "../../store/portfolioStore";
import { useState, useEffect, useCallback } from "react";
import { Label } from "../ui/label";
import axios from "axios";

interface AddTickerModalProps {
  portfolioId: string;
  portfolioName: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function AddTickerModal({ portfolioId, portfolioName, open, onOpenChange }: AddTickerModalProps) {
  const { addTickerToPortfolio } = usePortfolioStore();
  const [ticker, setTicker] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAddTicker = useCallback(async () => {
    if (!ticker.trim()) {
      setError("Symbol is required");
      return;
    }
    setError(null);
    setIsSubmitting(true);
    try {
      await addTickerToPortfolio(portfolioId, ticker.trim().toUpperCase());
      onOpenChange(false);
    } catch (e: unknown) {
      console.error(e);
      if (axios.isAxiosError(e)) {
        setError(e.response?.data?.detail || "Failed to add ticker. Please check the symbol.");
      } else {
        setError("An unexpected error occurred.");
      }
    } finally {
      setIsSubmitting(false);
    }
  }, [ticker, portfolioId, addTickerToPortfolio, onOpenChange]);

  useEffect(() => {
    if (open) {
      setTicker("");
      setError(null);
    }
  }, [open]);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Add to {portfolioName}</DialogTitle>
          <DialogDescription>
            Enter the ticker symbol (e.g., TSLA, RELIANCE.NS).
          </DialogDescription>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="grid gap-2">
            <Label htmlFor="ticker">Stock Symbol</Label>
            <Input
              id="ticker"
              value={ticker}
              autoFocus
              onChange={(e) => setTicker(e.target.value.toUpperCase())}
              placeholder="e.g. AAPL or RELIANCE.NS"
              onKeyDown={(e) => e.key === "Enter" && handleAddTicker()}
            />
            {error && <p aria-live="polite" className="text-sm text-destructive font-medium">{error}</p>}
          </div>
        </div>
        <DialogFooter>
          <Button onClick={handleAddTicker} disabled={isSubmitting}>
            {isSubmitting ? "Adding..." : "Add Symbol"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
