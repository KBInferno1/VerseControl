'use client';

export const dynamic = 'force-dynamic';

import React, { useEffect, useState } from 'react';
import { fetchAnalyticsSummary } from '@/lib/api';
import AnalyticsCharts from '@/components/AnalyticsCharts';
import { BarChart3, ArrowLeft, RefreshCw, Sparkles } from 'lucide-react';
import Link from 'next/link';

export default function AnalyticsPage() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const loadAnalytics = async () => {
    setLoading(true);
    setError('');
    try {
      const summary = await fetchAnalyticsSummary();
      setData(summary);
    } catch (e: any) {
      setError(e.message || 'Failed to load analytics data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAnalytics();
  }, []);

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="bg-gradient-to-r from-lds-navy via-lds-blue to-lds-teal p-8 rounded-2xl border border-gray-800 shadow-2xl relative overflow-hidden">
        <div className="relative z-10 space-y-3">
          <Link href="/" className="inline-flex items-center gap-1.5 text-xs text-lds-accent hover:underline mb-1">
            <ArrowLeft className="w-3.5 h-3.5" /> Back to Catalog
          </Link>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-lds-gold/20 text-lds-gold border border-lds-gold/30 text-xs font-semibold">
            <Sparkles className="w-3.5 h-3.5" /> Data Taxonomist & Metrics Engine
          </div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight sm:text-4xl flex items-center gap-3">
            <BarChart3 className="w-8 h-8 text-lds-accent" /> Hymnal Analytics & Theological Insights
          </h1>
          <p className="text-sm text-gray-300 leading-relaxed max-w-3xl">
            Visualizing 500 years of hymnological shifts, major taxonomy distributions, sub-theme concentrations, and AI-identified change patterns.
          </p>
        </div>
      </div>

      {/* Main Content Area */}
      {loading ? (
        <div className="py-20 text-center text-gray-400 text-sm animate-pulse">
          Calculating hymnal metrics & aggregating taxonomy charts...
        </div>
      ) : error ? (
        <div className="py-16 text-center text-red-400 text-sm space-y-3">
          <p>{error}</p>
          <button
            onClick={loadAnalytics}
            className="px-4 py-2 bg-slate-800 text-white rounded-lg text-xs hover:bg-slate-700 transition-colors inline-flex items-center gap-2"
          >
            <RefreshCw className="w-3.5 h-3.5" /> Retry
          </button>
        </div>
      ) : data ? (
        <AnalyticsCharts data={data} />
      ) : null}
    </div>
  );
}
