export default function JobCard({ job, isSelected, onSelect, onApply }) {
  return (
    <article
      className={`rounded-3xl border p-5 shadow-soft transition hover:border-indigo-400 hover:shadow-lg ${
        isSelected ? 'border-indigo-500 bg-indigo-50/50' : 'border-slate-200 bg-white'
      }`}
    >
      <div className="flex items-start justify-between gap-4">
        <div>
          <h3 className="text-lg font-semibold text-slate-900">{job.title || job.role || 'Untitled Role'}</h3>
          <p className="mt-1 text-sm text-slate-600">{job.company}</p>
        </div>
        <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-slate-700">
          {job.location || 'Remote'}
        </span>
      </div>

      <div className="mt-4 flex flex-wrap items-center gap-2 text-sm text-slate-600">
        {job.match_score != null && (
          <span className="rounded-full bg-emerald-100 px-3 py-1 font-medium text-emerald-800">
            Match {job.match_score}%
          </span>
        )}
        {job.employment_type && <span className="rounded-full bg-slate-100 px-3 py-1">{job.employment_type}</span>}
      </div>

      <p className="mt-4 line-clamp-4 text-sm leading-6 text-slate-700">{job.description}</p>

      {Array.isArray(job.skills) && job.skills.length > 0 && (
        <div className="mt-4 flex flex-wrap gap-2">
          {job.skills.slice(0, 6).map((skill) => (
            <span key={skill} className="rounded-full bg-slate-100 px-3 py-1 text-xs text-slate-700">
              {skill}
            </span>
          ))}
        </div>
      )}

      <div className="mt-5 flex flex-wrap gap-3">
        <button
          type="button"
          onClick={() => onSelect?.(job)}
          className="rounded-full border border-indigo-200 bg-indigo-50 px-4 py-2 text-sm font-semibold text-indigo-700 transition hover:bg-indigo-100"
        >
          View details
        </button>
        <button
          type="button"
          onClick={() => onApply?.(job)}
          className="rounded-full border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
        >
          Apply
        </button>
      </div>
    </article>
  )
}
