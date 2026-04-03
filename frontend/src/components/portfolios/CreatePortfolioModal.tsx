// /frontend/src/components/portfolios/CreatePortfolioModal.tsx
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { 
    Dialog, 
    DialogContent, 
    DialogHeader, 
    DialogTitle, 
    DialogDescription,
    DialogFooter
} from "../ui/dialog";
import { 
    Form, 
    FormControl, 
    FormField, 
    FormItem, 
    FormLabel, 
    FormMessage 
} from "../ui/form";
import { 
    Select, 
    SelectContent, 
    SelectItem, 
    SelectTrigger, 
    SelectValue 
} from "../ui/select";
import { Input } from "../ui/input";
import { Button } from "../ui/button";
import { usePortfolioStore } from "../../store/portfolioStore";
import type { AccountType } from "../../store/portfolioStore";
import { useState, useEffect } from "react";
import axios from "axios";

const formSchema = z.object({
  name: z.string().min(1, "Portfolio name is required").max(50),
  account_type: z.enum(["DOMESTIC", "INTERNATIONAL", "EMPLOYEE_EQUITY"]),
});

interface CreatePortfolioModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function CreatePortfolioModal({ open, onOpenChange }: CreatePortfolioModalProps) {
  const { createPortfolio } = usePortfolioStore();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: "",
      account_type: "DOMESTIC",
    },
  });
  const { reset } = form;

  useEffect(() => {
    if (open) {
      setSubmitError(null);
      reset();
    }
  }, [open, reset]);

  async function onSubmit(values: z.infer<typeof formSchema>) {
    setIsSubmitting(true);
    setSubmitError(null);
    try {
      await createPortfolio(values.name, values.account_type as AccountType);
      form.reset();
      onOpenChange(false);
    } catch (error: unknown) {
      console.error(error);
      if (axios.isAxiosError(error)) {
        setSubmitError(error.response?.data?.detail || 'Failed to create portfolio');
      } else {
        setSubmitError('An unexpected error occurred');
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Create Portfolio</DialogTitle>
          <DialogDescription>
            Create a new watchlist or portfolio to track your stocks.
          </DialogDescription>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Portfolio Name</FormLabel>
                  <FormControl>
                    <Input placeholder="Tech Stocks 2024" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="account_type"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Account Type</FormLabel>
                  <Select onValueChange={field.onChange} defaultValue={field.value}>
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Select an account type" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      <SelectItem value="DOMESTIC">Domestic</SelectItem>
                      <SelectItem value="INTERNATIONAL">International</SelectItem>
                      <SelectItem value="EMPLOYEE_EQUITY">Employee Equity</SelectItem>
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
               )}
            />
            {submitError && <p aria-live="polite" className="text-sm font-medium text-destructive">{submitError}</p>}
            <DialogFooter>
              <Button type="submit" disabled={isSubmitting}>
                {isSubmitting ? "Creating..." : "Create Portfolio"}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
