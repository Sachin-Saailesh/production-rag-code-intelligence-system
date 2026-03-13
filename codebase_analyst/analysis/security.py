"""
Security vulnerability scanner.
Detects common security issues and anti-patterns.
"""
from typing import List, Dict, Any
import re

class SecurityAnalyzer:
    """Scan code for potential security vulnerabilities"""
    
    def __init__(self, chunks: List[Dict[str, Any]], include_tests: bool = False):
        self.chunks = chunks
        self.include_tests = include_tests
        self.vulnerability_patterns = {
            'hardcoded_secrets': {
                'patterns': [
                    r'password\s*=\s*["\']([^"\']+)["\']',
                    r'api_key\s*=\s*["\']([^"\']+)["\']',
                    r'secret\s*=\s*["\']([^"\']+)["\']',
                    r'token\s*=\s*["\']([^"\']+)["\']',
                ],
                'severity': 'high',
                'description': 'Hardcoded credentials detected'
            },
            'sql_injection': {
                'patterns': [
                    r'execute\([^)]*%s',
                    r'cursor\.execute\([^)]*\+',
                ],
                'severity': 'high',
                'description': 'Potential SQL injection vulnerability'
            },
            'insecure_random': {
                'patterns': [
                    r'import\s+random\b',
                    r'random\.random',
                    r'Math\.random',
                ],
                'severity': 'medium',
                'description': 'Use of insecure random number generator'
            },
            'eval_usage': {
                'patterns': [
                    r'\beval\s*\(',
                    r'\bexec\s*\(',
                ],
                'severity': 'high',
                'description': 'Dangerous use of eval/exec'
            },
            'debug_mode': {
                'patterns': [
                    r'DEBUG\s*=\s*True',
                    r'debug\s*=\s*True',
                ],
                'severity': 'medium',
                'description': 'Debug mode enabled'
            },
        }
    
    def scan(self) -> Dict[str, Any]:
        """Perform security scan"""
        findings = []
        
        for chunk in self.chunks:
            content = chunk['content']
            file_path = chunk['file_path']
            
            if not self.include_tests:
                # Fast semantic exclusion: Skip common test/doc/script paths
                path_lower = file_path.lower()
                if any(ignored in path_lower for ignored in ['/test', 'test_', 'docs/', 'docs_src/', 'tutorial', 'example', 'scripts/']):
                    continue
                # Skip chunks inside test functions/classes
                symbol = chunk.get('symbol_name', '').lower()
                if 'test' in symbol:
                    continue
            
            
            for vuln_type, config in self.vulnerability_patterns.items():
                for pattern in config['patterns']:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        findings.append({
                            'type': vuln_type,
                            'severity': config['severity'],
                            'description': config['description'],
                            'file': file_path,
                            'line': content[:match.start()].count('\n') + chunk.get('start_line', 1),
                            'snippet': match.group(0)[:100]
                        })
        
        return {
            'total_findings': len(findings),
            'by_severity': self._group_by_severity(findings),
            'findings': findings[:50],  # Limit for display
            'risk_score': self._calculate_risk_score(findings)
        }
    
    def _group_by_severity(self, findings: List[Dict]) -> Dict[str, int]:
        """Group findings by severity"""
        severity_count = {'high': 0, 'medium': 0, 'low': 0}
        for f in findings:
            severity_count[f['severity']] += 1
        return severity_count
    
    def _calculate_risk_score(self, findings: List[Dict]) -> int:
        """Calculate overall risk score (0-100)"""
        weights = {'high': 10, 'medium': 5, 'low': 1}
        score = sum(weights.get(f['severity'], 1) for f in findings)
        return min(score, 100)
    
    def get_recommendations(self, findings: List[Dict]) -> List[str]:
        """Get security recommendations based on findings"""
        recommendations = []
        
        finding_types = set(f['type'] for f in findings)
        
        if 'hardcoded_secrets' in finding_types:
            recommendations.append("Move secrets to environment variables or secret management service")
        if 'sql_injection' in finding_types:
            recommendations.append("Use parameterized queries or ORM for database access")
        if 'insecure_random' in finding_types:
            recommendations.append("Use secrets.SystemRandom() for cryptographic operations")
        if 'eval_usage' in finding_types:
            recommendations.append("Avoid eval/exec; use safer alternatives like ast.literal_eval")
        if 'debug_mode' in finding_types:
            recommendations.append("Disable debug mode in production environments")
        
        return recommendations
