import { useState, useEffect } from 'react'

export interface PerformanceMetric {
  agentId: string
  agentName: string
  cpu: number
  memory: number
  responseTime: number
  throughput: number
  errorRate: number
  timestamp: string
}

export interface PerformanceAlert {
  id: string
  agentId: string
  type: 'high_cpu' | 'high_memory' | 'slow_response' | 'high_error_rate'
  severity: 'low' | 'medium' | 'high' | 'critical'
  message: string
  timestamp: string
  resolved: boolean
}

export const useAgentPerformance = () => {
  const [metrics, setMetrics] = useState<PerformanceMetric[]>([])
  const [alerts, setAlerts] = useState<PerformanceAlert[]>([])

  // Real performance data from API
  useEffect(() => {
    const fetchPerformanceData = async () => {
      try {
        const response = await fetch('/api/performance')
        if (response.ok) {
          const data = await response.json()
          if (Array.isArray(data.metrics)) {
            setMetrics(data.metrics)
          }
          if (Array.isArray(data.alerts)) {
            setAlerts(data.alerts)
          }
        }
      } catch (error) {
        console.warn('Failed to fetch performance data:', error)
        // Fallback to empty arrays
        setMetrics([])
        setAlerts([])
      }
    }

    fetchPerformanceData()
    const interval = setInterval(fetchPerformanceData, 15000) // Refresh every 15 seconds
    return () => clearInterval(interval)
  }, [])

  const resolveAlert = (alertId: string) => {
    setAlerts(prev => prev.map(alert => 
      alert.id === alertId ? { ...alert, resolved: true } : alert
    ))
  }

  const getPerformanceSummary = () => {
    if (metrics.length === 0) return null

    const avgCpu = metrics.reduce((sum, m) => sum + m.cpu, 0) / metrics.length
    const avgMemory = metrics.reduce((sum, m) => sum + m.memory, 0) / metrics.length
    const avgResponseTime = metrics.reduce((sum, m) => sum + m.responseTime, 0) / metrics.length
    const avgThroughput = metrics.reduce((sum, m) => sum + m.throughput, 0) / metrics.length
    const avgErrorRate = metrics.reduce((sum, m) => sum + m.errorRate, 0) / metrics.length

    return {
      avgCpu,
      avgMemory,
      avgResponseTime,
      avgThroughput,
      avgErrorRate,
      totalAlerts: alerts.filter(a => !a.resolved).length
    }
  }

  return {
    metrics,
    alerts,
    resolveAlert,
    getPerformanceSummary
  }
} 