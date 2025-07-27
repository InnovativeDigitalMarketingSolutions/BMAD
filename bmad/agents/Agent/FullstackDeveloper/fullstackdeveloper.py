#!/usr/bin/env python3
"""
Fullstack Developer Agent voor CoPilot AI Business Suite
Implementeert features van frontend tot backend met Shadcn/ui integratie.
Output in code snippets, pull requests, changelogs, testresultaten en dev logs.
"""

import argparse
import sys
import textwrap
import logging
import time
import json
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import asyncio
from dotenv import load_dotenv
load_dotenv()
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

from bmad.agents.core.communication.message_bus import publish, subscribe
from bmad.agents.core.agent.test_sprites import get_sprite_library
from bmad.agents.core.agent.agent_performance_monitor import get_performance_monitor, MetricType
from bmad.agents.core.policy.advanced_policy_engine import get_advanced_policy_engine
from bmad.agents.core.data.supabase_context import save_context, get_context
from bmad.agents.core.ai.llm_client import ask_openai
from bmad.agents.core.ai.confidence_scoring import confidence_scoring
from integrations.slack.slack_notify import send_slack_message

# Configure logging
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

class FullstackDeveloperAgent:
    def __init__(self):
        # Initialize core services
        self.monitor = get_performance_monitor()
        self.policy_engine = get_advanced_policy_engine()
        self.sprite_library = get_sprite_library()
        
        # Resource paths
        self.resource_base = Path("/Users/yannickmacgillavry/Projects/BMAD/bmad/resources")
        self.template_paths = {
            "best-practices": self.resource_base / "templates/fullstackdeveloper/best-practices.md",
            "shadcn-component": self.resource_base / "templates/fullstackdeveloper/shadcn-component-template.tsx",
            "api-template": self.resource_base / "templates/fullstackdeveloper/api-template.py",
            "frontend-template": self.resource_base / "templates/fullstackdeveloper/frontend-template.tsx",
            "test-template": self.resource_base / "templates/fullstackdeveloper/test-template.py",
            "ci-cd-template": self.resource_base / "templates/fullstackdeveloper/ci-cd-template.yaml",
            "performance-report": self.resource_base / "templates/fullstackdeveloper/performance-report-template.md"
        }
        self.data_paths = {
            "changelog": self.resource_base / "data/fullstackdeveloper/changelog.md",
            "history": self.resource_base / "data/fullstackdeveloper/history.md",
            "feedback": self.resource_base / "data/fullstackdeveloper/feedback.md"
        }
        
        # Initialize histories
        self.development_history = []
        self.performance_history = []
        self._load_development_history()
        self._load_performance_history()

    def _load_development_history(self):
        try:
            if self.data_paths["history"].exists():
                with open(self.data_paths["history"], 'r') as f:
                    content = f.read()
                    lines = content.split('\n')
                    for line in lines:
                        if line.strip().startswith('- '):
                            self.development_history.append(line.strip()[2:])
        except Exception as e:
            logger.warning(f"Could not load development history: {e}")

    def _save_development_history(self):
        try:
            self.data_paths["history"].parent.mkdir(parents=True, exist_ok=True)
            with open(self.data_paths["history"], 'w') as f:
                f.write("# Development History\n\n")
                for dev in self.development_history[-50:]:
                    f.write(f"- {dev}\n")
        except Exception as e:
            logger.error(f"Could not save development history: {e}")

    def _load_performance_history(self):
        try:
            if self.data_paths["feedback"].exists():
                with open(self.data_paths["feedback"], 'r') as f:
                    content = f.read()
                    lines = content.split('\n')
                    for line in lines:
                        if line.strip().startswith('- '):
                            self.performance_history.append(line.strip()[2:])
        except Exception as e:
            logger.warning(f"Could not load performance history: {e}")

    def _save_performance_history(self):
        try:
            self.data_paths["feedback"].parent.mkdir(parents=True, exist_ok=True)
            with open(self.data_paths["feedback"], 'w') as f:
                f.write("# Performance History\n\n")
                for perf in self.performance_history[-50:]:
                    f.write(f"- {perf}\n")
        except Exception as e:
            logger.error(f"Could not save performance history: {e}")

    def show_help(self):
        help_text = """
FullstackDeveloper Agent Commands:
  help                    - Show this help message
  implement-story         - Implement user story
  build-api               - Build API endpoint
  build-frontend          - Build frontend with Shadcn/ui
  build-shadcn-component  - Generate Shadcn component
  integrate-service       - Integrate external service
  write-tests             - Write tests
  ci-cd                   - Show CI/CD pipeline
  dev-log                 - Show development log
  review                  - Code review
  refactor                - Refactoring advice
  security-check          - Security checklist
  blockers                - Show blockers
  show-development-history - Show development history
  show-performance        - Show performance metrics
  show-best-practices     - Show best practices
  show-changelog          - Show changelog
  export-report [format]  - Export report (md, json)
  test                    - Test resource completeness
  collaborate             - Demonstrate collaboration
  api-contract            - Show API contract
  component-doc           - Show component documentation
  performance-profile     - Show performance profile
  a11y-check              - Show accessibility check
  feature-toggle          - Show feature toggle config
  monitoring-setup        - Show monitoring setup
  release-notes           - Show release notes
  devops-handover         - Show DevOps handover
  tech-debt               - Show technical debt
        """
        print(help_text)

    def show_resource(self, resource_type: str):
        try:
            if resource_type == "best-practices":
                path = self.template_paths["best-practices"]
            elif resource_type == "changelog":
                path = self.data_paths["changelog"]
            elif resource_type == "shadcn-component":
                path = self.template_paths["shadcn-component"]
            else:
                print(f"Unknown resource type: {resource_type}")
                return
            if path.exists():
                with open(path, 'r') as f:
                    print(f.read())
            else:
                print(f"Resource file not found: {path}")
        except Exception as e:
            logger.error(f"Error reading resource {resource_type}: {e}")

    def show_development_history(self):
        if not self.development_history:
            print("No development history available.")
            return
        print("Development History:")
        print("=" * 50)
        for i, dev in enumerate(self.development_history[-10:], 1):
            print(f"{i}. {dev}")

    def show_performance(self):
        if not self.performance_history:
            print("No performance history available.")
            return
        print("Performance History:")
        print("=" * 50)
        for i, perf in enumerate(self.performance_history[-10:], 1):
            print(f"{i}. {perf}")

    def export_report(self, format_type: str = "md", report_data: Optional[Dict] = None):
        if not report_data:
            report_data = {
                "story": "User Authentication",
                "status": "implemented",
                "frontend_components": 3,
                "backend_endpoints": 2,
                "tests_written": 5,
                "shadcn_components": 2,
                "timestamp": datetime.now().isoformat(),
                "agent": "FullstackDeveloperAgent"
            }
        
        try:
            if format_type == "md":
                self._export_markdown(report_data)
            elif format_type == "json":
                self._export_json(report_data)
            else:
                print(f"Unsupported format: {format_type}")
        except Exception as e:
            logger.error(f"Error exporting report: {e}")

    def _export_markdown(self, report_data: Dict):
        output_file = f"fullstack_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        content = f"""# Fullstack Developer Report

