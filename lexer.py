from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
import re

from error import LexError
from token import Token, TokenType


KEYWORDS = {
    "let": TokenType.LET,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "while": TokenType.WHILE,
    "func": TokenType.FUNC,
    "return": TokenType.RETURN,
}


@dataclass
class Lexer:
    source: str
    index: int = 0
    line: int = 1
    column: int = 1

    def tokenize(self) -> list[Token]:
        tokens: list[Token] = []
        while not self._is_at_end():
            char = self._peek()
            if char in " \r\t":
                self._advance()
                continue
            if char == "\n":
                self._advance_line()
                continue
            start_line, start_column = self.line, self.column
            if char.isalpha() or char == "_":
                tokens.append(self._identifier(start_line, start_column))
                continue
            if char.isdigit():
                tokens.append(self._number(start_line, start_column))
                continue
            if char == '"':
                tokens.append(self._string(start_line, start_column))
                continue
            tokens.append(self._symbol(start_line, start_column))
        tokens.append(Token(TokenType.EOF, "", self.line, self.column))
        return tokens

    def _identifier(self, line: int, column: int) -> Token:
        start = self.index
        while not self._is_at_end() and (self._peek().isalnum() or self._peek() == "_"):
            self._advance()
        lexeme = self.source[start:self.index]
        token_type = KEYWORDS.get(lexeme, TokenType.IDENTIFIER)
        return Token(token_type, lexeme, line, column)

    def _number(self, line: int, column: int) -> Token:
        start = self.index
        while not self._is_at_end() and self._peek().isdigit():
            self._advance()
        lexeme = self.source[start:self.index]
        return Token(TokenType.NUMBER, lexeme, line, column)

    def _string(self, line: int, column: int) -> Token:
        self._advance()
        start = self.index
        while not self._is_at_end() and self._peek() != '"':
            if self._peek() == "\n":
                raise LexError("字符串未闭合", line, column)
            self._advance()
        if self._is_at_end():
            raise LexError("字符串未闭合", line, column)
        lexeme = self.source[start:self.index]
        self._advance()
        return Token(TokenType.STRING, lexeme, line, column)

    def _symbol(self, line: int, column: int) -> Token:
        char = self._advance()
        next_char = self._peek() if not self._is_at_end() else ""
        two_char = char + next_char
        multi = {
            "==": TokenType.EQUAL,
            "!=": TokenType.NOT_EQUAL,
            "<=": TokenType.LESS_EQUAL,
            ">=": TokenType.GREATER_EQUAL,
        }
        if two_char in multi:
            self._advance()
            return Token(multi[two_char], two_char, line, column)
        single = {
            "(": TokenType.LPAREN,
            ")": TokenType.RPAREN,
            "{": TokenType.LBRACE,
            "}": TokenType.RBRACE,
            ",": TokenType.COMMA,
            ";": TokenType.SEMICOLON,
            "=": TokenType.ASSIGN,
            "+": TokenType.PLUS,
            "-": TokenType.MINUS,
            "*": TokenType.STAR,
            "/": TokenType.SLASH,
            "!": TokenType.BANG,
            "<": TokenType.LESS,
            ">": TokenType.GREATER,
        }
        if char not in single:
            raise LexError(f"无法识别的字符: {char}", line, column)
        return Token(single[char], char, line, column)

    def _is_at_end(self) -> bool:
        return self.index >= len(self.source)

    def _peek(self) -> str:
        return self.source[self.index]

    def _advance(self) -> str:
        char = self.source[self.index]
        self.index += 1
        self.column += 1
        return char

    def _advance_line(self) -> None:
        self.index += 1
        self.line += 1
        self.column = 1
