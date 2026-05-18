import os
import subprocess
import shutil
from tkinter import messagebox
from graphviz import Digraph

class ASTGraphvizDrawer:
    # ... (ASTGraphvizDrawer 代码来自之前的提示 - 保持不变) ...
    # (确保它包含了您 AST 节点的所有 visit 方法)
    def __init__(self):
        self.graph = Digraph('AST', node_attr={'shape': 'box', 'fontname': 'monospace'})
        self.node_id = 0

    def add_node(self, label):
        node_name = f"node{self.node_id}"
        self.graph.node(node_name, label)
        self.node_id += 1
        return node_name

    def visit_program(self, node):
        program_node = self.add_node("Program")
        for stmt in getattr(node, 'body', []):
            child = self.visit(stmt)
            if child:
                self.graph.edge(program_node, child)
        return program_node

    def visit_let_statement(self, node):
        name = getattr(node, 'name', None)
        label = f"Let: {name}"
        if getattr(node, 'mutable', False):
            label = f"Let mut: {name}"
        let_node = self.add_node(label)
        if getattr(node, 'value', None) is not None:
            value_node = self.visit(node.value)
            if value_node:
                self.graph.edge(let_node, value_node, label="value")
        # type_name may be a string
        if getattr(node, 'type_name', None):
            type_node = self.add_node(f"Type: {node.type_name}")
            self.graph.edge(let_node, type_node, label="type")
        return let_node

    def visit_return_statement(self, node):
        ret_node = self.add_node("Return")
        if getattr(node, 'value', None) is not None:
            value_node = self.visit(node.value)
            if value_node:
                self.graph.edge(ret_node, value_node)
        return ret_node

    def visit_expression_statement(self, node):
        expr_node = self.add_node("ExpressionStmt")
        if getattr(node, 'expression', None) is not None:
            child_node = self.visit(node.expression)
            if child_node:
                self.graph.edge(expr_node, child_node)
        return expr_node

    def visit_block_statement(self, node):
        block_node = self.add_node("Block")
        for stmt in getattr(node, 'body', []):
            child = self.visit(stmt)
            if child:
                self.graph.edge(block_node, child)
        return block_node

    def visit_function_declaration(self, node):
        name = getattr(node, 'name', None)
        func_label = f"Function: {name}"
        func_node = self.add_node(func_label)
        for param in getattr(node, 'parameters', []):
            param_node = self.visit(param)
            if param_node:
                self.graph.edge(func_node, param_node, label="param")
        for stmt in getattr(node, 'body', []):
            child = self.visit(stmt)
            if child:
                self.graph.edge(func_node, child, label="body")
        if getattr(node, 'return_type', None):
            return_type_node = self.add_node(f"Type: {node.return_type}")
            self.graph.edge(func_node, return_type_node, label="return_type")
        return func_node

    def visit_parameter_node(self, node):
        # Parameter dataclass uses 'name' and 'type_name'
        name = getattr(node, 'name', None)
        label = f"Param: {name}"
        if getattr(node, 'mutable', False):
            label = f"Param mut: {name}"
        param_node = self.add_node(label)
        if getattr(node, 'type_name', None):
            type_node = self.add_node(f"Type: {node.type_name}")
            self.graph.edge(param_node, type_node, label="type")
        return param_node

    def visit_if_statement(self, node):
        if_node = self.add_node("IfStatement")
        cond_node = self.visit(node.condition)
        if cond_node: self.graph.edge(if_node, cond_node, label="condition")
        # then_branch is a list
        then_parent = self.add_node("Then")
        self.graph.edge(if_node, then_parent)
        for stmt in getattr(node, 'then_branch', []):
            child = self.visit(stmt)
            if child: self.graph.edge(then_parent, child)
        if getattr(node, 'else_branch', None):
            else_parent = self.add_node("Else")
            self.graph.edge(if_node, else_parent)
            for stmt in getattr(node, 'else_branch', []):
                child = self.visit(stmt)
                if child: self.graph.edge(else_parent, child)
        return if_node

    def visit_identifier(self, node):
        return self.add_node(f"Identifier: {getattr(node, 'name', node)}")

    def visit_integer_literal(self, node):
        return self.add_node(f"Integer: {getattr(node, 'value', node)}")

    def visit_boolean_literal(self, node):
        return self.add_node(f"Boolean: {str(getattr(node, 'value', node))}")

    def visit_prefix_expression(self, node):
        label = f"Prefix: {getattr(node, 'operator', '')}"
        prefix_node = self.add_node(label)
        right_node = self.visit(getattr(node, 'operand', getattr(node, 'right', None)))
        if right_node: self.graph.edge(prefix_node, right_node, label="right")
        return prefix_node

    def visit_infix_expression(self, node):
        label = f"Infix: {getattr(node, 'operator', '')}"
        infix_node = self.add_node(label)
        left_node = self.visit(getattr(node, 'left', None))
        right_node = self.visit(getattr(node, 'right', None))
        if left_node: self.graph.edge(infix_node, left_node, label="left")
        if right_node: self.graph.edge(infix_node, right_node, label="right")
        return infix_node

    def visit_call_expression(self, node):
        call_node = self.add_node("Call")
        func_node = self.visit(getattr(node, 'callee', getattr(node, 'function', None)))
        if func_node: self.graph.edge(call_node, func_node, label="function")
        for i, arg in enumerate(getattr(node, 'arguments', getattr(node, 'args', []))):
            arg_node = self.visit(arg)
            if arg_node: self.graph.edge(call_node, arg_node, label=f"arg{i}")
        return call_node

    def visit_type_node(self, node):
        return self.add_node(f"Type: {getattr(node, 'name', node)}")

    def visit_while_statement(self, node):
        while_node = self.add_node("While")
        cond_node = self.visit(getattr(node, 'condition', None))
        if cond_node: self.graph.edge(while_node, cond_node, label="condition")
        for stmt in getattr(node, 'body', []):
            child = self.visit(stmt)
            if child: self.graph.edge(while_node, child, label="body")
        return while_node

    def visit_for_statement(self, node):
        var = getattr(node, 'variable', None)
        var_name = getattr(var, 'name', str(var)) if var is not None else '?'
        for_node = self.add_node(f"For: {var_name}")
        iterator_node = self.visit(getattr(node, 'iterator', None))
        if iterator_node: self.graph.edge(for_node, iterator_node, label="in")
        for stmt in getattr(node, 'body', []):
            child = self.visit(stmt)
            if child: self.graph.edge(for_node, child, label="body")
        return for_node

    def visit_assignment_statement(self, node):
        assign_node = self.add_node("Assign")
        target_node = self.visit(getattr(node, 'target', None))
        if target_node: self.graph.edge(assign_node, target_node, label="target")
        value_node = self.visit(getattr(node, 'value', None))
        if value_node: self.graph.edge(assign_node, value_node, label="value")
        return assign_node

    def visit_loop_statement(self, node):
        loop_node = self.add_node("Loop")
        for stmt in getattr(node, 'body', []):
            child = self.visit(stmt)
            if child: self.graph.edge(loop_node, child, label="body")
        return loop_node

    def visit_break_statement(self, node):
        return self.add_node("Break")

    def visit_continue_statement(self, node):
        return self.add_node("Continue")

    # Generic visit dispatcher to allow calling visit(...) instead of node.accept(...)
    def visit(self, node):
        if node is None:
            return None
        if isinstance(node, list):
            parent = None
            # create a grouping node for list if needed
            for item in node:
                self.visit(item)
            return None
        cls_name = node.__class__.__name__.lower()
        method = getattr(self, f'visit_{cls_name}', None)
        if method:
            return method(node)
        # Fallback: leaf value
        if hasattr(node, 'name'):
            return self.add_node(str(getattr(node, 'name')))
        if hasattr(node, 'value'):
            return self.add_node(str(getattr(node, 'value')))
        return self.add_node(repr(node))

    def render_to_memory(self, base_dir):
        """尝试渲染 AST 图为 PNG 字节流，多种回退策略"""
        try:
            tmp_filepath = os.path.join(base_dir, "ast_tmp_output")
            tmp_filepath_dot = tmp_filepath + ".dot"
            tmp_filepath_png = tmp_filepath + ".png"

            self.graph.save(tmp_filepath_dot)

            # 方案 1: 尝试 graphviz Python 库的 render 方法
            try:
                self.graph.render(tmp_filepath, format='png', cleanup=True)
                if os.path.exists(tmp_filepath_png):
                    with open(tmp_filepath_png, "rb") as f:
                        img_bytes = f.read()
                    if os.path.exists(tmp_filepath_png):
                        os.remove(tmp_filepath_png)
                    return img_bytes
            except Exception:
                pass

            # 方案 2: 尝试系统 dot 命令
            try:
                dot_cmd = 'dot' if shutil.which('dot') else 'dot.exe'
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

            # 方案 3: 尝试本地 graphviz_bin
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

            # 全部失败，清理并报错
            if os.path.exists(tmp_filepath_dot):
                os.remove(tmp_filepath_dot)

            raise RuntimeError(
                "无法渲染 AST 图。请确保 Graphviz 已正确安装。\n"
                "Windows: choco install graphviz 或从 https://graphviz.org/download/ 下载\n"
                "macOS: brew install graphviz\n"
                "Linux: sudo apt install graphviz"
            )

        except Exception as e:
            print(f"AST图像错误: {e}")
            messagebox.showerror("AST图像错误", f"Graphviz渲染失败:\n{str(e)}")
            return None