from __future__ import annotations

from ast_nodes import (
    AssignmentStatement,
    BinaryExpression,
    CallExpression,
    ContinueStatement,
    ExpressionStatement,
    ForStatement,
    FunctionDeclaration,
    Identifier,
    IfStatement,
    LetStatement,
    Literal,
    LValue,
    LoopStatement,
    Node,
    Program,
    RangeExpression,
    ReturnStatement,
    UnaryExpression,
    WhileStatement,
    BreakStatement,
)


class IRGenerator:
    """简单四元式中间代码生成器"""

    def __init__(self):
        self.instructions: list[tuple[str, str, str, str]] = []
        self.temp_count = 0
        self.label_count = 0
        self.current_function: str | None = None
        self.loop_stack: list[dict[str, str]] = []

    def new_temp(self) -> str:
        name = f"t{self.temp_count}"
        self.temp_count += 1
        return name

    def new_label(self, prefix: str = "L") -> str:
        label = f"{prefix}{self.label_count}"
        self.label_count += 1
        return label

    def emit(self, op: str, arg1: str = "", arg2: str = "", result: str = "") -> None:
        self.instructions.append((op, arg1, arg2, result))

    def format_quad(self, quad: tuple[str, str, str, str]) -> str:
        op, arg1, arg2, result = quad
        def field(x: str) -> str:
            return x if x != "" else "_"
        return f"({field(op)}, {field(arg1)}, {field(arg2)}, {field(result)})"

    def generate(self, node: Node) -> str:
        self.visit(node)
        return "\n".join(self.format_quad(instr) for instr in self.instructions)

    def visit(self, node: Node) -> str | None:
        method_name = f"visit_{type(node).__name__}"
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node: Node) -> str:
        raise NotImplementedError(f"IRGenerator does not support node type {type(node).__name__}")

    def visit_Program(self, node: Program) -> None:
        for stmt in node.body:
            self.visit(stmt)

    def visit_FunctionDeclaration(self, node: FunctionDeclaration) -> None:
        params = [
            f"{param.name}: {param.type_name or 'unknown'}"
            for param in node.parameters
        ]
        return_type = node.return_type or "unit"
        self.current_function = node.name
        self.emit("func", node.name, ", ".join(params), return_type)

        for stmt in node.body:
            self.visit(stmt)

        if not any(isinstance(stmt, ReturnStatement) for stmt in node.body):
            self.emit("return")

        self.emit("endfunc", node.name)
        self.emit("")
        self.current_function = None

    def visit_LetStatement(self, node: LetStatement) -> None:
        if node.value is not None:
            value = self.visit(node.value)
            self.emit("assign", value, "", node.name)
        else:
            self.emit("assign", "undef", "", node.name)

    def visit_AssignmentStatement(self, node: AssignmentStatement) -> None:
        value = self.visit(node.value)
        self.emit("assign", value, "", node.target.name)

    def visit_ExpressionStatement(self, node: ExpressionStatement) -> None:
        result = self.visit(node.expression)
        if result is not None and result.startswith("t"):
            # keep the temporary result if it is computed
            pass

    def visit_IfStatement(self, node: IfStatement) -> None:
        cond = self.visit(node.condition)
        else_label = self.new_label("L")
        end_label = self.new_label("L")
        self.emit("ifz", cond, "", else_label)

        for stmt in node.then_branch:
            self.visit(stmt)

        self.emit("goto", end_label)
        self.emit("label", else_label)

        for stmt in node.else_branch:
            self.visit(stmt)

        self.emit("label", end_label)

    def visit_WhileStatement(self, node: WhileStatement) -> None:
        start_label = self.new_label("L")
        end_label = self.new_label("L")
        self.emit("label", start_label)
        cond = self.visit(node.condition)
        self.emit("ifz", cond, "", end_label)

        self.loop_stack.append({"continue": start_label, "break": end_label})
        for stmt in node.body:
            self.visit(stmt)
        self.loop_stack.pop()

        self.emit("goto", start_label)
        self.emit("label", end_label)

    def visit_ForStatement(self, node: ForStatement) -> None:
        if isinstance(node.iterable, RangeExpression):
            start = self.visit(node.iterable.start)
            end = self.visit(node.iterable.end)
            self.emit("assign", start, "", node.iterator)
            begin_label = self.new_label("L")
            continue_label = self.new_label("L")
            end_label = self.new_label("L")
            self.emit("label", begin_label)
            cond = self.new_temp()
            self.emit("<", node.iterator, end, cond)
            self.emit("ifz", cond, "", end_label)

            self.loop_stack.append({"continue": continue_label, "break": end_label})
            for stmt in node.body:
                self.visit(stmt)
            self.loop_stack.pop()

            self.emit("label", continue_label)
            next_val = self.new_temp()
            self.emit("+", node.iterator, "1", next_val)
            self.emit("assign", next_val, "", node.iterator)
            self.emit("goto", begin_label)
            self.emit("label", end_label)
        else:
            iterable = self.visit(node.iterable)
            start_label = self.new_label("L")
            continue_label = self.new_label("L")
            end_label = self.new_label("L")
            self.emit("for", iterable, "", node.iterator)
            self.emit("label", start_label)

            self.loop_stack.append({"continue": continue_label, "break": end_label})
            for stmt in node.body:
                self.visit(stmt)
            self.loop_stack.pop()

            self.emit("label", continue_label)
            self.emit("goto", start_label)
            self.emit("label", end_label)

    def visit_LoopStatement(self, node: LoopStatement) -> None:
        start_label = self.new_label("L")
        end_label = self.new_label("L")
        self.emit("label", start_label)

        self.loop_stack.append({"continue": start_label, "break": end_label})
        for stmt in node.body:
            self.visit(stmt)
        self.loop_stack.pop()

        self.emit("goto", start_label)
        self.emit("label", end_label)

    def visit_BreakStatement(self, node: BreakStatement) -> None:
        if self.loop_stack:
            self.emit("goto", self.loop_stack[-1]["break"], "", "")
        else:
            self.emit("break")

    def visit_ContinueStatement(self, node: ContinueStatement) -> None:
        if self.loop_stack:
            self.emit("goto", self.loop_stack[-1]["continue"], "", "")
        else:
            self.emit("continue")

    def visit_RangeExpression(self, node: RangeExpression) -> str:
        start = self.visit(node.start)
        end = self.visit(node.end)
        temp = self.new_temp()
        self.emit("range", start, end, temp)
        return temp

    def visit_ReturnStatement(self, node: ReturnStatement) -> None:
        if node.value is None:
            self.emit("return")
            return
        value = self.visit(node.value)
        self.emit("return", value)

    def visit_BinaryExpression(self, node: BinaryExpression) -> str:
        left = self.visit(node.left)
        right = self.visit(node.right)
        temp = self.new_temp()
        self.emit(node.operator, left, right, temp)
        return temp

    def visit_UnaryExpression(self, node: UnaryExpression) -> str:
        operand = self.visit(node.operand)
        if node.operator == "-":
            temp = self.new_temp()
            self.emit("neg", operand, "", temp)
            return temp
        if node.operator == "&":
            temp = self.new_temp()
            self.emit("addr", operand, "", temp)
            return temp
        return operand

    def visit_Literal(self, node: Literal) -> str:
        return str(node.value)

    def visit_Identifier(self, node: Identifier) -> str:
        return node.name

    def visit_LValue(self, node: LValue) -> str:
        return node.name

    def visit_CallExpression(self, node: CallExpression) -> str:
        callee = self.visit(node.callee)
        args = [self.visit(arg) for arg in node.arguments]
        temp = self.new_temp()
        self.emit("call", ", ".join(args), callee, temp)
        return temp
