"""
类Rust语言词法语法分析器 - 可视化演示程序
文件名: rust_lex_syntax_visualizer.py
浅色美化版本 - 清爽明亮的现代化UI设计
"""

import tkinter as tk
from tkinter import ttk
from enum import Enum
import re

# ==================== 预定义数据 ====================

class TokenType(Enum):
    """词法单元类型"""
    KEYWORD = "关键字"
    IDENTIFIER = "标识符"
    INTEGER = "整数常量"
    FLOAT = "浮点常量"
    STRING = "字符串常量"
    CHAR = "字符常量"
    BOOLEAN = "布尔常量"
    OPERATOR = "运算符"
    BOUNDARY = "界符"
    ATTRIBUTE = "属性标记"
    LIFETIME = "生命周期"
    MACRO = "宏调用"
    COMMENT = "注释"

# 预定义的词法分析结果（模拟Rust代码的词法分析）
PREDEFINED_TOKENS = [
    {"index": 1, "type": TokenType.ATTRIBUTE, "value": "#[derive(Debug)]", "position": "1-17"},
    {"index": 2, "type": TokenType.KEYWORD, "value": "struct", "position": "19-24"},
    {"index": 3, "type": TokenType.IDENTIFIER, "value": "Person", "position": "26-31"},
    {"index": 4, "type": TokenType.BOUNDARY, "value": "{", "position": "33-33"},
    {"index": 5, "type": TokenType.IDENTIFIER, "value": "name", "position": "39-42"},
    {"index": 6, "type": TokenType.BOUNDARY, "value": ":", "position": "43-43"},
    {"index": 7, "type": TokenType.IDENTIFIER, "value": "String", "position": "45-50"},
    {"index": 8, "type": TokenType.BOUNDARY, "value": ",", "position": "51-51"},
    {"index": 9, "type": TokenType.IDENTIFIER, "value": "age", "position": "57-59"},
    {"index": 10, "type": TokenType.BOUNDARY, "value": ":", "position": "60-60"},
    {"index": 11, "type": TokenType.IDENTIFIER, "value": "u32", "position": "62-64"},
    {"index": 12, "type": TokenType.BOUNDARY, "value": ",", "position": "65-65"},
    {"index": 13, "type": TokenType.IDENTIFIER, "value": "email", "position": "71-75"},
    {"index": 14, "type": TokenType.BOUNDARY, "value": ":", "position": "76-76"},
    {"index": 15, "type": TokenType.IDENTIFIER, "value": "Option", "position": "78-83"},
    {"index": 16, "type": TokenType.BOUNDARY, "value": "<", "position": "84-84"},
    {"index": 17, "type": TokenType.IDENTIFIER, "value": "String", "position": "85-90"},
    {"index": 18, "type": TokenType.BOUNDARY, "value": ">", "position": "91-91"},
    {"index": 19, "type": TokenType.BOUNDARY, "value": ",", "position": "92-92"},
    {"index": 20, "type": TokenType.BOUNDARY, "value": "}", "position": "98-98"},
    {"index": 21, "type": TokenType.KEYWORD, "value": "impl", "position": "104-107"},
    {"index": 22, "type": TokenType.IDENTIFIER, "value": "Person", "position": "109-114"},
    {"index": 23, "type": TokenType.BOUNDARY, "value": "{", "position": "116-116"},
    {"index": 24, "type": TokenType.KEYWORD, "value": "fn", "position": "122-123"},
    {"index": 25, "type": TokenType.IDENTIFIER, "value": "new", "position": "125-127"},
    {"index": 26, "type": TokenType.BOUNDARY, "value": "(", "position": "128-128"},
    {"index": 27, "type": TokenType.IDENTIFIER, "value": "name", "position": "129-132"},
    {"index": 28, "type": TokenType.BOUNDARY, "value": ":", "position": "133-133"},
    {"index": 29, "type": TokenType.IDENTIFIER, "value": "String", "position": "135-140"},
    {"index": 30, "type": TokenType.BOUNDARY, "value": ",", "position": "141-141"},
    {"index": 31, "type": TokenType.IDENTIFIER, "value": "age", "position": "143-145"},
    {"index": 32, "type": TokenType.BOUNDARY, "value": ":", "position": "146-146"},
    {"index": 33, "type": TokenType.IDENTIFIER, "value": "u32", "position": "148-150"},
    {"index": 34, "type": TokenType.BOUNDARY, "value": ")", "position": "151-151"},
    {"index": 35, "type": TokenType.OPERATOR, "value": "->", "position": "153-154"},
    {"index": 36, "type": TokenType.IDENTIFIER, "value": "Self", "position": "156-159"},
    {"index": 37, "type": TokenType.BOUNDARY, "value": "{", "position": "161-161"},
    {"index": 38, "type": TokenType.IDENTIFIER, "value": "Self", "position": "167-170"},
    {"index": 39, "type": TokenType.BOUNDARY, "value": "{", "position": "172-172"},
    {"index": 40, "type": TokenType.IDENTIFIER, "value": "name", "position": "178-181"},
    {"index": 41, "type": TokenType.BOUNDARY, "value": ",", "position": "182-182"},
    {"index": 42, "type": TokenType.IDENTIFIER, "value": "age", "position": "188-190"},
    {"index": 43, "type": TokenType.BOUNDARY, "value": ",", "position": "191-191"},
    {"index": 44, "type": TokenType.IDENTIFIER, "value": "email", "position": "197-201"},
    {"index": 45, "type": TokenType.BOUNDARY, "value": ":", "position": "202-202"},
    {"index": 46, "type": TokenType.IDENTIFIER, "value": "None", "position": "204-207"},
    {"index": 47, "type": TokenType.BOUNDARY, "value": "}", "position": "213-213"},
    {"index": 48, "type": TokenType.BOUNDARY, "value": "}", "position": "219-219"},
    {"index": 49, "type": TokenType.KEYWORD, "value": "fn", "position": "225-226"},
    {"index": 50, "type": TokenType.IDENTIFIER, "value": "greet", "position": "228-232"},
    {"index": 51, "type": TokenType.BOUNDARY, "value": "(", "position": "233-233"},
    {"index": 52, "type": TokenType.OPERATOR, "value": "&", "position": "234-234"},
    {"index": 53, "type": TokenType.KEYWORD, "value": "self", "position": "235-238"},
    {"index": 54, "type": TokenType.BOUNDARY, "value": ")", "position": "239-239"},
    {"index": 55, "type": TokenType.OPERATOR, "value": "->", "position": "241-242"},
    {"index": 56, "type": TokenType.IDENTIFIER, "value": "String", "position": "244-249"},
    {"index": 57, "type": TokenType.BOUNDARY, "value": "{", "position": "251-251"},
    {"index": 58, "type": TokenType.IDENTIFIER, "value": "format", "position": "257-262"},
    {"index": 59, "type": TokenType.OPERATOR, "value": "!", "position": "263-263"},
    {"index": 60, "type": TokenType.BOUNDARY, "value": "(", "position": "264-264"},
    {"index": 61, "type": TokenType.STRING, "value": '"Hello, {}!"', "position": "265-276"},
    {"index": 62, "type": TokenType.BOUNDARY, "value": ",", "position": "277-277"},
    {"index": 63, "type": TokenType.IDENTIFIER, "value": "self", "position": "279-282"},
    {"index": 64, "type": TokenType.OPERATOR, "value": ".", "position": "283-283"},
    {"index": 65, "type": TokenType.IDENTIFIER, "value": "name", "position": "284-287"},
    {"index": 66, "type": TokenType.BOUNDARY, "value": ")", "position": "288-288"},
    {"index": 67, "type": TokenType.BOUNDARY, "value": "}", "position": "294-294"},
    {"index": 68, "type": TokenType.BOUNDARY, "value": "}", "position": "300-300"},
    {"index": 69, "type": TokenType.KEYWORD, "value": "fn", "position": "306-307"},
    {"index": 70, "type": TokenType.IDENTIFIER, "value": "main", "position": "309-312"},
    {"index": 71, "type": TokenType.BOUNDARY, "value": "(", "position": "313-313"},
    {"index": 72, "type": TokenType.BOUNDARY, "value": ")", "position": "314-314"},
    {"index": 73, "type": TokenType.BOUNDARY, "value": "{", "position": "316-316"},
    {"index": 74, "type": TokenType.KEYWORD, "value": "let", "position": "322-324"},
    {"index": 75, "type": TokenType.IDENTIFIER, "value": "person", "position": "326-331"},
    {"index": 76, "type": TokenType.OPERATOR, "value": "=", "position": "333-333"},
    {"index": 77, "type": TokenType.IDENTIFIER, "value": "Person", "position": "335-340"},
    {"index": 78, "type": TokenType.OPERATOR, "value": "::", "position": "341-342"},
    {"index": 79, "type": TokenType.IDENTIFIER, "value": "new", "position": "343-345"},
    {"index": 80, "type": TokenType.BOUNDARY, "value": "(", "position": "346-346"},
    {"index": 81, "type": TokenType.STRING, "value": '"Alice"', "position": "347-354"},
    {"index": 82, "type": TokenType.BOUNDARY, "value": ",", "position": "355-355"},
    {"index": 83, "type": TokenType.INTEGER, "value": "30", "position": "357-358"},
    {"index": 84, "type": TokenType.BOUNDARY, "value": ")", "position": "359-359"},
    {"index": 85, "type": TokenType.BOUNDARY, "value": ";", "position": "360-360"},
    {"index": 86, "type": TokenType.KEYWORD, "value": "match", "position": "366-370"},
    {"index": 87, "type": TokenType.IDENTIFIER, "value": "person", "position": "372-377"},
    {"index": 88, "type": TokenType.OPERATOR, "value": ".", "position": "378-378"},
    {"index": 89, "type": TokenType.IDENTIFIER, "value": "email", "position": "379-383"},
    {"index": 90, "type": TokenType.BOUNDARY, "value": "{", "position": "385-385"},
    {"index": 91, "type": TokenType.IDENTIFIER, "value": "Some", "position": "391-394"},
    {"index": 92, "type": TokenType.BOUNDARY, "value": "(", "position": "395-395"},
    {"index": 93, "type": TokenType.IDENTIFIER, "value": "e", "position": "396-396"},
    {"index": 94, "type": TokenType.BOUNDARY, "value": ")", "position": "397-397"},
    {"index": 95, "type": TokenType.OPERATOR, "value": "=>", "position": "399-400"},
    {"index": 96, "type": TokenType.MACRO, "value": "println!", "position": "402-409"},
    {"index": 97, "type": TokenType.BOUNDARY, "value": "(", "position": "410-410"},
    {"index": 98, "type": TokenType.STRING, "value": '"Email: {}"', "position": "411-421"},
    {"index": 99, "type": TokenType.BOUNDARY, "value": ",", "position": "422-422"},
    {"index": 100, "type": TokenType.IDENTIFIER, "value": "e", "position": "424-424"},
    {"index": 101, "type": TokenType.BOUNDARY, "value": ")", "position": "425-425"},
    {"index": 102, "type": TokenType.BOUNDARY, "value": ",", "position": "426-426"},
    {"index": 103, "type": TokenType.IDENTIFIER, "value": "None", "position": "432-435"},
    {"index": 104, "type": TokenType.OPERATOR, "value": "=>", "position": "437-438"},
    {"index": 105, "type": TokenType.MACRO, "value": "println!", "position": "440-447"},
    {"index": 106, "type": TokenType.BOUNDARY, "value": "(", "position": "448-448"},
    {"index": 107, "type": TokenType.STRING, "value": '"No email"', "position": "449-459"},
    {"index": 108, "type": TokenType.BOUNDARY, "value": ")", "position": "460-460"},
    {"index": 109, "type": TokenType.BOUNDARY, "value": ",", "position": "461-461"},
    {"index": 110, "type": TokenType.BOUNDARY, "value": "}", "position": "467-467"},
    {"index": 111, "type": TokenType.KEYWORD, "value": "let", "position": "473-475"},
    {"index": 112, "type": TokenType.IDENTIFIER, "value": "greeting", "position": "477-484"},
    {"index": 113, "type": TokenType.OPERATOR, "value": "=", "position": "486-486"},
    {"index": 114, "type": TokenType.IDENTIFIER, "value": "person", "position": "488-493"},
    {"index": 115, "type": TokenType.OPERATOR, "value": ".", "position": "494-494"},
    {"index": 116, "type": TokenType.IDENTIFIER, "value": "greet", "position": "495-499"},
    {"index": 117, "type": TokenType.BOUNDARY, "value": "(", "position": "500-500"},
    {"index": 118, "type": TokenType.BOUNDARY, "value": ")", "position": "501-501"},
    {"index": 119, "type": TokenType.BOUNDARY, "value": ";", "position": "502-502"},
    {"index": 120, "type": TokenType.MACRO, "value": "println!", "position": "508-515"},
    {"index": 121, "type": TokenType.BOUNDARY, "value": "(", "position": "516-516"},
    {"index": 122, "type": TokenType.STRING, "value": '"{}"', "position": "517-520"},
    {"index": 123, "type": TokenType.BOUNDARY, "value": ",", "position": "521-521"},
    {"index": 124, "type": TokenType.IDENTIFIER, "value": "greeting", "position": "523-530"},
    {"index": 125, "type": TokenType.BOUNDARY, "value": ")", "position": "531-531"},
    {"index": 126, "type": TokenType.BOUNDARY, "value": ";", "position": "532-532"},
    {"index": 127, "type": TokenType.BOUNDARY, "value": "}", "position": "538-538"},
]

