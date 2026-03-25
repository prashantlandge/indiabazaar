"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import {
  ArrowLeft, MapPin, Star, Globe, Phone, Mail, Building2,
  Calendar, Users, BadgeDollarSign, ShieldCheck, ExternalLink,
  Bookmark
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { TrustScore, TrustBreakdown } from "@/components/supplier/TrustScore";
import { api, type Supplier, type MatchedProduct } from "@/lib/api";
import { formatPrice } from "@/lib/utils";

export default function SupplierProfilePage() {
  const params = useParams();
  const slug = params.slug as string;
  const [supplier, setSupplier] = useState<Supplier | null>(null);
  const [products, setProducts] = useState<MatchedProduct[]>([]);
  const [similar, setSimilar] = useState<Supplier[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [s, p, sim] = await Promise.all([
          api.getSupplier(slug),
          api.getSupplierProducts(slug),
          api.getSimilarSuppliers(slug).catch(() => []),
        ]);
        setSupplier(s);
        setProducts(p);
        setSimilar(sim);
        api.trackView(slug).catch(() => {});
      } catch (err) {
        console.error("Failed to load supplier:", err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [slug]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
        <div className="mx-auto max-w-6xl px-4 py-8">
          <Skeleton className="h-8 w-64 mb-4" />
          <Skeleton className="h-48 w-full rounded-lg mb-4" />
          <Skeleton className="h-64 w-full rounded-lg" />
        </div>
      </div>
    );
  }

  if (!supplier) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <h2 className="text-lg font-semibold">Supplier not found</h2>
          <Link href="/suppliers"><Button variant="link">Back to suppliers</Button></Link>
        </div>
      </div>
    );
  }

  const trustBreakdown = {
    gst_verified: supplier.gst_verified,
    indiamart_verified: supplier.indiamart_verified,
    rating: supplier.rating,
    num_reviews: supplier.num_reviews,
    certifications: supplier.certifications || [],
    trust_seal: supplier.trust_seal,
    has_website: !!supplier.website,
    year_established: supplier.year_established,
    years_in_business: supplier.year_established ? new Date().getFullYear() - supplier.year_established : 0,
    product_count: products.length,
    profile_completeness: supplier.profile_completeness,
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
      {/* Header */}
      <header className="border-b border-gray-200 bg-white dark:border-gray-800 dark:bg-gray-950">
        <div className="mx-auto max-w-6xl px-4 py-4">
          <Link href="/suppliers" className="mb-4 inline-flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700">
            <ArrowLeft className="h-4 w-4" /> Back to suppliers
          </Link>
        </div>
      </header>

      <div className="mx-auto max-w-6xl px-4 py-6">
        <div className="flex gap-6">
          {/* Main content */}
          <div className="flex-1 min-w-0 space-y-6">
            {/* Profile header */}
            <Card>
              <CardContent className="p-6">
                <div className="flex items-start gap-4">
                  <div className="flex h-16 w-16 flex-shrink-0 items-center justify-center rounded-xl bg-brand-50 text-2xl font-bold text-brand-700 dark:bg-brand-950">
                    {supplier.company_name.charAt(0)}
                  </div>
                  <div className="flex-1">
                    <h1 className="font-display text-2xl font-bold text-gray-900 dark:text-white">
                      {supplier.company_name}
                    </h1>
                    <div className="mt-1 flex flex-wrap items-center gap-3 text-sm text-gray-500">
                      {supplier.city && (
                        <span className="flex items-center gap-1">
                          <MapPin className="h-4 w-4" />
                          {supplier.city}{supplier.state ? `, ${supplier.state}` : ""}
                        </span>
                      )}
                      {supplier.rating && (
                        <span className="flex items-center gap-1">
                          <Star className="h-4 w-4 fill-amber-400 text-amber-400" />
                          {supplier.rating} ({supplier.num_reviews} reviews)
                        </span>
                      )}
                    </div>
                    <div className="mt-3 flex flex-wrap gap-1.5">
                      {supplier.gst_verified && <Badge variant="success">GST Verified</Badge>}
                      {supplier.indiamart_verified && <Badge variant="success">Platform Verified</Badge>}
                      {supplier.trust_seal && <Badge variant="trust">Trust Seal</Badge>}
                      {supplier.nature_of_business && <Badge variant="secondary">{supplier.nature_of_business}</Badge>}
                      {supplier.certifications?.map((c) => (
                        <Badge key={c} variant="trust">{c}</Badge>
                      ))}
                    </div>
                  </div>
                  <TrustScore score={supplier.trust_score} size="lg" />
                </div>
              </CardContent>
            </Card>

            {/* Trust breakdown */}
            <Card>
              <CardContent className="p-6">
                <TrustBreakdown breakdown={trustBreakdown} />
              </CardContent>
            </Card>

            {/* About */}
            <Card>
              <CardHeader>
                <CardTitle>About</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  {supplier.year_established && (
                    <div className="flex items-center gap-2">
                      <Calendar className="h-4 w-4 text-gray-400" />
                      <span>Established {supplier.year_established}</span>
                    </div>
                  )}
                  {supplier.annual_turnover && (
                    <div className="flex items-center gap-2">
                      <BadgeDollarSign className="h-4 w-4 text-gray-400" />
                      <span>Turnover: {supplier.annual_turnover}</span>
                    </div>
                  )}
                  {supplier.num_employees && (
                    <div className="flex items-center gap-2">
                      <Users className="h-4 w-4 text-gray-400" />
                      <span>{supplier.num_employees} employees</span>
                    </div>
                  )}
                  {supplier.nature_of_business && (
                    <div className="flex items-center gap-2">
                      <Building2 className="h-4 w-4 text-gray-400" />
                      <span>{supplier.nature_of_business}</span>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Products */}
            {products.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>Products ({products.length})</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid gap-3 sm:grid-cols-2">
                    {products.map((product) => (
                      <div
                        key={product.id}
                        className="rounded-lg border border-gray-100 p-3 transition-colors hover:bg-gray-50 dark:border-gray-800 dark:hover:bg-gray-800/50"
                      >
                        <h4 className="font-medium text-gray-900 dark:text-white">{product.name}</h4>
                        {product.description && (
                          <p className="mt-1 text-xs text-gray-500 line-clamp-2">{product.description}</p>
                        )}
                        <div className="mt-2 flex items-center justify-between">
                          <span className="text-sm font-medium text-brand-600">
                            {formatPrice(product.price_min, product.price_max, product.price_unit)}
                          </span>
                          {product.min_order_qty && (
                            <span className="text-xs text-gray-400">MOQ: {product.min_order_qty}</span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Similar suppliers */}
            {similar.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>Similar Suppliers</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex gap-3 overflow-x-auto pb-2">
                    {similar.map((s) => (
                      <Link
                        key={s.id}
                        href={`/suppliers/${s.slug}`}
                        className="flex-shrink-0 rounded-lg border border-gray-100 p-3 transition-colors hover:bg-gray-50 dark:border-gray-800 dark:hover:bg-gray-800/50"
                        style={{ minWidth: "200px" }}
                      >
                        <h4 className="text-sm font-medium text-gray-900 dark:text-white">{s.company_name}</h4>
                        <p className="mt-0.5 text-xs text-gray-500">{s.city}</p>
                        <TrustScore score={s.trust_score} size="sm" showLabel={false} />
                      </Link>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Sticky sidebar */}
          <aside className="hidden w-72 flex-shrink-0 lg:block">
            <div className="sticky top-6 space-y-4">
              <Card>
                <CardContent className="p-5 text-center">
                  <TrustScore score={supplier.trust_score} size="lg" />
                  <div className="mt-4 space-y-2">
                    <Link href={`/rfq?supplier=${supplier.slug}`}>
                      <Button className="w-full" size="lg">Send RFQ</Button>
                    </Link>
                    <Button variant="outline" className="w-full">
                      <Bookmark className="mr-2 h-4 w-4" />
                      Save Supplier
                    </Button>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-5 space-y-3 text-sm">
                  {supplier.contact_person && (
                    <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                      <Users className="h-4 w-4 text-gray-400" />
                      {supplier.contact_person}
                    </div>
                  )}
                  {(supplier.city || supplier.state) && (
                    <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                      <MapPin className="h-4 w-4 text-gray-400" />
                      {[supplier.city, supplier.state].filter(Boolean).join(", ")}
                    </div>
                  )}
                  {supplier.website && (
                    <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                      <Globe className="h-4 w-4 text-gray-400" />
                      <span className="truncate">{supplier.website}</span>
                    </div>
                  )}
                  {supplier.member_since && (
                    <p className="text-xs text-gray-400">Member since {supplier.member_since}</p>
                  )}
                </CardContent>
              </Card>
            </div>
          </aside>
        </div>
      </div>
    </div>
  );
}
