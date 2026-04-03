import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"
import type { AccountType } from "../store/portfolioStore"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatAccountType(type: AccountType): string {
  if (!type) return "";
  return type
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(" ");
}
