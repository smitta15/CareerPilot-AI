import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useCareerPilot } from '../context/CareerPilotContext'
import LoadingSpinner from '../components/LoadingSpinner'

export default function HomePage() {
  const navigate = useNavigate()
  const { searchInternships, loading, error, success } = useCareerPilot()
  const [query, setQuery] = useState('')

  const handleSubmit = async (event) => {
    event.preventDefault()
    if (!query.trim()) return

    const parsed = await searchInternships(query.trim())
    if (parsed) {
      navigate('/results')
    }
  }

  return (
    <main className="min-h-[calc(100vh-72px)] bg-slate-50 pb-16">
      <section className="mx-auto max-w-6xl px-4 py-12 sm:px-6 lg:px-8">
        <div className="rounded-[2rem] border border-slate-200 bg-white/90 p-10 shadow-soft sm:p-14">
          <div className="max-w-3xl">
            <p className="mb-4 inline-flex rounded-full bg-indigo-50 px-4 py-2 text-sm font-semibold text-indigo-700">
              AI-powered internship matching
            </p>
            <h1 className="text-4xl font-semibold tracking-tight text-slate-900 sm:text-5xl">
              Find and apply to the best internships with CareerPilot AI.
            </h1>
            <p className="mt-6 text-lg leading-8 text-slate-600">
              Search internships, match your profile, get skill gap guidance, tailor your resume, and submit applications in one workflow.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="mt-10 grid gap-4 sm:grid-cols-[1.8fr,auto]">
            <label className="sr-only" htmlFor="search-query">
              Search internships
            </label>
            <input
              id="search-query"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="e.g. Backend internship with Python and FastAPI"
              className="w-full rounded-3xl border border-slate-300 bg-slate-50 px-5 py-4 text-base text-slate-900 outline-none transition focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100"
            />
            <button
              type="submit"
              disabled={loading}
              className="rounded-3xl bg-indigo-600 px-6 py-4 text-sm font-semibold text-white transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:bg-slate-400"
            >
              {loading ? 'Analyzing...' : 'Search internships'}
            </button>
          </form>

          {loading && <LoadingSpinner />}
          {(error || success) && (
            <div className="mt-6 space-y-3 rounded-3xl border px-5 py-4 text-sm shadow-sm sm:px-6">
              {error && <p className="text-rose-700">{error}</p>}
              {success && <p className="text-emerald-700">{success}</p>}
            </div>
          )}

          <div className="mt-12 grid gap-6 sm:grid-cols-2">
            <div className="rounded-3xl border border-slate-200 bg-slate-50 p-6 shadow-soft">
              <h2 className="text-lg font-semibold text-slate-900">What CareerPilot does</h2>
              <ul className="mt-4 space-y-3 text-sm text-slate-600">
                <li>• Converts your internship query into a targeted search.</li>
                <li>• Scores and shortlists the strongest matches.</li>
                <li>• Compares company needs, skills, and resume fit.</li>
                <li>• Lets you apply from the app and track submissions.</li>
              </ul>
            </div>
            <div className="rounded-3xl border border-slate-200 bg-slate-50 p-6 shadow-soft">
              <h2 className="text-lg font-semibold text-slate-900">Ready when you are</h2>
              <p className="mt-4 text-sm leading-7 text-slate-600">
                Enter a simple description like “Find backend internships” and CareerPilot will build the analysis pipeline for you.
              </p>
            </div>
          </div>
        </div>
      </section>
    </main>
  )
}
