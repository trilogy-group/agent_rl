#!/usr/bin/env python3
"""
Extract tools that are decorated with @evolve decorator.

This script finds and extracts functions marked with the @evolve decorator
for evolutionary optimization.
"""

import ast
import os
import sys
import json
import importlib.util
import inspect
from pathlib import Path
from typing import Dict, List, Any, Optional
from evolve_decorator import EvolveCandidate


class DecoratedToolExtractor:
    """Extract tools marked with @evolve decorator"""
    
    def __init__(self, output_dir: str = "evolution/tools"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.extracted_tools = []
    
    def extract_from_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Extract decorated functions from a Python file"""
        file_path = Path(file_path)
        if not file_path.exists():
            print(f"Error: File {file_path} does not exist")
            return []
        
        print(f"\n🔍 Scanning {file_path}")
        
        # First, parse AST to find decorated functions
        with open(file_path, 'r') as f:
            source_code = f.read()
        
        tree = ast.parse(source_code)
        decorated_functions = self._find_decorated_functions(tree, source_code)
        
        # Import the module to get runtime metadata
        try:
            # Add the file's directory to Python path temporarily
            file_dir = str(file_path.parent)
            if file_dir not in sys.path:
                sys.path.insert(0, file_dir)
                path_added = True
            else:
                path_added = False
            
            spec = importlib.util.spec_from_file_location("temp_module", file_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules["temp_module"] = module
            spec.loader.exec_module(module)
            
            # Get decorated functions from the module
            extracted = []
            for name, obj in inspect.getmembers(module):
                if hasattr(obj, '_evolve_candidate') and obj._evolve_candidate:
                    # Found a decorated function
                    func_info = self._extract_function_info(obj, file_path, source_code)
                    if func_info:
                        extracted.append(func_info)
                        print(f"  ✅ Found decorated function: {func_info['name']}")
                
                # Check class methods
                elif inspect.isclass(obj):
                    for method_name, method in inspect.getmembers(obj):
                        if hasattr(method, '_evolve_candidate') and method._evolve_candidate:
                            func_info = self._extract_method_info(
                                method, obj, method_name, file_path, source_code
                            )
                            if func_info:
                                extracted.append(func_info)
                                print(f"  ✅ Found decorated method: {obj.__name__}.{method_name}")
            
            return extracted
            
        except Exception as e:
            print(f"  ❌ Error importing module: {e}")
            print(f"  🔄 Attempting AST-only extraction...")
            # Fall back to AST parsing without runtime import
            return self._extract_from_ast_only(tree, source_code, file_path)
        finally:
            # Clean up
            if "temp_module" in sys.modules:
                del sys.modules["temp_module"]
            if path_added and file_dir in sys.path:
                sys.path.remove(file_dir)
    
    def _find_decorated_functions(self, tree: ast.AST, source_code: str) -> List[Dict]:
        """Find functions with @evolve decorator in AST"""
        decorated = []
        
        class DecoratorVisitor(ast.NodeVisitor):
            def visit_FunctionDef(self, node):
                for decorator in node.decorator_list:
                    decorator_name = self._get_decorator_name(decorator)
                    if decorator_name and 'evolve' in decorator_name:
                        decorated.append({
                            'name': node.name,
                            'node': node,
                            'decorator': decorator_name
                        })
                self.generic_visit(node)
            
            def visit_ClassDef(self, node):
                # Check methods in classes
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        for decorator in item.decorator_list:
                            decorator_name = self._get_decorator_name(decorator)
                            if decorator_name and 'evolve' in decorator_name:
                                decorated.append({
                                    'name': f"{node.name}.{item.name}",
                                    'node': item,
                                    'class_node': node,
                                    'decorator': decorator_name
                                })
                self.generic_visit(node)
            
            def _get_decorator_name(self, decorator):
                if isinstance(decorator, ast.Name):
                    return decorator.id
                elif isinstance(decorator, ast.Call):
                    if isinstance(decorator.func, ast.Name):
                        return decorator.func.id
                return None
        
        visitor = DecoratorVisitor()
        visitor.visit(tree)
        return decorated
    
    def _extract_from_ast_only(self, tree: ast.AST, source_code: str, file_path: Path) -> List[Dict[str, Any]]:
        """Extract decorated functions using only AST parsing (fallback when import fails)"""
        decorated = self._find_decorated_functions(tree, source_code)
        extracted = []
        
        for func_info in decorated:
            node = func_info['node']
            func_name = func_info['name']
            
            # Extract function source code
            func_source = ast.get_source_segment(source_code, node)
            if not func_source:
                # Fallback: extract lines manually
                func_source = self._extract_function_source(source_code, node)
            
            # Parse decorator arguments
            decorator_args = self._parse_decorator_args(func_info)
            
            # Ensure we have a valid name
            tool_name = decorator_args.get('name') or func_name.split('.')[-1] or 'unknown_tool'
            
            info = {
                'name': tool_name,
                'description': decorator_args.get('description') or f"Function {func_name}",
                'category': decorator_args.get('category', 'utility'),
                'metrics': decorator_args.get('metrics', []),
                'metadata': decorator_args.get('metadata', {}),
                'source_file': str(file_path),
                'function_name': func_name,
                'source_code': func_source,
                'args': self._extract_args_from_ast(node),
                'module': str(file_path.stem),
                'qualname': func_name,
                'is_method': '.' in func_name
            }
            
            extracted.append(info)
            print(f"  ✅ AST extracted: {info['name']}")
        
        return extracted
    
    def _extract_function_source(self, source_code: str, node: ast.FunctionDef) -> str:
        """Extract function source code from AST node"""
        lines = source_code.split('\n')
        start_line = node.lineno - 1
        
        # Find the end of the function
        end_line = start_line + 1
        while end_line < len(lines):
            line = lines[end_line]
            # Simple heuristic: function ends at next function/class or unindented line
            if (line.strip() and not line.startswith(' ') and not line.startswith('\t')) or \
               line.strip().startswith(('def ', 'class ', '@')):
                break
            end_line += 1
        
        return '\n'.join(lines[start_line:end_line])
    
    def _parse_decorator_args(self, decorator_info: Dict) -> Dict[str, Any]:
        """Parse decorator arguments from AST info"""
        decorator_name = decorator_info.get('decorator', '')
        node = decorator_info.get('node')
        decorators = getattr(node, 'decorator_list', [])
        
        # Find the evolve decorator
        for decorator in decorators:
            if isinstance(decorator, ast.Call):
                func_name = ''
                if isinstance(decorator.func, ast.Name):
                    func_name = decorator.func.id
                elif isinstance(decorator.func, ast.Attribute):
                    func_name = decorator.func.attr
                
                if 'evolve' in func_name:
                    # Parse keyword arguments
                    args = {}
                    for keyword in decorator.keywords:
                        if isinstance(keyword.value, ast.Constant):
                            args[keyword.arg] = keyword.value.value
                        elif isinstance(keyword.value, ast.Str):  # Python < 3.8
                            args[keyword.arg] = keyword.value.s
                        elif isinstance(keyword.value, ast.List):
                            # Handle list arguments like metrics
                            list_items = []
                            for item in keyword.value.elts:
                                if isinstance(item, ast.Constant):
                                    list_items.append(item.value)
                                elif isinstance(item, ast.Str):
                                    list_items.append(item.s)
                            args[keyword.arg] = list_items
                    
                    return {
                        'name': args.get('name'),
                        'description': args.get('description'),
                        'category': self._get_category_from_decorator(func_name),
                        'metrics': args.get('metrics', []),
                        'metadata': args.get('metadata', {})
                    }
        
        # Default fallback
        return {
            'name': None,
            'description': None,
            'category': self._get_category_from_decorator(decorator_name),
            'metrics': [],
            'metadata': {}
        }
    
    def _get_category_from_decorator(self, decorator_name: str) -> str:
        """Determine category from decorator name"""
        if 'nlg' in decorator_name:
            return 'natural_language_generation'
        elif 'research' in decorator_name:
            return 'research'
        elif 'classification' in decorator_name:
            return 'classification'
        else:
            return 'utility'
    
    def _extract_args_from_ast(self, node: ast.FunctionDef) -> List[str]:
        """Extract function arguments from AST node"""
        return [arg.arg for arg in node.args.args]
    
    def _extract_function_info(self, func, file_path: Path, source_code: str) -> Optional[Dict]:
        """Extract information about a decorated function"""
        try:
            # Get source code
            func_source = inspect.getsource(func)
            
            # Get metadata from decorator
            info = {
                'name': func._evolve_name,
                'description': func._evolve_description or func.__doc__ or "No description",
                'category': func._evolve_category or 'utility',
                'metrics': func._evolve_metrics,
                'metadata': func._evolve_metadata,
                'source_file': str(file_path),
                'function_name': func.__name__,
                'source_code': func_source,
                'args': self._get_function_args(func),
                'module': func.__module__,
                'qualname': func.__qualname__
            }
            
            return info
            
        except Exception as e:
            print(f"    ⚠️  Error extracting {func.__name__}: {e}")
            return None
    
    def _extract_method_info(self, method, cls, method_name: str, 
                           file_path: Path, source_code: str) -> Optional[Dict]:
        """Extract information about a decorated class method"""
        try:
            # Get source code for the entire class
            class_source = inspect.getsource(cls)
            
            # Extract just the method source
            method_source = inspect.getsource(method)
            
            info = {
                'name': method._evolve_name,
                'description': method._evolve_description or method.__doc__ or "No description",
                'category': method._evolve_category or 'utility',
                'metrics': method._evolve_metrics,
                'metadata': method._evolve_metadata,
                'source_file': str(file_path),
                'class_name': cls.__name__,
                'method_name': method_name,
                'function_name': f"{cls.__name__}.{method_name}",
                'source_code': method_source,
                'class_source': class_source,
                'args': self._get_function_args(method),
                'is_method': True,
                'module': method.__module__,
                'qualname': f"{cls.__qualname__}.{method_name}"
            }
            
            return info
            
        except Exception as e:
            print(f"    ⚠️  Error extracting {cls.__name__}.{method_name}: {e}")
            return None
    
    def _get_function_args(self, func) -> List[str]:
        """Get function arguments"""
        try:
            sig = inspect.signature(func)
            return list(sig.parameters.keys())
        except:
            return []
    
    def save_extracted_tool(self, tool_info: Dict[str, Any]):
        """Save an extracted tool to a file"""
        tool_name = tool_info['name']
        tool_dir = self.output_dir / tool_name
        tool_dir.mkdir(exist_ok=True)
        
        # Save tool source code
        tool_file = tool_dir / "tool.py"
        
        # Generate standalone tool code
        if tool_info.get('is_method'):
            # For class methods, include the whole class
            tool_code = self._generate_method_tool_code(tool_info)
        else:
            tool_code = self._generate_function_tool_code(tool_info)
        
        with open(tool_file, 'w') as f:
            f.write(tool_code)
        
        # Save metadata
        metadata = {
            'name': tool_info['name'],
            'description': tool_info['description'],
            'category': tool_info['category'],
            'metrics': tool_info['metrics'],
            'original_file': tool_info['source_file'],
            'function_name': tool_info['function_name'],
            'args': tool_info['args'],
            'decorator_metadata': tool_info['metadata'],
            'is_method': tool_info.get('is_method', False)
        }
        
        metadata_file = tool_dir / "metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"  💾 Saved to {tool_dir}")
        self.extracted_tools.append(tool_name)
    
    def _generate_function_tool_code(self, tool_info: Dict) -> str:
        """Generate standalone code for a function"""
        # Extract imports and dependencies from original file
        imports = self._extract_imports(tool_info['source_file'])
        dependencies = self._extract_dependencies(tool_info['source_file'], tool_info['function_name'])
        
        code = f'''"""
Tool: {tool_info['name']}
Extracted from: {Path(tool_info['source_file']).name}

{tool_info['description']}
"""

{imports}

{dependencies}

{tool_info['source_code']}

if __name__ == "__main__":
    # Test the tool here
    # result = {tool_info['function_name']}(...)
    pass
'''
        return code
    
    def _generate_method_tool_code(self, tool_info: Dict) -> str:
        """Generate standalone code for a class method"""
        imports = self._extract_imports(tool_info['source_file'])
        
        code = f'''"""
Tool: {tool_info['name']}
Extracted from: {Path(tool_info['source_file']).name}
Class method: {tool_info['class_name']}.{tool_info['method_name']}

{tool_info['description']}
"""

{imports}

{tool_info['class_source']}

# Create a convenience function that instantiates the class and calls the method
def {tool_info['name']}(*args, **kwargs):
    """Wrapper function for the class method"""
    instance = {tool_info['class_name']}()
    return instance.{tool_info['method_name']}(*args, **kwargs)

if __name__ == "__main__":
    # Test the tool here
    # result = {tool_info['name']}(...)
    pass
'''
        return code
    
    def _extract_imports(self, file_path: str) -> str:
        """Extract import statements from a file"""
        with open(file_path, 'r') as f:
            source = f.read()
        
        tree = ast.parse(source)
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.append(ast.unparse(node))
            elif isinstance(node, ast.ImportFrom):
                # Skip decorator imports in standalone tools
                if node.module and 'evolve_decorator' in node.module:
                    continue
                imports.append(ast.unparse(node))
        
        return '\n'.join(imports)
    
    def _extract_dependencies(self, file_path: str, function_name: str) -> str:
        """Extract constants, variables, and other dependencies needed by the function"""
        with open(file_path, 'r') as f:
            source = f.read()
        
        tree = ast.parse(source)
        lines = source.split('\n')
        
        # Find the function to analyze its dependencies
        func_node = None
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == function_name.split('.')[-1]:
                func_node = node
                break
        
        if not func_node:
            return ""
        
        # Extract ALL names referenced in the function (not just variables)
        referenced_names = set()
        
        class NameCollector(ast.NodeVisitor):
            def visit_Name(self, node):
                if isinstance(node.ctx, ast.Load):
                    referenced_names.add(node.id)
                self.generic_visit(node)
            
            def visit_Attribute(self, node):
                # For PROMPT.format(), we want PROMPT
                if isinstance(node.value, ast.Name):
                    referenced_names.add(node.value.id)
                self.generic_visit(node)
        
        collector = NameCollector()
        collector.visit(func_node)
        
        # Remove function parameters and Python builtins
        param_names = {arg.arg for arg in func_node.args.args}
        referenced_names -= param_names
        builtins = {'len', 'str', 'int', 'float', 'bool', 'list', 'dict', 'set', 'tuple', 'range', 'enumerate', 'zip', 'print', 'f', 'join'}
        referenced_names -= builtins
        
        print(f"DEBUG: Function {function_name} references: {referenced_names}")
        
        dependencies = []
        
        # Always add load_dotenv if we use environment variables
        if any(name in referenced_names for name in ['os', 'load_dotenv']) or 'environ' in source:
            dependencies.append("load_dotenv()")
        
        # Add logger setup if referenced
        if 'logger' in referenced_names:
            dependencies.append("logger = logging.getLogger(__name__)")
        
        # Add model setup if referenced
        if 'model' in referenced_names:
            dependencies.append('model = ChatOpenAI(model="gpt-4o", temperature=0.2)')
        
        # Add tavily setup if referenced  
        if 'tavily' in referenced_names:
            dependencies.append('tavily = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])')
        
        # Now find ALL module-level assignments that are referenced
        module_assignments = {}
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        module_assignments[target.id] = node
        
        # Extract assignments for referenced names
        for name in referenced_names:
            if name in module_assignments and name not in ['logger', 'model', 'tavily']:
                node = module_assignments[name]
                
                # Use ast.get_source_segment first, fallback to manual extraction
                try:
                    dep_code = ast.get_source_segment(source, node)
                    if dep_code:
                        dependencies.append(dep_code)
                        print(f"DEBUG: Extracted via ast.get_source_segment: {name}")
                        continue
                except:
                    pass
                
                # Manual extraction for complex multi-line assignments
                start_line = node.lineno - 1
                end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line + 1
                
                # For string constants, find the actual end
                if isinstance(node.value, (ast.Constant, ast.Str)):
                    # Search for the closing triple quotes
                    line_text = lines[start_line]
                    if '"""' in line_text:
                        # Multi-line string - find closing """
                        quote_count = line_text.count('"""')
                        if quote_count == 1:  # Opening """ only
                            for i in range(start_line + 1, len(lines)):
                                if '"""' in lines[i]:
                                    end_line = i + 1
                                    break
                
                dep_code = '\n'.join(lines[start_line:end_line])
                if dep_code and dep_code.strip():
                    dependencies.append(dep_code)
                    print(f"DEBUG: Extracted manually: {name}")
        
        result = '\n\n'.join(dependencies)
        print(f"DEBUG: Final dependencies:\n{result}")
        return result
    
    def extract_from_directory(self, directory: str, recursive: bool = True):
        """Extract all decorated tools from a directory"""
        directory = Path(directory)
        
        pattern = '**/*.py' if recursive else '*.py'
        
        for py_file in directory.glob(pattern):
            if py_file.name.startswith('_') or py_file.name == 'setup.py':
                continue
            
            tools = self.extract_from_file(py_file)
            for tool in tools:
                self.save_extracted_tool(tool)
        
        print(f"\n✨ Extraction complete! Found {len(self.extracted_tools)} decorated tools.")
        return self.extracted_tools


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python extract_decorated_tools.py <file_or_directory> [output_directory]")
        print("\nExamples:")
        print("  python extract_decorated_tools.py mytools.py")
        print("  python extract_decorated_tools.py src/tools/")
        print("  python extract_decorated_tools.py src/agent.py evolution/decorated_tools")
        sys.exit(1)
    
    target = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "evolution/tools"
    
    extractor = DecoratedToolExtractor(output_dir)
    
    if os.path.isfile(target):
        tools = extractor.extract_from_file(target)
        for tool in tools:
            extractor.save_extracted_tool(tool)
    elif os.path.isdir(target):
        extractor.extract_from_directory(target)
    else:
        print(f"Error: {target} is not a valid file or directory")
        sys.exit(1)
    
    print(f"\nExtracted tools saved to: {output_dir}")


if __name__ == "__main__":
    main()