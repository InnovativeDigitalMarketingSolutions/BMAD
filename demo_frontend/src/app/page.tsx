'use client'

import React, { useState, useEffect } from 'react'
import AgentCard from '../components/shared/AgentCard'

// Types
interface Task {
  id: string;
  title: string;
  description: string;
  status: 'pending' | 'in_progress' | 'completed' | 'blocked';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  assignedTo: string;
  createdAt: string;
  startedAt?: string;
  completedAt?: string;
  estimatedHours: number;
  actualHours?: number;
  tags: string[];
}

interface Agent {
  id: string;
  name: string;
  status: 'online' | 'offline' | 'busy';
  activeSessions: number;
  waitTime: number;
  productivity: number;
  lastActivity: string;
  tasks: string[];
  completedTasks: Task[];
  pendingTasks: Task[];
  currentTask?: Task;
}

interface Project {
  id: string;
  name: string;
  status: 'active' | 'completed' | 'paused';
  progress: number;
  tasks: number;
  completedTasks: number;
}

interface Notification {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  message: string;
  timestamp: string;
  read: boolean;
}

// Mock task data
const mockTasks: Task[] = [
  {
    id: 'task-1',
    title: 'Requirements Analysis',
    description: 'Analyze user requirements and create detailed specifications',
    status: 'completed',
    priority: 'high',
    assignedTo: '1',
    createdAt: '2025-07-26T10:00:00Z',
    startedAt: '2025-07-26T10:30:00Z',
    completedAt: '2025-07-26T14:00:00Z',
    estimatedHours: 4,
    actualHours: 3.5,
    tags: ['analysis', 'requirements']
  },
  {
    id: 'task-2',
    title: 'User Story Creation',
    description: 'Create user stories for the BMAD frontend project',
    status: 'in_progress',
    priority: 'high',
    assignedTo: '1',
    createdAt: '2025-07-26T14:30:00Z',
    startedAt: '2025-07-26T15:00:00Z',
    estimatedHours: 6,
    tags: ['user-stories', 'planning']
  },
  {
    id: 'task-3',
    title: 'Backlog Prioritization',
    description: 'Prioritize the product backlog based on business value',
    status: 'pending',
    priority: 'medium',
    assignedTo: '1',
    createdAt: '2025-07-26T16:00:00Z',
    estimatedHours: 2,
    tags: ['backlog', 'prioritization']
  },
  {
    id: 'task-4',
    title: 'System Architecture Design',
    description: 'Design the overall system architecture for the BMAD platform',
    status: 'in_progress',
    priority: 'urgent',
    assignedTo: '2',
    createdAt: '2025-07-26T09:00:00Z',
    startedAt: '2025-07-26T09:30:00Z',
    estimatedHours: 8,
    tags: ['architecture', 'design']
  },
  {
    id: 'task-5',
    title: 'API Specification',
    description: 'Create detailed API specifications for all endpoints',
    status: 'pending',
    priority: 'high',
    assignedTo: '2',
    createdAt: '2025-07-26T16:30:00Z',
    estimatedHours: 5,
    tags: ['api', 'specification']
  },
  {
    id: 'task-6',
    title: 'Component Development',
    description: 'Develop React components for the dashboard',
    status: 'in_progress',
    priority: 'high',
    assignedTo: '3',
    createdAt: '2025-07-26T11:00:00Z',
    startedAt: '2025-07-26T11:30:00Z',
    estimatedHours: 6,
    tags: ['react', 'components']
  },
  {
    id: 'task-7',
    title: 'UI Implementation',
    description: 'Implement the user interface using Tailwind CSS',
    status: 'pending',
    priority: 'medium',
    assignedTo: '3',
    createdAt: '2025-07-26T16:00:00Z',
    estimatedHours: 4,
    tags: ['ui', 'tailwind']
  },
  {
    id: 'task-8',
    title: 'Test Plan Creation',
    description: 'Create comprehensive test plans for all components',
    status: 'pending',
    priority: 'medium',
    assignedTo: '4',
    createdAt: '2025-07-26T15:00:00Z',
    estimatedHours: 3,
    tags: ['testing', 'planning']
  }
]

