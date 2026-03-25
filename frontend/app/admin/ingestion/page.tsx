"use client";

import { useCallback, useState } from "react";
import Link from "next/link";
import { ArrowLeft, Upload, FileJson, FileSpreadsheet, CheckCircle2, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";

export default function IngestionPage() {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<{
    job_id: string;
    status: string;
    total: number;
    added: number;
    updated: number;
    skipped: number;
    errors: number;
  } | null>(null);
  const [error, setError] = useState("");

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    const f = e.dataTransfer.files[0];
    if (f && (f.name.endsWith(".json") || f.name.endsWith(".csv"))) {
      setFile(f);
      setError("");
    } else {
      setError("Only JSON and CSV files are supported");
    }
  }, []);

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    setError("");
    setResult(null);

    try {
      const res = await api.ingestFile(file);
      setResult(res);
    } catch (err) {
      setError("Upload failed. Please try again.");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
      <header className="border-b border-gray-200 bg-white dark:border-gray-800 dark:bg-gray-950">
        <div className="mx-auto flex max-w-4xl items-center gap-4 px-4 py-4">
          <Link href="/admin"><Button variant="ghost" size="icon"><ArrowLeft className="h-5 w-5" /></Button></Link>
          <h1 className="font-display text-xl font-bold">Data Ingestion</h1>
        </div>
      </header>

      <div className="mx-auto max-w-4xl px-4 py-8 space-y-6">
        {/* Upload zone */}
        <Card>
          <CardHeader><CardTitle>Upload Supplier Data</CardTitle></CardHeader>
          <CardContent>
            <div
              onDragOver={(e) => e.preventDefault()}
              onDrop={handleDrop}
              className="flex flex-col items-center justify-center rounded-lg border-2 border-dashed border-gray-300 bg-gray-50 p-12 transition-colors hover:border-brand-400 hover:bg-brand-50/50 dark:border-gray-700 dark:bg-gray-800/50"
            >
              <Upload className="h-10 w-10 text-gray-400" />
              <p className="mt-3 text-sm font-medium text-gray-700 dark:text-gray-300">
                Drag & drop your file here, or
              </p>
              <label className="mt-2">
                <input
                  type="file"
                  accept=".json,.csv"
                  className="hidden"
                  onChange={(e) => {
                    const f = e.target.files?.[0];
                    if (f) { setFile(f); setError(""); }
                  }}
                />
                <span className="cursor-pointer text-sm font-medium text-brand-600 hover:text-brand-700">
                  browse to upload
                </span>
              </label>
              <p className="mt-1 text-xs text-gray-400">Supports JSON and CSV files from the scraper</p>
            </div>

            {file && (
              <div className="mt-4 flex items-center justify-between rounded-lg border border-gray-200 bg-white p-3 dark:border-gray-700 dark:bg-gray-900">
                <div className="flex items-center gap-2">
                  {file.name.endsWith(".json") ? (
                    <FileJson className="h-5 w-5 text-amber-500" />
                  ) : (
                    <FileSpreadsheet className="h-5 w-5 text-emerald-500" />
                  )}
                  <span className="text-sm font-medium">{file.name}</span>
                  <span className="text-xs text-gray-400">({(file.size / 1024).toFixed(1)} KB)</span>
                </div>
                <Button onClick={handleUpload} disabled={uploading}>
                  {uploading ? "Uploading..." : "Import Data"}
                </Button>
              </div>
            )}

            {error && (
              <div className="mt-4 flex items-center gap-2 rounded-lg bg-red-50 p-3 text-sm text-red-700 dark:bg-red-950 dark:text-red-300">
                <AlertCircle className="h-4 w-4" />
                {error}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Results */}
        {result && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <CheckCircle2 className="h-5 w-5 text-emerald-500" />
                Import Complete
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4 sm:grid-cols-5">
                <div className="text-center">
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">{result.total}</p>
                  <p className="text-xs text-gray-500">Total Records</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-emerald-600">{result.added}</p>
                  <p className="text-xs text-gray-500">Added</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-blue-600">{result.updated}</p>
                  <p className="text-xs text-gray-500">Updated</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-gray-400">{result.skipped}</p>
                  <p className="text-xs text-gray-500">Skipped</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-red-500">{result.errors}</p>
                  <p className="text-xs text-gray-500">Errors</p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
