// SystemMetrics Component - Real-time system health monitoring (Shadcn/ui compatible)
import React, { useState, memo } from 'react'
import { 
  Cpu, 
  HardDrive, 
  TrendingUp,
  Download
} from 'lucide-react'
import { useSystemMetrics } from '@/hooks/useSystemMetrics'
import { PageHeader } from '@/components/ui/PageHeader'
import { ErrorDisplay } from '@/components/ui/ErrorDisplay'
import { PerformanceTest } from '@/components/ui/PerformanceTest'
import { cn } from '@/lib/utils'

// Alert thresholds
const ALERT_THRESHOLDS = {
  cpu: { warning: 70, critical: 90 },
  memory: { warning: 80, critical: 95 }
}

// Get alert status
const getAlertStatus = (value: number, thresholds: { warning: number; critical: number }) => {
  if (value >= thresholds.critical) return 'critical'
  if (value >= thresholds.warning) return 'warning'
  return 'normal'
}

// Get alert color
const getAlertColor = (status: string) => {
  switch (status) {
    case 'critical': return 'text-red-500 bg-red-500/10'
    case 'warning': return 'text-yellow-500 bg-yellow-500/10'
    default: return 'text-green-500 bg-green-500/10'
  }
}

// Get alert icon
const getAlertIcon = (status: string) => {
  switch (status) {
    case 'critical': return '🔴'
    case 'warning': return '🟡'
    default: return '🟢'
  }
}

// Progress Bar Component
const ProgressBar: React.FC<{ value: number; status: string }> = ({ value, status }) => (
  <div className="w-full bg-muted rounded-full h-2 mb-2">
    <div
      className={cn(
        "h-2 rounded-full transition-all duration-300",
        status === 'critical' ? "bg-red-500" :
        status === 'warning' ? "bg-yellow-500" : "bg-green-500"
      )}
      style={{ width: `${Math.min(value, 100)}%` }}
    />
  </div>
)

// Metric Card Component
const MetricCard: React.FC<{
  icon: React.ComponentType<{ className?: string }>
  title: string
  value: string | number
  status: string
  description: string
  badge: string
  badgeColor: string
}> = ({ icon: Icon, title, value, status, description, badge, badgeColor }) => (
  <div className={cn(
    "bg-card rounded-2xl p-6 shadow-lg border",
    "border-border hover:shadow-xl transition-all duration-200"
  )}>
    <div className="flex items-center justify-between mb-4">
      <div className={cn("p-3 rounded-lg", getAlertColor(status))}>
        <Icon className="w-8 h-8" />
      </div>
      <div className="flex items-center space-x-2">
        <span className={cn(
          "px-3 py-1 rounded-full text-xs font-medium",
          badgeColor
        )}>
          {badge}
        </span>
        <span className="text-lg">{getAlertIcon(status)}</span>
      </div>
    </div>
    <h3 className="text-lg font-semibold text-card-foreground mb-2">
      {title}
    </h3>
    <div className="text-3xl font-bold text-card-foreground mb-2">
      {value}
    </div>
    <div className="text-sm text-muted-foreground mb-3">
      {description}
    </div>
    {typeof value === 'number' && <ProgressBar value={value} status={status} />}
  </div>
)

