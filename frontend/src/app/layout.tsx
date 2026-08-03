import './globals.css';
import Navbar from '@/components/Navbar';

export const metadata = {
  title: 'VerseControl - LDS Hymnal Theological & Lyrical Comparison Tool',
  description: 'Catalog, compare, and analyze lyrical and theological changes between the 1985 LDS hymnal, new digital releases, and traditional Christian origins.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-lds-darkBg text-slate-100 min-h-screen flex flex-col antialiased">
        <Navbar />
        <main className="flex-1 max-w-7xl w-full mx-auto px-6 py-8">
          {children}
        </main>
        <footer className="border-t border-gray-800 bg-lds-cardBg py-6 px-6 text-center text-xs text-gray-500">
          LDS Hymnal Theological & Lyrical Comparison System • Deployed via Docker Compose & Portainer
        </footer>
      </body>
    </html>
  );
}
