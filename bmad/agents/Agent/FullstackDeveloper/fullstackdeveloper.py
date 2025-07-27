#!/usr/bin/env python3
"""
Fullstack Developer Agent voor CoPilot AI Business Suite
Implementeert features van frontend tot backend. Output in code snippets, pull requests, changelogs, testresultaten en dev logs.
"""

import argparse
import sys
import textwrap
import logging
import time
from dotenv import load_dotenv
load_dotenv()
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

from bmad.agents.core.communication.message_bus import publish, subscribe
from bmad.agents.core.data.supabase_context import save_context, get_context


class FullstackDeveloperAgent:
    def __init__(self):
        pass

    def implement_story(self):
        print(
            textwrap.dedent(
                """
        ## Pull Request: User Authentication
        - [x] Endpoint `/auth/login` geïmplementeerd (FastAPI)
        - [x] JWT integratie met Supabase
        - [x] Frontend login form (Next.js)
        - [x] Unit tests (pytest, coverage 95%)
        - [ ] E2E test pending
        **Blockers:**
        - Nog geen e-mail service voor registratiebevestiging
        """
            )
        )

    def build_api(self):
        print(
            textwrap.dedent(
                """
        @router.post("/auth/login")
        def login(user: UserLogin):
            token = auth_service.authenticate(user.email, user.password)
            return {"access_token": token}
        """
            )
        )

    def build_frontend(self):
        """Bouw de BMAD frontend dashboard."""
        print("🚀 FullstackDeveloper - BMAD Frontend Development")
        print("=" * 60)
        
        # Haal architectuur op van de Architect
        architecture = get_context("Architect", "frontend_architecture")
        
        print("📋 BMAD Dashboard Componenten:")
        print("=" * 40)
        
        # Dashboard Component
        print("""
// components/Dashboard.tsx
import React, { useState, useEffect } from 'react';
import { AgentStatus } from './AgentStatus';
import { WorkflowManager } from './WorkflowManager';
import { APITester } from './APITester';
import { MetricsChart } from './MetricsChart';

export function Dashboard(): JSX.Element {
  const [activeTab, setActiveTab] = useState('agents');
  const [agents, setAgents] = useState([]);
  const [workflows, setWorkflows] = useState([]);
  const [metrics, setMetrics] = useState({});

  useEffect(() => {
    // Load initial data
    fetchAgents();
    fetchWorkflows();
    fetchMetrics();
  }, []);

  const fetchAgents = async () => {
    try {
      const response = await fetch('/api/agents/status');
      const data = await response.json();
      setAgents(data);
    } catch (error) {
      console.error('Error fetching agents:', error);
    }
  };

  const fetchWorkflows = async () => {
    try {
      const response = await fetch('/api/orchestrator/status');
      const data = await response.json();
      setWorkflows(data);
    } catch (error) {
      console.error('Error fetching workflows:', error);
    }
  };

  const fetchMetrics = async () => {
    try {
      const response = await fetch('/api/orchestrator/metrics');
      const data = await response.json();
      setMetrics(data);
    } catch (error) {
      console.error('Error fetching metrics:', error);
    }
  };

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>BMAD Dashboard</h1>
        <nav className="dashboard-nav">
          <button 
            className={activeTab === 'agents' ? 'active' : ''} 
            onClick={() => setActiveTab('agents')}
          >
            Agent Status
          </button>
          <button 
            className={activeTab === 'workflows' ? 'active' : ''} 
            onClick={() => setActiveTab('workflows')}
          >
            Workflows
          </button>
          <button 
            className={activeTab === 'api' ? 'active' : ''} 
            onClick={() => setActiveTab('api')}
          >
            API Testing
          </button>
          <button 
            className={activeTab === 'metrics' ? 'active' : ''} 
            onClick={() => setActiveTab('metrics')}
          >
            Metrics
          </button>
        </nav>
      </header>

      <main className="dashboard-content">
        {activeTab === 'agents' && <AgentStatus agents={agents} />}
        {activeTab === 'workflows' && <WorkflowManager workflows={workflows} />}
        {activeTab === 'api' && <APITester />}
        {activeTab === 'metrics' && <MetricsChart metrics={metrics} />}
      </main>
    </div>
  );
}
""")

        # Agent Status Component
        print("""
// components/AgentStatus.tsx
import React from 'react';

interface Agent {
  name: string;
  status: 'online' | 'offline' | 'error';
  lastSeen: string;
  performance: {
    responseTime: number;
    throughput: number;
  };
}

interface AgentStatusProps {
  agents: Agent[];
}

export function AgentStatus({ agents }: AgentStatusProps): JSX.Element {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online': return 'green';
      case 'offline': return 'red';
      case 'error': return 'orange';
      default: return 'gray';
    }
  };

  return (
    <div className="agent-status">
      <h2>Agent Status</h2>
      <div className="agent-grid">
        {agents.map((agent) => (
          <div key={agent.name} className="agent-card">
            <div className="agent-header">
              <h3>{agent.name}</h3>
              <span 
                className={`status-indicator ${getStatusColor(agent.status)}`}
                title={agent.status}
              />
            </div>
            <div className="agent-details">
              <p>Last seen: {agent.lastSeen}</p>
              <p>Response time: {agent.performance.responseTime}ms</p>
              <p>Throughput: {agent.performance.throughput}/min</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
""")

        # Workflow Manager Component
        print("""
// components/WorkflowManager.tsx
import React, { useState } from 'react';

interface Workflow {
  id: string;
  name: string;
  status: 'running' | 'completed' | 'failed' | 'paused';
  progress: number;
  startTime: string;
  endTime?: string;
}

interface WorkflowManagerProps {
  workflows: Workflow[];
}

export function WorkflowManager({ workflows }: WorkflowManagerProps): JSX.Element {
  const [selectedWorkflow, setSelectedWorkflow] = useState<string | null>(null);

  const startWorkflow = async (workflowName: string) => {
    try {
      const response = await fetch('/api/orchestrator/start-workflow', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ workflow: workflowName })
      });
      
      if (response.ok) {
        console.log('Workflow started successfully');
        // Refresh workflows
      }
    } catch (error) {
      console.error('Error starting workflow:', error);
    }
  };

  return (
    <div className="workflow-manager">
      <h2>Workflow Management</h2>
      
      <div className="workflow-controls">
        <button onClick={() => startWorkflow('feature')}>
          Start Feature Workflow
        </button>
        <button onClick={() => startWorkflow('bugfix')}>
          Start Bugfix Workflow
        </button>
        <button onClick={() => startWorkflow('deployment')}>
          Start Deployment Workflow
        </button>
      </div>

      <div className="workflow-list">
        {workflows.map((workflow) => (
          <div key={workflow.id} className="workflow-card">
            <div className="workflow-header">
              <h3>{workflow.name}</h3>
              <span className={`status ${workflow.status}`}>
                {workflow.status}
              </span>
            </div>
            <div className="workflow-progress">
              <div 
                className="progress-bar" 
                style={{ width: `${workflow.progress}%` }}
              />
              <span>{workflow.progress}%</span>
            </div>
            <div className="workflow-timestamps">
              <p>Started: {workflow.startTime}</p>
              {workflow.endTime && <p>Ended: {workflow.endTime}</p>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
""")

        # API Tester Component
        print("""
// components/APITester.tsx
import React, { useState } from 'react';

export function APITester(): JSX.Element {
  const [endpoint, setEndpoint] = useState('/api/test/ping');
  const [method, setMethod] = useState('GET');
  const [requestBody, setRequestBody] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);

  const testEndpoint = async () => {
    setLoading(true);
    try {
      const options: RequestInit = {
        method,
        headers: { 'Content-Type': 'application/json' }
      };

      if (method !== 'GET' && requestBody) {
        options.body = requestBody;
      }

      const response = await fetch(endpoint, options);
      const data = await response.json();
      
      setResponse(JSON.stringify(data, null, 2));
    } catch (error) {
      setResponse(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="api-tester">
      <h2>API Testing Interface</h2>
      
      <div className="api-controls">
        <div className="endpoint-input">
          <label>Endpoint:</label>
          <input 
            type="text" 
            value={endpoint} 
            onChange={(e) => setEndpoint(e.target.value)}
            placeholder="/api/endpoint"
          />
        </div>
        
        <div className="method-selector">
          <label>Method:</label>
          <select value={method} onChange={(e) => setMethod(e.target.value)}>
            <option value="GET">GET</option>
            <option value="POST">POST</option>
            <option value="PUT">PUT</option>
            <option value="DELETE">DELETE</option>
          </select>
        </div>
        
        <button onClick={testEndpoint} disabled={loading}>
          {loading ? 'Testing...' : 'Test Endpoint'}
        </button>
      </div>

      {method !== 'GET' && (
        <div className="request-body">
          <label>Request Body (JSON):</label>
          <textarea
            value={requestBody}
            onChange={(e) => setRequestBody(e.target.value)}
            placeholder='{"key": "value"}'
            rows={5}
          />
        </div>
      )}

      {response && (
        <div className="response">
          <h3>Response:</h3>
          <pre>{response}</pre>
        </div>
      )}
    </div>
  );
}
""")

        # Metrics Chart Component
        print("""
// components/MetricsChart.tsx
import React from 'react';

interface Metrics {
  workflows: {
    total: number;
    running: number;
    completed: number;
    failed: number;
  };
  agents: {
    total: number;
    online: number;
    offline: number;
  };
  performance: {
    avgResponseTime: number;
    totalRequests: number;
    successRate: number;
  };
}

interface MetricsChartProps {
  metrics: Metrics;
}

export function MetricsChart({ metrics }: MetricsChartProps): JSX.Element {
  return (
    <div className="metrics-chart">
      <h2>System Metrics</h2>
      
      <div className="metrics-grid">
        <div className="metric-card">
          <h3>Workflows</h3>
          <div className="metric-values">
            <div>Total: {metrics.workflows?.total || 0}</div>
            <div>Running: {metrics.workflows?.running || 0}</div>
            <div>Completed: {metrics.workflows?.completed || 0}</div>
            <div>Failed: {metrics.workflows?.failed || 0}</div>
          </div>
        </div>

        <div className="metric-card">
          <h3>Agents</h3>
          <div className="metric-values">
            <div>Total: {metrics.agents?.total || 0}</div>
            <div>Online: {metrics.agents?.online || 0}</div>
            <div>Offline: {metrics.agents?.offline || 0}</div>
          </div>
        </div>

        <div className="metric-card">
          <h3>Performance</h3>
          <div className="metric-values">
            <div>Avg Response: {metrics.performance?.avgResponseTime || 0}ms</div>
            <div>Total Requests: {metrics.performance?.totalRequests || 0}</div>
            <div>Success Rate: {metrics.performance?.successRate || 0}%</div>
          </div>
        </div>
      </div>
    </div>
  );
}
""")

        print("\n🎨 CSS Styling:")
        print("""
/* styles/dashboard.css */
.dashboard {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 2px solid #eee;
}

.dashboard-nav {
  display: flex;
  gap: 10px;
}

.dashboard-nav button {
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  background: #f0f0f0;
  cursor: pointer;
  transition: background 0.3s;
}

.dashboard-nav button.active {
  background: #007bff;
  color: white;
}

.agent-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.agent-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  background: white;
}

.status-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  display: inline-block;
}

.status-indicator.green { background: #28a745; }
.status-indicator.red { background: #dc3545; }
.status-indicator.orange { background: #ffc107; }
.status-indicator.gray { background: #6c757d; }

.workflow-controls {
  margin-bottom: 20px;
}

.workflow-controls button {
  margin-right: 10px;
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  background: #007bff;
  color: white;
  cursor: pointer;
}

.api-controls {
  display: grid;
  grid-template-columns: 1fr auto auto;
  gap: 15px;
  margin-bottom: 20px;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.metric-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  background: white;
  text-align: center;
}
""")

        print("\n📦 Package.json:")
        print("""
{
  "name": "bmad-dashboard",
  "version": "1.0.0",
  "description": "BMAD Agent Dashboard",
  "main": "index.js",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "test": "vitest"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.8.0"
  },
  "devDependencies": {
    "@types/react": "^18.0.27",
    "@types/react-dom": "^18.0.10",
    "@vitejs/plugin-react": "^3.1.0",
    "typescript": "^4.9.4",
    "vite": "^4.1.0",
    "vitest": "^0.29.0"
  }
}
""")

        # Sla de frontend code op
        save_context("FullstackDeveloper", "frontend_code", {
            "timestamp": time.time(),
            "components": ["Dashboard", "AgentStatus", "WorkflowManager", "APITester", "MetricsChart"],
            "status": "generated"
        })

        # Publiceer event
        publish("frontend_code_generated", {
            "agent": "FullstackDeveloper",
            "status": "success",
            "components_count": 5
        })

        print("\n✅ BMAD Frontend Dashboard gegenereerd!")
        print("📁 Componenten: Dashboard, AgentStatus, WorkflowManager, APITester, MetricsChart")
        print("🎨 CSS styling en package.json inbegrepen")
        print("🔗 Klaar voor integratie met BMAD API")

    def integrate_service(self):
        print(
            textwrap.dedent(
                """
        # Integratie met Supabase, Redis, pgvector, Langchain
        from supabase import create_client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        """
            )
        )

    def write_tests(self):
        print(
            textwrap.dedent(
                """
        def test_login_success(client):
            response = client.post("/auth/login", json={"email": "test@test.com", "password": "secret"})
            assert response.status_code == 200
            assert "access_token" in response.json()
        """
            )
        )

    def ci_cd(self):
        print(
            textwrap.dedent(
                """
        # CI/CD Pipeline (GitHub Actions)
        name: CI
        on: [push]
        jobs:
          build:
            runs-on: ubuntu-latest
            steps:
              - uses: actions/checkout@v3
              - name: Set up Python
                uses: actions/setup-python@v4
                with:
                  python-version: '3.11'
              - name: Install dependencies
                run: pip install -r requirements.txt
              - name: Run tests
                run: pytest
        """
            )
        )

    def dev_log(self):
        print(
            textwrap.dedent(
                """
        ### Dev Log 2024-07-20
        - User login endpoint gebouwd
        - JWT integratie getest
        - Frontend login form aangemaakt
        - Unit tests toegevoegd
        - Blocker: wacht op e-mail service
        """
            )
        )

    def review(self):
        print(
            textwrap.dedent(
                """
        # Code Review
        - [x] Code voldoet aan style guide
        - [x] Alle tests geslaagd
        - [ ] Edge cases afgedekt
        - [ ] Security checks uitgevoerd
        """
            )
        )

    def refactor(self):
        print(
            textwrap.dedent(
                """
        # Refactoring Advies
        - Herstructureer login logica naar aparte service
        - Gebruik environment variables voor secrets
        - Voeg type hints toe aan alle functies
        """
            )
        )

    def security_check(self):
        print(
            textwrap.dedent(
                """
        # Security Checklist
        - [x] Input validatie aanwezig
        - [x] JWT tokens met expiry
        - [ ] Rate limiting op login endpoint
        - [ ] Dependency scan uitgevoerd
        """
            )
        )

    def blockers(self):
        print(
            textwrap.dedent(
                """
        # Blockers
        - E-mail service ontbreekt voor registratie
        - Testdata niet beschikbaar voor E2E tests
        """
            )
        )

    # --- Uitbreidingen hieronder ---
    def api_contract(self):
        print(
            "Zie OpenAPI contract voorbeeld in: resources/templates/openapi-snippet.yaml"
        )

    def component_doc(self):
        print(
            "Zie Storybook/MDX voorbeeld in: resources/templates/storybook-mdx-template.mdx"
        )

    def performance_profile(self):
        print(
            "Zie performance report template in: resources/templates/performance-report-template.md"
        )

    def a11y_check(self):
        print(
            textwrap.dedent(
                """
        ## Accessibility Check
        - [x] Alle inputs hebben labels
        - [x] Contrast ratio voldoet aan WCAG AA
        - [ ] Keyboard navigation volledig ondersteund
        """
            )
        )

    def feature_toggle(self):
        print(
            "Zie feature toggle config in: resources/templates/feature-toggle-config.yaml"
        )

    def monitoring_setup(self):
        print(
            "Zie monitoring config snippet in: resources/templates/monitoring-config-snippet.yaml"
        )

    def release_notes(self):
        print(
            "Zie release notes template in: resources/templates/release-notes-template.md"
        )

    def devops_handover(self):
        print(
            "Zie DevOps handover checklist in: resources/templates/devops-handover-checklist.md"
        )

    def tech_debt(self):
        print(
            textwrap.dedent(
                """
        # Technische schuld
        - [ ] Oude API endpoints refactoren
        - [ ] Dependency upgrades nodig
        - [ ] Test coverage verhogen voor legacy code
        """
            )
        )

    def collaborate_example(self):
        """Voorbeeld van samenwerking: publiceer event en deel context via Supabase."""
        publish("feature_deployed", {"status": "success", "agent": "FullstackDeveloper"})
        save_context("FullstackDeveloper", {"feature_status": "deployed"})
        print("Event gepubliceerd en context opgeslagen.")
        context = get_context("FullstackDeveloper")
        print(f"Opgehaalde context: {context}")

    def handle_tasks_assigned(self, event):
        logging.info("[FullstackDeveloper] Taken ontvangen, ontwikkeling wordt gestart...")
        time.sleep(1)
        publish("development_started", {"desc": "Ontwikkeling gestart"})
        logging.info("[FullstackDeveloper] Ontwikkeling gestart, development_started gepubliceerd.")

    def handle_development_started(self, event):
        logging.info("[FullstackDeveloper] Ontwikkeling in uitvoering...")
        time.sleep(2)
        publish("testing_started", {"desc": "Testen gestart"})
        logging.info("[FullstackDeveloper] Testen gestart, testing_started gepubliceerd.")

    def setup_event_handlers(self):
        subscribe("tasks_assigned", self.handle_tasks_assigned)
        subscribe("development_started", self.handle_development_started)

    def show_help(self):
        print(
            """
Beschikbare commando's:
- implement-story
- build-api
- build-frontend
- integrate-service
- write-tests
- ci-cd
- dev-log
- review
- refactor
- security-check
- blockers
- api-contract
- component-doc
- performance-profile
- a11y-check
- feature-toggle
- monitoring-setup
- release-notes
- devops-handover
- tech-debt
- collaborate-example
- help
        """
        )

    def run(self, command):
        commands = {
            "implement-story": self.implement_story,
            "build-api": self.build_api,
            "build-frontend": self.build_frontend,
            "integrate-service": self.integrate_service,
            "write-tests": self.write_tests,
            "ci-cd": self.ci_cd,
            "dev-log": self.dev_log,
            "review": self.review,
            "refactor": self.refactor,
            "security-check": self.security_check,
            "blockers": self.blockers,
            "api-contract": self.api_contract,
            "component-doc": self.component_doc,
            "performance-profile": self.performance_profile,
            "a11y-check": self.a11y_check,
            "feature-toggle": self.feature_toggle,
            "monitoring-setup": self.monitoring_setup,
            "release-notes": self.release_notes,
            "devops-handover": self.devops_handover,
            "tech-debt": self.tech_debt,
            "collaborate-example": self.collaborate_example,
            "help": self.show_help,
        }
        func = commands.get(command)
        if func:
            func()
        else:
            print(f"❌ Onbekend commando: {command}")
            self.show_help()


def main():
    parser = argparse.ArgumentParser(description="Fullstack Developer Agent")
    parser.add_argument("command", nargs="?", help="Commando om uit te voeren")
    args = parser.parse_args()
    agent = FullstackDeveloperAgent()
    agent.setup_event_handlers()
    if args.command:
        agent.run(args.command)
    else:
        agent.show_help()


if __name__ == "__main__":
    main()
