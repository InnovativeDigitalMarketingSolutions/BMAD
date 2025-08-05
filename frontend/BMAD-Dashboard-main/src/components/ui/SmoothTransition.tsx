// Smooth Transition Component voor Consistente UI Updates
import React, { useState, useEffect } from 'react'
import { cn } from '@/lib/utils'

interface SmoothTransitionProps {
  children: React.ReactNode
  className?: string
  transitionDuration?: number
  fadeIn?: boolean
  fadeOut?: boolean
  onTransitionComplete?: () => void
}

export const SmoothTransition: React.FC<SmoothTransitionProps> = ({
  children,
  className,
  transitionDuration = 300
}) => {
  return (
    <div
      className={cn(
        "transition-all duration-300 ease-in-out opacity-100 scale-100",
        className
      )}
      style={{
        transitionDuration: `${transitionDuration}ms`
      }}
    >
      {children}
    </div>
  )
}

// Stable Container voor Content die niet mag flickeren
interface StableContainerProps {
  children: React.ReactNode
  className?: string
  minHeight?: string
  loading?: boolean
}

export const StableContainer: React.FC<StableContainerProps> = ({
  children,
  className,
  minHeight = "h-64",
  loading = false
}) => {
  return (
    <div
      className={cn(
        "transition-all duration-300 ease-in-out",
        minHeight,
        {
          "opacity-50": loading,
          "opacity-100": !loading
        },
        className
      )}
    >
      {children}
    </div>
  )
}

// Smooth Loading State
interface SmoothLoadingProps {
  isLoading: boolean
  children: React.ReactNode
  fallback?: React.ReactNode
  className?: string
}

export const SmoothLoading: React.FC<SmoothLoadingProps> = ({
  isLoading,
  children,
  fallback,
  className
}) => {
  const [showContent, setShowContent] = useState(!isLoading)
  const [showFallback, setShowFallback] = useState(isLoading)

  useEffect(() => {
    if (isLoading) {
      setShowFallback(true)
      setShowContent(false)
    } else {
      // Delay showing content to prevent flickering
      setTimeout(() => {
        setShowFallback(false)
        setShowContent(true)
      }, 100)
    }
  }, [isLoading])

  return (
    <div className={cn("relative", className)}>
      {showFallback && fallback && (
        <div className="absolute inset-0 z-10">
          {fallback}
        </div>
      )}
      {showContent && (
        <div className={cn(
          "transition-opacity duration-300",
          showContent ? "opacity-100" : "opacity-0"
        )}>
          {children}
        </div>
      )}
    </div>
  )
}

export default SmoothTransition 