import { useState, useEffect } from 'react'
import { FileCode, Copy, Check } from 'lucide-react'
import { api, QueryRecord } from '../api/client'

export default function QueryHistory() {
  const [queries, setQueries] = useState<QueryRecord[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [copiedId, setCopiedId] = useState<number | null>(null)

  useEffect(() => {
    api.getQueries()
      .then((r) => setQueries(r.queries))
      .catch((e) => setError(e instanceof Error ? e.message : 'Failed to load'))
      .finally(() => setLoading(false))
  }, [])

  const copy = (id: number, sql: string) => {
    navigator.clipboard.writeText(sql)
    setCopiedId(id)
    setTimeout(() => setCopiedId(null), 2000)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="animate-pulse text-slate-600">Loading query history...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-red-700">{error}</div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold text-slate-800">Query History</h2>
        <p className="text-slate-600 mt-1">All user-generated queries tracked for analytics</p>
      </div>

      {queries.length === 0 ? (
        <div className="rounded-xl border border-slate-200 bg-white/80 shadow-sm p-12 text-center text-slate-600">
          <FileCode size={48} className="mx-auto mb-3 opacity-50" />
          No queries yet. Generate SQL from the Generate page to see them here.
        </div>
      ) : (
        <div className="space-y-4">
          {queries.map((q) => (
            <div
              key={q.id}
              className="rounded-xl border border-slate-200 bg-white/80 shadow-sm overflow-hidden"
            >
              <div className="flex items-center justify-between px-4 py-3 border-b border-slate-200">
                <div className="flex items-center gap-2">
                  <span className="text-sm text-slate-600">#{q.id}</span>
                  <span className="text-xs px-2 py-0.5 rounded bg-slate-100 text-slate-600">{q.model_used}</span>
                  <span
                    className={`text-xs px-2 py-0.5 rounded ${q.success ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}
                  >
                    {q.success ? 'Success' : 'Failed'}
                  </span>
                  {q.execution_time_ms != null && (
                    <span className="text-xs text-slate-600">{Math.round(q.execution_time_ms)}ms</span>
                  )}
                  {q.created_at && (
                    <span className="text-xs text-slate-600">{new Date(q.created_at).toLocaleString()}</span>
                  )}
                </div>
                {q.generated_sql && (
                  <button
                    onClick={() => copy(q.id, q.generated_sql!)}
                    className="flex items-center gap-1 px-2 py-1 rounded bg-slate-100 hover:bg-slate-200 text-slate-600 text-xs"
                  >
                    {copiedId === q.id ? <Check size={14} /> : <Copy size={14} />}
                    {copiedId === q.id ? 'Copied' : 'Copy'}
                  </button>
                )}
              </div>
              <div className="p-4 space-y-3">
                <div>
                  <p className="text-xs text-slate-600 mb-1">Prompt</p>
                  <p className="text-slate-700">{q.prompt}</p>
                </div>
                {q.generated_sql && (
                  <div>
                    <p className="text-xs text-slate-600 mb-1">Generated SQL</p>
                    <pre className="text-sm text-teal-800 overflow-x-auto whitespace-pre-wrap font-mono">{q.generated_sql}</pre>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
