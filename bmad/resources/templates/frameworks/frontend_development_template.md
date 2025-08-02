# Frontend Development Framework Template

## 🎯 Frontend Development Overview

Dit framework template biedt een complete gids voor frontend development binnen het BMAD systeem, inclusief moderne web development best practices, component architecture, en development workflows.

## 🏗️ Frontend Architecture Patterns

### Component-Based Architecture
```
Frontend Application:
├── Components/
│   ├── UI/                 # Reusable UI components
│   │   ├── Button/
│   │   ├── Input/
│   │   ├── Modal/
│   │   └── Card/
│   ├── Layout/             # Layout components
│   │   ├── Header/
│   │   ├── Sidebar/
│   │   ├── Footer/
│   │   └── Navigation/
│   ├── Features/           # Feature-specific components
│   │   ├── Dashboard/
│   │   ├── AgentManagement/
│   │   ├── WorkflowEditor/
│   │   └── Analytics/
│   └── Common/             # Shared components
│       ├── Loading/
│       ├── ErrorBoundary/
│       └── Toast/
├── Pages/                  # Page components
├── Hooks/                  # Custom React hooks
├── Services/               # API services
├── Utils/                  # Utility functions
├── Types/                  # TypeScript type definitions
└── Styles/                 # Global styles and themes
```

### State Management Patterns
- **Local State**: React useState voor component-level state
- **Global State**: Zustand/Redux voor application-level state
- **Server State**: React Query/TanStack Query voor API state
- **Form State**: React Hook Form voor form management
- **URL State**: React Router voor route-based state

### Data Flow Architecture
```
Data Flow:
API Layer → Service Layer → State Management → Components → UI
    ↑                                                      ↓
    └─────────────── Error Handling ←──────────────────────┘
```

## 🔧 Frontend Development Best Practices

### Code Structure
```
frontend-app/
├── src/
│   ├── components/         # Reusable components
│   │   ├── ui/            # Base UI components
│   │   ├── layout/        # Layout components
│   │   └── features/      # Feature components
│   ├── pages/             # Page components
│   ├── hooks/             # Custom React hooks
│   ├── services/          # API services
│   ├── utils/             # Utility functions
│   ├── types/             # TypeScript definitions
│   ├── styles/            # Global styles
│   ├── constants/         # Application constants
│   └── assets/            # Static assets
├── public/                # Public assets
├── tests/                 # Test files
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   └── e2e/              # End-to-end tests
├── docs/                  # Documentation
├── package.json           # Dependencies
├── tsconfig.json          # TypeScript config
├── vite.config.ts         # Build configuration
└── tailwind.config.js     # Tailwind CSS config
```

### Component Design Principles
```typescript
// Component Structure
interface ComponentProps {
  // Props interface
}

const Component: React.FC<ComponentProps> = ({ prop1, prop2 }) => {
  // Hooks
  const [state, setState] = useState();
  const { data, isLoading, error } = useQuery();
  
  // Event handlers
  const handleClick = useCallback(() => {
    // Handler logic
  }, []);
  
  // Effects
  useEffect(() => {
    // Side effects
  }, []);
  
  // Render
  if (isLoading) return <Loading />;
  if (error) return <Error message={error.message} />;
  
  return (
    <div className="component">
      {/* JSX */}
    </div>
  );
};

export default Component;
```

### TypeScript Best Practices
```typescript
// Type Definitions
interface User {
  id: string;
  email: string;
  name: string;
  role: UserRole;
  createdAt: Date;
  updatedAt: Date;
}

type UserRole = 'admin' | 'user' | 'guest';

// API Response Types
interface ApiResponse<T> {
  data: T;
  message: string;
  success: boolean;
}

interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
}

// Component Props with Generics
interface ListProps<T> {
  items: T[];
  renderItem: (item: T, index: number) => React.ReactNode;
  onItemClick?: (item: T) => void;
  loading?: boolean;
  error?: string;
}
```

## 🧪 Frontend Testing Strategy

### Unit Testing Framework
```typescript
// Component Testing
import { render, screen, fireEvent } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Component from './Component';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: false },
    mutations: { retry: false },
  },
});

const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <QueryClientProvider client={queryClient}>
    {children}
  </QueryClientProvider>
);

describe('Component', () => {
  it('renders correctly', () => {
    render(
      <TestWrapper>
        <Component />
      </TestWrapper>
    );
    
    expect(screen.getByText('Expected Text')).toBeInTheDocument();
  });
  
  it('handles user interaction', () => {
    render(
      <TestWrapper>
        <Component />
      </TestWrapper>
    );
    
    const button = screen.getByRole('button');
    fireEvent.click(button);
    
    expect(screen.getByText('Clicked!')).toBeInTheDocument();
  });
  
  it('displays loading state', () => {
    render(
      <TestWrapper>
        <Component loading={true} />
      </TestWrapper>
    );
    
    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
  });
});
```

