"use client";

import Link from "next/link";
import {
  MapPin, Star, Building2, Calendar, CheckCircle2,
  AlertTriangle, ChevronRight, Bookmark
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { TrustScore } from "@/components/supplier/TrustScore";
import type { SupplierSearchResult } from "@/lib/api";
import { formatPrice } from "@/lib/utils";

interface Props {
  result: SupplierSearchResult;
  position: number;
  onRFQClick?: () => void;
}

export function SupplierCard({ result, position, onRFQClick }: Props) {
  const { supplier, final_score, match_reasons, gap_flags, matched_products, trust_breakdown } = result;

  return (
    <Card className="group overflow-hidden transition-shadow hover:shadow-elevated">
      <div className="p-5">
        {/* Header */}
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-start gap-3">
            <div className="flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-lg bg-brand-50 text-lg font-bold text-brand-700 dark:bg-brand-950 dark:text-brand-300">
              {supplier.company_name.charAt(0)}
            </div>
            <div>
              <Link
                href={`/suppliers/${supplier.slug}`}
                className="text-base font-semibold text-gray-900 hover:text-brand-600 dark:text-gray-100"
              >
                {supplier.company_name}
              </Link>
              <div className="mt-0.5 flex flex-wrap items-center gap-2 text-sm text-gray-500">
                {supplier.rating && (
                  <span className="flex items-center gap-0.5">
                    <Star className="h-3.5 w-3.5 fill-amber-400 text-amber-400" />
                    {supplier.rating} ({supplier.num_reviews})
                  </span>
                )}
                {supplier.city && (
                  <span className="flex items-center gap-0.5">
                    <MapPin className="h-3.5 w-3.5" />
                    {supplier.city}{supplier.state ? `, ${supplier.state}` : ""}
                  </span>
                )}
              </div>
            </div>
          </div>
          <TrustScore score={supplier.trust_score} size="sm" />
        </div>

        {/* Tags row */}
        <div className="mt-3 flex flex-wrap gap-1.5">
          {supplier.nature_of_business && (
            <Badge variant="secondary" className="text-xs">
              <Building2 className="mr-1 h-3 w-3" />
              {supplier.nature_of_business}
            </Badge>
          )}
          {supplier.year_established && (
            <Badge variant="secondary" className="text-xs">
              <Calendar className="mr-1 h-3 w-3" />
              Est. {supplier.year_established}
            </Badge>
          )}
          {supplier.certifications?.map((cert) => (
            <Badge key={cert} variant="trust" className="text-xs">{cert}</Badge>
          ))}
          {supplier.gst_verified && (
            <Badge variant="success" className="text-xs">GST Verified</Badge>
          )}
        </div>

        {/* Matched products */}
        {matched_products.length > 0 && (
          <div className="mt-3 rounded-lg bg-gray-50 p-3 dark:bg-gray-800/50">
            <p className="mb-1.5 text-xs font-medium uppercase tracking-wide text-gray-500">
              Matched Products
            </p>
            <div className="space-y-1">
              {matched_products.slice(0, 3).map((product) => (
                <div key={product.id} className="flex items-center justify-between text-sm">
                  <span className="text-gray-800 dark:text-gray-200">{product.name}</span>
                  <span className="text-xs text-gray-500">
                    {formatPrice(product.price_min, product.price_max, product.price_unit)}
                    {product.min_order_qty && ` (MOQ: ${product.min_order_qty})`}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Match reasons */}
        <div className="mt-3">
          <p className="mb-1 text-xs font-medium uppercase tracking-wide text-gray-500">
            Why This Match
          </p>
          <div className="space-y-0.5">
            {match_reasons.slice(0, 4).map((reason, i) => (
              <div key={i} className="flex items-start gap-1.5 text-sm text-gray-600 dark:text-gray-400">
                <CheckCircle2 className="mt-0.5 h-3.5 w-3.5 flex-shrink-0 text-emerald-500" />
                <span>{reason}</span>
              </div>
            ))}
            {gap_flags.slice(0, 2).map((flag, i) => (
              <div key={i} className="flex items-start gap-1.5 text-sm text-amber-600 dark:text-amber-400">
                <AlertTriangle className="mt-0.5 h-3.5 w-3.5 flex-shrink-0" />
                <span>{flag}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Actions */}
        <div className="mt-4 flex items-center gap-2">
          <Link href={`/suppliers/${supplier.slug}`}>
            <Button variant="outline" size="sm">
              View Profile
              <ChevronRight className="ml-1 h-3.5 w-3.5" />
            </Button>
          </Link>
          <Button size="sm" onClick={onRFQClick}>
            Send RFQ
          </Button>
          <Button variant="ghost" size="icon" className="ml-auto h-8 w-8">
            <Bookmark className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </Card>
  );
}
