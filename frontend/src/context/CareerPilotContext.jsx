/* eslint-disable react-refresh/only-export-components */
import { createContext, useCallback, useContext, useMemo, useState } from 'react'
import { api, parseGraphResponse } from '../api/api'

const CareerPilotContext = createContext(null)

export function useCareerPilot() {
  const context = useContext(CareerPilotContext)
  if (!context) {
    throw new Error('useCareerPilot must be used within CareerPilotProvider')
  }
  return context
}

export function CareerPilotProvider({ children }) {
  const [threadId, setThreadId] = useState('')
  const [query, setQuery] = useState('')
  const [analysis, setAnalysis] = useState(null)
  const [applications, setApplications] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const clearMessages = useCallback(() => {
    setError('')
    setSuccess('')
  }, [])

  const searchInternships = useCallback(
    async (userQuery) => {
      setLoading(true)
      clearMessages()

      try {
        const response = await api.post('/chat', { user_query: userQuery })
        const parsed = parseGraphResponse(response)
        setThreadId(parsed.threadId)
        setQuery(userQuery)
        setAnalysis(parsed)
        return parsed
      } catch (err) {
        console.error(err)
        setError('Unable to run analysis. Please try again.')
        return null
      } finally {
        setLoading(false)
      }
    },
    [clearMessages]
  )

  const fetchApplications = useCallback(async () => {
    setLoading(true)
    clearMessages()
    try {
      const response = await api.get('/applications')
      const list = response?.data?.applications ?? []
      setApplications(list)
      return list
    } catch (err) {
      console.error(err)
      setError('Unable to load application history.')
      return []
    } finally {
      setLoading(false)
    }
  }, [clearMessages])

  const submitApplication = useCallback(async () => {
    if (!threadId) {
      setError('No active search thread. Start a search before applying.')
      return null
    }

    setLoading(true)
    clearMessages()

    try {
      const response = await api.post('/apply', {
        thread_id: threadId,
        approved: true,
      })
      const payload = response?.data ?? {}
      const list = payload.applications ?? []
      setApplications(list)
      const recorded = payload.application_recorded || payload.status === 'tracked'
      setSuccess(
        recorded
          ? 'Application recorded for tracking. No external employer submission was performed.'
          : 'Application was not recorded.'
      )
      return list
    } catch (err) {
      console.error(err)
      setError('Unable to record your application. Please try again.')
      return null
    } finally {
      setLoading(false)
    }
  }, [threadId, clearMessages])

  const refreshSelectedJob = useCallback((job) => {
    setAnalysis((current) => {
      if (!current) return current
      return {
        ...current,
        selectedJob: job,
      }
    })
  }, [])

  const value = useMemo(
    () => ({
      threadId,
      query,
      analysis,
      applications,
      loading,
      error,
      success,
      searchInternships,
      fetchApplications,
      submitApplication,
      refreshSelectedJob,
      clearMessages,
      setError,
      setSuccess,
    }),
    [
      threadId,
      query,
      analysis,
      applications,
      loading,
      error,
      success,
      searchInternships,
      fetchApplications,
      submitApplication,
      refreshSelectedJob,
      clearMessages,
    ]
  )

  return <CareerPilotContext.Provider value={value}>{children}</CareerPilotContext.Provider>
}