### Integration Testing
```typescript
// API Integration Testing
import { rest } from 'msw';
import { setupServer } from 'msw/node';
import { render, screen, waitFor } from '@testing-library/react';
import UserList from './UserList';

const server = setupServer(
  rest.get('/api/users', (req, res, ctx) => {
    return res(
      ctx.json({
        data: [
          { id: '1', name: 'John Doe', email: 'john@example.com' },
          { id: '2', name: 'Jane Smith', email: 'jane@example.com' },
        ],
        success: true,
      })
    );
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('UserList Integration', () => {
  it('fetches and displays users', async () => {
    render(<UserList />);
    
    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('Jane Smith')).toBeInTheDocument();
    });
  });
  
  it('handles API errors', async () => {
    server.use(
      rest.get('/api/users', (req, res, ctx) => {
        return res(ctx.status(500));
      })
    );
    
    render(<UserList />);
    
    await waitFor(() => {
      expect(screen.getByText('Error loading users')).toBeInTheDocument();
    });
  });
});
```

### E2E Testing
```typescript
// Playwright E2E Testing
import { test, expect } from '@playwright/test';

test.describe('User Management', () => {
  test('user can create a new agent', async ({ page }) => {
    await page.goto('/dashboard');
    
    // Login
    await page.fill('[data-testid="email-input"]', 'user@example.com');
    await page.fill('[data-testid="password-input"]', 'password123');
    await page.click('[data-testid="login-button"]');
    
    // Navigate to agent creation
    await page.click('[data-testid="create-agent-button"]');
    
    // Fill agent form
    await page.fill('[data-testid="agent-name-input"]', 'Test Agent');
    await page.selectOption('[data-testid="agent-type-select"]', 'backend');
    await page.fill('[data-testid="agent-description-input"]', 'Test agent description');
    
    // Submit form
    await page.click('[data-testid="submit-button"]');
    
    // Verify success
    await expect(page.locator('[data-testid="success-message"]')).toBeVisible();
    await expect(page.locator('text=Test Agent')).toBeVisible();
  });
  
  test('user can view agent analytics', async ({ page }) => {
    await page.goto('/dashboard/agents/123/analytics');
    
    // Wait for analytics to load
    await page.waitForSelector('[data-testid="analytics-chart"]');
    
    // Verify analytics data
    await expect(page.locator('[data-testid="total-executions"]')).toContainText('150');
    await expect(page.locator('[data-testid="success-rate"]')).toContainText('95%');
  });
});
```

## 🚀 Frontend Development Workflow

### Development Environment Setup
```bash
# 1. Create React application with Vite
npm create vite@latest frontend-app -- --template react-ts

# 2. Install dependencies
cd frontend-app
npm install

# 3. Install additional dependencies
npm install @tanstack/react-query @tanstack/react-query-devtools
npm install zustand react-hook-form @hookform/resolvers
npm install react-router-dom @types/react-router-dom
npm install tailwindcss @tailwindcss/forms @tailwindcss/typography
npm install @headlessui/react @heroicons/react
npm install axios msw

# 4. Setup Tailwind CSS
npx tailwindcss init -p

# 5. Start development server
npm run dev
```

### Code Quality Gates
```json
// package.json scripts
{
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest --coverage",
    "lint": "eslint src --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
    "lint:fix": "eslint src --ext ts,tsx --fix",
    "type-check": "tsc --noEmit",
    "format": "prettier --write src/",
    "format:check": "prettier --check src/"
  }
}
```

### Pre-commit Hooks
```json
// .husky/pre-commit
#!/bin/sh
. "$(dirname "$0")/_/husky.sh"

npm run lint
npm run type-check
npm run test:coverage
npm run format:check
```

## 🎨 Frontend Styling & Design System

### Tailwind CSS Configuration
```javascript
// tailwind.config.js
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          500: '#3b82f6',
          900: '#1e3a8a',
        },
        secondary: {
          50: '#f8fafc',
          500: '#64748b',
          900: '#0f172a',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
}
```

