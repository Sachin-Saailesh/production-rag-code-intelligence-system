"""
Comprehensive Gradio UI with all advanced features.
Includes: Query, Impact Analysis, Architecture, Security, Evaluation, Export.
"""
import gradio as gr
from ..core import EnhancedCodebaseAnalyst, reindex_repository, CodeTools
from ..retrieval.hybrid import HybridRetriever
from ..indexing.cache import SemanticCache
from ..caching.manager import CacheManager

# Global state
analyst: EnhancedCodebaseAnalyst = None
components_cache = {}

def load_system():
    global analyst, components_cache
    print("Initializing system...")
    components = reindex_repository()
    components_cache = components
    
    hybrid_retriever = HybridRetriever(
        vector_store=components['vector_store'],
        sparse_retriever=components['sparse_retriever'],
        embedding_engine=components['embedding_engine'],
        dense_weight=0.6
    )
    
    code_tools = CodeTools(components['repo_dir'], components['all_chunks'])
    cache = SemanticCache(components['embedding_engine'])
    
    analyst = EnhancedCodebaseAnalyst(
        hybrid_retriever=hybrid_retriever,
        code_tools=code_tools,
        chunks=components['all_chunks'],
        cache_manager=cache
    )
    return "✅ System Loaded! You can now use all tabs."

def chat(message, history):
    if not analyst:
        return "⚠️ Please load the system first using the Setup tab."
    
    result = analyst.analyze(message)
    return result["answer"]

def query_with_options(query, use_expansion, top_k):
    if not analyst:
        return "⚠️ Please load the system first."
    
    result = analyst.analyze_with_expansion(query, expand=use_expansion, top_k=top_k)
    
    # Format response
    response = f"**Answer:**\n\n{result['answer']}\n\n"
    response += f"**Metrics:**\n- Latency: {result['latency']:.2f}s\n- LLM Latency: {result['llm_latency']:.2f}s\n"
    response += f"- Chunks Retrieved: {len(result['context'])}\n"
    if result.get('query_expanded'):
        response += "- Query Expansion: Enabled\n"
    
    return response

def analyze_impact(file_path):
    if not analyst:
        return "⚠️ Please load the system first."
    
    try:
        impact = analyst.analyze_impact(file_path)
        
        response = f"# Impact Analysis: {file_path}\n\n"
        response += f"**Risk Level:** {impact['risk_level'].upper()}\n\n"
        response += f"**Direct Dependents:** {impact['direct_dependents']}\n"
        response += f"**Total Affected Files:** {impact['total_affected_files']}\n\n"
        
        if impact['affected_files']:
            response += "**Affected Files (sample):**\n"
            for f in impact['affected_files'][:10]:
                response += f"- `{f}`\n"
        
        return response
    except Exception as e:
        return f"Error: {e}"

def show_architecture():
    if not analyst:
        return "⚠️ Please load the system first."
    
    arch = analyst.show_architecture()
    
    response = f"# Architecture Analysis\n\n"
    response += f"**Primary Pattern:** {arch['primary_pattern'].upper()}\n\n"
    response += f"**Total Files:** {arch['file_count']}\n\n"
    
    response += "## Detected Patterns:\n\n"
    for pattern, details in arch['detected_patterns'].items():
        if details['detected']:
            response += f"- **{pattern.upper()}**: {details['confidence']:.1%} confidence\n"
    
    return response

def scan_security():
    if not analyst:
        return "⚠️ Please load the system first."
    
    scan = analyst.security_scan()
    
    response = f"# Security Scan Results\n\n"
    response += f"**Risk Score:** {scan['risk_score']}/100\n\n"
    response += f"**Total Findings:** {scan['total_findings']}\n\n"
    
    response += "## By Severity:\n"
    for sev, count in scan['by_severity'].items():
        response += f"- **{sev.upper()}**: {count}\n"
    
    if scan['findings']:
        response += "\n## Sample Findings:\n\n"
        for finding in scan['findings'][:10]:
            response += f"### {finding['type']} ({finding['severity']})\n"
            response += f"- **File:** `{finding['file']}`\n"
            response += f"- **Line:** {finding['line']}\n"
            response += f"- **Description:** {finding['description']}\n\n"
    
    return response

def export_last_result(format):
    # This would need access to the last query result
    # For now, return a message
    return f"Export functionality configured for format: {format}. Implement session storage to track last result."

def create_ui():
    with gr.Blocks(title="Enhanced Codebase Analyst", theme=gr.themes.Soft()) as demo:
        gr.Markdown("# 🚀 Enhanced Codebase Analyst (Azure OpenAI)\nAdvanced code analysis with monitoring, evaluation, and security scanning.")
        
        with gr.Tabs():
            # Tab 1: Setup
            with gr.Tab("⚙️ Setup"):
                gr.Markdown("### System Initialization\nLoad the repository and initialize all analyzers.")
                load_btn = gr.Button("🔄 Load/Reindex Repository", variant="primary", size="lg")
                status = gr.Textbox(label="Status", value="Not Loaded", interactive=False, lines=2)
                load_btn.click(fn=load_system, inputs=[], outputs=[status])
            
            # Tab 2: Query
            with gr.Tab("💬 Query"):
                gr.Markdown("### Ask Questions About the Codebase")
                
                with gr.Row():
                    with gr.Column(scale=3):
                        query_input = gr.Textbox(label="Your Question", placeholder="Where is the main entrypoint?", lines=3)
                    with gr.Column(scale=1):
                        expand_check = gr.Checkbox(label="Query Expansion", value=False)
                        top_k_slider = gr.Slider(minimum=1, maximum=20, value=8, step=1, label="Top K Results")
                
                query_btn = gr.Button("🔍 Analyze", variant="primary")
                query_output = gr.Markdown(label="Result")
                
                query_btn.click(
                    fn=query_with_options,
                    inputs=[query_input, expand_check, top_k_slider],
                    outputs=[query_output]
                )
            
            # Tab 3: Impact Analysis
            with gr.Tab("📊 Impact Analysis"):
                gr.Markdown("### Analyze Change Impact\nSee what would be affected if you modify a file.")
                file_input = gr.Textbox(label="File Path", placeholder="src/main.py")
                impact_btn = gr.Button("Analyze Impact", variant="primary")
                impact_output = gr.Markdown()
                
                impact_btn.click(fn=analyze_impact, inputs=[file_input], outputs=[impact_output])
            
            # Tab 3: Architecture
            with gr.Tab("🏗️ Architecture"):
                gr.Markdown("### Architecture Pattern Detection")
                arch_btn = gr.Button("Detect Architecture", variant="primary")
                arch_output = gr.Markdown()
                
                arch_btn.click(fn=show_architecture, inputs=[], outputs=[arch_output])
            
            # Tab 5: Security
            with gr.Tab("🔒 Security"):
                gr.Markdown("### Security Vulnerability Scan")
                sec_btn = gr.Button("Run Security Scan", variant="primary")
                sec_output = gr.Markdown()
                
                sec_btn.click(fn=scan_security, inputs=[], outputs=[sec_output])
            
            # Tab 6: Export
            with gr.Tab("📥 Export"):
                gr.Markdown("### Export Results\n*Note: Requires query to be run first.*")
                format_choice = gr.Radio(["markdown", "html", "json"], label="Export Format", value="markdown")
                export_btn = gr.Button("Export Last Result", variant="secondary")
                export_output = gr.Textbox(label="Export Status")
                
                export_btn.click(fn=export_last_result, inputs=[format_choice], outputs=[export_output])
        
        gr.Markdown("---\n**Tip:** Start with the Setup tab to load your repository, then explore other features!")
        
    return demo
