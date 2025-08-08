// Agent Card Component - Apple-inspired design voor BMAD agents (Shadcn/ui compatible)
import React from 'react'
import { Play, Square, Activity, Clock } from 'lucide-react'
import { BMADAgent } from '@/types/bmad'
import { cn } from '@/lib/utils'

interface AgentCardProps {
  agent: BMADAgent
  onStart: (agentId: string) => void
  onStop: (agentId: string) => void
  onClick?: (agent: BMADAgent) => void
}

export const AgentCard: React.FC<AgentCardProps> = ({ agent, onStart, onStop, onClick }) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-500'
      case 'stopped':
        return 'bg-gray-500'
      case 'error':
        return 'bg-red-500'
      default:
        return 'bg-yellow-500'
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'active':
        return 'Actief'
      case 'stopped':
        return 'Gestopt'
      case 'error':
        return 'Kritiek'
      case 'idle':
        return 'Inactief'
      default:
        return 'Inactief' // Default to idle instead of unknown
    }
  }

  return (
    <div 
      className={cn(
        "bg-card rounded-2xl p-6 shadow-lg border border-border",
        "hover:shadow-xl transition-all duration-200",
        "relative agent-card",
        onClick && "cursor-pointer"
      )}
      onClick={() => onClick?.(agent)}
    >
      {/* Status Indicator */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <div className={cn(
            "w-3 h-3 rounded-full",
            getStatusColor(agent.status)
          )} />
          <span className={cn(
            "text-sm font-medium",
            agent.status === 'active' ? 'text-green-600' :
            agent.status === 'stopped' ? 'text-gray-600' :
            agent.status === 'error' ? 'text-red-600' : 'text-yellow-600'
          )}>
            {getStatusText(agent.status)}
          </span>
        </div>
        <div className="flex items-center space-x-1">
          <Activity className="w-4 h-4 text-muted-foreground" />
          <span className="text-sm text-muted-foreground">{agent.performance}%</span>
        </div>
      </div>

      {/* Agent Info */}
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-card-foreground mb-1">
          {agent.name}
        </h3>
        <p className="text-sm text-muted-foreground mb-2">
          {agent.type}
        </p>
        <div className="flex items-center space-x-2 text-sm text-muted-foreground">
          <Clock className="w-3 h-3" />
          <span>{agent.last_activity}</span>
        </div>
      </div>

      {/* Performance Bar */}
      <div className="mb-4">
        <div className="flex items-center justify-between text-sm mb-1">
          <span className="text-muted-foreground">Prestatie</span>
          <span className="text-card-foreground font-medium">{agent.performance}%</span>
        </div>
        <div className="w-full bg-muted rounded-full h-2 relative overflow-hidden">
          <div
            className={cn(
              "h-2 rounded-full transition-all duration-300",
              // All values under 100% stay green, only over 100% becomes red
              agent.performance > 100 ? "bg-red-500" : "bg-green-500"
            )}
            style={{ 
              width: `${Math.min(agent.performance, 100)}%`,
              // Add a stronger glow effect for critical values over 100%
              ...(agent.performance > 100 && {
                boxShadow: '0 0 12px rgba(239, 68, 68, 0.8)',
                filter: 'brightness(1.2)'
              })
            }}
          />
          {/* Show critical overflow indicator for values over 100% */}
          {agent.performance > 100 && (
            <div className="absolute right-0 top-0 h-2 w-1 bg-red-400 rounded-r-full" />
          )}
        </div>
        {/* Show critical warning for values over 100% */}
        {agent.performance > 100 && (
          <div className="text-xs text-red-600 mt-1 flex items-center">
            <Activity className="w-3 h-3 mr-1" />
            Kritiek: {agent.performance}% performance
          </div>
        )}
      </div>

      {/* Control Buttons */}
      <div className="flex items-center space-x-2">
        <button
          onClick={(e) => {
            e.stopPropagation()
            onStart(agent.id)
          }}
          disabled={agent.status === 'active'}
          className={cn(
            "flex items-center space-x-1 px-3 py-2 rounded-lg text-sm",
            agent.status === 'active'
              ? "bg-green-500 text-white cursor-not-allowed"
              : "bg-primary text-primary-foreground hover:bg-primary/90"
          )}
        >
          <Play className="w-3 h-3" />
          <span>Start</span>
        </button>
        <button
          onClick={(e) => {
            e.stopPropagation()
            onStop(agent.id)
          }}
          disabled={agent.status === 'stopped'}
          className={cn(
            "flex items-center space-x-1 px-3 py-2 rounded-lg text-sm",
            agent.status === 'stopped'
              ? "bg-gray-500 text-white cursor-not-allowed"
              : "bg-destructive text-destructive-foreground hover:bg-destructive/90"
          )}
        >
          <Square className="w-3 h-3" />
          <span>Stop</span>
        </button>
      </div>
    </div>
  )
} 