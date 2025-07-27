#!/usr/bin/env python3
"""
Webhook CLI - Command line interface for webhook notifications.
"""

import os
import sys
import argparse
import json
from typing import Optional, Dict, Any

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bmad.agents.core.notification_manager import (
    NotificationManager,
    NotificationType,
    send_notification,
    send_hitl_notification,
    send_workflow_notification
)

def setup_webhook_config():
    """Interactive setup for webhook configuration."""
    print("🔧 Webhook Configuration Setup")
    print("=" * 40)
    
    webhook_url = input("Enter webhook URL (or press Enter to skip): ").strip()
    if not webhook_url:
        print("⚠️  No webhook URL provided. Setup cancelled.")
        return False
    
    # Additional webhook URLs
    alerts_url = input("Enter alerts webhook URL (optional): ").strip()
    general_url = input("Enter general webhook URL (optional): ").strip()
    
    # Create .env entries
    env_entries = []
    env_entries.append(f"WEBHOOK_URL={webhook_url}")
    
    if alerts_url:
        env_entries.append(f"WEBHOOK_URL_ALERTS={alerts_url}")
    
    if general_url:
        env_entries.append(f"WEBHOOK_URL_GENERAL={general_url}")
    
    # Write to .env file
    env_file = ".env"
    with open(env_file, "a") as f:
        f.write("\n# Webhook Configuration\n")
        for entry in env_entries:
            f.write(f"{entry}\n")
    
    print(f"✅ Webhook configuration saved to {env_file}")
    print("📝 Environment variables added:")
    for entry in env_entries:
        print(f"   {entry}")
    
    return True

def test_webhook():
    """Test webhook configuration."""
    print("🧪 Testing Webhook Configuration")
    print("=" * 40)
    
    manager = NotificationManager(NotificationType.WEBHOOK)
    status = manager.get_status()
    
    print(f"Notification Type: {status['type']}")
    print(f"Webhook Available: {status['webhook_available']}")
    print(f"Webhook Configured: {status['webhook_configured']}")
    
    if not status['webhook_configured']:
        print("❌ Webhook not configured. Run 'setup' first.")
        return False
    
    # Test basic message
    print("\n📤 Testing basic message...")
    result = send_notification("Test message from BMAD Webhook CLI", notification_type=NotificationType.WEBHOOK)
    
    if result:
        print("✅ Basic message test successful!")
    else:
        print("❌ Basic message test failed!")
        return False
    
    # Test HITL alert
    print("\n🚨 Testing HITL alert...")
    result = send_hitl_notification("Test HITL alert from CLI", notification_type=NotificationType.WEBHOOK)
    
    if result:
        print("✅ HITL alert test successful!")
    else:
        print("❌ HITL alert test failed!")
        return False
    
    # Test workflow notification
    print("\n🔄 Testing workflow notification...")
    result = send_workflow_notification("test-workflow", "completed", notification_type=NotificationType.WEBHOOK)
    
    if result:
        print("✅ Workflow notification test successful!")
    else:
        print("❌ Workflow notification test failed!")
        return False
    
    print("\n🎉 All webhook tests passed!")
    return True

def send_message(text: str, channel: Optional[str] = None):
    """Send a message via webhook."""
    print(f"📤 Sending message: {text}")
    
    result = send_notification(text, channel=channel, notification_type=NotificationType.WEBHOOK)
    
    if result:
        print("✅ Message sent successfully!")
    else:
        print("❌ Failed to send message!")
        return False
    
    return True

def send_alert(reason: str, channel: Optional[str] = None):
    """Send a HITL alert via webhook."""
    print(f"🚨 Sending HITL alert: {reason}")
    
    result = send_hitl_notification(reason, channel=channel, notification_type=NotificationType.WEBHOOK)
    
    if result:
        print("✅ HITL alert sent successfully!")
    else:
        print("❌ Failed to send HITL alert!")
        return False
    
    return True

def send_workflow(workflow_name: str, status: str, channel: Optional[str] = None):
    """Send a workflow notification via webhook."""
    print(f"🔄 Sending workflow notification: {workflow_name} - {status}")
    
    result = send_workflow_notification(workflow_name, status, channel=channel, notification_type=NotificationType.WEBHOOK)
    
    if result:
        print("✅ Workflow notification sent successfully!")
    else:
        print("❌ Failed to send workflow notification!")
        return False
    
    return True

def show_status():
    """Show webhook status."""
    print("📊 Webhook Status")
    print("=" * 40)
    
    manager = NotificationManager(NotificationType.WEBHOOK)
    status = manager.get_status()
    
    print(f"Notification Type: {status['type']}")
    print(f"Webhook Available: {status['webhook_available']}")
    print(f"Webhook Configured: {status['webhook_configured']}")
    print(f"Slack Available: {status['slack_available']}")
    print(f"Slack Configured: {status['slack_configured']}")
    
    # Show environment variables
    print("\n🔧 Environment Variables:")
    webhook_url = os.getenv("WEBHOOK_URL")
    alerts_url = os.getenv("WEBHOOK_URL_ALERTS")
    general_url = os.getenv("WEBHOOK_URL_GENERAL")
    
    print(f"WEBHOOK_URL: {'✅ Set' if webhook_url else '❌ Not set'}")
    print(f"WEBHOOK_URL_ALERTS: {'✅ Set' if alerts_url else '❌ Not set'}")
    print(f"WEBHOOK_URL_GENERAL: {'✅ Set' if general_url else '❌ Not set'}")

def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="BMAD Webhook CLI - Manage webhook notifications",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python webhook_cli.py setup                    # Setup webhook configuration
  python webhook_cli.py test                     # Test webhook configuration
  python webhook_cli.py send "Hello World"       # Send a message
  python webhook_cli.py alert "Deployment needed" # Send HITL alert
  python webhook_cli.py workflow "deploy" "started" # Send workflow notification
  python webhook_cli.py status                   # Show status
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Setup command
    subparsers.add_parser('setup', help='Setup webhook configuration')
    
    # Test command
    subparsers.add_parser('test', help='Test webhook configuration')
    
    # Send message command
    send_parser = subparsers.add_parser('send', help='Send a message')
    send_parser.add_argument('message', help='Message to send')
    send_parser.add_argument('--channel', '-c', help='Channel to send to')
    
    # Alert command
    alert_parser = subparsers.add_parser('alert', help='Send HITL alert')
    alert_parser.add_argument('reason', help='Alert reason')
    alert_parser.add_argument('--channel', '-c', help='Channel to send to')
    
    # Workflow command
    workflow_parser = subparsers.add_parser('workflow', help='Send workflow notification')
    workflow_parser.add_argument('name', help='Workflow name')
    workflow_parser.add_argument('status', help='Workflow status')
    workflow_parser.add_argument('--channel', '-c', help='Channel to send to')
    
    # Status command
    subparsers.add_parser('status', help='Show webhook status')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'setup':
            setup_webhook_config()
        elif args.command == 'test':
            test_webhook()
        elif args.command == 'send':
            send_message(args.message, args.channel)
        elif args.command == 'alert':
            send_alert(args.reason, args.channel)
        elif args.command == 'workflow':
            send_workflow(args.name, args.status, args.channel)
        elif args.command == 'status':
            show_status()
        else:
            print(f"❌ Unknown command: {args.command}")
            parser.print_help()
    
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 