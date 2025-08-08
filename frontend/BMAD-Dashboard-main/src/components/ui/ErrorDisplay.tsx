// Error Display Component - User-friendly error messages
import React from 'react'
import { AlertTriangle, RefreshCw, Wifi, Server } from 'lucide-react'
import { cn } from '@/lib/utils'

interface ErrorDisplayProps {
  error: string | null
  onRetry?: () => void
  variant?: 'inline' | 'card' | 'fullscreen'
  className?: string
}

export const ErrorDisplay: React.FC<ErrorDisplayProps> = ({
  error,
  onRetry,
  variant = 'inline',
  className
}) => {
  if (!error) return null

  // Determine error type and icon
  const getErrorIcon = (errorMessage: string) => {
    if (errorMessage.includes('timeout') || errorMessage.includes('niet bereikbaar')) {
      return <Wifi className="w-5 h-5" />
    }
    if (errorMessage.includes('Server error')) {
      return <Server className="w-5 h-5" />
    }
    return <AlertTriangle className="w-5 h-5" />
  }

  const getErrorColor = (errorMessage: string) => {
    if (errorMessage.includes('timeout') || errorMessage.includes('niet bereikbaar')) {
      return 'border-yellow-500/20 bg-yellow-500/10 text-yellow-700'
    }
    if (errorMessage.includes('Server error')) {
      return 'border-red-500/20 bg-red-500/10 text-red-700'
    }
    return 'border-orange-500/20 bg-orange-500/10 text-orange-700'
  }

  const getErrorMessage = (errorMessage: string) => {
    if (errorMessage.includes('timeout') || errorMessage.includes('niet bereikbaar')) {
      return 'Verbinding met server verloren. Controleer je internetverbinding.'
    }
    if (errorMessage.includes('Server error')) {
      return 'Server probleem gedetecteerd. Probeer het later opnieuw.'
    }
    return 'Er is een fout opgetreden. Probeer de pagina te verversen.'
  }

  const errorIcon = getErrorIcon(error)
  const errorColor = getErrorColor(error)
  const userMessage = getErrorMessage(error)

  if (variant === 'fullscreen') {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center p-4">
        <div className={cn(
          "bg-card rounded-2xl p-8 shadow-lg border max-w-2xl w-full text-center",
          errorColor
        )}>
          <div className="flex justify-center mb-6">
            <div className="p-4 rounded-full bg-current/10">
              {errorIcon}
            </div>
          </div>
          <h2 className="text-xl font-semibold mb-4">Verbinding Probleem</h2>
          <p className="text-sm mb-6">{userMessage}</p>
          {onRetry && (
            <button
              onClick={onRetry}
              className="inline-flex items-center space-x-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
            >
              <RefreshCw className="w-4 h-4" />
              <span>Opnieuw proberen</span>
            </button>
          )}
        </div>
      </div>
    )
  }

  if (variant === 'card') {
    return (
      <div className={cn(
        "bg-card rounded-2xl p-6 shadow-lg border",
        errorColor,
        className
      )}>
        <div className="flex items-start space-x-4">
          <div className="flex-shrink-0">
            {errorIcon}
          </div>
          <div className="flex-1">
            <h3 className="font-semibold mb-2">Verbinding Probleem</h3>
            <p className="text-sm mb-4">{userMessage}</p>
            {onRetry && (
              <button
                onClick={onRetry}
                className="inline-flex items-center space-x-2 px-3 py-1.5 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors text-sm"
              >
                <RefreshCw className="w-3 h-3" />
                <span>Opnieuw proberen</span>
              </button>
            )}
          </div>
        </div>
      </div>
    )
  }

  // Inline variant (default)
  return (
    <div className={cn(
      "flex items-center space-x-3 p-3 rounded-lg border",
      errorColor,
      className
    )}>
      {errorIcon}
      <div className="flex-1">
        <p className="text-sm font-medium">{userMessage}</p>
      </div>
      {onRetry && (
        <button
          onClick={onRetry}
          className="flex-shrink-0 p-1 rounded hover:bg-current/10 transition-colors"
          title="Opnieuw proberen"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      )}
    </div>
  )
} 