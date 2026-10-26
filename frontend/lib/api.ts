const getApiBaseUrl = (): string => {
  if (process.env.NEXT_PUBLIC_API_URL && !process.env.NEXT_PUBLIC_API_URL.includes('localhost')) {
    return process.env.NEXT_PUBLIC_API_URL;
  }
  if (typeof window !== 'undefined') {
    const hostname = window.location.hostname;
    const protocol = window.location.protocol;
    if (hostname !== 'localhost' && hostname !== '127.0.0.1') {
      return `${protocol}//${hostname}:8000/api/v1`;
    }
  }
  return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
};

class ApiService {
  private token: string | null = null;

  public get baseUrl(): string {
    return getApiBaseUrl();
  }

  constructor() {
    if (typeof window !== 'undefined') {
      this.token = localStorage.getItem('finpilot_token');
    }
  }

  public setToken(token: string) {
    this.token = token;
    if (typeof window !== 'undefined') {
      localStorage.setItem('finpilot_token', token);
    }
  }

  public getToken(): string | null {
    if (!this.token && typeof window !== 'undefined') {
      this.token = localStorage.getItem('finpilot_token');
    }
    return this.token;
  }

  public async ensureAuth(): Promise<string> {
    let tok = this.getToken();
    if (!tok) {
      // 1-click auto demo login
      const res = await fetch(`${this.baseUrl}/auth/demo-login`, { method: 'POST' });
      if (res.ok) {
        const data = await res.json();
        this.setToken(data.access_token);
        tok = data.access_token;
      }
    }
    return tok || '';
  }


  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const token = await this.ensureAuth();
    const headers: Record<string, string> = {
      ...(options.headers as Record<string, string> || {}),
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    if (!(options.body instanceof FormData) && !headers['Content-Type']) {
      headers['Content-Type'] = 'application/json';
    }

    const res = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers
    });

    if (res.status === 401) {
      // Refresh demo token
      if (typeof window !== 'undefined') {
        localStorage.removeItem('finpilot_token');
      }
      this.token = null;
      const newToken = await this.ensureAuth();
      headers['Authorization'] = `Bearer ${newToken}`;
      const retryRes = await fetch(`${this.baseUrl}${endpoint}`, { ...options, headers });
      if (!retryRes.ok) throw new Error(`HTTP ${retryRes.status}: ${await retryRes.text()}`);
      return retryRes.json();
    }

    if (!res.ok) {
      const errText = await res.text();
      throw new Error(`API Error ${res.status}: ${errText}`);
    }

    if (res.status === 204) {
      return {} as T;
    }

    return res.json();
  }

  // Dashboard
  async getDashboardMetrics() {
    return this.request<any>('/dashboard/metrics');
  }

  // Transactions
  async listTransactions(params: Record<string, any> = {}) {
    const q = new URLSearchParams();
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== '') q.append(k, String(v));
    });
    return this.request<any>(`/transactions?${q.toString()}`);
  }

  async getCategories() {
    return this.request<any[]>('/transactions/categories');
  }

  async createTransaction(tx: any) {
    return this.request<any>('/transactions', {
      method: 'POST',
      body: JSON.stringify(tx)
    });
  }

  async importTransactionsCSV(file: File) {
    const token = await this.ensureAuth();
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE_URL}/transactions/import-csv`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
      body: formData
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  }

  // Budgets & Goals
  async getBudgets(monthYear?: string) {
    const q = monthYear ? `?month_year=${monthYear}` : '';
    return this.request<any[]>(`/budgets${q}`);
  }

  async setBudget(budget: { category_id: string; monthly_limit: number; month_year: string }) {
    return this.request<any>('/budgets', {
      method: 'POST',
      body: JSON.stringify(budget)
    });
  }

  async getSavingsGoals() {
    return this.request<any[]>('/budgets/goals');
  }

  async createSavingsGoal(goal: { title: string; target_amount: number; current_amount?: number; target_date?: string }) {
    return this.request<any>('/budgets/goals', {
      method: 'POST',
      body: JSON.stringify(goal)
    });
  }

  // Chat Copilot
  async sendChatMessage(message: string, conversationId?: string) {
    return this.request<any>('/chat', {
      method: 'POST',
      body: JSON.stringify({ message, conversation_id: conversationId })
    });
  }

  async listConversations() {
    return this.request<any[]>('/chat/conversations');
  }

  async getConversation(id: string) {
    return this.request<any>(`/chat/conversations/${id}`);
  }

  async deleteConversation(id: string) {
    return this.request<void>(`/chat/conversations/${id}`, { method: 'DELETE' });
  }

  // Documents
  async listDocuments() {
    return this.request<any[]>('/documents');
  }

  async getDocument(id: string) {
    return this.request<any>(`/documents/${id}`);
  }

  async deleteDocument(id: string) {
    return this.request<void>(`/documents/${id}`, { method: 'DELETE' });
  }

  async uploadDocument(file: File) {
    const token = await this.ensureAuth();
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${this.baseUrl}/documents/upload`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
      body: formData
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  }

  // Calculations
  async calculateEMI(principal: number, annualInterestRate: number, tenureMonths: number) {
    return this.request<any>('/calculations/emi', {
      method: 'POST',
      body: JSON.stringify({
        principal,
        annual_interest_rate: annualInterestRate,
        tenure_months: tenureMonths
      })
    });
  }

  async calculateAffordability(proposedEMI: number, existingEMIs: number = 0) {
    return this.request<any>('/calculations/affordability', {
      method: 'POST',
      body: JSON.stringify({
        proposed_emi: proposedEMI,
        existing_emis: existingEMIs
      })
    });
  }

  // System & Observability
  async getSystemMetrics() {
    return this.request<any>('/system/metrics');
  }

  async runEvaluation() {
    return this.request<any>('/system/run-evaluation', { method: 'POST' });
  }
}

export const api = new ApiService();
