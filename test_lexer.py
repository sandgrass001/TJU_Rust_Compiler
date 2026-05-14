# test_lexer.py

import sys
sys.path.insert(0, '.')

from lexer.lexer import Lexer
from lexer.token import TokenType


def test_basic_tokens():
    """测试基础Token"""
    code = "= == + - * / < <= > >= != & ( ) { } [ ] ; : , . .. ->"
    lexer = Lexer(code)
    
    expected = [
        (TokenType.ASSIGN, '='),
        (TokenType.EQ, '=='),
        (TokenType.PLUS, '+'),
        (TokenType.MINUS, '-'),
        (TokenType.STAR, '*'),
        (TokenType.SLASH, '/'),
        (TokenType.LT, '<'),
        (TokenType.LTE, '<='),
        (TokenType.GT, '>'),
        (TokenType.GTE, '>='),
        (TokenType.NOT_EQ, '!='),
        (TokenType.AND, '&'),
        (TokenType.LPAREN, '('),
        (TokenType.RPAREN, ')'),
        (TokenType.LBRACE, '{'),
        (TokenType.RBRACE, '}'),
        (TokenType.LBRACKET, '['),
        (TokenType.RBRACKET, ']'),
        (TokenType.SEMICOLON, ';'),
        (TokenType.COLON, ':'),
        (TokenType.COMMA, ','),
        (TokenType.DOT, '.'),
        (TokenType.DOTDOT, '..'),
        (TokenType.ARROW, '->'),
        (TokenType.EOF, ''),
    ]
    
    for exp_type, exp_literal in expected:
        tok = lexer.next_token()
        print(f"预期: {exp_type.value:12} '{exp_literal}'")
        print(f"实际: {tok.type.value:12} '{tok.literal}'")
        print("-" * 40)
        assert tok.type == exp_type
        assert tok.literal == exp_literal
    
    print("✅ test_basic_tokens 通过")


def test_keywords_and_identifiers():
    """测试关键字和标识符"""
    code = "let mut fn return if else while for in loop break continue i32 my_var x123 _hello"
    lexer = Lexer(code)
    
    # 预期结果
    expected = [
        (TokenType.LET, 'let'),
        (TokenType.MUT, 'mut'),
        (TokenType.FN, 'fn'),
        (TokenType.RETURN, 'return'),
        (TokenType.IF, 'if'),
        (TokenType.ELSE, 'else'),
        (TokenType.WHILE, 'while'),
        (TokenType.FOR, 'for'),
        (TokenType.IN, 'in'),
        (TokenType.LOOP, 'loop'),
        (TokenType.BREAK, 'break'),
        (TokenType.CONTINUE, 'continue'),
        (TokenType.I32, 'i32'),
        (TokenType.IDENT, 'my_var'),
        (TokenType.IDENT, 'x123'),
        (TokenType.IDENT, '_hello'),
        (TokenType.EOF, ''),
    ]
    
    for exp_type, exp_literal in expected:
        tok = lexer.next_token()
        print(f"预期: {exp_type.value:12} '{exp_literal}'")
        print(f"实际: {tok.type.value:12} '{tok.literal}'")
        print("-" * 40)
        assert tok.type == exp_type
        assert tok.literal == exp_literal
    
    print("✅ test_keywords_and_identifiers 通过")


def test_numbers():
    """测试数字"""
    code = "0 123 45678"
    lexer = Lexer(code)
    
    tok = lexer.next_token()
    assert tok.type == TokenType.INT and tok.literal == '0'
    tok = lexer.next_token()
    assert tok.type == TokenType.INT and tok.literal == '123'
    tok = lexer.next_token()
    assert tok.type == TokenType.INT and tok.literal == '45678'
    tok = lexer.next_token()
    assert tok.type == TokenType.EOF
    
    print("✅ test_numbers 通过")


def test_identifier_vs_keyword():
    """测试标识符和关键字的区分"""
    code = "let123 ifabc"
    lexer = Lexer(code)
    
    tok = lexer.next_token()
    assert tok.type == TokenType.IDENT and tok.literal == 'let123'
    
    tok = lexer.next_token()
    assert tok.type == TokenType.IDENT and tok.literal == 'ifabc'
    
    tok = lexer.next_token()
    assert tok.type == TokenType.EOF
    
    print("✅ test_identifier_vs_keyword 通过")


def test_comments():
    """测试注释"""
    code = """
    let x = 10;  // 这是单行注释
    /* 
       多行注释
       中间内容
    */
    let y = 20;
    """
    lexer = Lexer(code)
    
    tokens = []
    while True:
        tok = lexer.next_token()
        tokens.append(tok.type)
        if tok.type == TokenType.EOF:
            break
    
    # 注释应该被跳过，只保留有效token
    assert TokenType.LET in tokens
    assert TokenType.IDENT in tokens
    assert TokenType.INT in tokens
    assert TokenType.ASSIGN in tokens
    assert TokenType.SEMICOLON in tokens
    
    print("✅ test_comments 通过")


def test_line_and_column():
    """测试行列号追踪"""
    code = "let x\ny = 5;"
    lexer = Lexer(code)
    
    tok1 = lexer.next_token()
    assert tok1.type == TokenType.LET
    assert tok1.line == 1
    assert tok1.col == 1
    
    tok2 = lexer.next_token()
    assert tok2.type == TokenType.IDENT
    assert tok2.literal == 'x'
    assert tok2.line == 1
    assert tok2.col == 5
    
    tok3 = lexer.next_token()
    assert tok3.type == TokenType.IDENT
    assert tok3.literal == 'y'
    assert tok3.line == 2
    assert tok3.col == 1
    
    print("✅ test_line_and_column 通过")


def test_error_handling():
    """测试错误处理"""
    code = "let @ invalid #"
    lexer = Lexer(code)
    
    # let 正常
    tok = lexer.next_token()
    assert tok.type == TokenType.LET
    
    # @ 非法字符
    tok = lexer.next_token()
    assert tok.type == TokenType.ILLEGAL
    assert tok.literal == '@'
    
    # invalid 标识符
    tok = lexer.next_token()
    assert tok.type == TokenType.IDENT
    assert tok.literal == 'invalid'
    
    # # 非法字符
    tok = lexer.next_token()
    assert tok.type == TokenType.ILLEGAL
    assert tok.literal == '#'
    
    # 应该有错误记录
    assert lexer.has_errors()
    print(f"捕获到的错误: {lexer.get_errors()}")
    
    print("✅ test_error_handling 通过")


def test_complete_program():
    """测试完整程序"""
    code = """
fn main() -> i32 {
    let mut x: i32 = 10;
    let y = 20;
    if x > y {
        return x;
    } else {
        return y;
    }
}
"""
    lexer = Lexer(code)
    
    print("\n完整程序词法分析结果：")
    print("=" * 50)
    while True:
        tok = lexer.next_token()
        print(f"{tok.type.value:15} '{tok.literal}' (行:{tok.line}, 列:{tok.col})")
        if tok.type == TokenType.EOF:
            break
    
    if lexer.has_errors():
        print(f"\n错误: {lexer.get_errors()}")
    else:
        print("\n✅ 无词法错误")


if __name__ == "__main__":
    print("=" * 50)
    print("词法分析器测试")
    print("=" * 50 + "\n")
    
    test_basic_tokens()
    print()
    test_keywords_and_identifiers()
    print()
    test_numbers()
    print()
    test_identifier_vs_keyword()
    print()
    test_comments()
    print()
    test_line_and_column()
    print()
    test_error_handling()
    print()
    test_complete_program()
    
    print("\n" + "=" * 50)
    print("🎉 所有测试通过！")