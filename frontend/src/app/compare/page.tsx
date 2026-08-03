'use client';

import React, { useEffect, useState } from 'react';
import { fetchHymnLineage, triggerAIComparison, HymnLineageItem } from '@/lib/api';
import ThreeWayDiff from '@/components/ThreeWayDiff';
import { GitCompare, Sparkles, ArrowLeft } from 'lucide-react';
import Link from 'next/link';

export default function ComparePage() {
  const [lineageItems, setLineageItems] = useState<HymnLineageItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [comparingId, setComparingId] = useState<number | null>(null);

  const loadLineage = async () => {
    setLoading(true);
    try {
      const data = await fetchHymnLineage();
      setLineageItems(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadLineage();
  }, []);

  const handleRunAI = async (id1985: number) => {
    setComparingId(id1985);
    try {
      await triggerAIComparison(id1985);
      await loadLineage(); // reload updated change log & themes
    } catch (e: any) {
      alert('AI Comparison error: ' + e.message);
    } finally {
      setComparingId(null);
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <Link href="/" className="inline-flex items-center gap-1.5 text-xs text-lds-accent hover:underline mb-2">
            <ArrowLeft className="w-3.5 h-3.5" /> Back to Catalog
          </Link>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white flex items-center gap-3">
            <GitCompare className="w-7 h-7 text-lds-accent" /> 3-Way Hymn Comparison & AI Analysis
          </h1>
          <p className="text-xs text-gray-400 mt-1">
            Compare side-by-side: Traditional Christian Original ↔ 1985 LDS Hymnal ↔ New Digital Release
          </p>
        </div>
      </div>

      {loading ? (
        <div className="py-16 text-center text-gray-400 text-sm">Loading 3-Way Comparison Dataset...</div>
      ) : lineageItems.length === 0 ? (
        <div className="py-16 text-center text-gray-500 text-sm">No hymn lineage entries found in database.</div>
      ) : (
        <div className="space-y-8">
          {lineageItems.map((item) => (
            <ThreeWayDiff
              key={item.id_1985}
              item={item}
              onRunAI={handleRunAI}
              isComparing={comparingId === item.id_1985}
            />
          ))}
        </div>
      )}
    </div>
  );
}
