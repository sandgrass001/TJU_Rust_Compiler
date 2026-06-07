import os
import shutil
import subprocess
import sys
from dataclasses import is_dataclass
from tkinter import messagebox

try:
    from graphviz import Digraph
except ModuleNotFoundError:
    Digraph = None


class SimpleDigraph:
    def __init__(self, name, node_attr=None):
        self.name = name
        self.node_attr = node_attr or {}
        self.nodes = []
        self.edges = []

    @staticmethod
    def quote(value):
        return '"' + str(value).replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n') + '"'

    def node(self, name, label):
        self.nodes.append((name, label))

    def edge(self, start, end, label=None):
        self.edges.append((start, end, label))

    @property
    def source(self):
        lines = [f"digraph {self.name} {{"]
        if self.node_attr:
            attrs = ", ".join(f"{key}={self.quote(value)}" for key, value in self.node_attr.items())
            lines.append(f"  node [{attrs}];")
        for name, label in self.nodes:
            lines.append(f"  {self.quote(name)} [label={self.quote(label)}];")
        for start, end, label in self.edges:
            if label is None:
                lines.append(f"  {self.quote(start)} -> {self.quote(end)};")
            else:
                lines.append(f"  {self.quote(start)} -> {self.quote(end)} [label={self.quote(label)}];")
        lines.append("}")
        return "\n".join(lines)

    def save(self, filepath):
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(self.source)

    def render(self, filepath, format='png', cleanup=False):
        output_path = f"{filepath}.{format}"
        dot_path = filepath
        if not dot_path.endswith(".dot"):
            dot_path += ".dot"
        self.save(dot_path)
        dot_cmd = find_dot_executable()
        subprocess.run([dot_cmd, f"-T{format}", dot_path, "-o", output_path], check=True, capture_output=True)
        if cleanup and os.path.exists(dot_path):
            os.remove(dot_path)
        return output_path


def find_dot_executable():
    dot_cmd = shutil.which('dot') or shutil.which('dot.exe')
    if dot_cmd:
        return dot_cmd

    candidates = [
        os.path.join(sys.prefix, 'Library', 'bin', 'dot.exe'),
        os.path.join(sys.prefix, 'bin', 'dot'),
        os.path.join(os.path.dirname(sys.executable), 'Library', 'bin', 'dot.exe'),
    ]
    for candidate in candidates:
        if os.path.exists(candidate):
            return candidate

    return 'dot'


