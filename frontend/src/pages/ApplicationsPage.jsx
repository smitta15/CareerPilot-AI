import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useCareerPilot } from '../context/CareerPilotContext'
import LoadingSpinner from '../components/LoadingSpinner'

export default function ApplicationsPage() {
  const navigate = useNavigate()
  const { applications, loading, error, fetchApplications } = useCareerPilot()

  useEffect(() => {
    fetchApplications()
  }, [fetchApplications])

  const normalizeApp = (item) => {
    const job = item?.job || {}
    return {
      company: item?.company || job.company || 'Unknown company',
      role: item?.role || job.title || job.role || 'Opportunity',
      status: item?.status || 'tracked',
      applyLink: item?.apply_link || item?.external_application_link || job.apply_link || '',
      timestamp: item?.timestamp || item?.created_at || '',
      resume: item?.resume || '',
      applicationSubmitted: Boolean(item?.application_submitted),
    }
  }

  return (
    <main className="min-h-[calc(100vh-72px)] bg-slate-50 pb-16">
      <section className="mx-auto max-w-6xl px-4 py-12 sm:px-6 lg:px-8">
        <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-sm uppercase tracking-[0.24em] text-indigo-600">Application history</p>
            <h1 className="mt-3 text-3xl font-semibold tracking-tight text-slate-900 sm:text-4xl">Tracked opportunities</h1>
          </div>
          <button
            type="button"
            onClick={() => navigate('/')}
            className="inline-flex items-center rounded-full bg-white px-5 py-3 text-sm font-semibold text-slate-900 shadow-soft transition hover:bg-slate-100"
          >
            Back to search
          </button>
        </div>

        {loading && <LoadingSpinner />}

        {error && (
          <div className="mb-6 rounded-3xl border border-rose-100 bg-rose-50 px-5 py-4 text-sm text-rose-700 shadow-sm">
            {error}
          </div>
        )}

        <div className="grid gap-6">
          {applications.length === 0 ? (
            <div className="rounded-3xl border border-slate-200 bg-white p-8 text-center shadow-soft">
              <p className="text-lg font-semibold text-slate-900">No tracked applications yet</p>
              <p className="mt-3 text-sm leading-7 text-slate-600">Track one from the results page to build your history automatically.</p>
            </div>
          ) : (
            applications.map((item, index) => {
              const app = normalizeApp(item)
              return (
                <div key={`${app.company}-${app.role}-${index}`} className="rounded-3xl border border-slate-200 bg-white p-6 shadow-soft">
                  <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                    <div>
                      <p className="text-sm uppercase tracking-[0.24em] text-indigo-600">{app.status}</p>
                      <h2 className="mt-2 text-xl font-semibold text-slate-900">{app.role}</h2>
                      <p className="mt-1 text-sm text-slate-600">{app.company}</p>
                    </div>
                    {app.timestamp && (
                      <p className="text-sm text-slate-500">{new Date(app.timestamp).toLocaleDateString()}</p>
                    )}
                  </div>
                  {app.applyLink && (
                    <a
                      href={app.applyLink}
                      target="_blank"
                      rel="noreferrer"
                      className="mt-4 inline-flex rounded-full border border-indigo-200 bg-indigo-50 px-4 py-2 text-sm font-semibold text-indigo-700 hover:bg-indigo-100"
                    >
                      External application link
                    </a>
                  )}
                  {!app.applicationSubmitted && (
                    <p className="mt-4 text-sm text-slate-600">
                      CareerPilot recorded this application internally; no employer submission was performed by the app.
                    </p>
                  )}
                  {app.resume && (
                    <div className="mt-5 rounded-3xl bg-slate-50 p-4 text-sm text-slate-700">
                      <p className="font-semibold text-slate-900">Resume snippet</p>
                      <p className="mt-2 whitespace-pre-wrap">{app.resume}</p>
                    </div>
                  )}
                </div>
              )
            })
          )}
        </div>
      </section>
    </main>
  )
}
