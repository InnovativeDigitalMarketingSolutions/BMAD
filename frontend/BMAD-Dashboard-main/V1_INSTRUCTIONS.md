# BMAD Dashboard v1.0 - Instructies

## 🎯 V1 Dashboard - BMAD Agents Live Monitoring

### **Nieuwe V1 Instructies:**

1. **BMAD Agents Focus**: Dashboard specifiek voor BMAD agent monitoring en management
2. **Live Backend Data**: Real-time data van BMAD agents via API endpoints
3. **Modern Apple-inspired Design**: Clean, minimal design met Apple OS invloeden
4. **Dark/Light Theme**: Toggle tussen donkere en lichte thema's
5. **Real-time Agent Monitoring**: Live status, performance, en activiteit van BMAD agents
6. **Agent Management**: Start/stop agents, configure agents, monitor agent health

### **BMAD Agents API Integration:**

**Live Data Endpoints:**
- `/api/agents` - Alle BMAD agents met status
- `/api/agents/{id}` - Specifieke agent details
- `/api/metrics` - System metrics voor agent performance
- `/api/workflows` - Agent workflows en taken

**Agent Data Structure:**
```typescript
interface BMADAgent {
  id: string
  name: string
  status: 'active' | 'idle' | 'error' | 'stopped'
  type: 'development' | 'testing' | 'planning' | 'management'
  performance: number // 0-100
  last_activity: string
  tasks: AgentTask[]
  metrics: {
    cpu_usage: number
    memory_usage: number
    response_time: number
  }
}
```

### **V1 Dashboard Features:**

1. **Agent Overview Cards**:
   - Total BMAD Agents
   - Active Agents
   - Idle Agents
   - Error Agents

2. **Live Agent Monitoring**:
   - Real-time agent status
   - Performance metrics
   - Last activity timestamps
   - Agent health indicators

3. **Agent Management**:
   - Start/Stop agents
   - Agent configuration
   - Performance monitoring
   - Error handling

4. **System Metrics for Agents**:
   - CPU usage per agent
   - Memory usage per agent
   - Response times
   - System health

### **Nieuwe V1 Architectuur:**

```
src/
├── components/
│   ├── v1/
│   │   ├── BMADDashboard.tsx      # Hoofddashboard voor BMAD agents
│   │   ├── AgentOverview.tsx      # Agent overzicht cards
│   │   ├── AgentMonitor.tsx       # Live agent monitoring
│   │   ├── AgentManagement.tsx    # Agent management tools
│   │   └── SystemMetrics.tsx      # System metrics voor agents
│   ├── ui/
│   │   ├── ThemeToggle.tsx
│   │   ├── LoadingSpinner.tsx
│   │   ├── AgentCard.tsx          # Nieuwe agent card component
│   │   └── StatusIndicator.tsx    # Agent status indicators
│   └── layout/
│       └── BMADLayout.tsx         # BMAD-specifieke layout
├── hooks/
│   ├── useBMADAgents.ts           # Hook voor agent data
│   ├── useAgentManagement.ts      # Hook voor agent management
│   └── useSystemMetrics.ts        # Hook voor system metrics
├── api/
│   ├── agentApi.ts                # BMAD agent API calls
│   └── metricsApi.ts              # System metrics API calls
└── types/
    └── bmad.ts                    # BMAD-specifieke types
```

### **Live Data Integration:**

1. **Real-time Agent Status**:
   - Poll agents elke 30 seconden
   - Live status updates
   - Performance monitoring

2. **Agent Management Actions**:
   - Start agent: `POST /api/agents/{id}/start`
   - Stop agent: `POST /api/agents/{id}/stop`
   - Configure agent: `PUT /api/agents/{id}`

3. **System Metrics for Agents**:
   - CPU usage monitoring
   - Memory usage tracking
   - Response time analysis
   - Error rate monitoring

### **V1 Design Specificaties:**

1. **BMAD-focused UI**:
   - Agent-centric design
   - Clear agent status indicators
   - Performance visualization
   - Management controls

2. **Apple-inspired Design**:
   - Clean, minimal interface
   - Subtle shadows en blur effects
   - Rounded corners
   - Apple system fonts

3. **Dark/Light Theme**:
   - Dark: `#1a1a1a` background, `#ffffff` text
   - Light: `#ffffff` background, `#1a1a1a` text
   - Smooth transitions

4. **Real-time Features**:
   - Live agent status updates
   - Real-time performance metrics
   - Instant management feedback
   - Error notifications

### **Implementatie Stappen:**

1. **Verwijder alle dummy data** - Geen bestaande data gebruiken
2. **Bouw nieuwe BMAD v1 componenten** - Vanaf 0 opbouwen
3. **Implementeer live BMAD agent monitoring** - Real-time data
4. **Test live BMAD agent data** - API integration

### **API Endpoints (Poort 5001):**
- `http://localhost:5001/api/agents` - BMAD agents
- `http://localhost:5001/api/metrics` - System metrics
- `http://localhost:5001/api/workflows` - Agent workflows

### **Belangrijke Regels:**
- **GEEN dummy data gebruiken**
- **Alleen live API data van poort 5001**
- **BMAD agents focus**
- **Apple-inspired design**
- **Real-time monitoring**

---

**Status**: 📋 **V1 INSTRUCTIES OPGESLAGEN** - Klaar voor implementatie 