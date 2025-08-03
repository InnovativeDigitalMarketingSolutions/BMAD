#!/usr/bin/env python3
"""
Complex Test File Fix Script
Automated detection and fixing of syntax errors in test files.

Based on lessons learned from DocumentationAgent complex issues.
"""

import os
import re
import ast
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple

class ComplexTestFileFixer:
    """Automated fixer for complex test files with syntax errors."""
    
    def __init__(self, test_file_path: str):
        self.test_file_path = test_file_path
        self.content = ""
        self.fixes_applied = []
        self.complexity_score = 0
        
    def analyze_complexity(self) -> Dict[str, int]:
        """Analyze file complexity and return metrics."""
        with open(self.test_file_path, 'r') as f:
            self.content = f.read()
        
        metrics = {
            'total_lines': len(self.content.split('\n')),
            'trailing_commas': len(re.findall(r'with patch\([^)]*\),\s*$', self.content, re.MULTILINE)),
            'mock_data_issues': len(re.findall(r'nn', self.content)),
            'await_outside_async': len(re.findall(r'await\s+\w+\.\w+', self.content)),
            'syntax_errors': 0
        }
        
        # Count syntax errors
        try:
            ast.parse(self.content)
        except SyntaxError as e:
            metrics['syntax_errors'] = 1
        
        # Calculate complexity score
        self.complexity_score = (
            metrics['total_lines'] * 0.1 +
            metrics['trailing_commas'] * 5 +
            metrics['mock_data_issues'] * 2 +
            metrics['await_outside_async'] * 3 +
            metrics['syntax_errors'] * 10
        )
        
        return metrics
    
    def fix_trailing_commas_advanced(self) -> bool:
        """Advanced fix for trailing commas in with statements."""
        original_content = self.content
        
        # More comprehensive pattern matching
        lines = self.content.split('\n')
        fixed_lines = []
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Check if this line has a trailing comma in with statement
            if re.match(r'^\s*with patch\([^)]*\),\s*$', line):
                # Look ahead to find the next patch line
                next_line_idx = i + 1
                while next_line_idx < len(lines) and not re.match(r'^\s*patch\(', lines[next_line_idx]):
                    next_line_idx += 1
                
                if next_line_idx < len(lines):
                    # Fix the current line
                    fixed_line = line.rstrip() + ' \\'
                    fixed_lines.append(fixed_line)
                    
                    # Skip the next line if it's a patch line (it will be handled)
                    i = next_line_idx
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
            
            i += 1
        
        self.content = '\n'.join(fixed_lines)
        
        if self.content != original_content:
            self.fixes_applied.append("Fixed trailing commas in with statements (advanced)")
            return True
        return False
    
    def fix_trailing_commas_simple(self) -> bool:
        """Simple fix for trailing commas in with statements."""
        original_content = self.content
        
        # Pattern 1: with patch(...), -> with patch(...), \
        pattern1 = r'(with patch\([^)]*\)),(\s*)(patch\([^)]*\))'
        replacement1 = r'\1, \\\2\3'
        self.content = re.sub(pattern1, replacement1, self.content)
        
        # Pattern 2: with patch(...), -> with patch(...), \
        pattern2 = r'(with patch\([^)]*\)),(\s*)(patch\([^)]*\)),(\s*)(patch\([^)]*\))'
        replacement2 = r'\1, \\\2\3, \\\4\5'
        self.content = re.sub(pattern2, replacement2, self.content)
        
        # Pattern 3: with patch(...), -> with patch(...), \
        pattern3 = r'(with patch\([^)]*\)),(\s*)(patch\([^)]*\)),(\s*)(patch\([^)]*\)),(\s*)(patch\([^)]*\))'
        replacement3 = r'\1, \\\2\3, \\\4\5, \\\6\7'
        self.content = re.sub(pattern3, replacement3, self.content)
        
        if self.content != original_content:
            self.fixes_applied.append("Fixed trailing commas in with statements (simple)")
            return True
        return False
    
    def fix_mock_data_escape_sequences(self) -> bool:
        """Fix mock data escape sequences."""
        original_content = self.content
        
        # Fix nn -> \n\n
        self.content = re.sub(r'nn', r'\\n\\n', self.content)
        
        # Fix double escaped newlines
        self.content = re.sub(r'\\\\n\\\\n', r'\\n\\n', self.content)
        
        if self.content != original_content:
            self.fixes_applied.append("Fixed mock data escape sequences")
            return True
        return False
    
    def fix_await_outside_async(self) -> bool:
        """Fix await outside async function issues."""
        original_content = self.content
        
        # This is more complex and requires context analysis
        # For now, we'll just detect the issues
        await_pattern = r'await\s+\w+\.\w+'
        await_matches = re.findall(await_pattern, self.content)
        
        if await_matches:
            self.fixes_applied.append(f"Detected {len(await_matches)} await outside async issues (manual fix required)")
            return True
        return False
    
    def validate_syntax(self) -> bool:
        """Validate that the file has correct syntax."""
        try:
            ast.parse(self.content)
            return True
        except SyntaxError as e:
            print(f"❌ Syntax error still present: {e}")
            return False
    
    def apply_fixes(self) -> bool:
        """Apply all automated fixes."""
        print(f"🔧 Applying fixes to {self.test_file_path}")
        
        fixes_made = False
        
        # Try simple fixes first
        fixes_made |= self.fix_mock_data_escape_sequences()
        fixes_made |= self.fix_await_outside_async()
        
        # Try simple trailing comma fix
        if self.fix_trailing_commas_simple():
            fixes_made = True
            if self.validate_syntax():
                # Simple fix worked, write the file
                with open(self.test_file_path, 'w') as f:
                    f.write(self.content)
                print(f"✅ Applied {len(self.fixes_applied)} fixes (simple approach)")
                for fix in self.fixes_applied:
                    print(f"   - {fix}")
                return True
            else:
                # Simple fix failed, revert and try advanced approach
                with open(self.test_file_path, 'r') as f:
                    self.content = f.read()
                self.fixes_applied = []
        
        # Try advanced trailing comma fix
        if self.fix_trailing_commas_advanced():
            fixes_made = True
        
        if fixes_made:
            # Validate syntax before writing
            if self.validate_syntax():
                with open(self.test_file_path, 'w') as f:
                    f.write(self.content)
                print(f"✅ Applied {len(self.fixes_applied)} fixes")
                for fix in self.fixes_applied:
                    print(f"   - {fix}")
                return True
            else:
                print("❌ Syntax validation failed, reverting changes")
                return False
        else:
            print("ℹ️  No automated fixes needed")
            return False
    
    def get_complexity_level(self) -> str:
        """Get complexity level based on score."""
        if self.complexity_score < 50:
            return "LOW"
        elif self.complexity_score < 100:
            return "MEDIUM"
        else:
            return "HIGH"

def main():
    """Main function to fix complex test files."""
    test_dir = Path("tests/unit/agents")
    
    print("🔍 Analyzing complex test files...")
    
    for test_file in test_dir.glob("test_*.py"):
        print(f"\n📁 Analyzing {test_file.name}...")
        
        fixer = ComplexTestFileFixer(str(test_file))
        metrics = fixer.analyze_complexity()
        complexity_level = fixer.get_complexity_level()
        
        print(f"   Complexity Level: {complexity_level} (Score: {fixer.complexity_score:.1f})")
        print(f"   Total Lines: {metrics['total_lines']}")
        print(f"   Trailing Commas: {metrics['trailing_commas']}")
        print(f"   Mock Data Issues: {metrics['mock_data_issues']}")
        print(f"   Await Issues: {metrics['await_outside_async']}")
        print(f"   Syntax Errors: {metrics['syntax_errors']}")
        
        if complexity_level in ["MEDIUM", "HIGH"]:
            print(f"   🎯 Applying fixes for {complexity_level} complexity file...")
            fixer.apply_fixes()
        else:
            print(f"   ℹ️  {complexity_level} complexity - no fixes needed")

if __name__ == "__main__":
    main() 