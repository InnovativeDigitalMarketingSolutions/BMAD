// Theme Toggle Component - Apple-inspired design (Shadcn/ui compatible)
import React from 'react'
import { Moon, Sun } from 'lucide-react'
import { useTheme } from '@/hooks/useTheme'
import { cn } from '@/lib/utils'

export const ThemeToggle: React.FC = () => {
  const { isDark, toggle } = useTheme()

  return (
    <button
      onClick={toggle}
      className={cn(
        "relative inline-flex h-10 w-20 items-center rounded-full",
        "bg-gradient-to-r from-slate-200 to-slate-300 dark:from-slate-700 dark:to-slate-600",
        "hover:from-slate-300 hover:to-slate-400 dark:hover:from-slate-600 dark:hover:to-slate-500",
        "transition-all duration-300 ease-in-out",
        "focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:ring-offset-2",
        "focus:ring-offset-background shadow-md"
      )}
      aria-label="Toggle theme"
    >
      <span
        className={cn(
          "inline-block h-8 w-8 transform rounded-full",
          "bg-gradient-to-br from-white to-slate-100 dark:from-slate-800 dark:to-slate-900",
          "shadow-lg border border-slate-200 dark:border-slate-600",
          "transition-all duration-300 ease-in-out",
          isDark ? "translate-x-10" : "translate-x-1"
        )}
      />
      <Sun className="absolute left-2 h-4 w-4 text-amber-500 dark:text-amber-400" />
      <Moon className="absolute right-2 h-4 w-4 text-slate-600 dark:text-slate-300" />
    </button>
  )
} 