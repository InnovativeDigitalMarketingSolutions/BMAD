// Memory Leak Detector Component
import React, { useEffect, useRef, useState } from 'react'
import { AlertTriangle, TrendingDown } from 'lucide-react'
import { cn } from '@/lib/utils'

interface MemorySnapshot {
  timestamp: number
  usedJSHeapSize: number
  totalJSHeapSize: number
  jsHeapSizeLimit: number
}

interface MemoryLeakDetectorProps {
  enabled?: boolean
  interval?: number // milliseconds
  threshold?: number // MB increase threshold
  className?: string
}

export const MemoryLeakDetector: React.FC<MemoryLeakDetectorProps> = ({
  enabled = true,
  interval = 10000, // 10 seconds
  threshold = 50, // 50MB increase threshold
  className
}) => {
  const [, setMemorySnapshots] = useState<MemorySnapshot[]>([])
  const [isLeakDetected, setIsLeakDetected] = useState(false)
  const [currentMemory, setCurrentMemory] = useState<number | null>(null)
  const intervalRef = useRef<NodeJS.Timeout | null>(null)

  // Get memory info if available
  const getMemoryInfo = (): MemorySnapshot | null => {
    if ('memory' in performance) {
      const memory = (performance as any).memory
      return {
        timestamp: Date.now(),
        usedJSHeapSize: memory.usedJSHeapSize,
        totalJSHeapSize: memory.totalJSHeapSize,
        jsHeapSizeLimit: memory.jsHeapSizeLimit
      }
    }
    return null
  }

  // Check for memory leaks
  const checkForLeaks = (snapshots: MemorySnapshot[]) => {
    if (snapshots.length < 3) return false // Need at least 3 snapshots

    const recentSnapshots = snapshots.slice(-3)
    const memoryIncrease = recentSnapshots[recentSnapshots.length - 1].usedJSHeapSize - recentSnapshots[0].usedJSHeapSize
    const memoryIncreaseMB = memoryIncrease / (1024 * 1024)

    return memoryIncreaseMB > threshold
  }

  useEffect(() => {
    if (!enabled) return

    const takeSnapshot = () => {
      const memoryInfo = getMemoryInfo()
      if (memoryInfo) {
        setCurrentMemory(memoryInfo.usedJSHeapSize / (1024 * 1024))
        
        setMemorySnapshots(prev => {
          const newSnapshots = [...prev, memoryInfo]
          // Keep only last 10 snapshots
          const trimmedSnapshots = newSnapshots.slice(-10)
          
          // Check for leaks
          const leakDetected = checkForLeaks(trimmedSnapshots)
          setIsLeakDetected(leakDetected)
          
          return trimmedSnapshots
        })
      }
    }

    // Take initial snapshot
    takeSnapshot()

    // Set up interval
    intervalRef.current = setInterval(takeSnapshot, interval)

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }
  }, [enabled, interval, threshold])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }
  }, [])

  if (!enabled || !currentMemory) return null

  return (
    <div className={cn(
      "fixed bottom-4 right-4 z-50 p-3 rounded-lg border shadow-lg",
      isLeakDetected 
        ? "bg-red-500/10 border-red-500/20 text-red-700" 
        : "bg-green-500/10 border-green-500/20 text-green-700",
      className
    )}>
      <div className="flex items-center space-x-2">
        {isLeakDetected ? (
          <AlertTriangle className="w-4 h-4" />
        ) : (
          <TrendingDown className="w-4 h-4" />
        )}
        <div className="text-xs">
          <div className="font-medium">
            {isLeakDetected ? 'Memory Leak Detected' : 'Memory OK'}
          </div>
          <div className="text-xs opacity-75">
            {currentMemory.toFixed(1)}MB
          </div>
        </div>
      </div>
    </div>
  )
}

// Hook for memory monitoring
export const useMemoryMonitor = () => {
  const [memoryUsage, setMemoryUsage] = useState<number | null>(null)
  const [isLeaking, setIsLeaking] = useState(false)

  useEffect(() => {
    const checkMemory = () => {
      if ('memory' in performance) {
        const memory = (performance as any).memory
        const usageMB = memory.usedJSHeapSize / (1024 * 1024)
        setMemoryUsage(usageMB)
        
        // Simple leak detection: if usage is very high
        if (usageMB > 200) { // 200MB threshold
          setIsLeaking(true)
        } else {
          setIsLeaking(false)
        }
      }
    }

    checkMemory()
    const interval = setInterval(checkMemory, 5000) // Check every 5 seconds

    return () => clearInterval(interval)
  }, [])

  return { memoryUsage, isLeaking }
} 