# 示例Rust源代码
EXAMPLE_CODE = '''#[derive(Debug)]
struct Person {
    name: String,
    age: u32,
    email: Option<String>,
}

impl Person {
    fn new(name: String, age: u32) -> Self {
        Self {
            name,
            age,
            email: None,
        }
    }
    
    fn greet(&self) -> String {
        format!("Hello, {}!", self.name)
    }
}

fn main() {
    let person = Person::new(String::from("Alice"), 30);
    
    match person.email {
        Some(e) => println!("Email: {}", e),
        None => println!("No email"),
    }
    
    let greeting = person.greet();
    println!("{}", greeting);
}'''

# 预定义的LR(1)分析表数据
LR1_DATA = {
    "states": ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
    "action": {
        ("0", "struct"): "s2", ("0", "impl"): "s3", ("0", "fn"): "s4", ("0", "let"): "s5", ("0", "#"): "acc",
        ("2", "identifier"): "s6", ("2", "{"): "s7",
        ("3", "identifier"): "s8", ("3", "{"): "s9",
        ("4", "identifier"): "s10", ("4", "("): "s11",
        ("5", "identifier"): "s12", ("5", "mut"): "s13",
        ("6", ":"): "s14", ("6", ","): "r1",
        ("7", "identifier"): "s15", ("7", "}"): "r2",
    },
    "goto": {
        ("0", "Program"): "1",
        ("2", "StructDef"): "16",
        ("3", "ImplDef"): "17",
        ("4", "FnDef"): "18",
    },
    "productions": [
        "Program -> Item*",
        "Item -> StructDef | ImplDef | FnDef",
        "StructDef -> 'struct' Identifier '{' Field* '}'",
        "Field -> Identifier ':' Type ','",
        "ImplDef -> 'impl' Identifier '{' Method* '}'",
        "MethodDef -> 'fn' Identifier '(' Parameters ')' '->' Type Block",
        "LetStmt -> 'let' Pattern '=' Expression ';'",
        "MatchExpr -> 'match' Expression '{' MatchArm* '}'",
        "MatchArm -> Pattern '=>' Expression ','",
    ]
}

