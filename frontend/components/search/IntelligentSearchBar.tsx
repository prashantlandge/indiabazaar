"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { Search, Mic, X, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { api, type SuggestionItem } from "@/lib/api";
import { useSearchStore } from "@/lib/store";
import { cn } from "@/lib/utils";

const PLACEHOLDER_EXAMPLES = [
  "500kg food-grade HDPE pellets, Maharashtra, ISO certified",
  "industrial conveyor belts, urgent, Mumbai",
  "SS pipe fittings, bulk order, manufacturer",
  "corrugated packaging boxes, 10000 pieces, Delhi NCR",
  "transformer oil, ISI certified, wholesale",
];

interface Props {
  size?: "hero" | "compact";
  autoFocus?: boolean;
}

export function IntelligentSearchBar({ size = "hero", autoFocus = false }: Props) {
  const router = useRouter();
  const { query, setQuery } = useSearchStore();
  const [localQuery, setLocalQuery] = useState(query);
  const [suggestions, setSuggestions] = useState<SuggestionItem[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [placeholderIndex, setPlaceholderIndex] = useState(0);
  const [parsedChips, setParsedChips] = useState<string[]>([]);
  const [isListening, setIsListening] = useState(false);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const debounceRef = useRef<NodeJS.Timeout>();
  const chipTimeoutRef = useRef<NodeJS.Timeout>();

  // Cycle placeholder text
  useEffect(() => {
    const interval = setInterval(() => {
      setPlaceholderIndex((i) => (i + 1) % PLACEHOLDER_EXAMPLES.length);
    }, 4000);
    return () => clearInterval(interval);
  }, []);

  // Fetch suggestions with debounce
  const fetchSuggestions = useCallback(async (q: string) => {
    if (q.length < 3) {
      setSuggestions([]);
      return;
    }
    try {
      const res = await api.suggest(q);
      setSuggestions(res.suggestions || []);
    } catch {
      setSuggestions([]);
    }
  }, []);

  // Show parsed intent chips after user pauses typing
  const showParsePreview = useCallback((q: string) => {
    if (q.length < 5) {
      setParsedChips([]);
      return;
    }
    // Simple client-side preview (real parsing happens on search)
    const chips: string[] = [];
    const words = q.toLowerCase();

    // Detect product
    const productWords = words.replace(/\b(kg|ton|pieces|urgent|iso|ce|bis|mumbai|pune|delhi|maharashtra|karnataka|certified|need|want|bulk|order)\b/gi, "").trim();
    if (productWords) chips.push(`Product: ${productWords.split(/\s+/).slice(0, 3).join(" ")}`);

    // Detect location
    const locations = ["mumbai", "pune", "delhi", "maharashtra", "karnataka", "bangalore", "chennai", "kolkata", "hyderabad", "gujarat", "ahmedabad"];
    for (const loc of locations) {
      if (words.includes(loc)) {
        chips.push(`Location: ${loc.charAt(0).toUpperCase() + loc.slice(1)}`);
        break;
      }
    }

    // Detect certifications
    const certs = ["iso", "ce", "bis", "fssai", "gmp"];
    const foundCerts = certs.filter((c) => words.includes(c));
    if (foundCerts.length) chips.push(`Cert: ${foundCerts.map((c) => c.toUpperCase()).join(", ")}`);

    // Detect quantity
    const qtyMatch = q.match(/(\d+)\s*(kg|ton|pieces|pcs|units|meters)/i);
    if (qtyMatch) chips.push(`Qty: ${qtyMatch[1]} ${qtyMatch[2]}`);

    // Detect urgency
    if (words.includes("urgent") || words.includes("asap")) chips.push("Urgency: High");

    setParsedChips(chips);
  }, []);

  const handleChange = (value: string) => {
    setLocalQuery(value);
    setShowSuggestions(true);

    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => fetchSuggestions(value), 300);

    if (chipTimeoutRef.current) clearTimeout(chipTimeoutRef.current);
    chipTimeoutRef.current = setTimeout(() => showParsePreview(value), 800);
  };

  const handleSearch = (searchQuery?: string) => {
    const q = searchQuery || localQuery;
    if (!q.trim()) return;
    setQuery(q);
    setShowSuggestions(false);
    router.push(`/search?q=${encodeURIComponent(q)}`);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSearch();
    }
  };

  const handleVoiceInput = () => {
    if (!("webkitSpeechRecognition" in window || "SpeechRecognition" in window)) return;

    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.lang = "en-IN";
    recognition.continuous = false;

    recognition.onstart = () => setIsListening(true);
    recognition.onend = () => setIsListening(false);
    recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      setLocalQuery(transcript);
      handleChange(transcript);
    };

    recognition.start();
  };

  const isHero = size === "hero";

  return (
    <div className="relative w-full">
      <div
        className={cn(
          "relative flex items-start rounded-xl border-2 bg-white transition-all dark:bg-gray-900",
          isHero
            ? "border-brand-200 shadow-elevated focus-within:border-brand-500 focus-within:shadow-lg"
            : "border-gray-200 shadow-card focus-within:border-brand-400",
        )}
      >
        <Search
          className={cn(
            "absolute left-4 text-gray-400",
            isHero ? "top-4 h-6 w-6" : "top-3 h-5 w-5"
          )}
        />
        <textarea
          ref={inputRef}
          value={localQuery}
          onChange={(e) => handleChange(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={() => setShowSuggestions(true)}
          onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
          autoFocus={autoFocus}
          placeholder={PLACEHOLDER_EXAMPLES[placeholderIndex]}
          rows={isHero ? 2 : 1}
          className={cn(
            "flex-1 resize-none bg-transparent outline-none placeholder:text-gray-400",
            isHero
              ? "px-12 py-4 text-lg"
              : "px-11 py-3 text-sm",
          )}
        />
        <div className={cn("absolute right-2 flex items-center gap-1", isHero ? "top-3" : "top-2")}>
          {localQuery && (
            <button
              onClick={() => { setLocalQuery(""); setParsedChips([]); setSuggestions([]); }}
              className="rounded-full p-1.5 text-gray-400 hover:bg-gray-100 hover:text-gray-600 dark:hover:bg-gray-800"
            >
              <X className="h-4 w-4" />
            </button>
          )}
          <button
            onClick={handleVoiceInput}
            className={cn(
              "rounded-full p-1.5 transition-colors",
              isListening
                ? "bg-red-100 text-red-500 animate-pulse"
                : "text-gray-400 hover:bg-gray-100 hover:text-gray-600 dark:hover:bg-gray-800"
            )}
          >
            <Mic className="h-4 w-4" />
          </button>
          <Button
            onClick={() => handleSearch()}
            size={isHero ? "lg" : "sm"}
            className={cn(isHero && "ml-1")}
          >
            Search
          </Button>
        </div>
      </div>

      {/* Parsed intent chips */}
      {parsedChips.length > 0 && (
        <div className="mt-2 flex flex-wrap items-center gap-2 animate-in fade-in slide-in-from-top-1 duration-300">
          <Sparkles className="h-4 w-4 text-brand-500" />
          <span className="text-xs font-medium text-brand-600 dark:text-brand-400">We understood:</span>
          {parsedChips.map((chip) => (
            <span
              key={chip}
              className="inline-flex items-center rounded-full bg-brand-50 px-2.5 py-0.5 text-xs font-medium text-brand-700 dark:bg-brand-950 dark:text-brand-300"
            >
              {chip}
            </span>
          ))}
        </div>
      )}

      {/* Suggestions dropdown */}
      {showSuggestions && suggestions.length > 0 && (
        <div className="absolute z-50 mt-1 w-full rounded-lg border border-gray-200 bg-white shadow-elevated dark:border-gray-700 dark:bg-gray-900">
          {suggestions.map((s, i) => (
            <button
              key={`${s.text}-${i}`}
              className="flex w-full items-center gap-3 px-4 py-2.5 text-left text-sm hover:bg-gray-50 first:rounded-t-lg last:rounded-b-lg dark:hover:bg-gray-800"
              onMouseDown={() => handleSearch(s.text)}
            >
              <Search className="h-4 w-4 flex-shrink-0 text-gray-400" />
              <span className="flex-1 truncate">{s.text}</span>
              <span className="text-xs text-gray-400">
                {s.type === "product" ? "Product" : s.type === "supplier" ? "Supplier" : "Search"}
              </span>
              {s.count > 0 && (
                <span className="text-xs text-gray-400">{s.count}</span>
              )}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
