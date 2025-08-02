-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create notifications table
CREATE TABLE IF NOT EXISTS notifications (
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

-- Create templates table
CREATE TABLE IF NOT EXISTS templates (
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

-- Create delivery_logs table
CREATE TABLE IF NOT EXISTS delivery_logs (
    id VARCHAR(255) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    notification_id VARCHAR(255) REFERENCES notifications(id) ON DELETE CASCADE,
    channel VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    delivered_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create channel_configs table
CREATE TABLE IF NOT EXISTS channel_configs (
    id VARCHAR(255) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    channel VARCHAR(50) UNIQUE NOT NULL,
    config JSONB NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    rate_limit_per_minute INTEGER DEFAULT 60,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_channel ON notifications(channel);
CREATE INDEX IF NOT EXISTS idx_notifications_status ON notifications(status);
CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at);
CREATE INDEX IF NOT EXISTS idx_notifications_scheduled_at ON notifications(scheduled_at);

CREATE INDEX IF NOT EXISTS idx_templates_channel ON templates(channel);
CREATE INDEX IF NOT EXISTS idx_templates_language ON templates(language);
CREATE INDEX IF NOT EXISTS idx_templates_is_active ON templates(is_active);

CREATE INDEX IF NOT EXISTS idx_delivery_logs_notification_id ON delivery_logs(notification_id);
CREATE INDEX IF NOT EXISTS idx_delivery_logs_channel ON delivery_logs(channel);
CREATE INDEX IF NOT EXISTS idx_delivery_logs_status ON delivery_logs(status);
CREATE INDEX IF NOT EXISTS idx_delivery_logs_created_at ON delivery_logs(created_at);

-- Insert default channel configurations
INSERT INTO channel_configs (channel, config, rate_limit_per_minute) VALUES
('email', '{"provider": "sendgrid", "from_email": "noreply@bmad.com", "from_name": "BMAD System"}', 60),
('sms', '{"provider": "twilio", "from_number": "+1234567890"}', 30),
('slack', '{"webhook_url": "https://hooks.slack.com/services/your-webhook"}', 100),
('webhook', '{"timeout": 30, "retry_attempts": 3}', 200)
ON CONFLICT (channel) DO NOTHING;

-- Insert default templates
INSERT INTO templates (name, description, channel, subject_template, content_template, variables) VALUES
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

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_notifications_updated_at BEFORE UPDATE ON notifications
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_templates_updated_at BEFORE UPDATE ON templates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_channel_configs_updated_at BEFORE UPDATE ON channel_configs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create function to clean up old delivery logs
CREATE OR REPLACE FUNCTION cleanup_old_delivery_logs()
RETURNS void AS $$
BEGIN
    DELETE FROM delivery_logs 
    WHERE created_at < NOW() - INTERVAL '90 days';
END;
$$ LANGUAGE plpgsql;

-- Create function to get notification statistics
CREATE OR REPLACE FUNCTION get_notification_stats(
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
    FROM notifications
    WHERE (p_user_id IS NULL OR user_id = p_user_id)
        AND (p_channel IS NULL OR channel = p_channel)
        AND (p_start_date IS NULL OR created_at >= p_start_date)
        AND (p_end_date IS NULL OR created_at <= p_end_date);
END;
$$ LANGUAGE plpgsql; 