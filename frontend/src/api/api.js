import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

export const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export function parseGraphResponse(response) {
  const payload = response?.data ?? {}
  const result = payload.result ?? payload
  const state = result?.state ?? result ?? {}
  const interruptValue = Array.isArray(state?.__interrupt__) && state.__interrupt__.length > 0
    ? state.__interrupt__[0]?.value || {}
    : {}

  return {
    threadId: payload.thread_id || state?.thread_id || '',
    query: state?.user_query || '',
    status: payload.status || state?.status || '',
    approvalRequired: Boolean(payload.approval_required || state?.approval_required || interruptValue.approval_required),
    selectedJob: state?.selected_job || interruptValue.selected_job || state?.shortlisted_jobs?.[0] || {},
    shortlistedJobs: state?.shortlisted_jobs || state?.opportunities || [],
    companyReport: state?.company_report || {},
    skillGap: state?.skill_gap || {},
    tailoredResume: state?.tailored_resume || '',
    decision: state?.decision || interruptValue.decision || payload?.decision || {},
    matchScore: state?.match_score ?? interruptValue.match_score ?? 0,
    matchReason: state?.match_reason || interruptValue.match_reason || '',
    applications: state?.applications || [],
    rawState: state,
  }
}
