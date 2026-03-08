import { useState, useEffect } from 'react'
import { BarChart2, TrendingUp, Zap, Database, Activity } from 'lucide-react'
import { api, AnalyticsSummary } from '../api/client'

function StatCard({ icon: Icon, label, value }: { icon: React.ElementType; label: string; value: string | number }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white/80 shadow-sm p-5">
      <div className="flex items-center gap-2 text-slate-600 mb-1">
        <Icon size={18} />
        <span className="text-sm">{label}</span>
      </div>
      <p className="text-2xl font-semibold text-teal-700">{value}</p>
    </div>
  )
}

export default function Dashboard() {
  const [data, setData] = useState<AnalyticsSummary | null>(null)
  const [days, setDays] = useState(7)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    setLoading(true)
    api.getAnalytics(days)
      .then(setData)
      .catch((e) => setError(e instanceof Error ? e.message : 'Failed to load'))
      .finally(() => setLoading(false))
  }, [days])

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="animate-pulse text-slate-600">Loading analytics...</div>
      </div>
    )
  }

  if (error || !data) {
    return (
      <div className="rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-red-700">
        {error || 'No analytics data'}
      </div>
    )
  }

  const modelEntries = Object.entries(data.queries_by_model)
  const maxCount = Math.max(...Object.values(data.queries_by_model), 1)

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold text-slate-800">Analytics Dashboard</h2>
          <p className="text-slate-600 mt-1">Query generation performance and usage metrics</p>
        </div>
        <select
          value={days}
          onChange={(e) => setDays(Number(e.target.value))}
          className="px-4 py-2 rounded-lg bg-white border border-slate-200 text-slate-800"
        >
          <option value={1}>Last 1 day</option>
          <option value={7}>Last 7 days</option>
          <option value={30}>Last 30 days</option>
        </select>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard icon={Database} label="Total Queries" value={data.total_queries} />
        <StatCard icon={TrendingUp} label="Success Rate" value={`${data.success_rate}%`} />
        <StatCard icon={Activity} label="Queries Today" value={data.queries_today} />
        <StatCard
          icon={Zap}
          label="Avg. Latency"
          value={data.avg_execution_time_ms != null ? `${Math.round(data.avg_execution_time_ms)}ms` : '-'}
        />
      </div>

      <div className="rounded-xl border border-slate-200 bg-white/80 shadow-sm p-5">
        <div className="flex items-center gap-2 text-slate-600 mb-4">
          <BarChart2 size={18} />
          <span>Queries by Model</span>
        </div>
        {modelEntries.length ? (
          <div className="space-y-3">
            {modelEntries.map(([model, count]) => (
              <div key={model} className="flex items-center gap-3">
                <span className="w-36 text-slate-700 text-sm truncate">
                  {model === 'ollama' ? 'Ollama (Local)' : model === 'openai-gpt4' ? 'OpenAI GPT-4' : model === 'anthropic-claude' ? 'Anthropic Claude' : model}
                </span>
                <div className="flex-1 h-8 rounded-lg bg-slate-100 overflow-hidden">
                  <div
                    className="h-full bg-teal-500 rounded-lg transition-all"
                    style={{ width: `${(count / maxCount) * 100}%` }}
                  />
                </div>
                <span className="text-slate-600 text-sm w-12">{count}</span>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-slate-600">No queries yet. Generate some SQL to see metrics.</p>
        )}
      </div>

      <div className="rounded-xl border border-slate-200 bg-white/80 shadow-sm p-5">
        <div className="flex items-center gap-2 text-slate-600 mb-4">Recent Queries</div>
        {data.recent_queries.length ? (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-slate-600 border-b border-slate-200">
                  <th className="text-left py-2">Prompt</th>
                  <th className="text-left py-2">Model</th>
                  <th className="text-left py-2">Status</th>
                  <th className="text-left py-2">Time</th>
                </tr>
              </thead>
              <tbody>
                {data.recent_queries.map((q) => (
                  <tr key={q.id} className="border-b border-slate-100">
                    <td className="py-2 text-slate-700 max-w-xs truncate">{q.prompt}</td>
                    <td className="py-2 text-slate-600">{q.model_used}</td>
                    <td className="py-2">
                      <span
                        className={`px-2 py-0.5 rounded text-xs ${q.success ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}
                      >
                        {q.success ? 'Success' : 'Failed'}
                      </span>
                    </td>
                    <td className="py-2 text-slate-600">{q.created_at ? new Date(q.created_at).toLocaleString() : '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-slate-600">No recent queries.</p>
        )}
      </div>
    </div>
  )
}
