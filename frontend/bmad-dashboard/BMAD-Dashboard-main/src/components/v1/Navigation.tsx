// Navigation Component - Easy switching between component pages
import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Cpu, Monitor, Users } from 'lucide-react'
import { cn } from '@/lib/utils'

export const Navigation: React.FC = () => {
  const location = useLocation()

  const navItems = [
    {
      path: '/dashboard',
      label: 'Dashboard',
      icon: Monitor,
      description: 'Complete overview'
    },
    {
      path: '/systemmetrics',
      label: 'System Metrics',
      icon: Cpu,
      description: 'System health monitoring'
    },
    {
      path: '/agentoverzicht',
      label: 'Agent Management',
      icon: Users,
      description: 'Comprehensive agent monitoring & control'
    }
  ]

  return (
    <div className="fixed bottom-4 left-1/2 transform -translate-x-1/2 z-50">
      <div className={cn(
        "bg-card rounded-full shadow-lg border border-border",
        "px-4 py-3", // Iets meer padding voor betere spacing
        "w-[600px] h-16", // Smaller voor 3 buttons in plaats van 4
        "transition-none" // Geen transition op container
      )}>
        <div className="grid grid-cols-3 gap-3 h-full items-center">
          {navItems.map((item) => {
            const Icon = item.icon
            const isActive = location.pathname === item.path
            
            return (
              <Link
                key={item.path}
                to={item.path}
                className={cn(
                  // Consistente structuur voor alle buttons
                  "flex items-center justify-center gap-2 px-3 py-2.5 rounded-full",
                  "h-10", // Vaste hoogte voor alle buttons
                  "border border-transparent", // Consistente border
                  "font-medium text-sm", // Vaste font-weight en size
                  "outline-none", // Geen focus ring
                  "transition-all duration-200", // Smooth transitions
                  "min-w-0", // Voorkom overflow
                  "flex-shrink-0", // Voorkom krimpen
                  // Active state met consistente styling
                  isActive
                    ? "bg-primary text-primary-foreground shadow-md"
                    : "text-muted-foreground hover:bg-muted hover:text-foreground"
                )}
                title={item.description}
              >
                <Icon className="w-4 h-4 flex-shrink-0" />
                <span className="text-sm font-medium hidden sm:inline whitespace-nowrap truncate">
                  {item.label}
                </span>
              </Link>
            )
          })}
        </div>
      </div>
    </div>
  )
}

export default Navigation 