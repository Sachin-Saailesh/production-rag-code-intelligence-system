"""
Architecture pattern detection and analysis.
Identifies common patterns like MVC, layered architecture, microservices, etc.
"""
from typing import List, Dict, Any
from collections import Counter
import re

class ArchitectureAnalyzer:
    """Detect and analyze architectural patterns in codebases"""
    
    def __init__(self, chunks: List[Dict[str, Any]]):
        self.chunks = chunks
        self.files = list(set(c['file_path'] for c in chunks))
    
    def detect_patterns(self) -> Dict[str, Any]:
        """Detect common architectural patterns"""
        patterns = {
            'mvc': self._detect_mvc(),
            'layered': self._detect_layered(),
            'microservices': self._detect_microservices(),
            'monolithic': self._detect_monolithic(),
        }
        
        # Determine primary pattern
        pattern_scores = {k: v['confidence'] for k, v in patterns.items() if v['detected']}
        primary = max(pattern_scores.items(), key=lambda x: x[1])[0] if pattern_scores else 'unknown'
        
        return {
            'primary_pattern': primary,
            'detected_patterns': patterns,
            'file_count': len(self.files),
            'component_analysis': self._analyze_components()
        }
    
    def _detect_mvc(self) -> Dict[str, Any]:
        """Detect MVC pattern"""
        mvc_indicators = {
            'models': 0,
            'views': 0,
            'controllers': 0
        }
        
        for f in self.files:
            f_lower = f.lower()
            if 'model' in f_lower:
                mvc_indicators['models'] += 1
            if 'view' in f_lower or 'template' in f_lower:
                mvc_indicators['views'] += 1
            if 'controller' in f_lower or 'handler' in f_lower:
                mvc_indicators['controllers'] += 1
        
        detected = all(count > 0 for count in mvc_indicators.values())
        confidence = sum(mvc_indicators.values()) / len(self.files) if self.files else 0
        
        return {
            'detected': detected,
            'confidence': min(confidence, 1.0),
            'details': mvc_indicators
        }
    
    def _detect_layered(self) -> Dict[str, Any]:
        """Detect layered architecture"""
        layers = {
            'presentation': 0,
            'business': 0,
            'data': 0,
            'infrastructure': 0
        }
        
        for f in self.files:
            f_lower = f.lower()
            if any(x in f_lower for x in ['ui', 'views', 'frontend', 'presentation']):
                layers['presentation'] += 1
            if any(x in f_lower for x in ['service', 'business', 'logic', 'domain']):
                layers['business'] += 1
            if any(x in f_lower for x in ['data', 'repository', 'dao', 'database']):
                layers['data'] += 1
            if any(x in f_lower for x in ['util', 'helper', 'config', 'infrastructure']):
                layers['infrastructure'] += 1
        
        detected = sum(1 for c in layers.values() if c > 0) >= 3
        confidence = sum(1 for c in layers.values() if c > 0) / 4
        
        return {
            'detected': detected,
            'confidence': confidence,
            'details': layers
        }
    
    def _detect_microservices(self) -> Dict[str, Any]:
        """Detect microservices architecture"""
        service_indicators = []
        
        for f in self.files:
            if 'service' in f.lower() and ('api' in f.lower() or 'grpc' in f.lower()):
                service_indicators.append(f)
        
        detected = len(service_indicators) >= 2
        confidence = min(len(service_indicators) / 5, 1.0)
        
        return {
            'detected': detected,
            'confidence': confidence,
            'details': {'service_count': len(service_indicators)}
        }
    
    def _detect_monolithic(self) -> Dict[str, Any]:
        """Detect monolithic architecture"""
        # Simplified: large number of files in a single directory structure
        detected = len(self.files) > 50
        confidence = min(len(self.files) / 200, 1.0)
        
        return {
            'detected': detected,
            'confidence': confidence,
            'details': {'file_count': len(self.files)}
        }
    
    def _analyze_components(self) -> Dict[str, Any]:
        """Analyze codebase components"""
        extensions = Counter()
        for f in self.files:
            ext = f.split('.')[-1] if '.' in f else 'no_extension'
            extensions[ext] += 1
        
        return {
            'file_types': dict(extensions.most_common(10)),
            'total_files': len(self.files)
        }
    
    def get_summary(self) -> str:
        """Get human-readable architecture summary"""
        analysis = self.detect_patterns()
        pattern = analysis['primary_pattern']
        
        summaries = {
            'mvc': "MVC (Model-View-Controller) pattern detected",
            'layered': "Layered architecture with separation of concerns",
            'microservices': "Microservices architecture with distributed services",
            'monolithic': "Monolithic architecture with centralized structure",
            'unknown': "Architecture pattern unclear from file structure"
        }
        
        return summaries.get(pattern, "Unknown architecture")
