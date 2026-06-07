from typing import Any
from ast_nodes import *
from symbol_table.symbol_table import SymbolTable
from symbol_table.symbol import (
    Symbol, SymbolKind, Type,
    ReferenceType, ArrayType, TupleType,
    TYPE_I32, TYPE_UNIT, TYPE_ERROR, TYPE_UNKNOWN
)
from error import SemanticError, TypeError, BorrowError, ErrorReporter

class SemanticAnalyzer:
    def __init__(self, symbol_table: SymbolTable, error_reporter: ErrorReporter):
        self.symbol_table = symbol_table
        self.error_reporter = error_reporter
        
        # Track borrowings. 
        # For simplicity, we keep a stack of scopes.
        # Inside each scope, we track variable name -> list of borrows.
        # Borrow = {"type": "immutable" | "mutable"}
        self.borrows = [{}]
        self.current_function_return_type = TYPE_UNIT
        self.loop_depth = 0
        
    def _enter_scope(self):
        self.symbol_table.enter_scope()
        self.borrows.append({})
        
    def _exit_scope(self):
        self.borrows.pop()
        self.symbol_table.exit_scope()
        
    def _add_borrow(self, var_name: str, is_mutable: bool):
        # find the variable level
        for scope in reversed(self.borrows):
            if var_name in scope:
                borrows = scope[var_name]
                if is_mutable:
                    if len(borrows) > 0:
                        raise BorrowError(f"Cannot borrow '{var_name}' as mutable because it is already borrowed.")
                else:
                    for b in borrows:
                        if b["type"] == "mutable":
                            raise BorrowError(f"Cannot borrow '{var_name}' as immutable because it is already borrowed as mutable.")
                borrows.append({"type": "mutable" if is_mutable else "immutable"})
                return
        self.borrows[-1][var_name] = [{"type": "mutable" if is_mutable else "immutable"}]

    def analyze(self, node: Node) -> Any:
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node: Node) -> Any:
        raise SemanticError(f"No visit_{type(node).__name__} method")

    def visit_Program(self, node: Program) -> None:
        for stmt in node.body:
            self.analyze(stmt)

    def visit_LetStatement(self, node: LetStatement) -> None:
        expr_type = TYPE_UNKNOWN
        if node.value:
            expr_type = self.analyze(node.value)
            
        declared_type = TYPE_UNKNOWN
        if node.type_name:
            if node.type_name == "i32":
                declared_type = TYPE_I32
            # Handle other explicit types if parsed...
        
        if declared_type != TYPE_UNKNOWN and expr_type != TYPE_UNKNOWN:
            if declared_type != expr_type:
                raise TypeError(f"Type mismatch in let statement for '{node.name}'. Expected {declared_type}, got {expr_type}.")
                
        final_type = declared_type if declared_type != TYPE_UNKNOWN else expr_type
        
        # Use existing define logic from symbol table
        self.symbol_table.declare_variable(
            name=node.name,
            var_type=final_type,
            is_mutable=node.mutable,
            is_initialized=node.value is not None
        )
        # initialize borrow tracking for this var
        self.borrows[-1][node.name] = []

    def visit_AssignmentStatement(self, node: AssignmentStatement) -> None:
        target_name = node.target.name
        sym = self.symbol_table.lookup(target_name)
        if not sym:
            raise SemanticError(f"Variable '{target_name}' is not declared.")
            
        if sym.kind == SymbolKind.VARIABLE and not sym.is_mutable:
            raise SemanticError(f"Cannot assign twice to immutable variable '{target_name}'.")

        value_type = self.analyze(node.value)
        if hasattr(sym, "type") and sym.type != TYPE_UNKNOWN and value_type != TYPE_UNKNOWN:
            if sym.type != value_type:
                raise TypeError(f"Type mismatch in assignment. Expected {sym.type}, got {value_type}.")
                
        # If successfully assigned, mark initialized
        self.symbol_table.mark_initialized(target_name)

    def visit_ExpressionStatement(self, node: ExpressionStatement) -> Any:
        return self.analyze(node.expression)

    def visit_IfStatement(self, node: IfStatement) -> Type:
        cond_type = self.analyze(node.condition)
        # Assuming bool type is needed, but we only have TYPE_I32 right now so we might just check if it's evaluated.
        # Normally cond_type should be something like TYPE_BOOL
        
        self._enter_scope()
        for stmt in node.then_branch:
            self.analyze(stmt)
        self._exit_scope()
        
        if node.else_branch:
            self._enter_scope()
            for stmt in node.else_branch:
                self.analyze(stmt)
            self._exit_scope()
            
        return TYPE_UNIT

    def visit_WhileStatement(self, node: WhileStatement) -> Type:
        cond_type = self.analyze(node.condition)
        self.loop_depth += 1
        self._enter_scope()
        for stmt in node.body:
            self.analyze(stmt)
        self._exit_scope()
        self.loop_depth -= 1
        return TYPE_UNIT

    def visit_ForStatement(self, node: 'ForStatement') -> Type:
        iterable_type = self.analyze(node.iterable)
        iterator_type = TYPE_UNKNOWN
        if isinstance(node.iterable, RangeExpression):
            if iterable_type == TYPE_I32:
                iterator_type = TYPE_I32
            else:
                raise TypeError('for 循环范围表达式必须是 i32 类型')

        self.loop_depth += 1
        self._enter_scope()
        self.symbol_table.declare_variable(
            name=node.iterator,
            var_type=iterator_type,
            is_mutable=False,
            is_initialized=True
        )
        self.borrows[-1][node.iterator] = []
        for stmt in node.body:
            self.analyze(stmt)
        self._exit_scope()
        self.loop_depth -= 1
        return TYPE_UNIT

    def visit_LoopStatement(self, node: 'LoopStatement') -> Type:
        self.loop_depth += 1
        self._enter_scope()
        for stmt in node.body:
            self.analyze(stmt)
        self._exit_scope()
        self.loop_depth -= 1
        return TYPE_UNIT

    def visit_BreakStatement(self, node: 'BreakStatement') -> Type:
        if self.loop_depth == 0:
            raise SemanticError('break 语句只能出现在循环体中')
        return TYPE_UNIT

    def visit_ContinueStatement(self, node: 'ContinueStatement') -> Type:
        if self.loop_depth == 0:
            raise SemanticError('continue 语句只能出现在循环体中')
        return TYPE_UNIT

    def visit_RangeExpression(self, node: 'RangeExpression') -> Type:
        left_type = self.analyze(node.start)
        right_type = self.analyze(node.end)
        if left_type != TYPE_I32 or right_type != TYPE_I32:
            raise TypeError('范围表达式的起始和结束必须是 i32')
        return TYPE_I32

    def visit_FunctionDeclaration(self, node: FunctionDeclaration) -> None:
        # Build return type
        ret_type = TYPE_UNIT
        if node.return_type == "i32":
            ret_type = TYPE_I32
            
        param_types = []
        for param in node.parameters:
            pt = TYPE_I32 if param.type_name == "i32" else TYPE_UNKNOWN
            param_types.append(pt)
            
        self.symbol_table.declare_function(node.name, param_types, ret_type)
        prev_ret_type = self.current_function_return_type
        self.current_function_return_type = ret_type
        
        self._enter_scope()
        for param in node.parameters:
            pt = TYPE_I32 if param.type_name == "i32" else TYPE_UNKNOWN
            self.symbol_table.declare_parameter(param.name, pt, is_mutable=param.mutable)
            self.borrows[-1][param.name] = []
            
        for stmt in node.body:
            self.analyze(stmt)
            
        self._exit_scope()
        self.current_function_return_type = prev_ret_type

    def visit_ReturnStatement(self, node: ReturnStatement) -> Type:
        actual_type = TYPE_UNIT
        if node.value:
            actual_type = self.analyze(node.value)
        if hasattr(self, 'current_function_return_type') and self.current_function_return_type != actual_type:
            raise TypeError(f"Return type mismatch. Expected {self.current_function_return_type}, got {actual_type}.")
        return TYPE_UNIT

    def visit_BinaryExpression(self, node: BinaryExpression) -> Type:
        left_type = self.analyze(node.left)
        right_type = self.analyze(node.right)
        
        if left_type != right_type:
            raise TypeError(f"Mismatched types in binary expression: {left_type} and {right_type}.")
        # Assume i32 for arithmetic
        return left_type

    def visit_UnaryExpression(self, node: UnaryExpression) -> Any:
        if node.operator == "&" or node.operator == "&mut":
            if isinstance(node.operand, Identifier):
                var_name = node.operand.name
                sym = self.symbol_table.lookup(var_name)
                if not sym:
                    raise SemanticError(f"Variable '{var_name}' not found.")
                
                # Cannot borrow immutable as mutable
                if node.operator == "&mut" and not sym.is_mutable:
                    raise BorrowError(f"Cannot borrow '{var_name}' as mutable, as it is not declared as mutable.")
                
                self._add_borrow(var_name, node.operator == "&mut")
                return ReferenceType(referenced_type=sym.type, is_mutable_ref=(node.operator == "&mut"))
            else:
                raise SemanticError("Borrowing non-identifiers is currently unsupported")
                
        elif node.operator == "*":
            # Dereference
            op_type = self.analyze(node.operand)
            if not isinstance(op_type, ReferenceType):
                raise TypeError("Cannot dereference non-reference type.")
            return op_type.referenced_type

        return self.analyze(node.operand)

    def visit_Literal(self, node: Literal) -> Type:
        if isinstance(node.value, int):
            return TYPE_I32
        # Extend with strings/bools as needed
        return TYPE_UNKNOWN

    def visit_Identifier(self, node: Identifier) -> Type:
        sym = self.symbol_table.lookup(node.name)
        if not sym:
            raise SemanticError(f"Variable '{node.name}' is not defined in this scope.")
        # if using uninitialized
        if hasattr(sym, 'is_initialized') and not sym.is_initialized:
            raise SemanticError(f"Use of possibly-uninitialized variable: '{node.name}'")
        return sym.type

    def visit_LValue(self, node: LValue) -> None:
        # Return none, assignment handles it
        pass

    def visit_CallExpression(self, node: CallExpression) -> Type:
        if not isinstance(node.callee, Identifier):
            raise SemanticError("Only function name calls are supported.")
        func_name = node.callee.name
        func_sym = self.symbol_table.lookup(func_name)
        if not func_sym or func_sym.kind != SymbolKind.FUNCTION:
            raise SemanticError(f"'{func_name}' is not a function.")
            
        args_types = [self.analyze(arg) for arg in node.arguments]
        if len(args_types) != len(func_sym.param_types):
            raise TypeError(f"Function '{func_name}' expects {len(func_sym.param_types)} arguments, got {len(args_types)}.")
            
        for i, (expected, actual) in enumerate(zip(func_sym.param_types, args_types)):
            if expected != actual:
                raise TypeError(f"Argument {i+1} of '{func_name}' mismatched. Expected {expected}, got {actual}.")
                
        return func_sym.return_type

    # Extension nodes for array/tuple if they are present in AST (To be completed later)
    # def visit_ArrayAccessExpression(self, node) 
    # def visit_TupleAccessExpression(self, node)
    def visit_IndexExpression(self, node: IndexExpression) -> Type:
        col_type = self.analyze(node.collection)
        idx_type = self.analyze(node.index)
        if idx_type != TYPE_I32:
            raise TypeError('Array index must be of type i32')
        if not isinstance(col_type, ArrayType):
            raise TypeError('Cannot index into non-array type')
        if isinstance(node.index, Literal) and isinstance(node.index.value, int):
            if node.index.value < 0 or node.index.value >= col_type.length:
                raise SemanticError(f'Index {node.index.value} out of bounds for array of length {col_type.length}')
        return col_type.element_type

    def visit_TupleAccessExpression(self, node: TupleAccessExpression) -> Type:
        col_type = self.analyze(node.collection)
        if not isinstance(col_type, TupleType):
            raise TypeError('Cannot access elements on non-tuple type')
        if node.index < 0 or node.index >= len(col_type.element_types):
            raise SemanticError(f'Tuple access index {node.index} out of bounds')
        return col_type.element_types[node.index]


