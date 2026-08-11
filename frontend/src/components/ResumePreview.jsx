import { useMemo } from 'react'

export default function ResumePreview({ resume }) {
  const markdown = resume || 'No tailored resume is available yet.'

  const fileName = useMemo(() => `careerpilot-resume-${new Date().getTime()}.md`, [])

  const downloadResume = () => {
    const blob = new Blob([markdown], { type: 'text/markdown;charset=utf-8' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = fileName
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  }

  return (
    <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-soft">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-lg font-semibold text-slate-900">Tailored resume</h2>
          <p className="mt-2 text-sm text-slate-600">Download a resume version crafted for the selected internship.</p>
        </div>
        <button
          type="button"
          onClick={downloadResume}
          className="rounded-full bg-indigo-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-indigo-700"
        >
          Download resume
        </button>
      </div>

      <pre className="mt-5 max-h-80 overflow-y-auto whitespace-pre-wrap rounded-3xl bg-slate-50 p-5 text-sm leading-6 text-slate-700">
        {markdown}
      </pre>
    </section>
  )
}
