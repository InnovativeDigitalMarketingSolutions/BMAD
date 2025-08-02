"""
Workflow Store

This module provides persistent storage for workflows and executions using PostgreSQL and Redis.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import json
import asyncpg
import redis.asyncio as redis
from pydantic import BaseModel

from .workflow_manager import Workflow, WorkflowExecution, WorkflowStatus, WorkflowType

logger = logging.getLogger(__name__)

class WorkflowStore:
    """Persistent storage for workflows and executions using PostgreSQL and Redis."""
    
    def __init__(self, postgres_url: str, redis_url: str):
        self.postgres_url = postgres_url
        self.redis_url = redis_url
        self.pg_pool: Optional[asyncpg.Pool] = None
        self.redis_client: Optional[redis.Redis] = None
        
    async def connect(self):
        """Initialize database connections."""
        try:
            # PostgreSQL connection
            self.pg_pool = await asyncpg.create_pool(
                self.postgres_url,
                min_size=1,
                max_size=10
            )
            
            # Redis connection
            self.redis_client = redis.from_url(
                self.redis_url,
                decode_responses=True
            )
            await self.redis_client.ping()
            
            # Create tables if they don't exist
            await self._create_tables()
            
            logger.info("Workflow store connections established")
            
        except Exception as e:
            logger.error(f"Failed to connect to workflow store: {e}")
            raise
            
    async def disconnect(self):
        """Close database connections."""
        if self.pg_pool:
            await self.pg_pool.close()
        if self.redis_client:
            await self.redis_client.close()
        logger.info("Workflow store connections closed")
        
    async def _create_tables(self):
        """Create database tables if they don't exist."""
        async with self.pg_pool.acquire() as conn:
            # Workflows table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS workflows (
                    id VARCHAR(255) PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    workflow_type VARCHAR(50) NOT NULL,
                    status VARCHAR(50) DEFAULT 'draft',
                    config JSONB DEFAULT '{}',
                    metadata JSONB DEFAULT '{}',
                    tags TEXT[] DEFAULT '{}',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    started_at TIMESTAMP WITH TIME ZONE,
                    completed_at TIMESTAMP WITH TIME ZONE,
                    execution_count INTEGER DEFAULT 0,
                    success_count INTEGER DEFAULT 0,
                    failure_count INTEGER DEFAULT 0,
                    average_duration_seconds DECIMAL(10,2) DEFAULT 0.0
                )
            """)
            
            # Workflow steps table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS workflow_steps (
                    id VARCHAR(255) PRIMARY KEY,
                    workflow_id VARCHAR(255) REFERENCES workflows(id) ON DELETE CASCADE,
                    name VARCHAR(255) NOT NULL,
                    step_type VARCHAR(100) NOT NULL,
                    agent_id VARCHAR(255),
                    config JSONB DEFAULT '{}',
                    dependencies TEXT[] DEFAULT '{}',
                    timeout_seconds INTEGER DEFAULT 300,
                    retry_count INTEGER DEFAULT 3,
                    status VARCHAR(50) DEFAULT 'pending',
                    result JSONB,
                    error TEXT,
                    started_at TIMESTAMP WITH TIME ZONE,
                    completed_at TIMESTAMP WITH TIME ZONE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
            
            # Workflow executions table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS workflow_executions (
                    id VARCHAR(255) PRIMARY KEY,
                    workflow_id VARCHAR(255) REFERENCES workflows(id) ON DELETE CASCADE,
                    status VARCHAR(50) DEFAULT 'pending',
                    input_data JSONB DEFAULT '{}',
                    output_data JSONB,
                    step_results JSONB DEFAULT '{}',
                    started_at TIMESTAMP WITH TIME ZONE,
                    completed_at TIMESTAMP WITH TIME ZONE,
                    error TEXT,
                    duration_seconds DECIMAL(10,2),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
            
            # Create indexes
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_workflows_type ON workflows(workflow_type);
                CREATE INDEX IF NOT EXISTS idx_workflows_status ON workflows(status);
                CREATE INDEX IF NOT EXISTS idx_workflows_updated_at ON workflows(updated_at);
                CREATE INDEX IF NOT EXISTS idx_workflow_steps_workflow_id ON workflow_steps(workflow_id);
                CREATE INDEX IF NOT EXISTS idx_workflow_executions_workflow_id ON workflow_executions(workflow_id);
                CREATE INDEX IF NOT EXISTS idx_workflow_executions_status ON workflow_executions(status);
                CREATE INDEX IF NOT EXISTS idx_workflow_executions_started_at ON workflow_executions(started_at);
            """)
            
    async def save_workflow(self, workflow: Workflow) -> bool:
        """Save workflow to database and cache."""
        try:
            # Save workflow to PostgreSQL
            async with self.pg_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO workflows (id, name, description, workflow_type, status, config, 
                                        metadata, tags, created_at, updated_at, started_at, completed_at,
                                        execution_count, success_count, failure_count, average_duration_seconds)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16)
                    ON CONFLICT (id) DO UPDATE SET
                        name = EXCLUDED.name,
                        description = EXCLUDED.description,
                        workflow_type = EXCLUDED.workflow_type,
                        status = EXCLUDED.status,
                        config = EXCLUDED.config,
                        metadata = EXCLUDED.metadata,
                        tags = EXCLUDED.tags,
                        updated_at = EXCLUDED.updated_at,
                        started_at = EXCLUDED.started_at,
                        completed_at = EXCLUDED.completed_at,
                        execution_count = EXCLUDED.execution_count,
                        success_count = EXCLUDED.success_count,
                        failure_count = EXCLUDED.failure_count,
                        average_duration_seconds = EXCLUDED.average_duration_seconds
                """, workflow.id, workflow.name, workflow.description, workflow.workflow_type.value,
                     workflow.status.value, json.dumps(workflow.config), json.dumps(workflow.metadata),
                     workflow.tags, workflow.created_at, workflow.updated_at, workflow.started_at,
                     workflow.completed_at, workflow.execution_count, workflow.success_count,
                     workflow.failure_count, workflow.average_duration_seconds)
                
                # Save workflow steps
                for step in workflow.steps:
                    await conn.execute("""
                        INSERT INTO workflow_steps (id, workflow_id, name, step_type, agent_id, config,
                                                  dependencies, timeout_seconds, retry_count, status,
                                                  result, error, started_at, completed_at, created_at, updated_at)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16)
                        ON CONFLICT (id) DO UPDATE SET
                            name = EXCLUDED.name,
                            step_type = EXCLUDED.step_type,
                            agent_id = EXCLUDED.agent_id,
                            config = EXCLUDED.config,
                            dependencies = EXCLUDED.dependencies,
                            timeout_seconds = EXCLUDED.timeout_seconds,
                            retry_count = EXCLUDED.retry_count,
                            status = EXCLUDED.status,
                            result = EXCLUDED.result,
                            error = EXCLUDED.error,
                            started_at = EXCLUDED.started_at,
                            completed_at = EXCLUDED.completed_at,
                            updated_at = EXCLUDED.updated_at
                    """, step.id, workflow.id, step.name, step.step_type, step.agent_id,
                         json.dumps(step.config), step.dependencies, step.timeout_seconds,
                         step.retry_count, step.status, json.dumps(step.result) if step.result else None,
                         step.error, step.started_at, step.completed_at, step.started_at or datetime.now(timezone.utc),
                         step.completed_at or datetime.now(timezone.utc))
                
            # Cache in Redis
            cache_key = f"workflow:{workflow.id}"
            await self.redis_client.setex(
                cache_key,
                3600,  # 1 hour TTL
                json.dumps(workflow.dict())
            )
            
            logger.debug(f"Saved workflow: {workflow.id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save workflow {workflow.id}: {e}")
            return False
            
    async def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """Get workflow from cache or database."""
        try:
            # Try cache first
            cache_key = f"workflow:{workflow_id}"
            cached_data = await self.redis_client.get(cache_key)
            
            if cached_data:
                workflow_data = json.loads(cached_data)
                return Workflow(**workflow_data)
                
            # Get from database
            async with self.pg_pool.acquire() as conn:
                # Get workflow
                workflow_row = await conn.fetchrow("""
                    SELECT id, name, description, workflow_type, status, config, metadata, tags,
                           created_at, updated_at, started_at, completed_at, execution_count,
                           success_count, failure_count, average_duration_seconds
                    FROM workflows WHERE id = $1
                """, workflow_id)
                
                if not workflow_row:
                    return None
                    
                # Get workflow steps
                step_rows = await conn.fetch("""
                    SELECT id, name, step_type, agent_id, config, dependencies, timeout_seconds,
                           retry_count, status, result, error, started_at, completed_at
                    FROM workflow_steps WHERE workflow_id = $1
                    ORDER BY created_at ASC
                """, workflow_id)
                
                # Convert to Workflow object
                workflow_data = dict(workflow_row)
                workflow_data['workflow_type'] = WorkflowType(workflow_data['workflow_type'])
                workflow_data['status'] = WorkflowStatus(workflow_data['status'])
                workflow_data['config'] = json.loads(workflow_data['config'])
                workflow_data['metadata'] = json.loads(workflow_data['metadata'])
                
                # Convert steps
                steps = []
                for step_row in step_rows:
                    step_data = dict(step_row)
                    step_data['config'] = json.loads(step_data['config'])
                    step_data['result'] = json.loads(step_data['result']) if step_data['result'] else None
                    steps.append(step_data)
                    
                workflow_data['steps'] = steps
                workflow = Workflow(**workflow_data)
                
                # Cache the result
                await self.redis_client.setex(
                    cache_key,
                    3600,
                    json.dumps(workflow.dict())
                )
                
                return workflow
                
        except Exception as e:
            logger.error(f"Failed to get workflow {workflow_id}: {e}")
            return None
            
    async def delete_workflow(self, workflow_id: str) -> bool:
        """Delete workflow from database and cache."""
        try:
            # Delete from database (cascade will handle steps)
            async with self.pg_pool.acquire() as conn:
                result = await conn.execute(
                    "DELETE FROM workflows WHERE id = $1",
                    workflow_id
                )
                
            # Remove from cache
            cache_key = f"workflow:{workflow_id}"
            await self.redis_client.delete(cache_key)
            
            success = result != "DELETE 0"
            if success:
                logger.debug(f"Deleted workflow: {workflow_id}")
            return success
            
        except Exception as e:
            logger.error(f"Failed to delete workflow {workflow_id}: {e}")
            return False
            
    async def list_workflows(self, workflow_type: Optional[WorkflowType] = None,
                           status: Optional[WorkflowStatus] = None,
                           tags: Optional[List[str]] = None,
                           limit: int = 100) -> List[Workflow]:
        """List workflows from database."""
        try:
            query = """
                SELECT id, name, description, workflow_type, status, config, metadata, tags,
                       created_at, updated_at, started_at, completed_at, execution_count,
                       success_count, failure_count, average_duration_seconds
                FROM workflows
            """
            params = []
            conditions = []
            
            if workflow_type:
                conditions.append("workflow_type = $1")
                params.append(workflow_type.value)
                
            if status:
                conditions.append("status = $" + str(len(params) + 1))
                params.append(status.value)
                
            if tags:
                tag_conditions = []
                for i, tag in enumerate(tags):
                    param_idx = len(params) + 1
                    tag_conditions.append(f"${param_idx} = ANY(tags)")
                    params.append(tag)
                conditions.append(f"({' OR '.join(tag_conditions)})")
                
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
                
            query += " ORDER BY updated_at DESC LIMIT $" + str(len(params) + 1)
            params.append(limit)
            
            async with self.pg_pool.acquire() as conn:
                rows = await conn.fetch(query, *params)
                
            workflows = []
            for row in rows:
                workflow_data = dict(row)
                workflow_data['workflow_type'] = WorkflowType(workflow_data['workflow_type'])
                workflow_data['status'] = WorkflowStatus(workflow_data['status'])
                workflow_data['config'] = json.loads(workflow_data['config'])
                workflow_data['metadata'] = json.loads(workflow_data['metadata'])
                workflow_data['steps'] = []  # Don't load steps for list view
                workflows.append(Workflow(**workflow_data))
                
            return workflows
            
        except Exception as e:
            logger.error(f"Failed to list workflows: {e}")
            return []
            
    async def save_execution(self, execution: WorkflowExecution) -> bool:
        """Save workflow execution to database."""
        try:
            async with self.pg_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO workflow_executions (id, workflow_id, status, input_data, output_data,
                                                   step_results, started_at, completed_at, error, duration_seconds)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                    ON CONFLICT (id) DO UPDATE SET
                        status = EXCLUDED.status,
                        input_data = EXCLUDED.input_data,
                        output_data = EXCLUDED.output_data,
                        step_results = EXCLUDED.step_results,
                        started_at = EXCLUDED.started_at,
                        completed_at = EXCLUDED.completed_at,
                        error = EXCLUDED.error,
                        duration_seconds = EXCLUDED.duration_seconds,
                        updated_at = NOW()
                """, execution.id, execution.workflow_id, execution.status.value,
                     json.dumps(execution.input_data), json.dumps(execution.output_data) if execution.output_data else None,
                     json.dumps(execution.step_results), execution.started_at, execution.completed_at,
                     execution.error, execution.duration_seconds)
                
            logger.debug(f"Saved execution: {execution.id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save execution {execution.id}: {e}")
            return False
            
    async def get_execution(self, execution_id: str) -> Optional[WorkflowExecution]:
        """Get workflow execution from database."""
        try:
            async with self.pg_pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT id, workflow_id, status, input_data, output_data, step_results,
                           started_at, completed_at, error, duration_seconds, created_at, updated_at
                    FROM workflow_executions WHERE id = $1
                """, execution_id)
                
                if not row:
                    return None
                    
                execution_data = dict(row)
                execution_data['status'] = WorkflowStatus(execution_data['status'])
                execution_data['input_data'] = json.loads(execution_data['input_data'])
                execution_data['output_data'] = json.loads(execution_data['output_data']) if execution_data['output_data'] else None
                execution_data['step_results'] = json.loads(execution_data['step_results'])
                
                return WorkflowExecution(**execution_data)
                
        except Exception as e:
            logger.error(f"Failed to get execution {execution_id}: {e}")
            return None
            
    async def list_executions(self, workflow_id: Optional[str] = None,
                            status: Optional[WorkflowStatus] = None,
                            limit: int = 100) -> List[WorkflowExecution]:
        """List workflow executions from database."""
        try:
            query = """
                SELECT id, workflow_id, status, input_data, output_data, step_results,
                       started_at, completed_at, error, duration_seconds, created_at, updated_at
                FROM workflow_executions
            """
            params = []
            conditions = []
            
            if workflow_id:
                conditions.append("workflow_id = $1")
                params.append(workflow_id)
                
            if status:
                conditions.append("status = $" + str(len(params) + 1))
                params.append(status.value)
                
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
                
            query += " ORDER BY started_at DESC LIMIT $" + str(len(params) + 1)
            params.append(limit)
            
            async with self.pg_pool.acquire() as conn:
                rows = await conn.fetch(query, *params)
                
            executions = []
            for row in rows:
                execution_data = dict(row)
                execution_data['status'] = WorkflowStatus(execution_data['status'])
                execution_data['input_data'] = json.loads(execution_data['input_data'])
                execution_data['output_data'] = json.loads(execution_data['output_data']) if execution_data['output_data'] else None
                execution_data['step_results'] = json.loads(execution_data['step_results'])
                executions.append(WorkflowExecution(**execution_data))
                
            return executions
            
        except Exception as e:
            logger.error(f"Failed to list executions: {e}")
            return []
            
    async def health_check(self) -> Dict[str, Any]:
        """Check store health."""
        try:
            # Test PostgreSQL
            async with self.pg_pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
                
            # Test Redis
            await self.redis_client.ping()
            
            return {
                "status": "healthy",
                "postgresql": "connected",
                "redis": "connected"
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            } 