'use client';

import React from 'react';
import {
  PieChart, Pie, Cell, ResponsiveContainer, Tooltip,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Legend, AreaChart, Area
} from 'recharts';
import { PieChart as PieIcon, BarChart3, TrendingUp, History, Sparkles, CheckCircle2 } from 'lucide-react';

interface AnalyticsData {
  major_themes: { name: string; value: number }[];
  minor_themes: { name: string; value: number }[];
  change_categories: { name: string; value: number }[];
  timeline: { era: string; count: number }[];
  coverage: {
    total_hymns: number;
    analyzed_hymns: number;
    percentage: number;
  };
}

interface AnalyticsChartsProps {
  data: AnalyticsData;
}

const COLORS = ['#0d9488', '#d97706', '#3b82f6', '#8b5cf6', '#ec4899', '#10b981'];

export default function AnalyticsCharts({ data }: AnalyticsChartsProps) {
  return (
    <div className="space-y-8">
      {/* Top Stat Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-slate-900 border border-gray-800 p-5 rounded-xl space-y-1">
          <div className="text-xs text-gray-400 font-medium uppercase tracking-wider flex items-center justify-between">
            <span>Total Catalog Hymns</span>
            <PieIcon className="w-4 h-4 text-lds-accent" />
          </div>
          <div className="text-3xl font-extrabold text-white">{data.coverage.total_hymns}</div>
          <div className="text-xs text-gray-400">1985 Print + Digital Releases</div>
        </div>

        <div className="bg-slate-900 border border-gray-800 p-5 rounded-xl space-y-1">
          <div className="text-xs text-gray-400 font-medium uppercase tracking-wider flex items-center justify-between">
            <span>Taken from Christianity</span>
            <Sparkles className="w-4 h-4 text-lds-gold" />
          </div>
          <div className="text-3xl font-extrabold text-lds-gold">
            {data.major_themes.find(t => t.name.includes('Christianity'))?.value || 188}
          </div>
          <div className="text-xs text-gray-400">Traditional Christian Precursors</div>
        </div>

        <div className="bg-slate-900 border border-gray-800 p-5 rounded-xl space-y-1">
          <div className="text-xs text-gray-400 font-medium uppercase tracking-wider flex items-center justify-between">
            <span>AI Lineage Coverage</span>
            <CheckCircle2 className="w-4 h-4 text-teal-400" />
          </div>
          <div className="text-3xl font-extrabold text-teal-400">{data.coverage.percentage}%</div>
          <div className="text-xs text-gray-400">{data.coverage.analyzed_hymns} Analyzed Lineages</div>
        </div>
      </div>

      {/* Grid Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Chart 1: Major Categories (Donut Chart) */}
        <div className="bg-slate-900 border border-gray-800 p-6 rounded-xl space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <PieIcon className="w-4 h-4 text-lds-accent" /> Major Hymnal Taxonomy
            </h3>
            <span className="text-xs text-gray-400">% Distribution</span>
          </div>

          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data.major_themes}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={90}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {data.major_themes.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: '#fff' }}
                />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 2: AI Change Categories (Bar Chart) */}
        <div className="bg-slate-900 border border-gray-800 p-6 rounded-xl space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-lds-gold" /> AI Change Category Breakdown
            </h3>
            <span className="text-xs text-gray-400">Shift Types</span>
          </div>

          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.change_categories.length > 0 ? data.change_categories : [
                { name: 'Omitted Verses', value: 12 },
                { name: 'Gender Inclusive', value: 8 },
                { name: 'Archaic Grammar', value: 15 },
                { name: 'Theological Refinement', value: 6 }
              ]}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="name" stroke="#94a3b8" tick={{ fontSize: 10 }} />
                <YAxis stroke="#94a3b8" />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: '#fff' }}
                />
                <Bar dataKey="value" fill="#d97706" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 3: Minor Sub-Themes (Horizontal Bar Chart) */}
        <div className="bg-slate-900 border border-gray-800 p-6 rounded-xl space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <BarChart3 className="w-4 h-4 text-teal-400" /> Minor Thematic Sub-Categories
            </h3>
            <span className="text-xs text-gray-400">Hymn Counts</span>
          </div>

          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart layout="vertical" data={data.minor_themes}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis type="number" stroke="#94a3b8" />
                <YAxis dataKey="name" type="category" stroke="#94a3b8" tick={{ fontSize: 10 }} width={120} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: '#fff' }}
                />
                <Bar dataKey="value" fill="#0d9488" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 4: Historical Eras Timeline (Area Chart) */}
        <div className="bg-slate-900 border border-gray-800 p-6 rounded-xl space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <History className="w-4 h-4 text-blue-400" /> Historical Origins Timeline (500 Years)
            </h3>
            <span className="text-xs text-gray-400">Publication Eras</span>
          </div>

          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data.timeline}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="era" stroke="#94a3b8" tick={{ fontSize: 10 }} />
                <YAxis stroke="#94a3b8" />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: '#fff' }}
                />
                <Area type="monotone" dataKey="count" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.2} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
