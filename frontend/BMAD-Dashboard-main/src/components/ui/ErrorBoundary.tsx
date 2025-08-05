// Enhanced Error Boundary Component
import { Component, ErrorInfo, ReactNode } from 'react'
import { AlertTriangle, RefreshCw, Home } from 'lucide-react'
import { cn } from '@/lib/utils'

interface Props {
  children: ReactNode
  fallback?: ReactNode
}

interface State {
  hasError: boolean
  error: Error | null
  errorInfo: ErrorInfo | null
  retryCount: number
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      retryCount: 0
    }
  }

  static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      error,
      errorInfo: null,
      retryCount: 0
    }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo)
    
    this.setState({
      error,
      errorInfo
    })

    // Log error to console for debugging
    console.group('🚨 Error Boundary Error')
    console.error('Error:', error)
    console.error('Error Info:', errorInfo)
    console.error('Component Stack:', errorInfo.componentStack)
    console.groupEnd()
  }

  handleRetry = () => {
    this.setState(prevState => ({
      hasError: false,
      error: null,
      errorInfo: null,
      retryCount: prevState.retryCount + 1
    }))
  }

  handleGoHome = () => {
    window.location.href = '/dashboard'
  }

  render() {
    if (this.state.hasError) {
      // Custom fallback UI
      if (this.props.fallback) {
        return this.props.fallback
      }

      return (
        <div className={cn(
          "min-h-screen bg-background flex items-center justify-center p-4"
        )}>
          <div className={cn(
            "bg-card rounded-2xl p-8 shadow-lg border border-border",
            "max-w-2xl w-full"
          )}>
            {/* Error Icon */}
            <div className="flex justify-center mb-6">
              <div className={cn(
                "p-4 rounded-full bg-destructive/10"
              )}>
                <AlertTriangle className="w-12 h-12 text-destructive" />
              </div>
            </div>

            {/* Error Message */}
            <div className="text-center mb-6">
              <h1 className="text-2xl font-bold text-card-foreground mb-2">
                Oeps! Er is iets misgegaan
              </h1>
              <p className="text-muted-foreground mb-4">
                Er is een onverwachte fout opgetreden. Probeer de pagina te verversen of ga terug naar het dashboard.
              </p>
              
              {this.state.error && (
                <details className="text-left bg-muted rounded-lg p-4 mb-4">
                  <summary className="cursor-pointer font-medium text-card-foreground mb-2">
                    Technische Details
                  </summary>
                  <div className="text-sm text-muted-foreground space-y-2">
                    <div>
                      <strong>Error:</strong> {this.state.error.message}
                    </div>
                    {this.state.errorInfo && (
                      <div>
                        <strong>Component Stack:</strong>
                        <pre className="mt-2 p-2 bg-background rounded text-xs overflow-x-auto">
                          {this.state.errorInfo.componentStack}
                        </pre>
                      </div>
                    )}
                  </div>
                </details>
              )}
            </div>

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              <button
                onClick={this.handleRetry}
                className={cn(
                  "flex items-center justify-center space-x-2 px-4 py-2",
                  "bg-primary text-primary-foreground rounded-lg",
                  "hover:bg-primary/90 transition-colors duration-200"
                )}
              >
                <RefreshCw className="w-4 h-4" />
                <span>Opnieuw Proberen</span>
              </button>
              
              <button
                onClick={this.handleGoHome}
                className={cn(
                  "flex items-center justify-center space-x-2 px-4 py-2",
                  "bg-secondary text-secondary-foreground rounded-lg",
                  "hover:bg-secondary/80 transition-colors duration-200"
                )}
              >
                <Home className="w-4 h-4" />
                <span>Terug naar Dashboard</span>
              </button>
            </div>

            {/* Retry Count */}
            {this.state.retryCount > 0 && (
              <div className="text-center mt-4">
                <p className="text-sm text-muted-foreground">
                  Poging {this.state.retryCount} van 3
                </p>
              </div>
            )}
          </div>
        </div>
      )
    }

    return this.props.children
  }
} 