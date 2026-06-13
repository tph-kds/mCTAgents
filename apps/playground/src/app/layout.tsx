import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "mCTAgents Playground",
  description: "Interactive playground for mCTAgents social reasoning",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <nav className="border-b border-gray-800 px-6 py-3">
          <div className="flex items-center justify-between">
            <a href="/" className="text-lg font-bold">mCTAgents Playground</a>
            <div className="flex gap-4 text-sm text-gray-400">
              <a href="/" className="hover:text-white">Home</a>
              <a href="/compare" className="hover:text-white">Compare</a>
            </div>
          </div>
        </nav>
        <main className="max-w-6xl mx-auto px-6 py-8">{children}</main>
      </body>
    </html>
  );
}
