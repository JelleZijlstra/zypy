
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
	assert_parses(str, StatementList([WhileStatement(condition=IntegerToken(42), statements=[ImportsList([ImportStatement("a")])])]))

def test_generator_expression():
	str = '''
while (x for x in y):
	import a
'''
	assert_parses(str, StatementList([
		WhileStatement(
			condition=GeneratorExpression(code=Variable("x"),
				clauses=[ComprehensionClause(type=ForKeyword, variable=Variable("x"), collection=Variable("y"))]),
			statements=[ImportsList([ImportStatement("a")])])]))

def test_for_else():
	str = '''
for x in y:
	import a
else:
	import b
'''
	assert_parses(str, StatementList([
		ForStatement(
			lvalue=Variable("x"),
			collection=Variable("y"),
			statements=[ImportsList([ImportStatement("a")])],
			else_block=[ImportsList([ImportStatement("b")])]
		)]))

def test_multiple_lines():
	str = '''
while True:
	import a
	import b

import c
'''
	assert_parses(str, StatementList([
		WhileStatement(
			condition=Variable("True"),
			statements=[ImportsList([ImportStatement("a")]), ImportsList([ImportStatement("b")])]
		),
		ImportsList([ImportStatement("c")])]))

def test_multiline_while():
	str = '''
while True:
	break
	continue
'''
	assert_parses(str, StatementList([
		WhileStatement(
			condition=Variable("True"),
			statements=[BreakStatement, ContinueStatement]
		)]))


def test_nested_while():
	str = '''
while True:
	break
	while False:
		pass
	pass
'''
	assert_parses(str, StatementList([
		WhileStatement(
			condition=Variable("True"),
			statements=[BreakStatement, WhileStatement(
				condition=Variable('False'),
				statements=[PassStatement]
			), PassStatement]
		)]))


def test_def():
	str = '''
def foo(x):
	pass
'''
	assert_parses(str, StatementList([
		DefStatement('foo', [PassStatement], ['x'], {}, None, None)
	]))

	str = '''
def foo(x, y=3, *args, **kwargs):
	pass
'''
	assert_parses(str, StatementList([
		DefStatement('foo', [PassStatement], ['x'], {'y': IntegerToken(3)}, 'args', 'kwargs')
	]))

def test_with():
	str = '''
with x as y:
	pass
'''
	assert_parses(str, StatementList([
		WithStatement(Variable('x'), 'y', [PassStatement])
	]))
	str = '''
with x:
	pass
'''
	assert_parses(str, StatementList([
		WithStatement(Variable('x'), None, [PassStatement])
	]))

def test_class():
	str = '''
class foo(object):
	pass
'''
	assert_parses(str, StatementList([
		ClassStatement('foo', [Variable('object')], [PassStatement])
	]))
	str = '''
class foo(object, 42):
	pass
'''
	assert_parses(str, StatementList([
		ClassStatement('foo', [Variable('object'), IntegerToken(42)], [PassStatement])
	]))
