"""
符号表测试脚本

运行方式：
    python test_symbol_table.py
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from symbol_table import (
    SymbolTable, 
    Type, 
    ReferenceType, 
    ArrayType, 
    TupleType,
    TYPE_I32, 
    TYPE_UNIT
)


def test_basic_scope():
    """测试1：基础作用域管理"""
    print("\n=== 测试1：基础作用域管理 ===")
    st = SymbolTable()
    
    print(f"初始作用域深度: {st.get_scope_depth()}")
    st.print_scopes()
    
    st.enter_scope()
    print(f"进入作用域后深度: {st.get_scope_depth()}")
    
    st.exit_scope()
    print(f"退出作用域后深度: {st.get_scope_depth()}")
    
    assert st.get_scope_depth() == 1
    print("✅ 通过")


def test_variable_declaration():
    """测试2：变量声明和查询"""
    print("\n=== 测试2：变量声明和查询 ===")
    st = SymbolTable()
    
    st.declare_variable("x", TYPE_I32, is_mutable=True, line=1, col=5)
    st.declare_variable("y", TYPE_I32, is_mutable=False, line=2, col=5)
    
    sym_x = st.lookup("x")
    sym_y = st.lookup("y")
    
    print(f"x: {sym_x}")
    print(f"y: {sym_y}")
    
    assert sym_x is not None
    assert sym_y is not None
    assert sym_x.is_mutable is True
    assert sym_y.is_mutable is False
    assert st.is_mutable("x") is True
    assert st.is_mutable("y") is False
    
    st.mark_initialized("x")
    assert st.is_initialized("x") is True
    assert st.is_initialized("y") is False
    
    sym_z = st.lookup("z")
    assert sym_z is None
    
    print("✅ 通过")


def test_function_declaration():
    """测试3：函数声明"""
    print("\n=== 测试3：函数声明 ===")
    st = SymbolTable()
    
    st.declare_function("main", [], TYPE_I32, line=1, col=1)
    st.declare_function("fib", [TYPE_I32], TYPE_I32, line=2, col=1)
    
    sym_main = st.lookup("main")
    sym_fib = st.lookup("fib")
    
    print(f"main: {sym_main}")
    print(f"fib: {sym_fib}")
    
    assert sym_main is not None
    assert sym_fib is not None
    assert sym_main.return_type == TYPE_I32
    assert sym_fib.param_types == [TYPE_I32]
    
    print("✅ 通过")


def test_nested_scope_and_shadowing():
    """测试4：作用域嵌套和重影"""
    print("\n=== 测试4：作用域嵌套和重影 ===")
    st = SymbolTable()
    
    st.declare_variable("x", TYPE_I32, is_mutable=True, line=1, col=1)
    st.mark_initialized("x")
    
    st.enter_scope()
    st.declare_variable("x", TYPE_I32, is_mutable=False, line=3, col=5)
    st.mark_initialized("x")
    
    sym_inner = st.lookup("x")
    print(f"内层 x: {sym_inner}")
    assert sym_inner.is_mutable is False
    assert sym_inner.scope_level == 1
    
    st.exit_scope()
    
    sym_outer = st.lookup("x")
    print(f"外层 x: {sym_outer}")
    assert sym_outer.is_mutable is True
    assert sym_outer.scope_level == 0
    
    print("✅ 通过")


def test_error_handling():
    """测试5：错误处理"""
    print("\n=== 测试5：错误处理 ===")
    st = SymbolTable()
    
    st.add_error("测试错误", line=10, col=5)
    
    assert st.has_errors() is True
    assert len(st.get_errors()) == 1
    print(f"错误内容: {st.get_errors()[0]}")
    
    st.clear_errors()
    assert st.has_errors() is False
    
    print("✅ 通过")


def test_reference_type():
    """测试6：引用类型"""
    print("\n=== 测试6：引用类型 ===")
    
    ref1 = ReferenceType(TYPE_I32, is_mutable_ref=False)
    print(f"&i32: {ref1}")
    assert str(ref1) == "&i32"
    
    ref2 = ReferenceType(TYPE_I32, is_mutable_ref=True)
    print(f"&mut i32: {ref2}")
    assert str(ref2) == "&mut i32"
    
    ref3 = ReferenceType(ref1, is_mutable_ref=False)
    print(f"&&i32: {ref3}")
    
    print("✅ 通过")


def test_array_type():
    """测试7：数组类型"""
    print("\n=== 测试7：数组类型 ===")
    
    arr = ArrayType(TYPE_I32, length=5)
    print(f"[i32; 5]: {arr}")
    assert str(arr) == "[i32; 5]"
    
    ref_arr = ReferenceType(arr, is_mutable_ref=False)
    print(f"&[i32; 5]: {ref_arr}")
    
    print("✅ 通过")


def test_tuple_type():
    """测试8：元组类型"""
    print("\n=== 测试8：元组类型 ===")
    
    tup = TupleType([TYPE_I32, TYPE_I32])
    print(f"(i32, i32): {tup}")
    assert str(tup) == "(i32, i32)"
    
    tup2 = TupleType([TYPE_I32, tup])
    print(f"(i32, (i32, i32)): {tup2}")
    
    print("✅ 通过")


if __name__ == "__main__":
    print("=" * 50)
    print("符号表模块测试")
    print("=" * 50)
    
    test_basic_scope()
    test_variable_declaration()
    test_function_declaration()
    test_nested_scope_and_shadowing()
    test_error_handling()
    test_reference_type()
    test_array_type()
    test_tuple_type()
    
    print("\n" + "=" * 50)
    print("🎉 所有测试通过！")