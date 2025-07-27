# Webhook Integration - Slack Alternative

## Overview

The Webhook Integration provides a comprehensive alternative to Slack notifications for the BMAD system. It supports multiple webhook endpoints, various notification types, and integrates seamlessly with the existing notification infrastructure.

## Features

### 🔔 **Notification Types**
- **General Messages**: Basic text notifications
- **HITL Alerts**: Human-in-the-Loop approval requests
- **Workflow Notifications**: Workflow status updates
- **Error Notifications**: Error alerts with context
- **Success Notifications**: Success confirmations
- **Deployment Notifications**: Deployment status updates

### 🌐 **Multi-Channel Support**
- **Default Channel**: General notifications
- **Alerts Channel**: Critical alerts and HITL requests
- **Workflows Channel**: Workflow status updates
- **Errors Channel**: Error notifications
- **Deployments Channel**: Deployment updates
- **Custom Channels**: Any additional channels you configure

### 🔧 **Advanced Features**
- **Connection Testing**: Built-in webhook testing
- **Status Monitoring**: System status and configuration info
- **Fallback Support**: Automatic fallback to default webhook
- **Attachment Support**: Rich message attachments
- **Unified Interface**: Works with Notification Manager

## Configuration

### Environment Variables

Add these to your `.env` file:

```bash
# Basic webhook configuration
WEBHOOK_URL=https://your-webhook-endpoint.com/webhook

# Channel-specific webhooks (optional)
WEBHOOK_URL_ALERTS=https://your-webhook-endpoint.com/alerts
WEBHOOK_URL_WORKFLOWS=https://your-webhook-endpoint.com/workflows
WEBHOOK_URL_ERRORS=https://your-webhook-endpoint.com/errors
WEBHOOK_URL_DEPLOYMENTS=https://your-webhook-endpoint.com/deployments

# Default channel (optional, defaults to "general")
WEBHOOK_DEFAULT_CHANNEL=general
```

### Webhook Endpoint Setup

Your webhook endpoint should accept POST requests with JSON payloads:

```json
{
  "text": "Message content",
  "timestamp": "2025-07-27T10:30:00",
  "channel": "general",
  "source": "BMAD",
  "notification_type": "workflow",
  "workflow_name": "feature-development",
  "status": "started"
}
```

## Usage

### Direct Webhook Usage

```python
from bmad.agents.core.webhook_notify import (
    send_webhook_message,
    send_webhook_hitl_alert,
    send_webhook_workflow_notification,
    send_webhook_error_notification,
    send_webhook_success_notification,
    send_webhook_deployment_notification
)

# Send a general message
send_webhook_message("Hello from BMAD!", channel="general")

# Send a HITL alert
send_webhook_hitl_alert(
    "Deployment approval required",
    channel="alerts",
    user_mention="@admin",
    alert_id="deploy-123"
)

# Send a workflow notification
send_webhook_workflow_notification(
    "feature-development",
    "completed",
    channel="workflows"
)

# Send an error notification
send_webhook_error_notification(
    "Database connection failed",
    "Production environment",
    channel="errors"
)

# Send a success notification
send_webhook_success_notification(
    "User registration completed",
    "New user: john.doe@example.com",
    channel="success"
)

# Send a deployment notification
send_webhook_deployment_notification(
    "frontend-app",
    "completed",
    "production",
    channel="deployments"
)
```

### Using Notification Manager

```python
from bmad.agents.core.notification_manager import (
    send_notification,
    send_hitl_notification,
    send_workflow_notification,
    send_error_notification,
    send_success_notification,
    send_deployment_notification,
    NotificationType
)

# Send using auto-detection (webhook or Slack)
send_notification("Hello from BMAD!")

# Force webhook usage
send_notification(
    "Hello from BMAD!",
    notification_type=NotificationType.WEBHOOK
)

# Send HITL alert
send_hitl_notification("Approval needed", channel="alerts")

# Send workflow notification
send_workflow_notification("deploy", "started", channel="workflows")

# Send error notification
send_error_notification("Connection failed", "API timeout", channel="errors")

# Send success notification
send_success_notification("Task completed", "User created", channel="success")

# Send deployment notification
send_deployment_notification("app", "completed", "production", channel="deployments")
```

