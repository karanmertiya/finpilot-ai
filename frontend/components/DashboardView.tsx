'use client';

import React from 'react';
import {
  TrendingUp,
  TrendingDown,
  Wallet,
  PiggyBank,
  AlertTriangle,
  ArrowUpRight,
  ShieldAlert,
  Sparkles,
  ExternalLink
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { DashboardMetrics } from '@/lib/types';

interface DashboardViewProps {
  metrics: DashboardMetrics | null;
  loading: boolean;
  onNavigateToAssistant: () => void;
  onNavigateToTransactions: () => void;
}

export const DashboardView: React.FC<DashboardViewProps> = ({
  metrics,
  loading,
  onNavigateToAssistant,
  onNavigateToTransactions
}) => {
  if (loading || !metrics) {
    return (
      <div className="space-y-6 animate-pulse">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-32 bg-slate-900 rounded-2xl border border-slate-800" />
          ))}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 h-80 bg-slate-900 rounded-2xl border border-slate-800" />
          <div className="h-80 bg-slate-900 rounded-2xl border border-slate-800" />
        </div>
      </div>
    );
  }

  const formatINR = (val: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(val);
  };

  return (
    <div className="space-y-6">
      {/* AI Financial Summary Banner */}
      <div className="relative overflow-hidden rounded-2xl border border-teal-800/40 bg-gradient-to-r from-[#0d2836] via-[#0f2136] to-[#0a1526] p-5 shadow-xl">
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-start gap-3.5">
            <div className="p-2.5 rounded-xl bg-teal-500/10 border border-teal-500/30 text-teal-300 shrink-0">
              <Sparkles className="w-5 h-5 animate-pulse" />
            </div>
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="text-xs font-bold uppercase tracking-wider text-teal-400">Verified Intelligence Brief</span>
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-teal-900/60 text-teal-200 border border-teal-800">Deterministic Analysis</span>
              </div>
              <p className="text-sm text-slate-200 leading-relaxed max-w-4xl">
                {metrics.ai_financial_summary}
              </p>
            </div>
          </div>
          <button
            onClick={onNavigateToAssistant}
            className="hidden sm:flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-teal-600 hover:bg-teal-500 text-white text-xs font-semibold shrink-0 transition-all shadow-md active:scale-95"
          >
            <span>Ask Copilot</span>
            <ArrowUpRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Top Key Metrics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Income */}
        <div className="p-5 rounded-2xl bg-[#0f182a] border border-[#1e2c45] relative overflow-hidden group hover:border-slate-700 transition-all">
          <div className="flex items-center justify-between text-slate-400 mb-2 text-xs font-medium">
            <span>Total Income</span>
            <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400">
              <TrendingUp className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-white tracking-tight">
            {formatINR(metrics.total_income)}
          </div>
          <p className="text-[11px] text-emerald-400 mt-2 font-medium flex items-center gap-1">
            <span>Verified Salary & Inflows</span>
          </p>
        </div>

        {/* Total Expenses */}
        <div className="p-5 rounded-2xl bg-[#0f182a] border border-[#1e2c45] relative overflow-hidden group hover:border-slate-700 transition-all">
          <div className="flex items-center justify-between text-slate-400 mb-2 text-xs font-medium">
            <span>Total Expenses</span>
            <div className="p-2 rounded-lg bg-rose-500/10 text-rose-400">
              <TrendingDown className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-white tracking-tight">
            {formatINR(metrics.total_expenses)}
          </div>
          <p className="text-[11px] text-slate-400 mt-2 font-medium">
            {metrics.spending_by_category.length} categories active
          </p>
        </div>

        {/* Net Cash Flow */}
        <div className="p-5 rounded-2xl bg-[#0f182a] border border-[#1e2c45] relative overflow-hidden group hover:border-slate-700 transition-all">
          <div className="flex items-center justify-between text-slate-400 mb-2 text-xs font-medium">
            <span>Net Cash Flow</span>
            <div className="p-2 rounded-lg bg-teal-500/10 text-teal-400">
              <Wallet className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-white tracking-tight">
            {formatINR(metrics.net_cash_flow)}
          </div>
          <p className="text-[11px] text-teal-400 mt-2 font-medium">
            Surplus retained this cycle
          </p>
        </div>

        {/* Savings Rate */}
        <div className="p-5 rounded-2xl bg-[#0f182a] border border-[#1e2c45] relative overflow-hidden group hover:border-slate-700 transition-all">
          <div className="flex items-center justify-between text-slate-400 mb-2 text-xs font-medium">
            <span>Savings Rate</span>
            <div className="p-2 rounded-lg bg-amber-500/10 text-amber-400">
              <PiggyBank className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-white tracking-tight">
            {metrics.savings_rate.toFixed(1)}%
          </div>
          <div className="w-full bg-slate-800 h-1.5 rounded-full mt-3 overflow-hidden">
            <div
              className="bg-gradient-to-r from-teal-500 to-emerald-400 h-full rounded-full"
              style={{ width: `${Math.min(metrics.savings_rate, 100)}%` }}
            />
          </div>
        </div>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Monthly Inflow vs Outflow */}
        <div className="lg:col-span-2 p-5 rounded-2xl bg-[#0f182a] border border-[#1e2c45]">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-semibold text-white">Monthly Cash Flow Trend</h3>
              <p className="text-xs text-slate-400">Comparison of monthly income and expenditure</p>
            </div>
            <div className="flex items-center gap-4 text-xs font-medium">
              <span className="flex items-center gap-1.5 text-emerald-400">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" /> Income
              </span>
              <span className="flex items-center gap-1.5 text-rose-400">
                <span className="w-2.5 h-2.5 rounded-full bg-rose-500" /> Expense
              </span>
            </div>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={metrics.monthly_trend} barGap={6}>
                <XAxis dataKey="month" stroke="#64748b" fontSize={11} tickLine={false} />
                <YAxis
                  stroke="#64748b"
                  fontSize={11}
                  tickLine={false}
                  tickFormatter={(v) => `₹${v / 1000}k`}
                />
                <Tooltip
                  contentStyle={{ backgroundColor: '#090e17', borderColor: '#1e2c45', borderRadius: '12px' }}
                  formatter={(val: any) => formatINR(Number(val))}
                />
                <Bar dataKey="income" fill="#10b981" radius={[4, 4, 0, 0]} />
                <Bar dataKey="expenses" fill="#f43f5e" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Spending Breakdown by Category */}
        <div className="p-5 rounded-2xl bg-[#0f182a] border border-[#1e2c45] flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-semibold text-white">Spending by Category</h3>
            <p className="text-xs text-slate-400">Relative allocation of total expenses</p>
          </div>

          <div className="h-52 w-full my-2">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={metrics.spending_by_category}
                  dataKey="amount"
                  nameKey="category"
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={75}
                  paddingAngle={3}
                >
                  {metrics.spending_by_category.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color || '#0ea5e9'} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#090e17', borderColor: '#1e2c45', borderRadius: '12px' }}
                  formatter={(val: any) => formatINR(Number(val))}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="space-y-1.5 max-h-32 overflow-y-auto pr-1">
            {metrics.spending_by_category.slice(0, 4).map((c, idx) => (
              <div key={idx} className="flex items-center justify-between text-xs">
                <span className="flex items-center gap-2 text-slate-300">
                  <span className="w-2 h-2 rounded-full" style={{ backgroundColor: c.color }} />
                  {c.category}
                </span>
                <span className="font-semibold text-white">{formatINR(c.amount)} ({c.percentage}%)</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Anomaly Alerts & Budget Utilization */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Unusual Transaction Alerts */}
        <div className="p-5 rounded-2xl bg-[#0f182a] border border-[#1e2c45]">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 text-amber-400" />
              <h3 className="text-sm font-semibold text-white">Atypical Spend Alerts</h3>
            </div>
            <span className="text-[10px] px-2 py-0.5 rounded-full bg-amber-950/80 text-amber-300 border border-amber-800">
              Isolation Forest + IQR
            </span>
          </div>

          {metrics.unusual_alerts.length === 0 ? (
            <p className="text-xs text-slate-400 py-6 text-center">No abnormal spending detected.</p>
          ) : (
            <div className="space-y-3">
              {metrics.unusual_alerts.map((alert) => (
                <div
                  key={alert.transaction_id}
                  className="p-3.5 rounded-xl bg-slate-900/80 border border-amber-500/20 hover:border-amber-500/40 transition-all"
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-bold text-white">{alert.merchant}</span>
                    <span className="text-xs font-bold text-rose-400">{formatINR(alert.amount)}</span>
                  </div>
                  <p className="text-xs text-amber-200/90 leading-relaxed mb-1.5">{alert.reason}</p>
                  <div className="flex items-center justify-between text-[10px] text-slate-400">
                    <span>{alert.historical_benchmark}</span>
                    <span className="text-slate-400 italic">{alert.caveat}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Budget Utilization Progress */}
        <div className="p-5 rounded-2xl bg-[#0f182a] border border-[#1e2c45]">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-white">Budget Utilization (October 2026)</h3>
            <span className="text-xs text-slate-400">Actual vs Monthly Limits</span>
          </div>

          <div className="space-y-3.5">
            {metrics.budget_utilization.slice(0, 5).map((b) => (
              <div key={b.category_id} className="space-y-1">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-slate-300 font-medium">{b.category_name}</span>
                  <div className="flex items-center gap-2">
                    <span className="text-slate-400 font-mono">
                      {formatINR(b.actual_spent)} / {formatINR(b.budget_limit)}
                    </span>
                    <span
                      className={`text-[10px] font-bold px-1.5 py-0.2 rounded ${
                        b.is_over_budget ? 'bg-rose-950 text-rose-400' : 'bg-slate-800 text-teal-300'
                      }`}
                    >
                      {b.percentage_used.toFixed(0)}%
                    </span>
                  </div>
                </div>
                <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all ${
                      b.is_over_budget ? 'bg-rose-500' : 'bg-teal-500'
                    }`}
                    style={{ width: `${Math.min(b.percentage_used, 100)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recent Transactions Mini Table */}
      <div className="p-5 rounded-2xl bg-[#0f182a] border border-[#1e2c45]">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-sm font-semibold text-white">Recent Transactions</h3>
            <p className="text-xs text-slate-400">Latest activity from your verified records</p>
          </div>
          <button
            onClick={onNavigateToTransactions}
            className="text-xs font-semibold text-teal-400 hover:text-teal-300 transition-colors flex items-center gap-1"
          >
            <span>View All Transactions</span>
            <ArrowUpRight className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400">
                <th className="pb-2.5 font-medium">Date</th>
                <th className="pb-2.5 font-medium">Merchant / Description</th>
                <th className="pb-2.5 font-medium">Category</th>
                <th className="pb-2.5 font-medium">Method</th>
                <th className="pb-2.5 font-medium text-right">Amount</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {metrics.recent_transactions.slice(0, 6).map((tx) => (
                <tr key={tx.id} className="hover:bg-slate-800/30 transition-colors">
                  <td className="py-3 text-slate-400 font-mono text-[11px]">{tx.date}</td>
                  <td className="py-3">
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-white">{tx.merchant}</span>
                      {tx.anomaly_flag && (
                        <span className="p-0.5 rounded bg-amber-500/20 text-amber-300" title="Flagged outlier">
                          <AlertTriangle className="w-3 h-3" />
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="py-3">
                    <span
                      className="px-2 py-0.5 rounded-full text-[10px] font-medium"
                      style={{
                        backgroundColor: `${tx.category_color}20`,
                        color: tx.category_color || '#38bdf8'
                      }}
                    >
                      {tx.category_name}
                    </span>
                  </td>
                  <td className="py-3 text-slate-400 uppercase text-[10px] font-mono">{tx.payment_method}</td>
                  <td className={`py-3 text-right font-semibold font-mono ${
                    tx.type === 'INCOME' ? 'text-emerald-400' : 'text-slate-200'
                  }`}>
                    {tx.type === 'INCOME' ? '+' : '-'}{formatINR(tx.amount)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
