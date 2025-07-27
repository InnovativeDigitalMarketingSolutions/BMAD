# Webhook Integration - Alternative to Slack

## Overview

BMAD now includes a webhook-based notification system as an alternative to Slack. This system provides similar functionality but uses standard HTTP webhooks, making it compatible with any messaging platform that supports webhooks.

## Features

- **Message Sending**: Send text messages to webhook endpoints
- **HITL Alerts**: Human-in-the-Loop alerts for approval workflows
- **Workflow Notifications**: Status updates for workflow progress
- **Channel Support**: Multiple webhook endpoints for different channels
- **Error Handling**: Robust error handling and logging
- **Testing Support**: Built-in testing mode with `use_api=False`

## Configuration

### Environment Variables

Set up webhook URLs using environment variables:

```bash
# Default webhook URL
WEBHOOK_URL=https://your-webhook-endpoint.com/webhook

# Channel-specific webhooks
WEBHOOK_URL_ALERTS=https://your-alerts-webhook.com/webhook
WEBHOOK_URL_GENERAL=https://your-general-webhook.com/webhook
WEBHOOK_URL_DEPLOYMENTS=https://your-deployments-webhook.com/webhook

# Default channel name
WEBHOOK_DEFAULT_CHANNEL=general
```

### Supported Platforms

The webhook system works with any platform that accepts HTTP POST requests with JSON payloads:

- **Discord**: Use Discord webhook URLs
- **Microsoft Teams**: Use Teams webhook URLs
- **Slack**: Use Slack incoming webhooks
- **Custom Applications**: Any application with webhook support
- **Email Services**: Services like Zapier, IFTTT, etc.

## Usage

### Basic Message Sending

```python
from bmad.agents.core.webhook_notify import send_webhook_message

# Send a simple message
send_webhook_message("Hello from BMAD!", "general")

# Send to specific channel
send_webhook_message("Alert: System is down!", "alerts")
```

### HITL (Human-in-the-Loop) Alerts

```python
from bmad.agents.core.webhook_notify import send_webhook_hitl_alert

# Send approval request
send_webhook_hitl_alert(
    reason="Deployment to production requires approval",
    channel="deployments",
    user_mention="admin",
    alert_id="deploy-123"
)
```

### Workflow Notifications

```python
from bmad.agents.core.webhook_notify import send_webhook_workflow_notification

# Notify workflow status changes
send_webhook_workflow_notification(
    workflow_name="feature-development",
    status="started",
    channel="general"
)

send_webhook_workflow_notification(
    workflow_name="feature-development",
    status="completed",
    channel="general"
)
```

### Testing Mode

For testing, you can disable actual webhook calls:

```python
# This will log the message but not send it
send_webhook_message("Test message", use_api=False)
```

## Integration Examples

### Discord Integration

1. Create a Discord webhook in your server
2. Set the webhook URL in your environment:

```bash
WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_TOKEN
```

### Microsoft Teams Integration

1. Create a Teams webhook in your channel
2. Set the webhook URL:

```bash
WEBHOOK_URL=https://your-org.webhook.office.com/webhookb2/YOUR_WEBHOOK_ID
```

### Custom Application Integration

For custom applications, the webhook payload format is:

```json
{
  "text": "Your message here",
  "timestamp": "2025-07-27T01:00:00.000000",
  "channel": "general",
  "source": "BMAD",
  "alert_type": "hitl",
  "alert_id": "alert-123"
}
```

## Migration from Slack

To migrate from Slack to webhooks:

1. **Replace imports**:
   ```python
   # Old (Slack)
   from bmad.agents.core.slack_notify import send_slack_message
   
   # New (Webhook)
   from bmad.agents.core.webhook_notify import send_webhook_message
   ```

2. **Update function calls**:
   ```python
   # Old
   send_slack_message("Hello", "general", use_api=True)
   
   # New
   send_webhook_message("Hello", "general", use_api=True)
   ```

3. **Update environment variables**:
   ```bash
   # Old
   SLACK_BOT_TOKEN=xoxb-your-token
   SLACK_DEFAULT_CHANNEL=general
   
   # New
   WEBHOOK_URL=https://your-webhook-endpoint.com/webhook
   WEBHOOK_DEFAULT_CHANNEL=general
   ```

## Testing

Run the webhook tests:

```bash
python -m pytest tests/backend/test_webhook_notify.py -v
```

## Benefits Over Slack

1. **No API Limits**: No rate limiting from Slack API
2. **Platform Agnostic**: Works with any webhook-enabled platform
3. **Simpler Setup**: No need for bot tokens or OAuth flows
4. **Cost Effective**: No Slack workspace requirements
5. **Privacy**: Messages go directly to your chosen platform
6. **Reliability**: Fewer dependencies on external services

## Troubleshooting

### Common Issues

1. **"No webhook URLs configured"**
   - Check that `WEBHOOK_URL` is set in your environment
   - Verify the URL is correct and accessible

2. **"Failed to send message"**
   - Check network connectivity
   - Verify webhook endpoint is active
   - Check webhook URL format

3. **Messages not appearing**
   - Verify webhook URL is correct
   - Check platform-specific webhook requirements
   - Review webhook payload format

### Debug Mode

Enable debug logging to see detailed webhook activity:

```python
import logging
logging.getLogger('bmad.agents.core.webhook_notify').setLevel(logging.DEBUG)
```

## Future Enhancements

- **Retry Logic**: Automatic retry for failed webhook calls
- **Rate Limiting**: Built-in rate limiting for webhook endpoints
- **Payload Templates**: Customizable message templates
- **Webhook Validation**: Validate webhook URLs on startup
- **Metrics**: Track webhook success/failure rates 