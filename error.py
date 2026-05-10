from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CompilerError(Exception):
    message: str
    line: int | None = None
    column: int | None = None

    def __str__(self) -> str:
        location = ""
        if self.line is not None:
            location = f"(line {self.line}"
            if self.column is not None:
                location += f", column {self.column}"
            location += ")"
        return f"{self.message} {location}".strip()


class LexError(CompilerError):
    pass


class ParseError(CompilerError):
    pass


class ErrorReporter:
    def report(self, error: CompilerError) -> None:
        print(f"错误: {error}")
