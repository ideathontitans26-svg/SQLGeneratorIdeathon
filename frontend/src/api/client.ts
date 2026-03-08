const API_BASE = '/api';

const getAuthHeaders = (): Record<string, string> => {
  const token = localStorage.getItem('token');
  if (!token) return {};
  return { Authorization: `Bearer ${token}` };
};

async function fetchApi<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders(), ...options?.headers },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || res.statusText);
  }
  return res.json();
}

export const api = {
  generate: (prompt: string, model: string, schemaInfo?: string) =>
    fetchApi<{ sql: string; model_used: string; success: boolean; execution_time_ms?: number }>(
      '/generate',
      {
        method: 'POST',
        body: JSON.stringify({ prompt, model, schema_info: schemaInfo }),
      }
    ),
  getModels: () => fetchApi<{ models: string[] }>('/models'),
  getAnalytics: (days = 7) => fetchApi<AnalyticsSummary>(`/analytics?days=${days}`),
  getQueries: (limit = 50) => fetchApi<{ queries: QueryRecord[] }>(`/queries?limit=${limit}`),
  getStoredPrompts: () => fetchApi<{ prompts: StoredPrompt[] }>('/stored-prompts'),
  extractSchema: (connectionString: string) =>
    fetchApi<{ schema: string }>('/extract-schema', {
      method: 'POST',
      body: JSON.stringify({ connection_string: connectionString }),
    }),
  validateConnection: (connectionString: string) =>
    fetchApi<{ valid: boolean }>('/validate-connection', {
      method: 'POST',
      body: JSON.stringify({ connection_string: connectionString }),
    }),
  login: (email: string, password: string) =>
    fetchApi<{ email: string; token: string }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),
  register: (email: string, password: string) =>
    fetchApi<{ email: string; token: string }>('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),
  getMe: () => fetchApi<{ email: string }>('/auth/me'),
};

export interface AnalyticsSummary {
  total_queries: number;
  success_rate: number;
  queries_by_model: Record<string, number>;
  queries_today: number;
  avg_execution_time_ms: number | null;
  recent_queries: { id: number; prompt: string; model_used: string; success: boolean; created_at: string }[];
}

export interface QueryRecord {
  id: number;
  prompt: string;
  generated_sql: string | null;
  model_used: string;
  success: boolean;
  execution_time_ms: number | null;
  created_at: string | null;
}

export interface StoredPrompt {
  id: number;
  prompt: string;
  generated_sql: string | null;
  model_used: string | null;
  created_at: string | null;
}
