"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { api, type MatchedProduct } from "@/lib/api";
import { formatPrice } from "@/lib/utils";

export default function ProductPage() {
  const params = useParams();
  const slug = params.slug as string;

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
      <header className="border-b border-gray-200 bg-white dark:border-gray-800 dark:bg-gray-950">
        <div className="mx-auto flex max-w-4xl items-center gap-4 px-4 py-4">
          <Link href="/"><Button variant="ghost" size="icon"><ArrowLeft className="h-5 w-5" /></Button></Link>
          <h1 className="font-display text-xl font-bold">Product Details</h1>
        </div>
      </header>

      <div className="mx-auto max-w-4xl px-4 py-8">
        <Card>
          <CardContent className="p-6 text-center">
            <p className="text-gray-500">Product page for: {slug}</p>
            <p className="mt-2 text-sm text-gray-400">Full product details are available on the supplier profile page.</p>
            <Link href="/search"><Button className="mt-4">Search Products</Button></Link>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