const SystemMetricsComponent: React.FC = memo(() => {
  const { metrics, loading, error, fetchMetrics } = useSystemMetrics()
  const [selectedTimeframe, setSelectedTimeframe] = useState<'1h' | '6h' | '24h'>('1h')
  const [showDetailedMetrics, setShowDetailedMetrics] = useState(false)

  // Loading state
  if (loading) {
    return (
      <div className="min-h-screen bg-background text-foreground">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <PageHeader title="Systeem Metrics" subtitle="Live Monitoring" />
          <div className="text-center py-12">
            <h2 className="text-xl font-semibold text-card-foreground mb-2">
              Laden Systeem Metrics...
            </h2>
          </div>
        </div>
      </div>
    )
  }

  // Error state
  if (error || !metrics) {
    return (
      <div className="min-h-screen bg-background text-foreground">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <PageHeader title="Systeem Metrics" subtitle="Live Monitoring" />
          <ErrorDisplay 
            error={error} 
            onRetry={fetchMetrics}
            variant="card"
            className="mt-6"
          />
        </div>
      </div>
    )
  }

  // Parse agent-based metrics for alerts
  const cpuValue = parseInt(metrics.system_health.cpu_usage) || 0
  const memoryValue = parseInt(metrics.system_health.memory_usage) || 0
  const successRate = metrics.system_health.agent_success_rate || 0
  const responseTime = metrics.system_health.average_response_time || 0

  // Export function
  const handleExport = () => {
    const data = JSON.stringify(metrics, null, 2)
    const blob = new Blob([data], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `systeem-metrics-${new Date().toISOString().split('T')[0]}.json`
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="min-h-screen bg-background text-foreground">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* Header with Export */}
        <PageHeader
          title="Systeem Metrics"
          subtitle="Live Monitoring"
        >
          {/* Timeframe Selector */}
          <div className="flex bg-muted rounded-lg p-1">
            {(['1h', '6h', '24h'] as const).map((timeframe) => (
              <button
                key={timeframe}
                onClick={() => setSelectedTimeframe(timeframe)}
                className={cn(
                  "px-3 py-1 rounded-md text-sm font-medium transition-all duration-200",
                  selectedTimeframe === timeframe
                    ? "bg-background text-foreground shadow-sm"
                    : "text-muted-foreground hover:text-foreground"
                )}
              >
                {timeframe}
              </button>
            ))}
          </div>
          {/* Export Button */}
          <button
            onClick={handleExport}
            className="p-2 rounded-lg bg-secondary hover:bg-secondary/80 transition-colors duration-200"
            title="Export Metrics"
          >
            <Download className="w-5 h-5" />
          </button>
        </PageHeader>

        {/* System Health Overview */}
        <div className="mb-8">
          <div className="bg-card rounded-2xl p-8 shadow-lg border border-border">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-card-foreground">
                BMAD Agent Systeem Gezondheid
              </h2>
              <button
                onClick={() => setShowDetailedMetrics(!showDetailedMetrics)}
                className="px-3 py-1 rounded-lg text-sm font-medium bg-secondary text-secondary-foreground hover:bg-secondary/80 transition-all duration-200"
              >
                {showDetailedMetrics ? 'Details Verbergen' : 'Details Tonen'}
              </button>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              
              {/* Agent CPU Usage Card */}
              <MetricCard
                icon={Cpu}
                title="Agent CPU Gebruik"
                value={`${cpuValue}%`}
                status={getAlertStatus(cpuValue, ALERT_THRESHOLDS.cpu)}
                description="Gemiddeld CPU gebruik van alle agents"
                badge="Agent CPU"
                badgeColor="bg-blue-500 text-white"
              />

              {/* Agent Memory Usage Card */}
              <MetricCard
                icon={HardDrive}
                title="Agent Geheugen"
                value={`${memoryValue}%`}
                status={getAlertStatus(memoryValue, ALERT_THRESHOLDS.memory)}
                description="Gemiddeld geheugen gebruik van alle agents"
                badge="Agent RAM"
                badgeColor="bg-green-500 text-white"
              />

              {/* Agent Success Rate Card */}
              <MetricCard
                icon={TrendingUp}
                title="Agent Success Rate"
                value={`${successRate}%`}
                status={getAlertStatus(successRate, { warning: 70, critical: 50 })}
                description="Percentage succesvolle agent taken"
                badge="Success"
                badgeColor="bg-purple-500 text-white"
              />

            </div>
          </div>
        </div>

        {/* Detailed Metrics */}
        {showDetailedMetrics && (
          <div className="mb-8">
            <div className="bg-card rounded-2xl p-8 shadow-lg border border-border">
              <h2 className="text-xl font-semibold text-card-foreground mb-6">
                Gedetailleerde Metingen
              </h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                
                {/* Agent CPU Usage */}
                <div className="bg-muted rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-medium text-card-foreground">Agent CPU Gebruik</h3>
                    <span className="text-sm text-muted-foreground">{cpuValue}%</span>
                  </div>
                  <ProgressBar value={cpuValue} status={getAlertStatus(cpuValue, ALERT_THRESHOLDS.cpu)} />
                </div>

                {/* Agent Memory Usage */}
                <div className="bg-muted rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-medium text-card-foreground">Agent Geheugen</h3>
                    <span className="text-sm text-muted-foreground">{memoryValue}%</span>
                  </div>
                  <ProgressBar value={memoryValue} status={getAlertStatus(memoryValue, ALERT_THRESHOLDS.memory)} />
                </div>

                {/* Agent Success Rate */}
                <div className="bg-muted rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-medium text-card-foreground">Agent Success Rate</h3>
                    <span className="text-sm text-muted-foreground">{successRate}%</span>
                  </div>
                  <ProgressBar value={successRate} status={getAlertStatus(successRate, { warning: 70, critical: 50 })} />
                </div>

                {/* Agent Response Time */}
                <div className="bg-muted rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-medium text-card-foreground">Gemiddelde Response Time</h3>
                    <span className="text-sm text-muted-foreground">{responseTime}ms</span>
                  </div>
                  <div className="text-2xl font-bold text-blue-500">⚡</div>
                </div>

              </div>
            </div>
          </div>
        )}

        {/* Performance Trends */}
        <div className="mb-8">
          <div className="bg-card rounded-2xl p-8 shadow-lg border border-border">
            <div className="flex items-center space-x-3 mb-6">
              <TrendingUp className="w-6 h-6 text-primary" />
              <h2 className="text-xl font-semibold text-card-foreground">
                Prestatie Trends
              </h2>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              
              {/* CPU Trend */}
              <div className="bg-muted rounded-lg p-4">
                <h3 className="font-medium text-card-foreground mb-3">CPU Trend</h3>
                <div className="flex items-center justify-between">
                  <span className="text-2xl font-bold text-card-foreground">
                    {cpuValue}%
                  </span>
                  <span className="text-sm text-muted-foreground">
                    Gemiddeld over {selectedTimeframe}
                  </span>
                </div>
                <div className="mt-3 h-2 bg-background rounded-full">
                  <div 
                    className="h-2 bg-primary rounded-full transition-all duration-300"
                    style={{ width: `${cpuValue}%` }}
                  />
                </div>
              </div>

              {/* Memory Trend */}
              <div className="bg-muted rounded-lg p-4">
                <h3 className="font-medium text-card-foreground mb-3">Geheugen Trend</h3>
                <div className="flex items-center justify-between">
                  <span className="text-2xl font-bold text-card-foreground">
                    {memoryValue}%
                  </span>
                  <span className="text-sm text-muted-foreground">
                    Gemiddeld over {selectedTimeframe}
                  </span>
                </div>
                <div className="mt-3 h-2 bg-background rounded-full">
                  <div 
                    className="h-2 bg-green-500 rounded-full transition-all duration-300"
                    style={{ width: `${memoryValue}%` }}
                  />
                </div>
              </div>

            </div>
          </div>
        </div>

        {/* Performance Testing Section */}
        <div className="mb-8">
          <PerformanceTest 
            onComplete={() => {
              // Performance results are logged by the component itself
            }}
          />
        </div>

      </div>
    </div>
  )
})

export const SystemMetrics = SystemMetricsComponent
export default SystemMetricsComponent 