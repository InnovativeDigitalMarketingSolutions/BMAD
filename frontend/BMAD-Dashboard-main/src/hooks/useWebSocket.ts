// WebSocket Hook voor Real-time Updates
import { useState, useEffect, useRef, useCallback } from 'react'

interface WebSocketMessage {
  type: 'agents' | 'metrics' | 'logs' | 'alerts'
  data: any
  timestamp: number
}

interface UseWebSocketOptions {
  url?: string
  autoReconnect?: boolean
  reconnectInterval?: number
  maxReconnectAttempts?: number
  fallbackToPolling?: boolean
  pollingInterval?: number
}

interface UseWebSocketReturn {
  isConnected: boolean
  isConnecting: boolean
  lastMessage: WebSocketMessage | null
  sendMessage: (message: any) => void
  reconnect: () => void
  error: string | null
  connectionStatus: 'connected' | 'connecting' | 'disconnected' | 'error'
}

export const useWebSocket = (options: UseWebSocketOptions = {}): UseWebSocketReturn => {
  const {
    url = 'ws://localhost:5001/ws', // Changed to port 5001
    autoReconnect = true,
    reconnectInterval = 3000,
    maxReconnectAttempts = 5,
    fallbackToPolling = true,
    pollingInterval = 3000 // Verlaagd naar 3 seconden voor snellere updates
  } = options

  const [isConnected, setIsConnected] = useState(false)
  const [isConnecting, setIsConnecting] = useState(false)
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'connecting' | 'disconnected' | 'error'>('disconnected')
  const [reconnectAttempts, setReconnectAttempts] = useState(0)
  const [usePolling, setUsePolling] = useState(false)

  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const pollingIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const isMountedRef = useRef(true)

  // Cleanup function
  const cleanup = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
      reconnectTimeoutRef.current = null
    }
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current)
      pollingIntervalRef.current = null
    }
  }, [])

  // Polling fallback - Use correct API endpoint
  const startPolling = useCallback(() => {
    if (!fallbackToPolling || !isMountedRef.current) return

    console.log('Starting polling fallback...')
    setUsePolling(true)
    setConnectionStatus('connecting')

    const poll = async () => {
      if (!isMountedRef.current) return
      
      try {
        const controller = new AbortController()
        const timeoutId = setTimeout(() => controller.abort(), 5000)
        
        console.log('Polling API endpoint: http://localhost:5001/api-proxy/agents')
        const response = await fetch('http://localhost:5001/api-proxy/agents', {
          signal: controller.signal,
          headers: {
            'Content-Type': 'application/json'
          }
        })
        
        clearTimeout(timeoutId)
        
        if (response.ok && isMountedRef.current) {
          const data = await response.json()
          console.log('Polling successful, data received:', data)
          
          // Check if data has the expected structure
          if (data && (data.agents || data.error)) {
            setLastMessage({
              type: 'agents',
              data,
              timestamp: Date.now()
            })
            setConnectionStatus('connected')
            setError(null)
          } else {
            console.warn('Polling failed, invalid data structure:', data)
            setConnectionStatus('disconnected')
            setError('Invalid API response structure')
          }
        } else {
          // If response is not ok, show as disconnected
          console.warn('Polling failed, response not ok:', response.status)
          setConnectionStatus('disconnected')
          setError('API response not ok')
        }
      } catch (err) {
        if (isMountedRef.current) {
          console.warn('Polling fallback error:', err)
          setError('Connection failed, using polling fallback')
          setConnectionStatus('error') // Show as error instead of connected
        }
      }
    }

    // Initial poll
    poll()

    // Set up polling interval
    pollingIntervalRef.current = setInterval(poll, pollingInterval)
  }, [fallbackToPolling, pollingInterval])

  const stopPolling = useCallback(() => {
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current)
      pollingIntervalRef.current = null
    }
    setUsePolling(false)
  }, [])

  // WebSocket connection
  const connect = useCallback(() => {
    if (!isMountedRef.current) return
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return
    }

    setIsConnecting(true)
    setConnectionStatus('connecting')
    setError(null)

    try {
      const ws = new WebSocket(url)
      wsRef.current = ws

      ws.onopen = () => {
        if (!isMountedRef.current) return
        
        setIsConnected(true)
        setIsConnecting(false)
        setConnectionStatus('connected')
        setReconnectAttempts(0)
        setError(null)
        stopPolling()
      }

      ws.onmessage = (event) => {
        if (!isMountedRef.current) return
        
        try {
          const message: WebSocketMessage = JSON.parse(event.data)
          setLastMessage(message)
        } catch (err) {
          console.error('Failed to parse WebSocket message:', err)
        }
      }

      ws.onclose = () => {
        if (!isMountedRef.current) return
        
        setIsConnected(false)
        setIsConnecting(false)
        setConnectionStatus('disconnected')

        if (autoReconnect && reconnectAttempts < maxReconnectAttempts && isMountedRef.current) {
          setReconnectAttempts(prev => prev + 1)
          
          reconnectTimeoutRef.current = setTimeout(() => {
            if (isMountedRef.current) {
              connect()
            }
          }, reconnectInterval)
        } else if (fallbackToPolling && !usePolling && isMountedRef.current) {
          console.log('WebSocket failed, starting polling fallback')
          startPolling()
        }
      }

      ws.onerror = () => {
        if (!isMountedRef.current) return
        
        console.warn('WebSocket error, falling back to polling')
        setError('WebSocket error, using polling fallback')
        setConnectionStatus('error') // Show as error first
        setIsConnecting(false)
        
        // Automatically fall back to polling
        if (fallbackToPolling && !usePolling) {
          console.log('WebSocket error, starting polling fallback')
          startPolling()
        }
      }

    } catch (err) {
      if (!isMountedRef.current) return
      
      console.warn('Failed to create WebSocket, using polling fallback:', err)
      setError('WebSocket not available, using polling fallback')
      setConnectionStatus('error') // Show as error first
      setIsConnecting(false)
      
      // Automatically fall back to polling
      if (fallbackToPolling && !usePolling) {
        console.log('WebSocket creation failed, starting polling fallback')
        startPolling()
      }
    }
  }, [url, autoReconnect, reconnectInterval, maxReconnectAttempts, reconnectAttempts, fallbackToPolling, usePolling, startPolling, stopPolling])

  const disconnect = useCallback(() => {
    cleanup()
    if (isMountedRef.current) {
      setIsConnected(false)
      setIsConnecting(false)
      setConnectionStatus('disconnected')
    }
  }, [cleanup])

  const sendMessage = useCallback((message: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message))
    } else {
      console.warn('WebSocket is not connected, cannot send message')
    }
  }, [])

  const reconnect = useCallback(() => {
    disconnect()
    setReconnectAttempts(0)
    connect()
  }, [disconnect, connect])

  // Auto-connect on mount
  useEffect(() => {
    isMountedRef.current = true
    connect()

    return () => {
      isMountedRef.current = false
      disconnect()
    }
  }, [connect, disconnect])

  return {
    isConnected,
    isConnecting,
    lastMessage,
    sendMessage,
    reconnect,
    error,
    connectionStatus
  }
}

export default useWebSocket 