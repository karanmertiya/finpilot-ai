'use client';

import React, { useState, useEffect } from 'react';
import {
  Search,
  Filter,
  Download,
  Upload,
  AlertTriangle,
  ChevronLeft,
  ChevronRight,
  Plus,
  CheckCircle2,
  X
} from 'lucide-react';
import { api } from '@/lib/api';
import { Transaction } from '@/lib/types';

export const TransactionsView: React.FC = () => {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(15);
  const [search, setSearch] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [categories, setCategories] = useState<any[]>([]);
  const [anomalyOnly, setAnomalyOnly] = useState(false);
  const [loading, setLoading] = useState(false);

  // CSV Import Modal State
  const [isImportModalOpen, setIsImportModalOpen] = useState(false);
  const [importFile, setImportFile] = useState<File | null>(null);
  const [importLoading, setImportLoading] = useState(false);
  const [importResult, setImportResult] = useState<any | null>(null);

  const fetchTransactions = async () => {
    setLoading(true);
    try {
      const data = await api.listTransactions({
        page,
        page_size: pageSize,
        search,
        type: typeFilter,
        category_id: categoryFilter,
        anomaly_only: anomalyOnly
      });
      setTransactions(data.transactions);
      setTotalCount(data.total_count);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    api.getCategories().then(setCategories).catch(console.error);
  }, []);

  useEffect(() => {
    fetchTransactions();
  }, [page, typeFilter, categoryFilter, anomalyOnly]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchTransactions();
  };

  const handleDownloadDemo = () => {
    window.open('http://localhost:8000/api/v1/transactions/export-demo', '_blank');
  };

  const handleImportSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!importFile) return;
    setImportLoading(true);
    try {
      const res = await api.importTransactionsCSV(importFile);
      setImportResult(res);
      fetchTransactions();
    } catch (err: any) {
      setImportResult({ error: err.message || 'Import failed' });
    } finally {
      setImportLoading(false);
    }
  };

  const formatINR = (val: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 2
    }).format(val);
  };

  const totalPages = Math.ceil(totalCount / pageSize) || 1;

  return (
    <div className="space-y-6">
      {/* Top Action Bar */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-5 rounded-2xl bg-[#0f182a] border border-[#1e2c45]">
        <div>
          <h2 className="text-base font-bold text-white">Financial Transactions Ledger</h2>
          <p className="text-xs text-slate-400">Search, filter, and audit all seeded Indian financial records</p>
        </div>

        <div className="flex items-center gap-2.5 w-full sm:w-auto">
          <button
            onClick={handleDownloadDemo}
            className="flex-1 sm:flex-none flex items-center justify-center gap-1.5 px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium transition-all"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Download Demo CSV</span>
          </button>

          <button
            onClick={() => {
              setImportResult(null);
              setImportFile(null);
              setIsImportModalOpen(true);
            }}
            className="flex-1 sm:flex-none flex items-center justify-center gap-1.5 px-3.5 py-2 rounded-xl bg-teal-600 hover:bg-teal-500 text-white text-xs font-semibold transition-all shadow-md active:scale-95"
          >
            <Upload className="w-3.5 h-3.5" />
            <span>Import CSV</span>
          </button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="p-4 rounded-2xl bg-[#0f182a] border border-[#1e2c45] flex flex-wrap items-center gap-3">
        <form onSubmit={handleSearchSubmit} className="flex-1 min-w-[220px] relative">
          <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search merchant, description..."
            className="w-full bg-slate-900 border border-slate-700/80 rounded-xl pl-9 pr-4 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-teal-500"
          />
        </form>

        {/* Category Dropdown */}
        <select
          value={categoryFilter}
          onChange={(e) => {
            setCategoryFilter(e.target.value);
            setPage(1);
          }}
          className="bg-slate-900 border border-slate-700/80 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-teal-500"
        >
          <option value="">All Categories</option>
          {categories.map((c) => (
            <option key={c.id} value={c.id}>{c.name}</option>
          ))}
        </select>

        {/* Type Filter */}
        <select
          value={typeFilter}
          onChange={(e) => {
            setTypeFilter(e.target.value);
            setPage(1);
          }}
          className="bg-slate-900 border border-slate-700/80 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-teal-500"
        >
          <option value="">All Types</option>
          <option value="INCOME">Income Only</option>
          <option value="EXPENSE">Expense Only</option>
        </select>

        {/* Anomaly Toggle */}
        <button
          onClick={() => {
            setAnomalyOnly(!anomalyOnly);
            setPage(1);
          }}
          className={`px-3 py-2 rounded-xl text-xs font-medium flex items-center gap-1.5 transition-all ${
            anomalyOnly
              ? 'bg-amber-950 text-amber-300 border border-amber-700'
              : 'bg-slate-900 text-slate-400 border border-slate-800 hover:text-slate-200'
          }`}
        >
          <AlertTriangle className="w-3.5 h-3.5" />
          <span>Anomalies Only</span>
        </button>
      </div>

      {/* Transactions Table */}
      <div className="p-5 rounded-2xl bg-[#0f182a] border border-[#1e2c45] overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400">
                <th className="pb-3 font-medium">Date</th>
                <th className="pb-3 font-medium">Merchant & Description</th>
                <th className="pb-3 font-medium">Category</th>
                <th className="pb-3 font-medium">Method</th>
                <th className="pb-3 font-medium">Status / Flag</th>
                <th className="pb-3 font-medium text-right">Amount</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {loading ? (
                <tr>
                  <td colSpan={6} className="py-8 text-center text-slate-400">Loading verified transactions...</td>
                </tr>
              ) : transactions.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-8 text-center text-slate-400">No matching transactions found.</td>
                </tr>
              ) : (
                transactions.map((t) => (
                  <tr key={t.id} className="hover:bg-slate-800/30 transition-colors">
                    <td className="py-3.5 text-slate-400 font-mono text-[11px] whitespace-nowrap">{t.date}</td>
                    <td className="py-3.5">
                      <div>
                        <span className="font-semibold text-white">{t.merchant}</span>
                        {t.description && (
                          <p className="text-[11px] text-slate-400 truncate max-w-xs">{t.description}</p>
                        )}
                      </div>
                    </td>
                    <td className="py-3.5">
                      <span
                        className="px-2.5 py-0.5 rounded-full text-[10px] font-medium"
                        style={{
                          backgroundColor: `${t.category_color}20`,
                          color: t.category_color || '#38bdf8'
                        }}
                      >
                        {t.category_name}
                      </span>
                    </td>
                    <td className="py-3.5 text-slate-300 font-mono text-[10px] uppercase">{t.payment_method}</td>
                    <td className="py-3.5">
                      {t.anomaly_flag ? (
                        <div className="flex items-center gap-1.5 text-amber-400 text-[10px] font-semibold bg-amber-950/60 px-2 py-0.5 rounded-full border border-amber-800 w-fit" title={t.anomaly_reason || ''}>
                          <AlertTriangle className="w-3 h-3" />
                          <span>Atypical Outlier</span>
                        </div>
                      ) : (
                        <span className="text-slate-400 text-[10px]">Normal</span>
                      )}
                    </td>
                    <td className={`py-3.5 text-right font-bold font-mono ${
                      t.type === 'INCOME' ? 'text-emerald-400' : 'text-slate-100'
                    }`}>
                      {t.type === 'INCOME' ? '+' : '-'}{formatINR(t.amount)}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="flex items-center justify-between pt-4 mt-2 border-t border-slate-800 text-xs text-slate-400">
          <span>Showing {transactions.length} of {totalCount} records</span>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page <= 1}
              className="p-1.5 rounded-lg border border-slate-800 hover:bg-slate-800 disabled:opacity-40 transition-colors"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <span className="font-mono text-slate-200">Page {page} of {totalPages}</span>
            <button
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page >= totalPages}
              className="p-1.5 rounded-lg border border-slate-800 hover:bg-slate-800 disabled:opacity-40 transition-colors"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* CSV Import Modal */}
      {isImportModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="w-full max-w-md rounded-2xl bg-[#0f182a] border border-[#1e2c45] p-6 shadow-2xl relative">
            <button
              onClick={() => setIsImportModalOpen(false)}
              className="absolute right-4 top-4 text-slate-400 hover:text-white"
            >
              <X className="w-4 h-4" />
            </button>
            <h3 className="text-sm font-bold text-white mb-1">Import Financial CSV</h3>
            <p className="text-xs text-slate-400 mb-4">
              Upload bank statement or ledger CSV. Automated duplicate detection and validation are enforced.
            </p>

            <form onSubmit={handleImportSubmit} className="space-y-4">
              <input
                type="file"
                accept=".csv"
                onChange={(e) => setImportFile(e.target.files?.[0] || null)}
                className="w-full text-xs text-slate-300 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-teal-600 file:text-white hover:file:bg-teal-500 cursor-pointer"
              />

              {importResult && (
                <div className={`p-3 rounded-xl text-xs border ${
                  importResult.error
                    ? 'bg-rose-950/60 border-rose-800 text-rose-300'
                    : 'bg-emerald-950/60 border-emerald-800 text-emerald-300'
                }`}>
                  {importResult.error ? (
                    <p>{importResult.error}</p>
                  ) : (
                    <div>
                      <p className="font-semibold">{importResult.message}</p>
                      <p className="text-[11px] mt-1 text-slate-300">
                        Imported: {importResult.imported_count} | Skipped Duplicates: {importResult.duplicate_count}
                      </p>
                    </div>
                  )}
                </div>
              )}

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setIsImportModalOpen(false)}
                  className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs"
                >
                  Close
                </button>
                <button
                  type="submit"
                  disabled={!importFile || importLoading}
                  className="px-4 py-2 rounded-xl bg-teal-600 hover:bg-teal-500 disabled:opacity-50 text-white text-xs font-semibold"
                >
                  {importLoading ? 'Processing...' : 'Upload & Process'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
