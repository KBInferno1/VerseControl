import Link from 'next/link';
import { BookOpen, GitCompare, RefreshCw, Sparkles } from 'lucide-react';

export default function Navbar() {
  return (
    <nav className="bg-lds-cardBg border-b border-gray-800 px-6 py-4 sticky top-0 z-50 shadow-md">
      <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
        <Link href="/" className="flex items-center gap-3 group">
          <div className="p-2 bg-gradient-to-tr from-lds-accent to-teal-500 rounded-lg text-slate-900 group-hover:scale-105 transition-transform">
            <BookOpen className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
              LDS Hymnal Catalog <span className="text-xs px-2 py-0.5 rounded bg-lds-gold/20 text-lds-gold border border-lds-gold/30">AI Analysis</span>
            </h1>
            <p className="text-xs text-gray-400">1985 Hymnal ↔ New "Hymns—for Home and Church" ↔ Traditional Christian Originals</p>
          </div>
        </Link>

        <div className="flex items-center gap-4">
          <Link
            href="/"
            className="flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium text-gray-300 hover:text-white hover:bg-gray-800 transition-colors"
          >
            <BookOpen className="w-4 h-4 text-lds-accent" />
            Catalog
          </Link>
          <Link
            href="/compare"
            className="flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium bg-lds-accent/10 border border-lds-accent/30 text-lds-accent hover:bg-lds-accent/20 transition-colors"
          >
            <GitCompare className="w-4 h-4" />
            3-Way Comparison
          </Link>
        </div>
      </div>
    </nav>
  );
}
