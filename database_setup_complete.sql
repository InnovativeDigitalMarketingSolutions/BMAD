-- =====================================================
-- BMAD System Complete Database Setup
-- =====================================================
-- This script sets up all databases for BMAD microservices
-- Run this in your Supabase SQL Editor

-- =====================================================
-- 1. AUTHENTICATION SERVICE DATABASE
-- =====================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create auth_service schema
CREATE SCHEMA IF NOT EXISTS auth_service;

-- Users table
CREATE TABLE IF NOT EXISTS auth_service.users (
    id VARCHAR(255) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(255) UNIQUE,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    password_hash VARCHAR(255),
    status VARCHAR(50) DEFAULT 'active',
    email_verified BOOLEAN DEFAULT FALSE,
    mfa_enabled BOOLEAN DEFAULT FALSE,
    mfa_secret VARCHAR(255),
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    user_metadata JSONB DEFAULT '{}',
    auth0_id VARCHAR(255) UNIQUE
);

-- Sessions table
CREATE TABLE IF NOT EXISTS auth_service.sessions (
    id VARCHAR(255) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    user_id VARCHAR(255) REFERENCES auth_service.users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL,
    refresh_token_hash VARCHAR(255),
    device_info JSONB DEFAULT '{}',
    ip_address INET,
    user_agent TEXT,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_used_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- Roles table
CREATE TABLE IF NOT EXISTS auth_service.roles (
    id VARCHAR(255) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    permissions TEXT[] DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User roles table
CREATE TABLE IF NOT EXISTS auth_service.user_roles (
    user_id VARCHAR(255) REFERENCES auth_service.users(id) ON DELETE CASCADE,
    role_id VARCHAR(255) REFERENCES auth_service.roles(id) ON DELETE CASCADE,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    assigned_by VARCHAR(255),
    PRIMARY KEY (user_id, role_id)
);

-- Audit logs table
CREATE TABLE IF NOT EXISTS auth_service.audit_logs (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) REFERENCES auth_service.users(id) ON DELETE SET NULL,
    action VARCHAR(255) NOT NULL,
    resource_type VARCHAR(255),
    resource_id VARCHAR(255),
    details JSONB DEFAULT '{}',
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Password reset tokens table
CREATE TABLE IF NOT EXISTS auth_service.password_reset_tokens (
    id VARCHAR(255) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    user_id VARCHAR(255) REFERENCES auth_service.users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    used_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- MFA backup codes table
CREATE TABLE IF NOT EXISTS auth_service.mfa_backup_codes (
    id VARCHAR(255) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    user_id VARCHAR(255) REFERENCES auth_service.users(id) ON DELETE CASCADE,
    code_hash VARCHAR(255) NOT NULL,
    used_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for auth service
CREATE INDEX IF NOT EXISTS idx_auth_users_email ON auth_service.users(email);
CREATE INDEX IF NOT EXISTS idx_auth_users_username ON auth_service.users(username);
CREATE INDEX IF NOT EXISTS idx_auth_users_auth0_id ON auth_service.users(auth0_id);
CREATE INDEX IF NOT EXISTS idx_auth_sessions_user_id ON auth_service.sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_auth_sessions_token_hash ON auth_service.sessions(token_hash);
CREATE INDEX IF NOT EXISTS idx_auth_sessions_expires_at ON auth_service.sessions(expires_at);
CREATE INDEX IF NOT EXISTS idx_auth_audit_logs_user_id ON auth_service.audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_auth_audit_logs_action ON auth_service.audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_auth_password_reset_tokens_user_id ON auth_service.password_reset_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_auth_password_reset_tokens_expires_at ON auth_service.password_reset_tokens(expires_at);
CREATE INDEX IF NOT EXISTS idx_auth_mfa_backup_codes_user_id ON auth_service.mfa_backup_codes(user_id);

-- =====================================================
-- 2. NOTIFICATION SERVICE DATABASE
-- =====================================================

-- Create notification_service schema
CREATE SCHEMA IF NOT EXISTS notification_service;

-- Notifications table
CREATE TABLE IF NOT EXISTS notification_service.notifications (
    id VARCHAR(255) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    user_id VARCHAR(255),
    channel VARCHAR(50) NOT NULL,
    template_id VARCHAR(255),
    subject VARCHAR(500),
    content TEXT NOT NULL,
    recipient VARCHAR(255) NOT NULL,
    metadata JSONB DEFAULT '{}',
    status VARCHAR(50) DEFAULT 'pending',
    scheduled_at TIMESTAMP WITH TIME ZONE,
    sent_at TIMESTAMP WITH TIME ZONE,
    delivered_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Templates table
CREATE TABLE IF NOT EXISTS notification_service.templates (
    id VARCHAR(255) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    channel VARCHAR(50) NOT NULL,
    subject_template TEXT,
    content_template TEXT NOT NULL,
    variables JSONB DEFAULT '{}',
    language VARCHAR(10) DEFAULT 'en',
    version INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Delivery logs table
CREATE TABLE IF NOT EXISTS notification_service.delivery_logs (
    id VARCHAR(255) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    notification_id VARCHAR(255) REFERENCES notification_service.notifications(id) ON DELETE CASCADE,
    channel VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    delivered_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Channel configs table
CREATE TABLE IF NOT EXISTS notification_service.channel_configs (
    id VARCHAR(255) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    channel VARCHAR(50) UNIQUE NOT NULL,
    config JSONB NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    rate_limit_per_minute INTEGER DEFAULT 60,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for notification service
CREATE INDEX IF NOT EXISTS idx_notif_user_id ON notification_service.notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notif_channel ON notification_service.notifications(channel);
CREATE INDEX IF NOT EXISTS idx_notif_status ON notification_service.notifications(status);
CREATE INDEX IF NOT EXISTS idx_notif_created_at ON notification_service.notifications(created_at);
CREATE INDEX IF NOT EXISTS idx_notif_scheduled_at ON notification_service.notifications(scheduled_at);
CREATE INDEX IF NOT EXISTS idx_notif_templates_channel ON notification_service.templates(channel);
CREATE INDEX IF NOT EXISTS idx_notif_templates_language ON notification_service.templates(language);
CREATE INDEX IF NOT EXISTS idx_notif_templates_is_active ON notification_service.templates(is_active);
CREATE INDEX IF NOT EXISTS idx_notif_delivery_logs_notification_id ON notification_service.delivery_logs(notification_id);
CREATE INDEX IF NOT EXISTS idx_notif_delivery_logs_channel ON notification_service.delivery_logs(channel);
CREATE INDEX IF NOT EXISTS idx_notif_delivery_logs_status ON notification_service.delivery_logs(status);
CREATE INDEX IF NOT EXISTS idx_notif_delivery_logs_created_at ON notification_service.delivery_logs(created_at);

-- =====================================================
-- 3. AGENT SERVICE DATABASE
-- =====================================================

-- Create agent_service schema
CREATE SCHEMA IF NOT EXISTS agent_service;

-- Agents table
CREATE TABLE IF NOT EXISTS agent_service.agents (
    id VARCHAR(255) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    agent_type VARCHAR(100) NOT NULL,
    status VARCHAR(50) DEFAULT 'idle',
    config JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_execution TIMESTAMP WITH TIME ZONE,
    execution_count INTEGER DEFAULT 0
);

-- Agent executions table
CREATE TABLE IF NOT EXISTS agent_service.executions (
    id VARCHAR(255) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    agent_id VARCHAR(255) REFERENCES agent_service.agents(id) ON DELETE CASCADE,
    status VARCHAR(50) DEFAULT 'pending',
    input_data JSONB DEFAULT '{}',
    output_data JSONB DEFAULT '{}',
    error_message TEXT,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for agent service
CREATE INDEX IF NOT EXISTS idx_agent_name ON agent_service.agents(name);
CREATE INDEX IF NOT EXISTS idx_agent_type ON agent_service.agents(agent_type);
CREATE INDEX IF NOT EXISTS idx_agent_status ON agent_service.agents(status);
CREATE INDEX IF NOT EXISTS idx_agent_executions_agent_id ON agent_service.executions(agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_executions_status ON agent_service.executions(status);
CREATE INDEX IF NOT EXISTS idx_agent_executions_created_at ON agent_service.executions(created_at);

-- =====================================================
-- 4. WORKFLOW SERVICE DATABASE
-- =====================================================

-- Create workflow_service schema
CREATE SCHEMA IF NOT EXISTS workflow_service;

-- Workflows table
CREATE TABLE IF NOT EXISTS workflow_service.workflows (
    id VARCHAR(255) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
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
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Workflow steps table
CREATE TABLE IF NOT EXISTS workflow_service.workflow_steps (
    id VARCHAR(255) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    workflow_id VARCHAR(255) REFERENCES workflow_service.workflows(id) ON DELETE CASCADE,
    step_name VARCHAR(255) NOT NULL,
    step_type VARCHAR(100) NOT NULL,
    order_index INTEGER NOT NULL,
    config JSONB DEFAULT '{}',
    dependencies TEXT[] DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Workflow executions table
CREATE TABLE IF NOT EXISTS workflow_service.executions (
    id VARCHAR(255) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    workflow_id VARCHAR(255) REFERENCES workflow_service.workflows(id) ON DELETE CASCADE,
    status VARCHAR(50) DEFAULT 'pending',
    input_data JSONB DEFAULT '{}',
    output_data JSONB DEFAULT '{}',
    current_step VARCHAR(255),
    error_message TEXT,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for workflow service
CREATE INDEX IF NOT EXISTS idx_workflow_name ON workflow_service.workflows(name);
CREATE INDEX IF NOT EXISTS idx_workflow_type ON workflow_service.workflows(workflow_type);
CREATE INDEX IF NOT EXISTS idx_workflow_status ON workflow_service.workflows(status);
CREATE INDEX IF NOT EXISTS idx_workflow_steps_workflow_id ON workflow_service.workflow_steps(workflow_id);
CREATE INDEX IF NOT EXISTS idx_workflow_steps_order_index ON workflow_service.workflow_steps(order_index);
CREATE INDEX IF NOT EXISTS idx_workflow_executions_workflow_id ON workflow_service.executions(workflow_id);
CREATE INDEX IF NOT EXISTS idx_workflow_executions_status ON workflow_service.executions(status);

-- =====================================================
-- 5. CONTEXT SERVICE DATABASE
-- =====================================================

-- Create context_service schema
CREATE SCHEMA IF NOT EXISTS context_service;

-- Contexts table
CREATE TABLE IF NOT EXISTS context_service.contexts (
    id VARCHAR(255) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    user_id VARCHAR(255),
    context_type VARCHAR(100) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    data JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Context versions table
CREATE TABLE IF NOT EXISTS context_service.context_versions (
    id VARCHAR(255) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    context_id VARCHAR(255) REFERENCES context_service.contexts(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    data JSONB NOT NULL,
    change_description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for context service
CREATE INDEX IF NOT EXISTS idx_context_user_id ON context_service.contexts(user_id);
CREATE INDEX IF NOT EXISTS idx_context_type ON context_service.contexts(context_type);
CREATE INDEX IF NOT EXISTS idx_context_is_active ON context_service.contexts(is_active);
CREATE INDEX IF NOT EXISTS idx_context_versions_context_id ON context_service.context_versions(context_id);
CREATE INDEX IF NOT EXISTS idx_context_versions_version_number ON context_service.context_versions(version_number);

-- =====================================================
-- 6. INTEGRATION SERVICE DATABASE
-- =====================================================

-- Create integration_service schema
CREATE SCHEMA IF NOT EXISTS integration_service;

-- Integrations table
CREATE TABLE IF NOT EXISTS integration_service.integrations (
    id VARCHAR(255) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    name VARCHAR(255) NOT NULL,
    integration_type VARCHAR(100) NOT NULL,
    provider VARCHAR(100) NOT NULL,
    config JSONB NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    is_enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Integration logs table
CREATE TABLE IF NOT EXISTS integration_service.integration_logs (
    id VARCHAR(255) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    integration_id VARCHAR(255) REFERENCES integration_service.integrations(id) ON DELETE CASCADE,
    action VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL,
    request_data JSONB DEFAULT '{}',
    response_data JSONB DEFAULT '{}',
    error_message TEXT,
    duration_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for integration service
CREATE INDEX IF NOT EXISTS idx_integration_name ON integration_service.integrations(name);
CREATE INDEX IF NOT EXISTS idx_integration_type ON integration_service.integrations(integration_type);
CREATE INDEX IF NOT EXISTS idx_integration_provider ON integration_service.integrations(provider);
CREATE INDEX IF NOT EXISTS idx_integration_status ON integration_service.integrations(status);
CREATE INDEX IF NOT EXISTS idx_integration_logs_integration_id ON integration_service.integration_logs(integration_id);
CREATE INDEX IF NOT EXISTS idx_integration_logs_status ON integration_service.integration_logs(status);
CREATE INDEX IF NOT EXISTS idx_integration_logs_created_at ON integration_service.integration_logs(created_at);

-- =====================================================
-- 7. COMMON FUNCTIONS AND TRIGGERS
-- =====================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for all tables with updated_at
CREATE TRIGGER update_auth_users_updated_at BEFORE UPDATE ON auth_service.users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_auth_roles_updated_at BEFORE UPDATE ON auth_service.roles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_notif_notifications_updated_at BEFORE UPDATE ON notification_service.notifications
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_notif_templates_updated_at BEFORE UPDATE ON notification_service.templates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_notif_channel_configs_updated_at BEFORE UPDATE ON notification_service.channel_configs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_agent_agents_updated_at BEFORE UPDATE ON agent_service.agents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_workflow_workflows_updated_at BEFORE UPDATE ON workflow_service.workflows
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_context_contexts_updated_at BEFORE UPDATE ON context_service.contexts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_integration_integrations_updated_at BEFORE UPDATE ON integration_service.integrations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- 8. CLEANUP FUNCTIONS
-- =====================================================

-- Cleanup expired sessions
CREATE OR REPLACE FUNCTION auth_service.cleanup_expired_sessions()
RETURNS void AS $$
BEGIN
    DELETE FROM auth_service.sessions 
    WHERE expires_at < NOW();
END;
$$ LANGUAGE plpgsql;

-- Cleanup expired password reset tokens
CREATE OR REPLACE FUNCTION auth_service.cleanup_expired_password_reset_tokens()
RETURNS void AS $$
BEGIN
    DELETE FROM auth_service.password_reset_tokens 
    WHERE expires_at < NOW();
END;
$$ LANGUAGE plpgsql;

-- Cleanup old delivery logs
CREATE OR REPLACE FUNCTION notification_service.cleanup_old_delivery_logs()
RETURNS void AS $$
BEGIN
    DELETE FROM notification_service.delivery_logs 
    WHERE created_at < NOW() - INTERVAL '90 days';
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- 9. DEFAULT DATA INSERTION
-- =====================================================

-- Insert default roles
INSERT INTO auth_service.roles (name, description, permissions) VALUES
('admin', 'System Administrator', ARRAY['*']),
('user', 'Regular User', ARRAY['read:own', 'write:own']),
('manager', 'Team Manager', ARRAY['read:team', 'write:team', 'read:own', 'write:own'])
ON CONFLICT (name) DO NOTHING;

-- Insert default admin user (password: admin123)
INSERT INTO auth_service.users (email, username, first_name, last_name, password_hash, status, email_verified) VALUES
('admin@bmad.com', 'admin', 'System', 'Administrator', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.s5u.G', 'active', true)
ON CONFLICT (email) DO NOTHING;

-- Assign admin role to admin user
INSERT INTO auth_service.user_roles (user_id, role_id)
SELECT u.id, r.id 
FROM auth_service.users u, auth_service.roles r 
WHERE u.email = 'admin@bmad.com' AND r.name = 'admin'
ON CONFLICT DO NOTHING;

-- Insert default channel configurations
INSERT INTO notification_service.channel_configs (channel, config, rate_limit_per_minute) VALUES
('email', '{"provider": "sendgrid", "from_email": "noreply@bmad.com", "from_name": "BMAD System"}', 60),
('sms', '{"provider": "twilio", "from_number": "+1234567890"}', 30),
('slack', '{"webhook_url": "https://hooks.slack.com/services/your-webhook"}', 100),
('webhook', '{"timeout": 30, "retry_attempts": 3}', 200)
ON CONFLICT (channel) DO NOTHING;

-- Insert default notification templates
INSERT INTO notification_service.templates (name, description, channel, subject_template, content_template, variables) VALUES
('welcome_email', 'Welcome email for new users', 'email', 'Welcome to BMAD, {{user_name}}!', 
'Hi {{user_name}},\n\nWelcome to BMAD! We''re excited to have you on board.\n\nBest regards,\nThe BMAD Team', 
'{"user_name": "string"}'),
('password_reset', 'Password reset email template', 'email', 'Password Reset Request', 
'Hi {{user_name}},\n\nYou requested a password reset. Click the link below to reset your password:\n\n{{reset_link}}\n\nIf you didn''t request this, please ignore this email.\n\nBest regards,\nThe BMAD Team', 
'{"user_name": "string", "reset_link": "string"}'),
('notification_alert', 'General notification template', 'slack', NULL, 
'🔔 *{{title}}*\n\n{{message}}\n\n*User:* {{user_name}}\n*Time:* {{timestamp}}', 
'{"title": "string", "message": "string", "user_name": "string", "timestamp": "string"}'),
('sms_alert', 'SMS alert template', 'sms', NULL, 
'BMAD Alert: {{message}}', 
'{"message": "string"}')
ON CONFLICT DO NOTHING;

-- Insert default integrations
INSERT INTO integration_service.integrations (name, integration_type, provider, config, status) VALUES
('auth0', 'authentication', 'auth0', '{"domain": "your-domain.auth0.com", "client_id": "your-client-id", "client_secret": "your-client-secret"}', 'active'),
('postgresql', 'database', 'postgresql', '{"host": "localhost", "port": 5432, "database": "bmad", "username": "bmad_user"}', 'active'),
('redis', 'cache', 'redis', '{"host": "localhost", "port": 6379, "database": 0}', 'active'),
('sendgrid', 'email', 'sendgrid', '{"api_key": "your-sendgrid-api-key", "from_email": "noreply@bmad.com"}', 'active'),
('twilio', 'sms', 'twilio', '{"account_sid": "your-account-sid", "auth_token": "your-auth-token", "from_number": "+1234567890"}', 'active')
ON CONFLICT DO NOTHING;

-- =====================================================
-- 10. STATISTICS FUNCTIONS
-- =====================================================

-- Get notification statistics
CREATE OR REPLACE FUNCTION notification_service.get_notification_stats(
    p_user_id VARCHAR DEFAULT NULL,
    p_channel VARCHAR DEFAULT NULL,
    p_start_date TIMESTAMP WITH TIME ZONE DEFAULT NULL,
    p_end_date TIMESTAMP WITH TIME ZONE DEFAULT NULL
)
RETURNS TABLE(
    total_notifications BIGINT,
    sent_notifications BIGINT,
    delivered_notifications BIGINT,
    failed_notifications BIGINT,
    success_rate NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*) as total_notifications,
        COUNT(CASE WHEN status = 'sent' THEN 1 END) as sent_notifications,
        COUNT(CASE WHEN status = 'delivered' THEN 1 END) as delivered_notifications,
        COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_notifications,
        ROUND(
            (COUNT(CASE WHEN status = 'delivered' THEN 1 END)::NUMERIC / COUNT(*)) * 100, 2
        ) as success_rate
    FROM notification_service.notifications
    WHERE (p_user_id IS NULL OR user_id = p_user_id)
        AND (p_channel IS NULL OR channel = p_channel)
        AND (p_start_date IS NULL OR created_at >= p_start_date)
        AND (p_end_date IS NULL OR created_at <= p_end_date);
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- 11. ROW LEVEL SECURITY (RLS) SETUP
-- =====================================================

-- Enable RLS on all tables
ALTER TABLE auth_service.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE auth_service.sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE auth_service.roles ENABLE ROW LEVEL SECURITY;
ALTER TABLE auth_service.user_roles ENABLE ROW LEVEL SECURITY;
ALTER TABLE auth_service.audit_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE auth_service.password_reset_tokens ENABLE ROW LEVEL SECURITY;
ALTER TABLE auth_service.mfa_backup_codes ENABLE ROW LEVEL SECURITY;

ALTER TABLE notification_service.notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE notification_service.templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE notification_service.delivery_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE notification_service.channel_configs ENABLE ROW LEVEL SECURITY;

ALTER TABLE agent_service.agents ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_service.executions ENABLE ROW LEVEL SECURITY;

ALTER TABLE workflow_service.workflows ENABLE ROW LEVEL SECURITY;
ALTER TABLE workflow_service.workflow_steps ENABLE ROW LEVEL SECURITY;
ALTER TABLE workflow_service.executions ENABLE ROW LEVEL SECURITY;

ALTER TABLE context_service.contexts ENABLE ROW LEVEL SECURITY;
ALTER TABLE context_service.context_versions ENABLE ROW LEVEL SECURITY;

ALTER TABLE integration_service.integrations ENABLE ROW LEVEL SECURITY;
ALTER TABLE integration_service.integration_logs ENABLE ROW LEVEL SECURITY;

-- =====================================================
-- 12. COMPLETION MESSAGE
-- =====================================================

-- This will show in the Supabase SQL Editor
SELECT 'BMAD Database Setup Complete!' as status,
       'All microservices databases have been created successfully.' as message,
       NOW() as completed_at; 