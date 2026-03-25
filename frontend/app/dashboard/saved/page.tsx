"use client";

import Link from "next/link";
import { ArrowLeft, Bookmark } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function SavedSuppliersPage() {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
      <header className="border-b border-gray-200 bg-white dark:border-gray-800 dark:bg-gray-950">
        <div className="mx-auto flex max-w-6xl items-center gap-4 px-4 py-4">
          <Link href="/dashboard"><Button variant="ghost" size="icon"><ArrowLeft className="h-5 w-5" /></Button></Link>
          <h1 className="font-display text-xl font-bold">Saved Suppliers</h1>
        </div>
      </header>

      <div className="mx-auto max-w-6xl px-4 py-12 text-center">
        <Bookmark className="mx-auto h-12 w-12 text-gray-300 dark:text-gray-600" />
        <h2 className="mt-4 font-display text-lg font-semibold text-gray-900 dark:text-white">No saved suppliers yet</h2>
        <p className="mt-2 text-sm text-gray-500">Search for suppliers and bookmark them to see them here</p>
        <Link href="/search"><Button className="mt-4">Search Suppliers</Button></Link>
      </div>
    </div>
  );
}
