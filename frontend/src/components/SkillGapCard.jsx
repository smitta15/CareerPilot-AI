export default function SkillGapCard({ gap }) {
  if (!gap || Object.keys(gap).length === 0) {
    return (
      <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-soft">
        <h2 className="text-lg font-semibold text-slate-900">Skill gap</h2>
        <p className="mt-3 text-sm text-slate-600">A skill gap summary will appear after the analysis is complete.</p>
      </div>
    )
  }

  if (typeof gap === 'string') {
    return (
      <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-soft">
        <h2 className="text-lg font-semibold text-slate-900">Skill gap</h2>
        <pre className="mt-3 whitespace-pre-wrap text-sm leading-7 text-slate-700">{gap}</pre>
      </div>
    )
  }

  return (
    <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-soft">
      <h2 className="text-lg font-semibold text-slate-900">Skill gap</h2>
      <div className="mt-5 grid gap-5 sm:grid-cols-2">
        {gap.matched_skills && (
          <div>
            <h3 className="text-sm font-semibold text-slate-900">Matched skills</h3>
            <ul className="mt-3 space-y-2 text-sm text-slate-700">
              {gap.matched_skills.map((skill) => (
                <li key={skill} className="rounded-2xl bg-slate-100 px-3 py-2">
                  {skill}
                </li>
              ))}
            </ul>
          </div>
        )}
        {gap.missing_skills && (
          <div>
            <h3 className="text-sm font-semibold text-slate-900">Missing skills</h3>
            <ul className="mt-3 space-y-2 text-sm text-slate-700">
              {gap.missing_skills.map((skill) => (
                <li key={skill} className="rounded-2xl bg-rose-100 px-3 py-2 text-rose-900">
                  {skill}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
      {gap.priority && (
        <div className="mt-6">
          <h3 className="text-sm font-semibold text-slate-900">Learning priority</h3>
          <ol className="mt-3 list-decimal space-y-2 pl-5 text-sm text-slate-700">
            {gap.priority.map((skill) => (
              <li key={skill}>{skill}</li>
            ))}
          </ol>
        </div>
      )}
    </section>
  )
}
