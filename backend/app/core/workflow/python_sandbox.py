import ast
import asyncio
import json
import os
import sys
import tempfile
from typing import Any, Dict, Optional, Tuple

FORBIDDEN_IMPORTS = {
    "os", "sys", "subprocess", "socket", "shutil", "pathlib", "ctypes",
    "importlib", "signal", "pty", "platform", "builtins", "code", "codeop",
    "multiprocessing", "threading", "asyncio", "pickle", "shelve", "dbm",
    "sqlite3", "tempfile", "urllib", "requests", "httpx", "http", "ftplib",
    "poplib", "imaplib", "smtplib", "telnetlib", "xmlrpc"
}

FORBIDDEN_CALLS = {
    "exec", "eval", "compile", "__import__", "open", "input",
    "getattr", "setattr", "delattr", "globals", "locals", "vars",
    "dir", "help", "exit", "quit", "breakpoint"
}

FORBIDDEN_ATTRS = {
    "__builtins__", "__globals__", "__locals__", "__class__",
    "__subclasses__", "__mro__", "__bases__", "__code__",
    "__closure__", "__dict__", "__getattribute__", "__import__"
}


class ASTSecurityVisitor(ast.NodeVisitor):
    """AST visitor that checks Python code for security policy violations."""

    def __init__(self):
        self.errors = []

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            name = alias.name.split(".")[0]
            if name in FORBIDDEN_IMPORTS:
                self.errors.append(f"Security Policy Violation: Import of module '{alias.name}' is prohibited.")
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.module:
            name = node.module.split(".")[0]
            if name in FORBIDDEN_IMPORTS:
                self.errors.append(f"Security Policy Violation: Import from module '{node.module}' is prohibited.")
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name):
        if node.id in FORBIDDEN_CALLS or node.id in FORBIDDEN_ATTRS:
            self.errors.append(f"Security Policy Violation: Use of restricted identifier '{node.id}' is prohibited.")
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute):
        if node.attr in FORBIDDEN_ATTRS or node.attr in FORBIDDEN_CALLS:
            self.errors.append(f"Security Policy Violation: Accessing restricted attribute '{node.attr}' is prohibited.")
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        if isinstance(node.func, ast.Name) and node.func.id in FORBIDDEN_CALLS:
            self.errors.append(f"Security Policy Violation: Invoking restricted function '{node.func.id}()' is prohibited.")
        self.generic_visit(node)


def validate_python_code_security(code_str: str) -> Tuple[bool, str]:
    """Parses and audits Python code AST for safety violations."""
    try:
        tree = ast.parse(code_str)
    except SyntaxError as e:
        return False, f"Python Syntax Error on line {e.lineno}: {e.msg}"

    visitor = ASTSecurityVisitor()
    visitor.visit(tree)
    if visitor.errors:
        return False, "; ".join(visitor.errors)

    return True, ""


WRAPPER_TEMPLATE = """
import sys
import json
import math
import re
import datetime
import statistics
import collections

# Load context from stdin
try:
    context = json.loads(sys.stdin.read())
except Exception as e:
    context = {}

inputs = context.get("inputs", {})
variables = context.get("variables", {})
previous_output = context.get("previous_output", None)

result = None
outputs = {}

# Execute user code in isolated scope
user_scope = {
    "inputs": inputs,
    "variables": variables,
    "previous_output": previous_output,
    "result": None,
    "outputs": {},
    "math": math,
    "re": re,
    "datetime": datetime,
    "statistics": statistics,
    "collections": collections,
    "json": json,
    "len": len,
    "range": range,
    "min": min,
    "max": max,
    "sum": sum,
    "abs": abs,
    "round": round,
    "str": str,
    "int": int,
    "float": float,
    "bool": bool,
    "list": list,
    "dict": dict,
    "set": set,
    "tuple": tuple,
}

# User Script Execution
user_code = r'''__USER_CODE__'''
exec(user_code, user_scope)

# Capture final output
final_res = user_scope.get("result") if user_scope.get("result") is not None else user_scope.get("outputs", {"status": "executed"})
if not isinstance(final_res, (dict, list, str, int, float, bool, type(None))):
    final_res = str(final_res)

print("---NEURODESK_OUTPUT_START---")
print(json.dumps({"result": final_res, "variables": {k: v for k, v in user_scope.items() if k not in ["inputs", "variables", "previous_output", "math", "re", "datetime", "statistics", "collections", "json", "len", "range", "min", "max", "sum", "abs", "round", "str", "int", "float", "bool", "list", "dict", "set", "tuple"] and not k.startswith("__")}}))
print("---NEURODESK_OUTPUT_END---")
"""


class PythonSandboxExecutor:
    """Executes Python code snippets in a isolated, timeout-bounded subprocess."""

    @staticmethod
    async def execute_script(
        code: str,
        context: Optional[Dict[str, Any]] = None,
        timeout_seconds: float = 5.0,
    ) -> Dict[str, Any]:
        context = context or {}
        # 1. AST Security Audit
        is_safe, error_msg = validate_python_code_security(code)
        if not is_safe:
            return {
                "status": "FAILED",
                "success": False,
                "result": None,
                "stdout": "",
                "stderr": error_msg,
            }

        # 2. Prepare isolated wrapper script
        wrapper_code = WRAPPER_TEMPLATE.replace("__USER_CODE__", code)

        # 3. Create isolated environment (explicitly stripping secrets)
        safe_env = {
            "PATH": os.environ.get("PATH", ""),
            "SYSTEMROOT": os.environ.get("SYSTEMROOT", ""),
            "PYTHONPATH": "",
        }

        # Write code to temp file
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as tmp:
            tmp.write(wrapper_code)
            tmp_path = tmp.name

        try:
            input_data = json.dumps({
                "inputs": context.get("inputs", {}),
                "variables": context.get("variables", {}),
                "previous_output": context.get("last_output", None),
            })

            proc = await asyncio.create_subprocess_exec(
                sys.executable,
                tmp_path,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=safe_env,
            )

            try:
                stdout_data, stderr_data = await asyncio.wait_for(
                    proc.communicate(input=input_data.encode("utf-8")),
                    timeout=timeout_seconds,
                )
            except asyncio.TimeoutError:
                try:
                    proc.kill()
                    await proc.wait()
                except Exception:
                    pass
                raise TimeoutError(f"Python execution timed out after {timeout_seconds} seconds.")

            stdout_str = stdout_data.decode("utf-8", errors="replace")
            stderr_str = stderr_data.decode("utf-8", errors="replace")

            if proc.returncode != 0:
                clean_err = stderr_str.strip() if stderr_str else "Subprocess returned non-zero exit code."
                raise RuntimeError(f"Python Script Execution Error: {clean_err}")

            # Parse JSON output payload from stdout
            if "---NEURODESK_OUTPUT_START---" in stdout_str:
                raw_json = stdout_str.split("---NEURODESK_OUTPUT_START---")[1].split("---NEURODESK_OUTPUT_END---")[0].strip()
                parsed = json.loads(raw_json)
                return {
                    "success": True,
                    "result": parsed.get("result"),
                    "stdout": stdout_str.split("---NEURODESK_OUTPUT_START---")[0].strip(),
                    "stderr": stderr_str.strip(),
                    "status": "executed",
                }

            return {
                "success": True,
                "result": stdout_str.strip(),
                "stdout": stdout_str.strip(),
                "stderr": stderr_str.strip(),
                "status": "executed",
            }

        finally:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass


python_sandbox = PythonSandboxExecutor()
