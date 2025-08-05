// Auto-refresh Toggle Component
import React, { useState } from 'react'
import { RefreshCw, Settings } from 'lucide-react'
import { cn } from '@/lib/utils'

interface AutoRefreshToggleProps {
  isEnabled: boolean
  isRefreshing: boolean
  interval: number
  lastRefresh: Date | null
  nextRefresh: Date | null
  onToggle: (enabled: boolean) => void
  onIntervalChange: (interval: number) => void
  className?: string
}

const INTERVAL_OPTIONS = [
  { value: 10000, label: '10s' },
  { value: 30000, label: '30s' },
  { value: 60000, label: '1m' },
  { value: 300000, label: '5m' },
  { value: 600000, label: '10m' }
]

export const AutoRefreshToggle: React.FC<AutoRefreshToggleProps> = ({
  isEnabled,
  isRefreshing,
  interval,
  lastRefresh,
  nextRefresh,
  onToggle,
  onIntervalChange,
  className
}) => {
  const [showSettings, setShowSettings] = useState(false)

  const formatTime = (date: Date | null) => {
    if (!date) return '--'
    return date.toLocaleTimeString('nl-NL', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  }

  const getTimeUntilNext = () => {
    if (!nextRefresh) return '--'
    const now = new Date()
    const diff = nextRefresh.getTime() - now.getTime()
    if (diff <= 0) return 'Nu'
    
    const seconds = Math.floor(diff / 1000)
    if (seconds < 60) return `${seconds}s`
    const minutes = Math.floor(seconds / 60)
    return `${minutes}m ${seconds % 60}s`
  }

  return (
    <div className={cn(
      "flex items-center space-x-2",
      className
    )}>
      {/* Toggle Button */}
      <button
        onClick={() => onToggle(!isEnabled)}
        className={cn(
          "flex items-center space-x-2 px-3 py-2 rounded-lg border",
          "transition-colors duration-200",
          isEnabled
            ? "bg-primary text-primary-foreground border-primary"
            : "bg-secondary text-secondary-foreground border-border hover:bg-secondary/80"
        )}
        title={isEnabled ? 'Auto-refresh aan' : 'Auto-refresh uit'}
      >
        <RefreshCw className={cn(
          "w-4 h-4",
          isRefreshing && "animate-spin"
        )} />
        <span className="text-sm font-medium">
          Auto-refresh
        </span>
      </button>

      {/* Settings Button */}
      <button
        onClick={() => setShowSettings(!showSettings)}
        className={cn(
          "p-2 rounded-lg border border-border",
          "hover:bg-secondary/50 transition-colors duration-200"
        )}
        title="Auto-refresh instellingen"
      >
        <Settings className="w-4 h-4" />
      </button>

      {/* Settings Panel */}
      {showSettings && (
        <div className={cn(
          "absolute top-full mt-2 right-0 z-50",
          "bg-card border border-border rounded-lg shadow-lg p-4",
          "min-w-64"
        )}>
          <div className="space-y-4">
            {/* Interval Selection */}
            <div>
              <label className="block text-sm font-medium text-card-foreground mb-2">
                Refresh Interval
              </label>
              <div className="grid grid-cols-3 gap-2">
                {INTERVAL_OPTIONS.map((option) => (
                  <button
                    key={option.value}
                    onClick={() => {
                      onIntervalChange(option.value)
                      setShowSettings(false)
                    }}
                    className={cn(
                      "px-3 py-2 text-sm rounded-md border transition-colors",
                      interval === option.value
                        ? "bg-primary text-primary-foreground border-primary"
                        : "bg-secondary text-secondary-foreground border-border hover:bg-secondary/80"
                    )}
                  >
                    {option.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Status Information */}
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Laatste refresh:</span>
                <span className="font-mono">{formatTime(lastRefresh)}</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Volgende refresh:</span>
                <span className="font-mono">{getTimeUntilNext()}</span>
              </div>
            </div>

            {/* Status Indicator */}
            <div className="flex items-center space-x-2">
              <div className={cn(
                "w-2 h-2 rounded-full",
                isEnabled ? "bg-green-500" : "bg-gray-400"
              )} />
              <span className="text-sm text-muted-foreground">
                {isEnabled ? 'Actief' : 'Inactief'}
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

// Compact version for small spaces
export const CompactAutoRefreshToggle: React.FC<{
  isEnabled: boolean
  isRefreshing: boolean
  onToggle: (enabled: boolean) => void
  className?: string
}> = ({
  isEnabled,
  isRefreshing,
  onToggle,
  className
}) => {
  return (
    <button
      onClick={() => onToggle(!isEnabled)}
      className={cn(
        "p-2 rounded-lg border transition-colors duration-200",
        isEnabled
          ? "bg-primary text-primary-foreground border-primary"
          : "bg-secondary text-secondary-foreground border-border hover:bg-secondary/80",
        className
      )}
      title={isEnabled ? 'Auto-refresh aan' : 'Auto-refresh uit'}
    >
      <RefreshCw className={cn(
        "w-4 h-4",
        isRefreshing && "animate-spin"
      )} />
    </button>
  )
}

export default AutoRefreshToggle 