# 预定义的规约过程
REDUCE_PROCESS = [
    {"step": 1, "state_stack": "[0]", "symbol_stack": "[]", "input": "struct", "action": "移进 struct"},
    {"step": 2, "state_stack": "[0,2]", "symbol_stack": "[struct]", "input": "Person", "action": "移进 Identifier: Person"},
    {"step": 3, "state_stack": "[0,2,6]", "symbol_stack": "[struct, Person]", "input": "{", "action": "移进 {"},
    {"step": 4, "state_stack": "[0,2,6,7]", "symbol_stack": "[struct, Person, {]", "input": "name", "action": "移进 Identifier: name"},
    {"step": 5, "state_stack": "[0,2,6,7,15]", "symbol_stack": "[struct, Person, {, name]", "input": ":", "action": "移进 :"},
    {"step": 6, "state_stack": "[0,2,6,7,15,14]", "symbol_stack": "[struct, Person, {, name, :]", "input": "String", "action": "移进 Type: String"},
    {"step": 7, "state_stack": "[0,2,6,7,15,14,19]", "symbol_stack": "[struct, Person, {, name, :, String]", "input": ",", "action": "规约 Field -> Identifier : Type ,"},
    {"step": 8, "state_stack": "[0,2,6,7,20]", "symbol_stack": "[struct, Person, {, Field]", "input": "age", "action": "继续解析下一个字段..."},
    {"step": 9, "state_stack": "[0,2,6,7,20]", "symbol_stack": "[struct, Person, {, Field*]", "input": "}", "action": "规约 StructDef -> 'struct' Identifier '{' Field* '}'"},
    {"step": 10, "state_stack": "[0,1]", "symbol_stack": "[Program]", "input": "#", "action": "接受 - 语法分析成功"},
]

