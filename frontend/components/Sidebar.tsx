'use client';

import React from 'react';
import {
  LayoutDashboard,
  MessageSquareCode,
  Receipt,
  PiggyBank,
  FileText,
  Activity,
  ShieldCheck,
  ChevronRight
} from 'lucide-react';

export type ActiveTab = 'dashboard' | 'assistant' | 'transactions' | 'budgets' | 'documents' | 'system';

interface SidebarProps {
  activeTab: ActiveTab;
  onTabChange: (tab: ActiveTab) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, onTabChange }) => {
  const navItems: { id: ActiveTab; label: string; icon: React.ElementType; badge?: string }[] = [
    { id: 'dashboard', label: 'Financial Dashboard', icon: LayoutDashboard },
    { id: 'assistant', label: 'AI Copilot Assistant', icon: MessageSquareCode, badge: 'RAG' },
    { id: 'transactions', label: 'Transactions', icon: Receipt },
    { id: 'budgets', label: 'Budgets & Goals', icon: PiggyBank },
    { id: 'documents', label: 'Document Center', icon: FileText },
    { id: 'system', label: 'System & Evaluation', icon: Activity, badge: 'Live' },
  ];

  return (
    <aside className="w-64 border-r border-slate-800 bg-[#0a0f1c] p-4 flex flex-col justify-between shrink-0 min-h-[calc(100vh-65px)]">
      <div>
        <div className="px-3 py-2 text-[11px] font-semibold tracking-wider text-slate-400 uppercase">
          Navigation
        </div>
        <nav className="space-y-1.5 mt-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onTabChange(item.id)}
                className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-teal-950/70 text-teal-300 border border-teal-800/60 shadow-md shadow-teal-950/50'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
                }`}
              >
                <div className="flex items-center gap-3">
                  <Icon className={`w-4 h-4 ${isActive ? 'text-teal-400' : 'text-slate-500'}`} />
                  <span>{item.label}</span>
                </div>
                {item.badge && (
                  <span className={`text-[10px] px-1.5 py-0.5 rounded font-bold ${
                    isActive ? 'bg-teal-800/80 text-teal-200' : 'bg-slate-800 text-slate-400'
                  }`}>
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Security & Verification Card */}
      <div className="p-3.5 rounded-xl bg-slate-900/70 border border-slate-800/80 mt-6">
        <div className="flex items-center gap-2 mb-1.5 text-xs font-semibold text-slate-300">
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
          <span>FDE System Verified</span>
        </div>
        <p className="text-[11px] text-slate-400 leading-relaxed">
          Deterministic arithmetic, tenant isolation, pgvector RAG, and prompt injection filters active.
        </p>
      </div>
    </aside>
  );
};
