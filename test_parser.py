
from tokens import *
from peeking_iterator import peeking_iterator
import zypy_parser
import lexer

def assert_parses(str, tree):
	parsed = zypy_parser.parse(str)
	assert parsed == tree, "%s != %s" % (parsed, tree)

def test_import():
	assert_parses("import a", StatementList([ImportsList([ImportStatement("a")])]))
	assert_parses("from a import b", StatementList([ImportsList([ImportStatement("a", from_list=[("b", None)])])]))
	assert_parses("import a as b", StatementList([ImportsList([ImportStatement("a", as_name="b")])]))
	assert_parses("import a, b", StatementList([ImportsList([ImportStatement("a"), ImportStatement("b")])]))

def test_number():
	str = '42'
	lexed = lexer.tokenize(str)
	parsed = zypy_parser.parse_expression(peeking_iterator(lexed))
	assert parsed == IntegerToken(42)

def test_while():
	str = '''
while 42:
	import a
'''
	assert_parses(str, StatementList([NullStatement, WhileStatement(condition=IntegerToken(42), statements=[ImportsList([ImportStatement("a")])])]))

def test_generator_expression():
	str = '''
while (x for x in y):
	import a
'''
	assert_parses(str, StatementList([NullStatement,
		WhileStatement(
			condition=GeneratorExpression(code=Variable("x"),
				clauses=[ComprehensionClause(type=ForKeyword, variable=Variable("x"), collection=Variable("y"))]),
			statements=[ImportsList([ImportStatement("a")])])
		]))