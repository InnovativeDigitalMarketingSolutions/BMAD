"""
BMAD Architecture Quality Metrics

Metrics voor het meten van architectuur kwaliteit.
Inclusief coupling, cohesion, en modularity metrics.
"""

import ast
import logging
import os
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any
from collections import defaultdict

logger = logging.getLogger(__name__)

class ArchitectureMetrics:
    """
    Architecture quality metrics voor BMAD.
    """
    
    def __init__(self, base_path: str = "bmad"):
        self.base_path = Path(base_path)
        self.metrics: Dict[str, Any] = {}
    
    def analyze_codebase(self) -> Dict[str, Any]:
        """
        Analyze de hele codebase voor architecture metrics.
        
        Returns:
            Dict met alle metrics
        """
        logger.info("Starting architecture analysis...")
        
        # Collect all Python files
        python_files = list(self.base_path.rglob("*.py"))
        
        # Analyze each file
        file_metrics = {}
        for file_path in python_files:
            try:
                metrics = self._analyze_file(file_path)
                file_metrics[str(file_path)] = metrics
            except Exception as e:
                logger.warning(f"Failed to analyze {file_path}: {e}")
        
        # Calculate overall metrics
        overall_metrics = self._calculate_overall_metrics(file_metrics)
        
        # Store results
        self.metrics = {
            "files": file_metrics,
            "overall": overall_metrics,
            "summary": self._generate_summary(overall_metrics)
        }
        
        return self.metrics
    
    def _analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Analyze een individueel Python file.
        
        Args:
            file_path: Path naar het Python file
            
        Returns:
            Dict met file metrics
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return {"error": "Syntax error in file"}
        
        # Analyze AST
        analyzer = FileAnalyzer()
        analyzer.visit(tree)
        
        return {
            "lines_of_code": len(content.splitlines()),
            "classes": len(analyzer.classes),
            "functions": len(analyzer.functions),
            "imports": len(analyzer.imports),
            "internal_imports": len(analyzer.internal_imports),
            "external_imports": len(analyzer.external_imports),
            "complexity": analyzer.calculate_complexity(),
            "coupling": analyzer.calculate_coupling(),
            "cohesion": analyzer.calculate_cohesion()
        }
    
    def _calculate_overall_metrics(self, file_metrics: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate overall metrics van alle files.
        
        Args:
            file_metrics: Metrics per file
            
        Returns:
            Overall metrics
        """
        total_files = len(file_metrics)
        total_lines = sum(m.get("lines_of_code", 0) for m in file_metrics.values() if "error" not in m)
        total_classes = sum(m.get("classes", 0) for m in file_metrics.values() if "error" not in m)
        total_functions = sum(m.get("functions", 0) for m in file_metrics.values() if "error" not in m)
        
        # Calculate averages
        avg_lines_per_file = total_lines / total_files if total_files > 0 else 0
        avg_classes_per_file = total_classes / total_files if total_files > 0 else 0
        avg_functions_per_file = total_functions / total_files if total_files > 0 else 0
        
        # Calculate coupling and cohesion
        coupling_scores = [m.get("coupling", 0) for m in file_metrics.values() if "error" not in m]
        cohesion_scores = [m.get("cohesion", 0) for m in file_metrics.values() if "error" not in m]
        
        avg_coupling = sum(coupling_scores) / len(coupling_scores) if coupling_scores else 0
        avg_cohesion = sum(cohesion_scores) / len(cohesion_scores) if cohesion_scores else 0
        
        return {
            "total_files": total_files,
            "total_lines": total_lines,
            "total_classes": total_classes,
            "total_functions": total_functions,
            "avg_lines_per_file": avg_lines_per_file,
            "avg_classes_per_file": avg_classes_per_file,
            "avg_functions_per_file": avg_functions_per_file,
            "avg_coupling": avg_coupling,
            "avg_cohesion": avg_cohesion,
            "modularity_score": self._calculate_modularity_score(avg_coupling, avg_cohesion)
        }
    
    def _calculate_modularity_score(self, coupling: float, cohesion: float) -> float:
        """
        Calculate modularity score based on coupling and cohesion.
        
        Args:
            coupling: Average coupling score
            cohesion: Average cohesion score
            
        Returns:
            Modularity score (0-100)
        """
        # Lower coupling is better, higher cohesion is better
        coupling_score = max(0, 100 - (coupling * 10))  # Scale coupling to 0-100
        cohesion_score = min(100, cohesion * 10)  # Scale cohesion to 0-100
        
        # Modularity is combination of low coupling and high cohesion
        modularity = (coupling_score + cohesion_score) / 2
        return round(modularity, 2)
    
    def _generate_summary(self, overall_metrics: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate human-readable summary van metrics.
        
        Args:
            overall_metrics: Overall metrics
            
        Returns:
            Summary dict
        """
        modularity_score = overall_metrics.get("modularity_score", 0)
        
        if modularity_score >= 80:
            modularity_grade = "Excellent"
        elif modularity_score >= 60:
            modularity_grade = "Good"
        elif modularity_score >= 40:
            modularity_grade = "Fair"
        else:
            modularity_grade = "Poor"
        
        return {
            "modularity_grade": modularity_grade,
            "modularity_score": f"{modularity_score}/100",
            "recommendations": self._generate_recommendations(overall_metrics)
        }
    
    def _generate_recommendations(self, metrics: Dict[str, Any]) -> List[str]:
        """
        Generate recommendations based on metrics.
        
        Args:
            metrics: Overall metrics
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        avg_coupling = metrics.get("avg_coupling", 0)
        avg_cohesion = metrics.get("avg_cohesion", 0)
        avg_lines_per_file = metrics.get("avg_lines_per_file", 0)
        
        if avg_coupling > 5:
            recommendations.append("Consider reducing coupling between modules")
        
        if avg_cohesion < 3:
            recommendations.append("Improve cohesion within modules")
        
        if avg_lines_per_file > 300:
            recommendations.append("Consider splitting large files into smaller modules")
        
        if not recommendations:
            recommendations.append("Architecture quality is good, maintain current practices")
        
        return recommendations

class FileAnalyzer(ast.NodeVisitor):
    """
    AST analyzer voor Python files.
    """
    
    def __init__(self):
        self.classes: List[str] = []
        self.functions: List[str] = []
        self.imports: List[str] = []
        self.internal_imports: List[str] = []
        self.external_imports: List[str] = []
        self.complexity_score = 0
    
    def visit_ClassDef(self, node: ast.ClassDef):
        """Visit class definitions."""
        self.classes.append(node.name)
        self.complexity_score += 1
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Visit function definitions."""
        self.functions.append(node.name)
        self.complexity_score += 1
        self.generic_visit(node)
    
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        """Visit async function definitions."""
        self.functions.append(node.name)
        self.complexity_score += 1
        self.generic_visit(node)
    
    def visit_Import(self, node: ast.Import):
        """Visit import statements."""
        for alias in node.names:
            self.imports.append(alias.name)
            if alias.name.startswith("bmad"):
                self.internal_imports.append(alias.name)
            else:
                self.external_imports.append(alias.name)
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node: ast.ImportFrom):
        """Visit from import statements."""
        if node.module:
            self.imports.append(node.module)
            if node.module.startswith("bmad"):
                self.internal_imports.append(node.module)
            else:
                self.external_imports.append(node.module)
        self.generic_visit(node)
    
    def visit_If(self, node: ast.If):
        """Visit if statements."""
        self.complexity_score += 1
        self.generic_visit(node)
    
    def visit_For(self, node: ast.For):
        """Visit for loops."""
        self.complexity_score += 1
        self.generic_visit(node)
    
    def visit_While(self, node: ast.While):
        """Visit while loops."""
        self.complexity_score += 1
        self.generic_visit(node)
    
    def visit_Try(self, node: ast.Try):
        """Visit try blocks."""
        self.complexity_score += 1
        self.generic_visit(node)
    
    def calculate_complexity(self) -> int:
        """Calculate cyclomatic complexity."""
        return self.complexity_score
    
    def calculate_coupling(self) -> float:
        """Calculate coupling score."""
        # Coupling is based on number of imports
        return len(self.imports) / max(1, len(self.classes) + len(self.functions))
    
    def calculate_cohesion(self) -> float:
        """Calculate cohesion score."""
        # Cohesion is based on internal vs external imports
        total_imports = len(self.imports)
        if total_imports == 0:
            return 5.0  # High cohesion if no dependencies
        
        internal_ratio = len(self.internal_imports) / total_imports
        return internal_ratio * 5.0  # Scale to 0-5

# Global architecture metrics
architecture_metrics = ArchitectureMetrics() 