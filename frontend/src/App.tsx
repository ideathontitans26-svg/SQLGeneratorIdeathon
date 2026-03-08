import { Routes, Route, Link, useLocation, Navigate, Outlet } from 'react-router-dom'
import { LayoutDashboard, Database, FileCode, LogOut } from 'lucide-react'
import { AuthProvider, useAuth } from './context/AuthContext'
import SQLGenerator from './pages/SQLGenerator'
import Dashboard from './pages/Dashboard'
import QueryHistory from './pages/QueryHistory'
import Login from './pages/Login'

function NavLink({ to, icon: Icon, children }: { to: string; icon: React.ElementType; children: React.ReactNode }) {
  const loc = useLocation()
  const active = loc.pathname === to
  return (
    <Link
      to={to}
      className={`flex items-center gap-2 px-4 py-3 rounded-lg transition-colors ${
        active ? 'bg-teal-100 text-teal-700 font-medium' : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
      }`}
    >
      <Icon size={20} />
      {children}
    </Link>
  )
}

function ProtectedLayout() {
  const { isAuthenticated, loading, email, logout } = useAuth()

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-transparent">
        <div className="animate-pulse text-slate-600 font-sans">Loading...</div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return (
    <div className="min-h-screen flex flex-col bg-transparent">
      <header className="border-b border-slate-200 bg-white/80 backdrop-blur-sm shadow-sm">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <h1 className="text-xl font-semibold text-teal-700">SQL Generator Tool</h1>
          <nav className="flex items-center gap-1">
            <NavLink to="/" icon={Database}>Generate</NavLink>
            <NavLink to="/dashboard" icon={LayoutDashboard}>Analytics</NavLink>
            <NavLink to="/history" icon={FileCode}>Query History</NavLink>
            <span className="text-slate-600 text-sm mx-2">{email}</span>
            <button
              onClick={logout}
              className="flex items-center gap-2 px-4 py-3 rounded-lg text-slate-600 hover:bg-red-50 hover:text-red-600 transition-colors"
              title="Sign out"
            >
              <LogOut size={20} />
              Sign out
            </button>
          </nav>
        </div>
      </header>

      <main className="flex-1 max-w-6xl w-full mx-auto px-4 py-6">
        <Outlet />
      </main>
    </div>
  )
}

function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<ProtectedLayout />}>
          <Route index element={<SQLGenerator />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="history" element={<QueryHistory />} />
        </Route>
      </Routes>
    </AuthProvider>
  )
}

export default App