class ASTGraphvizDrawer:
    def __init__(self):
        graph_class = Digraph or SimpleDigraph
        self.graph = graph_class('AST', node_attr={'shape': 'box', 'fontname': 'monospace'})
        self.node_id = 0

    def add_node(self, label):
        node_name = f"node{self.node_id}"
        self.graph.node(node_name, label)
        self.node_id += 1
        return node_name

    def add_child(self, parent, child, label=None):
        child_node = self.visit(child)
        if child_node:
            self.graph.edge(parent, child_node, label=label)

    def add_children(self, parent, children, label=None):
        for child in children:
            self.add_child(parent, child, label)

    def visit_program(self, node):
        program_node = self.add_node("Program")
        self.add_children(program_node, node.body)
        return program_node

    def visit_letstatement(self, node):
        prefix = "Let mut" if node.mutable else "Let"
        let_node = self.add_node(f"{prefix}: {node.name}")
        if node.type_name:
            type_node = self.add_node(f"Type: {node.type_name}")
            self.graph.edge(let_node, type_node, label="type")
        if node.value is not None:
            self.add_child(let_node, node.value, "value")
        return let_node

    def visit_assignmentstatement(self, node):
        assign_node = self.add_node("Assignment")
        self.add_child(assign_node, node.target, "target")
        self.add_child(assign_node, node.value, "value")
        return assign_node

    def visit_emptystatement(self, node):
        return self.add_node("Empty")

    def visit_ifstatement(self, node):
        if_node = self.add_node("If")
        self.add_child(if_node, node.condition, "condition")

        then_node = self.add_node("Then")
        self.graph.edge(if_node, then_node)
        self.add_children(then_node, node.then_branch)

        if node.else_branch:
            else_node = self.add_node("Else")
            self.graph.edge(if_node, else_node)
            self.add_children(else_node, node.else_branch)

        return if_node

    def visit_whilestatement(self, node):
        while_node = self.add_node("While")
        self.add_child(while_node, node.condition, "condition")
        self.add_children(while_node, node.body, "body")
        return while_node

    def visit_functiondeclaration(self, node):
        func_node = self.add_node(f"Function: {node.name}")

        for param in node.parameters:
            self.add_child(func_node, param, "param")

        if node.return_type:
            return_type_node = self.add_node(f"Type: {node.return_type}")
            self.graph.edge(func_node, return_type_node, label="return")

        self.add_children(func_node, node.body, "body")
        return func_node

    def visit_returnstatement(self, node):
        ret_node = self.add_node("Return")
        if node.value is not None:
            self.add_child(ret_node, node.value, "value")
        return ret_node

    def visit_expressionstatement(self, node):
        expr_stmt_node = self.add_node("ExpressionStatement")
        self.add_child(expr_stmt_node, node.expression)
        return expr_stmt_node

    def visit_identifier(self, node):
        return self.add_node(f"Identifier: {node.name}")

    def visit_lvalue(self, node):
        return self.add_node(f"LValue: {node.name}")

    def visit_literal(self, node):
        return self.add_node(f"Literal: {node.value!r}")

    def visit_binaryexpression(self, node):
        binary_node = self.add_node(f"Binary: {node.operator}")
        self.add_child(binary_node, node.left, "left")
        self.add_child(binary_node, node.right, "right")
        return binary_node

    def visit_unaryexpression(self, node):
        unary_node = self.add_node(f"Unary: {node.operator}")
        self.add_child(unary_node, node.operand, "operand")
        return unary_node

    def visit_callexpression(self, node):
        call_node = self.add_node("Call")
        self.add_child(call_node, node.callee, "callee")
        for i, argument in enumerate(node.arguments):
            self.add_child(call_node, argument, f"arg{i}")
        return call_node

    def visit_parameter(self, node):
        prefix = "Param mut" if node.mutable else "Param"
        param_node = self.add_node(f"{prefix}: {node.name}")
        if node.type_name:
            type_node = self.add_node(f"Type: {node.type_name}")
            self.graph.edge(param_node, type_node, label="type")
        return param_node

    def visit(self, node):
        if node is None:
            return None
        if isinstance(node, list):
            list_node = self.add_node("List")
            self.add_children(list_node, node)
            return list_node

        cls_name = node.__class__.__name__
        method = getattr(self, f'visit_{cls_name.lower()}', None)
        if method:
            return method(node)

        if is_dataclass(node):
            return self.visit_dataclass(node, cls_name)

        return self.add_node(repr(node))

    def visit_dataclass(self, node, cls_name):
        parent = self.add_node(cls_name)
        for field_name in node.__dataclass_fields__:
            value = getattr(node, field_name)
            if isinstance(value, list):
                list_node = self.add_node(field_name)
                self.graph.edge(parent, list_node)
                self.add_children(list_node, value)
            elif is_dataclass(value):
                self.add_child(parent, value, field_name)
            elif value is not None:
                value_node = self.add_node(f"{field_name}: {value!r}")
                self.graph.edge(parent, value_node)
        return parent

    def render_to_memory(self, base_dir):
        """Render the AST to PNG bytes."""
        try:
            tmp_filepath = os.path.join(base_dir, "ast_tmp_output")
            tmp_filepath_dot = tmp_filepath + ".dot"
            tmp_filepath_png = tmp_filepath + ".png"

            self.graph.save(tmp_filepath_dot)

            try:
                self.graph.render(tmp_filepath, format='png', cleanup=True)
                if os.path.exists(tmp_filepath_png):
                    with open(tmp_filepath_png, "rb") as f:
                        img_bytes = f.read()
                    os.remove(tmp_filepath_png)
                    return img_bytes
            except Exception:
                pass

            try:
                dot_cmd = find_dot_executable()
                subprocess.run([
                    dot_cmd,
                    "-Tpng",
                    tmp_filepath_dot,
                    "-o",
                    tmp_filepath_png
                ], check=True, capture_output=True)

                if os.path.exists(tmp_filepath_png):
                    with open(tmp_filepath_png, "rb") as f:
                        img_bytes = f.read()
                    os.remove(tmp_filepath_dot)
                    os.remove(tmp_filepath_png)
                    return img_bytes
            except Exception:
                pass

            try:
                dot_exe_path = os.path.join(base_dir, 'graphviz_bin', 'dot.exe')
                if os.path.exists(dot_exe_path):
                    subprocess.run([
                        dot_exe_path,
                        "-Tpng",
                        tmp_filepath_dot,
                        "-o",
                        tmp_filepath_png
                    ], check=True, capture_output=True)

                    if os.path.exists(tmp_filepath_png):
                        with open(tmp_filepath_png, "rb") as f:
                            img_bytes = f.read()
                        os.remove(tmp_filepath_dot)
                        os.remove(tmp_filepath_png)
                        return img_bytes
            except Exception:
                pass

            if os.path.exists(tmp_filepath_dot):
                os.remove(tmp_filepath_dot)

            raise RuntimeError(
                "Failed to render AST PNG. Please install Graphviz.\n"
                "Windows: choco install graphviz, or download it from https://graphviz.org/download/\n"
                "macOS: brew install graphviz\n"
                "Linux: sudo apt install graphviz"
            )

        except Exception as e:
            messagebox.showerror("AST render error", f"Graphviz render failed:\n{str(e)}")
            return None