// Mock data
const initialAgents: Agent[] = [
  {
    id: '1',
    name: 'ProductOwner Agent',
    status: 'online',
    activeSessions: 3,
    waitTime: 0,
    productivity: 95,
    lastActivity: '2 minuten geleden',
    tasks: ['Requirements analysis', 'User story creation', 'Backlog prioritization'],
    completedTasks: [mockTasks[0]],
    pendingTasks: [mockTasks[2]],
    currentTask: mockTasks[1]
  },
  {
    id: '2',
    name: 'Architect Agent',
    status: 'busy',
    activeSessions: 1,
    waitTime: 120,
    productivity: 87,
    lastActivity: '5 minuten geleden',
    tasks: ['System design', 'API specification'],
    completedTasks: [],
    pendingTasks: [mockTasks[4]],
    currentTask: mockTasks[3]
  },
  {
    id: '3',
    name: 'FrontendDeveloper Agent',
    status: 'online',
    activeSessions: 2,
    waitTime: 30,
    productivity: 92,
    lastActivity: '1 minuut geleden',
    tasks: ['Component development', 'UI implementation'],
    completedTasks: [],
    pendingTasks: [mockTasks[6]],
    currentTask: mockTasks[5]
  },
  {
    id: '4',
    name: 'TestEngineer Agent',
    status: 'offline',
    activeSessions: 0,
    waitTime: 0,
    productivity: 0,
    lastActivity: '1 uur geleden',
    tasks: [],
    completedTasks: [],
    pendingTasks: [mockTasks[7]],
    currentTask: undefined
  },
]

const initialProjects: Project[] = [
  { id: '1', name: 'BMAD Frontend', status: 'active', progress: 75, tasks: 12, completedTasks: 9 },
  { id: '2', name: 'API Integration', status: 'active', progress: 45, tasks: 8, completedTasks: 4 },
  { id: '3', name: 'Database Migration', status: 'paused', progress: 30, tasks: 6, completedTasks: 2 },
  { id: '4', name: 'Security Audit', status: 'completed', progress: 100, tasks: 5, completedTasks: 5 },
  { id: '5', name: 'Performance Optimization', status: 'active', progress: 20, tasks: 10, completedTasks: 2 },
]

const initialNotifications: Notification[] = [
  { id: '1', type: 'success', message: 'ProductOwner Agent completed user story generation', timestamp: '2 min geleden', read: false },
  { id: '2', type: 'info', message: 'New project "BMAD Frontend" created', timestamp: '5 min geleden', read: false },
  { id: '3', type: 'warning', message: 'Architect Agent has high wait time (120s)', timestamp: '10 min geleden', read: true },
  { id: '4', type: 'error', message: 'TestEngineer Agent went offline', timestamp: '1 uur geleden', read: true },
]

