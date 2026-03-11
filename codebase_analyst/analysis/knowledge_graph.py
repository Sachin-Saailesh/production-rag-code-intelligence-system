"""
Code knowledge graph and impact analysis using NetworkX.
Tracks dependencies, function calls, and analyzes change impact.
"""
import networkx as nx
from typing import List, Dict, Any, Set
from pathlib import Path
import re

class CodeKnowledgeGraph:
    """Build and query dependency graphs from parsed code"""
    
    def __init__(self):
        self.graph = nx.DiGraph()
        self.file_map: Dict[str, Dict[str, Any]] = {}
    
    def add_file(self, file_path: str, functions: List[Dict], classes: List[Dict], imports: List[str]):
        """Add file node with its components"""
        self.file_map[file_path] = {
            'functions': functions,
            'classes': classes,
            'imports': imports
        }
        
        # Add file node
        self.graph.add_node(file_path, type='file')
        
        # Add function nodes
        for func in functions:
            func_id = f"{file_path}::{func['name']}"
            self.graph.add_node(func_id, type='function', **func)
            self.graph.add_edge(file_path, func_id, relationship='contains')
        
        # Add class nodes
        for cls in classes:
            cls_id = f"{file_path}::{cls['name']}"
            self.graph.add_node(cls_id, type='class', **cls)
            self.graph.add_edge(file_path, cls_id, relationship='contains')
            
            # Add methods
            for method in cls.get('methods', []):
                method_id = f"{cls_id}.{method}"
                self.graph.add_node(method_id, type='method', name=method)
                self.graph.add_edge(cls_id, method_id, relationship='has_method')
        
        # Add import edges
        for imp in imports:
            # Try to find imported module in our graph
            potential_files = [f for f in self.file_map.keys() if imp in f]
            for imp_file in potential_files:
                self.graph.add_edge(file_path, imp_file, relationship='imports')
    
    def build_from_chunks(self, chunks: List[Dict[str, Any]]):
        """Build graph from parsed chunks"""
        # Group by file
        files_data = {}
        for chunk in chunks:
            fp = chunk['file_path']
            if fp not in files_data:
                files_data[fp] = {'functions': [], 'classes': []}
            
            files_data[fp]['functions'].extend(chunk.get('functions', []))
            files_data[fp]['classes'].extend(chunk.get('classes', []))
        
        # Add each file (simplified - no import tracking here)
        for fp, data in files_data.items():
            self.add_file(fp, data['functions'], data['classes'], [])
    
    def get_dependencies(self, file_path: str) -> List[str]:
        """Get files that this file depends on"""
        if file_path not in self.graph:
            return []
        return [n for n in self.graph.successors(file_path) if self.graph.nodes[n].get('type') == 'file']
    
    def get_dependents(self, file_path: str) -> List[str]:
        """Get files that depend on this file"""
        if file_path not in self.graph:
            return []
        return [n for n in self.graph.predecessors(file_path) if self.graph.nodes[n].get('type') == 'file']
    
    def find_central_files(self, top_k: int = 10) -> List[tuple]:
        """Find most central/important files using PageRank"""
        file_subgraph = self.graph.subgraph([n for n in self.graph.nodes if self.graph.nodes[n].get('type') == 'file'])
        pagerank = nx.pagerank(file_subgraph)
        return sorted(pagerank.items(), key=lambda x: -x[1])[:top_k]

class ImpactAnalyzer:
    """Analyze impact of code changes using the knowledge graph"""
    
    def __init__(self, knowledge_graph: CodeKnowledgeGraph):
        self.kg = knowledge_graph
    
    def analyze_file_impact(self, file_path: str) -> Dict[str, Any]:
        """Analyze impact if a file is modified"""
        direct_dependents = self.kg.get_dependents(file_path)
        
        # Get transitive closure (all affected files)
        affected = set()
        to_visit = set(direct_dependents)
        visited = set()
        
        while to_visit:
            current = to_visit.pop()
            if current in visited:
                continue
            visited.add(current)
            affected.add(current)
            
            deps = self.kg.get_dependents(current)
            to_visit.update(deps)
        
        return {
            'file': file_path,
            'direct_dependents': len(direct_dependents),
            'total_affected_files': len(affected),
            'affected_files': list(affected)[:20],  # Limit for display
            'risk_level': self._calculate_risk(len(affected))
        }
    
    def _calculate_risk(self, num_affected: int) -> str:
        """Calculate risk level based on number of affected files"""
        if num_affected == 0:
            return 'low'
        elif num_affected < 5:
            return 'medium'
        else:
            return 'high'
    
    def find_critical_paths(self, from_file: str, to_file: str) -> List[List[str]]:
        """Find dependency paths between two files"""
        try:
            paths = list(nx.all_simple_paths(self.kg.graph, from_file, to_file, cutoff=5))
            return paths[:5]  # Limit to 5 paths
        except (nx.NodeNotFound, nx.NetworkXNoPath):
            return []
