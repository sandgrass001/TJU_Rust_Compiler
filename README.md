# compiler_project

这是一个用于编译器课程/实验的 Python 项目框架，按词法分析、语法分析、AST、错误处理和测试样例拆分模块。

## 目录结构

- `main.py` 主入口，负责集成词法分析和语法分析
- `lexer.py` 词法分析器
- `parser.py` 语法分析器
- `ast_nodes.py` AST 节点定义
- `token.py` Token 类型定义
- `error.py` 错误处理模块
- `tests/` 测试样例
- `outputs/` 生成输出目录
- `docs/` 文档和截图

## 运行方式

```bash
python main.py tests/test_1_let.txt
```

当前框架已经包含基础的 Token、AST、Lexer、Parser 和错误类型定义，后续可以直接在这些文件里继续补完语法规则和语义分析逻辑。

## 建议的下一步

1. 先补全 `parser.py` 中的声明语句和表达式解析。
2. 再根据实验要求扩展 `ast_nodes.py`。
3. 最后补充自动化测试输出和文档截图。
