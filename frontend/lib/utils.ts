import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatPrice(min: number | null, max: number | null, unit: string | null): string {
  if (!min && !max) return "Price on request";
  const fmt = (n: number) =>
    new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(n);

  if (min && max && min !== max) {
    return `${fmt(min)} - ${fmt(max)}${unit ? ` ${unit}` : ""}`;
  }
  return `${fmt(min || max!)}${unit ? ` ${unit}` : ""}`;
}

export function truncate(str: string, length: number): string {
  if (str.length <= length) return str;
  return str.slice(0, length) + "...";
}
