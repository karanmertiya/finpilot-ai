import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "FinPilot AI — Personal Financial Intelligence Copilot",
  description: "Production-grade AI fintech copilot combining deterministic calculations, document RAG, anomaly detection, and controlled agentic workflows.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark h-full antialiased">
      <body className="min-h-full flex flex-col bg-[#090e17] text-slate-100">
        {children}
      </body>
    </html>
  );
}
