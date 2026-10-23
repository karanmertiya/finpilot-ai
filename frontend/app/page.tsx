'use client';

import React, { useState, useEffect } from 'react';
import { Navbar } from '@/components/Navbar';
import { Sidebar, ActiveTab } from '@/components/Sidebar';
import { DashboardView } from '@/components/DashboardView';
import { ChatView } from '@/components/ChatView';
import { TransactionsView } from '@/components/TransactionsView';
import { BudgetsView } from '@/components/BudgetsView';
import { DocumentsView } from '@/components/DocumentsView';
import { SystemView } from '@/components/SystemView';
import { CalculatorModal } from '@/components/CalculatorModal';
import { api } from '@/lib/api';
import { DashboardMetrics } from '@/lib/types';

export default function Home() {
  const [activeTab, setActiveTab] = useState<ActiveTab>('dashboard');
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [apiHealthy, setApiHealthy] = useState(false);
  const [isCalculatorOpen, setIsCalculatorOpen] = useState(false);

  const loadData = async () => {
    try {
      const data = await api.getDashboardMetrics();
      setMetrics(data);
      setApiHealthy(true);
    } catch (err) {
      console.error('Failed to load dashboard metrics:', err);
      setApiHealthy(false);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  return (
    <div className="min-h-screen bg-[#090e17] text-slate-100 flex flex-col font-sans selection:bg-teal-500/30">
      {/* Top Navbar */}
      <Navbar
        onOpenCalculator={() => setIsCalculatorOpen(true)}
        apiHealthy={apiHealthy}
      />

      {/* Main Workspace */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left Sidebar */}
        <Sidebar activeTab={activeTab} onTabChange={setActiveTab} />

        {/* Tab Content */}
        <main className="flex-1 overflow-y-auto p-6 md:p-8 bg-[#090e17]">
          <div className="max-w-7xl mx-auto">
            {activeTab === 'dashboard' && (
              <DashboardView
                metrics={metrics}
                loading={loading}
                onNavigateToAssistant={() => setActiveTab('assistant')}
                onNavigateToTransactions={() => setActiveTab('transactions')}
              />
            )}

            {activeTab === 'assistant' && <ChatView />}

            {activeTab === 'transactions' && <TransactionsView />}

            {activeTab === 'budgets' && <BudgetsView />}

            {activeTab === 'documents' && <DocumentsView />}

            {activeTab === 'system' && <SystemView />}
          </div>
        </main>
      </div>

      {/* Interactive Calculator Modal */}
      <CalculatorModal
        isOpen={isCalculatorOpen}
        onClose={() => setIsCalculatorOpen(false)}
      />
    </div>
  );
}
