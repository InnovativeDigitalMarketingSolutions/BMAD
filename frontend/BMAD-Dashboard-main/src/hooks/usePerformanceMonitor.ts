// Performance Monitoring Hook
import { useEffect, useRef, useCallback } from 'react'

interface PerformanceMetrics {
  pageLoadTime: number
  apiResponseTimes: number[]
  memoryUsage: number | null
  renderCount: number
}

interface PerformanceThresholds {
  pageLoadTime: number // milliseconds
  apiResponseTime: number // milliseconds
  memoryUsage: number // MB
}

const DEFAULT_THRESHOLDS: PerformanceThresholds = {
  pageLoadTime: 2000, // 2 seconds
  apiResponseTime: 500, // 500ms
  memoryUsage: 100 // 100MB
}

export const usePerformanceMonitor = (
  componentName: string,
  thresholds: Partial<PerformanceThresholds> = {}
) => {
  const metrics = useRef<PerformanceMetrics>({
    pageLoadTime: 0,
    apiResponseTimes: [],
    memoryUsage: null,
    renderCount: 0
  })
  
  const startTime = useRef<number>(Date.now())
  const finalThresholds = { ...DEFAULT_THRESHOLDS, ...thresholds }

  // Track page load time
  useEffect(() => {
    const loadTime = Date.now() - startTime.current
    metrics.current.pageLoadTime = loadTime
    
    if (loadTime > finalThresholds.pageLoadTime) {
      console.warn(`⚠️ Performance Warning: ${componentName} took ${loadTime}ms to load (threshold: ${finalThresholds.pageLoadTime}ms)`)
    } else {
      console.log(`✅ Performance OK: ${componentName} loaded in ${loadTime}ms`)
    }
  }, [componentName, finalThresholds.pageLoadTime])

  // Track memory usage
  useEffect(() => {
    if ('memory' in performance) {
      const memory = (performance as any).memory
      const memoryUsageMB = memory.usedJSHeapSize / (1024 * 1024)
      metrics.current.memoryUsage = memoryUsageMB
      
      if (memoryUsageMB > finalThresholds.memoryUsage) {
        console.warn(`⚠️ Memory Warning: ${componentName} using ${memoryUsageMB.toFixed(2)}MB (threshold: ${finalThresholds.memoryUsage}MB)`)
      }
    }
  }, [componentName, finalThresholds.memoryUsage])

  // Track render count
  useEffect(() => {
    metrics.current.renderCount++
  })

  // API response time tracker
  const trackApiResponse = useCallback((apiName: string, responseTime: number) => {
    metrics.current.apiResponseTimes.push(responseTime)
    
    if (responseTime > finalThresholds.apiResponseTime) {
      console.warn(`⚠️ API Performance Warning: ${apiName} took ${responseTime}ms (threshold: ${finalThresholds.apiResponseTime}ms)`)
    } else {
      console.log(`✅ API Performance OK: ${apiName} responded in ${responseTime}ms`)
    }
  }, [finalThresholds.apiResponseTime])

  // Get performance report
  const getPerformanceReport = useCallback(() => {
    const avgApiTime = metrics.current.apiResponseTimes.length > 0 
      ? metrics.current.apiResponseTimes.reduce((a, b) => a + b, 0) / metrics.current.apiResponseTimes.length 
      : 0

    return {
      component: componentName,
      pageLoadTime: metrics.current.pageLoadTime,
      averageApiResponseTime: avgApiTime,
      memoryUsage: metrics.current.memoryUsage,
      renderCount: metrics.current.renderCount,
      isHealthy: {
        pageLoad: metrics.current.pageLoadTime <= finalThresholds.pageLoadTime,
        apiResponse: avgApiTime <= finalThresholds.apiResponseTime,
        memory: metrics.current.memoryUsage === null || metrics.current.memoryUsage <= finalThresholds.memoryUsage
      }
    }
  }, [componentName, finalThresholds])

  return {
    trackApiResponse,
    getPerformanceReport,
    metrics: metrics.current
  }
} 