## Summary
- **Story**: {report_data.get('story', 'N/A')}
- **Status**: {report_data.get('status', 'N/A')}
- **Timestamp**: {report_data.get('timestamp', 'N/A')}
- **Agent**: {report_data.get('agent', 'N/A')}

## Components
- Frontend Components: {report_data.get('frontend_components', 0)}
- Backend Endpoints: {report_data.get('backend_endpoints', 0)}
- Tests Written: {report_data.get('tests_written', 0)}
- Shadcn Components: {report_data.get('shadcn_components', 0)}

## Performance
- Accessibility Score: {report_data.get('accessibility_score', 0)}%
- Performance Score: {report_data.get('performance_score', 0)}%
"""
        
        with open(output_file, 'w') as f:
            f.write(content)
        print(f"Report export saved to: {output_file}")

    def _export_json(self, report_data: Dict):
        output_file = f"fullstack_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(output_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"Report export saved to: {output_file}")

    def test_resource_completeness(self):
        print("Testing resource completeness...")
        missing_resources = []
        
        for name, path in self.template_paths.items():
            if not path.exists():
                missing_resources.append(f"Template: {name} ({path})")
        
        for name, path in self.data_paths.items():
            if not path.exists():
                missing_resources.append(f"Data: {name} ({path})")
        
        if missing_resources:
            print("Missing resources:")
            for resource in missing_resources:
                print(f"  - {resource}")
        else:
            print("All resources are available!")

    def build_shadcn_component(self, component_name: str = "Button") -> Dict[str, Any]:
        logger.info(f"Building Shadcn component: {component_name}")
        
        # Simuleer Shadcn component bouw
        time.sleep(1)
        result = {
            "component": component_name,
            "type": "Shadcn/ui",
            "variants": ["default", "secondary", "outline", "destructive", "ghost", "link"],
            "sizes": ["sm", "default", "lg", "icon"],
            "status": "created",
            "accessibility_score": 98,
            "timestamp": datetime.now().isoformat(),
            "agent": "FullstackDeveloperAgent"
        }
        
        # Log performance metric
        self.monitor._record_metric("FullstackDeveloper", MetricType.SUCCESS_RATE, result["accessibility_score"], "%")
        
        logger.info(f"Shadcn component build result: {result}")
        return result

    def collaborate_example(self):
        """Voorbeeld van samenwerking: publiceer event en deel context via Supabase."""
        logger.info("Starting collaboration example...")
        
        # Publish development request
        publish("fullstack_development_requested", {
            "agent": "FullstackDeveloperAgent",
            "story": "User Authentication",
            "timestamp": datetime.now().isoformat()
        })
        
        # Implement story
        self.implement_story()
        
        # Build frontend with Shadcn
        self.build_frontend()
        
        # Build Shadcn component
        component_result = self.build_shadcn_component("Button")
        
        # Publish completion
        publish("fullstack_development_completed", {
            "status": "success", 
            "agent": "FullstackDeveloperAgent",
            "shadcn_components": 1
        })
        
        # Save context
        save_context("FullstackDeveloper", {"feature_status": "deployed"})
        
        # Notify via Slack
        try:
            send_slack_message(f"Fullstack development completed with {component_result['variants']} Shadcn component variants")
        except Exception as e:
            logger.warning(f"Could not send Slack notification: {e}")
        
        print("Event gepubliceerd en context opgeslagen.")
        context = get_context("FullstackDeveloper")
        print(f"Opgehaalde context: {context}")

    def handle_fullstack_development_requested(self, event):
        logger.info(f"Fullstack development requested: {event}")
        story = event.get("story", "User Authentication")
        self.implement_story()

    async def handle_fullstack_development_completed(self, event):
        logger.info(f"Fullstack development completed: {event}")
        
        # Evaluate policy
        try:
            allowed = await self.policy_engine.evaluate_policy("fullstack_development", event)
            logger.info(f"Policy evaluation result: {allowed}")
        except Exception as e:
            logger.error(f"Policy evaluation failed: {e}")

    def run(self):
        def sync_handler(event):
            asyncio.run(self.handle_fullstack_development_completed(event))
        
        subscribe("fullstack_development_completed", sync_handler)
        subscribe("fullstack_development_requested", self.handle_fullstack_development_requested)
        
        logger.info("FullstackDeveloperAgent ready and listening for events...")
        self.collaborate_example()

    # --- ORIGINELE FUNCTIONALITEIT BEHOUDEN ---
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
        
        # Log performance metric
        self.monitor._record_metric("FullstackDeveloper", MetricType.SUCCESS_RATE, 95, "%")
        
        # Add to history
        dev_entry = f"{datetime.now().isoformat()}: User Authentication story implemented"
        self.development_history.append(dev_entry)
        self._save_development_history()

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
        
        # Log performance metric
        self.monitor._record_metric("FullstackDeveloper", MetricType.SUCCESS_RATE, 90, "%")

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
        
        # Log performance metric
        self.monitor._record_metric("FullstackDeveloper", MetricType.SUCCESS_RATE, 95, "%")
        
        # Add to history
        dev_entry = f"{datetime.now().isoformat()}: Frontend Dashboard generated with 5 components"
        self.development_history.append(dev_entry)
        self._save_development_history()

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

def main():
    parser = argparse.ArgumentParser(description="FullstackDeveloper Agent CLI")
    parser.add_argument("command", nargs="?", default="help", 
                       choices=["help", "implement-story", "build-api", "build-frontend", "build-shadcn-component",
                               "write-tests", "show-development-history", "show-performance", "show-best-practices", 
                               "show-changelog", "export-report", "test", "collaborate", "run", "integrate-service",
                               "ci-cd", "dev-log", "review", "refactor", "security-check", "blockers", "api-contract",
                               "component-doc", "performance-profile", "a11y-check", "feature-toggle", "monitoring-setup",
                               "release-notes", "devops-handover", "tech-debt"])
    parser.add_argument("--name", default="User Authentication", help="Story/Component name")
    parser.add_argument("--format", choices=["md", "json"], default="md", help="Export format")
    
    args = parser.parse_args()
    
    agent = FullstackDeveloperAgent()
    
    if args.command == "help":
        agent.show_help()
    elif args.command == "implement-story":
        agent.implement_story()
    elif args.command == "build-api":
        agent.build_api()
    elif args.command == "build-frontend":
        agent.build_frontend()
    elif args.command == "build-shadcn-component":
        agent.build_shadcn_component(args.name)
    elif args.command == "write-tests":
        agent.write_tests()
    elif args.command == "show-development-history":
        agent.show_development_history()
    elif args.command == "show-performance":
        agent.show_performance()
    elif args.command == "show-best-practices":
        agent.show_resource("best-practices")
    elif args.command == "show-changelog":
        agent.show_resource("changelog")
    elif args.command == "export-report":
        agent.export_report(args.format)
    elif args.command == "test":
        agent.test_resource_completeness()
    elif args.command == "collaborate":
        agent.collaborate_example()
    elif args.command == "run":
        agent.run()
    elif args.command == "integrate-service":
        agent.integrate_service()
    elif args.command == "ci-cd":
        agent.ci_cd()
    elif args.command == "dev-log":
        agent.dev_log()
    elif args.command == "review":
        agent.review()
    elif args.command == "refactor":
        agent.refactor()
    elif args.command == "security-check":
        agent.security_check()
    elif args.command == "blockers":
        agent.blockers()
    elif args.command == "api-contract":
        agent.api_contract()
    elif args.command == "component-doc":
        agent.component_doc()
    elif args.command == "performance-profile":
        agent.performance_profile()
    elif args.command == "a11y-check":
        agent.a11y_check()
    elif args.command == "feature-toggle":
        agent.feature_toggle()
    elif args.command == "monitoring-setup":
        agent.monitoring_setup()
    elif args.command == "release-notes":
        agent.release_notes()
    elif args.command == "devops-handover":
        agent.devops_handover()
    elif args.command == "tech-debt":
        agent.tech_debt()

if __name__ == "__main__":
    main()
