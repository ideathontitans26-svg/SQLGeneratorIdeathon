import { useState, useEffect } from 'react'
import { Sparkles, Copy, Check, Loader2, Database, ChevronDown } from 'lucide-react'
import { api } from '../api/client'

export default function SQLGenerator() {
  const [prompt, setPrompt] = useState('')
  const [schema, setSchema] = useState('')
  const [connectionString, setConnectionString] = useState('')
  const [schemaExpanded, setSchemaExpanded] = useState(false)
  const [connExpanded, setConnExpanded] = useState(false)
  const [models, setModels] = useState<string[]>([])
  const [selectedModel, setSelectedModel] = useState('ollama')
  const [result, setResult] = useState<{ sql: string; model_used: string; execution_time_ms?: number } | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    api.getModels().then((r) => {
      setModels(r.models)
      if (r.models.length && !r.models.includes(selectedModel)) setSelectedModel(r.models[0])
    })
  }, [])

  const handleGenerate = async () => {
    if (!prompt.trim()) return
    setLoading(true)
    setError('')
    setResult(null)
    try {
      const res = await api.generate(prompt, selectedModel, schema || undefined)
      setResult({
        sql: res.sql,
        model_used: res.model_used,
        execution_time_ms: res.execution_time_ms,
      })
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to generate SQL')
    } finally {
      setLoading(false)
    }
  }

  const handleExtractSchema = async () => {
    if (!connectionString.trim()) return
    setError('')
    try {
      const res = await api.extractSchema(connectionString)
      setSchema(res.schema)
      setSchemaExpanded(true)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to extract schema')
    }
  }

  const copyResult = () => {
    if (!result) return
    navigator.clipboard.writeText(result.sql)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold text-slate-100">Generate SQL from Natural Language</h2>
        <p className="text-slate-400 mt-1">Describe your query in plain English; the LLM will convert it to SQL.</p>
      </div>

      {/* Model selector */}
      <div>
        <label className="block text-sm font-medium text-slate-400 mb-2">LLM Model</label>
        <select
          value={selectedModel}
          onChange={(e) => setSelectedModel(e.target.value)}
          className="w-full max-w-xs px-4 py-2 rounded-lg bg-slate-800 border border-slate-600 text-slate-200 focus:ring-2 focus:ring-cyan-500 focus:border-transparent"
        >
          {models.map((m) => (
            <option key={m} value={m}>
              {m === 'ollama' ? 'Ollama (Local)' : m === 'openai-gpt4' ? 'OpenAI GPT-4' : m === 'anthropic-claude' ? 'Anthropic Claude' : m === 'google-gemini' ? 'Google Gemini' : m}
            </option>
          ))}
        </select>
      </div>

      {/* Connect Database + Schema - above prompt */}
      <div className="rounded-lg border border-slate-700 bg-slate-800/50 overflow-hidden">
        <button
          onClick={() => setConnExpanded(!connExpanded)}
          className="w-full flex items-center justify-between px-4 py-3 text-left text-slate-300 hover:bg-slate-700/50"
        >
          <span className="flex items-center gap-2">
            <Database size={18} />
            Optional: Connect Database (Schema Only - Data Privacy)
          </span>
          <ChevronDown className={`transition-transform ${connExpanded ? 'rotate-180' : ''}`} size={18} />
        </button>
        {connExpanded && (
          <div className="px-4 pb-4 space-y-2">
            <input
              type="password"
              value={connectionString}
              onChange={(e) => setConnectionString(e.target.value)}
              placeholder="postgresql://user:pass@host:5432/db or sqlite:///path/to/db.db"
              className="w-full px-4 py-2 rounded-lg bg-slate-800 border border-slate-600 text-slate-200 placeholder-slate-500 focus:ring-2 focus:ring-cyan-500"
            />
            <button
              onClick={handleExtractSchema}
              className="px-4 py-2 rounded-lg bg-slate-700 hover:bg-slate-600 text-slate-200 text-sm"
            >
              Extract Schema
            </button>
          </div>
        )}
      </div>

      {schema && (
        <div className="rounded-lg border border-slate-700 bg-slate-800/50 overflow-hidden">
          <button
            onClick={() => setSchemaExpanded(!schemaExpanded)}
            className="w-full flex items-center justify-between px-4 py-3 text-left text-slate-300 hover:bg-slate-700/50"
          >
            Schema (used for generation)
            <ChevronDown className={`transition-transform ${schemaExpanded ? 'rotate-180' : ''}`} size={18} />
          </button>
          {schemaExpanded && (
            <pre className="p-4 text-sm text-slate-400 overflow-x-auto max-h-48">{schema}</pre>
          )}
        </div>
      )}

      {/* Natural Language Prompt - below schema */}
      <div>
        <label className="block text-sm font-medium text-slate-400 mb-2">Natural Language Prompt</label>
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="e.g. Get all customer details with address where CUST_ID = 2"
          rows={4}
          className="w-full px-4 py-3 rounded-lg bg-slate-800 border border-slate-600 text-slate-200 placeholder-slate-500 focus:ring-2 focus:ring-cyan-500 focus:border-transparent resize-none"
        />
      </div>

      {error && (
        <div className="px-4 py-3 rounded-lg bg-red-900/30 border border-red-700 text-red-300">{error}</div>
      )}

      <button
        onClick={handleGenerate}
        disabled={loading || !prompt.trim()}
        className="flex items-center gap-2 px-6 py-3 rounded-lg bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium"
      >
        {loading ? (
          <>
            <Loader2 className="animate-spin" size={20} />
            Generating...
          </>
        ) : (
          <>
            <Sparkles size={20} />
            Generate SQL
          </>
        )}
      </button>

      {result && (
        <div className="rounded-lg border border-slate-700 bg-slate-800/50 overflow-hidden">
          <div className="flex items-center justify-between px-4 py-3 border-b border-slate-700">
            <span className="text-sm text-slate-400">
              Generated ({result.model_used})
              {result.execution_time_ms != null && ` • ${Math.round(result.execution_time_ms)}ms`}
            </span>
            <button
              onClick={copyResult}
              className="flex items-center gap-2 px-3 py-1 rounded bg-slate-700 hover:bg-slate-600 text-slate-300 text-sm"
            >
              {copied ? <Check size={16} /> : <Copy size={16} />}
              {copied ? 'Copied' : 'Copy'}
            </button>
          </div>
          <pre className="p-4 text-sm text-cyan-200 overflow-x-auto whitespace-pre-wrap">{result.sql}</pre>
        </div>
      )}
    </div>
  )
}
