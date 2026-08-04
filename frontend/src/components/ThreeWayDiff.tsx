'use client';

import React from 'react';
import { HymnLineageItem, getLineageHymnNumber } from '@/lib/api';
import { Tag, Sparkles, AlertCircle, ArrowRight } from 'lucide-react';

interface Props {
  item: HymnLineageItem;
  onRunAI?: (id1985?: number | null, idNew?: number | null, idOriginal?: number | null) => void;
  isComparing?: boolean;
}

export default function ThreeWayDiff({ item, onRunAI, isComparing }: Props) {
  const parseJson = (val: any) => {
    if (!val) return [];
    if (typeof val === 'string') {
      try { return JSON.parse(val); } catch { return []; }
    }
    return val;
  };

  const omittedVerses = parseJson(item.omitted_verses);
  const alteredPhrases = parseJson(item.altered_phrases);
  const changeCategories = parseJson(item.change_categories);

  const displayTitle = item.title_1985 || item.title_new || item.title_original || 'Hymn Comparison';

  return (
    <div className="bg-lds-cardBg border border-gray-800 rounded-xl p-6 shadow-xl space-y-6">
      {/* Header Banner */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b border-gray-800 pb-4">
        <div>
          <div className="flex items-center gap-3">
            <span className="bg-lds-accent/20 text-lds-accent border border-lds-accent/40 font-mono text-sm px-2.5 py-0.5 rounded-md font-bold">
              #{getLineageHymnNumber(item)}
            </span>
            <h2 className="text-2xl font-bold text-white">{displayTitle}</h2>
          </div>
          {item.major_theme && (
            <div className="flex items-center gap-2 mt-2">
              <span className="text-xs px-2.5 py-1 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20 font-medium">
                {item.major_theme}
              </span>
              {item.minor_theme && (
                <span className="text-xs px-2.5 py-1 rounded-full bg-purple-500/10 text-purple-400 border border-purple-500/20">
                  {item.minor_theme}
                </span>
              )}
            </div>
          )}
        </div>

        {onRunAI && (
          <button
            onClick={() => onRunAI(item.id_1985, item.id_new, item.id_original)}
            disabled={isComparing}
            className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-teal-500 to-lds-accent text-slate-950 font-semibold rounded-lg hover:brightness-110 disabled:opacity-50 transition-all text-sm shadow-md"
          >
            <Sparkles className="w-4 h-4" />
            {isComparing ? 'Running AI Engine...' : 'Run AI Theological Analysis'}
          </button>
        )}
      </div>

      {/* 3-Column Side-by-Side Hymn Comparison */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Column 1: Traditional Christian Original */}
        <div className="bg-slate-900/60 border border-amber-500/20 rounded-lg p-4 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3 border-b border-amber-500/20 pb-2">
              <h3 className="font-semibold text-amber-300 text-sm flex items-center gap-1.5">
                Traditional Christian Original
              </h3>
              {item.publication_year && (
                <span className="text-xs text-amber-400/70 font-mono">{item.publication_year}</span>
              )}
            </div>
            {item.title_original ? (
              <div>
                <p className="text-xs font-semibold text-gray-300 mb-2">Author: {item.original_author || 'Unknown'}</p>
                <div className="whitespace-pre-wrap text-xs font-serif text-gray-300 leading-relaxed max-h-80 overflow-y-auto bg-slate-950/40 p-3 rounded border border-gray-800">
                  {item.lyrics_original}
                </div>
              </div>
            ) : (
              <p className="text-xs text-gray-500 italic py-8 text-center">No original traditional Christian precursor linked</p>
            )}
          </div>
        </div>

        {/* Column 2: 1985 LDS Hymnal */}
        <div className="bg-slate-900/60 border border-blue-500/20 rounded-lg p-4">
          <div className="flex items-center justify-between mb-3 border-b border-blue-500/20 pb-2">
            <h3 className="font-semibold text-blue-300 text-sm">1985 Hymnal (#{getLineageHymnNumber(item)})</h3>
            <span className="text-xs text-blue-400/70">1985 Print</span>
          </div>
          {item.lyrics_1985 ? (
            <div className="whitespace-pre-wrap text-xs font-serif text-gray-300 leading-relaxed max-h-80 overflow-y-auto bg-slate-950/40 p-3 rounded border border-gray-800">
              {item.lyrics_1985}
            </div>
          ) : (
            <p className="text-xs text-gray-500 italic py-8 text-center">Not present in 1985 LDS Hymnal print edition</p>
          )}
        </div>

        {/* Column 3: New Digital Release */}
        <div className="bg-slate-900/60 border border-emerald-500/20 rounded-lg p-4">
          <div className="flex items-center justify-between mb-3 border-b border-emerald-500/20 pb-2">
            <h3 className="font-semibold text-emerald-300 text-sm">New Hymns Release</h3>
            <span className="text-xs px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-mono">
              {item.batch_release || 'Batch 1'}
            </span>
          </div>
          {item.lyrics_new ? (
            <div className="whitespace-pre-wrap text-xs font-serif text-gray-300 leading-relaxed max-h-80 overflow-y-auto bg-slate-950/40 p-3 rounded border border-gray-800">
              {item.lyrics_new}
            </div>
          ) : (
            <p className="text-xs text-gray-500 italic py-8 text-center">Not yet released in new digital batches</p>
          )}
        </div>
      </div>

      {/* AI Analysis Output & Change Log */}
      {item.summary && (
        <div className="bg-slate-900 border border-lds-accent/30 rounded-lg p-5 space-y-4">
          <div className="flex items-center gap-2 text-lds-accent font-semibold text-sm">
            <Sparkles className="w-5 h-5 text-lds-gold" />
            AI Theological Analysis & Editor Rationale
          </div>
          <p className="text-sm text-gray-200 leading-relaxed italic bg-slate-950/60 p-3.5 rounded border border-gray-800">
            "{item.summary}"
          </p>

          {/* Change Categories */}
          {changeCategories.length > 0 && (
            <div className="space-y-1.5">
              <span className="text-xs font-semibold text-gray-400">Identified Change Categories:</span>
              <div className="flex flex-wrap gap-2">
                {changeCategories.map((cat: string, idx: number) => (
                  <span key={idx} className="text-xs px-2.5 py-1 rounded bg-teal-950 text-teal-300 border border-teal-800/50">
                    {cat}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Altered Phrases Grid */}
          {alteredPhrases.length > 0 && (
            <div className="space-y-2">
              <span className="text-xs font-semibold text-gray-400">Line-by-Line Phrase Alterations:</span>
              <div className="grid grid-cols-1 gap-2">
                {alteredPhrases.map((phrase: any, idx: number) => (
                  <div key={idx} className="flex flex-col sm:flex-row sm:items-center justify-between text-xs bg-slate-950 p-2.5 rounded border border-gray-800 gap-2">
                    <span className="text-red-400 line-through bg-red-950/30 px-2 py-1 rounded border border-red-900/30">
                      {phrase.original}
                    </span>
                    <ArrowRight className="w-4 h-4 text-gray-500 hidden sm:block shrink-0" />
                    <span className="text-emerald-400 bg-emerald-950/30 px-2 py-1 rounded border border-emerald-900/30">
                      {phrase.new}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Omitted Verses */}
          {omittedVerses.length > 0 && (
            <div className="space-y-1.5">
              <span className="text-xs font-semibold text-amber-400 flex items-center gap-1">
                <AlertCircle className="w-3.5 h-3.5" /> Omitted Verses / Stanzas:
              </span>
              <ul className="list-disc list-inside text-xs text-amber-300/80 space-y-1">
                {omittedVerses.map((v: string, idx: number) => (
                  <li key={idx}>{v}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