### Component Styling Patterns
```typescript
// Utility-first styling
const Button: React.FC<ButtonProps> = ({ variant = 'primary', size = 'md', children, ...props }) => {
  const baseClasses = 'inline-flex items-center justify-center rounded-md font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2';
  
  const variantClasses = {
    primary: 'bg-primary-500 text-white hover:bg-primary-600 focus:ring-primary-500',
    secondary: 'bg-secondary-100 text-secondary-900 hover:bg-secondary-200 focus:ring-secondary-500',
    outline: 'border border-secondary-300 bg-white text-secondary-700 hover:bg-secondary-50 focus:ring-primary-500',
  };
  
  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-sm',
    lg: 'px-6 py-3 text-base',
  };
  
  const className = `${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]}`;
  
  return (
    <button className={className} {...props}>
      {children}
    </button>
  );
};
```

### Design System Components
```typescript
// Design System Component Library
export const components = {
  Button,
  Input,
  Select,
  Modal,
  Card,
  Badge,
  Alert,
  Toast,
  Loading,
  ErrorBoundary,
} as const;

// Component variants
export const buttonVariants = {
  primary: 'bg-primary-500 text-white hover:bg-primary-600',
  secondary: 'bg-secondary-100 text-secondary-900 hover:bg-secondary-200',
  outline: 'border border-secondary-300 bg-white text-secondary-700 hover:bg-secondary-50',
  ghost: 'text-secondary-700 hover:bg-secondary-100',
  destructive: 'bg-red-500 text-white hover:bg-red-600',
} as const;
```

## 🔒 Frontend Security Framework

### Authentication & Authorization
```typescript
// Authentication Context
interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  
  const login = async (email: string, password: string) => {
    try {
      const response = await authService.login(email, password);
      setUser(response.user);
      localStorage.setItem('token', response.token);
    } catch (error) {
      throw new Error('Login failed');
    }
  };
  
  const logout = () => {
    setUser(null);
    localStorage.removeItem('token');
  };
  
  useEffect(() => {
    // Check for existing token on app load
    const token = localStorage.getItem('token');
    if (token) {
      authService.validateToken(token)
        .then(user => setUser(user))
        .catch(() => logout())
        .finally(() => setIsLoading(false));
    } else {
      setIsLoading(false);
    }
  }, []);
  
  return (
    <AuthContext.Provider value={{ user, login, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
};

// Protected Route Component
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, isLoading } = useAuth();
  
  if (isLoading) {
    return <Loading />;
  }
  
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  
  return <>{children}</>;
};
```

### Input Validation & Sanitization
```typescript
// Form Validation with React Hook Form
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const userSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string()
    .min(8, 'Password must be at least 8 characters')
    .regex(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/, 'Password must contain uppercase, lowercase, and number'),
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"],
});

type UserFormData = z.infer<typeof userSchema>;

const UserForm: React.FC = () => {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<UserFormData>({
    resolver: zodResolver(userSchema),
  });
  
  const onSubmit = async (data: UserFormData) => {
    try {
      await userService.createUser(data);
      toast.success('User created successfully');
    } catch (error) {
      toast.error('Failed to create user');
    }
  };
  
  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <div>
        <label htmlFor="email">Email</label>
        <input
          id="email"
          type="email"
          {...register('email')}
          className={errors.email ? 'border-red-500' : ''}
        />
        {errors.email && <span className="text-red-500">{errors.email.message}</span>}
      </div>
      
      <div>
        <label htmlFor="password">Password</label>
        <input
          id="password"
          type="password"
          {...register('password')}
          className={errors.password ? 'border-red-500' : ''}
        />
        {errors.password && <span className="text-red-500">{errors.password.message}</span>}
      </div>
      
      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Creating...' : 'Create User'}
      </button>
    </form>
  );
};
```

## 📊 Frontend Performance Optimization

### Code Splitting & Lazy Loading
```typescript
// Route-based code splitting
import { lazy, Suspense } from 'react';
import { Routes, Route } from 'react-router-dom';

const Dashboard = lazy(() => import('./pages/Dashboard'));
const AgentManagement = lazy(() => import('./pages/AgentManagement'));
const Analytics = lazy(() => import('./pages/Analytics'));

const App: React.FC = () => {
  return (
    <Suspense fallback={<Loading />}>
      <Routes>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/agents" element={<AgentManagement />} />
        <Route path="/analytics" element={<Analytics />} />
      </Routes>
    </Suspense>
  );
};

// Component lazy loading
const HeavyComponent = lazy(() => import('./HeavyComponent'));

const ParentComponent: React.FC = () => {
  const [showHeavy, setShowHeavy] = useState(false);
  
  return (
    <div>
      <button onClick={() => setShowHeavy(true)}>Load Heavy Component</button>
      {showHeavy && (
        <Suspense fallback={<Loading />}>
          <HeavyComponent />
        </Suspense>
      )}
    </div>
  );
};
```

