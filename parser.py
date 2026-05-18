from __future__ import annotations

from dataclasses import dataclass

from ast_nodes import (
	AssignmentStatement,
	BinaryExpression,
	CallExpression,
	EmptyStatement,
	Expression,
	ExpressionStatement,
	FunctionDeclaration,
	Identifier,
	IfStatement,
	LetStatement,
	Literal,
	LValue,
	Parameter,
	Program,
	ReturnStatement,
	Statement,
	UnaryExpression,
	WhileStatement,
)
from error import ParseError
from lexer.token import Token, TokenType


@dataclass
class Parser:
	tokens: list[Token]
	current: int = 0

	def parse_program(self) -> Program:
		declarations: list[Statement] = []
		while not self._check(TokenType.EOF):
			declarations.append(self._declaration())
		return Program(body=declarations)

	def _declaration(self) -> Statement:
		if self._match(TokenType.FN):
			return self._function_declaration()
		if self._check(TokenType.IDENT) and self._peek().literal == "func":
			self._advance()
			return self._function_declaration()
		return self._statement()

	def _function_declaration(self) -> FunctionDeclaration:
		name = self._consume(TokenType.IDENT, "函数声明需要函数名")
		self._consume(TokenType.LPAREN, "函数名后缺少 '('")

		parameters: list[Parameter] = []
		if not self._check(TokenType.RPAREN):
			parameters = self._parameter_list()

		self._consume(TokenType.RPAREN, "形参列表后缺少 ')'")

		return_type = None
		if self._match(TokenType.ARROW):
			return_type = self._parse_type()

		body = self._block()
		return FunctionDeclaration(
			name=name.literal,
			parameters=parameters,
			return_type=return_type,
			body=body,
		)

	def _parameter_list(self) -> list[Parameter]:
		parameters = [self._parameter()]
		while self._match(TokenType.COMMA):
			parameters.append(self._parameter())
		return parameters

	def _parameter(self) -> Parameter:
		is_mut = self._match(TokenType.MUT)
		ident = self._consume(TokenType.IDENT, "形参需要标识符")
		self._consume(TokenType.COLON, "形参声明缺少 ':'")
		type_name = self._parse_type()
		return Parameter(name=ident.literal, mutable=is_mut, type_name=type_name)

	def _parse_type(self) -> str:
		if self._match(TokenType.I32):
			return "i32"
		if self._check(TokenType.IDENT):
			return self._advance().literal
		token = self._peek()
		raise ParseError("缺少类型名（当前仅要求支持 i32）", token.line, token.col)

	def _block(self) -> list[Statement]:
		self._consume(TokenType.LBRACE, "语句块缺少 '{'")
		statements: list[Statement] = []
		while not self._check(TokenType.RBRACE) and not self._check(TokenType.EOF):
			statements.append(self._statement())
		self._consume(TokenType.RBRACE, "语句块缺少 '}'")
		return statements

	def _statement(self) -> Statement:
		if self._match(TokenType.SEMICOLON):
			return EmptyStatement()
		if self._match(TokenType.LET):
			return self._let_statement()
		if self._match(TokenType.RETURN):
			return self._return_statement()
		if self._match(TokenType.IF):
			return self._if_statement()
		if self._match(TokenType.WHILE):
			return self._while_statement()
		if self._check(TokenType.IDENT) and self._check_next(TokenType.ASSIGN):
			return self._assignment_statement()
		return self._expression_statement()

	def _let_statement(self) -> LetStatement:
		is_mut = self._match(TokenType.MUT)
		ident = self._consume(TokenType.IDENT, "let 声明缺少变量名")

		type_name = None
		if self._match(TokenType.COLON):
			type_name = self._parse_type()

		value = None
		if self._match(TokenType.ASSIGN):
			value = self._expression()

		self._consume(TokenType.SEMICOLON, "let 语句缺少 ';'")
		return LetStatement(
			name=ident.literal,
			mutable=is_mut,
			type_name=type_name,
			value=value,
		)

	def _assignment_statement(self) -> AssignmentStatement:
		name = self._consume(TokenType.IDENT, "赋值语句左侧需要变量")
		self._consume(TokenType.ASSIGN, "赋值语句缺少 '='")
		value = self._expression()
		self._consume(TokenType.SEMICOLON, "赋值语句缺少 ';'")
		return AssignmentStatement(target=LValue(name=name.literal), value=value)

	def _return_statement(self) -> ReturnStatement:
		if self._match(TokenType.SEMICOLON):
			return ReturnStatement(value=None)

		value = self._expression()
		self._consume(TokenType.SEMICOLON, "return 语句缺少 ';'")
		return ReturnStatement(value=value)

	def _if_statement(self) -> IfStatement:
		condition = self._expression()
		then_branch = self._block()
		else_branch: list[Statement] = []
		if self._match(TokenType.ELSE):
			else_branch = self._block()
		return IfStatement(condition=condition, then_branch=then_branch, else_branch=else_branch)

	def _while_statement(self) -> WhileStatement:
		condition = self._expression()
		body = self._block()
		return WhileStatement(condition=condition, body=body)

	def _expression_statement(self) -> ExpressionStatement:
		expr = self._expression()
		# 兼容样例：文件末尾可省略分号的单个表达式。
		if self._check(TokenType.SEMICOLON):
			self._advance()
		elif not self._check(TokenType.EOF):
			self._consume(TokenType.SEMICOLON, "表达式语句缺少 ';'")
		return ExpressionStatement(expression=expr)

	def _expression(self) -> Expression:
		return self._comparison()

	def _comparison(self) -> Expression:
		expr = self._additive()
		while self._match(
			TokenType.LT,
			TokenType.LTE,
			TokenType.GT,
			TokenType.GTE,
			TokenType.EQ,
			TokenType.NOT_EQ,
		):
			operator = self._previous().literal
			right = self._additive()
			expr = BinaryExpression(left=expr, operator=operator, right=right)
		return expr

	def _additive(self) -> Expression:
		expr = self._term()
		while self._match(TokenType.PLUS, TokenType.MINUS):
			operator = self._previous().literal
			right = self._term()
			expr = BinaryExpression(left=expr, operator=operator, right=right)
		return expr

	def _term(self) -> Expression:
		expr = self._factor()
		while self._match(TokenType.STAR, TokenType.SLASH):
			operator = self._previous().literal
			right = self._factor()
			expr = BinaryExpression(left=expr, operator=operator, right=right)
		return expr

	def _factor(self) -> Expression:
		if self._match(TokenType.AND):
			ident = self._consume(TokenType.IDENT, "'&' 后需要标识符")
			return UnaryExpression(operator="&", operand=Identifier(name=ident.literal))
		if self._match(TokenType.MINUS):
			operand = self._factor()
			return UnaryExpression(operator="-", operand=operand)
		return self._call_or_primary()

	def _call_or_primary(self) -> Expression:
		expr = self._primary()
		while self._match(TokenType.LPAREN):
			args: list[Expression] = []
			if not self._check(TokenType.RPAREN):
				args.append(self._expression())
				while self._match(TokenType.COMMA):
					args.append(self._expression())
			self._consume(TokenType.RPAREN, "函数调用缺少 ')'")
			expr = CallExpression(callee=expr, arguments=args)
		return expr

	def _primary(self) -> Expression:
		if self._match(TokenType.INT):
			return Literal(value=int(self._previous().literal))

		if self._match(TokenType.IDENT):
			return Identifier(name=self._previous().literal)

		if self._match(TokenType.LPAREN):
			expr = self._expression()
			self._consume(TokenType.RPAREN, "括号表达式缺少 ')'")
			return expr

		token = self._peek()
		raise ParseError(f"无法解析表达式，遇到: {token.literal!r}", token.line, token.col)

	def _match(self, *types: TokenType) -> bool:
		for token_type in types:
			if self._check(token_type):
				self._advance()
				return True
		return False

	def _consume(self, token_type: TokenType, message: str) -> Token:
		if self._check(token_type):
			return self._advance()
		token = self._peek()
		raise ParseError(message, token.line, token.col)

	def _check(self, token_type: TokenType) -> bool:
		if self._is_at_end():
			return token_type == TokenType.EOF
		return self._peek().type == token_type

	def _check_next(self, token_type: TokenType) -> bool:
		if self.current + 1 >= len(self.tokens):
			return False
		return self.tokens[self.current + 1].type == token_type

	def _is_at_end(self) -> bool:
		return self._peek().type == TokenType.EOF

	def _peek(self) -> Token:
		return self.tokens[self.current]

	def _previous(self) -> Token:
		return self.tokens[self.current - 1]

	def _advance(self) -> Token:
		if not self._is_at_end():
			self.current += 1
		return self._previous()
