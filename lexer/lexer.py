# lexer/lexer.py

from .token import Token, TokenType, lookup_ident


class Lexer:
    def __init__(self, input_code: str):
        self.input = input_code
        self.position = 0          # 当前字符在input中的索引
        self.read_position = 0     # 下一个要读取的字符索引
        self.ch = ''               # 当前字符
        self.line = 1              # 当前行号
        self.col = 0               # 当前列号（从0开始，显示时+1）
        self.errors = []           # 词法错误列表
        
        self._read_char()          # 初始化第一个字符
    
    # ==================== 字符读取相关 ====================
    
    def _read_char(self):
        """读取下一个字符，更新位置信息"""
        if self.read_position >= len(self.input):
            self.ch = ''  # EOF
        else:
            self.ch = self.input[self.read_position]
        
        self.position = self.read_position
        self.read_position += 1
        self.col += 1
    
    def _peek_char(self) -> str:
        """预读下一个字符（不移动指针）"""
        if self.read_position >= len(self.input):
            return ''
        return self.input[self.read_position]
    
    # ==================== 跳过空白和注释 ====================
    
    def _skip_whitespace_and_comments(self):
        """跳过空白字符和注释"""
        while self.ch:
            # 跳过空白字符
            if self.ch.isspace():
                if self.ch == '\n':
                    self.line += 1
                    self.col = 0    # 换行后重置列号
                self._read_char()
                continue
            
            # 跳过单行注释 //
            if self.ch == '/' and self._peek_char() == '/':
                while self.ch and self.ch != '\n':  # 一直读到行尾或文件尾
                    self._read_char()
                self.col = 0    # 换行后重置列号
                continue
            
            # 跳过多行注释 /*
            if self.ch == '/' and self._peek_char() == '*':
                self._read_char()  # 消耗 '/'
                self._read_char()  # 消耗 '*'
                while self.ch:
                    if self.ch == '*' and self._peek_char() == '/':
                        self._read_char()  # 消耗 '*'
                        self._read_char()  # 消耗 '/'
                        break
                    if self.ch == '\n':
                        self.line += 1
                        self.col = 0    # 换行后重置列号
                    self._read_char()
                continue
            
            # 不是空白也不是注释，退出循环
            break
    
    # ==================== 读取标识符和数字 ====================
    
    def _read_identifier(self) -> str:
        """读取标识符（字母或下划线开头，后跟字母/数字/下划线）"""
        start_pos = self.position
        while self.ch and (self.ch.isalpha() or self.ch.isdigit() or self.ch == '_'):
            self._read_char()
        return self.input[start_pos:self.position]
    
    def _read_number(self) -> str:
        """读取数字（只支持整数）"""
        start_pos = self.position
        while self.ch and self.ch.isdigit():
            self._read_char()
        return self.input[start_pos:self.position]
    
    # ==================== 错误处理 ====================
    
    def _add_error(self, msg: str, line: int, col: int):
        """添加词法错误"""
        self.errors.append(f"词法错误 (行:{line}, 列:{col}): {msg}")
    
    # ==================== 核心方法：获取下一个Token ====================
    
    def next_token(self) -> Token:
        """获取下一个Token"""
        self._skip_whitespace_and_comments()
        
        # 记录 Token 的起始位置
        start_line = self.line
        start_col = self.col
        
        # 处理不同类型的Token
        token = None
        
        # EOF
        if self.ch == '':
            token = Token(TokenType.EOF, '', start_line, start_col)
        
        # 赋值号 =
        elif self.ch == '=':
            if self._peek_char() == '=':
                # ==
                self._read_char()
                token = Token(TokenType.EQ, '==', start_line, start_col)
            else:
                token = Token(TokenType.ASSIGN, '=', start_line, start_col)
        
        # 算符 +
        elif self.ch == '+':
            token = Token(TokenType.PLUS, '+', start_line, start_col)
        
        # 算符 -
        elif self.ch == '-':
            if self._peek_char() == '>':
                # ->
                self._read_char()
                token = Token(TokenType.ARROW, '->', start_line, start_col)
            else:
                token = Token(TokenType.MINUS, '-', start_line, start_col)
        
        # 算符 *
        elif self.ch == '*':
            token = Token(TokenType.STAR, '*', start_line, start_col)
        
        # 算符 /
        elif self.ch == '/':
            token = Token(TokenType.SLASH, '/', start_line, start_col)
        
        # 算符 < 和 <=
        elif self.ch == '<':
            if self._peek_char() == '=':
                self._read_char()
                token = Token(TokenType.LTE, '<=', start_line, start_col)
            else:
                token = Token(TokenType.LT, '<', start_line, start_col)
        
        # 算符 > 和 >=
        elif self.ch == '>':
            if self._peek_char() == '=':
                self._read_char()
                token = Token(TokenType.GTE, '>=', start_line, start_col)
            else:
                token = Token(TokenType.GT, '>', start_line, start_col)
        
        # 算符 !=
        elif self.ch == '!':
            if self._peek_char() == '=':
                self._read_char()
                token = Token(TokenType.NOT_EQ, '!=', start_line, start_col)
            else:
                self._add_error(f"未识别的字符 '!'", start_line, start_col)
                token = Token(TokenType.ILLEGAL, '!', start_line, start_col)
        
        # 算符 &
        elif self.ch == '&':
            token = Token(TokenType.AND, '&', start_line, start_col)
        
        # 界符 (
        elif self.ch == '(':
            token = Token(TokenType.LPAREN, '(', start_line, start_col)
        
        # 界符 )
        elif self.ch == ')':
            token = Token(TokenType.RPAREN, ')', start_line, start_col)
        
        # 界符 {
        elif self.ch == '{':
            token = Token(TokenType.LBRACE, '{', start_line, start_col)
        
        # 界符 }
        elif self.ch == '}':
            token = Token(TokenType.RBRACE, '}', start_line, start_col)
        
        # 界符 [
        elif self.ch == '[':
            token = Token(TokenType.LBRACKET, '[', start_line, start_col)
        
        # 界符 ]
        elif self.ch == ']':
            token = Token(TokenType.RBRACKET, ']', start_line, start_col)
        
        # 分隔符 ;
        elif self.ch == ';':
            token = Token(TokenType.SEMICOLON, ';', start_line, start_col)
        
        # 分隔符 :
        elif self.ch == ':':
            token = Token(TokenType.COLON, ':', start_line, start_col)
        
        # 分隔符 ,
        elif self.ch == ',':
            token = Token(TokenType.COMMA, ',', start_line, start_col)
        
        # 特殊符号 .
        elif self.ch == '.':
            if self._peek_char() == '.':
                self._read_char()
                token = Token(TokenType.DOTDOT, '..', start_line, start_col)
            else:
                token = Token(TokenType.DOT, '.', start_line, start_col)
        
        # 标识符或关键字
        elif self.ch.isalpha() or self.ch == '_':
            literal = self._read_identifier()   # 读取完整的标识符
            tok_type = lookup_ident(literal)    # 判断是关键字还是普通标识符
            # _read_identifier 已经移动了指针，直接返回
            return Token(tok_type, literal, start_line, start_col)
        
        # 数字
        elif self.ch.isdigit():
            literal = self._read_number()
            return Token(TokenType.INT, literal, start_line, start_col)
        
        # 非法字符
        else:
            self._add_error(f"未识别的字符 '{self.ch}'", start_line, start_col)
            token = Token(TokenType.ILLEGAL, self.ch, start_line, start_col)
        
        # 对于非标识符/数字的token，移动到下一个字符
        if token:
            self._read_char()
        
        return token
    
    # ==================== 辅助方法 ====================
    
    def get_all_tokens(self) -> list:
        """获取所有Token（用于测试）"""
        tokens = []
        while True:
            tok = self.next_token()
            tokens.append(tok)
            if tok.type == TokenType.EOF:
                break
        return tokens
    
    def get_errors(self) -> list:
        """获取所有词法错误"""
        return self.errors
    
    def has_errors(self) -> bool:
        """是否有词法错误"""
        return len(self.errors) > 0