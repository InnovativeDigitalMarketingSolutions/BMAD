// System Metrics Hook - Live API data van poort 5001
import { useState, useEffect, useCallback } from 'react'
import { BMADMetrics } from '@/types/bmad'

const API_BASE = 'http://localhost:5001/api'
const API_TIMEOUT = 5000 // 5 seconden timeout

interface MetricsResponse {
  metrics: BMADMetrics
  timestamp?: string
}

// Timeout wrapper voor fetch
const fetchWithTimeout = async (url: string, options: RequestInit = {}, timeout: number = API_TIMEOUT) => {
  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), timeout)
  
  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal
    })
    clearTimeout(timeoutId)
    return response
  } catch (error) {
    clearTimeout(timeoutId)
    if (error instanceof Error && error.name === 'AbortError') {
      throw new Error('Request timeout - server niet bereikbaar')
    }
    throw error
  }
}

export const useSystemMetrics = () => {
  const [metrics, setMetrics] = useState<BMADMetrics | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [retryCount, setRetryCount] = useState(0)

  const fetchMetrics = useCallback(async () => {
    const startTime = Date.now()
    
    try {
      setLoading(true)
      setError(null)
      
      const response = await fetchWithTimeout(`${API_BASE}/metrics`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      }, API_TIMEOUT)
      
      if (!response.ok) {
        const errorText = await response.text().catch(() => 'Unknown error')
        throw new Error(`Server error: ${response.status} - ${errorText}`)
      }
      
      const data: MetricsResponse = await response.json()
      
      // Validate response structure
      if (data && data.metrics && data.metrics.system_health) {
        setMetrics(data.metrics)
        setRetryCount(0) // Reset retry count on success
        
        // Log performance metrics only for slow responses
        const responseTime = Date.now() - startTime
        
        if (responseTime > 500) {
          console.warn(`⚠️ Slow API Response: SystemMetrics took ${responseTime}ms`)
        }
      } else {
        console.warn('Invalid metrics response structure:', data)
        throw new Error('Ongeldige data van server ontvangen')
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Verbinding met server mislukt'
      setError(errorMessage)
      console.error('Error fetching system metrics:', err)
      
      // Increment retry count for exponential backoff
      setRetryCount(prev => prev + 1)
      
      // Don't crash the app, just set null
      setMetrics(null)
    } finally {
      setLoading(false)
    }
  }, [])

  // Auto-refresh met exponential backoff bij errors
  useEffect(() => {
    fetchMetrics()
    
    // Calculate interval based on retry count (exponential backoff)
    const baseInterval = 15000 // 15 seconds
    const backoffMultiplier = Math.min(Math.pow(2, retryCount), 8) // Max 8x backoff
    const interval = retryCount > 0 ? baseInterval * backoffMultiplier : baseInterval
    
    const timeoutId = setTimeout(fetchMetrics, interval)
    return () => clearTimeout(timeoutId)
  }, [fetchMetrics, retryCount])

  return {
    metrics,
    loading,
    error,
    retryCount,
    fetchMetrics
  }
} 