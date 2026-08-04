'use client';

export const dynamic = 'force-dynamic';

import React, { useEffect, useState, Suspense } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { fetchHymnLineage, triggerAIComparison, HymnLineageItem, getLineageHymnNumber } from '@/lib/api';
import ThreeWayDiff from '@/components/ThreeWayDiff';
import SongAnalyticsWidget from '@/components/SongAnalyticsWidget';
import { GitCompare, ArrowLeft, ChevronLeft, ChevronRight, Hash, Search } from 'lucide-react';
import Link from 'next/link';

function CompareContent() {
  const searchParams = useSearchParams();
  const router = useRouter();

  const [lineageItems, setLineageItems] = useState<HymnLineageItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [comparingId, setComparingId] = useState<number | null>(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [jumpInput, setJumpInput] = useState('');

  const matchHymnNumber = (item: HymnLineageItem, target: number) => {
    const num1985 = item.number_1985 ?? item.hymn_number_1985 ?? item.hymn_number;
    const numNew = item.number_new ?? item.hymn_number_new;
    return num1985 === target || numNew === target;
  };

  const loadLineage = async () => {
    setLoading(true);
    try {
      const data = await fetchHymnLineage();
      setLineageItems(data);

      // Check initial URL param for hymn number
      const hymnParam = searchParams.get('hymn');
      if (hymnParam && data.length > 0) {
        const num = parseInt(hymnParam, 10);
        const idx = data.findIndex(item => matchHymnNumber(item, num));
        if (idx !== -1) {
          setCurrentIndex(idx);
          setJumpInput(hymnParam);
        }
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadLineage();
  }, []);

  useEffect(() => {
    const hymnParam = searchParams.get('hymn');
    if (hymnParam && lineageItems.length > 0) {
      const num = parseInt(hymnParam, 10);
      const idx = lineageItems.findIndex(item => matchHymnNumber(item, num));
      if (idx !== -1 && idx !== currentIndex) {
        setCurrentIndex(idx);
        setJumpInput(hymnParam);
      }
    }
  }, [searchParams, lineageItems]);

  const updateUrlParam = (num?: number | string) => {
    if (num && num !== '?') {
      router.replace(`/compare?hymn=${num}`, { scroll: false });
    }
  };

  const handleRunAI = async (id1985: number) => {
    setComparingId(id1985);
    try {
      await triggerAIComparison(id1985);
      await loadLineage();
    } catch (e: any) {
      alert('AI Comparison error: ' + e.message);
    } finally {
      setComparingId(null);
    }
  };

  const currentItem = lineageItems[currentIndex];

  const handlePrev = () => {
    if (currentIndex > 0) {
      const nextIdx = currentIndex - 1;
      setCurrentIndex(nextIdx);
      const num = getLineageHymnNumber(lineageItems[nextIdx]);
      if (num !== '?') {
        setJumpInput(num.toString());
        updateUrlParam(num);
      }
    }
  };

  const handleNext = () => {
    if (currentIndex < lineageItems.length - 1) {
      const nextIdx = currentIndex + 1;
      setCurrentIndex(nextIdx);
      const num = getLineageHymnNumber(lineageItems[nextIdx]);
      if (num !== '?') {
        setJumpInput(num.toString());
        updateUrlParam(num);
      }
    }
  };

  const handleJump = (e: React.FormEvent) => {
    e.preventDefault();
    if (!jumpInput.trim()) return;
    const targetNum = parseInt(jumpInput.trim(), 10);
    if (isNaN(targetNum)) return;

    const idx = lineageItems.findIndex(item => matchHymnNumber(item, targetNum));
    if (idx !== -1) {
      setCurrentIndex(idx);
      updateUrlParam(targetNum);
    } else {
      alert(`Hymn #${targetNum} not found in lineage catalog.`);
    }
  };

  const handleSelectChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const idx = parseInt(e.target.value, 10);
    if (!isNaN(idx) && idx >= 0 && idx < lineageItems.length) {
      setCurrentIndex(idx);
      const num = getLineageHymnNumber(lineageItems[idx]);
      if (num !== '?') {
        setJumpInput(num.toString());
        updateUrlParam(num);
      }
    }
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/80 p-6 rounded-2xl border border-gray-800 shadow-xl">
        <div>
          <Link href="/" className="inline-flex items-center gap-1.5 text-xs text-lds-accent hover:underline mb-2">
            <ArrowLeft className="w-3.5 h-3.5" /> Back to Catalog
          </Link>
          <h1 className="text-xl sm:text-2xl font-extrabold text-white flex items-center gap-2.5">
            <GitCompare className="w-6 h-6 text-lds-accent" /> 3-Way Hymn Comparison & AI Analysis
          </h1>
          <p className="text-xs text-gray-400 mt-0.5">
            Side-by-side lineage diff: Traditional Christian Precursor ↔ 1985 LDS Hymnal ↔ New Digital Release
          </p>
        </div>

        {/* Navigation & Jump Bar */}
        {!loading && lineageItems.length > 0 && (
          <div className="flex flex-wrap items-center gap-3">
            {/* Dropdown Selector */}
            <select
              value={currentIndex}
              onChange={handleSelectChange}
              className="bg-slate-950 border border-gray-700 text-gray-200 text-xs rounded-lg px-3 py-2 focus:ring-2 focus:ring-lds-accent outline-none"
            >
              {lineageItems.map((item, index) => (
                <option key={item.id_1985} value={index}>
                  #{getLineageHymnNumber(item)} {item.title_1985}
                </option>
              ))}
            </select>

            {/* Jump Box */}
            <form onSubmit={handleJump} className="flex items-center gap-1.5">
              <div className="relative">
                <Hash className="w-3.5 h-3.5 text-gray-400 absolute left-2.5 top-2.5" />
                <input
                  type="number"
                  placeholder="Jump #"
                  value={jumpInput}
                  onChange={(e) => setJumpInput(e.target.value)}
                  className="w-24 bg-slate-950 border border-gray-700 text-gray-200 text-xs rounded-lg pl-8 pr-2 py-2 focus:ring-2 focus:ring-lds-accent outline-none"
                />
              </div>
              <button
                type="submit"
                className="px-3 py-2 bg-lds-blue border border-lds-teal/40 text-white font-semibold text-xs rounded-lg hover:bg-lds-teal transition-colors"
              >
                Go
              </button>
            </form>

            {/* Previous / Next Buttons */}
            <div className="flex items-center gap-1 bg-slate-950 p-1 rounded-lg border border-gray-800">
              <button
                onClick={handlePrev}
                disabled={currentIndex === 0}
                className="p-1.5 rounded-md hover:bg-slate-800 disabled:opacity-30 text-gray-200 transition-colors"
                title="Previous Hymn"
              >
                <ChevronLeft className="w-5 h-5" />
              </button>
              <span className="text-xs font-bold px-2 text-lds-accent">
                {currentIndex + 1} / {lineageItems.length}
              </span>
              <button
                onClick={handleNext}
                disabled={currentIndex === lineageItems.length - 1}
                className="p-1.5 rounded-md hover:bg-slate-800 disabled:opacity-30 text-gray-200 transition-colors"
                title="Next Hymn"
              >
                <ChevronRight className="w-5 h-5" />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Main Diff Display Area */}
      {loading ? (
        <div className="py-20 text-center text-gray-400 text-sm animate-pulse">
          Loading 3-Way Hymn Comparison...
        </div>
      ) : lineageItems.length === 0 ? (
        <div className="py-20 text-center text-gray-500 text-sm">
          No hymn lineage entries found in database.
        </div>
      ) : currentItem ? (
        <div className="space-y-4">
          <div className="flex items-center justify-between text-xs text-gray-400 px-2">
            <span>Viewing Entry {currentIndex + 1} of {lineageItems.length}</span>
            <span className="font-semibold text-lds-gold">1985 Hymn #{getLineageHymnNumber(currentItem)}</span>
          </div>

          <SongAnalyticsWidget item={currentItem} />

          <ThreeWayDiff
            key={currentItem.id_1985}
            item={currentItem}
            onRunAI={handleRunAI}
            isComparing={comparingId === currentItem.id_1985}
          />

          {/* Bottom Nav Bar */}
          <div className="flex items-center justify-between pt-4">
            <button
              onClick={handlePrev}
              disabled={currentIndex === 0}
              className="flex items-center gap-2 px-4 py-2.5 bg-slate-900 border border-gray-800 text-gray-200 font-semibold text-xs rounded-lg hover:bg-slate-800 disabled:opacity-30 transition-colors"
            >
              <ChevronLeft className="w-4 h-4" /> Previous Hymn
            </button>
            <button
              onClick={handleNext}
              disabled={currentIndex === lineageItems.length - 1}
              className="flex items-center gap-2 px-4 py-2.5 bg-lds-blue border border-lds-teal/40 text-white font-semibold text-xs rounded-lg hover:bg-lds-teal disabled:opacity-30 transition-colors shadow-lg"
            >
              Next Hymn <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      ) : null}
    </div>
  );
}

export default function ComparePage() {
  return (
    <Suspense fallback={<div className="py-20 text-center text-gray-400 text-sm">Loading...</div>}>
      <CompareContent />
    </Suspense>
  );
}
