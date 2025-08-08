// Stable Loading Hook voor Consistente UI States
import { useState, useEffect, useRef } from 'react'

interface UseStableLoadingOptions {
  minLoadingTime?: number
  debounceTime?: number
  stableThreshold?: number
}

interface UseStableLoadingReturn {
  isLoading: boolean
  isStable: boolean
  setLoading: (loading: boolean) => void
}

export const useStableLoading = (options: UseStableLoadingOptions = {}): UseStableLoadingReturn => {
  const {
    minLoadingTime = 500, // Minimum tijd dat loading state wordt getoond
    debounceTime = 100,   // Debounce tijd voor snelle updates
    stableThreshold = 1000 // Tijd voordat state als "stabiel" wordt beschouwd
  } = options

  const [isLoading, setIsLoading] = useState(false)
  const [isStable, setIsStable] = useState(true)
  const loadingStartTime = useRef<number | null>(null)
  const debounceTimeout = useRef<ReturnType<typeof setTimeout> | null>(null)
  const stableTimeout = useRef<ReturnType<typeof setTimeout> | null>(null)

  const setLoading = (loading: boolean) => {
    // Clear existing timeouts
    if (debounceTimeout.current) {
      clearTimeout(debounceTimeout.current)
    }
    if (stableTimeout.current) {
      clearTimeout(stableTimeout.current)
    }

    if (loading) {
      // Start loading state
      if (!isLoading) {
        loadingStartTime.current = Date.now()
        setIsLoading(true)
        setIsStable(false)
      }
    } else {
      // Debounce loading end to prevent flickering
      debounceTimeout.current = setTimeout(() => {
        const elapsed = loadingStartTime.current ? Date.now() - loadingStartTime.current : 0
        
        if (elapsed >= minLoadingTime) {
          setIsLoading(false)
          
          // Set stable after threshold
          stableTimeout.current = setTimeout(() => {
            setIsStable(true)
          }, stableThreshold)
        } else {
          // Wait for minimum loading time
          setTimeout(() => {
            setIsLoading(false)
            stableTimeout.current = setTimeout(() => {
              setIsStable(true)
            }, stableThreshold)
          }, minLoadingTime - elapsed)
        }
      }, debounceTime)
    }
  }

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (debounceTimeout.current) {
        clearTimeout(debounceTimeout.current)
      }
      if (stableTimeout.current) {
        clearTimeout(stableTimeout.current)
      }
    }
  }, [])

  return {
    isLoading,
    isStable,
    setLoading
  }
}

export default useStableLoading 