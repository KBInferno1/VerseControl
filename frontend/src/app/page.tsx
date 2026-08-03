'use client';

import React, { useEffect, useState } from 'react';
import { fetchStats, fetch1985Hymns, fetchHymnLineage, triggerScraper, Hymn1985, HymnLineageItem } from '@/lib/api';
import { BookOpen, RefreshCw, Sparkles, Filter, Search, Layers, GitCompare } from 'lucide-react';
import Link from 'next/link';

export default function CatalogPage() {
  const [stats, setStats] = useState<any>(null);
  const [hymns, setHymns] = useState<Hymn1985[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTheme, setSelectedTheme] = useState('');
  const [loading, setLoading] = useState(true);
  const [scraping, setScraping] = useState(false);

  const loadData = async () => {
    setLoading(true);
    try {
      const [statsData, hymnsData] = await Promise.all([
        fetchStats().catch(() => null),
        fetch1985Hymns(searchQuery, selectedTheme).catch(() => [])
      ]);
      setStats(statsData);
      setHymns(hymnsData);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [searchQuery, selectedTheme]);

  const handleTriggerScraper = async () => {
    setScraping(true);
    try {
      await triggerScraper();
      alert('Scraper dispatched in background to poll for new digital hymns.');
    } catch (e: any) {
      alert('Error triggering scraper: ' + e.message);
    } finally {
      setScraping(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Hero Header */}
      <div className="bg-gradient-to-r from-lds-navy via-lds-blue to-lds-teal p-8 rounded-2xl border border-gray-800 shadow-2xl relative overflow-hidden">
        <div className="relative z-10 max-w-3xl space-y-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-lds-gold/20 text-lds-gold border border-lds-gold/30 text-xs font-semibold">
            <Sparkles className="w-3.5 h-3.5" /> AI Taxonomist & Theological Editor
          </div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight sm:text-4xl">
            LDS Hymnal Catalog & Theological Analysis
          </h1>
          <p className="text-sm text-gray-300 leading-relaxed">
            Cataloging and comparing lyrical shifts between the 1985 LDS Hymnal, the new "Hymns—for Home and Church" digital releases, and traditional Christian original hymn sources.
          </p>

          <div className="pt-2 flex flex-wrap items-center gap-4">
            <Link
              href="/compare"
              className="flex items-center gap-2 px-5 py-2.5 bg-lds-accent text-slate-950 font-bold rounded-lg hover:bg-teal-400 transition-colors text-sm shadow-lg"
            >
              <GitCompare className="w-4 h-4" /> View 3-Way Lineage Diff
            </Link>
            <button
              onClick={handleTriggerScraper}
              disabled={scraping}
              className="flex items-center gap-2 px-4 py-2.5 bg-slate-900/80 border border-gray-700 text-gray-200 font-semibold rounded-lg hover:bg-slate-800 transition-colors text-sm"
            >
              <RefreshCw className={`w-4 h-4 text-lds-accent ${scraping ? 'animate-spin' : ''}`} />
              {scraping ? 'Polling Church Library...' : 'Poll Church Digital Library'}
            </button>
          </div>
        </div>
      </div>

      {/* Metrics Cards */}
      {stats && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-lds-cardBg border border-gray-800 p-5 rounded-xl">
            <span className="text-xs font-medium text-gray-400">1985 Hymns Cataloged</span>
            <div className="text-2xl font-bold text-white mt-1">{stats.count_1985}</div>
          </div>
          <div className="bg-lds-cardBg border border-gray-800 p-5 rounded-xl">
            <span className="text-xs font-medium text-gray-400">New Digital Releases</span>
            <div className="text-2xl font-bold text-emerald-400 mt-1">{stats.count_new}</div>
          </div>
          <div className="bg-lds-cardBg border border-gray-800 p-5 rounded-xl">
            <span className="text-xs font-medium text-gray-400">Traditional Christian Precursors</span>
            <div className="text-2xl font-bold text-amber-400 mt-1">{stats.count_original}</div>
          </div>
          <div className="bg-lds-cardBg border border-gray-800 p-5 rounded-xl">
            <span className="text-xs font-medium text-gray-400">AI Change Logs Generated</span>
            <div className="text-2xl font-bold text-lds-accent mt-1">{stats.count_change_logs}</div>
          </div>
        </div>
      )}

      {/* Filters & Catalog Search */}
      <div className="bg-lds-cardBg border border-gray-800 p-6 rounded-xl space-y-4">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="relative w-full sm:w-96">
            <Search className="w-4 h-4 text-gray-400 absolute left-3 top-3" />
            <input
              type="text"
              placeholder="Search hymns by title or lyrics..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-slate-950 border border-gray-800 rounded-lg pl-9 pr-4 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-lds-accent"
            />
          </div>

          <div className="flex items-center gap-3 w-full sm:w-auto">
            <Filter className="w-4 h-4 text-lds-accent" />
            <select
              value={selectedTheme}
              onChange={(e) => setSelectedTheme(e.target.value)}
              className="bg-slate-950 border border-gray-800 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-lds-accent"
            >
              <option value="">All Major Themes</option>
              <option value="Taken from Christianity">Taken from Christianity</option>
              <option value="LDS-specific">LDS-specific</option>
              <option value="National/Patriotic">National/Patriotic</option>
              <option value="Other">Other</option>
            </select>
          </div>
        </div>

        {/* Hymn List Grid */}
        {loading ? (
          <div className="py-12 text-center text-gray-400 text-sm">Loading catalog items...</div>
        ) : hymns.length === 0 ? (
          <div className="py-12 text-center text-gray-500 text-sm">No hymns found matching filter.</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 pt-4">
            {hymns.map((hymn) => (
              <div key={hymn.id} className="bg-slate-900/60 border border-gray-800 hover:border-lds-accent/50 p-5 rounded-xl transition-all space-y-3 flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-mono text-xs text-lds-accent font-bold bg-lds-accent/10 px-2 py-0.5 rounded border border-lds-accent/20">
                      #{hymn.hymn_number}
                    </span>
                    {hymn.major_theme && (
                      <span className="text-xs text-gray-400 bg-slate-950 px-2 py-0.5 rounded border border-gray-800">
                        {hymn.major_theme}
                      </span>
                    )}
                  </div>
                  <h3 className="font-bold text-white text-base">{hymn.title}</h3>
                  <p className="text-xs text-gray-400 font-serif line-clamp-3 mt-2 leading-relaxed">
                    {hymn.lyrics}
                  </p>
                </div>

                <div className="pt-3 border-t border-gray-800/60 flex items-center justify-between">
                  <span className="text-xs text-gray-500">1985 Hymnal</span>
                  <Link
                    href={`/compare?id=${hymn.id}`}
                    className="text-xs font-semibold text-lds-accent hover:underline flex items-center gap-1"
                  >
                    Compare <GitCompare className="w-3 h-3" />
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
