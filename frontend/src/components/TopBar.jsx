import { Link } from 'react-router-dom'

export default function TopBar() {
  return (
    <header className="border-b border-slate-200 bg-white/80 backdrop-blur-xl sticky top-0 z-20">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4 sm:px-6">
        <Link to="/" className="text-xl font-semibold tracking-tight text-slate-900">
          CareerPilot AI
        </Link>

        <nav className="flex items-center gap-3 text-sm font-medium text-slate-700">
          <Link to="/" className="hover:text-slate-900">
            Search
          </Link>
          <Link to="/results" className="hover:text-slate-900">
            Results
          </Link>
          <Link to="/applications" className="hover:text-slate-900">
            History
          </Link>
        </nav>
      </div>
    </header>
  )
}
