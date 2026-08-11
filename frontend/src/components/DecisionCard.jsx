export default function DecisionCard({ decision }) {
  if (!decision || Object.keys(decision).length === 0) {
    return (
      <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-soft">
        <h2 className="text-lg font-semibold text-slate-900">Decision</h2>
        <p className="mt-3 text-sm text-slate-600">The decision assistant will summarize whether you should apply.</p>
      </div>
    )
  }

  const recommendation = decision.recommendation || decision.summary || decision.reason || 'No recommendation available.'
  const strengths = Array.isArray(decision.strengths) ? decision.strengths : []
  const weaknesses = Array.isArray(decision.weaknesses) ? decision.weaknesses : []
  const nextSteps = Array.isArray(decision.next_steps) ? decision.next_steps : []

  return (
    <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-soft">
      <div className="flex items-center justify-between gap-4">
        <h2 className="text-lg font-semibold text-slate-900">Decision summary</h2>
        {decision.confidence != null && (
          <span className="rounded-full bg-emerald-100 px-3 py-1 text-sm font-semibold text-emerald-700">
            {Number(decision.confidence).toFixed(0)}% confident
          </span>
        )}
      </div>
      <p className="mt-4 text-sm font-semibold uppercase tracking-[0.18em] text-indigo-600">
        {decision.decision || 'decision'}
      </p>
      <p className="mt-4 text-sm leading-7 text-slate-700">{recommendation}</p>

      {decision.reason && (
        <div className="mt-4 rounded-3xl bg-slate-50 p-4 text-sm text-slate-700">
          <strong className="text-slate-900">Why:</strong> {decision.reason}
        </div>
      )}

      {(strengths.length > 0 || weaknesses.length > 0 || nextSteps.length > 0) && (
        <div className="mt-6 grid gap-5 md:grid-cols-3">
          {strengths.length > 0 && (
            <div className="rounded-2xl bg-emerald-50 p-4">
              <h3 className="text-sm font-semibold text-emerald-800">Strengths</h3>
              <ul className="mt-3 space-y-2 text-sm text-emerald-900">
                {strengths.map((item) => <li key={item}>• {item}</li>)}
              </ul>
            </div>
          )}
          {weaknesses.length > 0 && (
            <div className="rounded-2xl bg-amber-50 p-4">
              <h3 className="text-sm font-semibold text-amber-800">Watch-outs</h3>
              <ul className="mt-3 space-y-2 text-sm text-amber-900">
                {weaknesses.map((item) => <li key={item}>• {item}</li>)}
              </ul>
            </div>
          )}
          {nextSteps.length > 0 && (
            <div className="rounded-2xl bg-slate-100 p-4">
              <h3 className="text-sm font-semibold text-slate-900">Next steps</h3>
              <ul className="mt-3 space-y-2 text-sm text-slate-700">
                {nextSteps.map((item) => <li key={item}>• {item}</li>)}
              </ul>
            </div>
          )}
        </div>
      )}
    </section>
  )
}
