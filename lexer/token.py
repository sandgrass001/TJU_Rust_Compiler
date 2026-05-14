# lexer/token.py


from enum import Enum
from dataclasses import dataclass

class TokenType(Enum):
    # 关键字
    I32 = "i32"
    LET = "let"
    IF = "if"
    ELSE = "else"
    WHILE = "while"
    RETURN = "return"
    MUT = "mut"
    FN = "fn"
    FOR = "for"
    IN = "in"
    LOOP = "loop"
    BREAK = "break"
    CONTINUE = "continue"
    
    # 标识符
    IDENT = "IDENT"

    # 数值
    INT = "INT"
    
    # 运算符
    # 赋值号
    ASSIGN = "="
    # 算符
    PLUS = "+"
    MINUS = "-"
    STAR = "*"
    SLASH = "/"
    EQ = "=="
    GT = ">"
    GTE = ">="
    LT = "<"
    LTE = "<="
    NOT_EQ = "!="
    AND = "&"

    
    # 界符
    LPAREN = "("
    RPAREN = ")"
    LBRACE = "{"
    RBRACE = "}"
    LBRACKET = "["
    RBRACKET = "]"
    
    # 分隔符
    SEMICOLON = ";"
    COLON = ":"
    COMMA = ","
    
    # 特殊
    ARROW = "->"
    DOT = "."
    DOTDOT = ".."
    
    # 结束符
    EOF = "EOF"
    ILLEGAL = "ILLEGAL"


@dataclass
class Token:
    type: TokenType # Token类型
    literal: str    # Token原始字符串文本
    line: int       # Token所在行号
    col: int        # Token所在列号

    def __str__(self):
        return f"Token({self.type.value}, '{self.literal}', {self.line}:{self.col})"


# 关键字映射表
KEYWORDS = {
    "let": TokenType.LET,
    "mut": TokenType.MUT,
    "fn": TokenType.FN,
    "return": TokenType.RETURN,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "while": TokenType.WHILE,
    "for": TokenType.FOR,
    "in": TokenType.IN,
    "loop": TokenType.LOOP,
    "break": TokenType.BREAK,
    "continue": TokenType.CONTINUE,
    "i32": TokenType.I32,
}


def lookup_ident(ident: str) -> TokenType:
    """判断标识符是否是关键字"""
    return KEYWORDS.get(ident, TokenType.IDENT)