"""Parse source code using tree-sitter and Python AST."""
import logging
import ast as python_ast
from pathlib import Path
from typing import Dict, Any, List

from ..config import settings

logger = logging.getLogger(__name__)

# Tree-sitter setup
try:
    from tree_sitter import Parser
    from tree_sitter_languages import get_language

    _LANGUAGES = {}
    for lang in ["python", "javascript", "typescript", "java", "go", "rust", "c", "cpp", "ruby"]:
        try:
            _LANGUAGES[lang] = get_language(lang)
        except Exception:
            pass

    TREE_SITTER_AVAILABLE = True
except ImportError:
    logger.info("tree-sitter not available — using AST/regex fallbacks")
    Parser = None
    _LANGUAGES = {}
    TREE_SITTER_AVAILABLE = False


class CodeParser:
    """Parse source code using tree-sitter and Python AST."""

    SUPPORTED_EXTENSIONS = {
        ".py": "python", ".js": "javascript", ".ts": "typescript",
        ".tsx": "typescript", ".jsx": "javascript",
        ".java": "java", ".go": "go", ".rs": "rust",
        ".c": "c", ".cpp": "cpp", ".cxx": "cpp", ".cc": "cpp",
        ".h": "c", ".hpp": "cpp", ".rb": "ruby",
    }

    def __init__(self):
        self.parser = Parser() if Parser else None

    def parse_file(self, file_path: Path) -> Dict[str, Any]:
        """Parse a source file and extract structured information."""
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            if len(content) > settings.max_file_size:
                return None

            ext = file_path.suffix.lower()
            lang = self.SUPPORTED_EXTENSIONS.get(ext)
            if not lang:
                return None

            if lang == "python":
                return self._parse_python(file_path, content)

            if TREE_SITTER_AVAILABLE and lang in _LANGUAGES:
                return self._parse_tree_sitter(file_path, content, lang)

            return self._parse_generic(file_path, content, lang)

        except Exception as e:
            logger.debug("Error parsing %s: %s", file_path, e)
            return None

    def _parse_python(self, file_path: Path, content: str) -> Dict[str, Any]:
        """Parse Python file using built-in AST."""
        try:
            tree = python_ast.parse(content)
            functions, classes, imports = [], [], []

            for node in python_ast.walk(tree):
                if isinstance(node, python_ast.FunctionDef):
                    functions.append({
                        "name": node.name,
                        "lineno": node.lineno,
                        "end_lineno": getattr(node, "end_lineno", node.lineno + 5),
                        "docstring": python_ast.get_docstring(node),
                        "args": [arg.arg for arg in node.args.args],
                    })
                elif isinstance(node, python_ast.ClassDef):
                    classes.append({
                        "name": node.name,
                        "lineno": node.lineno,
                        "end_lineno": getattr(node, "end_lineno", node.lineno + 10),
                        "docstring": python_ast.get_docstring(node),
                        "methods": [m.name for m in node.body if isinstance(m, python_ast.FunctionDef)],
                    })
                elif isinstance(node, (python_ast.Import, python_ast.ImportFrom)):
                    if isinstance(node, python_ast.Import):
                        imports.extend([alias.name for alias in node.names])
                    elif node.module:
                        imports.append(node.module)

            return {
                "file_path": str(file_path),
                "language": "python",
                "content": content,
                "functions": functions,
                "classes": classes,
                "imports": imports,
                "lines": len(content.splitlines()),
            }
        except SyntaxError:
            return self._parse_generic(file_path, content, "python")

    def _parse_tree_sitter(self, file_path: Path, content: str, lang: str) -> Dict[str, Any]:
        """Parse using tree-sitter for non-Python languages."""
        try:
            self.parser.set_language(_LANGUAGES[lang])
            tree = self.parser.parse(content.encode())

            functions, classes, imports = [], [], []
            self._walk_tree(tree.root_node, functions, classes, imports, lang)

            return {
                "file_path": str(file_path),
                "language": lang,
                "content": content,
                "functions": functions,
                "classes": classes,
                "imports": imports,
                "lines": len(content.splitlines()),
            }
        except Exception as e:
            logger.debug("Tree-sitter parse error for %s: %s", file_path, e)
            return self._parse_generic(file_path, content, lang)

    def _walk_tree(self, node, functions, classes, imports, lang):
        """Walk tree-sitter AST and extract symbols."""
        type_name = node.type

        # Function detection
        func_types = {"function_definition", "function_declaration", "method_definition",
                       "arrow_function", "function_item"}
        if type_name in func_types:
            name = self._get_name(node)
            if name:
                functions.append({
                    "name": name,
                    "lineno": node.start_point[0] + 1,
                    "end_lineno": node.end_point[0] + 1,
                })

        # Class detection
        class_types = {"class_definition", "class_declaration", "struct_item", "impl_item"}
        if type_name in class_types:
            name = self._get_name(node)
            if name:
                classes.append({
                    "name": name,
                    "lineno": node.start_point[0] + 1,
                    "end_lineno": node.end_point[0] + 1,
                    "methods": [],
                })

        # Import detection
        import_types = {"import_statement", "import_declaration", "use_declaration"}
        if type_name in import_types:
            imports.append(node.text.decode("utf-8", errors="ignore"))

        for child in node.children:
            self._walk_tree(child, functions, classes, imports, lang)

    def _get_name(self, node) -> str:
        """Extract name from a tree-sitter node."""
        for child in node.children:
            if child.type in ("identifier", "name", "property_identifier"):
                return child.text.decode("utf-8", errors="ignore")
        return ""

    def _parse_generic(self, file_path: Path, content: str, lang: str = "unknown") -> Dict[str, Any]:
        """Generic fallback parsing."""
        return {
            "file_path": str(file_path),
            "language": lang,
            "content": content,
            "functions": [],
            "classes": [],
            "imports": [],
            "lines": len(content.splitlines()),
        }
