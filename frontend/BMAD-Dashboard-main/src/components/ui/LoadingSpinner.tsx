// Enhanced Loading Spinner Component
import React from 'react'
import { Loader2, Activity, Cpu, HardDrive } from 'lucide-react'
import { cn } from '@/lib/utils'

interface LoadingSpinnerProps {
  variant?: 'default' | 'dots' | 'pulse' | 'system'
  size?: 'sm' | 'md' | 'lg' | 'xl'
  text?: string
  className?: string
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  variant = 'default',
  size = 'md',
  text,
  className
}) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
    xl: 'w-12 h-12'
  }

  const renderSpinner = () => {
    switch (variant) {
      case 'dots':
        return (
          <div className="flex space-x-1">
            <div className="w-2 h-2 bg-primary rounded-full animate-bounce"></div>
            <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
            <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
          </div>
        )
      
      case 'pulse':
        return (
          <div className={cn(
            "rounded-full bg-primary animate-pulse",
            sizeClasses[size]
          )} />
        )
      
      case 'system':
        return (
          <div className="flex items-center space-x-2">
            <Cpu className={cn("animate-spin text-primary", sizeClasses[size])} />
            <HardDrive className={cn("animate-pulse text-secondary", sizeClasses[size])} />
            <Activity className={cn("animate-bounce text-accent", sizeClasses[size])} />
          </div>
        )
      
      default:
        return (
          <Loader2 className={cn(
            "animate-spin text-primary",
            sizeClasses[size]
          )} />
        )
    }
  }

  return (
    <div className={cn(
      "flex flex-col items-center justify-center space-y-3",
      className
    )}>
      {renderSpinner()}
      {text && (
        <p className="text-sm text-muted-foreground text-center">
          {text}
        </p>
      )}
    </div>
  )
}

// Full screen loading component
export const FullScreenLoader: React.FC<{ text?: string }> = ({ text = "Loading dashboard..." }) => (
  <div className="min-h-screen bg-background flex items-center justify-center">
    <LoadingSpinner
      variant="default"
      size="xl"
      text={text}
    />
  </div>
)

// Inline loading component
export const InlineLoader: React.FC<{ text?: string }> = ({ text }) => (
  <div className="flex items-center justify-center py-8">
    <LoadingSpinner
      variant="dots"
      size="md"
      text={text}
    />
  </div>
)

// System loading component for metrics
export const SystemLoader: React.FC<{ text?: string }> = ({ text = "Loading system metrics..." }) => (
  <div className="flex items-center justify-center py-8">
    <LoadingSpinner
      variant="system"
      size="lg"
      text={text}
    />
  </div>
)

export default LoadingSpinner 