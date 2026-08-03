function getApiBaseUrl(): string {
  if (process.env.NEXT_PUBLIC_API_URL && process.env.NEXT_PUBLIC_API_URL !== 'http://localhost:8000') {
    return process.env.NEXT_PUBLIC_API_URL;
  }
  if (typeof window !== 'undefined') {
    return `${window.location.protocol}//${window.location.hostname}:8000`;
  }
  return 'http://localhost:8000';
}

export interface Hymn1985 {
  id: number;
  hymn_number: number;
  title: string;
  lyrics: string;
  major_theme: string | null;
  minor_theme: string | null;
  original_hymn_id: number | null;
}

export interface HymnNew {
  id: number;
  hymn_number: number;
  title: string;
  lyrics: string;
  major_theme: string | null;
  minor_theme: string | null;
  batch_release: string;
  hymn_1985_id: number | null;
  original_hymn_id: number | null;
}

export interface HymnOriginal {
  id: number;
  title: string;
  original_author: string | null;
  publication_year: number | null;
  original_source: string | null;
  lyrics: string;
  major_theme: string | null;
  minor_theme: string | null;
}

export interface HymnLineageItem {
  id_1985: number;
  number_1985: number;
  title_1985: string;
  lyrics_1985: string;
  major_theme: string | null;
  minor_theme: string | null;
  id_new: number | null;
  number_new: number | null;
  title_new: string | null;
  lyrics_new: string | null;
  batch_release: string | null;
  id_original: number | null;
  title_original: string | null;
  original_author: string | null;
  publication_year: number | null;
  lyrics_original: string | null;
  change_log_id: number | null;
  summary: string | null;
  omitted_verses: any;
  altered_phrases: any;
  change_categories: any;
}

export async function fetchStats() {
  const res = await fetch(`${getApiBaseUrl()}/api/stats`, { cache: 'no-store' });
  if (!res.ok) throw new Error('Failed to fetch stats');
  return res.json();
}

export async function fetch1985Hymns(query?: string, theme?: string) {
  const params = new URLSearchParams();
  if (query) params.append('query', query);
  if (theme) params.append('major_theme', theme);
  
  const res = await fetch(`${getApiBaseUrl()}/api/hymns/1985?${params.toString()}`, { cache: 'no-store' });
  if (!res.ok) throw new Error('Failed to fetch 1985 hymns');
  return res.json();
}

export async function fetchHymnLineage(): Promise<HymnLineageItem[]> {
  const res = await fetch(`${getApiBaseUrl()}/api/hymns/lineage`, { cache: 'no-store' });
  if (!res.ok) throw new Error('Failed to fetch hymn lineage');
  return res.json();
}

export async function triggerAIComparison(hymn1985Id: number, hymnNewId?: number) {
  const res = await fetch(`${getApiBaseUrl()}/api/compare/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ hymn_1985_id: hymn1985Id, hymn_new_id: hymnNewId }),
  });
  if (!res.ok) {
    const errorData = await res.json();
    throw new Error(errorData.detail || 'Failed to execute AI comparison');
  }
  return res.json();
}

export async function triggerScraper() {
  const res = await fetch(`${getApiBaseUrl()}/api/scrape/trigger`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to trigger scraper');
  return res.json();
}

export async function triggerSeedPopulation() {
  const res = await fetch(`${getApiBaseUrl()}/api/seed/populate`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to populate hymnal dataset');
  return res.json();
}

export async function triggerDatabaseCleanup() {
  const res = await fetch(`${getApiBaseUrl()}/api/db/cleanup`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to clean up database duplicates');
  return res.json();
}
