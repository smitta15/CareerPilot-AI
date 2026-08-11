export default function CompanyReport({ report }) {
  if (!report || Object.keys(report).length === 0) {
    return (
      <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-soft">
        <h2 className="text-lg font-semibold text-slate-900">Company report</h2>
        <p className="mt-3 text-sm text-slate-600">Run a search to review the company's hiring focus and ATS keywords.</p>
      </div>
    )
  }

  return (
    <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-soft">
      <h2 className="text-lg font-semibold text-slate-900">Company report</h2>
      <div className="mt-5 space-y-5 text-sm text-slate-700">
        {report.overview && (
          <div>
            <h3 className="font-semibold text-slate-900">Overview</h3>
            <p className="mt-2 leading-7">{report.overview}</p>
          </div>
        )}
        {report.tech_stack && (
          <div>
            <h3 className="font-semibold text-slate-900">Tech stack</h3>
            <p className="mt-2 leading-7">{report.tech_stack}</p>
          </div>
        )}
        {report.interview_process && (
          <div>
            <h3 className="font-semibold text-slate-900">Interview process</h3>
            <p className="mt-2 leading-7">{report.interview_process}</p>
          </div>
        )}
        {report.hiring_focus && (
          <div>
            <h3 className="font-semibold text-slate-900">Hiring focus</h3>
            <p className="mt-2 leading-7">{report.hiring_focus}</p>
          </div>
        )}
        {report.ats_keywords && (
          <div>
            <h3 className="font-semibold text-slate-900">ATS keywords</h3>
            <p className="mt-2 leading-7 whitespace-pre-wrap">{report.ats_keywords}</p>
          </div>
        )}
      </div>
    </section>
  )
}
