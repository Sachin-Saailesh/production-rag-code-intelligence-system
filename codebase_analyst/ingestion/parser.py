import os
import ast as python_ast
from pathlib import Path
from typing import Dict, Any, List
from ..config import config

# Tree-sitter setup
try:
    import tree_sitter
    from tree_sitter import Language, Parser
    
    # Try new tree-sitter API first (0.22+), then fallback
    try:
        from tree_sitter_languages import get_language
        py_lang = get_language("python")
        js_lang = get_language("javascript")
    except ImportError:
        # Fallback manual build (generic stub, assuming pre-built in env)
        py_lang = None
        js_lang = None
        print("Warning: tree-sitter-languages not found. Code parsing might be limited.")
except ImportError:
    print("Warning: tree-sitter not found. Code parsing will rely on simple fallbacks.")
    Parser = None
    py_lang = None

class CodeParser:
    """Parse source code using tree-sitter and Python AST"""

    def __init__(self):
        self.supported_extensions = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
        }
        self.parser = Parser() if Parser else None

    def set_language(self, lang_name: str):
        if not self.parser:
            return
        if lang_name == 'python' and py_lang:
            self.parser.set_language(py_lang)
        elif lang_name == 'javascript' and js_lang:
            self.parser.set_language(js_lang)

    def parse_file(self, file_path: Path) -> Dict[str, Any]:
        """Parse a source file and extract structured information"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Skip if too large
            if len(content) > config.max_file_size:
                return None

            ext = file_path.suffix
            if ext not in self.supported_extensions:
                return None

            # For Python, use AST (built-in is reliable)
            if ext == '.py':
                return self._parse_python(file_path, content)
            else:
                # For other languages, use simple extraction or tree-sitter if configured
                return self._parse_generic(file_path, content)

        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return None

    def _parse_python(self, file_path: Path, content: str) -> Dict[str, Any]:
        """Parse Python file using AST"""
        try:
            tree = python_ast.parse(content)

            functions = []
            classes = []
            imports = []

            for node in python_ast.walk(tree):
                if isinstance(node, python_ast.FunctionDef):
                    functions.append({
                        'name': node.name,
                        'lineno': node.lineno,
                        'docstring': python_ast.get_docstring(node),
                        'args': [arg.arg for arg in node.args.args],
                    })
                elif isinstance(node, python_ast.ClassDef):
                    classes.append({
                        'name': node.name,
                        'lineno': node.lineno,
                        'docstring': python_ast.get_docstring(node),
                        'methods': [m.name for m in node.body if isinstance(m, python_ast.FunctionDef)]
                    })
                elif isinstance(node, (python_ast.Import, python_ast.ImportFrom)):
                    if isinstance(node, python_ast.Import):
                        imports.extend([alias.name for alias in node.names])
                    else:
                        if node.module:
                            imports.append(node.module)

            return {
                'file_path': str(file_path),
                'language': 'python',
                'content': content,
                'functions': functions,
                'classes': classes,
                'imports': imports,
                'lines': len(content.split('\n'))
            }
        except SyntaxError:
            return self._parse_generic(file_path, content)

    def _parse_generic(self, file_path: Path, content: str) -> Dict[str, Any]:
        """Generic parsing for non-Python files"""
        return {
            'file_path': str(file_path),
            'language': self.supported_extensions.get(file_path.suffix, 'unknown'),
            'content': content,
            'functions': [],
            'classes': [],
            'imports': [],
            'lines': len(content.split('\n'))
        }
