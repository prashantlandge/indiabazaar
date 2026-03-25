"use client";

import { useState } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, Send, CheckCircle2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";

export default function RFQPage() {
  const searchParams = useSearchParams();
  const supplierSlug = searchParams.get("supplier");

  const [form, setForm] = useState({
    product_name: "",
    quantity: "",
    unit: "",
    target_price: "",
    delivery_location: "",
    message: "",
  });
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (!form.product_name || !form.quantity) {
      setError("Product name and quantity are required");
      return;
    }

    try {
      await api.submitRFQ(form);
      setSubmitted(true);
    } catch (err) {
      setError("Failed to submit RFQ. Please try again.");
    }
  };

  if (submitted) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50 dark:bg-gray-950">
        <Card className="max-w-md text-center">
          <CardContent className="p-8">
            <CheckCircle2 className="mx-auto h-12 w-12 text-emerald-500" />
            <h2 className="mt-4 font-display text-xl font-bold text-gray-900 dark:text-white">RFQ Submitted</h2>
            <p className="mt-2 text-sm text-gray-500">Your request for quote has been submitted. Suppliers will be notified.</p>
            <div className="mt-6 flex justify-center gap-3">
              <Link href="/"><Button variant="outline">Back to Home</Button></Link>
              <Button onClick={() => { setSubmitted(false); setForm({ product_name: "", quantity: "", unit: "", target_price: "", delivery_location: "", message: "" }); }}>
                Submit Another
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
      <header className="border-b border-gray-200 bg-white dark:border-gray-800 dark:bg-gray-950">
        <div className="mx-auto flex max-w-2xl items-center gap-4 px-4 py-4">
          <Link href="/"><Button variant="ghost" size="icon"><ArrowLeft className="h-5 w-5" /></Button></Link>
          <h1 className="font-display text-xl font-bold">Submit Request for Quote</h1>
        </div>
      </header>

      <div className="mx-auto max-w-2xl px-4 py-8">
        <Card>
          <CardContent className="p-6">
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="mb-1.5 block text-sm font-medium">Product Name *</label>
                <Input
                  value={form.product_name}
                  onChange={(e) => setForm({ ...form, product_name: e.target.value })}
                  placeholder="e.g., HDPE pellets, food grade"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="mb-1.5 block text-sm font-medium">Quantity *</label>
                  <Input
                    value={form.quantity}
                    onChange={(e) => setForm({ ...form, quantity: e.target.value })}
                    placeholder="e.g., 500"
                  />
                </div>
                <div>
                  <label className="mb-1.5 block text-sm font-medium">Unit</label>
                  <Input
                    value={form.unit}
                    onChange={(e) => setForm({ ...form, unit: e.target.value })}
                    placeholder="e.g., kg, pieces, tons"
                  />
                </div>
              </div>
              <div>
                <label className="mb-1.5 block text-sm font-medium">Target Price</label>
                <Input
                  value={form.target_price}
                  onChange={(e) => setForm({ ...form, target_price: e.target.value })}
                  placeholder="e.g., ₹85-₹95 per kg"
                />
              </div>
              <div>
                <label className="mb-1.5 block text-sm font-medium">Delivery Location</label>
                <Input
                  value={form.delivery_location}
                  onChange={(e) => setForm({ ...form, delivery_location: e.target.value })}
                  placeholder="e.g., Mumbai, Maharashtra"
                />
              </div>
              <div>
                <label className="mb-1.5 block text-sm font-medium">Additional Requirements</label>
                <textarea
                  value={form.message}
                  onChange={(e) => setForm({ ...form, message: e.target.value })}
                  rows={4}
                  className="w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 dark:border-gray-700 dark:bg-gray-900"
                  placeholder="Certifications needed, delivery timeline, quality requirements..."
                />
              </div>

              {error && <p className="text-sm text-red-500">{error}</p>}

              <Button type="submit" size="lg" className="w-full">
                <Send className="mr-2 h-4 w-4" />
                Submit RFQ
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