# 预定义的语法树结构
SYNTAX_TREE = {
    "root": {
        "name": "Program",
        "children": [
            {
                "name": "Item: StructDef",
                "children": [
                    {"name": "Attribute: #[derive(Debug)]", "children": []},
                    {"name": "struct", "children": []},
                    {"name": "Identifier: Person", "children": []},
                    {
                        "name": "Fields",
                        "children": [
                            {"name": "Field: name: String", "children": []},
                            {"name": "Field: age: u32", "children": []},
                            {"name": "Field: email: Option<String>", "children": []},
                        ]
                    }
                ]
            },
            {
                "name": "Item: ImplDef",
                "children": [
                    {"name": "impl", "children": []},
                    {"name": "Identifier: Person", "children": []},
                    {
                        "name": "Methods",
                        "children": [
                            {
                                "name": "Method: new",
                                "children": [
                                    {"name": "Parameters: name: String, age: u32", "children": []},
                                    {"name": "Return: Self", "children": []},
                                    {"name": "Body: Self { name, age, email: None }", "children": []}
                                ]
                            },
                            {
                                "name": "Method: greet",
                                "children": [
                                    {"name": "Parameters: &self", "children": []},
                                    {"name": "Return: String", "children": []},
                                    {"name": "Body: format!(\"Hello, {}!\", self.name)", "children": []}
                                ]
                            }
                        ]
                    }
                ]
            },
            {
                "name": "Item: FnDef - main",
                "children": [
                    {"name": "fn", "children": []},
                    {"name": "Identifier: main", "children": []},
                    {"name": "Parameters: ()", "children": []},
                    {
                        "name": "Block",
                        "children": [
                            {
                                "name": "LetStmt: person",
                                "children": [
                                    {"name": "Pattern: person", "children": []},
                                    {"name": "Expression: Person::new(String::from(\"Alice\"), 30)", "children": []}
                                ]
                            },
                            {
                                "name": "MatchExpr: person.email",
                                "children": [
                                    {"name": "Arm: Some(e) => println!(\"Email: {}\", e)", "children": []},
                                    {"name": "Arm: None => println!(\"No email\")", "children": []}
                                ]
                            },
                            {
                                "name": "LetStmt: greeting",
                                "children": [
                                    {"name": "Pattern: greeting", "children": []},
                                    {"name": "Expression: person.greet()", "children": []}
                                ]
                            },
                            {"name": "MacroCall: println!(\"{}\", greeting)", "children": []}
                        ]
                    }
                ]
            }
        ]
    }
}


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
        self.setup_ui()
        
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
        self.code_text.insert(1.0, EXAMPLE_CODE)
        self.code_text.config(state=tk.NORMAL)  # 先设置为可编辑状态以应用高亮
        self.apply_rust_syntax_highlight()
        self.code_text.config(state=tk.DISABLED)  # 最后设置为只读
        
        # 统计信息栏
        stats_frame = tk.Frame(left_frame, bg=self.colors['surface2'], height=36)
        stats_frame.pack(fill=tk.X, pady=(4, 0))
        stats_frame.pack_propagate(False)
        
        lines = len(EXAMPLE_CODE.split('\n'))
        chars = len(EXAMPLE_CODE)
        
        stats_text = f"📊 {lines} 行  |  {chars} 字符  |  🦀 Rust Edition 2024"
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
        
        # 清除所有已有标签
        for tag in self.code_text.tag_names():
            if tag not in ('sel', 'tk_focus', 'tk_focusNext', 'tk_focusPrev'):
                self.code_text.tag_delete(tag)
        
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
        self.lex_tree.column('位置', width=100, anchor='center')
        
        scroll_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.lex_tree.yview, style='Vertical.TScrollbar')
        scroll_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.lex_tree.xview, style='Horizontal.TScrollbar')
        self.lex_tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        
        self.lex_tree.grid(row=0, column=0, sticky='nsew')
        scroll_y.grid(row=0, column=1, sticky='ns')
        scroll_x.grid(row=1, column=0, sticky='ew')
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # 设置交替行颜色
        for i, token in enumerate(PREDEFINED_TOKENS):
            item_id = self.lex_tree.insert('', tk.END, values=(
                token['index'], token['type'].value, token['value'], token['position']
            ))
            if i % 2 == 0:
                self.lex_tree.tag_configure('oddrow', background=self.colors['surface2'])
                self.lex_tree.item(item_id, tags=('oddrow',))
        
        # 统计栏
        stats_frame = tk.Frame(self.lex_frame, bg=self.colors['surface2'], height=40)
        stats_frame.pack(fill=tk.X, side=tk.BOTTOM)
        stats_frame.pack_propagate(False)
        
        stats_label = tk.Label(
            stats_frame, 
            text=f"✅ 共识别 {len(PREDEFINED_TOKENS)} 个词法单元  |  Rust 词法规范",
            font=('Segoe UI', 10),
            bg=self.colors['surface2'], fg=self.colors['success']
        )
        stats_label.pack(padx=16, pady=10, anchor='w')
        
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
        
        self.generate_syntax_report()
        self.report_text.config(state=tk.DISABLED)
        
        # 配置文本标签样式
        self.report_text.tag_config("success", foreground=self.colors['success'])
        self.report_text.tag_config("warning", foreground=self.colors['warning'])
        self.report_text.tag_config("accent", foreground=self.colors['accent'])
        
    def generate_syntax_report(self):
        """生成语法分析报告 - 浅色版"""
        report = []
        report.append("═" * 80)
        report.append("🦀 RUST 语法分析报告")
        report.append("═" * 80)
        report.append("")
        report.append("✅ 语法分析成功! - 符合 Rust 语法规范")
        report.append("")
        report.append(f"📊 词法单元总数: {len(PREDEFINED_TOKENS)}")
        report.append("")
        
        report.append("📋 语法结构摘要:")
        report.append("─" * 60)
        report.append("  ✓ 属性标记: #[derive(Debug)]")
        report.append("  ✓ 结构体定义: struct Person { ... }")
        report.append("  ✓ 结构体字段: name: String, age: u32, email: Option<String>")
        report.append("  ✓ impl 块: impl Person { ... }")
        report.append("  ✓ 关联函数: fn new(...) -> Self")
        report.append("  ✓ 方法定义: fn greet(&self) -> String")
        report.append("  ✓ let 绑定: let person = Person::new(...)")
        report.append("  ✓ match 模式匹配: match person.email { ... }")
        report.append("  ✓ 宏调用: println!(\"...\", ...)")
        report.append("")
        
        report.append("📖 Rust 文法产生式:")
        report.append("─" * 60)
        for i, prod in enumerate(LR1_DATA['productions']):
            report.append(f"  ({i+1:2d}) {prod}")
        report.append("")
        
        report.append("🎯 Rust 特有语法分析:")
        report.append("─" * 60)
        report.append("  • 模式匹配 (Pattern Matching)")
        report.append("  • 所有权系统 (Ownership System)")
        report.append("  • 生命周期 (Lifetimes)")
        report.append("  • 宏系统 (Macros)")
        report.append("  • 特征系统 (Traits)")
        report.append("  • 枚举类型 (Enums)")
        report.append("")
        
        report.append("═" * 80)
        report.append("✨ 分析完成 - 代码符合 Rust 语法规则")
        
        self.report_text.insert(1.0, '\n'.join(report))
        
    def create_tree_tab(self):
        """创建语法树标签页 - 浅色版"""
        self.tree_frame = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.notebook.add(self.tree_frame, text="🌲 抽象语法树")
        
        tree_view_frame = tk.Frame(self.tree_frame, bg=self.colors['surface2'], bd=1, relief=tk.FLAT)
        tree_view_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        
        self.tree_view = ttk.Treeview(tree_view_frame, style='Treeview', selectmode='browse')
        self.tree_view.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        
        scroll_y = ttk.Scrollbar(tree_view_frame, orient=tk.VERTICAL, command=self.tree_view.yview, style='Vertical.TScrollbar')
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_view.configure(yscrollcommand=scroll_y.set)
        
        def add_tree_nodes(parent, node):
            node_id = self.tree_view.insert(parent, tk.END, text=node['name'], open=True)
            for child in node.get('children', []):
                add_tree_nodes(node_id, child)
                
        add_tree_nodes('', SYNTAX_TREE['root'])
        
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
        """生成LR(1)分析表文本 - 浅色版"""
        table_text = []
        table_text.append("═" * 100)
        table_text.append("🦀 LR(1) 分析表 - Rust 语法")
        table_text.append("═" * 100)
        table_text.append("")
        table_text.append(f"📊 状态数: {len(LR1_DATA['states'])}")
        table_text.append("")
        
        table_text.append("📋 ACTION 表 (移进/规约):")
        table_text.append("─" * 100)
        table_text.append(f"{'状态':<6} {'struct':<10} {'impl':<10} {'fn':<10} {'let':<10} {'identifier':<12} {'#':<6}")
        table_text.append("─" * 100)
        
        action_table = {}
        for (state, symbol), action in LR1_DATA['action'].items():
            if state not in action_table:
                action_table[state] = {}
            action_table[state][symbol] = action
            
        for state in LR1_DATA['states']:
            row = f"{state:<6}"
            for sym in ['struct', 'impl', 'fn', 'let', 'identifier', '#']:
                action = action_table.get(state, {}).get(sym, '')
                row += f"{action:<10}"
            table_text.append(row)
            
        table_text.append("")
        table_text.append("📋 GOTO 表 (状态转移):")
        table_text.append("─" * 80)
        table_text.append(f"{'状态':<6} {'Program':<12} {'StructDef':<12} {'ImplDef':<12} {'FnDef':<10}")
        table_text.append("─" * 80)
        
        goto_table = {}
        for (state, symbol), goto in LR1_DATA['goto'].items():
            if state not in goto_table:
                goto_table[state] = {}
            goto_table[state][symbol] = goto
            
        for state in LR1_DATA['states']:
            row = f"{state:<6}"
            for sym in ['Program', 'StructDef', 'ImplDef', 'FnDef']:
                goto = goto_table.get(state, {}).get(sym, '')
                row += f"{goto:<12}"
            table_text.append(row)
            
        table_text.append("")
        table_text.append("📌 符号说明:")
        table_text.append("─" * 50)
        table_text.append("  s#  - 移进 (shift) 到状态 #")
        table_text.append("  r#  - 规约 (reduce) 使用产生式 #")
        table_text.append("  acc - 接受输入")
        table_text.append("  空  - 错误状态")
        
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
            text="就绪 | 🦀 Rust Edition 2024 | LR(1) 语法分析器 | 支持模式匹配、所有权语义",
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
    print("=" * 60)
    print("🦀 类Rust语言词法语法分析器 - 可视化演示")
    print("=" * 60)
    print("特性:")
    print("  • struct结构体定义")
    print("  • impl实现块")
    print("  • 模式匹配 (match)")
    print("  • 宏调用 (println!等)")
    print("  • Option枚举类型")
    print("  • 所有权语义支持")
    print("")
    print("启动图形界面...")
    print("")
    
    app = RustLexSyntaxVisualizer()
    app.run()