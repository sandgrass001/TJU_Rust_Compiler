from __future__ import annotations

import sys
from pathlib import Path
from typing import Sequence

from error import CompilerError, ErrorReporter
from lexer import Lexer
from parser import Parser


def compile_source(source: str):
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    return parser.parse_program()


def main(argv: Sequence[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args:
        print("用法: python main.py <source-file>")
        return 1

    source_path = Path(args[0])
    if not source_path.exists():
        print(f"文件不存在: {source_path}")
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
