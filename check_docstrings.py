#!/usr/bin/env python3
"""
Script to check which methods are missing docstrings in ProductOwnerAgent
"""

import ast
from pathlib import Path

def check_method_docstrings(file_path):
    """Check which methods are missing docstrings."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    tree = ast.parse(content)
    
    # Find the main agent class
    agent_class = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and 'Agent' in node.name and node.name != 'AgentMessageBusIntegration':
            agent_class = node
            break
    
    if not agent_class:
        print("No agent class found")
        return
    
    print(f"Checking methods in {agent_class.name}:")
    print("=" * 50)
    
    methods_without_docstrings = []
    methods_with_docstrings = []
    
    for node in ast.walk(agent_class):
        if isinstance(node, ast.FunctionDef):
            method_name = node.name
            docstring = ast.get_docstring(node)
            
            if docstring is None:
                methods_without_docstrings.append(method_name)
                print(f"❌ {method_name} - NO DOCSTRING")
            else:
                methods_with_docstrings.append(method_name)
                print(f"✅ {method_name} - Has docstring")
    
    print("\n" + "=" * 50)
    print(f"Methods with docstrings: {len(methods_with_docstrings)}")
    print(f"Methods without docstrings: {len(methods_without_docstrings)}")
    
    if methods_without_docstrings:
        print(f"\nMethods missing docstrings:")
        for method in methods_without_docstrings:
            print(f"  - {method}")

if __name__ == "__main__":
    file_path = Path("bmad/agents/Agent/ProductOwner/product_owner.py")
    check_method_docstrings(file_path) 