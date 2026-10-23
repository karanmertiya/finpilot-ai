'use client';

import React, { useState } from 'react';
import { X, Calculator, ShieldCheck, ArrowRight, Percent, Calendar, DollarSign } from 'lucide-react';
import { api } from '@/lib/api';

interface CalculatorModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const CalculatorModal: React.FC<CalculatorModalProps> = ({ isOpen, onClose }) => {
  const [activeTab, setActiveTab] = useState<'emi' | 'affordability'>('emi');

  // EMI State
  const [principal, setPrincipal] = useState(2000000);
  const [rate, setRate] = useState(8.5);
  const [tenureYears, setTenureYears] = useState(20);
  const [emiResult, setEmiResult] = useState<any | null>(null);
  const [emiLoading, setEmiLoading] = useState(false);

  // Affordability State
  const [proposedEmi, setProposedEmi] = useState(25000);
  const [existingEmis, setExistingEmis] = useState(0);
  const [affResult, setAffResult] = useState<any | null>(null);
  const [affLoading, setAffLoading] = useState(false);

  if (!isOpen) return null;

  const handleCalculateEMI = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setEmiLoading(true);
    try {
      const res = await api.calculateEMI(principal, rate, tenureYears * 12);
      setEmiResult(res);
    } catch (err) {
      console.error(err);
    } finally {
      setEmiLoading(false);
    }
  };

  const handleCalculateAffordability = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setAffLoading(true);
    try {
      const res = await api.calculateAffordability(proposedEmi, existingEmis);
      setAffResult(res);
    } catch (err) {
      console.error(err);
    } finally {
      setAffLoading(false);
    }
  };

  const formatINR = (val: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(val);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4">
      <div className="w-full max-w-xl max-h-[90vh] overflow-y-auto rounded-2xl bg-[#0f182a] border border-[#1e2c45] p-6 shadow-2xl relative">
        <button
          onClick={onClose}
          className="absolute right-4 top-4 text-slate-400 hover:text-white"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Modal Header */}
        <div className="flex items-center gap-2.5 mb-4">
          <div className="p-2 rounded-xl bg-teal-500/10 text-teal-400">
            <Calculator className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white">Deterministic Financial Calculators</h3>
            <p className="text-xs text-slate-400">Verified math using reducing-balance amortization and DTI thresholds</p>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-slate-800 mb-5">
          <button
            onClick={() => setActiveTab('emi')}
            className={`pb-2.5 px-4 text-xs font-semibold border-b-2 transition-all ${
              activeTab === 'emi'
                ? 'border-teal-400 text-teal-300'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            Loan EMI Amortization
          </button>
          <button
            onClick={() => setActiveTab('affordability')}
            className={`pb-2.5 px-4 text-xs font-semibold border-b-2 transition-all ${
              activeTab === 'affordability'
                ? 'border-teal-400 text-teal-300'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            Cash Flow Affordability
          </button>
        </div>

        {/* EMI Calculator Tab */}
        {activeTab === 'emi' && (
          <div className="space-y-4">
            <form onSubmit={handleCalculateEMI} className="space-y-3.5">
              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-slate-300">Loan Principal (₹)</span>
                  <span className="font-mono font-bold text-white">{formatINR(principal)}</span>
                </div>
                <input
                  type="range"
                  min="100000"
                  max="10000000"
                  step="50000"
                  value={principal}
                  onChange={(e) => setPrincipal(Number(e.target.value))}
                  className="w-full accent-teal-500"
                />
              </div>

              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-slate-300">Annual Interest Rate (%)</span>
                  <span className="font-mono font-bold text-white">{rate}%</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="20"
                  step="0.1"
                  value={rate}
                  onChange={(e) => setRate(Number(e.target.value))}
                  className="w-full accent-teal-500"
                />
              </div>

              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-slate-300">Tenure (Years)</span>
                  <span className="font-mono font-bold text-white">{tenureYears} Years ({tenureYears * 12} mo)</span>
                </div>
                <input
                  type="range"
                  min="1"
                  max="30"
                  step="1"
                  value={tenureYears}
                  onChange={(e) => setTenureYears(Number(e.target.value))}
                  className="w-full accent-teal-500"
                />
              </div>

              <button
                type="submit"
                disabled={emiLoading}
                className="w-full py-2.5 rounded-xl bg-teal-600 hover:bg-teal-500 text-white text-xs font-semibold shadow-md"
              >
                {emiLoading ? 'Calculating...' : 'Compute Amortization'}
              </button>
            </form>

            {emiResult && (
              <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-3 text-xs">
                <div className="grid grid-cols-2 gap-3 pb-3 border-b border-slate-800 text-center">
                  <div>
                    <span className="text-slate-400">Monthly EMI</span>
                    <div className="text-xl font-bold font-mono text-teal-400 mt-0.5">
                      {formatINR(emiResult.monthly_emi)}
                    </div>
                  </div>
                  <div>
                    <span className="text-slate-400">Total Interest Payable</span>
                    <div className="text-xl font-bold font-mono text-white mt-0.5">
                      {formatINR(emiResult.total_interest)}
                    </div>
                  </div>
                </div>

                <div className="flex justify-between text-slate-300">
                  <span>Total Repayment Amount:</span>
                  <span className="font-bold text-white">{formatINR(emiResult.total_payment)}</span>
                </div>
                <div className="flex justify-between text-slate-300">
                  <span>Interest-to-Principal Ratio:</span>
                  <span className="font-bold text-amber-400">{(emiResult.interest_to_principal_ratio * 100).toFixed(1)}%</span>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Affordability Tab */}
        {activeTab === 'affordability' && (
          <div className="space-y-4">
            <form onSubmit={handleCalculateAffordability} className="space-y-3.5">
              <div>
                <label className="block text-xs text-slate-300 mb-1">Proposed Monthly EMI (₹)</label>
                <input
                  type="number"
                  required
                  min="1000"
                  value={proposedEmi}
                  onChange={(e) => setProposedEmi(Number(e.target.value))}
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white"
                />
              </div>

              <div>
                <label className="block text-xs text-slate-300 mb-1">Existing Active Monthly EMIs (₹)</label>
                <input
                  type="number"
                  min="0"
                  value={existingEmis}
                  onChange={(e) => setExistingEmis(Number(e.target.value))}
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white"
                />
              </div>

              <button
                type="submit"
                disabled={affLoading}
                className="w-full py-2.5 rounded-xl bg-teal-600 hover:bg-teal-500 text-white text-xs font-semibold shadow-md"
              >
                {affLoading ? 'Evaluating Disposable Cash Flow...' : 'Check Affordability'}
              </button>
            </form>

            {affResult && (
              <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-3 text-xs">
                <div className="flex items-center justify-between">
                  <span className="text-slate-300 font-semibold">Affordability Verdict:</span>
                  <span className={`px-2.5 py-0.5 rounded-full font-bold text-[10px] ${
                    affResult.affordability_verdict === 'AFFORDABLE'
                      ? 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                      : affResult.affordability_verdict === 'TIGHT'
                      ? 'bg-amber-950 text-amber-300 border border-amber-800'
                      : 'bg-rose-950 text-rose-300 border border-rose-800'
                  }`}>
                    {affResult.affordability_verdict}
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-2 text-[11px] text-slate-300 py-1">
                  <div>Debt-To-Income (DTI): <strong className="text-white">{affResult.debt_to_income_ratio}%</strong></div>
                  <div>Projected Surplus: <strong className="text-white">{formatINR(affResult.remaining_disposable_cash_flow)}</strong></div>
                </div>

                <p className="text-slate-300 leading-relaxed text-[11px]">{affResult.analysis_text}</p>

                <div className="pt-2 border-t border-slate-800 text-[10px] text-slate-400">
                  <span className="italic">*Illustrative estimate based on your recorded 3-month spending. Does not constitute guaranteed lending approval.</span>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
