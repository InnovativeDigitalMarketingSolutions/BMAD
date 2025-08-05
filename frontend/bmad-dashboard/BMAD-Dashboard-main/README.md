# BMAD Dashboard v1.0

Een moderne React dashboard voor BMAD (Business Model Agent Development) met real-time monitoring en agent management.

## 🚀 Features

### Core Functionaliteiten
- **Real-time Monitoring**: Agent status, workflow progress, system metrics
- **Agent Management**: Start/stop agents, performance tracking, configuration
- **Workflow Management**: Workflow monitoring, progress tracking, error handling
- **System Metrics**: CPU, memory, disk usage met real-time updates
- **Responsive Design**: Werkt op desktop en mobile devices

### UI/UX
- **Modern Design**: Clean, professional interface met Tailwind CSS
- **Dark/Light Theme**: Toggle tussen thema's
- **Collapsible Sidebar**: Ruimte-efficiënte navigatie
- **Real-time Updates**: Auto-refresh elke 30 seconden
- **Loading States**: Duidelijke feedback tijdens operaties
- **Error Handling**: Graceful error handling met user-friendly messages

### Component Architectuur
- **Modular Design**: Alle componenten zijn herbruikbaar en aanpasbaar
- **TypeScript**: Volledige type safety
- **Zustand State Management**: Efficiënte state management
- **API Integration**: RESTful API calls met error handling

## 🏗️ Architectuur

### Mappenstructuur
```
src/
├── components/
│   ├── ui/              # Herbruikbare UI primitives
│   │   ├── Button.tsx
│   │   ├── Card.tsx
│   │   ├── Badge.tsx
│   │   └── Progress.tsx
│   ├── layout/          # Layout componenten
│   │   ├── Sidebar.tsx
│   │   ├── Header.tsx
│   │   └── DashboardLayout.tsx
│   ├── agents/          # Agent-specifieke componenten
│   │   └── AgentCard.tsx
│   └── Dashboard/       # Dashboard pagina's
│       └── DashboardPage.tsx
├── state/               # Zustand stores
│   ├── agentStore.ts
│   ├── workflowStore.ts
│   └── uiStore.ts
├── lib/                 # API clients
│   ├── apiClient.ts
│   ├── agentApi.ts
│   └── workflowApi.ts
└── types/               # TypeScript types
    └── index.ts
```

### State Management
- **agentStore**: Agent data en acties
- **workflowStore**: Workflow data en acties  
- **uiStore**: UI state (sidebar, theme, notifications)

### API Integration
- **Base API Client**: Axios met interceptors en error handling
- **Agent API**: CRUD operaties voor agents
- **Workflow API**: CRUD operaties voor workflows

## 🚀 Quick Start

### Installatie
```bash
cd dashboard
npm install
```

### Development Server
```bash
npm run dev
```

De applicatie draait op `http://localhost:3000`

### Build voor Productie
```bash
npm run build
```

### Preview Build
```bash
npm run preview
```

## 🔧 Configuration

### Environment Variables
```env
VITE_API_BASE_URL=http://localhost:5001/api
VITE_APP_TITLE=BMAD Dashboard
```

### Port Configuration
- **Development**: Port 3000 (dashboard) + Port 5001 (API)
- **Production**: Port 3000 (dashboard) + Port 5000 (API)

## 📊 Dashboard Features

### Overview Cards
- **Active Agents**: Aantal actieve agents
- **Running Workflows**: Aantal actieve workflows
- **Active Tasks**: Aantal actieve taken
- **System Uptime**: Systeem uptime

### System Metrics
- **CPU Usage**: Real-time CPU gebruik met progress bar
- **Memory Usage**: Memory gebruik met details
- **Disk Usage**: Disk gebruik met vrije ruimte

### Agent Management
- **Agent Cards**: Overzicht van alle agents
- **Performance Metrics**: CPU, memory, response time
- **Status Indicators**: Visual status badges
- **Quick Actions**: Start/stop, edit, delete

### Real-time Updates
- **Auto-refresh**: Elke 30 seconden
- **Live Metrics**: Real-time performance data
- **Status Updates**: Agent en workflow status

## 🎨 UI Components

### Button Variants
- `primary`: Blauwe primary buttons
- `secondary`: Grijze secondary buttons
- `success`: Groene success buttons
- `warning`: Oranje warning buttons
- `error`: Rode error buttons
- `ghost`: Transparante ghost buttons

### Card Variants
- `default`: Standaard card met shadow
- `elevated`: Verhoogde card met meer shadow
- `outlined`: Card met border alleen

### Progress Variants
- `default`: Blauwe progress bar
- `success`: Groene progress bar
- `warning`: Oranje progress bar
- `error`: Rode progress bar

## 🔒 Security

### Best Practices
- **Input Validation**: Alle user inputs worden gevalideerd
- **Error Handling**: Comprehensive error handling
- **CORS**: Proper cross-origin handling
- **Authentication**: Ready voor auth implementatie

## 📱 Responsive Design

### Breakpoints
- **Mobile**: < 768px
- **Tablet**: 768px - 1024px
- **Desktop**: > 1024px

### Features
- **Collapsible Sidebar**: Past zich aan aan schermgrootte
- **Grid Layouts**: Responsive grid system
- **Touch Friendly**: Optimized voor touch devices

## 🧪 Testing

### Test Commands
```bash
# Type checking
npm run type-check

# Linting
npm run lint

# Build test
npm run build
```

## 📚 Development

### Code Standards
- **TypeScript**: Strict mode enabled
- **ESLint**: Code linting met React rules
- **Prettier**: Code formatting
- **Tailwind**: Utility-first CSS

### Component Guidelines
- **Props Interface**: Alle componenten hebben TypeScript interfaces
- **Default Props**: Sensible defaults voor alle props
- **Error Boundaries**: Error handling voor componenten
- **Loading States**: Loading indicators waar nodig

### State Management
- **Zustand**: Lightweight state management
- **Async Actions**: Proper async/await handling
- **Error States**: Error handling in stores
- **Loading States**: Loading indicators in stores

## 🚀 Deployment

### Build Process
```bash
npm run build
```

### Output
- **Dist Folder**: `dist/` met geoptimaliseerde files
- **Source Maps**: Voor debugging
- **Asset Optimization**: Geoptimaliseerde assets

### Server Requirements
- **Static Hosting**: Kan op elke static host
- **API Proxy**: Configureer proxy naar backend
- **HTTPS**: Aanbevolen voor productie

## 🔄 Updates & Maintenance

### Version Control
- **Git**: Conventional commits
- **Branches**: Feature branches voor nieuwe features
- **Releases**: Tagged releases

### Dependencies
- **Regular Updates**: Keep dependencies updated
- **Security**: Regular security audits
- **Compatibility**: Test compatibility bij updates

## 📞 Support

### Issues
- **GitHub Issues**: Voor bug reports en feature requests
- **Documentation**: Uitgebreide documentatie
- **Examples**: Code examples en best practices

### Contributing
- **Code Standards**: Volg de established standards
- **Testing**: Test alle nieuwe features
- **Documentation**: Update documentatie bij changes

---

**Status**: ✅ **v1.0 READY FOR DEVELOPMENT**

Deze dashboard is volledig modulair opgebouwd en kan eenvoudig worden aangepast en uitgebreid volgens de nieuwe afspraken. 