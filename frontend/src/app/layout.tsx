/**
 * Root layout
 */
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Ad Intelligence Platform',
  description: 'Discover and analyze ads across Meta, TikTok, and YouTube',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.className} bg-background text-foreground antialiased`}>
        <div className="min-h-screen flex flex-col">
          {/* Header */}
          <header className="sticky top-0 z-50 border-b border-border bg-background/95 backdrop-blur">
            <div className="container mx-auto px-4 py-4">
              <div className="flex items-center justify-between">
                <a href="/" className="text-xl font-bold">
                  Ad Intelligence
                </a>

                <nav className="flex gap-6">
                  <a href="/" className="text-sm hover:text-primary transition">
                    Home
                  </a>
                  <a href="/about" className="text-sm hover:text-primary transition">
                    About
                  </a>
                </nav>
              </div>
            </div>
          </header>

          {/* Main content */}
          <main className="flex-1">{children}</main>

          {/* Footer */}
          <footer className="border-t border-border py-8">
            <div className="container mx-auto px-4 text-center text-sm text-gray-400">
              <p>Ad Intelligence Platform v0.1 • Built for demo purposes</p>
            </div>
          </footer>
        </div>
      </body>
    </html>
  );
}
