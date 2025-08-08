// BMAD v1 Types - Geen dummy data, alleen echte API types

export interface BMADAgent {
  id: string
  name: string
  status: 'active' | 'idle' | 'error' | 'stopped' | 'busy'
  type: 'development' | 'testing' | 'planning' | 'management' | 'operations' | 'security' | 'design' | 'data' | 'ai' | 'database' | 'network' | 'cloud' | 'qa' | 'performance' | 'integration' | 'monitoring' | 'automation'
  performance: number // 0-100
  last_activity: string
  task?: string // Current task (from server)
  progress?: number // Current progress (from server)
  tasks?: AgentTask[] // Optional array of tasks
  metrics?: {
    cpu_usage?: number
    memory_usage?: number
    response_time?: number
  }
}

export interface AgentTask {
  id: string
  name: string
  status: 'running' | 'completed' | 'failed' | 'pending'
  progress: number // 0-100
  start_time?: string
  end_time?: string
}

export interface BMADMetrics {
  system_health: {
    status: string
    uptime: string
    memory_usage: string
    cpu_usage: string
    disk_usage: string
    network_sent_mb: string
    network_recv_mb: string
    agent_success_rate?: number
    average_response_time?: number
    system_health_score?: number
  }
  agents: {
    total: number
    active: number
    idle: number
    busy?: number
  }
  workflows: {
    total: number
    running: number
    pending: number
    completed: number
  }
}

 