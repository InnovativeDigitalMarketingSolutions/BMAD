// Safe Refresh Hook voor Veilige Refresh Functionaliteit
import { useCallback } from 'react'

interface UseSafeRefreshOptions {
  onRefresh?: () => void | Promise<void>
  onReconnect?: () => void
  onError?: (error: Error) => void
}

interface UseSafeRefreshReturn {
  safeRefresh: () => void
  forceRefresh: () => void
  isRefreshing: boolean
}

export const useSafeRefresh = (options: UseSafeRefreshOptions = {}): UseSafeRefreshReturn => {
  const { onRefresh, onReconnect, onError } = options

  const safeRefresh = useCallback(async () => {
    try {
      // Eerst reconnect proberen
      if (onReconnect) {
        onReconnect()
      }
      
      // Dan data refresh
      if (onRefresh) {
        await onRefresh()
      }
    } catch (error) {
      console.error('❌ Safe refresh failed:', error)
      onError?.(error instanceof Error ? error : new Error('Refresh failed'))
    }
  }, [onRefresh, onReconnect, onError])

  const forceRefresh = useCallback(() => {
    try {
      // Force reconnect
      if (onReconnect) {
        onReconnect()
      }
      
      // Force data refresh
      if (onRefresh) {
        onRefresh()
      }
    } catch (error) {
      console.error('❌ Force refresh failed:', error)
      onError?.(error instanceof Error ? error : new Error('Force refresh failed'))
    }
  }, [onRefresh, onReconnect, onError])

  return {
    safeRefresh,
    forceRefresh,
    isRefreshing: false // Dit kan later uitgebreid worden
  }
}

export default useSafeRefresh 