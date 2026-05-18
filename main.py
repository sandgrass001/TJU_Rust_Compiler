from __future__ import annotations
import sys
import importlib.util
from types import ModuleType
from pathlib import Path
from typing import Sequence

from error import CompilerError, ErrorReporter
from lexer.lexer import Lexer


def _load_local_parser() -> type:
    parser_path = Path(__file__).with_name("parser.py")
    spec = importlib.util.spec_from_file_location("rust_compiler_parser", parser_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("无法加载本地 parser.py")

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module.Parser


Parser = _load_local_parser()

def compile_source(source: str):
    lexer = Lexer(source)
    tokens = lexer.get_all_tokens()
    parser = Parser(tokens)
    return parser.parse_program()

def main(argv: Sequence[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args:
        print("Usage: python main.py <source-file>")
        return 1

    source_path = Path(args[0])
    if not source_path.exists():
        print(f"File not found: {source_path}")
        return 1

    reporter = ErrorReporter()
    try:
        source = source_path.read_text(encoding="utf-8")
        ast = compile_source(source)
    except CompilerError as exc:
        reporter.report(exc)
        return 1

    print(ast)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
