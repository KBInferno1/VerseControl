'use client';

import React from 'react';
import { HymnLineageItem } from '@/lib/api';
import { BarChart3, Clock, Layers, FileText, CheckCircle2, AlertCircle, Sparkles, TrendingUp } from 'lucide-react';

interface SongAnalyticsWidgetProps {
  item: HymnLineageItem;
}

export default function SongAnalyticsWidget({ item }: SongAnalyticsWidgetProps) {
  // Compute Stanza Counts
  const countStanzas = (lyrics?: string) => {
    if (!lyrics || lyrics === 'Lyrics pending ingestion...') return 0;
    const lines = lyrics.split('\n').filter(l => l.trim().length > 0);
    const verses = lines.filter(l => l.toLowerCase().includes('verse') || l.toLowerCase().includes('stanza'));
    return verses.length > 0 ? verses.length : Math.max(1, Math.floor(lines.length / 4));
  };

  const countWords = (lyrics?: string) => {
    if (!lyrics || lyrics === 'Lyrics pending ingestion...') return 0;
    return lyrics.trim().split(/\s+/).length;
  };

  const origStanzas = countStanzas(item.lyrics_original);
  const ldsStanzas = countStanzas(item.lyrics_1985);
  const newStanzas = countStanzas(item.lyrics_new);

  const origWords = countWords(item.lyrics_original);
  const ldsWords = countWords(item.lyrics_1985);
  const newWords = countWords(item.lyrics_new);

  // Historical Age Gap calculation
  const origYear = item.publication_year;
  const currentYear = new Date().getFullYear();
  const ageSpan = origYear ? currentYear - origYear : null;

  // Stanza Retention Percentage
  const retentionPct = origStanzas > 0 ? Math.min(100, Math.round((ldsStanzas / origStanzas) * 100)) : null;

  // Change Log breakdown for this song
  const changeCategories = item.change_log?.change_categories || [];
  const alteredCount = item.change_log?.altered_phrases?.length || 0;
  const omittedCount = item.change_log?.omitted_verses?.length || 0;

  return (
    <div className="bg-slate-900/90 border border-lds-gold/30 rounded-xl p-5 shadow-2xl space-y-5 text-gray-100 relative overflow-hidden">
      {/* Background Accent Gradient */}
      <div className="absolute top-0 right-0 w-64 h-64 bg-lds-gold/5 rounded-full blur-3xl pointer-events-none" />

      {/* Title Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-gray-800 pb-3">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-lg bg-lds-gold/20 text-lds-gold border border-lds-gold/30">
            <BarChart3 className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-extrabold text-white text-base flex items-center gap-2">
              Song Lineage Analytics: <span className="text-lds-accent">{item.title_1985}</span>
            </h3>
            <p className="text-xs text-gray-400">
              Evolution metrics for 1985 Hymn #{item.hymn_number_1985}
            </p>
          </div>
        </div>

        {ageSpan && (
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-lds-blue/30 border border-lds-teal/40 text-lds-accent text-xs font-bold">
            <Clock className="w-3.5 h-3.5" /> {ageSpan} Years of Historical Evolution ({origYear} → {currentYear})
          </div>
        )}
      </div>

      {/* Grid Metrics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {/* Card 1: Stanza & Verse Retention */}
        <div className="bg-slate-950/80 border border-gray-800 p-4 rounded-lg space-y-2">
          <div className="flex items-center justify-between text-xs text-gray-400">
            <span className="flex items-center gap-1.5 font-semibold text-white">
              <Layers className="w-3.5 h-3.5 text-lds-gold" /> Stanza Retention
            </span>
            {retentionPct !== null && (
              <span className="text-lds-accent font-bold">{retentionPct}% Retained</span>
            )}
          </div>
          <div className="space-y-1.5 pt-1">
            <div className="flex justify-between text-xs">
              <span className="text-gray-400">Original ({origYear || 'Precursor'})</span>
              <span className="font-bold text-gray-200">{origStanzas} Stanzas ({origWords} words)</span>
            </div>
            <div className="flex justify-between text-xs">
              <span className="text-gray-400">1985 LDS Print</span>
              <span className="font-bold text-lds-gold">{ldsStanzas} Stanzas ({ldsWords} words)</span>
            </div>
            {item.hymn_new_id && (
              <div className="flex justify-between text-xs">
                <span className="text-gray-400">2024 Digital Release</span>
                <span className="font-bold text-lds-accent">{newStanzas} Stanzas ({newWords} words)</span>
              </div>
            )}
          </div>
        </div>

        {/* Card 2: Phrase Shift & Omissions Count */}
        <div className="bg-slate-950/80 border border-gray-800 p-4 rounded-lg space-y-2">
          <div className="flex items-center justify-between text-xs text-gray-400">
            <span className="flex items-center gap-1.5 font-semibold text-white">
              <TrendingUp className="w-3.5 h-3.5 text-lds-accent" /> AI Shift Counts
            </span>
            <span className="text-xs text-lds-gold font-bold">
              {item.change_log ? 'Analyzed' : 'Pending AI Run'}
            </span>
          </div>
          <div className="grid grid-cols-2 gap-2 pt-1 text-center">
            <div className="bg-slate-900 p-2 rounded border border-gray-800">
              <div className="text-lg font-extrabold text-amber-400">{alteredCount}</div>
              <div className="text-[10px] text-gray-400 font-medium">Altered Phrases</div>
            </div>
            <div className="bg-slate-900 p-2 rounded border border-gray-800">
              <div className="text-lg font-extrabold text-rose-400">{omittedCount}</div>
              <div className="text-[10px] text-gray-400 font-medium">Omitted Verses</div>
            </div>
          </div>
        </div>

        {/* Card 3: Change Classifications */}
        <div className="bg-slate-950/80 border border-gray-800 p-4 rounded-lg space-y-2">
          <div className="flex items-center justify-between text-xs text-gray-400">
            <span className="flex items-center gap-1.5 font-semibold text-white">
              <Sparkles className="w-3.5 h-3.5 text-teal-400" /> Change Categories
            </span>
            <span className="text-[10px] text-gray-400">{changeCategories.length} Types</span>
          </div>
          <div className="flex flex-wrap gap-1.5 pt-1">
            {changeCategories.length > 0 ? (
              changeCategories.map((cat, i) => (
                <span key={i} className="text-[11px] px-2 py-0.5 rounded bg-lds-accent/10 border border-lds-accent/30 text-lds-accent font-medium">
                  {cat}
                </span>
              ))
            ) : (
              <span className="text-xs text-gray-500 italic">No change log generated yet. Click "Run AI Analysis" below.</span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
