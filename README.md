# TJU Rust Compiler

这是一个用于编译原理课程实验的类 Rust 语言词法 / 语法分析可视化项目。项目包含词法分析器、递归下降语法分析器、AST 节点定义、AST 文本打印和 Graphviz 图形化展示。

## 项目结构

- `main.py`：程序入口，运行后启动可视化界面。
- `interface.py`：Tkinter 图形界面，展示源码、词法分析结果、语法分析报告和抽象语法树。
- `lexer/`：词法分析器与 Token 类型定义。
- `parser.py`：语法分析器，生成 `ast_nodes.py` 中定义的 AST。
- `ast_nodes.py`：AST 节点 dataclass 定义。
- `ast_printer.py`：将 AST 输出为文本树。
- `ast_drawer.py`：使用 Graphviz 将 AST 渲染为图形树。
- `error.py`：错误类型与错误报告。
- `tests/`：测试用例源码。
- `outputs/`、`docs/`：输出与文档相关目录。

## 运行环境

推荐环境：

- Python 3.9 或更新版本
- Tkinter
- Graphviz 可执行程序，即系统中可调用 `dot`
- Python 包：
  - `graphviz`
  - `pillow`
  - `pytest`，仅运行测试时需要

如果使用 Conda，可以创建或进入环境后安装依赖：

```bash
conda activate compiler
conda install -c conda-forge graphviz python-graphviz pillow pytest
```

也可以使用 pip 安装 Python 包：

```bash
pip install graphviz pillow pytest
```

注意：`pip install graphviz` 只安装 Python 调用库，不会安装 Graphviz 程序本体。若 AST 图片无法渲染，请确认 `dot` 可用：

```bash
dot -V
where dot
```

Windows 下 Conda 环境中的 `dot.exe` 通常位于：

```text
<conda_env>\Library\bin\dot.exe
```

## 运行方式

现在直接运行 `main.py` 启动可视化界面：

```bash
python main.py
```

界面启动后会自动加载 `tests/` 目录下的示例 `.rs` 文件。也可以在左侧源码框中修改代码，然后点击“运行分析”重新生成词法结果、语法报告和抽象语法树。



