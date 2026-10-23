'use client';

import React, { useState, useEffect } from 'react';
import {
  PiggyBank,
  Target,
  AlertCircle,
  Plus,
  TrendingUp,
  CheckCircle2,
  Calendar,
  Sparkles
} from 'lucide-react';
import { api } from '@/lib/api';
import { BudgetVsActual, SavingsGoal } from '@/lib/types';

export const BudgetsView: React.FC = () => {
  const [budgets, setBudgets] = useState<BudgetVsActual[]>([]);
  const [goals, setGoals] = useState<SavingsGoal[]>([]);
  const [loading, setLoading] = useState(true);

  // New Goal Form State
  const [goalTitle, setGoalTitle] = useState('');
  const [goalTarget, setGoalTarget] = useState('');
  const [goalCurrent, setGoalCurrent] = useState('');
  const [goalDate, setGoalDate] = useState('2027-06-30');
  const [isGoalModalOpen, setIsGoalModalOpen] = useState(false);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [bData, gData] = await Promise.all([
        api.getBudgets(),
        api.getSavingsGoals()
      ]);
      setBudgets(bData);
      setGoals(gData);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleCreateGoal = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!goalTitle || !goalTarget) return;

    try {
      await api.createSavingsGoal({
        title: goalTitle,
        target_amount: parseFloat(goalTarget),
        current_amount: parseFloat(goalCurrent || '0'),
        target_date: goalDate
      });
      setIsGoalModalOpen(false);
      setGoalTitle('');
      setGoalTarget('');
      setGoalCurrent('');
      fetchData();
    } catch (err) {
      console.error(err);
    }
  };

  const formatINR = (val: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(val);
  };

  const overBudgetCount = budgets.filter((b) => b.is_over_budget).length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-5 rounded-2xl bg-[#0f182a] border border-[#1e2c45]">
        <div>
          <h2 className="text-base font-bold text-white">Budgets & Strategic Financial Goals</h2>
          <p className="text-xs text-slate-400">Track monthly allocations against actual expenses and monitor savings horizons</p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setIsGoalModalOpen(true)}
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-teal-600 hover:bg-teal-500 text-white text-xs font-semibold transition-all shadow-md active:scale-95"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Create Savings Goal</span>
          </button>
        </div>
      </div>

      {/* AI Budget Alert Banner if Over Budget */}
      {overBudgetCount > 0 && (
        <div className="p-4 rounded-2xl bg-rose-950/40 border border-rose-800/60 flex items-center gap-3">
          <AlertCircle className="w-5 h-5 text-rose-400 shrink-0" />
          <div className="text-xs">
            <span className="font-bold text-rose-300">Budget Threshold Notice: </span>
            <span className="text-slate-200">
              {overBudgetCount} category is exceeding its planned monthly limit (e.g. Shopping due to one-off electronics purchase).
              Remaining categories are within planned discipline.
            </span>
          </div>
        </div>
      )}

      {/* Category Budgets Grid */}
      <div className="space-y-3">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 px-1">
          Monthly Category Spending vs Limits
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {budgets.map((b) => (
            <div
              key={b.category_id}
              className="p-5 rounded-2xl bg-[#0f182a] border border-[#1e2c45] space-y-3 hover:border-slate-700 transition-all"
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-white">{b.category_name}</span>
                <span
                  className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                    b.is_over_budget ? 'bg-rose-950 text-rose-300 border border-rose-800' : 'bg-teal-950 text-teal-300 border border-teal-800'
                  }`}
                >
                  {b.percentage_used.toFixed(0)}%
                </span>
              </div>

              <div>
                <div className="text-xl font-bold font-mono text-white">
                  {formatINR(b.actual_spent)}
                </div>
                <div className="text-[11px] text-slate-400 mt-0.5">
                  Limit: {formatINR(b.budget_limit)}
                </div>
              </div>

              {/* Progress bar */}
              <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all ${
                    b.is_over_budget ? 'bg-rose-500' : 'bg-teal-500'
                  }`}
                  style={{ width: `${Math.min(b.percentage_used, 100)}%` }}
                />
              </div>

              <div className="text-[10px] text-slate-400 pt-1 border-t border-slate-800/80 flex items-center justify-between">
                <span>{b.is_over_budget ? 'Over Limit by' : 'Surplus Remaining'}</span>
                <span className={`font-mono font-semibold ${b.is_over_budget ? 'text-rose-400' : 'text-emerald-400'}`}>
                  {formatINR(Math.abs(b.remaining))}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Savings Goals Horizons */}
      <div className="space-y-3 pt-4">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 px-1">
          Active Savings Horizons & Capital Targets
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {goals.map((g) => (
            <div
              key={g.id}
              className="p-5 rounded-2xl bg-[#0f182a] border border-[#1e2c45] space-y-4 hover:border-teal-500/30 transition-all relative overflow-hidden"
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex items-center gap-2">
                  <div className="p-2 rounded-xl bg-teal-500/10 text-teal-300">
                    <Target className="w-4 h-4" />
                  </div>
                  <div>
                    <h4 className="text-xs font-bold text-white line-clamp-1">{g.title}</h4>
                    <p className="text-[10px] text-slate-400 flex items-center gap-1 mt-0.5">
                      <Calendar className="w-3 h-3" /> Target Date: {g.target_date || 'Flexible'}
                    </p>
                  </div>
                </div>
              </div>

              <div>
                <div className="flex items-baseline justify-between text-xs mb-1.5">
                  <span className="font-bold font-mono text-lg text-white">{formatINR(g.current_amount)}</span>
                  <span className="text-slate-400 text-xs">of {formatINR(g.target_amount)}</span>
                </div>

                <div className="w-full bg-slate-800 h-2.5 rounded-full overflow-hidden">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-teal-500 to-emerald-400 transition-all"
                    style={{ width: `${Math.min(g.progress_percentage, 100)}%` }}
                  />
                </div>
              </div>

              <div className="flex items-center justify-between text-xs text-slate-400 pt-1">
                <span>Progress</span>
                <span className="font-bold text-teal-400">{g.progress_percentage.toFixed(1)}%</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Modal: Create Goal */}
      {isGoalModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="w-full max-w-md rounded-2xl bg-[#0f182a] border border-[#1e2c45] p-6 shadow-2xl">
            <h3 className="text-sm font-bold text-white mb-1">Set New Savings Goal</h3>
            <p className="text-xs text-slate-400 mb-4">Define a target fund with a target amount in INR.</p>

            <form onSubmit={handleCreateGoal} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Goal Name</label>
                <input
                  type="text"
                  required
                  value={goalTitle}
                  onChange={(e) => setGoalTitle(e.target.value)}
                  placeholder="e.g., Higher Education Fund"
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Target Amount (₹)</label>
                  <input
                    type="number"
                    required
                    min="1000"
                    value={goalTarget}
                    onChange={(e) => setGoalTarget(e.target.value)}
                    placeholder="500000"
                    className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Initial Saved (₹)</label>
                  <input
                    type="number"
                    min="0"
                    value={goalCurrent}
                    onChange={(e) => setGoalCurrent(e.target.value)}
                    placeholder="50000"
                    className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Target Completion Date</label>
                <input
                  type="date"
                  value={goalDate}
                  onChange={(e) => setGoalDate(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setIsGoalModalOpen(false)}
                  className="px-4 py-2 rounded-xl bg-slate-800 text-slate-300 text-xs"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-xl bg-teal-600 hover:bg-teal-500 text-white text-xs font-semibold"
                >
                  Create Goal
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
