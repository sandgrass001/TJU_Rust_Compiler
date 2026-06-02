"""
符号定义模块
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, List, Any, Union


class SymbolKind(Enum):
    """符号种类枚举"""
    VARIABLE = "variable"       # 变量
    PARAMETER = "parameter"     # 参数
    FUNCTION = "function"       # 函数


class Type(Enum):
    """基础类型枚举"""
    I32 = "i32"
    UNIT = "unit"
    ERROR = "error"
    UNKNOWN = "unknown"


# 预定义常用类型
TYPE_I32 = Type.I32
TYPE_UNIT = Type.UNIT
TYPE_ERROR = Type.ERROR
TYPE_UNKNOWN = Type.UNKNOWN


@dataclass
class ReferenceType:
    """引用类型"""
    referenced_type: Union[Type, 'ReferenceType', 'ArrayType', 'TupleType']
    is_mutable_ref: bool = False 
    
    def __str__(self) -> str:
        mut_str = "mut " if self.is_mutable_ref else "" # 可变引用增加mut前缀
        if isinstance(self.referenced_type, Type):
            ref_type_str = self.referenced_type.value   # 基本类型，直接取value
        else:
            ref_type_str = str(self.referenced_type)    # 其他类型，递归调用__str__
        return f"&{mut_str}{ref_type_str}"
    
    def __eq__(self, other) -> bool:                    # 自定义比较：当且仅的类型和可变性都相同才认为相等
        if not isinstance(other, ReferenceType):
            return False
        return (self.referenced_type == other.referenced_type and 
                self.is_mutable_ref == other.is_mutable_ref)


@dataclass
class ArrayType:
    """数组类型"""
    element_type: Union[Type, 'ReferenceType', 'ArrayType', 'TupleType']
    length: int
    
    def __str__(self) -> str:
        if isinstance(self.element_type, Type):
            elem_str = self.element_type.value
        else:
            elem_str = str(self.element_type)
        return f"[{elem_str}; {self.length}]"       # 数组类型格式：[元素类型; 长度]
    
    def __eq__(self, other) -> bool:                # 自定义比较：当且仅的元素类型和长度都相同才认为相等
        if not isinstance(other, ArrayType):
            return False
        return (self.element_type == other.element_type and 
                self.length == other.length)


@dataclass
class TupleType:
    """元组类型"""
    element_types: List[Union[Type, 'ReferenceType', 'ArrayType', 'TupleType']]
    
    def __str__(self) -> str:
        parts = []
        for t in self.element_types:
            if isinstance(t, Type):
                parts.append(t.value)
            else:
                parts.append(str(t))
        return f"({', '.join(parts)})"              # 元组类型格式：(元素类型1, 元素类型2, ...)（转换为字符串表示）
    
    def __eq__(self, other) -> bool:                # 自定义比较：当且仅的元素类型列表完全相同才认为相等
        if not isinstance(other, TupleType):
            return False
        return self.element_types == other.element_types


@dataclass
class Symbol:
    """符号信息类"""
    name: str                           # 符号名
    kind: SymbolKind                    # 符号种类（变量、参数、函数）
    type: Union[Type, 'ReferenceType', 'ArrayType', 'TupleType']    # 符号类型（i32、引用、数组、元组）
    is_mutable: bool = False            # 是否可变（mut关键字）
    is_initialized: bool = False        # 是否已初始化
    scope_level: int = 0                # 作用域层级
    line: int = 0                       # 所在行号
    col: int = 0                        # 所在列号

    # 函数特有属性
    # 参数类型列表（仅函数符号有效，其他符号此字段为None或空列表）
    param_types: List[Union[Type, 'ReferenceType', 'ArrayType', 'TupleType']] = field(default_factory=list)
    # 返回类型（仅函数符号有效，其他符号此字段为None）
    return_type: Union[Type, 'ReferenceType', 'ArrayType', 'TupleType', None] = None
    
    # 定义对象的字符串表示形式
    def __str__(self) -> str:
        base = f"Symbol(name={self.name}, kind={self.kind.value}, type={self.type}"
        if self.kind == SymbolKind.FUNCTION:
            base += f", params={self.param_types}, return={self.return_type}"
        return base + ")"