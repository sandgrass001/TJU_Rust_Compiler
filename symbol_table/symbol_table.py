"""
符号表核心模块

实现作用域栈管理、符号定义和查询功能

核心数据结构：
    - scopes: 作用域栈，每个元素是一个字典 {符号名: Symbol对象}
    - current_scope_level: 当前作用域层级（0=全局，1=函数，2=代码块...）

使用示例：
    sym_table = SymbolTable()
    sym_table.enter_scope()                    # 进入全局作用域
    sym_table.declare_function("main", [], TYPE_I32)  # 声明函数
    sym_table.enter_scope()                    # 进入函数体
    sym_table.declare_variable("x", TYPE_I32, is_mutable=True)  # 声明变量
    sym_table.mark_initialized("x")            # 标记已初始化
    sym = sym_table.lookup("x")                # 查找符号
    sym_table.exit_scope()                     # 退出作用域
"""

from typing import Optional, Dict, List, Union, Any
from .symbol import (
    Symbol, SymbolKind, Type,
    ReferenceType, ArrayType, TupleType,
    TYPE_I32, TYPE_UNIT, TYPE_ERROR, TYPE_UNKNOWN
)


class SymbolTable:
    """符号表：管理嵌套作用域"""
    
    def __init__(self):
        # 作用域栈：每个元素是一个字典 {符号名: Symbol对象}
        self.scopes: List[Dict[str, Symbol]] = []
        
        # 当前作用域层级（-1 表示未进入任何作用域）
        self.current_scope_level: int = -1
        
        # 错误列表
        self.errors: List[str] = []
        
        # 是否启用错误收集（默认启用）
        self.error_enabled: bool = True
        
        # 初始化：进入全局作用域
        self._enter_scope()
    
    # ==================== 作用域管理 ====================
    
    def _enter_scope(self):
        """内部方法：进入新作用域（不检查，直接进入）"""
        self.scopes.append({})
        self.current_scope_level += 1
    
    def enter_scope(self):
        """
        对外接口：进入新作用域
        
        使用场景：
            - 遇到函数声明时（进入函数体）
            - 遇到代码块 '{' 时
        """
        self._enter_scope()
    
    def exit_scope(self):
        """
        对外接口：退出当前作用域
        
        使用场景：
            - 遇到 '}' 时
            - 函数体解析完毕时
        """
        if self.scopes:
            self.scopes.pop()
            self.current_scope_level -= 1
    
    # ==================== 符号定义 ====================
    
    def _define(self, name: str, symbol: Symbol) -> bool:
        """
        内部方法：在当前作用域定义符号
        
        注意：
            - Rust允许重影（shadowing），同一作用域可以重复定义
            - 如果已存在同名的符号，直接覆盖（实现重影）
        
        返回：
            True 表示定义成功
        """
        if not self.scopes:
            return False
        
        current_scope = self.scopes[-1]
        symbol.scope_level = self.current_scope_level
        current_scope[name] = symbol
        return True
    
    def declare_variable(
        self, 
        name: str, 
        var_type: Union[Type, ReferenceType, ArrayType, TupleType],
        is_mutable: bool = False,
        is_initialized: bool = False,
        line: int = 0, 
        col: int = 0
    ) -> bool:
        """
        声明一个变量
        
        参数：
            name: 变量名
            var_type: 变量类型（Type枚举 或 ReferenceType/ArrayType/TupleType）
            is_mutable: 是否可变（mut关键字）
            is_initialized: 是否已初始化
            line: 声明行号
            col: 声明列号
        
        返回：
            True 表示声明成功
        """
        symbol = Symbol(
            name=name,
            kind=SymbolKind.VARIABLE,
            type=var_type,
            is_mutable=is_mutable,
            is_initialized=is_initialized,
            line=line,
            col=col,
        )
        return self._define(name, symbol)
    
    def declare_parameter(
        self, 
        name: str, 
        param_type: Union[Type, ReferenceType, ArrayType, TupleType],
        is_mutable: bool = False,
        line: int = 0, 
        col: int = 0
    ) -> bool:
        """
        声明一个函数参数
        
        注意：
            - 参数默认是已初始化的（调用时由调用方传入）
            - 参数的可变性由 is_mutable 决定
        
        参数：
            name: 参数名
            param_type: 参数类型
            is_mutable: 是否可变（mut关键字）
            line: 声明行号
            col: 声明列号
        
        返回：
            True 表示声明成功
        """
        symbol = Symbol(
            name=name,
            kind=SymbolKind.PARAMETER,
            type=param_type,
            is_mutable=is_mutable,
            is_initialized=True,      # 参数已初始化
            line=line,
            col=col,
        )
        return self._define(name, symbol)
    
    def declare_function(
        self, 
        name: str, 
        param_types: List[Union[Type, ReferenceType, ArrayType, TupleType]],
        return_type: Union[Type, ReferenceType, ArrayType, TupleType, None] = None,
        line: int = 0, 
        col: int = 0
    ) -> bool:
        """
        声明一个函数
        
        参数：
            name: 函数名
            param_types: 参数类型列表
            return_type: 返回类型（None 表示无返回值）
            line: 声明行号
            col: 声明列号
        
        返回：
            True 表示声明成功
        """
        if return_type is None:
            return_type = TYPE_UNIT
        
        symbol = Symbol(
            name=name,
            kind=SymbolKind.FUNCTION,
            type=return_type,          # 函数作为值时的类型是其返回类型
            param_types=param_types,
            return_type=return_type,
            is_mutable=False,          # 函数符号不可变
            is_initialized=True,       # 函数声明即存在
            line=line,
            col=col,
        )
        return self._define(name, symbol)
    
    # ==================== 符号查询 ====================
    
    def lookup(self, name: str) -> Optional[Symbol]:
        """
        查找符号（从内层作用域向外层查找）
        
        支持重影（shadowing）：返回最内层定义的符号
        
        参数：
            name: 符号名
        
        返回：
            找到的Symbol对象，未找到返回None
        """
        # 从栈顶（最内层）向栈底（最外层）查找
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None
    
    def lookup_current_scope(self, name: str) -> Optional[Symbol]:
        """
        仅在当前作用域查找（不向外层找）
        
        用于检查重复声明等场景
        
        参数：
            name: 符号名
        
        返回：
            找到的Symbol对象，未找到返回None
        """
        if not self.scopes:
            return None
        current_scope = self.scopes[-1]
        return current_scope.get(name)
    
    def is_defined_in_current_scope(self, name: str) -> bool:
        """
        检查符号是否在当前作用域已定义
        
        用于检测重影（shadowing）或重复声明
        """
        return self.lookup_current_scope(name) is not None
    
    # ==================== 初始化状态管理 ====================
    
    def mark_initialized(self, name: str) -> bool:
        """
        标记变量为已初始化
        
        使用场景：
            - 变量声明时带有初始化表达式
            - 变量被赋值时
        
        参数：
            name: 变量名
        
        返回：
            True 表示标记成功，False 表示变量不存在
        """
        symbol = self.lookup(name)
        if symbol and symbol.kind in (SymbolKind.VARIABLE, SymbolKind.PARAMETER):
            symbol.is_initialized = True
            return True
        return False
    
    def is_initialized(self, name: str) -> bool:
        """
        检查变量是否已初始化
        
        用于检查"使用前未初始化"的错误
        
        参数：
            name: 变量名
        
        返回：
            True 表示已初始化，False 表示未初始化或变量不存在
        """
        symbol = self.lookup(name)
        return symbol is not None and symbol.is_initialized
    
    # ==================== 类型查询 ====================
    
    def get_type(self, name: str) -> Optional[Union[Type, ReferenceType, ArrayType, TupleType]]:
        """获取符号的类型"""
        symbol = self.lookup(name)
        return symbol.type if symbol else None
    
    def is_mutable(self, name: str) -> bool:
        """检查变量是否可变"""
        symbol = self.lookup(name)
        return symbol is not None and symbol.is_mutable
    
    # ==================== 错误处理 ====================
    
    def add_error(self, msg: str, line: int = 0, col: int = 0):
        """添加语义错误"""
        if not self.error_enabled:
            return
        if line and col:
            error = f"语义错误 (行:{line}, 列:{col}): {msg}"
        else:
            error = f"语义错误: {msg}"
        self.errors.append(error)
    
    def get_errors(self) -> List[str]:
        """获取所有错误"""
        return self.errors
    
    def has_errors(self) -> bool:
        """是否有错误"""
        return len(self.errors) > 0
    
    def clear_errors(self):
        """清空错误"""
        self.errors.clear()
    
    def disable_errors(self):
        """禁用错误收集（用于测试）"""
        self.error_enabled = False
    
    def enable_errors(self):
        """启用错误收集"""
        self.error_enabled = True
    
    # ==================== 调试辅助 ====================
    
    def print_scopes(self):
        """打印当前所有作用域的内容（调试用）"""
        print(f"\n=== 符号表 (当前层级: {self.current_scope_level}) ===")
        for i, scope in enumerate(self.scopes):
            print(f"  Scope {i}: {list(scope.keys())}")
        print("=" * 40)
    
    def get_current_scope_name(self) -> str:
        """获取当前作用域的简要描述"""
        return f"level_{self.current_scope_level}"
    
    def get_scope_depth(self) -> int:
        """获取当前作用域深度"""
        return len(self.scopes)