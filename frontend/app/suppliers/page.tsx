"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ArrowLeft, MapPin, Star } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { TrustScore } from "@/components/supplier/TrustScore";
import { api, type Supplier } from "@/lib/api";

export default function SuppliersPage() {
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        const res = await api.listSuppliers({ page });
        setSuppliers(res.suppliers);
        setTotal(res.total);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [page]);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
      <header className="border-b border-gray-200 bg-white dark:border-gray-800 dark:bg-gray-950">
        <div className="mx-auto flex max-w-6xl items-center gap-4 px-4 py-4">
          <Link href="/"><Button variant="ghost" size="icon"><ArrowLeft className="h-5 w-5" /></Button></Link>
          <h1 className="font-display text-xl font-bold">Supplier Directory</h1>
        </div>
      </header>

      <div className="mx-auto max-w-6xl px-4 py-6">
        <p className="mb-4 text-sm text-gray-500">{total} suppliers</p>

        {loading ? (
          <div className="space-y-3">{[1,2,3,4].map(i => <Skeleton key={i} className="h-24 w-full rounded-lg" />)}</div>
        ) : (
          <div className="space-y-3">
            {suppliers.map((s) => (
              <Card key={s.id} className="p-4">
                <div className="flex items-start justify-between">
                  <div>
                    <Link href={`/suppliers/${s.slug}`} className="font-semibold text-gray-900 hover:text-brand-600 dark:text-white">
                      {s.company_name}
                    </Link>
                    <div className="mt-1 flex items-center gap-3 text-sm text-gray-500">
                      {s.city && <span className="flex items-center gap-1"><MapPin className="h-3.5 w-3.5" />{s.city}</span>}
                      {s.rating && <span className="flex items-center gap-1"><Star className="h-3.5 w-3.5 fill-amber-400 text-amber-400" />{s.rating}</span>}
                      {s.nature_of_business && <Badge variant="secondary" className="text-xs">{s.nature_of_business}</Badge>}
                    </div>
                  </div>
                  <TrustScore score={s.trust_score} size="sm" />
                </div>
              </Card>
            ))}
          </div>
        )}

        {total > 20 && (
          <div className="mt-6 flex justify-center gap-2">
            <Button variant="outline" size="sm" disabled={page <= 1} onClick={() => setPage(p => p - 1)}>Previous</Button>
            <span className="text-sm text-gray-500 self-center">Page {page}</span>
            <Button variant="outline" size="sm" disabled={page >= Math.ceil(total / 20)} onClick={() => setPage(p => p + 1)}>Next</Button>
          </div>
        )}
      </div>
    </div>
  );
}
