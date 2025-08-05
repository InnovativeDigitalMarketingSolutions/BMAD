import { useState } from 'react'

export interface AgentControl {
  id: string
  agentId: string
  action: 'start' | 'stop' | 'restart'
  status: 'pending' | 'success' | 'error'
  message?: string
  timestamp: string
}

export const useAgentControls = () => {
  const [controls, setControls] = useState<AgentControl[]>([])

  const executeControl = async (agentId: string, action: AgentControl['action']) => {
    try {
      const response = await fetch(`http://localhost:5001/api-proxy/agents/${agentId}/${action}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      })

      const control: AgentControl = {
        id: Date.now().toString(),
        agentId,
        action,
        status: response.ok ? 'success' : 'error',
        message: response.ok 
          ? `${action} command executed successfully for agent ${agentId}`
          : `Failed to ${action} agent ${agentId}`,
        timestamp: new Date().toISOString()
      }

      setControls(prev => [control, ...prev].slice(0, 50)) // Keep last 50 controls
      
      return { success: response.ok, message: control.message }
    } catch (err) {
      const errorMessage = `Failed to ${action} agent ${agentId}`
      
      const control: AgentControl = {
        id: Date.now().toString(),
        agentId,
        action,
        status: 'error',
        message: errorMessage,
        timestamp: new Date().toISOString()
      }

      setControls(prev => [control, ...prev].slice(0, 50))
      
      return { success: false, message: errorMessage }
    }
  }

  const startAgent = (agentId: string) => executeControl(agentId, 'start')
  const stopAgent = (agentId: string) => executeControl(agentId, 'stop')
  const restartAgent = (agentId: string) => executeControl(agentId, 'restart')

  return {
    controls,
    startAgent,
    stopAgent,
    restartAgent
  }
} 