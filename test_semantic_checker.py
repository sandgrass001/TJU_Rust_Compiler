import sys
from pathlib import Path
from lexer.lexer import Lexer
from parser import Parser
from symbol_table.symbol_table import SymbolTable
from semantic import SemanticAnalyzer
from error import ErrorReporter, CompilerError

def run_semantic_analysis(source_code: str):
    print("=" * 40)
    print("【源代码】:")
    print(source_code)
    print("-" * 40)
    
    error_reporter = ErrorReporter()
    
    try:
        # 1. 词法分析
        lexer = Lexer(source_code)
        tokens = []
        import lexer.token as token_module # for TokenType
        while True:
            tok = lexer.next_token()
            tokens.append(tok)
            if tok.type == token_module.TokenType.EOF:
                break
        
        # 2. 语法分析 (生成 AST)
        parser = Parser(tokens)
        ast_root = parser.parse_program()
        
        # 3. 语义分析 & 类型检查
        symbol_table = SymbolTable()
        analyzer = SemanticAnalyzer(symbol_table, error_reporter)
        
        analyzer.analyze(ast_root)
        print("✅ 语义分析与类型检查通过！没有任何错误。")
        
    except CompilerError as e:
        print(f"❌ 发现错误: {e}")

if __name__ == "__main__":
    # 测试用例 1: 正常的代码
    test_code_1 = """
    fn add(a: i32, b: i32) -> i32 {
        return a + b;
    }

    fn main() {
        let mut x: i32 = 10;
        x = add(x, 5);
    }
    """
    run_semantic_analysis(test_code_1)
    
    # 测试用例 2: 类型不匹配 (返回类型错误)
    test_code_2 = """
    fn do_something() -> i32 {
        let x = 10;
        return; // 错误：期待 i32 却返回了空 (UNIT)
    }
    """
    run_semantic_analysis(test_code_2)

    # 测试用例 3: 借用规则冲突
    test_code_3 = """
    fn main() {
        let mut a: i32 = 1;
        let b = &mut a;
        let c = &a; // 错误：在同一作用域内，a 已经被可变借用了！
    }
    """
    run_semantic_analysis(test_code_3)
    
    # 测试用例 4: 不可变变量被重新赋值
    test_code_4 = """
    fn main() {
        let x: i32 = 10;
        x = 20; // 错误：x 是不可变的
    }
    """
    run_semantic_analysis(test_code_4)