export default function Home() {
  // State
  const [agents, setAgents] = useState<Agent[]>(initialAgents)
  const [projects, setProjects] = useState<Project[]>(initialProjects)
  const [notifications, setNotifications] = useState<Notification[]>(initialNotifications)
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null)
  const [showNotifications, setShowNotifications] = useState(false)
  const [activeTab, setActiveTab] = useState<'overview' | 'agents' | 'projects' | 'analytics' | 'tasks'>('overview')
  const [selectedTask, setSelectedTask] = useState<string | null>(null)

  // Real-time updates simulation
  useEffect(() => {
    const interval = setInterval(() => {
      setAgents(prevAgents => 
        prevAgents.map(agent => {
          // Simulate task progress
          if (agent.currentTask && (agent.status === 'online' || agent.status === 'busy')) {
            const task = agent.currentTask
            const progress = Math.min(100, (task.actualHours || 0) + Math.random() * 0.5)
            
            // Complete task if progress reaches 100%
            if (progress >= task.estimatedHours) {
              const completedTask = { ...task, status: 'completed' as const, actualHours: task.estimatedHours }
              return {
                ...agent,
                productivity: Math.max(0, Math.min(100, agent.productivity + (Math.random() - 0.5) * 5)),
                waitTime: agent.status === 'busy' ? Math.max(0, agent.waitTime - 10) : agent.waitTime,
                lastActivity: agent.status === 'online' || agent.status === 'busy' ? 'Nu' : agent.lastActivity,
                completedTasks: [...agent.completedTasks, completedTask],
                currentTask: agent.pendingTasks.length > 0 ? agent.pendingTasks[0] : undefined,
                pendingTasks: agent.pendingTasks.slice(1)
              }
            }
            
            return {
              ...agent,
              productivity: Math.max(0, Math.min(100, agent.productivity + (Math.random() - 0.5) * 5)),
              waitTime: agent.status === 'busy' ? Math.max(0, agent.waitTime - 10) : agent.waitTime,
              lastActivity: agent.status === 'online' || agent.status === 'busy' ? 'Nu' : agent.lastActivity,
              currentTask: { ...task, actualHours: progress }
            }
          }
          
          return {
            ...agent,
            productivity: Math.max(0, Math.min(100, agent.productivity + (Math.random() - 0.5) * 5)),
            waitTime: agent.status === 'busy' ? Math.max(0, agent.waitTime - 10) : agent.waitTime,
            lastActivity: agent.status === 'online' ? 'Nu' : agent.lastActivity
          }
        })
      )
    }, 5000)

    return () => clearInterval(interval)
  }, [])

  // Handlers
  const handleAgentClick = (agentId: string) => {
    setSelectedAgent(selectedAgent === agentId ? null : agentId)
  }

  const handleAgentStatusChange = (agentId: string, newStatus: Agent['status']) => {
    setAgents(prevAgents =>
      prevAgents.map(agent =>
        agent.id === agentId
          ? { ...agent, status: newStatus, lastActivity: 'Nu' }
          : agent
      )
    )
  }

  const handleTaskStatusChange = (taskId: string, newStatus: Task['status']) => {
    setAgents(prevAgents =>
      prevAgents.map(agent => {
        // Update current task
        if (agent.currentTask?.id === taskId) {
          return {
            ...agent,
            currentTask: { ...agent.currentTask, status: newStatus }
          }
        }
        
        // Update pending tasks
        const updatedPendingTasks = agent.pendingTasks.map(task =>
          task.id === taskId ? { ...task, status: newStatus } : task
        )
        
        return {
          ...agent,
          pendingTasks: updatedPendingTasks
        }
      })
    )
  }

  const handleNotificationClick = (notificationId: string) => {
    setNotifications(prevNotifications =>
      prevNotifications.map(notification =>
        notification.id === notificationId
          ? { ...notification, read: true }
          : notification
      )
    )
  }

  const handleProjectStatusChange = (projectId: string, newStatus: Project['status']) => {
    setProjects(prevProjects =>
      prevProjects.map(project =>
        project.id === projectId
          ? { ...project, status: newStatus }
          : project
      )
    )
  }

  // Computed values
  const activeAgents = agents.filter(agent => agent.status === 'online').length
  const totalTasks = projects.reduce((sum, project) => sum + project.tasks, 0)
  const completedTasks = projects.reduce((sum, project) => sum + project.completedTasks, 0)
  const unreadNotifications = notifications.filter(n => !n.read).length

  const getPriorityColor = (priority: Task['priority']) => {
    switch (priority) {
      case 'urgent': return 'bg-red-500 text-white'
      case 'high': return 'bg-orange-500 text-white'
      case 'medium': return 'bg-yellow-500 text-black'
      case 'low': return 'bg-green-500 text-white'
      default: return 'bg-gray-500 text-white'
    }
  }

  const getStatusColor = (status: Task['status']) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800'
      case 'in_progress': return 'bg-blue-100 text-blue-800'
      case 'pending': return 'bg-yellow-100 text-yellow-800'
      case 'blocked': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const formatDuration = (hours: number) => {
    if (hours < 1) return `${Math.round(hours * 60)}m`
    const wholeHours = Math.floor(hours)
    const minutes = Math.round((hours - wholeHours) * 60)
    return minutes > 0 ? `${wholeHours}h ${minutes}m` : `${wholeHours}h`
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">BMAD Dashboard</h1>
              <p className="text-gray-600">Generated by BMAD Agents</p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="relative">
                <button
                  onClick={() => setShowNotifications(!showNotifications)}
                  className="relative p-2 text-gray-600 hover:text-gray-900 focus:outline-none"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-5 5v-5z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M9 11h.01M9 8h.01" />
                  </svg>
                  {unreadNotifications > 0 && (
                    <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                      {unreadNotifications}
                    </span>
                  )}
                </button>
                
                {/* Notifications dropdown */}
                {showNotifications && (
                  <div className="absolute right-0 mt-2 w-80 bg-white rounded-md shadow-lg z-50">
                    <div className="py-2">
                      {notifications.map(notification => (
                        <div
                          key={notification.id}
                          onClick={() => handleNotificationClick(notification.id)}
                          className={`px-4 py-2 hover:bg-gray-50 cursor-pointer ${
                            !notification.read ? 'bg-blue-50' : ''
                          }`}
                        >
                          <div className="flex items-start">
                            <div className={`w-2 h-2 rounded-full mt-2 mr-3 ${
                              notification.type === 'success' ? 'bg-green-500' :
                              notification.type === 'warning' ? 'bg-yellow-500' :
                              notification.type === 'error' ? 'bg-red-500' : 'bg-blue-500'
                            }`} />
                            <div className="flex-1">
                              <p className="text-sm text-gray-900">{notification.message}</p>
                              <p className="text-xs text-gray-500">{notification.timestamp}</p>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
              
              <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
                System Online
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-8">
            {[
              { id: 'overview', name: 'Overview' },
              { id: 'agents', name: 'Agents' },
              { id: 'projects', name: 'Projects' },
              { id: 'tasks', name: 'Tasks' },
              { id: 'analytics', name: 'Analytics' }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab.name}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {activeTab === 'overview' && (
            <>
              {/* Stats Overview */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                <div className="bg-white overflow-hidden shadow rounded-lg">
                  <div className="p-5">
                    <div className="flex items-center">
                      <div className="flex-shrink-0">
                        <div className="w-8 h-8 bg-blue-500 rounded-md flex items-center justify-center">
                          <span className="text-white font-bold">A</span>
                        </div>
                      </div>
                      <div className="ml-5 w-0 flex-1">
                        <dl>
                          <dt className="text-sm font-medium text-gray-500 truncate">Active Agents</dt>
                          <dd className="text-lg font-medium text-gray-900">{activeAgents}</dd>
                        </dl>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="bg-white overflow-hidden shadow rounded-lg">
                  <div className="p-5">
                    <div className="flex items-center">
                      <div className="flex-shrink-0">
                        <div className="w-8 h-8 bg-green-500 rounded-md flex items-center justify-center">
                          <span className="text-white font-bold">P</span>
                        </div>
                      </div>
                      <div className="ml-5 w-0 flex-1">
                        <dl>
                          <dt className="text-sm font-medium text-gray-500 truncate">Projects</dt>
                          <dd className="text-lg font-medium text-gray-900">{projects.length}</dd>
                        </dl>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="bg-white overflow-hidden shadow rounded-lg">
                  <div className="p-5">
                    <div className="flex items-center">
                      <div className="flex-shrink-0">
                        <div className="w-8 h-8 bg-yellow-500 rounded-md flex items-center justify-center">
                          <span className="text-white font-bold">T</span>
                        </div>
                      </div>
                      <div className="ml-5 w-0 flex-1">
                        <dl>
                          <dt className="text-sm font-medium text-gray-500 truncate">Tasks</dt>
                          <dd className="text-lg font-medium text-gray-900">{totalTasks}</dd>
                        </dl>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="bg-white overflow-hidden shadow rounded-lg">
                  <div className="p-5">
                    <div className="flex items-center">
                      <div className="flex-shrink-0">
                        <div className="w-8 h-8 bg-purple-500 rounded-md flex items-center justify-center">
                          <span className="text-white font-bold">U</span>
                        </div>
                      </div>
                      <div className="ml-5 w-0 flex-1">
                        <dl>
                          <dt className="text-sm font-medium text-gray-500 truncate">Users</dt>
                          <dd className="text-lg font-medium text-gray-900">8</dd>
                        </dl>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Agent Grid */}
              <div className="bg-white shadow rounded-lg mb-8">
                <div className="px-4 py-5 sm:p-6">
                  <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                    Agent Monitoring
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    {agents.map((agent) => (
                      <div key={agent.id} className="relative">
                        <AgentCard agent={agent} />
                        {selectedAgent === agent.id && (
                          <div className="absolute top-0 left-0 right-0 bg-blue-50 border border-blue-200 rounded-lg p-4 mt-2">
                            <h4 className="font-medium text-blue-900 mb-2">Agent Controls</h4>
                            <div className="space-y-2">
                              <select
                                value={agent.status}
                                onChange={(e) => handleAgentStatusChange(agent.id, e.target.value as Agent['status'])}
                                className="w-full text-sm border border-gray-300 rounded px-2 py-1"
                              >
                                <option value="online">Online</option>
                                <option value="busy">Busy</option>
                                <option value="offline">Offline</option>
                              </select>
                              <div className="text-xs text-gray-600">
                                <p>Last Activity: {agent.lastActivity}</p>
                                <p>Active Tasks: {agent.tasks.length}</p>
                              </div>
                            </div>
                          </div>
                        )}
                        <button
                          onClick={() => handleAgentClick(agent.id)}
                          className="mt-2 w-full text-sm text-blue-600 hover:text-blue-800"
                        >
                          {selectedAgent === agent.id ? 'Hide Controls' : 'Show Controls'}
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </>
          )}

          {activeTab === 'agents' && (
            <div className="bg-white shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                  Agent Management
                </h3>
                <div className="space-y-4">
                  {agents.map(agent => (
                    <div key={agent.id} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="font-medium">{agent.name}</h4>
                          <p className="text-sm text-gray-600">Status: {agent.status}</p>
                          <p className="text-sm text-gray-600">Productivity: {agent.productivity.toFixed(1)}%</p>
                        </div>
                        <div className="flex space-x-2">
                          <select
                            value={agent.status}
                            onChange={(e) => handleAgentStatusChange(agent.id, e.target.value as Agent['status'])}
                            className="text-sm border border-gray-300 rounded px-2 py-1"
                          >
                            <option value="online">Online</option>
                            <option value="busy">Busy</option>
                            <option value="offline">Offline</option>
                          </select>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'projects' && (
            <div className="bg-white shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                  Project Management
                </h3>
                <div className="space-y-4">
                  {projects.map(project => (
                    <div key={project.id} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <h4 className="font-medium">{project.name}</h4>
                          <div className="mt-2">
                            <div className="flex justify-between text-sm text-gray-600 mb-1">
                              <span>Progress</span>
                              <span>{project.progress}%</span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-2">
                              <div
                                className="bg-blue-600 h-2 rounded-full"
                                style={{ width: `${project.progress}%` }}
                              />
                            </div>
                          </div>
                          <p className="text-sm text-gray-600 mt-2">
                            Tasks: {project.completedTasks}/{project.tasks}
                          </p>
                        </div>
                        <div className="ml-4">
                          <select
                            value={project.status}
                            onChange={(e) => handleProjectStatusChange(project.id, e.target.value as Project['status'])}
                            className="text-sm border border-gray-300 rounded px-2 py-1"
                          >
                            <option value="active">Active</option>
                            <option value="paused">Paused</option>
                            <option value="completed">Completed</option>
                          </select>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'tasks' && (
            <div className="space-y-6">
              {/* Task Overview */}
              <div className="bg-white shadow rounded-lg">
                <div className="px-4 py-5 sm:p-6">
                  <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                    Task Management
                  </h3>
                  
                  {/* Task Statistics */}
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                    <div className="bg-blue-50 p-4 rounded-lg">
                      <div className="text-2xl font-bold text-blue-600">
                        {agents.reduce((sum, agent) => sum + agent.completedTasks.length, 0)}
                      </div>
                      <div className="text-sm text-blue-600">Completed</div>
                    </div>
                    <div className="bg-yellow-50 p-4 rounded-lg">
                      <div className="text-2xl font-bold text-yellow-600">
                        {agents.reduce((sum, agent) => sum + (agent.currentTask ? 1 : 0), 0)}
                      </div>
                      <div className="text-sm text-yellow-600">In Progress</div>
                    </div>
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <div className="text-2xl font-bold text-gray-600">
                        {agents.reduce((sum, agent) => sum + agent.pendingTasks.length, 0)}
                      </div>
                      <div className="text-sm text-gray-600">Pending</div>
                    </div>
                    <div className="bg-red-50 p-4 rounded-lg">
                      <div className="text-2xl font-bold text-red-600">
                        {mockTasks.filter(task => task.status === 'blocked').length}
                      </div>
                      <div className="text-sm text-red-600">Blocked</div>
                    </div>
                  </div>

                  {/* Agent Task Details */}
                  <div className="space-y-6">
                    {agents.map(agent => (
                      <div key={agent.id} className="border rounded-lg p-4">
                        <div className="flex items-center justify-between mb-4">
                          <h4 className="text-lg font-medium text-gray-900">{agent.name}</h4>
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                            agent.status === 'online' ? 'bg-green-100 text-green-800' :
                            agent.status === 'busy' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-gray-100 text-gray-800'
                          }`}>
                            {agent.status}
                          </span>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                          {/* Current Task */}
                          <div>
                            <h5 className="font-medium text-gray-700 mb-2">Current Task</h5>
                            {agent.currentTask ? (
                              <div className="bg-blue-50 p-3 rounded-lg">
                                <div className="flex items-center justify-between mb-2">
                                  <h6 className="font-medium text-blue-900">{agent.currentTask.title}</h6>
                                  <span className={`px-2 py-1 rounded text-xs ${getPriorityColor(agent.currentTask.priority)}`}>
                                    {agent.currentTask.priority}
                                  </span>
                                </div>
                                <p className="text-sm text-blue-700 mb-2">{agent.currentTask.description}</p>
                                <div className="flex justify-between text-xs text-blue-600">
                                  <span>Est: {formatDuration(agent.currentTask.estimatedHours)}</span>
                                  <span>Actual: {formatDuration(agent.currentTask.actualHours || 0)}</span>
                                </div>
                                {agent.currentTask.actualHours && (
                                  <div className="mt-2">
                                    <div className="flex justify-between text-xs text-blue-600 mb-1">
                                      <span>Progress</span>
                                      <span>{Math.round((agent.currentTask.actualHours / agent.currentTask.estimatedHours) * 100)}%</span>
                                    </div>
                                    <div className="w-full bg-blue-200 rounded-full h-1">
                                      <div
                                        className="bg-blue-600 h-1 rounded-full"
                                        style={{ width: `${Math.min(100, (agent.currentTask.actualHours / agent.currentTask.estimatedHours) * 100)}%` }}
                                      />
                                    </div>
                                  </div>
                                )}
                              </div>
                            ) : (
                              <div className="bg-gray-50 p-3 rounded-lg text-center">
                                <p className="text-sm text-gray-500">No current task</p>
                              </div>
                            )}
                          </div>

                          {/* Pending Tasks */}
                          <div>
                            <h5 className="font-medium text-gray-700 mb-2">Pending Tasks</h5>
                            <div className="space-y-2">
                              {agent.pendingTasks.length > 0 ? (
                                agent.pendingTasks.map(task => (
                                  <div key={task.id} className="bg-yellow-50 p-2 rounded">
                                    <div className="flex items-center justify-between mb-1">
                                      <h6 className="text-sm font-medium text-yellow-900">{task.title}</h6>
                                      <span className={`px-1 py-0.5 rounded text-xs ${getPriorityColor(task.priority)}`}>
                                        {task.priority}
                                      </span>
                                    </div>
                                    <p className="text-xs text-yellow-700 truncate">{task.description}</p>
                                    <div className="text-xs text-yellow-600 mt-1">
                                      Est: {formatDuration(task.estimatedHours)}
                                    </div>
                                  </div>
                                ))
                              ) : (
                                <div className="bg-gray-50 p-2 rounded text-center">
                                  <p className="text-xs text-gray-500">No pending tasks</p>
                                </div>
                              )}
                            </div>
                          </div>

                          {/* Completed Tasks */}
                          <div>
                            <h5 className="font-medium text-gray-700 mb-2">Completed Tasks</h5>
                            <div className="space-y-2">
                              {agent.completedTasks.length > 0 ? (
                                agent.completedTasks.map(task => (
                                  <div key={task.id} className="bg-green-50 p-2 rounded">
                                    <div className="flex items-center justify-between mb-1">
                                      <h6 className="text-sm font-medium text-green-900">{task.title}</h6>
                                      <span className="text-xs text-green-600">✓</span>
                                    </div>
                                    <p className="text-xs text-green-700 truncate">{task.description}</p>
                                    <div className="text-xs text-green-600 mt-1">
                                      {formatDuration(task.actualHours || task.estimatedHours)}
                                    </div>
                                  </div>
                                ))
                              ) : (
                                <div className="bg-gray-50 p-2 rounded text-center">
                                  <p className="text-xs text-gray-500">No completed tasks</p>
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'analytics' && (
            <div className="bg-white shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                  Analytics Dashboard
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h4 className="font-medium mb-2">Agent Performance</h4>
                    <div className="space-y-2">
                      {agents.map(agent => (
                        <div key={agent.id} className="flex justify-between items-center">
                          <span className="text-sm">{agent.name}</span>
                          <div className="flex items-center">
                            <div className="w-20 bg-gray-200 rounded-full h-2 mr-2">
                              <div
                                className="bg-green-500 h-2 rounded-full"
                                style={{ width: `${agent.productivity}%` }}
                              />
                            </div>
                            <span className="text-sm font-medium">{agent.productivity.toFixed(0)}%</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                  <div>
                    <h4 className="font-medium mb-2">Project Progress</h4>
                    <div className="space-y-2">
                      {projects.map(project => (
                        <div key={project.id} className="flex justify-between items-center">
                          <span className="text-sm">{project.name}</span>
                          <span className="text-sm font-medium">{project.progress}%</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Demo Info */}
          <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
            <h3 className="text-lg font-medium text-blue-900 mb-2">
              🎉 Interactive Demo Successfully Generated!
            </h3>
            <p className="text-blue-700 mb-4">
              This interactive frontend was completely generated by BMAD agents working together:
            </p>
            <ul className="text-blue-700 space-y-1">
              <li>• <strong>ProductOwner:</strong> Generated requirements and user stories</li>
              <li>• <strong>Architect:</strong> Designed component structure and architecture</li>
              <li>• <strong>FrontendDeveloper:</strong> Wrote React/TypeScript component code</li>
              <li>• <strong>TestEngineer:</strong> Generated Jest test code</li>
              <li>• <strong>DocumentationAgent:</strong> Created comprehensive documentation</li>
            </ul>
            <div className="mt-4 p-4 bg-white rounded border">
              <h4 className="font-medium text-gray-900 mb-2">Interactive Features:</h4>
              <ul className="text-sm text-gray-700 space-y-1">
                <li>• <strong>Real-time updates:</strong> Agent productivity and wait times update every 5 seconds</li>
                <li>• <strong>Agent controls:</strong> Click on agent cards to change their status</li>
                <li>• <strong>Project management:</strong> View and modify project status and progress</li>
                <li>• <strong>Task management:</strong> Track current, pending, and completed tasks for each agent</li>
                <li>• <strong>Notifications:</strong> Click the bell icon to view system notifications</li>
                <li>• <strong>Tab navigation:</strong> Switch between Overview, Agents, Projects, Tasks, and Analytics</li>
              </ul>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
} 