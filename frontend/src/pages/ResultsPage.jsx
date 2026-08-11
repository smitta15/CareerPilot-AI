import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useCareerPilot } from '../context/CareerPilotContext'
import JobCard from '../components/JobCard'
import CompanyReport from '../components/CompanyReport'
import SkillGapCard from '../components/SkillGapCard'
import ResumePreview from '../components/ResumePreview'
import DecisionCard from '../components/DecisionCard'
import LoadingSpinner from '../components/LoadingSpinner'

export default function ResultsPage() {
  const navigate = useNavigate()
  const {
    analysis,
    loading,
    error,
    success,
    submitApplication,
    fetchApplications,
    refreshSelectedJob,
  } = useCareerPilot()

  useEffect(() => {
    if (!analysis) {
      navigate('/')
    }
  }, [analysis, navigate])

  if (!analysis) {
    return null
  }

  const selectedJob = analysis.selectedJob || {}
  const jobList = analysis.shortlistedJobs || []

  const handleApply = async (job) => {
    const targetJob = job || selectedJob
    if (targetJob && targetJob.id !== selectedJob?.id) {
      refreshSelectedJob(targetJob)
    }
    await submitApplication()
    await fetchApplications()
  }

  return (
    <main className="min-h-[calc(100vh-72px)] bg-slate-50 pb-16">
      <section className="mx-auto max-w-6xl px-4 py-12 sm:px-6 lg:px-8">
        <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-sm uppercase tracking-[0.24em] text-indigo-600">Your internship analysis</p>
            <h1 className="mt-3 text-3xl font-semibold tracking-tight text-slate-900 sm:text-4xl">
              Results for “{analysis.query}”
            </h1>
          </div>
          <button
            type="button"
            onClick={() => navigate('/applications')}
            className="inline-flex items-center rounded-full bg-white px-5 py-3 text-sm font-semibold text-slate-900 shadow-soft transition hover:bg-slate-100"
          >
            View application history
          </button>
        </div>

        {loading && <LoadingSpinner />}

        {(error || success) && (
          <div className="mb-6 rounded-3xl border px-5 py-4 text-sm shadow-sm sm:px-6">
            {error && <p className="text-rose-700">{error}</p>}
            {success && <p className="text-emerald-700">{success}</p>}
          </div>
        )}

        <div className="grid gap-6 xl:grid-cols-[1.2fr,0.8fr]">
          <div className="space-y-6">
            <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-soft">
              <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                <div>
                  <p className="text-sm font-semibold uppercase tracking-[0.24em] text-indigo-600">Top match</p>
                  <h2 className="mt-2 text-2xl font-semibold text-slate-900">{selectedJob.title || selectedJob.role || 'Selected opportunity'}</h2>
                </div>
                <button
                  type="button"
                  onClick={handleApply}
                  className="rounded-full bg-indigo-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-indigo-700"
                >
                  Track this role
                </button>
              </div>
              <div className="mt-6 grid gap-4 sm:grid-cols-2">
                <div>
                  <p className="text-sm font-semibold text-slate-500">Company</p>
                  <p className="mt-2 text-base font-medium text-slate-900">{selectedJob.company}</p>
                </div>
                <div>
                  <p className="text-sm font-semibold text-slate-500">Location</p>
                  <p className="mt-2 text-base font-medium text-slate-900">{selectedJob.location || 'Remote'}</p>
                </div>
              </div>

              <div className="mt-6 flex flex-wrap items-center gap-3 text-sm text-slate-600">
                {selectedJob.employment_type && (
                  <span className="rounded-full bg-slate-100 px-3 py-1">{selectedJob.employment_type}</span>
                )}
                {selectedJob.match_score != null && (
                  <span className="rounded-full bg-emerald-100 px-3 py-1 text-emerald-700">Match {selectedJob.match_score}%</span>
                )}
                {selectedJob.match_reason && <span className="rounded-full bg-indigo-100 px-3 py-1 text-indigo-700">{selectedJob.match_reason}</span>}
              </div>

              <div className="mt-6 rounded-3xl bg-slate-50 p-5 text-sm leading-7 text-slate-700">
                <p>{selectedJob.description || 'A detailed summary from the job posting will appear here.'}</p>
              </div>
            </section>

            <CompanyReport report={analysis.companyReport} />
            <SkillGapCard gap={analysis.skillGap} />
            <ResumePreview resume={analysis.tailoredResume} />
            <DecisionCard decision={analysis.decision} />
          </div>

          <aside className="space-y-6">
            <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-soft">
              <div className="flex items-center justify-between gap-4">
                <div>
                  <h2 className="text-lg font-semibold text-slate-900">Shortlisted jobs</h2>
                  <p className="mt-2 text-sm text-slate-600">Browse the best matches from your search.</p>
                </div>
              </div>
              <div className="mt-6 space-y-4">
                {jobList.length === 0 ? (
                  <p className="text-sm text-slate-600">No additional opportunities were returned.</p>
                ) : (
                  jobList.slice(0, 4).map((job) => (
                    <JobCard
                      key={job.id || `${job.company}-${job.title}`}
                      job={job}
                      isSelected={selectedJob?.id === job?.id}
                      onSelect={(item) => refreshSelectedJob(item)}
                      onApply={() => handleApply(job)}
                    />
                  ))
                )}
              </div>
            </section>
          </aside>
        </div>
      </section>
    </main>
  )
}
