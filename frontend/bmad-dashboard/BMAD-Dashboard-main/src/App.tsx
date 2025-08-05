// BMAD Dashboard v1 - Main App Component
import { Suspense, lazy, useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { ErrorBoundary } from '@/components/ui/ErrorBoundary'
import { FullScreenLoader } from '@/components/ui/LoadingSpinner'
import { MemoryLeakDetector } from '@/components/ui/MemoryLeakDetector'
import Navigation from '@/components/v1/Navigation'
import { useTheme } from '@/hooks/useTheme'
import './index.css'

// Lazy load components for better performance
const BMADDashboard = lazy(() => import('@/components/v1/BMADDashboard').then(module => ({ default: module.BMADDashboard })))
const SystemMetrics = lazy(() => import('@/components/v1/SystemMetrics').then(module => ({ default: module.SystemMetrics })))
const AgentOverview = lazy(() => import('@/components/v1/AgentOverview').then(module => ({ default: module.AgentOverview })))


// Main Content Component with fixed container
const MainContent: React.FC = () => {
  const location = useLocation()
  const [currentPath, setCurrentPath] = useState(location.pathname)

  useEffect(() => {
    setCurrentPath(location.pathname)
  }, [location.pathname])

  return (
    <div className="relative w-full h-full min-h-screen">
      {/* Fixed container for all content to prevent layout shifts */}
      <div className="w-full h-full min-h-screen pb-20">
        <Suspense fallback={<FullScreenLoader />}>
          {/* Conditional rendering within fixed container */}
          {currentPath === '/dashboard' && <BMADDashboard />}
          {currentPath === '/systemmetrics' && <SystemMetrics />}
          {currentPath === '/agentoverzicht' && <AgentOverview />}

        </Suspense>
      </div>
    </div>
  )
}

function App() {
  // Initialize theme to ensure it's loaded on app start
  useTheme()

  return (
    <ErrorBoundary>
      <Router>
        <div className="App relative w-full h-full min-h-screen">
          <Routes>
            {/* Redirect root to dashboard */}
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            
            {/* All routes render the same MainContent component */}
            <Route path="/dashboard" element={<MainContent />} />
            <Route path="/systemmetrics" element={<MainContent />} />
            <Route path="/agentoverzicht" element={<MainContent />} />

            
            {/* Catch all - redirect to dashboard */}
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
          
          {/* Navigation component - always rendered, never unmounts */}
          <Navigation />
          
          {/* Memory Leak Detector - only in development */}
          {process.env.NODE_ENV === 'development' && (
            <MemoryLeakDetector enabled={true} />
          )}
        </div>
      </Router>
    </ErrorBoundary>
  )
}

export default App 