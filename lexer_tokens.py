
def singleton(cls):
	return cls()

class LexerToken(object):
	def __init__(self, value):
		self.value = value

	def __str__(self):
		return str(self.value)

class Keyword(LexerToken):
	keywords = {}

	def __init__(self, value):
		self.value = value
		Keyword.keywords[value] = self

	@classmethod
	def is_keyword(cls, kwd):
		try:
			return cls.keywords[kwd]
		except KeyError:
			return None

DefKeyword = Keyword("def")
ClassKeyword = Keyword("class")
LambdaKeyword = Keyword("lambda")
IfKeyword = Keyword("if")
ElifKeyword = Keyword("elif")
ElseKeyword = Keyword("else")
WhileKeyword = Keyword("while")
ForKeyword = Keyword("for")
InKeyword = Keyword("in")
BreakKeyword = Keyword("break")
ContinueKeyword = Keyword("continue")
WithKeyword = Keyword("with")
AsKeyword = Keyword("as")
ImportKeyword = Keyword("import")
FromKeyword = Keyword("from")
PassKeyword = Keyword("pass")
ReturnKeyword = Keyword("return")
YieldKeyword = Keyword("yield")
TryKeyword = Keyword("try")
ExceptKeyword = Keyword("except")
FinallyKeyword = Keyword("finally")
RaiseKeyword = Keyword("raise")
ExecKeyword = Keyword("exec")
PrintKeyword = Keyword("print")
AssertKeyword = Keyword("assert")
DelKeyword = Keyword("del")
NotKeyword = Keyword("not")
AndKeyword = Keyword("and")
OrKeyword = Keyword("or")
IsKeyword = Keyword("is")
GlobalKeyword = Keyword("global")

class StringToken(LexerToken):
	pass

class IntegerToken(LexerToken):
	pass

class FloatToken(LexerToken):
	pass

class ImaginaryToken(LexerToken):
	def __init__(self, a=0, b=0):
		self.a = a
		self.b = b

	def __str__(self):
		if self.a and self.b:
			return '(%s+%sj)' % (self.a, self.b)
		elif self.a:
			return str(self.a)
		else:
			return str(self.b) + 'j'


class Operator(LexerToken):
	operators = {}

	def __init__(self, value):
		self.value = value
		Operator.operators[value] = self

	@classmethod
	def is_operator(cls, kwd):
		try:
			return cls.operators[kwd]
		except KeyError:
			return None

PlusOperator = Operator("+")
MinusOperator = Operator("-")
MultiplyOperator = Operator("*")
DivideOperator = Operator("/")
ModuloOperator = Operator("%")
AndOperator = Operator("&")
OrOperator = Operator("|")
XorOperator = Operator("^")
ExponentOperator = Operator("**")
FloorDivideOperato = Operator("//")
LeftShiftOperator = Operator("<<")
RightShiftOperator = Operator(">>")
PlusAssignOperator = Operator("+=")
MinusAssignOperator = Operator("-=")
MultiplyAssignOperator = Operator("*=")
DivideAssignOperator = Operator("/=")
ModuloAssignOperator = Operator("%=")
AndAssignOperator = Operator("&=")
OrAssignOperator = Operator("|=")
XorAssignOperator = Operator("^=")
ExponentAssignOperator = Operator("**=")
FloorDivideAssignOperator = Operator("//=")
LeftShiftAssignOperator = Operator("<<=")
RightShiftAssignOperator = Operator(">>=")
ComplementOperator = Operator("~")
AssignmentOperator = Operator("=")
EqualsOperator = Operator("==")
NotEqualsOperator = Operator("!=")
LessThanOperator = Operator("<")
GreaterThanOperator = Operator(">")
LTEOperator = Operator("<=")
GreaterThanOperator = Operator(">=")
AtOperator = Operator("@")
OpeningParenOperator = Operator("(")
ClosingParenOperator = Operator(")")
OpeningCurlyBracketOperator = Operator("{")
ClosingCurlyBracketOperator = Operator("}")
OpeningSquareBracketOperator = Operator("[")
ClosingSquareBracketOperator = Operator("]")
CommaOperator = Operator(",")
DotOperator = Operator(".")
DoubleDotOperator = Operator("..")
ColonOperator = Operator(":")
SemicolonOperator = Operator(";")

class BarewordToken(LexerToken):
	pass

@singleton
class EOFToken(LexerToken):
	def __init__(self):
		pass

	def __str__(self):
		return "<eof>"

	# so we don't have to check for "is not EOFToken" all the time
	def isdigit(self):
		return False

	def isalpha(self):
		return False

	def isspace(self):
		return False

@singleton
class NewlineToken(LexerToken):
	def __init__(self):
		pass

	def __str__(self):
		return "<newline>"

class IndentationToken(LexerToken):
	def __str__(self):
		return "<indentation:%d>" % self.value