## CLI Tool

The webhook CLI tool provides comprehensive testing and management capabilities:

### Basic Commands

```bash
# Test webhook connection
python webhook_cli.py test

# Test notification manager
python webhook_cli.py test-manager

# Show system status
python webhook_cli.py status

# Run complete demo
python webhook_cli.py demo
```

### Sending Notifications

```bash
# Send a message
python webhook_cli.py message --message "Hello from CLI!"

# Send HITL alert
python webhook_cli.py hitl --reason "Deployment approval needed"

# Send workflow notification
python webhook_cli.py workflow --workflow "deploy" --status "started"

# Send error notification
python webhook_cli.py error --message "Connection failed" --context "API timeout"

# Send success notification
python webhook_cli.py success --message "Task completed" --context "User created"

# Send deployment notification
python webhook_cli.py deployment --workflow "app" --status "completed" --environment "production"
```

### Channel-Specific Notifications

```bash
# Send to specific channel
python webhook_cli.py message --message "Alert!" --channel alerts

# Send HITL to alerts channel
python webhook_cli.py hitl --reason "Critical issue" --channel alerts

# Send workflow to workflows channel
python webhook_cli.py workflow --workflow "test" --status "completed" --channel workflows
```

### Using Notification Manager

```bash
# Use notification manager instead of direct webhook
python webhook_cli.py message --message "Test" --use-manager

# Test notification manager connection
python webhook_cli.py test-manager
```

## Integration with Agents

### Agent Usage

Agents can use the webhook system through the notification manager:

```python
from bmad.agents.core.notification_manager import send_notification

class MyAgent:
    def process_task(self):
        try:
            # Do some work
            result = self.perform_work()
            
            # Send success notification
            send_notification(
                f"Task completed successfully: {result}",
                channel="success"
            )
            
        except Exception as e:
            # Send error notification
            send_notification(
                f"Task failed: {str(e)}",
                channel="errors"
            )
```

### Workflow Integration

```python
from bmad.agents.core.notification_manager import send_workflow_notification

def run_workflow(workflow_name):
    # Start workflow
    send_workflow_notification(workflow_name, "started", channel="workflows")
    
    try:
        # Execute workflow
        result = execute_workflow()
        
        # Complete workflow
        send_workflow_notification(workflow_name, "completed", channel="workflows")
        
    except Exception as e:
        # Workflow failed
        send_workflow_notification(workflow_name, "failed", channel="workflows")
        raise
```

## Testing

### Connection Testing

```python
from bmad.agents.core.webhook_notify import test_webhook_connection

# Test default webhook
success = test_webhook_connection()

# Test specific channel
success = test_webhook_connection("alerts")
```

### Status Checking

```python
from bmad.agents.core.webhook_notify import get_webhook_status
from bmad.agents.core.notification_manager import get_notification_status

# Get webhook status
webhook_status = get_webhook_status()
print(webhook_status)

# Get notification manager status
notification_status = get_notification_status()
print(notification_status)
```

## Error Handling

The webhook system includes comprehensive error handling:

- **Connection Failures**: Automatic retry and fallback
- **Invalid URLs**: Graceful error reporting
- **Timeout Handling**: Configurable timeouts
- **Payload Validation**: Automatic payload formatting

## Migration from Slack

### Simple Migration

1. **Configure Webhook URLs**: Add webhook endpoints to `.env`
2. **Update Agent Code**: Replace Slack calls with notification manager calls
3. **Test Integration**: Use CLI tool to verify functionality

### Example Migration