### State Management Optimization
```typescript
// Zustand Store with Selectors
import { create } from 'zustand';
import { subscribeWithSelector } from 'zustand/middleware';

interface AppState {
  users: User[];
  agents: Agent[];
  workflows: Workflow[];
  setUsers: (users: User[]) => void;
  addUser: (user: User) => void;
  updateUser: (id: string, updates: Partial<User>) => void;
  deleteUser: (id: string) => void;
}

const useAppStore = create<AppState>()(
  subscribeWithSelector((set, get) => ({
    users: [],
    agents: [],
    workflows: [],
    
    setUsers: (users) => set({ users }),
    
    addUser: (user) => set((state) => ({
      users: [...state.users, user]
    })),
    
    updateUser: (id, updates) => set((state) => ({
      users: state.users.map(user =>
        user.id === id ? { ...user, ...updates } : user
      )
    })),
    
    deleteUser: (id) => set((state) => ({
      users: state.users.filter(user => user.id !== id)
    })),
  }))
);

// Optimized selectors
export const useUsers = () => useAppStore((state) => state.users);
export const useUserById = (id: string) => useAppStore(
  (state) => state.users.find(user => user.id === id)
);
export const useUserActions = () => useAppStore((state) => ({
  addUser: state.addUser,
  updateUser: state.updateUser,
  deleteUser: state.deleteUser,
}));
```

### API Caching & Optimization
```typescript
// React Query Configuration
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
      retry: 3,
      refetchOnWindowFocus: false,
    },
    mutations: {
      retry: 1,
    },
  },
});

// Custom hooks for API calls
export const useUsers = () => {
  return useQuery({
    queryKey: ['users'],
    queryFn: userService.getUsers,
    staleTime: 5 * 60 * 1000,
  });
};

export const useUser = (id: string) => {
  return useQuery({
    queryKey: ['users', id],
    queryFn: () => userService.getUser(id),
    enabled: !!id,
  });
};

export const useCreateUser = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: userService.createUser,
    onSuccess: (newUser) => {
      // Update cache
      queryClient.setQueryData(['users'], (old: User[] = []) => [...old, newUser]);
      queryClient.invalidateQueries(['users']);
    },
  });
};
```

## 🚀 Frontend Deployment Strategy

### Build Configuration
```typescript
// vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
      '@components': resolve(__dirname, 'src/components'),
      '@pages': resolve(__dirname, 'src/pages'),
      '@services': resolve(__dirname, 'src/services'),
      '@utils': resolve(__dirname, 'src/utils'),
      '@types': resolve(__dirname, 'src/types'),
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          router: ['react-router-dom'],
          query: ['@tanstack/react-query'],
          ui: ['@headlessui/react', '@heroicons/react'],
        },
      },
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
});
```

### Docker Configuration
```dockerfile
# Multi-stage Docker build
FROM node:18-alpine as builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM nginx:alpine as runtime
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Nginx Configuration
```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
    
    server {
        listen 80;
        server_name localhost;
        root /usr/share/nginx/html;
        index index.html;
        
        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header Referrer-Policy "no-referrer-when-downgrade" always;
        add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
        
        # API proxy
        location /api/ {
            proxy_pass http://backend:8000/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # SPA routing
        location / {
            try_files $uri $uri/ /index.html;
        }
        
        # Static assets caching
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
```

## 📚 Frontend Development Resources

### Essential Libraries
- **React**: UI library for building user interfaces
- **TypeScript**: Static type checking for JavaScript
- **Vite**: Fast build tool and development server
- **Tailwind CSS**: Utility-first CSS framework
- **React Query**: Data fetching and caching library
- **React Hook Form**: Performant forms with easy validation
- **React Router**: Declarative routing for React
- **Zustand**: Lightweight state management
- **Headless UI**: Unstyled, accessible UI components
- **Heroicons**: Beautiful hand-crafted SVG icons

### Development Tools
- **ESLint**: JavaScript linting utility
- **Prettier**: Code formatter
- **Vitest**: Unit testing framework
- **Playwright**: End-to-end testing
- **MSW**: API mocking for development and testing
- **React Query Devtools**: Development tools for React Query

### Documentation
- **React Documentation**: https://react.dev/
- **TypeScript Documentation**: https://www.typescriptlang.org/docs/
- **Vite Documentation**: https://vitejs.dev/
- **Tailwind CSS Documentation**: https://tailwindcss.com/docs
- **React Query Documentation**: https://tanstack.com/query/latest
- **React Hook Form Documentation**: https://react-hook-form.com/

---

**Template Version**: 1.0  
**Last Updated**: 27 januari 2025  
**Maintained By**: Frontend Development Team 