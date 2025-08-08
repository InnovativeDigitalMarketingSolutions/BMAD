// BMAD Dashboard v1 - Hoofddashboard voor BMAD agents
import React, { useState, useMemo, memo } from 'react'
import { Cpu, HardDrive, Users, TrendingUp } from 'lucide-react'
import { useBMADAgents } from '@/hooks/useBMADAgents'
import { useSystemMetrics } from '@/hooks/useSystemMetrics'
import { useWebSocket } from '@/hooks/useWebSocket'

import { AgentCard } from '@/components/ui/AgentCard'
import { ThemeToggle } from '@/components/ui/ThemeToggle'
import { CompactConnectionStatus } from '@/components/ui/ConnectionStatus'
import { cn } from '@/lib/utils'

// Alert thresholds
const ALERT_THRESHOLDS = {
  cpu: { warning: 70, critical: 90 },
  memory: { warning: 80, critical: 95 }
}

// Get alert status
const getAlertStatus = (value: number, thresholds: { warning: number; critical: number }) => {
  if (value >= thresholds.critical) return 'critical'
  if (value >= thresholds.warning) return 'warning'
  return 'normal'
}

// Get alert color
const getAlertColor = (status: string) => {
  switch (status) {
    case 'critical': return 'text-red-500 bg-red-500/10'
    case 'warning': return 'text-yellow-500 bg-yellow-500/10'
    default: return 'text-green-500 bg-green-500/10'
  }
}

// Get alert icon
const getAlertIcon = (status: string) => {
  switch (status) {
    case 'critical': return '🔴'
    case 'warning': return '🟡'
    default: return '🟢'
  }
}

// Progress Bar Component
const ProgressBar: React.FC<{ value: number; status: string }> = ({ value, status }) => (
  <div className="w-full bg-muted rounded-full h-2 mb-2">
    <div
      className={cn(
        "h-2 rounded-full transition-all duration-300",
        status === 'critical' ? "bg-red-500" :
        status === 'warning' ? "bg-yellow-500" : "bg-green-500"
      )}
      style={{ width: `${Math.min(value, 100)}%` }}
    />
  </div>
)

// Metric Card Component
const MetricCard: React.FC<{
  icon: React.ComponentType<{ className?: string }>
  title: string
  value: string | number
  status: string
  description: string
  badge: string
  badgeColor: string
}> = ({ icon: Icon, title, value, status, description, badge, badgeColor }) => (
  <div className={cn(
    "bg-card rounded-2xl p-6 shadow-lg border",
    "border-border hover:shadow-xl transition-all duration-200"
  )}>
    <div className="flex items-center justify-between mb-4">
      <div className={cn("p-3 rounded-lg", getAlertColor(status))}>
        <Icon className="w-8 h-8" />
      </div>
      <div className="flex items-center space-x-2">
        <span className={cn(
          "px-3 py-1 rounded-full text-xs font-medium",
          badgeColor
        )}>
          {badge}
        </span>
        <span className="text-lg">{getAlertIcon(status)}</span>
      </div>
    </div>
    <h3 className="text-lg font-semibold text-card-foreground mb-2">
      {title}
    </h3>
    <div className="text-3xl font-bold text-card-foreground mb-2">
      {value}
    </div>
    <div className="text-sm text-muted-foreground mb-3">
      {description}
    </div>
    {typeof value === 'number' && <ProgressBar value={value} status={status} />}
  </div>
)

