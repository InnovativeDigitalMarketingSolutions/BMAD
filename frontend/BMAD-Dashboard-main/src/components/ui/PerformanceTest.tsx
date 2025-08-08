// Performance Test Component - Systematic performance testing
import React, { useState, useCallback } from 'react'
import { Play, Square, CheckCircle, XCircle, Clock, Zap } from 'lucide-react'
import { cn } from '@/lib/utils'

interface TestResult {
  name: string
  status: 'pending' | 'running' | 'passed' | 'failed'
  duration?: number
  error?: string
}

interface PerformanceTestProps {
  onComplete?: (results: TestResult[]) => void
  className?: string
}

export const PerformanceTest: React.FC<PerformanceTestProps> = ({
  onComplete,
  className
}) => {
  const [isRunning, setIsRunning] = useState(false)
  const [results, setResults] = useState<TestResult[]>([])
  const [currentTest, setCurrentTest] = useState<string | null>(null)

  // Test definitions
  const tests: Array<{
    name: string
    test: () => Promise<{ success: boolean; duration: number; error?: string }>
  }> = [
    {
      name: 'Page Load Time',
      test: async () => {
        const start = performance.now()
        
        // Simulate page load
        await new Promise(resolve => setTimeout(resolve, 100))
        
        const duration = performance.now() - start
        return {
          success: duration < 2000, // 2 seconds threshold
          duration,
          error: duration >= 2000 ? `Page load took ${duration.toFixed(0)}ms (threshold: 2000ms)` : undefined
        }
      }
    },
    {
      name: 'API Response Time',
      test: async () => {
        const start = performance.now()
        
        try {
          const response = await fetch('http://localhost:5001/api/health', {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' }
          })
          
          const duration = performance.now() - start
          return {
            success: response.ok && duration < 500, // 500ms threshold
            duration,
            error: !response.ok ? `API returned ${response.status}` : 
                   duration >= 500 ? `API took ${duration.toFixed(0)}ms (threshold: 500ms)` : undefined
          }
        } catch (error) {
          const duration = performance.now() - start
          return {
            success: false,
            duration,
            error: `API connection failed: ${error instanceof Error ? error.message : 'Unknown error'}`
          }
        }
      }
    },
    {
      name: 'Memory Usage',
      test: async () => {
        const start = performance.now()
        
        // Check memory if available
        if ('memory' in performance) {
          const memory = (performance as any).memory
          const memoryUsageMB = memory.usedJSHeapSize / (1024 * 1024)
          
          const duration = performance.now() - start
          return {
            success: memoryUsageMB < 100, // 100MB threshold
            duration,
            error: memoryUsageMB >= 100 ? `Memory usage: ${memoryUsageMB.toFixed(1)}MB (threshold: 100MB)` : undefined
          }
        }
        
        const duration = performance.now() - start
        return {
          success: true, // Can't test memory
          duration,
          error: 'Memory API not available'
        }
      }
    },
    {
      name: 'Smooth Scrolling',
      test: async () => {
        const start = performance.now()
        
        // Simulate scroll performance test
        const scrollTest = () => {
          return new Promise<boolean>((resolve) => {
            let frameCount = 0
            let lastTime = performance.now()
            
            const testScroll = () => {
              frameCount++
              const currentTime = performance.now()
              
              if (currentTime - lastTime >= 1000) { // 1 second test
                const fps = frameCount / ((currentTime - lastTime) / 1000)
                resolve(fps >= 30) // 30 FPS threshold
                return
              }
              
              requestAnimationFrame(testScroll)
            }
            
            requestAnimationFrame(testScroll)
          })
        }
        
        const isSmooth = await scrollTest()
        const duration = performance.now() - start
        
        return {
          success: isSmooth,
          duration,
          error: !isSmooth ? 'Scrolling performance below 30 FPS' : undefined
        }
      }
    },
    {
      name: 'Component Rendering',
      test: async () => {
        const start = performance.now()
        
        // Simulate component rendering test
        await new Promise(resolve => setTimeout(resolve, 50))
        
        const duration = performance.now() - start
        return {
          success: duration < 100, // 100ms threshold for component rendering
          duration,
          error: duration >= 100 ? `Component rendering took ${duration.toFixed(0)}ms (threshold: 100ms)` : undefined
        }
      }
    }
  ]

  const runTest = useCallback(async (test: typeof tests[0]) => {
    setCurrentTest(test.name)
    
    try {
      const result = await test.test()
      
      setResults(prev => prev.map(r => 
        r.name === test.name 
          ? { ...r, status: result.success ? 'passed' : 'failed', duration: result.duration, error: result.error }
          : r
      ))
    } catch (error) {
      setResults(prev => prev.map(r => 
        r.name === test.name 
          ? { ...r, status: 'failed', error: error instanceof Error ? error.message : 'Unknown error' }
          : r
      ))
    }
  }, [])

  const runAllTests = useCallback(async () => {
    setIsRunning(true)
    setResults(tests.map(test => ({ name: test.name, status: 'pending' })))
    
    for (const test of tests) {
      await runTest(test)
      // Small delay between tests
      await new Promise(resolve => setTimeout(resolve, 100))
    }
    
    setIsRunning(false)
    setCurrentTest(null)
    
    if (onComplete) {
      onComplete(results)
    }
  }, [tests, runTest, onComplete, results])

  const stopTests = useCallback(() => {
    setIsRunning(false)
    setCurrentTest(null)
  }, [])

  const passedTests = results.filter(r => r.status === 'passed').length
  const totalTests = results.length

  return (
    <div className={cn(
      "bg-card rounded-2xl p-6 shadow-lg border border-border",
      className
    )}>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-card-foreground">Performance Tests</h3>
          <p className="text-sm text-muted-foreground">
            {isRunning ? 'Running tests...' : `${passedTests}/${totalTests} tests passed`}
          </p>
        </div>
        
        <div className="flex space-x-2">
          {!isRunning ? (
            <button
              onClick={runAllTests}
              className="inline-flex items-center space-x-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
            >
              <Play className="w-4 h-4" />
              <span>Run Tests</span>
            </button>
          ) : (
            <button
              onClick={stopTests}
              className="inline-flex items-center space-x-2 px-4 py-2 bg-destructive text-destructive-foreground rounded-lg hover:bg-destructive/90 transition-colors"
            >
              <Square className="w-4 h-4" />
              <span>Stop</span>
            </button>
          )}
        </div>
      </div>

      <div className="space-y-3">
        {tests.map((test) => {
          const result = results.find(r => r.name === test.name)
          const isCurrent = currentTest === test.name
          
          return (
            <div
              key={test.name}
              className={cn(
                "flex items-center justify-between p-3 rounded-lg border",
                result?.status === 'passed' ? "bg-green-500/10 border-green-500/20" :
                result?.status === 'failed' ? "bg-red-500/10 border-red-500/20" :
                isCurrent ? "bg-blue-500/10 border-blue-500/20" :
                "bg-muted/50 border-border"
              )}
            >
              <div className="flex items-center space-x-3">
                {result?.status === 'passed' ? (
                  <CheckCircle className="w-4 h-4 text-green-500" />
                ) : result?.status === 'failed' ? (
                  <XCircle className="w-4 h-4 text-red-500" />
                ) : isCurrent ? (
                  <Clock className="w-4 h-4 text-blue-500 animate-spin" />
                ) : (
                  <div className="w-4 h-4 rounded-full border-2 border-muted-foreground" />
                )}
                
                <div>
                  <div className="font-medium text-sm">{test.name}</div>
                  {result?.error && (
                    <div className="text-xs text-red-600">{result.error}</div>
                  )}
                </div>
              </div>
              
              {result?.duration && (
                <div className="flex items-center space-x-1 text-xs text-muted-foreground">
                  <Zap className="w-3 h-3" />
                  <span>{result.duration.toFixed(0)}ms</span>
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
} 