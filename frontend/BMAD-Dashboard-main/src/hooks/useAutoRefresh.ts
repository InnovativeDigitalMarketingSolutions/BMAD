// Auto-refresh Hook voor Automatische Data Updates
import { useState, useEffect, useRef, useCallback } from 'react'

interface UseAutoRefreshOptions {
  enabled?: boolean
  interval?: number
  maxRetries?: number
  retryDelay?: number
  onRefresh?: () => void | Promise<void>
  onError?: (error: Error) => void
}

interface UseAutoRefreshReturn {
  isRefreshing: boolean
  lastRefresh: Date | null
  nextRefresh: Date | null
  refreshCount: number
  error: string | null
  enableAutoRefresh: () => void
  disableAutoRefresh: () => void
  triggerRefresh: () => void
  updateInterval: (interval: number) => void
}

export const useAutoRefresh = (options: UseAutoRefreshOptions = {}): UseAutoRefreshReturn => {
  const {
    enabled = false,
    interval = 30000, // 30 seconds default
    maxRetries = 3,
    retryDelay = 5000,
    onRefresh,
    onError
  } = options

  const [isRefreshing, setIsRefreshing] = useState(false)
  const [lastRefresh, setLastRefresh] = useState<Date | null>(null)
  const [nextRefresh, setNextRefresh] = useState<Date | null>(null)
  const [refreshCount, setRefreshCount] = useState(0)
  const [error, setError] = useState<string | null>(null)
  const [isEnabled, setIsEnabled] = useState(enabled)
  const [currentInterval, setCurrentInterval] = useState(interval)

  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const retryCountRef = useRef(0)

  const calculateNextRefresh = useCallback(() => {
    const next = new Date()
    next.setMilliseconds(next.getMilliseconds() + currentInterval)
    return next
  }, [currentInterval])

  const triggerRefresh = useCallback(async () => {
    if (!onRefresh) return

    setIsRefreshing(true)
    setError(null)

    try {
      await onRefresh()
      setLastRefresh(new Date())
      setNextRefresh(calculateNextRefresh())
      setRefreshCount(prev => prev + 1)
      retryCountRef.current = 0
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Refresh failed'
      setError(errorMessage)
      onError?.(err instanceof Error ? err : new Error(errorMessage))
      
      // Retry logic
      if (retryCountRef.current < maxRetries) {
        retryCountRef.current++
        setTimeout(() => {
          triggerRefresh()
        }, retryDelay)
      }
    } finally {
      setIsRefreshing(false)
    }
  }, [onRefresh, calculateNextRefresh, maxRetries, retryDelay, onError])

  const startAutoRefresh = useCallback(() => {
    if (!isEnabled || !onRefresh) return

    // Clear existing interval
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
    }

    // Set up new interval with wrapper function
    intervalRef.current = setInterval(() => {
      triggerRefresh()
    }, currentInterval)

    // Trigger initial refresh
    triggerRefresh()
  }, [isEnabled, onRefresh, currentInterval, triggerRefresh])

  const stopAutoRefresh = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
    }
  }, [])

  const enableAutoRefresh = useCallback(() => {
    setIsEnabled(true)
  }, [])

  const disableAutoRefresh = useCallback(() => {
    setIsEnabled(false)
    stopAutoRefresh()
  }, [stopAutoRefresh])

  const updateInterval = useCallback((newInterval: number) => {
    setCurrentInterval(newInterval)
  }, [])

  // Effect to start/stop auto-refresh when enabled state changes
  useEffect(() => {
    if (isEnabled && onRefresh) {
      startAutoRefresh()
    } else {
      stopAutoRefresh()
    }

    return () => {
      stopAutoRefresh()
    }
  }, [isEnabled, onRefresh, startAutoRefresh, stopAutoRefresh])

  // Effect to restart when interval changes
  useEffect(() => {
    if (isEnabled && onRefresh) {
      stopAutoRefresh()
      startAutoRefresh()
    }
  }, [currentInterval, isEnabled, onRefresh, startAutoRefresh, stopAutoRefresh])

  return {
    isRefreshing,
    lastRefresh,
    nextRefresh,
    refreshCount,
    error,
    enableAutoRefresh,
    disableAutoRefresh,
    triggerRefresh,
    updateInterval
  }
}

export default useAutoRefresh 