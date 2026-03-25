"use client";

import Link from "next/link";
import {
  Package, Factory, Cpu, FlaskConical, Shirt, Utensils,
  HardHat, Boxes, Car, Leaf, Pill, Gem, LogIn
} from "lucide-react";
import { IntelligentSearchBar } from "@/components/search/IntelligentSearchBar";
import { Button } from "@/components/ui/button";

const CATEGORIES = [
  { name: "Raw Materials", icon: Gem },
  { name: "Machinery", icon: Factory },
  { name: "Electronics", icon: Cpu },
  { name: "Chemicals", icon: FlaskConical },
  { name: "Textiles", icon: Shirt },
  { name: "Food & Beverages", icon: Utensils },
  { name: "Construction", icon: HardHat },
  { name: "Packaging", icon: Boxes },
  { name: "Automotive", icon: Car },
  { name: "Agriculture", icon: Leaf },
  { name: "Pharmaceuticals", icon: Pill },
  { name: "Consumer Goods", icon: Package },
];

const POPULAR_SEARCHES = [
  "HDPE pellets",
  "stainless steel pipes",
  "corrugated boxes",
  "industrial valves",
  "transformer oil",
  "cotton fabric",
  "PVC fittings",
  "chemical reagents",
];

export default function HomePage() {
  return (
    <div className="min-h-screen bg-white dark:bg-gray-950">
      {/* Navbar */}
      <nav className="border-b border-gray-100 dark:border-gray-800">
        <div className="mx-auto flex h-14 max-w-7xl items-center justify-between px-4">
          <Link href="/" className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-500 text-sm font-bold text-white">
              TR
            </div>
            <span className="font-display text-lg font-bold text-gray-900 dark:text-white">
              TradeRadar
            </span>
          </Link>
          <div className="flex items-center gap-3">
            <Link href="/suppliers">
              <Button variant="ghost" size="sm">Suppliers</Button>
            </Link>
            <Link href="/rfq">
              <Button variant="ghost" size="sm">Post RFQ</Button>
            </Link>
            <Link href="/admin">
              <Button variant="ghost" size="sm">Admin</Button>
            </Link>
            <Link href="/dashboard">
              <Button variant="outline" size="sm">
                <LogIn className="mr-1.5 h-3.5 w-3.5" />
                Login
              </Button>
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-brand-50/50 to-white dark:from-brand-950/20 dark:to-gray-950" />
        <div className="relative mx-auto max-w-4xl px-4 pb-16 pt-20 text-center">
          <h1 className="font-display text-4xl font-extrabold tracking-tight text-gray-900 sm:text-5xl dark:text-white">
            Find the right supplier.
            <br />
            <span className="text-brand-500">Describe what you need.</span>
          </h1>
          <p className="mx-auto mt-4 max-w-2xl text-lg text-gray-600 dark:text-gray-400">
            Not keyword search — procurement intelligence. Our AI understands
            quantity, quality, certifications, and location to find your best supplier match.
          </p>

          <div className="mx-auto mt-8 max-w-2xl">
            <IntelligentSearchBar size="hero" autoFocus />
          </div>

          {/* Popular searches */}
          <div className="mt-6 flex flex-wrap items-center justify-center gap-2">
            <span className="text-xs text-gray-500">Popular:</span>
            {POPULAR_SEARCHES.map((q) => (
              <Link
                key={q}
                href={`/search?q=${encodeURIComponent(q)}`}
                className="rounded-full border border-gray-200 bg-white px-3 py-1 text-xs text-gray-600 transition-colors hover:border-brand-300 hover:bg-brand-50 hover:text-brand-700 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-400 dark:hover:border-brand-600"
              >
                {q}
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* Categories */}
      <section className="mx-auto max-w-6xl px-4 pb-16">
        <h2 className="mb-6 text-center font-display text-xl font-semibold text-gray-900 dark:text-white">
          Browse by Industry
        </h2>
        <div className="grid grid-cols-3 gap-3 sm:grid-cols-4 md:grid-cols-6">
          {CATEGORIES.map((cat) => (
            <Link
              key={cat.name}
              href={`/search?q=${encodeURIComponent(cat.name)}`}
              className="flex flex-col items-center gap-2 rounded-xl border border-gray-100 bg-white p-4 transition-all hover:border-brand-200 hover:shadow-card dark:border-gray-800 dark:bg-gray-900 dark:hover:border-brand-700"
            >
              <cat.icon className="h-7 w-7 text-brand-500" />
              <span className="text-center text-xs font-medium text-gray-700 dark:text-gray-300">
                {cat.name}
              </span>
            </Link>
          ))}
        </div>
      </section>

      {/* Trust bar */}
      <section className="border-t border-gray-100 bg-gray-50 py-8 dark:border-gray-800 dark:bg-gray-900">
        <div className="mx-auto flex max-w-4xl flex-wrap items-center justify-center gap-8 text-center">
          <div>
            <div className="font-display text-2xl font-bold text-brand-600">50K+</div>
            <div className="text-sm text-gray-500">Verified Suppliers</div>
          </div>
          <div className="h-8 w-px bg-gray-200 dark:bg-gray-700" />
          <div>
            <div className="font-display text-2xl font-bold text-brand-600">200+</div>
            <div className="text-sm text-gray-500">Categories</div>
          </div>
          <div className="h-8 w-px bg-gray-200 dark:bg-gray-700" />
          <div>
            <div className="font-display text-2xl font-bold text-brand-600">500+</div>
            <div className="text-sm text-gray-500">Cities</div>
          </div>
          <div className="h-8 w-px bg-gray-200 dark:bg-gray-700" />
          <div>
            <div className="font-display text-2xl font-bold text-brand-600">AI-Powered</div>
            <div className="text-sm text-gray-500">Intent Matching</div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-100 py-8 dark:border-gray-800">
        <div className="mx-auto max-w-6xl px-4 text-center text-sm text-gray-500">
          <p>TradeRadar — AI-Powered B2B Supplier Intelligence Platform</p>
        </div>
      </footer>
    </div>
  );
}
