import sys
from pathlib import Path
from lexer.lexer import Lexer
from parser import Parser
from ir_generator import IRGenerator


def tokenize(source: str):
    lexer = Lexer(source)
    tokens = []
    import lexer.token as token_module
    while True:
        tok = lexer.next_token()
        tokens.append(tok)
        if tok.type == token_module.TokenType.EOF:
            break
    return tokens


def test_ir_generator_simple_function():
    source = '''
    fn add(a: i32, b: i32) -> i32 {
        return a + b;
    }
    '''
    tokens = tokenize(source)
    ast = Parser(tokens).parse_program()
    ir = IRGenerator().generate(ast)

    assert '(func, add, a: i32, b: i32, i32)' in ir
    assert '(+, a, b, t0)' in ir
    assert '(return, t0, _, _)' in ir


def test_ir_generator_control_flow():
    source = '''
    fn main() {
        let mut x: i32 = 1;
        if x < 2 {
            x = x + 1;
        } else {
            x = x - 1;
        }
    }
    '''
    tokens = tokenize(source)
    ast = Parser(tokens).parse_program()
    ir = IRGenerator().generate(ast)

    assert '(func, main, _, unit)' in ir
    assert '(label, L0, _, _)' in ir
    assert '(ifz, t0, _, L1)' in ir or '(ifz, t0, _, L0)' in ir
    assert '(goto, L0, _, _)' in ir or '(goto, L1, _, _)' in ir