**Before (Slack):**
```python
from bmad.agents.core.slack_notify import send_slack_message

send_slack_message("Hello from agent!", channel="general")
```

**After (Webhook):**
```python
from bmad.agents.core.notification_manager import send_notification

send_notification("Hello from agent!", channel="general")
```

## Best Practices

### 1. **Use Appropriate Channels**
- Use `alerts` for critical notifications
- Use `workflows` for workflow status
- Use `errors` for error reporting
- Use `deployments` for deployment updates

### 2. **Include Context**
```python
send_error_notification(
    "Database connection failed",
    "Production environment, user service",
    channel="errors"
)
```

### 3. **Test Regularly**
```bash
# Run tests regularly
python webhook_cli.py test
python webhook_cli.py demo
```

### 4. **Monitor Status**
```bash
# Check system status
python webhook_cli.py status
```

## Troubleshooting

### Common Issues

1. **Connection Failed**
   - Check webhook URL in `.env`
   - Verify webhook endpoint is accessible
   - Test with CLI tool

2. **Messages Not Received**
   - Check webhook endpoint logs
   - Verify payload format
   - Test with simple message first

3. **Channel Not Working**
   - Check channel-specific webhook URL
   - Verify channel name spelling
   - Use default channel as fallback

### Debug Mode

Enable debug logging:

```python
import logging
logging.getLogger('bmad.agents.core.webhook_notify').setLevel(logging.DEBUG)
```

## API Reference

### WebhookNotifier Class

```python
class WebhookNotifier:
    def send_webhook_message(message, channel=None, use_api=True, **kwargs)
    def send_human_in_loop_alert(reason, channel=None, user_mention=None, alert_id=None, use_api=True)
    def send_workflow_notification(workflow_name, status, channel=None, use_api=True)
    def send_error_notification(error_message, context=None, channel=None, use_api=True)
    def send_success_notification(success_message, context=None, channel=None, use_api=True)
    def send_deployment_notification(deployment_name, status, environment=None, channel=None, use_api=True)
    def test_connection(channel=None)
    def get_status()
```

### Notification Manager Functions

```python
def send_notification(text, channel=None, notification_type=None, **kwargs)
def send_hitl_notification(reason, channel=None, notification_type=None, **kwargs)
def send_workflow_notification(workflow_name, status, channel=None, notification_type=None, **kwargs)
def send_error_notification(error_message, context=None, channel=None, notification_type=None, **kwargs)
def send_success_notification(success_message, context=None, channel=None, notification_type=None, **kwargs)
def send_deployment_notification(deployment_name, status, environment=None, channel=None, notification_type=None, **kwargs)
def test_notification_connection(channel=None, notification_type=None)
def get_notification_status()
```

## Examples

### Complete Workflow Example

```python
from bmad.agents.core.notification_manager import (
    send_workflow_notification,
    send_hitl_notification,
    send_success_notification,
    send_error_notification
)

def deploy_application(app_name, environment):
    workflow_name = f"deploy-{app_name}"
    
    try:
        # Start deployment
        send_workflow_notification(workflow_name, "started", channel="workflows")
        
        # Check if approval needed
        if environment == "production":
            send_hitl_notification(
                f"Production deployment for {app_name}",
                channel="alerts"
            )
        
        # Execute deployment
        result = execute_deployment(app_name, environment)
        
        # Success
        send_workflow_notification(workflow_name, "completed", channel="workflows")
        send_success_notification(
            f"Deployment successful: {app_name}",
            f"Environment: {environment}",
            channel="success"
        )
        
    except Exception as e:
        # Failure
        send_workflow_notification(workflow_name, "failed", channel="workflows")
        send_error_notification(
            f"Deployment failed: {app_name}",
            f"Error: {str(e)}, Environment: {environment}",
            channel="errors"
        )
        raise
```

This webhook integration provides a robust, feature-rich alternative to Slack that integrates seamlessly with the BMAD system while offering greater flexibility and control over notification delivery. 