// BMAD Agents Hook - Live API data van poort 5001
import { useState, useEffect, useCallback } from 'react'
import { BMADAgent } from '@/types/bmad'
import { stabilityTest } from '@/utils/stabilityTest'

const API_BASE = 'http://localhost:5001/api-proxy'

interface AgentResponse {
  agents: BMADAgent[]
  total?: number
  active?: number
  timestamp?: string
}

interface AgentActionResponse {
  success: boolean
  message: string
}

export const useBMADAgents = () => {
  const [agents, setAgents] = useState<BMADAgent[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [retryCount, setRetryCount] = useState(0)

  // Ensure agents is always an array
  const safeAgents = Array.isArray(agents) ? agents : []

  const fetchAgents = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 10000) // Increased timeout to 10 seconds
      
      const response = await fetch(`${API_BASE}/agents`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: controller.signal
      })
      
      clearTimeout(timeoutId)
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const data: AgentResponse = await response.json()
      
      // Stability validation
      if (!stabilityTest.validateApiResponse(data, ['agents'])) {
        console.warn('Invalid agents API response structure')
        setAgents([])
        return
      }
      
      // Validate agents array
      if (stabilityTest.validateArray(data.agents, (agent) => 
        stabilityTest.validateObject(agent, ['id', 'name', 'status'])
      )) {
        setAgents(data.agents)
        setRetryCount(0) // Reset retry count on success
      } else {
        console.warn('Invalid agents array structure')
        setAgents([])
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch agents'
      setError(errorMessage)
      console.error('Error fetching BMAD agents:', err)
      
      // Increment retry count
      setRetryCount(prev => prev + 1)
      
      // Don't crash the app, just set empty array
      setAgents([])
    } finally {
      setLoading(false)
    }
  }, [])

  const startAgent = useCallback(async (agentId: string): Promise<AgentActionResponse> => {
    if (!stabilityTest.validateString(agentId, 1)) {
      return { success: false, message: 'Invalid agent ID' }
    }

    try {
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 5000)
      
      const response = await fetch(`${API_BASE}/agents/${agentId}/start`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json' 
        },
        signal: controller.signal
      })
      
      clearTimeout(timeoutId)
      
      if (!response.ok) {
        throw new Error(`Failed to start agent: ${response.status}`)
      }
      
      // Refresh agents after action
      await fetchAgents()
      return { success: true, message: 'Agent started successfully' }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to start agent'
      console.error('Error starting agent:', err)
      return { success: false, message }
    }
  }, [fetchAgents])

  const stopAgent = useCallback(async (agentId: string): Promise<AgentActionResponse> => {
    if (!stabilityTest.validateString(agentId, 1)) {
      return { success: false, message: 'Invalid agent ID' }
    }

    try {
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 5000)
      
      const response = await fetch(`${API_BASE}/agents/${agentId}/stop`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json' 
        },
        signal: controller.signal
      })
      
      clearTimeout(timeoutId)
      
      if (!response.ok) {
        throw new Error(`Failed to stop agent: ${response.status}`)
      }
      
      // Refresh agents after action
      await fetchAgents()
      return { success: true, message: 'Agent stopped successfully' }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to stop agent'
      console.error('Error stopping agent:', err)
      return { success: false, message }
    }
  }, [fetchAgents])

  // Auto-refresh elke 15 seconden voor betere real-time updates
  useEffect(() => {
    fetchAgents()
    
    const interval = setInterval(fetchAgents, 15000)
    return () => clearInterval(interval)
  }, [fetchAgents])

  return {
    agents: safeAgents,
    loading,
    error,
    retryCount,
    fetchAgents,
    startAgent,
    stopAgent
  }
} 