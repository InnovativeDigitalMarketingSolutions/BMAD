#!/usr/bin/env python3
"""
BMAD Advanced Policy CLI

CLI tool voor het beheren van geavanceerde policies met complexe conditions,
inheritance, composition, en versioning.
"""

import asyncio
import argparse
import json
import sys
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Add BMAD to path
sys.path.append(str(Path(__file__).parent.parent))

# Import BMAD modules
from bmad.agents.core.advanced_policy_engine import (
    AdvancedPolicyEngine,
    PolicyDefinition,
    PolicyRule,
    PolicyCondition,
    PolicyType,
    PolicySeverity,
    PolicyStatus,
    PolicyRequest,
    get_advanced_policy_engine
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AdvancedPolicyCLI:
    """CLI for managing advanced policies."""
    
    def __init__(self):
        self.engine = get_advanced_policy_engine()
    
    async def list_policies(self, policy_type: Optional[str] = None):
        """List all policies."""
        print("📋 Advanced Policies")
        print("=" * 50)
        
        try:
            policies = list(self.engine.policies.values())
            
            if policy_type:
                policies = [p for p in policies if p.policy_type.value == policy_type]
            
            if not policies:
                print("❌ No policies found")
                return
            
            for i, policy in enumerate(policies, 1):
                print(f"{i}. {policy.policy_name} ({policy.policy_id})")
                print(f"   📊 Type: {policy.policy_type.value}")
                print(f"   📝 Version: {policy.version}")
                print(f"   📈 Status: {policy.status.value}")
                print(f"   🔗 Rules: {len(policy.rules)}")
                if policy.parent_policy:
                    print(f"   👥 Parent: {policy.parent_policy}")
                print(f"   📅 Created: {policy.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                print()
                
        except Exception as e:
            print(f"❌ Failed to list policies: {e}")
    
    async def show_policy(self, policy_id: str):
        """Show detailed policy information."""
        print(f"📋 Policy Details: {policy_id}")
        print("=" * 50)
        
        try:
            if policy_id not in self.engine.policies:
                print(f"❌ Policy '{policy_id}' not found")
                return
            
            policy = self.engine.policies[policy_id]
            
            print(f"📝 Name: {policy.policy_name}")
            print(f"🆔 ID: {policy.policy_id}")
            print(f"📊 Type: {policy.policy_type.value}")
            print(f"📈 Version: {policy.version}")
            print(f"📈 Status: {policy.status.value}")
            print(f"📅 Created: {policy.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"📅 Updated: {policy.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")
            
            if policy.expires_at:
                print(f"⏰ Expires: {policy.expires_at.strftime('%Y-%m-%d %H:%M:%S')}")
            
            if policy.parent_policy:
                print(f"👥 Parent Policy: {policy.parent_policy}")
            
            if policy.metadata:
                print(f"🏷️  Tags: {policy.metadata.get('tags', [])}")
            
            print(f"\n📋 Rules ({len(policy.rules)}):")
            for i, rule in enumerate(policy.rules, 1):
                print(f"\n   {i}. {rule.rule_name} ({rule.rule_id})")
                print(f"      📊 Priority: {rule.priority}")
                print(f"      📈 Enabled: {rule.enabled}")
                print(f"      📝 Description: {rule.description}")
                print(f"      🎯 Actions: {', '.join(rule.actions)}")
                
                print(f"      📋 Conditions ({len(rule.conditions)}):")
                for j, condition in enumerate(rule.conditions, 1):
                    print(f"         {j}. {condition.condition_id}")
                    print(f"            📊 Type: {condition.condition_type}")
                    print(f"            📈 Severity: {condition.severity.value}")
                    print(f"            📝 Description: {condition.description}")
                    print(f"            ✅ Enabled: {condition.enabled}")
                    print(f"            ⚙️  Parameters: {json.dumps(condition.parameters, indent=12)}")
            
            # Show versions
            versions = self.engine.get_policy_versions(policy_id)
            if versions:
                print(f"\n📚 Versions ({len(versions)}):")
                for version in versions[-5:]:  # Show last 5 versions
                    status = "✅ Active" if version.is_active else "❌ Inactive"
                    print(f"   📝 {version.version_number} - {status}")
                    print(f"      📅 Created: {version.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"      👤 By: {version.created_by}")
                    print(f"      📝 Change: {version.change_description}")
                
        except Exception as e:
            print(f"❌ Failed to show policy: {e}")
    
    async def create_policy(self, policy_file: str):
        """Create a new policy from file."""
        print(f"🎯 Creating policy from: {policy_file}")
        print("=" * 50)
        
        try:
            with open(policy_file, 'r') as f:
                policy_data = json.load(f)
            
            policy = self.engine.create_policy(policy_data)
            
            print("✅ Policy created successfully")
            print(f"   📝 Name: {policy.policy_name}")
            print(f"   🆔 ID: {policy.policy_id}")
            print(f"   📊 Type: {policy.policy_type.value}")
            print(f"   📈 Version: {policy.version}")
            print(f"   📋 Rules: {len(policy.rules)}")
            
        except FileNotFoundError:
            print(f"❌ Policy file not found: {policy_file}")
        except json.JSONDecodeError:
            print(f"❌ Invalid JSON in policy file: {policy_file}")
        except Exception as e:
            print(f"❌ Failed to create policy: {e}")
    
    async def update_policy(self, policy_id: str, updates_file: str, change_description: str):
        """Update an existing policy."""
        print(f"🔧 Updating policy: {policy_id}")
        print("=" * 50)
        
        try:
            with open(updates_file, 'r') as f:
                updates = json.load(f)
            
            policy = self.engine.update_policy(policy_id, updates, change_description)
            
            print("✅ Policy updated successfully")
            print(f"   📝 Name: {policy.policy_name}")
            print(f"   📈 Version: {policy.version}")
            print(f"   📅 Updated: {policy.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   📝 Change: {change_description}")
            
        except FileNotFoundError:
            print(f"❌ Updates file not found: {updates_file}")
        except json.JSONDecodeError:
            print(f"❌ Invalid JSON in updates file: {updates_file}")
        except Exception as e:
            print(f"❌ Failed to update policy: {e}")
    
    async def evaluate_policy(self, policy_id: str, request_file: str):
        """Evaluate a policy with a request."""
        print(f"🧪 Evaluating policy: {policy_id}")
        print("=" * 50)
        
        try:
            with open(request_file, 'r') as f:
                request_data = json.load(f)
            
            request = PolicyRequest(**request_data)
            result = await self.engine.evaluate_policy(policy_id, request)
            
            print("📊 Evaluation Results:")
            print(f"   🎯 Policy: {result.policy_id}")
            print(f"   📋 Rule: {result.rule_id}")
            print(f"   ✅ Allowed: {result.allowed}")
            print(f"   📝 Reason: {result.reason}")
            print(f"   📈 Severity: {result.severity.value}")
            print(f"   📅 Timestamp: {result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            
            if result.conditions_met:
                print(f"   ✅ Conditions Met: {', '.join(result.conditions_met)}")
            
            if result.conditions_failed:
                print(f"   ❌ Conditions Failed: {', '.join(result.conditions_failed)}")
            
            if result.metadata:
                print(f"   📊 Metadata: {json.dumps(result.metadata, indent=6)}")
            
        except FileNotFoundError:
            print(f"❌ Request file not found: {request_file}")
        except json.JSONDecodeError:
            print(f"❌ Invalid JSON in request file: {request_file}")
        except Exception as e:
            print(f"❌ Failed to evaluate policy: {e}")
    
    async def evaluate_composite_policy(self, policy_ids: str, request_file: str):
        """Evaluate multiple policies."""
        print(f"🧪 Evaluating composite policies: {policy_ids}")
        print("=" * 50)
        
        try:
            policy_id_list = [pid.strip() for pid in policy_ids.split(',')]
            
            with open(request_file, 'r') as f:
                request_data = json.load(f)
            
            request = PolicyRequest(**request_data)
            results = await self.engine.evaluate_composite_policy(policy_id_list, request)
            
            print("📊 Composite Evaluation Results:")
            for i, result in enumerate(results, 1):
                print(f"\n   {i}. Policy: {result.policy_id}")
                print(f"      📋 Rule: {result.rule_id}")
                print(f"      ✅ Allowed: {result.allowed}")
                print(f"      📝 Reason: {result.reason}")
                print(f"      📈 Severity: {result.severity.value}")
            
        except FileNotFoundError:
            print(f"❌ Request file not found: {request_file}")
        except json.JSONDecodeError:
            print(f"❌ Invalid JSON in request file: {request_file}")
        except Exception as e:
            print(f"❌ Failed to evaluate composite policy: {e}")
    
    async def rollback_policy(self, policy_id: str, version_number: str):
        """Rollback a policy to a specific version."""
        print(f"⏪ Rolling back policy: {policy_id} to version {version_number}")
        print("=" * 50)
        
        try:
            policy = self.engine.rollback_policy(policy_id, version_number)
            
            print("✅ Policy rolled back successfully")
            print(f"   📝 Name: {policy.policy_name}")
            print(f"   📈 Version: {policy.version}")
            print(f"   📅 Updated: {policy.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")
            
        except Exception as e:
            print(f"❌ Failed to rollback policy: {e}")
    
    async def show_versions(self, policy_id: str):
        """Show all versions of a policy."""
        print(f"📚 Policy Versions: {policy_id}")
        print("=" * 50)
        
        try:
            versions = self.engine.get_policy_versions(policy_id)
            
            if not versions:
                print("❌ No versions found")
                return
            
            for i, version in enumerate(versions, 1):
                status = "✅ Active" if version.is_active else "❌ Inactive"
                print(f"{i}. Version {version.version_number} - {status}")
                print(f"   📅 Created: {version.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"   👤 By: {version.created_by}")
                print(f"   📝 Change: {version.change_description}")
                print()
            
        except Exception as e:
            print(f"❌ Failed to show versions: {e}")
    
    def create_policy_template(self, template_name: str):
        """Create a policy template file."""
        print(f"📝 Creating policy template: {template_name}")
        print("=" * 50)
        
        try:
            template = {
                "policy_id": "example_policy",
                "policy_name": "Example Policy",
                "policy_type": "access_control",
                "version": "1.0.0",
                "rules": [
                    {
                        "rule_id": "example_rule",
                        "rule_name": "Example Rule",
                        "policy_type": "access_control",
                        "priority": 100,
                        "conditions": [
                            {
                                "condition_id": "example_condition",
                                "condition_type": "role_based",
                                "parameters": {
                                    "required_roles": ["admin", "user"]
                                },
                                "description": "Example condition",
                                "severity": "medium",
                                "enabled": True
                            }
                        ],
                        "actions": ["allow"],
                        "description": "Example rule description"
                    }
                ],
                "status": "active",
                "metadata": {
                    "category": "example",
                    "tags": ["example", "template"]
                }
            }
            
            template_file = f"{template_name}.json"
            with open(template_file, 'w') as f:
                json.dump(template, f, indent=2)
            
            print(f"✅ Template created: {template_file}")
            print("📝 Edit the template and use 'create-policy' to create the actual policy")
            
        except Exception as e:
            print(f"❌ Failed to create template: {e}")
    
    def create_request_template(self, template_name: str):
        """Create a request template file."""
        print(f"📝 Creating request template: {template_name}")
        print("=" * 50)
        
        try:
            template = {
                "subject": "user123",
                "action": "read",
                "resource": "document",
                "context": {
                    "user_roles": ["admin"],
                    "time": "2024-01-01T12:00:00",
                    "ip_address": "192.168.1.1",
                    "cpu_usage": 45.2,
                    "memory_usage": 67.8,
                    "api_calls_count": 150
                }
            }
            
            template_file = f"{template_name}.json"
            with open(template_file, 'w') as f:
                json.dump(template, f, indent=2)
            
            print(f"✅ Template created: {template_file}")
            print("📝 Edit the template and use 'evaluate-policy' to test policies")
            
        except Exception as e:
            print(f"❌ Failed to create template: {e}")

async def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="BMAD Advanced Policy CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all policies
  python advanced_policy_cli.py list-policies
  
  # List policies by type
  python advanced_policy_cli.py list-policies --type access_control
  
  # Show policy details
  python advanced_policy_cli.py show-policy advanced_access_control
  
  # Create policy from file
  python advanced_policy_cli.py create-policy my_policy.json
  
  # Update policy
  python advanced_policy_cli.py update-policy policy_id updates.json "Updated description"
  
  # Evaluate policy
  python advanced_policy_cli.py evaluate-policy policy_id request.json
  
  # Evaluate composite policies
  python advanced_policy_cli.py evaluate-composite "policy1,policy2,policy3" request.json
  
  # Rollback policy
  python advanced_policy_cli.py rollback-policy policy_id 1.0.0
  
  # Show policy versions
  python advanced_policy_cli.py show-versions policy_id
  
  # Create templates
  python advanced_policy_cli.py create-policy-template my_policy
  python advanced_policy_cli.py create-request-template my_request
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List policies command
    list_parser = subparsers.add_parser('list-policies', help='List all policies')
    list_parser.add_argument('--type', help='Filter by policy type')
    
    # Show policy command
    show_parser = subparsers.add_parser('show-policy', help='Show policy details')
    show_parser.add_argument('policy_id', help='Policy ID')
    
    # Create policy command
    create_parser = subparsers.add_parser('create-policy', help='Create policy from file')
    create_parser.add_argument('policy_file', help='Policy JSON file')
    
    # Update policy command
    update_parser = subparsers.add_parser('update-policy', help='Update policy')
    update_parser.add_argument('policy_id', help='Policy ID')
    update_parser.add_argument('updates_file', help='Updates JSON file')
    update_parser.add_argument('change_description', help='Change description')
    
    # Evaluate policy command
    evaluate_parser = subparsers.add_parser('evaluate-policy', help='Evaluate policy')
    evaluate_parser.add_argument('policy_id', help='Policy ID')
    evaluate_parser.add_argument('request_file', help='Request JSON file')
    
    # Evaluate composite policy command
    composite_parser = subparsers.add_parser('evaluate-composite', help='Evaluate composite policies')
    composite_parser.add_argument('policy_ids', help='Comma-separated policy IDs')
    composite_parser.add_argument('request_file', help='Request JSON file')
    
    # Rollback policy command
    rollback_parser = subparsers.add_parser('rollback-policy', help='Rollback policy')
    rollback_parser.add_argument('policy_id', help='Policy ID')
    rollback_parser.add_argument('version_number', help='Version number')
    
    # Show versions command
    versions_parser = subparsers.add_parser('show-versions', help='Show policy versions')
    versions_parser.add_argument('policy_id', help='Policy ID')
    
    # Create templates commands
    policy_template_parser = subparsers.add_parser('create-policy-template', help='Create policy template')
    policy_template_parser.add_argument('template_name', help='Template name')
    
    request_template_parser = subparsers.add_parser('create-request-template', help='Create request template')
    request_template_parser.add_argument('template_name', help='Template name')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = AdvancedPolicyCLI()
    
    try:
        if args.command == 'list-policies':
            await cli.list_policies(args.type)
        
        elif args.command == 'show-policy':
            await cli.show_policy(args.policy_id)
        
        elif args.command == 'create-policy':
            await cli.create_policy(args.policy_file)
        
        elif args.command == 'update-policy':
            await cli.update_policy(args.policy_id, args.updates_file, args.change_description)
        
        elif args.command == 'evaluate-policy':
            await cli.evaluate_policy(args.policy_id, args.request_file)
        
        elif args.command == 'evaluate-composite':
            await cli.evaluate_composite_policy(args.policy_ids, args.request_file)
        
        elif args.command == 'rollback-policy':
            await cli.rollback_policy(args.policy_id, args.version_number)
        
        elif args.command == 'show-versions':
            await cli.show_versions(args.policy_id)
        
        elif args.command == 'create-policy-template':
            cli.create_policy_template(args.template_name)
        
        elif args.command == 'create-request-template':
            cli.create_request_template(args.template_name)
    
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        logger.error(f"CLI error: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(main()) 