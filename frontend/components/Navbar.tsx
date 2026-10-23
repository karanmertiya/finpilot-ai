'use client';

import React from 'react';
import { Compass, Sparkles, Calculator, CheckCircle2, Shield } from 'lucide-react';

interface NavbarProps {
  onOpenCalculator: () => void;
  apiHealthy: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({ onOpenCalculator, apiHealthy }) => {
  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-800 bg-[#090e17]/90 backdrop-blur-md px-6 py-3.5 flex items-center justify-between">
      {/* Brand */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-teal-500 to-emerald-600 flex items-center justify-center shadow-lg shadow-teal-500/20">
          <Compass className="w-5 h-5 text-white" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <span className="font-bold text-lg tracking-tight text-white">FinPilot <span className="text-teal-400">AI</span></span>
            <span className="px-2 py-0.5 text-[10px] font-semibold bg-teal-950/80 text-teal-300 border border-teal-800/60 rounded-full">
              FDE PORTFOLIO
            </span>
          </div>
          <p className="text-xs text-slate-400">Personal Financial Intelligence Copilot</p>
        </div>
      </div>

      {/* Middle Pill: Synthetic Data Notice */}
      <div className="hidden md:flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-slate-900 border border-slate-800 text-xs text-slate-300 shadow-inner">
        <Sparkles className="w-3.5 h-3.5 text-amber-400 animate-pulse" />
        <span>Demonstration Dataset: <strong className="text-white font-medium">Synthetic Indian Financial Records (INR ₹)</strong></span>
      </div>

      {/* Right Controls */}
      <div className="flex items-center gap-3">
        {/* Backend health status */}
        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-slate-900/80 border border-slate-800 text-xs">
          <span className={`w-2 h-2 rounded-full ${apiHealthy ? 'bg-emerald-400 animate-pulse' : 'bg-rose-500'}`} />
          <span className="text-slate-400 hidden sm:inline">{apiHealthy ? 'API Online' : 'Connecting...'}</span>
        </div>

        {/* Quick Calculator Modal */}
        <button
          onClick={onOpenCalculator}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-teal-600 hover:bg-teal-500 text-white text-xs font-medium transition-all shadow-md shadow-teal-600/20 active:scale-95"
        >
          <Calculator className="w-3.5 h-3.5" />
          <span>EMI & Affordability</span>
        </button>

        {/* Demo User Avatar */}
        <div className="flex items-center gap-2.5 pl-2 border-l border-slate-800">
          <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-slate-700 to-slate-800 border border-slate-700 flex items-center justify-center text-xs font-semibold text-teal-300">
            AS
          </div>
          <div className="hidden lg:block text-left">
            <p className="text-xs font-medium text-white leading-tight">Aarav Sharma</p>
            <p className="text-[10px] text-teal-400 leading-tight">Demo Account</p>
          </div>
        </div>
      </div>
    </header>
  );
};
