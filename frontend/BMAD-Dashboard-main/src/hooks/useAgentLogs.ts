import { useState, useEffect } from 'react'

export interface AgentLog {
  id: string
  agentId: string
  agentName: string
  level: 'INFO' | 'WARNING' | 'ERROR' | 'DEBUG'
  message: string
  timestamp: string
}

export const useAgentLogs = () => {
  const [logs, setLogs] = useState<AgentLog[]>([])

  // Real-time logs from API
  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const response = await fetch('/api/logs')
        if (response.ok) {
          const data = await response.json()
          if (Array.isArray(data.logs)) {
            setLogs(data.logs)
          }
        }
      } catch (error) {
        console.warn('Failed to fetch logs:', error)
        // Fallback to empty array
        setLogs([])
      }
    }

    fetchLogs()
    const interval = setInterval(fetchLogs, 10000) // Refresh every 10 seconds
    return () => clearInterval(interval)
  }, [])

  const clearLogs = () => {
    setLogs([])
  }

  const exportLogs = () => {
    const csvContent = logs.map(log => 
      `${log.timestamp},${log.agentName},${log.level},${log.message}`
    ).join('\n')
    
    const blob = new Blob([`timestamp,agent,level,message\n${csvContent}`], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `agent-logs-${new Date().toISOString().split('T')[0]}.csv`
    a.click()
    URL.revokeObjectURL(url)
  }

  return {
    logs,
    clearLogs,
    exportLogs
  }
} 