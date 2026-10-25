export interface Transaction {
  id: string;
  user_id: string;
  category_id: string;
  category_name?: string;
  category_color?: string;
  date: string;
  amount: number;
  type: 'INCOME' | 'EXPENSE';
  merchant: string;
  payment_method: string;
  description?: string;
  is_recurring: boolean;
  is_synthetic: boolean;
  anomaly_flag: boolean;
  anomaly_score: number;
  anomaly_reason?: string;
  created_at: string;
}

export interface BudgetVsActual {
  category_id: string;
  category_name: string;
  category_color?: string;
  budget_limit: number;
  actual_spent: number;
  remaining: number;
  percentage_used: number;
  is_over_budget: boolean;
}

export interface AnomalyItem {
  transaction_id: string;
  date: string;
  merchant: string;
  category: string;
  amount: number;
  anomaly_score: number;
  severity: 'LOW' | 'MEDIUM' | 'HIGH';
  reason: string;
  historical_benchmark: string;
  caveat: string;
}

export interface DashboardMetrics {
  total_income: number;
  total_expenses: number;
  net_cash_flow: number;
  savings_rate: number;
  currency: string;
  is_synthetic: boolean;
  spending_by_category: {
    category: string;
    amount: number;
    percentage: number;
    color: string;
  }[];
  monthly_trend: {
    month: string;
    income: number;
    expenses: number;
    net: number;
  }[];
  recent_transactions: Transaction[];
  budget_utilization: BudgetVsActual[];
  unusual_alerts: AnomalyItem[];
  ai_financial_summary: string;
}

export interface ToolCallRecord {
  tool_name: string;
  arguments: Record<string, any>;
  result: Record<string, any>;
  status: string;
  execution_time_ms: number;
}

export interface CitationRecord {
  document_id: string;
  filename: string;
  page_number?: number;
  passage: string;
  similarity_score: number;
}

export interface ChatMessage {
  id: string;
  conversation_id: string;
  sender: 'user' | 'assistant' | 'system';
  content: string;
  tool_calls?: ToolCallRecord[];
  citations?: CitationRecord[];
  chart_data?: any;
  created_at: string;
}

export interface DocumentItem {
  id: string;
  user_id: string;
  filename: string;
  file_type: string;
  file_size_bytes: number;
  status: string;
  error_message?: string;
  chunk_count: number;
  created_at: string;
  chunks?: { id: string; chunk_index: number; content: string; page_number?: number }[];
}

export interface SavingsGoal {
  id: string;
  user_id: string;
  title: string;
  target_amount: number;
  current_amount: number;
  target_date?: string;
  progress_percentage: number;
  created_at: string;
}

export interface SystemMetrics {
  total_requests_24h: number;
  avg_latency_ms: number;
  p95_latency_ms: number;
  error_rate_percentage: number;
  token_usage_total: number;
  estimated_cost_usd: number;
  tool_invocations: Record<string, number>;
  endpoint_breakdown: { endpoint: string; count: number; avg_latency_ms: number }[];
  recent_events: {
    id: string;
    action: string;
    resource_type: string;
    status: string;
    details?: any;
    timestamp: string;
  }[];
  evaluation_benchmarks?: {
    id: string;
    run_name: string;
    total_tests: number;
    passed_tests: number;
    failed_tests: number;
    pass_rate: number;
    avg_latency_ms: number;
    metrics: any;
    created_at: string;
  }[];
}
