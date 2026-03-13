"""
Comprehensive Gradio UI with all advanced features.
Includes: Query, Impact Analysis, Architecture, Security.
"""
import gradio as gr
import logging

logger = logging.getLogger(__name__)


def create_ui():
    """Create and return the Gradio UI demo."""
    # Lazy imports to avoid circular dependency issues
    from ..core import run_ingestion, get_system_components, CodeTools
    from ..services.retrieval import run_retrieval
    from ..services.answering import generate_answer
    from ..analysis.knowledge_graph import CodeKnowledgeGraph, ImpactAnalyzer
    from ..analysis.architecture import ArchitectureAnalyzer
    from ..analysis.security import SecurityAnalyzer

    # Global state
    _analyst_data = {}

    # Attempt to pre-load existing embeddings on startup
    try:
        _analyst_data["components"] = get_system_components()
        initial_status = "System Ready: Existing Index Database loaded. Querying available."
    except Exception:
        initial_status = "System Idle: No index loaded. Please initialize a repository."

    def load_system(repo_url=None, repo_name=None, progress=gr.Progress(track_tqdm=True)):
        """Run ingestion with tqdm progress tracking automatically wired to UI."""
        try:
            progress(0, desc="Initializing Telemetry and Ingestion Pipeline...")
            result = run_ingestion(repo_url=repo_url or None, repo_name=repo_name or None)
            
            progress(0.95, desc="Loading active components into memory...")
            _analyst_data["components"] = get_system_components(repo_name=result["repo_name"])
            
            msg = f"Ingestion Complete. Processed {result['files_processed']} files. Generated {result['chunks_created']} vector embeddings."
            if result.get('files_skipped'):
                msg += f" (Skipped {result['files_skipped']} unchanged components)"
            return msg
        except Exception as e:
            logger.exception("Ingestion failed")
            return f"Error: {str(e)}"

    def query_codebase(question, top_k):
        if "components" not in _analyst_data:
            return "Error: System not initialized. Please load the index via the Database Management panel."

        components = _analyst_data["components"]
        try:
            retrieval_result = run_retrieval(
                query=question,
                hybrid_retriever=components["hybrid_retriever"],
                chunks=components["all_chunks"],
                knowledge_graph=components.get("knowledge_graph"),
                top_k=int(top_k),
            )
            answer_result = generate_answer(
                query=question,
                candidates=retrieval_result["candidates"],
                query_type=retrieval_result["query_type"],
            )

            response = f"## Contextual Analysis\n\n{answer_result['answer']}\n\n"
            response += f"### System Telemetry\n"
            response += f"- **Classification Pipeline**: `{retrieval_result['query_type'].upper()}`\n"
            response += f"- **LLM Generation Latency**: `{answer_result['llm_latency_ms']:.0f}ms`\n"
            response += f"- **Vector Search Latency**: `{retrieval_result['retrieval_latency_ms']:.0f}ms`\n"
            response += f"- **Neural Reranking Latency**: `{retrieval_result.get('rerank_latency_ms', 0):.0f}ms`\n"
            response += f"- **Vector Documents Retrieved**: `{len(retrieval_result['candidates'])}`\n"
            return response
        except Exception as e:
            logger.exception("Query failed")
            return f"Error: {str(e)}"

    def show_architecture():
        if "components" not in _analyst_data:
            return "Error: System not initialized."
        chunks = _analyst_data["components"]["all_chunks"]
        analyzer = ArchitectureAnalyzer(chunks)
        arch = analyzer.detect_patterns()

        response = f"# Architectural Paradigm Assessment\n\n"
        response += f"**Primary Topological Pattern:** `{arch['primary_pattern'].upper()}`\n"
        response += f"**Target Files Actively Evaluated:** `{arch['file_count']}`\n\n"
        response += "### Diagnostic Breakdown (System Confidence):\n\n"
        for pattern, details in arch['detected_patterns'].items():
            if details['detected']:
                response += f"- **{pattern.upper()}**: `{details['confidence']:.2f}`\n"
        return response

    def scan_security(include_tests):
        if "components" not in _analyst_data:
            return "Error: System not initialized."
        chunks = _analyst_data["components"]["all_chunks"]
        analyzer = SecurityAnalyzer(chunks, include_tests=include_tests)
        scan = analyzer.scan()

        response = f"# Static Vulerability Audit\n\n"
        response += f"**Current Aggregate Risk Score:** `{scan['risk_score']} / 100`\n"
        response += f"**Categorized Flags Detected:** `{scan['total_findings']}`\n\n"
        response += "### Vulnerability Stratification:\n"
        for sev, count in scan['by_severity'].items():
            response += f"- **{sev.upper()}**: `{count}`\n"
        if scan['findings']:
            response += "\n### Priority Trace Audit:\n\n"
            for finding in scan['findings'][:10]:
                response += f"#### {finding['type']} ({finding['severity'].upper()})\n"
                response += f"- **Location:** `{finding['file']} : Line {finding['line']}`\n"
                response += f"- **Definition:** {finding['description']}\n\n"
        return response

    custom_theme = gr.themes.Soft(
        primary_hue="slate",
        secondary_hue="zinc",
        neutral_hue="gray",
        font=[gr.themes.GoogleFont("Inter"), "ui-sans-serif", "system-ui", "sans-serif"],
        font_mono=[gr.themes.GoogleFont("Fira Code"), "ui-monospace", "Consolas", "monospace"],
    ).set(
        body_background_fill="*neutral_950",
        body_background_fill_dark="*neutral_950",
        body_text_color="*neutral_200",
        button_primary_background_fill="*primary_600",
        block_background_fill="*neutral_900",
        block_border_width="1px",
        block_border_color="*neutral_800",
        border_color_primary="*neutral_700",
    )

    with gr.Blocks(title="Codebase AI Platform", theme=custom_theme) as demo:
        with gr.Row():
            with gr.Column(scale=4):
                gr.Markdown(
                    """
                    # Code Intelligence Control Plane
                    *Enterprise Context Engine for Architectural RAG and Automated Codebase Auditing.*
                    """
                )
            with gr.Column(scale=1, min_width=150):
                gr.HTML(
                    """
                    <div style="text-align: right; margin-top: 20px;">
                        <a href="/docs" target="_blank" style="text-decoration: none; font-weight: 600; padding: 8px 16px; background: #2563eb; color: white; border-radius: 6px; font-size: 14px; transition: background 0.2s;">
                            Open API Docs (Swagger) ↗
                        </a>
                    </div>
                    """
                )
        
        with gr.Group():
            gr.Markdown(
                """
                ### System Capabilities Overview
                - **Repository Management**: Initializes the static file taxonomy and computes dense vector embeddings for subsequent query targeting.
                - **Semantic Investigation**: Executes natural language instructions against the indexed Context Engine using Azure OpenAI and hybrid retrieval.
                - **Topological Profiler**: Evaluates exact architectural paradigms based on AST dependency configurations and module tree density.
                - **Security Exfiltration**: Conducts continuous inspection for zero-day vulnerabilities, deterministic secret leaks, and cryptographic flaws.
                """
            )
        
        with gr.Row():
            # Left Column (Setup & System State)
            with gr.Column(scale=1):
                gr.Markdown("### Repository Management")
                gr.Markdown("Provide a remote Git URI or local mount directory to compute Vector embeddings, extract AST taxonomies, and populate semantic cache.")
                repo_url_input = gr.Textbox(label="Target Source", placeholder="https://github.com/organization/svc.git")
                repo_name_input = gr.Textbox(label="Workspace UUID", placeholder="core-authentication-svc")
                load_btn = gr.Button("Initialize Context Database", variant="primary")
                
                gr.Markdown("### Service Telemetry")
                status = gr.Textbox(label="Database Status", value=initial_status, interactive=False, lines=2)
                
                load_btn.click(fn=load_system, inputs=[repo_url_input, repo_name_input], outputs=[status])
                
            # Right Column (Queries and Analysis)
            with gr.Column(scale=2):
                with gr.Tabs():
                    with gr.Tab("Semantic Investigation"):
                        gr.Markdown("Interface for natural language execution. Context dynamically constructs via topological graph expansion, BM25 statistical routing, and Cohere semantic reranking.")
                        with gr.Row():
                            query_input = gr.Textbox(label="Query Input", placeholder="Explain the primary JWT verification flow implementation...", lines=3, scale=4)
                            top_k_slider = gr.Slider(minimum=1, maximum=20, value=7, step=1, label="Retrieval Hyper-Parameter (K)", scale=1)
                        query_btn = gr.Button("Execute Analysis", variant="primary")
                        query_output = gr.Markdown(label="Generation Output")
                        query_btn.click(fn=query_codebase, inputs=[query_input, top_k_slider], outputs=[query_output])

                    with gr.Tab("Topological Profiler"):
                        gr.Markdown("Evaluates exact architectural paradigms based on AST dependency configurations and module tree density.")
                        arch_btn = gr.Button("Compute Blueprint Metrics", variant="primary")
                        arch_output = gr.Markdown()
                        arch_btn.click(fn=show_architecture, inputs=[], outputs=[arch_output])

                    with gr.Tab("Security Exfiltration"):
                        gr.Markdown("Conducts continuous inspection over normalized AST representations for zero-day vulnerabilities, deterministic secret leaks, and cryptographic flaws.")
                        with gr.Row():
                            sec_include_tests = gr.Checkbox(label="Include Test Suites & Documentation in Scan", value=False)
                            sec_btn = gr.Button("Execute Static Vulnerability Scan", variant="secondary")
                        sec_output = gr.Markdown()
                        sec_btn.click(fn=scan_security, inputs=[sec_include_tests], outputs=[sec_output])

    return demo
