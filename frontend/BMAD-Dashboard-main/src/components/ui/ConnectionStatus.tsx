// Connection Status Indicator Component
import React from 'react'
import { Wifi, WifiOff, RefreshCw, AlertCircle } from 'lucide-react'
import { cn } from '@/lib/utils'

interface ConnectionStatusProps {
  status: 'connected' | 'connecting' | 'disconnected' | 'error'
  isPolling?: boolean
  reconnectAttempts?: number
  maxReconnectAttempts?: number
  onReconnect?: () => void
  className?: string
}

export const ConnectionStatus: React.FC<ConnectionStatusProps> = ({
  status,
  isPolling = false,
  reconnectAttempts = 0,
  maxReconnectAttempts = 5,
  onReconnect,
  className
}) => {
  const getStatusConfig = () => {
    switch (status) {
      case 'connected':
        return {
          icon: Wifi,
          text: isPolling ? 'Polling Mode' : 'Connected',
          color: 'text-green-500',
          bgColor: 'bg-green-500/10',
          borderColor: 'border-green-500/20'
        }
      case 'connecting':
        return {
          icon: RefreshCw,
          text: `Connecting${reconnectAttempts > 0 ? ` (${reconnectAttempts}/${maxReconnectAttempts})` : ''}`,
          color: 'text-yellow-500',
          bgColor: 'bg-yellow-500/10',
          borderColor: 'border-yellow-500/20'
        }
      case 'disconnected':
        return {
          icon: WifiOff,
          text: 'Disconnected',
          color: 'text-gray-500',
          bgColor: 'bg-gray-500/10',
          borderColor: 'border-gray-500/20'
        }
      case 'error':
        return {
          icon: AlertCircle,
          text: 'Connection Error',
          color: 'text-red-500',
          bgColor: 'bg-red-500/10',
          borderColor: 'border-red-500/20'
        }
    }
  }

  const config = getStatusConfig()
  const Icon = config.icon

  return (
    <div className={cn(
      "flex items-center space-x-2 px-3 py-2 rounded-lg border",
      config.bgColor,
      config.borderColor,
      className
    )}>
      <Icon className={cn(
        "w-4 h-4",
        config.color,
        status === 'connecting' && "animate-spin"
      )} />
      
      <span className={cn(
        "text-sm font-medium",
        config.color
      )}>
        {config.text}
      </span>

      {status === 'disconnected' && onReconnect && (
        <button
          onClick={onReconnect}
          className={cn(
            "ml-2 p-1 rounded-md",
            "hover:bg-gray-500/20 transition-colors"
          )}
          title="Reconnect"
        >
          <RefreshCw className="w-3 h-3 text-gray-500" />
        </button>
      )}
    </div>
  )
}

// Compact version for small spaces
export const CompactConnectionStatus: React.FC<ConnectionStatusProps> = ({
  status,
  isPolling = false,
  className
}) => {
  const getStatusConfig = () => {
    switch (status) {
      case 'connected':
        return {
          icon: Wifi,
          color: 'text-green-500',
          title: isPolling ? 'Polling Mode' : 'Connected'
        }
      case 'connecting':
        return {
          icon: RefreshCw,
          color: 'text-yellow-500',
          title: 'Connecting'
        }
      case 'disconnected':
        return {
          icon: WifiOff,
          color: 'text-gray-500',
          title: 'Disconnected'
        }
      case 'error':
        return {
          icon: AlertCircle,
          color: 'text-red-500',
          title: 'Connection Error'
        }
    }
  }

  const config = getStatusConfig()
  const Icon = config.icon

  return (
    <div
      className={cn(
        "p-1 rounded-full",
        className
      )}
      title={config.title}
    >
      <Icon className={cn(
        "w-4 h-4",
        config.color,
        status === 'connecting' && "animate-spin"
      )} />
    </div>
  )
}

export default ConnectionStatus 