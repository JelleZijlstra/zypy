
def singleton(cls):
	cls.__init__ = lambda self: None
	return cls()

class Node(object):
	def __init__(self, value):
		self.value = value

	def __str__(self):
		return str(self.value)

	def __repr__(self):
		return str(self)

	def __ne__(self, other):
		return not (self == other)

	def __eq__(self, other):
		if not isinstance(other, self.__class__):
			return False
		try:
			for key in self.__dict__:
				if not hasattr(key, '__call__'):
					if getattr(self, key) != getattr(other, key):
						return False
			return True
		except AttributeError:
			return False

#
# Lexer
#

class LexerToken(Node):
	pass

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
UnderscoreKeyword = Keyword("_")

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

#
# Parser
#

class ASTNode(Node):
	def __str__(self):
		# hackish but useful dumping method
		out = self.__class__.__name__ + '('

		props = []
		for k, v in self.__dict__.iteritems():
			# exclude methods
			if not hasattr(v, '__call__'):
				props.append("%s=%s" % (k, str(v)))

		out += ', '.join(props)
		return out + ')'

class StatementList(ASTNode):
	def __init__(self, statements=None):
		if not statements:
			statements = []
		self.value = statements

class Statement(ASTNode):
	pass

class ImportsList(Statement):
	'''Set of imports given in a single statement. List members should be ImportStatement instances.'''
	def __init__(self, statements=None):
		if not statements:
			statements = []
		self.value = statements

class ImportStatement(ASTNode):
	def __init__(self, module_name, from_list=[], level=-1, as_name=None):
		self.module_name = module_name
		self.from_list = from_list
		self.level = level
		self.as_name = as_name

class WhileStatement(Statement):
	def __init__(self, condition, statements, else_block=None):
		self.condition = condition
		self.statements = statements
		self.else_block = else_block

class ForStatement(Statement):
	def __init__(self, lvalue, collection, statements, else_block=None):
		self.lvalue = lvalue
		self.collection = collection
		self.statements = statements
		self.else_block = else_block

class DefStatement(Statement):
	def __init__(self, fn_name, statements, args, kwargs, starargs=None, starkwargs=None):
		self.fn_name = fn_name
		self.statements = statements
		self.args = args
		self.kwargs = kwargs
		self.starargs = starargs
		self.starkwargs = starkwargs

class WithStatement(Statement):
	def __init__(self, context_manager, name, statements):
		self.context_manager = context_manager
		self.name = name
		self.statements = statements

class ClassStatement(Statement):
	def __init__(self, class_name, bases, statements):
		self.class_name = class_name
		self.bases = bases
		self.statements = statements

class ReturnStatement(Statement):
	pass

@singleton
class NullStatement(Statement):
	def __str__(self):
		return "<null statement>"

@singleton
class PassStatement(Statement):
	def __str__(self):
		return "pass"

@singleton
class BreakStatement(Statement):
	def __str__(self):
		return "break"

@singleton
class ContinueStatement(Statement):
	def __str__(self):
		return "continue"

class Expression(ASTNode):
	pass

class Variable(Expression):
	pass

class TupleLiteral(Expression):
	pass

class GeneratorExpression(Expression):
	def __init__(self, code, clauses):
		self.code = code
		self.clauses = clauses

class ComprehensionClause(ASTNode):
	def __init__(self, type, condition=None, variable=None, collection=None):
		self.type = type
		if type is ForKeyword:
			assert variable is not None, "for comprehension clause must have variable set"
			assert collection is not None, "for comprehension clause must have collection set"
			self.variable = variable
			self.collection = collection
		elif type is IfKeyword:
			assert condition is not None, "if comprehension clause must have condition set"
			self.condition = condition
		else:
			assert False, "invalid comprehension clause type"

#
# Literals
#


class Literal(LexerToken, ASTNode):
	pass

class StringToken(Literal):
	pass

class IntegerToken(Literal):
	pass

class FloatToken(Literal):
	pass

class ImaginaryToken(Literal):
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

