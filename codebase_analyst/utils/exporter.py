"""
Export analysis results to various formats (JSON, Markdown, HTML).
"""
import json
import shutil
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

class ResultExporter:
    """Export query results and analysis to multiple formats"""
    
    def __init__(self, output_dir: Path = None):
        self.output_dir = output_dir or Path("exports")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def export_to_json(self, data: Dict[str, Any], filename: str) -> Path:
        """Export data to JSON"""
        filepath = self.output_dir / f"{filename}.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return filepath
    
    def export_to_markdown(self, query: str, answer: str, contexts: List[Dict], 
                          metadata: Dict = None, filename: str = "report") -> Path:
        """Export query result to Markdown"""
        filepath = self.output_dir / f"{filename}.md"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# Codebase Analysis Report\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            if metadata:
                f.write(f"## Metadata\n\n")
                for key, value in metadata.items():
                    f.write(f"- **{key}**: {value}\n")
                f.write("\n")
            
            f.write(f"## Query\n\n```\n{query}\n```\n\n")
            f.write(f"## Answer\n\n{answer}\n\n")
            
            f.write(f"## Retrieved Context ({len(contexts)} chunks)\n\n")
            for i, ctx in enumerate(contexts, 1):
                payload = ctx.get('payload', ctx)
                f.write(f"### Context {i}\n\n")
                f.write(f"- **File**: `{payload['file_path']}`\n")
                f.write(f"- **Lines**: {payload['start_line']}-{payload['end_line']}\n")
                f.write(f"- **Score**: {ctx.get('score', 'N/A')}\n\n")
                f.write(f"```{payload.get('language', '')}\n")
                f.write(f"{payload['content']}\n")
                f.write(f"```\n\n")
        
        return filepath
    
    def export_to_html(self, query: str, answer: str, contexts: List[Dict],
                      metadata: Dict = None, filename: str = "report") -> Path:
        """Export query result to HTML"""
        filepath = self.output_dir / f"{filename}.html"
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Codebase Analysis Report</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; 
               max-width: 1200px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #2c3e50; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        .metadata {{ background: #f8f9fa; padding: 15px; border-radius: 5px; }}
        .query {{ background: #e8f4f8; padding: 15px; border-left: 4px solid #3498db; }}
        .answer {{ background: #e8f5e9; padding: 15px; border-left: 4px solid #4caf50; }}
        .context {{ background: #fff3cd; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        pre {{ background: #f4f4f4; padding: 10px; overflow-x: auto; border-radius: 3px; }}
        code {{ font-family: 'Courier New', monospace; }}
        .file-info {{ color: #666; font-size: 0.9em; }}
    </style>
</head>
<body>
    <h1>🔍 Codebase Analysis Report</h1>
    <p><em>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</em></p>
"""
        
        if metadata:
            html += "<div class='metadata'><h2>Metadata</h2><ul>"
            for key, value in metadata.items():
                html += f"<li><strong>{key}</strong>: {value}</li>"
            html += "</ul></div>"
        
        html += f"""
    <h2>Query</h2>
    <div class='query'><code>{query}</code></div>
    
    <h2>Answer</h2>
    <div class='answer'>{answer.replace(chr(10), '<br>')}</div>
    
    <h2>Retrieved Context ({len(contexts)} chunks)</h2>
"""
        
        for i, ctx in enumerate(contexts, 1):
            payload = ctx.get('payload', ctx)
            html += f"""
    <div class='context'>
        <h3>Context {i}</h3>
        <div class='file-info'>
            <strong>File:</strong> {payload['file_path']}<br>
            <strong>Lines:</strong> {payload['start_line']}-{payload['end_line']}<br>
            <strong>Score:</strong> {ctx.get('score', 'N/A')}
        </div>
        <pre><code>{payload['content']}</code></pre>
    </div>
"""
        
        html += """
</body>
</html>
"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return filepath
    
    def create_summary_report(self, results: List[Dict[str, Any]], filename: str = "summary") -> Dict[str, Path]:
        """Create summary report in multiple formats"""
        summary_data = {
            'total_queries': len(results),
            'generated_at': datetime.now().isoformat(),
            'results': results
        }
        
        json_path = self.export_to_json(summary_data, filename)
        
        return {
            'json': json_path,
            'output_dir': self.output_dir
        }
