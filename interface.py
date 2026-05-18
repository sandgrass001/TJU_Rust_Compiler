"""
类Rust语言词法语法分析器 - 可视化演示程序
文件名: rust_lex_syntax_visualizer.py
浅色美化版本 - 清爽明亮的现代化UI设计
"""

import importlib.util
import base64
import io
import sys
import tkinter as tk
from tkinter import ttk
import re
from dataclasses import is_dataclass, fields
from pathlib import Path

from ast_drawer import ASTGraphvizDrawer
from ast_printer import ASTPrinter
from lexer.lexer import Lexer
from lexer.token import TokenType as LexerTokenType
from error import ParseError

try:
    from PIL import Image, ImageTk
except ModuleNotFoundError:
    Image = None
    ImageTk = None

# 加载本地 parser.py，避免与标准库 parser 模块冲突
parser_path = Path(__file__).with_name("parser.py")
_spec = importlib.util.spec_from_file_location("local_parser", parser_path)
if _spec is None or _spec.loader is None:
    raise ImportError("无法加载本地 parser.py")
_parser_module = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _parser_module
_spec.loader.exec_module(_parser_module)
Parser = _parser_module.Parser

# 从 tests 目录读取测试用例源代码
TEST_FOLDER = Path(__file__).with_name("tests")
TEST_FILES = [p.name for p in sorted(TEST_FOLDER.glob("*.rs"))]
DEFAULT_TEST_FILE = TEST_FILES[0] if TEST_FILES else None

TOKEN_TYPE_LABELS = {
    LexerTokenType.I32: "类型关键字",
    LexerTokenType.LET: "关键字",
    LexerTokenType.IF: "关键字",
    LexerTokenType.ELSE: "关键字",
    LexerTokenType.WHILE: "关键字",
    LexerTokenType.RETURN: "关键字",
    LexerTokenType.MUT: "关键字",
    LexerTokenType.FN: "关键字",
    LexerTokenType.FOR: "关键字",
    LexerTokenType.IN: "关键字",
    LexerTokenType.LOOP: "关键字",
    LexerTokenType.BREAK: "关键字",
    LexerTokenType.CONTINUE: "关键字",
    LexerTokenType.IDENT: "标识符",
    LexerTokenType.INT: "整数",
    LexerTokenType.ASSIGN: "运算符",
    LexerTokenType.PLUS: "运算符",
    LexerTokenType.MINUS: "运算符",
    LexerTokenType.STAR: "运算符",
    LexerTokenType.SLASH: "运算符",
    LexerTokenType.EQ: "比较运算符",
    LexerTokenType.GT: "比较运算符",
    LexerTokenType.GTE: "比较运算符",
    LexerTokenType.LT: "比较运算符",
    LexerTokenType.LTE: "比较运算符",
    LexerTokenType.NOT_EQ: "比较运算符",
    LexerTokenType.AND: "运算符",
    LexerTokenType.LPAREN: "界符",
    LexerTokenType.RPAREN: "界符",
    LexerTokenType.LBRACE: "界符",
    LexerTokenType.RBRACE: "界符",
    LexerTokenType.LBRACKET: "界符",
    LexerTokenType.RBRACKET: "界符",
    LexerTokenType.SEMICOLON: "分隔符",
    LexerTokenType.COLON: "分隔符",
    LexerTokenType.COMMA: "分隔符",
    LexerTokenType.ARROW: "运算符",
    LexerTokenType.DOT: "运算符",
    LexerTokenType.DOTDOT: "运算符",
    LexerTokenType.EOF: "结束符",
    LexerTokenType.ILLEGAL: "非法字符",
}

LR1_DATA = {
    'states': [],
    'action': {},
    'goto': {},
    'productions': [],
}

REDUCE_PROCESS = []


