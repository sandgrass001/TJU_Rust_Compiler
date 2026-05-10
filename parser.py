from __future__ import annotations

from dataclasses import dataclass

from ast_nodes import Program
from error import ParseError
from token import Token, TokenType


@dataclass
class Parser:
    tokens: list[Token]
    current: int = 0

    def parse_program(self) -> Program:
        statements = []
        while not self._is_at_end():
            if self._check(TokenType.EOF):
                break
            statements.append(self._declaration())
        return Program(body=statements)

    def _declaration(self):
        token = self._peek()
        raise ParseError(f"暂未实现语法解析，当前位置: {token.lexeme!r}", token.line, token.column)

    def _is_at_end(self) -> bool:
        return self._peek().type == TokenType.EOF

    def _peek(self) -> Token:
        return self.tokens[self.current]

    def _previous(self) -> Token:
        return self.tokens[self.current - 1]

    def _advance(self) -> Token:
        if not self._is_at_end():
            self.current += 1
        return self._previous()

    def _check(self, token_type: TokenType) -> bool:
        if self._is_at_end():
            return token_type == TokenType.EOF
        return self._peek().type == token_type
