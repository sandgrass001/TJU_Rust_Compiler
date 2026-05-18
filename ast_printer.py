# ast_printer.py or add to parser.py
import io
from dataclasses import is_dataclass
from ast_nodes import *


class ASTPrinter:
    def __init__(self):
        self.indent_level = 0
        self._output = io.StringIO()

    def _print(self, *args, **kwargs):
        print(f"{'  ' * self.indent_level}", end='', file=self._output)
        print(*args, **kwargs, file=self._output)

    def get_output(self) -> str:
        return self._output.getvalue()

    def visit(self, node):
        if node is None:
            return
        if isinstance(node, list):
            for item in node:
                self.visit(item)
            return

        # Dispatch by type
        cls_name = node.__class__.__name__
        method = getattr(self, f'visit_{cls_name.lower()}', None)
        if method:
            return method(node)
        # Fallback: introspect dataclass fields
        if is_dataclass(node):
            self._print(f"{cls_name}:")
            self.indent_level += 1
            for field in node.__dataclass_fields__:
                value = getattr(node, field)
                self._print(f"{field}:")
                self.indent_level += 1
                self.visit(value)
                self.indent_level -= 1
            self.indent_level -= 1

    def print_node(self, node) -> str:
        self._output = io.StringIO()
        self.indent_level = 0
        self.visit(node)
        return self.get_output()

    # Specific implementations for common node types in ast_nodes.py
    def visit_program(self, node: Program):
        self._print("Program:")
        self.indent_level += 1
        for stmt in node.body:
            self.visit(stmt)
        self.indent_level -= 1

    def visit_letstatement(self, node: LetStatement):
        type_str = f", type='{node.type_name}'" if node.type_name else ""
        self._print(f"LetStatement(name='{node.name}', mutable={node.mutable}{type_str})")
        if node.value:
            self.indent_level += 1
            self._print("Value:")
            self.indent_level += 1
            self.visit(node.value)
            self.indent_level -= 2

    def visit_returnstatement(self, node: ReturnStatement):
        self._print("ReturnStatement:")
        if getattr(node, 'value', None) is not None:
            self.indent_level += 1
            self.visit(node.value)
            self.indent_level -= 1

    def visit_expressionstatement(self, node: ExpressionStatement):
        self._print("ExpressionStatement:")
        self.indent_level += 1
        self.visit(node.expression)
        self.indent_level -= 1

    def visit_functiondeclaration(self, node: FunctionDeclaration):
        ret = f" -> {node.return_type}" if node.return_type else ""
        self._print(f"FunctionDeclaration(name='{node.name}'{ret})")
        self.indent_level += 1
        if node.parameters:
            self._print("Parameters:")
            self.indent_level += 1
            for p in node.parameters:
                self.visit(p)
            self.indent_level -= 1
        if node.body:
            self._print("Body:")
            self.indent_level += 1
            for s in node.body:
                self.visit(s)
            self.indent_level -= 1
        self.indent_level -= 1

    def visit_parameter(self, node: Parameter):
        type_str = f", type='{node.type_name}'" if node.type_name else ""
        self._print(f"Parameter(name='{node.name}', mutable={node.mutable}{type_str})")

    def visit_ifstatement(self, node: IfStatement):
        self._print("IfStatement:")
        self.indent_level += 1
        self._print("Condition:")
        self.indent_level += 1
        self.visit(node.condition)
        self.indent_level -= 1
        if node.then_branch:
            self._print("Then:")
            self.indent_level += 1
            for s in node.then_branch:
                self.visit(s)
            self.indent_level -= 1
        if node.else_branch:
            self._print("Else:")
            self.indent_level += 1
            for s in node.else_branch:
                self.visit(s)
            self.indent_level -= 1
        self.indent_level -= 1

    def visit_identifier(self, node: Identifier):
        self._print(f"Identifier(name='{node.name}')")

    def visit_literal(self, node: Literal):
        self._print(f"Literal(value={node.value})")

    def visit_binaryexpression(self, node: BinaryExpression):
        self._print(f"BinaryExpression(operator='{node.operator}')")
        self.indent_level += 1
        self._print("Left:")
        self.indent_level += 1
        self.visit(node.left)
        self.indent_level -= 1
        self._print("Right:")
        self.indent_level += 1
        self.visit(node.right)
        self.indent_level -= 2

    def visit_unaryexpression(self, node: UnaryExpression):
        self._print(f"UnaryExpression(operator='{node.operator}')")
        self.indent_level += 1
        self.visit(node.operand)
        self.indent_level -= 1

    def visit_callexpression(self, node: CallExpression):
        self._print("CallExpression:")
        self.indent_level += 1
        self._print("Callee:")
        self.indent_level += 1
        self.visit(node.callee)
        self.indent_level -= 1
        if node.arguments:
            self._print("Arguments:")
            self.indent_level += 1
            for a in node.arguments:
                self.visit(a)
            self.indent_level -= 1
        self.indent_level -= 1

    def visit_assignmentstatement(self, node: AssignmentStatement):
        self._print("AssignmentStatement:")
        self.indent_level += 1
        self._print("Target:")
        self.indent_level += 1
        self.visit(node.target)
        self.indent_level -= 1
        self._print("Value:")
        self.indent_level += 1
        self.visit(node.value)
        self.indent_level -= 2

    def visit_emptystatement(self, node: EmptyStatement):
        self._print("EmptyStatement")

    def visit_whilestatement(self, node: WhileStatement):
        self._print("WhileStatement:")
        self.indent_level += 1
        self._print("Condition:")
        self.indent_level += 1
        self.visit(node.condition)
        self.indent_level -= 1
        if node.body:
            self._print("Body:")
            self.indent_level += 1
            for s in node.body:
                self.visit(s)
            self.indent_level -= 1
        self.indent_level -= 1

    def visit_lvalue(self, node: LValue):
        self._print(f"LValue(name='{node.name}')")
