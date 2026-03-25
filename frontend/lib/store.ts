import { create } from "zustand";
import type { SearchFilters, SearchResponse } from "./api";

interface SearchStore {
  query: string;
  filters: SearchFilters;
  results: SearchResponse | null;
  isLoading: boolean;
  setQuery: (query: string) => void;
  setFilters: (filters: SearchFilters) => void;
  setResults: (results: SearchResponse | null) => void;
  setLoading: (loading: boolean) => void;
  clearSearch: () => void;
}

export const useSearchStore = create<SearchStore>((set) => ({
  query: "",
  filters: {},
  results: null,
  isLoading: false,
  setQuery: (query) => set({ query }),
  setFilters: (filters) => set({ filters }),
  setResults: (results) => set({ results }),
  setLoading: (isLoading) => set({ isLoading }),
  clearSearch: () => set({ query: "", filters: {}, results: null, isLoading: false }),
}));

interface AuthStore {
  token: string | null;
  user: { email: string; full_name: string | null } | null;
  setAuth: (token: string, user: { email: string; full_name: string | null }) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthStore>((set) => ({
  token: null,
  user: null,
  setAuth: (token, user) => set({ token, user }),
  logout: () => set({ token: null, user: null }),
}));
