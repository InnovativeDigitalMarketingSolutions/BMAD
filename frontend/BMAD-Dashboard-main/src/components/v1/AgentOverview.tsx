// AgentOverview Component - Comprehensive agent management (Shadcn/ui compatible)
import React, { useState, useMemo, memo } from 'react'
import { Users, BarChart3, X, Activity, Clock, Zap, Search } from 'lucide-react'
import { AgentCard } from '@/components/ui/AgentCard'
import { PageHeader } from '@/components/ui/PageHeader'
import { BMADAgent } from '@/types/bmad'
import { useBMADAgents } from '@/hooks/useBMADAgents'
import { cn } from '@/lib/utils'

// Agent Details Modal Component
const AgentDetailsModal: React.FC<{
  agent: BMADAgent | null
  isOpen: boolean
  onClose: () => void
}> = ({ agent, isOpen, onClose }) => {
  if (!isOpen || !agent) return null

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-card rounded-2xl p-8 shadow-2xl border border-border max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-card-foreground">
            Agent Details - {agent.name}
          </h2>
          <button
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-muted transition-colors duration-200"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Agent Info */}
        <div className="space-y-6">
          {/* Basic Info */}
          <div className="bg-muted rounded-xl p-4">
            <h3 className="font-medium text-card-foreground mb-3">Basis Informatie</h3>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-muted-foreground">Naam:</span>
                <p className="text-card-foreground font-medium">{agent.name}</p>
              </div>
              <div>
                <span className="text-muted-foreground">ID:</span>
                <p className="text-card-foreground font-medium">{agent.id}</p>
              </div>
              <div>
                <span className="text-muted-foreground">Type:</span>
                <p className="text-card-foreground font-medium">{agent.type}</p>
              </div>
              <div>
                <span className="text-muted-foreground">Status:</span>
                <p className="text-card-foreground font-medium">{agent.status}</p>
              </div>
            </div>
          </div>

          {/* Performance Metrics */}
          <div className="bg-muted rounded-xl p-4">
            <h3 className="font-medium text-card-foreground mb-3">Prestatie Metingen</h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Algemene Prestatie</span>
                <span className="text-sm font-medium text-card-foreground">{agent.performance}%</span>
              </div>
              <div className="w-full bg-background rounded-full h-2">
                <div
                  className="bg-primary h-2 rounded-full transition-all duration-300"
                  style={{ width: `${agent.performance}%` }}
                />
              </div>
              <div className="grid grid-cols-3 gap-4 text-sm">
                <div>
                  <span className="text-muted-foreground">CPU:</span>
                  <p className="text-card-foreground">{agent.metrics?.cpu_usage || 'N/A'}%</p>
                </div>
                <div>
                  <span className="text-muted-foreground">Geheugen:</span>
                  <p className="text-card-foreground">{agent.metrics?.memory_usage || 'N/A'}%</p>
                </div>
                <div>
                  <span className="text-muted-foreground">Reactie:</span>
                  <p className="text-card-foreground">{agent.metrics?.response_time || 'N/A'}ms</p>
                </div>
              </div>
            </div>
          </div>

          {/* Tasks */}
          <div className="bg-muted rounded-xl p-4">
            <h3 className="font-medium text-card-foreground mb-3">Taken</h3>
            <div className="space-y-2">
              {Array.isArray(agent.tasks) && agent.tasks.length > 0 ? (
                agent.tasks.map((task) => (
                  <div key={task.id} className="flex items-center justify-between p-2 bg-background rounded-lg">
                    <div className="flex items-center space-x-2">
                      <span className="text-sm text-card-foreground">{task.name}</span>
                      <span className={cn(
                        "px-2 py-1 rounded-full text-xs font-medium",
                        task.status === 'running' ? 'bg-green-500 text-white' :
                        task.status === 'completed' ? 'bg-blue-500 text-white' :
                        task.status === 'failed' ? 'bg-red-500 text-white' :
                        'bg-yellow-500 text-black'
                      )}>
                        {task.status}
                      </span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className="text-sm text-muted-foreground">{task.progress}%</span>
                      <div className="w-16 h-2 bg-background rounded-full">
                        <div
                          className="bg-primary h-2 rounded-full transition-all duration-300"
                          style={{ width: `${task.progress}%` }}
                        />
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-sm text-muted-foreground">Geen actieve taken</p>
              )}
            </div>
          </div>

          {/* Last Activity */}
          <div className="bg-muted rounded-xl p-4">
            <h3 className="font-medium text-card-foreground mb-3">Laatste Activiteit</h3>
            <div className="flex items-center space-x-2 text-sm">
              <Clock className="w-4 h-4 text-muted-foreground" />
              <span className="text-muted-foreground">{agent.last_activity}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

const AgentOverviewComponent: React.FC = memo(() => {
  const { agents, loading, error } = useBMADAgents()
  const [selectedAgent, setSelectedAgent] = useState<BMADAgent | null>(null)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [showPerformanceView, setShowPerformanceView] = useState(false)
  const [filterStatus, setFilterStatus] = useState<'all' | 'active' | 'idle' | 'error' | 'stopped'>('all')
  const [sortBy, setSortBy] = useState<'name' | 'performance' | 'status'>('name')
  const [searchTerm, setSearchTerm] = useState('')

  // Performance statistics
  const performanceStats = useMemo(() => {
    // Ensure agents is always an array
    const safeAgents = Array.isArray(agents) ? agents : []
    
    const activeAgents = safeAgents.filter((agent: BMADAgent) => agent && agent.status === 'active')
    const avgPerformance = activeAgents.length > 0
      ? Math.round(activeAgents.reduce((sum: number, agent: BMADAgent) => sum + (agent.performance || 0), 0) / activeAgents.length)
      : 0

    return {
      totalAgents: safeAgents.length,
      activeAgents: safeAgents.filter((agent: BMADAgent) => agent && agent.status === 'active').length,
      idleAgents: safeAgents.filter((agent: BMADAgent) => agent && agent.status === 'idle').length,
      errorAgents: safeAgents.filter((agent: BMADAgent) => agent && agent.status === 'error').length,
      stoppedAgents: safeAgents.filter((agent: BMADAgent) => agent && agent.status === 'stopped').length,
      avgPerformance
    }
  }, [agents])

  // Filtered and sorted agents
  const filteredAgents = useMemo(() => {
    // Ensure agents is always an array
    const safeAgents = Array.isArray(agents) ? agents : []
    
    let filtered = safeAgents

    // Apply search filter
    if (searchTerm) {
      filtered = filtered.filter((agent: BMADAgent) => 
        agent && (
          agent.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
          agent.type.toLowerCase().includes(searchTerm.toLowerCase())
        )
      )
    }

    // Apply status filter
    if (filterStatus !== 'all') {
      filtered = filtered.filter((agent: BMADAgent) => agent && agent.status === filterStatus)
    }

    // Apply sorting
    filtered.sort((a: BMADAgent, b: BMADAgent) => {
      switch (sortBy) {
        case 'name':
          return (a.name || '').localeCompare(b.name || '')
        case 'performance':
          return (b.performance || 0) - (a.performance || 0)
        case 'status':
          return (a.status || '').localeCompare(b.status || '')
        default:
          return 0
      }
    })

    return filtered
  }, [agents, searchTerm, filterStatus, sortBy])

  const handleStartAgent = async (agentId: string) => {
    if (!agentId) {
      console.error('Invalid agent ID provided')
      return
    }
    
    try {
              // Starting agent
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
              // Stopping agent
    } catch (error) {
      console.error('Error stopping agent:', error)
    }
  }

  // Loading state
  if (loading) {
    return (
      <div className="min-h-screen bg-background text-foreground">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <PageHeader title="Agent Overzicht" subtitle="Live Monitoring" />
          <div className="text-center py-12">
            <h2 className="text-xl font-semibold text-card-foreground mb-2">
              Laden Agents...
            </h2>
          </div>
        </div>
      </div>
    )
  }

  // Error state
  if (error) {
    return (
      <div className="min-h-screen bg-background text-foreground">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <PageHeader title="Agent Overzicht" subtitle="Live Monitoring" />
          <div className="text-center py-12">
            <h2 className="text-xl font-semibold text-card-foreground mb-2">
              Fout bij laden agents
            </h2>
            <p className="text-muted-foreground">{error}</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background text-foreground">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* Header with Performance Toggle */}
        <PageHeader
          title="Agent Management"
          subtitle="Comprehensive Agent Monitoring & Control"
        >
          {/* Performance View Toggle */}
          <button
            onClick={() => setShowPerformanceView(!showPerformanceView)}
            className="flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium bg-secondary text-secondary-foreground hover:bg-secondary/80 transition-all duration-200"
          >
            <BarChart3 className="w-4 h-4" />
            <span>{showPerformanceView ? 'Analytics Verbergen' : 'Analytics Tonen'}</span>
          </button>
        </PageHeader>

        {/* Performance Analytics */}
        {showPerformanceView && (
          <div className="mb-8">
            <div className="bg-card rounded-2xl p-8 shadow-lg border border-border">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold text-card-foreground">
                  Prestatie Analytics
                </h2>
                <Zap className="w-6 h-6 text-muted-foreground" />
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* Average Performance */}
                <div className="bg-muted rounded-xl p-4">
                  <div className="flex items-center space-x-3 mb-3">
                    <BarChart3 className="w-5 h-5 text-primary" />
                    <h3 className="font-medium text-card-foreground">Gem. Prestatie</h3>
                  </div>
                  <div className="text-2xl font-bold text-card-foreground">
                    {performanceStats.avgPerformance}%
                  </div>
                  <div className="text-sm text-muted-foreground">
                    Over alle actieve agents
                  </div>
                </div>

                {/* Total Agents */}
                <div className="bg-muted rounded-xl p-4">
                  <div className="flex items-center space-x-3 mb-3">
                    <Users className="w-5 h-5 text-blue-500" />
                    <h3 className="font-medium text-card-foreground">Totaal Agents</h3>
                  </div>
                  <div className="text-2xl font-bold text-card-foreground">
                    {performanceStats.totalAgents}
                  </div>
                  <div className="text-sm text-muted-foreground">
                    Alle agent types
                  </div>
                </div>

                {/* Active Agents */}
                <div className="bg-muted rounded-xl p-4">
                  <div className="flex items-center space-x-3 mb-3">
                    <Activity className="w-5 h-5 text-green-500" />
                    <h3 className="font-medium text-card-foreground">Actieve Agents</h3>
                  </div>
                  <div className="text-2xl font-bold text-card-foreground">
                    {performanceStats.activeAgents}
                  </div>
                  <div className="text-sm text-muted-foreground">
                    Momenteel actief
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Agent Management */}
        <div className="mb-8">
          <div className="bg-card rounded-2xl p-8 shadow-lg border border-border">
            <div className="flex-shrink-0 mb-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-card-foreground">
                  BMAD Agents
                </h2>
                <div className="flex items-center space-x-3">
                  {/* Sort By */}
                  <select
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value as any)}
                    className="px-3 py-2 border rounded-lg text-sm bg-background"
                  >
                    <option value="name">Sorteer op Naam</option>
                    <option value="performance">Sorteer op Prestatie</option>
                    <option value="status">Sorteer op Status</option>
                  </select>
                </div>
              </div>
              
              {/* Search Bar */}
              <div className="relative mb-4">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
                <input
                  type="text"
                  placeholder="Zoek agents op naam of type..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary text-sm"
                />
              </div>
              
              {/* Filter Buttons */}
              <div className="flex flex-wrap gap-2">
                {[
                  { key: 'all', label: 'All Status', count: agents.length },
                  { key: 'active', label: 'Actief', count: performanceStats.activeAgents },
                  { key: 'idle', label: 'Inactief', count: performanceStats.idleAgents },
                  { key: 'stopped', label: 'Gestopt', count: performanceStats.stoppedAgents },
                  { key: 'error', label: 'Kritiek', count: performanceStats.errorAgents }
                ].map(({ key, label, count }) => (
                  <button
                    key={key}
                    onClick={() => setFilterStatus(key as any)}
                    className={cn(
                      "px-3 py-1 rounded-lg text-sm font-medium transition-all duration-200",
                      filterStatus === key
                        ? "bg-primary text-primary-foreground shadow-md"
                        : "bg-secondary text-secondary-foreground hover:bg-secondary/80"
                    )}
                  >
                    {label} ({count})
                  </button>
                ))}
              </div>
            </div>

            {/* Agent Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredAgents.map((agent) => (
                <AgentCard
                  key={agent.id}
                  agent={agent}
                  onStart={handleStartAgent}
                  onStop={handleStopAgent}
                  onClick={(agent) => {
                    setSelectedAgent(agent)
                    setIsModalOpen(true)
                  }}
                />
              ))}
            </div>

            {/* Empty State */}
            {filteredAgents.length === 0 && (
              <div className="text-center py-12">
                <Users className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-medium text-card-foreground mb-2">
                  Geen agents gevonden
                </h3>
                <p className="text-muted-foreground">
                  {filterStatus === 'all' 
                    ? 'Er zijn momenteel geen agents beschikbaar'
                    : `Geen agents met status "${filterStatus}" gevonden`
                  }
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Agent Status Summary */}
        <div className="mb-8">
          <div className="bg-card rounded-2xl p-8 shadow-lg border border-border">
            <h2 className="text-xl font-semibold text-card-foreground mb-6">
              Agent Status Samenvatting
            </h2>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-muted rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-green-500">
                  {performanceStats.activeAgents}
                </div>
                <div className="text-sm text-muted-foreground">Actief</div>
              </div>
              <div className="bg-muted rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-yellow-500">
                  {performanceStats.idleAgents}
                </div>
                <div className="text-sm text-muted-foreground">Inactief</div>
              </div>
              <div className="bg-muted rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-red-500">
                  {performanceStats.errorAgents}
                </div>
                <div className="text-sm text-muted-foreground">Fout</div>
              </div>
              <div className="bg-muted rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-gray-500">
                  {performanceStats.stoppedAgents}
                </div>
                <div className="text-sm text-muted-foreground">Gestopt</div>
              </div>
            </div>
          </div>
        </div>

      </div>

      {/* Agent Details Modal */}
      <AgentDetailsModal
        agent={selectedAgent}
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false)
          setSelectedAgent(null)
        }}
      />
    </div>
  )
})

export const AgentOverview = AgentOverviewComponent
export default AgentOverviewComponent 