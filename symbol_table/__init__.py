# symbol_table/__init__.py
"""
符号表模块
"""

from .symbol import (
    Symbol,
    SymbolKind,
    Type,
    ReferenceType,
    ArrayType,
    TupleType,
    TYPE_I32,      # 添加
    TYPE_UNIT,     # 添加
    TYPE_ERROR,    # 添加
    TYPE_UNKNOWN,  # 添加
)
from .symbol_table import SymbolTable

__all__ = [
    "Symbol",
    "SymbolKind",
    "Type",
    "ReferenceType",
    "ArrayType",
    "TupleType",
    "TYPE_I32",
    "TYPE_UNIT",
    "TYPE_ERROR",
    "TYPE_UNKNOWN",
    "SymbolTable",
]