import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "mCTAgents Studio",
  description: "Immersive Social Reasoning Workspace",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-[#030712] text-slate-200 antialiased">
        {/* Top nav bar */}
        <nav className="fixed top-0 left-0 right-0 z-50 glass-panel-solid border-b border-white/5">
          <div className="h-12 px-4 flex items-center justify-between">
            {/* Left: logo + title */}
            <div className="flex items-center gap-3">
              <div className="relative w-7 h-7 flex items-center justify-center">
                <div className="absolute inset-0 rounded-lg bg-blue-500/20 blur-sm" />
                <svg viewBox="0 0 24 24" className="relative w-5 h-5 text-blue-400" fill="none" stroke="currentColor" strokeWidth="2">
                  <polygon points="12,2 22,8.5 22,15.5 12,22 2,15.5 2,8.5" />
                  <line x1="12" y1="22" x2="12" y2="15.5" />
                  <polyline points="22,8.5 12,15.5 2,8.5" />
                </svg>
              </div>
              <span className="text-sm font-semibold tracking-wide text-glow-blue">
                mCTAgents
              </span>
              <span className="text-[10px] text-blue-400/60 font-mono ml-1">STUDIO</span>
            </div>

            {/* Center: nav links */}
            <div className="flex items-center gap-1">
              <a
                href="/"
                className="px-3 py-1.5 text-xs font-medium text-slate-400 hover:text-white rounded-md hover:bg-white/5 transition-colors"
              >
                Sessions
              </a>
              <a
                href="/runs/new"
                className="px-3 py-1.5 text-xs font-medium text-slate-400 hover:text-white rounded-md hover:bg-white/5 transition-colors"
              >
                New Session
              </a>
              <a
                href="https://github.com/mctagents/mctagents"
                target="_blank"
                rel="noopener noreferrer"
                className="px-3 py-1.5 text-xs font-medium text-slate-400 hover:text-white rounded-md hover:bg-white/5 transition-colors"
              >
                GitHub
              </a>
            </div>

            {/* Right: status indicator */}
            <div className="flex items-center gap-2">
              <div className="flex items-center gap-1.5">
                <div className="w-1.5 h-1.5 rounded-full bg-green-500 pulse-ring" />
                <span className="text-[10px] font-mono text-slate-500">ONLINE</span>
              </div>
            </div>
          </div>
          {/* Phase accent line */}
          <div className="phase-strip" />
        </nav>

        {/* Main content area */}
        <main className="pt-14 min-h-screen">
          {children}
        </main>
      </body>
    </html>
  );
}