const BMADDashboardComponent: React.FC = memo(() => {
  const { agents, loading: agentsLoading, error: agentsError, startAgent, stopAgent } = useBMADAgents()
  const { metrics } = useSystemMetrics()
  
  // WebSocket connection for real-time updates
  const {
    connectionStatus,
    isConnected
  } = useWebSocket({
    url: 'ws://localhost:5001/ws',
    autoReconnect: true,
    fallbackToPolling: true,
    pollingInterval: 10000 // 10 seconden voor betere performance
  })
  
  // Filter state
  const [statusFilter, setStatusFilter] = useState<string>('all')
  
  // Filtered agents with safety check
  const filteredAgents = useMemo(() => {
    if (!Array.isArray(agents)) return []
    if (statusFilter === 'all') return agents
    return agents.filter(agent => agent && agent.status === statusFilter)
  }, [agents, statusFilter])
  
  // Get unique statuses for filter options with safety check
  const availableStatuses = useMemo(() => {
    if (!Array.isArray(agents)) return ['all']
    const statuses = [...new Set(agents.filter(agent => agent && agent.status).map(agent => agent.status))]
    return ['all', ...statuses]
  }, [agents])

  const handleStartAgent = async (agentId: string) => {
    if (!agentId) {
      console.error('Invalid agent ID provided')
      return
    }
    
    try {
      const result = await startAgent(agentId)
      if (result.success) {
        // Agent started successfully
      } else {
        console.error('Failed to start agent:', result.message)
      }
    } catch (error) {
      console.error('Error starting agent:', error)
    }
  }

  const handleStopAgent = async (agentId: string) => {
    if (!agentId) {
      console.error('Invalid agent ID provided')
      return
    }
    
    try {
      const result = await stopAgent(agentId)
      if (result.success) {
        // Agent stopped successfully
      } else {
        console.error('Failed to stop agent:', result.message)
      }
    } catch (error) {
      console.error('Error stopping agent:', error)
    }
  }



  return (
    <div className={cn(
      "min-h-screen transition-colors duration-200",
      "bg-background text-foreground"
    )}>
      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* Header */}
        <div className="mb-8">
          <div className={cn(
            "bg-card rounded-2xl p-8 shadow-lg border",
            "border-border h-32" // Vaste hoogte van 128px voor consistentie
          )}>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div>
                  <h1 className="text-2xl font-bold text-card-foreground">
                    BMAD Dashboard v1.0
                  </h1>
                  <p className="text-sm text-muted-foreground">
                    Live Monitoring
                  </p>
                </div>
              </div>
              
              <div className="flex items-center space-x-4">
                {/* Connection Status */}
                <CompactConnectionStatus
                  status={connectionStatus}
                  isPolling={!isConnected && connectionStatus === 'connected'}
                  className="p-2 rounded-lg border border-border"
                />
                
                <ThemeToggle />
              </div>
            </div>
          </div>
        </div>

                {/* System Health Block */}
        <div className="mb-8">
          <div className={cn(
            "bg-card rounded-2xl p-8 shadow-lg border",
            "border-border"
          )}>
            <div className="flex-shrink-0 mb-6">
              <h2 className="text-xl font-semibold text-card-foreground">
                BMAD Agent Systeem Gezondheid
              </h2>
            </div>
            {metrics && metrics.system_health ? (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                
                {/* Agent CPU Usage Card */}
                <MetricCard
                  icon={Cpu}
                  title="Agent CPU Gebruik"
                  value={`${parseInt(metrics.system_health.cpu_usage) || 0}%`}
                  status={getAlertStatus(parseInt(metrics.system_health.cpu_usage) || 0, ALERT_THRESHOLDS.cpu)}
                  description="Gemiddeld CPU gebruik van alle agents"
                  badge="Agent CPU"
                  badgeColor="bg-blue-500 text-white"
                />

                {/* Agent Memory Usage Card */}
                <MetricCard
                  icon={HardDrive}
                  title="Agent Geheugen"
                  value={`${parseInt(metrics.system_health.memory_usage) || 0}%`}
                  status={getAlertStatus(parseInt(metrics.system_health.memory_usage) || 0, ALERT_THRESHOLDS.memory)}
                  description="Gemiddeld geheugen gebruik van alle agents"
                  badge="Agent RAM"
                  badgeColor="bg-green-500 text-white"
                />

                {/* Agent Success Rate Card */}
                <MetricCard
                  icon={TrendingUp}
                  title="Agent Success Rate"
                  value={`${metrics.system_health.agent_success_rate || 0}%`}
                  status={getAlertStatus(metrics.system_health.agent_success_rate || 0, { warning: 70, critical: 50 })}
                  description="Percentage succesvolle agent taken"
                  badge="Success"
                  badgeColor="bg-purple-500 text-white"
                />

              </div>
            ) : (
              <div className="text-center py-8">
                <p className="text-muted-foreground">Loading system health data...</p>
              </div>
            )}
          </div>
        </div>

        {/* BMAD Agents Block */}
        <div className="mb-8">
          <div className={cn(
            "bg-card rounded-2xl p-8 shadow-lg border",
            "border-border" // Verwijder vaste hoogte en flexbox
          )}>
            {/* Header met titel en filter buttons */}
            <div className="flex-shrink-0 mb-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-card-foreground">
                  BMAD Agents
                </h2>
                {agentsError && (
                  <div className="text-sm text-destructive">
                    Error loading agents: {agentsError}
                  </div>
                )}
              </div>
              
              {/* Filter Buttons */}
              <div className="flex flex-wrap gap-2">
                {availableStatuses.map(status => (
                  <button
                    key={status}
                    onClick={() => setStatusFilter(status)}
                    className={cn(
                      "px-3 py-1 rounded-lg text-sm font-medium transition-all duration-200",
                      statusFilter === status
                        ? "bg-primary text-primary-foreground shadow-md"
                        : "bg-secondary text-secondary-foreground hover:bg-secondary/80"
                    )}
                  >
                    {status === 'all' ? 'All Status' : status.charAt(0).toUpperCase() + status.slice(1)}
                  </button>
                ))}
                
                {/* Remove duplicate Error Filter Button - error status is handled in the loop above */}
              </div>
            </div>

            {agentsLoading ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-h-96 overflow-y-auto">
                {[1, 2, 3, 4, 5, 6].map((i) => (
                  <div key={i} className={cn(
                    "bg-muted rounded-xl p-6 animate-pulse"
                  )}>
                    <div className="h-4 bg-muted-foreground/20 rounded mb-4"></div>
                    <div className="h-3 bg-muted-foreground/20 rounded mb-2"></div>
                    <div className="h-3 bg-muted-foreground/20 rounded"></div>
                  </div>
                ))}
              </div>
            ) : filteredAgents.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-h-96 overflow-y-auto pr-2">
                {filteredAgents.map((agent) => (
                  <AgentCard
                    key={agent.id}
                    agent={agent}
                    onStart={handleStartAgent}
                    onStop={handleStopAgent}
                  />
                ))}
              </div>
            ) : (
              <div className="flex items-center justify-center py-8">
                <div className="text-center">
                  <Users className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
                  <h3 className="text-xl font-medium text-card-foreground mb-2">
                    No BMAD Agents Found
                  </h3>
                  <p className="text-muted-foreground">
                    No agents are currently running. Start some agents to see them here.
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
})

export const BMADDashboard = BMADDashboardComponent
export default BMADDashboardComponent 