class RustLexSyntaxVisualizer:
    """类Rust语言词法语法分析可视化展示器 - 浅色美化版"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🦀 Rust词法语法分析器")
        self.root.geometry("1600x1000")
        self.root.configure(bg='#f0f4f8')
        self.root.minsize(1400, 800)
        
        # 浅色主题配色方案 - 清爽明亮
        self.colors = {
            'bg': '#ffffff',           # 主背景 - 纯白
            'bg_light': '#ffffff',      # 纯白背景
            'bg_card': '#ffffff',       # 卡片背景 - 纯白
            'bg_hover': '#e8edf3',      # 悬停背景
            'fg': '#1e293b',            # 主文字色 - 深灰
            'fg_dim': '#64748b',        # 次要文字色 - 灰蓝
            'rust_orange': '#e85d04',   # Rust橙色
            'accent': '#2563eb',        # 蓝色强调
            'accent_light': '#dbeafe',  # 浅蓝背景
            'accent_hover': '#3b82f6',  # 蓝色悬停
            'success': '#16a34a',       # 绿色成功
            'error': '#dc2626',         # 红色错误
            'warning': '#d97706',       # 橙色警告
            'surface': '#ffffff',       # 表面色 - 白
            'surface2': '#f8fafc',      # 二级表面 - 极浅灰
            'surface3': '#e2e8f0',      # 三级表面 - 浅灰
            'border': '#cbd5e1',        # 边框色 - 灰
            'keyword': '#2563eb',       # 关键字蓝
            'type': '#0f766e',          # 类型绿松
            'string': '#b45309',        # 字符串棕橙
            'macro': '#7c3aed',         # 宏紫色
            'attribute': '#ca8a04',     # 属性金黄
            'comment': '#64748b',       # 注释灰
            'identifier': '#1e293b',    # 标识符深灰
        }
        
        self.style = ttk.Style(self.root)
        self.configure_ttk_style()

        self.current_tokens = []
        self.lexer_errors = []
        self.parse_error = None
        self.ast = None
        self.ast_text = ""
        self.ast_image_bytes = None
        self.ast_source_image = None
        self.ast_photo_image = None
        self.ast_zoom = 1.0
        self.ast_fit_zoom = 1.0

        self.AST_NODE_X_GAP = 24
        self.AST_NODE_Y_GAP = 100

        self.setup_ui()
        if DEFAULT_TEST_FILE:
            self.run_analysis()
        
    def configure_ttk_style(self):
        """配置ttk主题样式 - 浅色主题"""
        self.style.theme_use('clam')
        
        # Notebook样式
        self.style.configure('TNotebook', background=self.colors['bg'], borderwidth=0)
        self.style.configure('TNotebook.Tab', 
                           background=self.colors['surface2'],
                           foreground=self.colors['fg_dim'],
                           padding=[16, 10],
                           font=('Segoe UI', 11, 'bold'))
        self.style.map('TNotebook.Tab',
                      background=[('selected', self.colors['accent'])],
                      foreground=[('selected', 'white')],
                      expand=[('selected', [1, 1, 1, 1])])
        
        # 主按钮样式
        self.style.configure('Primary.TButton',
                           background=self.colors['accent'],
                           foreground='white',
                           padding=[12, 8],
                           borderwidth=0,
                           focuscolor='none',
                           font=('Segoe UI', 10, 'bold'))
        self.style.map('Primary.TButton',
                      background=[('active', self.colors['accent_hover']),
                                 ('pressed', self.colors['accent'])])
        
        
        # Treeview样式
        self.style.configure('Treeview',
                           background=self.colors['surface'],
                           fieldbackground=self.colors['surface'],
                           foreground=self.colors['fg'],
                           bordercolor=self.colors['border'],
                           borderwidth=1,
                           rowheight=28,
                           font=('Consolas', 10))
        self.style.configure('Treeview.Heading',
                           background=self.colors['surface2'],
                           foreground=self.colors['fg'],
                           relief='flat',
                           font=('Segoe UI', 10, 'bold'))
        self.style.map('Treeview',
                      background=[('selected', self.colors['accent_light'])],
                      foreground=[('selected', self.colors['accent'])])
        
        # 滚动条样式
        self.style.configure('Vertical.TScrollbar',
                           troughcolor=self.colors['surface2'],
                           background=self.colors['surface3'],
                           arrowcolor=self.colors['fg_dim'],
                           borderwidth=0)
        self.style.configure('Horizontal.TScrollbar',
                           troughcolor=self.colors['surface2'],
                           background=self.colors['surface3'],
                           arrowcolor=self.colors['fg_dim'],
                           borderwidth=0)
        
    def setup_ui(self):
        """设置界面"""
        main_container = tk.Frame(self.root, bg=self.colors['bg'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        
        self.create_title_bar(main_container)
        
        content_frame = tk.Frame(main_container, bg=self.colors['bg'])
        content_frame.pack(fill=tk.BOTH, expand=True, pady=12)
        
        # 使用 grid 布局，设置权重比例
        content_frame.grid_columnconfigure(0, weight=1)  # 代码面板权重1
        content_frame.grid_columnconfigure(1, weight=0)  # 分隔线
        content_frame.grid_columnconfigure(2, weight=2)  # 结果面板权重2
        
        self.create_code_panel(content_frame)
        
        # 分隔线
        separator = tk.Frame(content_frame, bg=self.colors['border'], width=2)
        separator.grid(row=0, column=1, sticky='ns', padx=8)
        
        self.create_result_panel(content_frame)
        self.create_status_bar(main_container)
        self.run_analysis()
        
    def create_title_bar(self, parent):
        """创建标题栏 - 现代化浅色设计"""
        title_frame = tk.Frame(parent, bg=self.colors['bg_card'], height=80, relief=tk.RAISED, bd=1)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        # 左侧标题区域
        left_area = tk.Frame(title_frame, bg=self.colors['bg_card'])
        left_area.pack(side=tk.LEFT, fill=tk.Y, padx=24, pady=12)
        
        title_label = tk.Label(
            left_area,
            text="Rust 词法语法分析器",
            font=('Segoe UI', 24, 'bold'),
            bg=self.colors['bg_card'],
            fg=self.colors['fg']
        )
        title_label.pack(side=tk.LEFT)
        
        
    def create_code_panel(self, parent):
        """创建代码展示面板 - 浅色设计（无行号版本）"""
        left_frame = tk.Frame(parent, bg=self.colors['bg'])
        left_frame.grid(row=0, column=0, sticky='nsew')
        
        # 面板头部
        panel_header = tk.Frame(left_frame, bg=self.colors['bg_card'], height=48)
        panel_header.pack(fill=tk.X)
        panel_header.pack_propagate(False)
        
        header_left = tk.Frame(panel_header, bg=self.colors['bg_card'])
        header_left.pack(side=tk.LEFT, padx=16, pady=8)
        
        icon_label = tk.Label(header_left, text="📄", font=('Segoe UI', 16),
                            bg=self.colors['bg_card'], fg=self.colors['rust_orange'])
        icon_label.pack(side=tk.LEFT)
        
        title_label = tk.Label(header_left, text="Rust 源代码",
                            font=('Segoe UI', 13, 'bold'),
                            bg=self.colors['bg_card'], fg=self.colors['fg'])
        title_label.pack(side=tk.LEFT, padx=(8, 0))
        
        header_right = tk.Frame(panel_header, bg=self.colors['bg_card'])
        header_right.pack(side=tk.RIGHT, padx=16, pady=8)
        
        self.test_selector = ttk.Combobox(header_right, values=TEST_FILES, state='readonly', width=24)
        if DEFAULT_TEST_FILE:
            self.test_selector.set(DEFAULT_TEST_FILE)
        self.test_selector.bind('<<ComboboxSelected>>', self.on_test_selection)
        self.test_selector.pack(side=tk.LEFT, padx=(0, 8))
        
        analyze_button = ttk.Button(header_right, text="运行分析", style='Primary.TButton', command=self.run_analysis)
        analyze_button.pack(side=tk.LEFT)
        
        # 代码区域
        code_frame = tk.Frame(left_frame, bg=self.colors['surface2'], bd=1, relief=tk.FLAT)
        code_frame.pack(fill=tk.BOTH, expand=True, pady=(2, 0))
        
        text_frame = tk.Frame(code_frame, bg=self.colors['surface2'])
        text_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, style='Vertical.TScrollbar')
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 主文本区域
        self.code_text = tk.Text(
            text_frame, font=('Consolas', 12),
            bg=self.colors['bg_light'], fg=self.colors['fg'],
            insertbackground=self.colors['fg'],
            wrap=tk.NONE, padx=16, pady=14,
            yscrollcommand=scrollbar.set,
            bd=0, relief=tk.FLAT, highlightthickness=0,
            selectbackground=self.colors['accent_light'],
            selectforeground=self.colors['accent']
        )
        self.code_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.code_text.yview)
        
        # 添加水平滚动条
        h_scrollbar = ttk.Scrollbar(code_frame, orient=tk.HORIZONTAL, command=self.code_text.xview, style='Horizontal.TScrollbar')
        h_scrollbar.pack(fill=tk.X, padx=12, pady=(0, 12))
        self.code_text.config(xscrollcommand=h_scrollbar.set)
        
        # 插入代码并应用高亮
        if DEFAULT_TEST_FILE:
            self.load_test_case(DEFAULT_TEST_FILE)
        else:
            self.code_text.insert(1.0, "// 未找到 tests 目录中的示例文件")
            self.apply_rust_syntax_highlight()
        
        # 统计信息栏
        stats_frame = tk.Frame(left_frame, bg=self.colors['surface2'], height=36)
        stats_frame.pack(fill=tk.X, pady=(4, 0))
        stats_frame.pack_propagate(False)
        
        current_source = self.code_text.get(1.0, tk.END).rstrip('\n')
        lines = len(current_source.split('\n')) if current_source else 0
        chars = len(current_source)
        
        stats_text = f"📊 {lines} 行  |  {chars} 字符  "
        stats_label = tk.Label(
            stats_frame, text=stats_text,
            font=('Segoe UI', 10),
            bg=self.colors['surface2'], fg=self.colors['accent']
        )
        stats_label.pack(padx=16, pady=8, anchor='w')

    def apply_rust_syntax_highlight(self):
        """应用Rust语法高亮 - 浅色版"""
        # 配置标签样式
        self.code_text.tag_config("keyword", foreground=self.colors['keyword'])
        self.code_text.tag_config("type", foreground=self.colors['type'])
        self.code_text.tag_config("macro", foreground=self.colors['macro'])
        self.code_text.tag_config("string", foreground=self.colors['string'])
        self.code_text.tag_config("attribute", foreground=self.colors['attribute'])
        self.code_text.tag_config("comment", foreground=self.colors['comment'])
        self.code_text.tag_config("number", foreground=self.colors['warning'])
        
        # 获取所有文本内容
        content = self.code_text.get(1.0, tk.END)
        
        # 清除所有已有标签范围（保留标签定义以复用样式）
        for tag in self.code_text.tag_names():
            if tag not in ('sel', 'tk_focus', 'tk_focusNext', 'tk_focusPrev'):
                try:
                    self.code_text.tag_remove(tag, '1.0', tk.END)
                except Exception:
                    # 如果某些标签无法移除，忽略错误以保证高亮过程继续
                    pass
        
        # 初始化使用的标签集合
        self.used_tags = set()
        
        # 逐行处理
        lines = content.split('\n')
        current_pos = 1
        
        for line in lines:
            line_start = f"{current_pos}.0"
            line_end = f"{current_pos}.{len(line)}"
            
            # 高亮属性标记
            if line.strip().startswith('#['):
                self.code_text.tag_add("attribute", line_start, line_end)
                self.used_tags.add("attribute")
            
            # 高亮关键字
            keywords = ['struct', 'impl', 'fn', 'let', 'match', 'Some', 'None', 
                        'Self', 'self', 'return', 'if', 'else', 'loop', 'while', 'for', 'in']
            for kw in keywords:
                self.highlight_pattern_in_line(line_start, line_end, rf'\b{kw}\b', "keyword")
            
            # 高亮类型
            types = ['String', 'Option', 'Person', 'u32', 'i32', 'Self', 'Result', 'Vec', 'Box']
            for t in types:
                self.highlight_pattern_in_line(line_start, line_end, rf'\b{t}\b', "type")
            
            # 高亮宏调用
            self.highlight_pattern_in_line(line_start, line_end, r'\b\w+!', "macro")
            
            # 高亮字符串
            self.highlight_pattern_in_line(line_start, line_end, r'"[^"]*"', "string")
            
            # 高亮数字
            self.highlight_pattern_in_line(line_start, line_end, r'\b\d+\b', "number")
            
            # 高亮注释
            if '//' in line:
                comment_start = line.find('//')
                comment_start_pos = f"{current_pos}.{comment_start}"
                self.code_text.tag_add("comment", comment_start_pos, line_end)
                self.used_tags.add("comment")
            
            current_pos += 1

        # 提高使用的标签优先级
        for tag in self.used_tags:
            self.code_text.tag_raise(tag)

    def highlight_pattern_in_line(self, start_pos, end_pos, pattern, tag):
        """在单行范围内查找并高亮"""
        start = self.code_text.index(start_pos)
        end = self.code_text.index(end_pos)
        text = self.code_text.get(start, end)
        
        for match in re.finditer(pattern, text):
            match_start = f"{start}+{match.start()}c"
            match_end = f"{start}+{match.end()}c"
            self.code_text.tag_add(tag, match_start, match_end)
            self.used_tags.add(tag)
        
    def create_result_panel(self, parent):
        """创建结果展示面板 - 浅色设计"""
        right_frame = tk.Frame(parent, bg=self.colors['bg'])
        right_frame.grid(row=0, column=2, sticky='nsew')
        
        # 面板头部
        panel_header = tk.Frame(right_frame, bg=self.colors['bg_card'], height=48)
        panel_header.pack(fill=tk.X)
        panel_header.pack_propagate(False)
        
        header_left = tk.Frame(panel_header, bg=self.colors['bg_card'])
        header_left.pack(side=tk.LEFT, padx=16, pady=8)
        
        icon_label = tk.Label(header_left, text="🔬", font=('Segoe UI', 16),
                            bg=self.colors['bg_card'], fg=self.colors['rust_orange'])
        icon_label.pack(side=tk.LEFT)
        
        title_label = tk.Label(header_left, text="分析结果",
                            font=('Segoe UI', 13, 'bold'),
                            bg=self.colors['bg_card'], fg=self.colors['fg'])
        title_label.pack(side=tk.LEFT, padx=(8, 0))
        
        # Notebook
        self.notebook = ttk.Notebook(right_frame, style='TNotebook')
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(4, 0))
        
        self.create_lex_tab()
        self.create_syntax_tab()
        self.create_tree_tab()
        self.create_lr_tab()
        self.create_reduce_tab()
            
    def create_lex_tab(self):
        """创建词法分析结果标签页 - 浅色版"""
        self.lex_frame = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.notebook.add(self.lex_frame, text="📝 词法分析")
        
        tree_frame = tk.Frame(self.lex_frame, bg=self.colors['surface2'], bd=1, relief=tk.FLAT)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        
        columns = ('序号', '类型', '值', '位置')
        self.lex_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=20, style='Treeview')
        
        self.lex_tree.heading('序号', text='序号')
        self.lex_tree.heading('类型', text='类型')
        self.lex_tree.heading('值', text='值')
        self.lex_tree.heading('位置', text='位置')
        
        self.lex_tree.column('序号', width=60, anchor='center')
        self.lex_tree.column('类型', width=120)
        self.lex_tree.column('值', width=320)
        self.lex_tree.column('位置', width=120, anchor='center')
        
        scroll_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.lex_tree.yview, style='Vertical.TScrollbar')
        scroll_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.lex_tree.xview, style='Horizontal.TScrollbar')
        self.lex_tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        
        self.lex_tree.grid(row=0, column=0, sticky='nsew')
        scroll_y.grid(row=0, column=1, sticky='ns')
        scroll_x.grid(row=1, column=0, sticky='ew')
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        self.lex_tree.tag_configure('oddrow', background=self.colors['surface2'])
        
        # 统计栏
        stats_frame = tk.Frame(self.lex_frame, bg=self.colors['surface2'], height=40)
        stats_frame.pack(fill=tk.X, side=tk.BOTTOM)
        stats_frame.pack_propagate(False)
        
        self.lex_stats_label = tk.Label(
            stats_frame,
            text="", 
            font=('Segoe UI', 10),
            bg=self.colors['surface2'], fg=self.colors['success']
        )
        self.lex_stats_label.pack(padx=16, pady=10, anchor='w')
        
    def create_syntax_tab(self):
        """创建语法分析结果标签页 - 浅色版"""
        self.syntax_frame = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.notebook.add(self.syntax_frame, text="🔍 语法分析")
        
        result_frame = tk.Frame(self.syntax_frame, bg=self.colors['surface2'], bd=1, relief=tk.FLAT)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        
        self.report_text = tk.Text(
            result_frame, font=('Consolas', 11),
            bg=self.colors['bg_light'], fg=self.colors['fg'],
            wrap=tk.WORD, padx=16, pady=16,
            bd=0, relief=tk.FLAT, highlightthickness=0,
            selectbackground=self.colors['accent_light'],
            selectforeground=self.colors['accent']
        )
        self.report_text.pack(fill=tk.BOTH, expand=True)
        
        scroll_y = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.report_text.yview, style='Vertical.TScrollbar')
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 4))
        self.report_text.config(yscrollcommand=scroll_y.set)
        
        self.report_text.tag_config("success", foreground=self.colors['success'])
        self.report_text.tag_config("warning", foreground=self.colors['warning'])
        self.report_text.tag_config("accent", foreground=self.colors['accent'])
        
    def update_syntax_report(self):
        """生成语法分析报告 - 动态内容"""
        self.report_text.config(state=tk.NORMAL)
        self.report_text.delete(1.0, tk.END)
        report = []
        report.append("═" * 80)
        report.append("🦀 语法分析报告")
        report.append("═" * 80)
        report.append("")
        report.append(f"📊 词法单元总数: {len(self.current_tokens)}")
        report.append("")

        if self.lexer_errors:
            report.append("❌ 词法错误:")
            for error in self.lexer_errors:
                report.append(f"  - {error}")
            report.append("")

        if self.parse_error or self.lexer_errors:
            if self.parse_error:
                report.append("❌ 语法分析失败:")
                report.append(f"  {self.parse_error}")
                report.append("")
            else:
                report.append("❌ 语法诊断: 存在词法错误，语法分析结果可能不准确。")
                report.append("")
            report.append("请修复错误后重新运行分析。")
        else:
            report.append("✅ 语法分析成功! 当前输入符合可解析子集语法。")
            report.append("")
            report.append("📋 语法结构摘要:")
            report.append("─" * 60)
            if self.ast is not None:
                if self.ast_text:
                    report.append("")
                    report.append("AST 文本结构:")
                    report.append("-" * 60)
                    report.append(self.ast_text.rstrip())
                    report.append("")
                report.append(f"  ✓ 程序包含 {len(self.ast.body)} 条顶层声明")
                for node in self.ast.body:
                    report.append(f"  ✓ 声明类型: {node.__class__.__name__}")
            report.append("")
            report.append("📌 支持语法特性:")
            report.append("  • 函数声明: fn name(...) -> type")
            report.append("  • let 绑定与可变变量")
            report.append("  • if 条件语句")
            report.append("  • return 语句")
            report.append("  • 赋值语句与表达式语句")
            report.append("  • 二元运算与函数调用")
            report.append("")

        report.append("═" * 80)
        self.report_text.insert(1.0, '\n'.join(report))
        self.report_text.config(state=tk.DISABLED)
        
    def create_tree_tab(self):
        """创建语法树标签页 - 浅色版"""
        self.tree_frame = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.notebook.add(self.tree_frame, text="🌲 抽象语法树")

        toolbar = tk.Frame(self.tree_frame, bg=self.colors['surface2'], height=40)
        toolbar.pack(fill=tk.X, padx=12, pady=(12, 0))
        toolbar.pack_propagate(False)

        ttk.Button(toolbar, text="-", command=lambda: self.zoom_ast(0.8)).pack(side=tk.LEFT, padx=(8, 4), pady=6)
        ttk.Button(toolbar, text="+", command=lambda: self.zoom_ast(1.25)).pack(side=tk.LEFT, padx=4, pady=6)
        ttk.Button(toolbar, text="fit", command=self.fit_ast_to_canvas).pack(side=tk.LEFT, padx=4, pady=6)
        ttk.Button(toolbar, text="100%", command=lambda: self.set_ast_zoom(1.0)).pack(side=tk.LEFT, padx=4, pady=6)

        self.ast_zoom_label = tk.Label(
            toolbar,
            text="缩放: 100%",
            font=('Segoe UI', 10),
            bg=self.colors['surface2'],
            fg=self.colors['fg_dim']
        )
        self.ast_zoom_label.pack(side=tk.LEFT, padx=12)
        
        canvas_wrapper = tk.Frame(self.tree_frame, bg=self.colors['surface2'], bd=1, relief=tk.FLAT)
        canvas_wrapper.pack(fill=tk.BOTH, expand=True, padx=12, pady=(8, 12))
        
        self.tree_canvas = tk.Canvas(canvas_wrapper, bg=self.colors['bg_light'], highlightthickness=0)
        self.tree_canvas.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        scroll_y = ttk.Scrollbar(canvas_wrapper, orient=tk.VERTICAL, command=self.tree_canvas.yview, style='Vertical.TScrollbar')
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_canvas.configure(yscrollcommand=scroll_y.set)
        
        scroll_x = ttk.Scrollbar(self.tree_frame, orient=tk.HORIZONTAL, command=self.tree_canvas.xview, style='Horizontal.TScrollbar')
        scroll_x.pack(fill=tk.X, padx=12)
        self.tree_canvas.configure(xscrollcommand=scroll_x.set)
        
        self.tree_canvas.bind('<Configure>', self.on_ast_canvas_configure)
        self.tree_canvas.bind('<Control-MouseWheel>', self.on_ast_mousewheel)
        
    def _ast_to_tree_data(self, node):
        if is_dataclass(node):
            node_name = node.__class__.__name__
            children = []
            for field in fields(node):
                value = getattr(node, field.name)
                if value is None:
                    continue
                if isinstance(value, list):
                    if not value:
                        children.append({'name': f"{field.name}: []", 'children': []})
                        continue
                    list_children = []
                    for idx, item in enumerate(value):
                        item_node = self._ast_to_tree_data(item)
                        item_node['name'] = f"[{idx}] {item_node['name']}"
                        list_children.append(item_node)
                    children.append({'name': field.name, 'children': list_children})
                elif is_dataclass(value):
                    child = self._ast_to_tree_data(value)
                    child['name'] = f"{field.name}: {child['name']}"
                    children.append(child)
                else:
                    children.append({'name': f"{field.name}: {value}", 'children': []})
            return {'name': node_name, 'children': children}
        elif isinstance(node, list):
            children = []
            for idx, item in enumerate(node):
                item_node = self._ast_to_tree_data(item)
                item_node['name'] = f"[{idx}] {item_node['name']}"
                children.append(item_node)
            return {
                'name': 'list',
                'children': children,
            }
        else:
            return {'name': repr(node), 'children': []}

    def _measure_ast_text(self, text: str) -> tuple[int, int]:
        width = max(120, len(text) * 7 + 24)
        height = 40
        return width, height

    def _prepare_ast_layout(self, node: dict) -> int:
        node_width, node_height = self._measure_ast_text(node['name'])
        node['node_width'] = node_width
        node['node_height'] = node_height
        if not node.get('children'):
            node['subtree_width'] = node_width
            return node['subtree_width']

        child_widths = [self._prepare_ast_layout(child) for child in node['children']]
        total_children = sum(child_widths) + self.AST_NODE_X_GAP * (len(child_widths) - 1)
        node['subtree_width'] = max(node_width, total_children)
        return node['subtree_width']

    def _assign_ast_positions(self, node: dict, x: int, y: int):
        node['x'] = x + node['subtree_width'] / 2
        node['y'] = y
        if not node.get('children'):
            return

        total_children = sum(child['subtree_width'] for child in node['children']) + self.AST_NODE_X_GAP * (len(node['children']) - 1)
        start_x = x + (node['subtree_width'] - total_children) / 2
        current_x = start_x
        for child in node['children']:
            self._assign_ast_positions(child, current_x, y + self.AST_NODE_Y_GAP)
            current_x += child['subtree_width'] + self.AST_NODE_X_GAP

    def _draw_ast_tree(self, node: dict):
        x = node['x']
        y = node['y']
        w = node['node_width']
        h = node['node_height']
        x0, y0, x1, y1 = x - w / 2, y - h / 2, x + w / 2, y + h / 2

        for child in node.get('children', []):
            self.tree_canvas.create_line(
                x, y1, child['x'], child['y'] - child['node_height'] / 2,
                fill=self.colors['border'], width=2)
            self._draw_ast_tree(child)

        self.tree_canvas.create_rectangle(
            x0, y0, x1, y1,
            fill=self.colors['surface3'], outline=self.colors['border'], width=1)
        self.tree_canvas.create_text(
            x, y,
            text=node['name'],
            font=('Segoe UI', 10),
            fill=self.colors['fg'],
            anchor='c')

    def on_ast_canvas_configure(self, event=None):
        self.tree_canvas.configure(scrollregion=self.tree_canvas.bbox('all'))

    def on_ast_mousewheel(self, event):
        if event.delta > 0:
            self.zoom_ast(1.15)
        elif event.delta < 0:
            self.zoom_ast(1 / 1.15)
        return "break"

    def get_ast_source_size(self):
        if self.ast_source_image is not None:
            return self.ast_source_image.size
        if self.ast_photo_image is not None:
            return self.ast_photo_image.width(), self.ast_photo_image.height()
        return 1, 1

    def calculate_ast_fit_zoom(self):
        self.tree_canvas.update_idletasks()
        source_width, source_height = self.get_ast_source_size()
        canvas_width = max(1, self.tree_canvas.winfo_width() - 40)
        canvas_height = max(1, self.tree_canvas.winfo_height() - 40)
        fit_zoom = min(canvas_width / source_width, canvas_height / source_height)
        return min(1.0, max(0.05, fit_zoom))

    def fit_ast_to_canvas(self):
        if not self.ast_image_bytes:
            return
        self.ast_fit_zoom = self.calculate_ast_fit_zoom()
        self.set_ast_zoom(self.ast_fit_zoom)

    def zoom_ast(self, factor):
        if not self.ast_image_bytes:
            return
        self.set_ast_zoom(self.ast_zoom * factor)

    def set_ast_zoom(self, zoom):
        if not self.ast_image_bytes:
            return
        self.ast_zoom = max(0.05, min(6.0, zoom))
        self.render_ast_image()

    def load_ast_image(self, image_bytes):
        self.ast_image_bytes = image_bytes
        self.ast_source_image = None
        if Image is not None:
            self.ast_source_image = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
        else:
            image_data = base64.b64encode(image_bytes).decode('ascii')
            self.ast_photo_image = tk.PhotoImage(data=image_data)
        self.fit_ast_to_canvas()

    def render_ast_image(self):
        self.tree_canvas.delete('all')
        if not self.ast_image_bytes:
            return

        if self.ast_source_image is not None and ImageTk is not None:
            source_width, source_height = self.ast_source_image.size
            width = max(1, int(source_width * self.ast_zoom))
            height = max(1, int(source_height * self.ast_zoom))
            resample = getattr(getattr(Image, "Resampling", Image), "LANCZOS", Image.BICUBIC)
            resized = self.ast_source_image.resize((width, height), resample)
            self.ast_photo_image = ImageTk.PhotoImage(resized)
        else:
            image_data = base64.b64encode(self.ast_image_bytes).decode('ascii')
            original = tk.PhotoImage(data=image_data)
            if self.ast_zoom >= 1:
                factor = max(1, round(self.ast_zoom))
                self.ast_photo_image = original.zoom(factor, factor)
                self.ast_zoom = float(factor)
            else:
                factor = max(1, int((1 / self.ast_zoom) + 0.9999))
                self.ast_photo_image = original.subsample(factor, factor)
                self.ast_zoom = 1 / factor

        self.tree_canvas.create_image(20, 20, image=self.ast_photo_image, anchor='nw')
        self.tree_canvas.configure(
            scrollregion=(0, 0, self.ast_photo_image.width() + 40, self.ast_photo_image.height() + 40)
        )
        if hasattr(self, 'ast_zoom_label'):
            self.ast_zoom_label.config(text=f"缩放: {int(self.ast_zoom * 100)}%")

    def update_lex_tree(self):
        """更新词法分析结果视图"""
        self.lex_tree.delete(*self.lex_tree.get_children())
        for i, token in enumerate(self.current_tokens, start=1):
            location = f"{token.line}:{token.col + 1}"
            type_name = TOKEN_TYPE_LABELS.get(token.type, token.type.name)
            item_id = self.lex_tree.insert('', tk.END, values=(i, type_name, token.literal, location))
            if i % 2 == 0:
                self.lex_tree.item(item_id, tags=('oddrow',))

        errors_text = "无词法错误"
        if self.lexer_errors:
            errors_text = f"词法错误 {len(self.lexer_errors)} 个"
        self.lex_stats_label.config(text=f"✅ 识别 {len(self.current_tokens)} 个词法单元  |  {errors_text}")

    def on_test_selection(self, event):
        selected = self.test_selector.get()
        if selected:
            self.load_test_case(selected)
            self.run_analysis()

    def load_test_case(self, filename: str):
        file_path = TEST_FOLDER.joinpath(filename)
        if file_path.exists():
            content = file_path.read_text(encoding='utf-8')
            self.code_text.config(state=tk.NORMAL)
            self.code_text.delete(1.0, tk.END)
            self.code_text.insert(1.0, content)
            self.apply_rust_syntax_highlight()
        else:
            self.code_text.config(state=tk.NORMAL)
            self.code_text.delete(1.0, tk.END)
            self.code_text.insert(1.0, f"// 找不到测试文件: {filename}")
            self.apply_rust_syntax_highlight()

    def update_ast_tree(self):
        """使用 ast_drawer.py 生成的 AST 图片更新语法树视图"""
        self.tree_canvas.delete('all')
        self.ast_image_bytes = None
        self.ast_source_image = None
        self.ast_photo_image = None

        if self.ast is None:
            self.tree_canvas.create_text(
                20, 20,
                text='无可视化语法树，先运行分析',
                anchor='nw',
                fill=self.colors['fg'],
                font=('Segoe UI', 12, 'bold'))
            self.tree_canvas.configure(scrollregion=self.tree_canvas.bbox('all'))
            return

        drawer = ASTGraphvizDrawer()
        drawer.visit(self.ast)
        image_bytes = drawer.render_to_memory(str(Path(__file__).parent))

        if image_bytes:
            self.load_ast_image(image_bytes)
            return

        fallback = drawer.graph.source
        self.tree_canvas.create_text(
            20, 20,
            text=f"Graphviz 渲染失败，以下是 AST DOT 源码:\n\n{fallback}",
            anchor='nw',
            fill=self.colors['fg'],
            font=('Consolas', 10))
        self.tree_canvas.configure(scrollregion=self.tree_canvas.bbox('all'))

    def run_analysis(self):
        """执行词法分析和语法分析"""
        source = self.code_text.get('1.0', tk.END).rstrip()
        lexer = Lexer(source)
        self.apply_rust_syntax_highlight()
        self.current_tokens = lexer.get_all_tokens()
        self.lexer_errors = lexer.get_errors()
        self.parse_error = None
        self.ast = None
        self.ast_text = ""

        try:
            parser = Parser(self.current_tokens)
            self.ast = parser.parse_program()
            self.ast_text = ASTPrinter().print_node(self.ast)
        except ParseError as exc:
            self.parse_error = exc

        self.update_lex_tree()
        self.update_syntax_report()
        self.update_ast_tree()
        self.code_text.config(state=tk.NORMAL)

    def create_lr_tab(self):
        """创建LR(1)分析表标签页 - 浅色版"""
        self.lr_frame = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.notebook.add(self.lr_frame, text="📊 LR(1)分析表")
        
        lr_frame_inner = tk.Frame(self.lr_frame, bg=self.colors['bg'])
        lr_frame_inner.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        
        self.lr_text = tk.Text(
            lr_frame_inner, font=('Consolas', 10),
            bg=self.colors['bg_light'], fg=self.colors['fg'],
            wrap=tk.NONE, padx=12, pady=12,
            selectbackground=self.colors['accent_light'],
            selectforeground=self.colors['accent']
        )
        
        scroll_y = ttk.Scrollbar(lr_frame_inner, orient=tk.VERTICAL, command=self.lr_text.yview, style='Vertical.TScrollbar')
        scroll_x = ttk.Scrollbar(lr_frame_inner, orient=tk.HORIZONTAL, command=self.lr_text.xview, style='Horizontal.TScrollbar')
        self.lr_text.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        
        self.lr_text.pack(fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.generate_lr_table_text()
        self.lr_text.config(state=tk.DISABLED)
        
    def generate_lr_table_text(self):
        """生成LR(1)分析表文本 - 说明当前语法分析类型"""
        table_text = []
        table_text.append("═" * 100)
        table_text.append("🦀 语法分析说明")
        table_text.append("═" * 100)
        table_text.append("")
        table_text.append("本演示使用当前项目中的词法分析器和递归下降解析器，而非完整的 LR(1) 分析表。")
        table_text.append("")
        table_text.append("当前支持语法子集说明:")
        table_text.append("─" * 100)
        table_text.append("  • 函数声明 fn name(...) -> type")
        table_text.append("  • let 可变绑定与类型注释")
        table_text.append("  • if 条件语句")
        table_text.append("  • return 语句")
        table_text.append("  • 赋值语句与表达式语句")
        table_text.append("  • 二元运算、函数调用与比较表达式")
        table_text.append("")
        table_text.append("该标签页保留为语法分析说明区，帮助理解项目当前解析能力。")
        table_text.append("")
        table_text.append("提示: 如果需要，可以在本项目后续扩展中补充完整的 LR(1) 分析表。")
        table_text.append("")
        table_text.append("═" * 100)
        self.lr_text.insert(1.0, '\n'.join(table_text))
        
    def create_reduce_tab(self):
        """创建规约过程标签页 - 浅色版"""
        self.reduce_frame = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.notebook.add(self.reduce_frame, text="⚙️ 规约过程")
        
        reduce_frame_inner = tk.Frame(self.reduce_frame, bg=self.colors['bg'])
        reduce_frame_inner.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        
        columns = ('步骤', '状态栈', '符号栈', '输入', '动作')
        self.reduce_tree = ttk.Treeview(reduce_frame_inner, columns=columns, show='headings', height=12, style='Treeview')
        
        for col in columns:
            self.reduce_tree.heading(col, text=col)
            width = 70 if col == '步骤' else (280 if col in ['状态栈', '符号栈'] else 200)
            self.reduce_tree.column(col, width=width)
            
        scroll_y = ttk.Scrollbar(reduce_frame_inner, orient=tk.VERTICAL, command=self.reduce_tree.yview, style='Vertical.TScrollbar')
        scroll_x = ttk.Scrollbar(reduce_frame_inner, orient=tk.HORIZONTAL, command=self.reduce_tree.xview, style='Horizontal.TScrollbar')
        self.reduce_tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        
        self.reduce_tree.grid(row=0, column=0, sticky='nsew')
        scroll_y.grid(row=0, column=1, sticky='ns')
        scroll_x.grid(row=1, column=0, sticky='ew')
        
        reduce_frame_inner.grid_rowconfigure(0, weight=1)
        reduce_frame_inner.grid_columnconfigure(0, weight=1)
        
        for i, step in enumerate(REDUCE_PROCESS):
            item_id = self.reduce_tree.insert('', tk.END, values=(
                step['step'], step['state_stack'], step['symbol_stack'], 
                step['input'], step['action']
            ))
            if i % 2 == 0:
                self.reduce_tree.tag_configure('oddrow', background=self.colors['surface2'])
                self.reduce_tree.item(item_id, tags=('oddrow',))
            
        # 信息栏
        info_frame = tk.Frame(self.reduce_frame, bg=self.colors['surface2'], height=40)
        info_frame.pack(fill=tk.X, side=tk.BOTTOM)
        info_frame.pack_propagate(False)
        
        info_label = tk.Label(
            info_frame,
            text="💡 移进-规约分析过程 | LR(1) 语法分析器逐步构建 AST",
            font=('Segoe UI', 10),
            bg=self.colors['surface2'], fg=self.colors['warning']
        )
        info_label.pack(padx=16, pady=10, anchor='w')
        
    def show_lex_tab(self):
        self.notebook.select(self.lex_frame)
        
    def show_syntax_tab(self):
        self.notebook.select(self.syntax_frame)
        
    def show_tree_tab(self):
        self.notebook.select(self.tree_frame)
        
    def show_lr_tab(self):
        self.notebook.select(self.lr_frame)
        
    def show_reduce_tab(self):
        self.notebook.select(self.reduce_frame)
        
    def create_status_bar(self, parent):
        """创建状态栏 - 浅色设计"""
        status_frame = tk.Frame(parent, bg=self.colors['surface2'], height=32)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        status_frame.pack_propagate(False)
        
        # 左侧状态信息
        left_status = tk.Frame(status_frame, bg=self.colors['surface2'])
        left_status.pack(side=tk.LEFT, padx=16, pady=6)
        
        status_dot = tk.Label(left_status, text="●", font=('Segoe UI', 10),
                             bg=self.colors['surface2'], fg=self.colors['success'])
        status_dot.pack(side=tk.LEFT)
        
        status_label = tk.Label(
            left_status, 
            text="就绪 | LR(1) 语法分析器 | 支持模式匹配、所有权语义",
            bg=self.colors['surface2'], fg=self.colors['fg_dim'],
            font=('Segoe UI', 9)
        )
        status_label.pack(side=tk.LEFT, padx=(6, 0))
        
        # 右侧信息
        right_status = tk.Frame(status_frame, bg=self.colors['surface2'])
        right_status.pack(side=tk.RIGHT, padx=16, pady=6)
        
        memory_label = tk.Label(
            right_status,
            text="LR(1) 分析器 • 移进-规约分析",
            bg=self.colors['surface2'], fg=self.colors['accent'],
            font=('Segoe UI', 9, 'bold')
        )
        memory_label.pack(side=tk.LEFT)
        
    def run(self):
        """运行程序"""
        self.root.mainloop()


if __name__ == "__main__":
    app = RustLexSyntaxVisualizer()
    app.run()
