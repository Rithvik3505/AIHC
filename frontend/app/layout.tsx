import "@/styles/globals.css";
import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "AI Health Check",
  description: "AI Assurance diagnostics for Lendingtech startups"
};

const nav = [
  {href: "/dashboard", label: "Dashboard"},
  {href: "/evaluate", label: "Evaluate"},
  {href: "/reports", label: "Reports"},
  {href: "/taxonomy", label: "Taxonomy"},
  {href: "/benchmarks", label: "Benchmarks"}
];

export default function RootLayout({children}: {children: React.ReactNode}) {
  return (
    <html lang="en">
      <body>
        <div className="min-h-screen bg-surface text-ink">
          <aside className="fixed inset-y-0 left-0 hidden w-64 border-r border-white/10 bg-[#111b24] p-5 lg:block">
            <div className="mb-8">
              <div className="text-lg font-semibold">AI Health Check</div>
              <div className="text-sm text-muted">Lendingtech assurance</div>
            </div>
            <nav className="space-y-2">
              {nav.map((item) => (
                <Link className="block rounded-md px-3 py-2 text-sm text-muted hover:bg-white/5 hover:text-ink" href={item.href} key={item.href}>
                  {item.label}
                </Link>
              ))}
            </nav>
          </aside>
          <main className="min-w-0 lg:pl-64">
            <div className="mx-auto min-w-0 max-w-7xl px-5 py-6">{children}</div>
          </main>
        </div>
      </body>
    </html>
  );
}
