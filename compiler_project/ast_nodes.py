from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Node:
    pass


@dataclass
class Program(Node):
    body: list[Node] = field(default_factory=list)


@dataclass
class Statement(Node):
    pass


@dataclass
class Expression(Node):
    pass


@dataclass
class LetStatement(Statement):
    name: str
    value: Expression | None = None


@dataclass
class IfStatement(Statement):
    condition: Expression
    then_branch: list[Statement] = field(default_factory=list)
    else_branch: list[Statement] = field(default_factory=list)


@dataclass
class WhileStatement(Statement):
    condition: Expression
    body: list[Statement] = field(default_factory=list)


@dataclass
class FunctionDeclaration(Statement):
    name: str
    parameters: list[str] = field(default_factory=list)
    body: list[Statement] = field(default_factory=list)


@dataclass
class ReturnStatement(Statement):
    value: Expression | None = None


@dataclass
class ExpressionStatement(Statement):
    expression: Expression


@dataclass
class Identifier(Expression):
    name: str


@dataclass
class Literal(Expression):
    value: Any


@dataclass
class BinaryExpression(Expression):
    left: Expression
    operator: str
    right: Expression


@dataclass
class CallExpression(Expression):
    callee: Expression
    arguments: list[Expression] = field(default_factory=list)
