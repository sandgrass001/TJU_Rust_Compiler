from __future__ import annotations

from interface import RustLexSyntaxVisualizer


def main() -> int:
    app = RustLexSyntaxVisualizer()
    app.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
