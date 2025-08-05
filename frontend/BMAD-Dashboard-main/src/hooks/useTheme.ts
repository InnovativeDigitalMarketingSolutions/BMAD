// Theme Hook - Dark/Light theme toggle (Shadcn/ui compatible)
import { useState, useEffect } from 'react'

export const useTheme = () => {
  const [isDark, setIsDark] = useState(() => {
    // Check localStorage for saved theme preference
    const saved = localStorage.getItem('bmad-theme')
    if (saved) {
      return saved === 'dark'
    }
    // Check system preference
    return window.matchMedia('(prefers-color-scheme: dark)').matches
  })

  useEffect(() => {
    // Update localStorage when theme changes
    localStorage.setItem('bmad-theme', isDark ? 'dark' : 'light')
    
    // Update document class for CSS variables (shadcn/ui compatible)
    const root = document.documentElement
    if (isDark) {
      root.classList.add('dark')
    } else {
      root.classList.remove('dark')
    }
  }, [isDark])

  // Initialize theme on mount to ensure it's applied immediately
  useEffect(() => {
    const saved = localStorage.getItem('bmad-theme')
    if (saved) {
      const root = document.documentElement
      if (saved === 'dark') {
        root.classList.add('dark')
      } else {
        root.classList.remove('dark')
      }
    }
  }, [])

  const toggle = () => setIsDark(!isDark)

  return {
    isDark,
    toggle
  }
} 