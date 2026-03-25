const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function fetchAPI<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const res = await fetch(`${API_URL}${endpoint}`, {
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
    ...options,
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(error.detail || `API error: ${res.status}`);
  }

  return res.json();
}

export interface SearchFilters {
  city?: string[];
  state?: string[];
  verified_only?: boolean;
  min_trust_score?: number;
  certifications?: string[];
  nature_of_business?: string[];
}

export interface SearchRequest {
  query: string;
  page?: number;
  per_page?: number;
  filters?: SearchFilters;
}

export interface MatchedProduct {
  id: string;
  supplier_id: string;
  name: string;
  slug: string;
  description: string | null;
  category: string | null;
  price_min: number | null;
  price_max: number | null;
  price_unit: string | null;
  min_order_qty: string | null;
  image_url: string | null;
  specs: Record<string, unknown>;
  view_count: number;
  created_at: string;
}

export interface Supplier {
  id: string;
  company_name: string;
  slug: string;
  gst_number: string | null;
  year_established: number | null;
  nature_of_business: string | null;
  contact_person: string | null;
  phone: string | null;
  mobile: string | null;
  email: string | null;
  website: string | null;
  address: string | null;
  city: string | null;
  state: string | null;
  pincode: string | null;
  country: string;
  indiamart_verified: boolean;
  gst_verified: boolean;
  trust_seal: boolean;
  rating: number | null;
  num_reviews: number;
  annual_turnover: string | null;
  num_employees: string | null;
  certifications: string[] | null;
  source_url: string | null;
  trust_score: number;
  profile_completeness: number;
  view_count: number;
  inquiry_count: number;
  created_at: string;
  updated_at: string;
}

export interface SupplierSearchResult {
  supplier: Supplier;
  final_score: number;
  match_reasons: string[];
  gap_flags: string[];
  matched_products: MatchedProduct[];
  trust_breakdown: Record<string, unknown>;
}

export interface QueryUnderstanding {
  product: string | null;
  intent_parsed: boolean;
  filters_applied: string[];
  expanded_to: string | null;
}

export interface FilterOption {
  value: string;
  count: number;
}

export interface AvailableFilters {
  cities: FilterOption[];
  certifications: FilterOption[];
  nature_of_business: FilterOption[];
  states: FilterOption[];
}

export interface SearchResponse {
  query_understanding: QueryUnderstanding;
  results: SupplierSearchResult[];
  total: number;
  related_searches: string[];
  available_filters: AvailableFilters;
  search_id: string;
}

export interface SuggestionItem {
  text: string;
  type: string;
  count: number;
}

export const api = {
  search: (data: SearchRequest) =>
    fetchAPI<SearchResponse>("/api/v1/search", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  suggest: (q: string) =>
    fetchAPI<{ suggestions: SuggestionItem[] }>(
      `/api/v1/search/suggest?q=${encodeURIComponent(q)}`
    ),

  trackClick: (data: { search_id: string; supplier_id: string; position: number }) =>
    fetchAPI("/api/v1/search/track-click", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  getSupplier: (slug: string) =>
    fetchAPI<Supplier>(`/api/v1/suppliers/${slug}`),

  getSupplierProducts: (slug: string) =>
    fetchAPI<MatchedProduct[]>(`/api/v1/suppliers/${slug}/products`),

  getSimilarSuppliers: (slug: string) =>
    fetchAPI<Supplier[]>(`/api/v1/suppliers/${slug}/similar`),

  trackView: (slug: string) =>
    fetchAPI(`/api/v1/suppliers/${slug}/view`, { method: "POST" }),

  listSuppliers: (params?: { page?: number; city?: string; state?: string }) => {
    const searchParams = new URLSearchParams();
    if (params?.page) searchParams.set("page", String(params.page));
    if (params?.city) searchParams.set("city", params.city);
    if (params?.state) searchParams.set("state", params.state);
    return fetchAPI<{ suppliers: Supplier[]; total: number; page: number; per_page: number }>(
      `/api/v1/suppliers?${searchParams}`
    );
  },

  submitRFQ: (data: {
    supplier_id?: string;
    product_name: string;
    quantity: string;
    unit?: string;
    target_price?: string;
    delivery_location?: string;
    message?: string;
  }) =>
    fetchAPI("/api/v1/rfq", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  register: (data: { email: string; password: string; full_name?: string; company_name?: string }) =>
    fetchAPI("/api/v1/auth/register", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  login: (data: { email: string; password: string }) =>
    fetchAPI<{ access_token: string; refresh_token: string }>(
      "/api/v1/auth/login",
      { method: "POST", body: JSON.stringify(data) }
    ),

  getStats: () => fetchAPI<{
    total_suppliers: number;
    total_products: number;
    total_searches: number;
    cities_covered: number;
    top_searches: { query: string; count: number }[];
  }>("/api/v1/admin/stats"),

  getSearchAnalytics: () => fetchAPI<{
    top_queries: { query: string; count: number }[];
    zero_result_queries: { query: string; count: number }[];
    daily_volume: { date: string; count: number }[];
  }>("/api/v1/admin/analytics/searches"),

  ingestFile: (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    return fetch(`${API_URL}/api/v1/admin/ingest`, {
      method: "POST",
      body: formData,
    }).then((r) => r.json());
  },
};
