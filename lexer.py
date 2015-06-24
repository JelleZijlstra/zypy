PUNCTUATION_CHARS = set("+-*/%&|^@=></,.!()[]{}~:;\"'\\")
QUOTE_CHARS = set("'\"")

from peeking_iterator import peeking_iterator
from tokens import *

class lexer_error(Exception):
	pass

def consume_while(it, pred):
	"""Eat all characters out of the iterator while predicate pred holds true; returns their concatenation"""
	out = ""
	while True:
		c = it.peek()
		if c is not EOFToken and pred(c):
			out += c
			it.next()
		else:
			return out

def initialize_operators():
	def add_to_tree(tree, op, obj):
		if len(op) == 1:
			if op in tree:
				_, subtree = tree[op]
				tree[op] = obj, subtree
			else:
				tree[op] = obj, {}
		else:
			if op[0] not in tree:
				tree[op[0]] = None, {}
			add_to_tree(tree[op[0]][1], op[1:], obj)

	tree = {}
	data = Operator.operators
	for op, obj in data.iteritems():
		add_to_tree(tree, op, obj)
	return tree

def get_operators(tree, c, it):
	if c in tree:
		next = it.peek()
		obj, subtree = tree[c]
		if next in subtree:
			it.next()
			return get_operators(subtree, next, it)
		else:
			return obj

def tokenize(string):
	it = peeking_iterator(iter(string), end_default=EOFToken)
	tree = initialize_operators()

	# yell about whitespace at beginning of file
	c = it.peek()
	if c.isspace() and c != '\n':
		raise lexer_error("Unexpected whitespace at beginning of file")

	while it.has_next():
		c = it.next()
		# EOF
		if c is EOFToken:
			yield EOFToken
		# special whitespace handling
		elif c == '\n':
			yield NewlineToken
			# consume indentation on next line
			indentation = consume_while(it, lambda c: c.isspace() and c != '\n')
			if indentation == '':
				yield IndentationToken(0)
			else:
				chars = set(indentation)
				if chars == {' '}:
					yield IndentationToken(len(indentation))
				elif chars == {'\t'}:
					yield IndentationToken(len(indentation) * 8)
				else:
					raise lexer_error("Invalid indentation: %s" % repr(indentation))
		# ignore whitespace
		elif c.isspace():
			continue
		elif c in QUOTE_CHARS:
			yield try_consume_string(c, it)
		# operators (and other punctuation)
		elif c in PUNCTUATION_CHARS:
			op = get_operators(tree, c, it)
			if not op:
				raise lexer_error("Unexpected character %s" % c)
			yield op
		elif c.isalpha() or c == '_':
			# raw string
			if c == 'r' and it.peek() in QUOTE_CHARS:
				q = it.next()
				yield try_consume_string(q, it, raw=True)
			else:
				brwd = c + consume_while(it, lambda c: c.isalnum() or c == '_')
				kwd = Keyword.is_keyword(brwd)
				if kwd:
					yield kwd
				else:
					yield BarewordToken(brwd)
		elif c.isdigit():
			yield consume_number(c, it)
		elif c == '#':
			consume_while(it, lambda c: c != '\n')
		else:
			raise lexer_error("Unexpected character %s" % c)

def consume_exponent(it, base):
	it.next()
	c = it.next()
	if c.isdigit():
		exponent = consume_number(c, it, recursive=False).value
		flt = base * (10 ** exponent)
		c = it.peek()
		if c in ('j', 'J'):
			it.next()
			return ImaginaryToken(b=flt)
		else:
			return FloatToken(flt)
	else:
		raise lexer_error("exponent missing in numeric literal")

def consume_number(c, it, recursive=True):
	digits = c + consume_while(it, lambda c: c.isdigit())
	next = it.peek()
	if next == 'x' and recursive:
		it.next()
		if digits == '0':
			hexdigits = consume_while(it, lambda c: c.isdigit() or c in set('abcdefABCDEF'))
			return IntegerToken(int(hexdigits, 16))
		else:
			raise lexer_error("x in numeric literal must be part of hexadecimal literal")
	elif next in ('j', 'J') and recursive:
		it.next()
		return ImaginaryToken(b=int(digits, 10))
	elif next == '.':
		it.next()
		more_digits = consume_while(it, lambda c: c.isdigit())
		number = float(digits + '.' + more_digits)
		peek = it.next()
		if peek in ('j', 'J'):
			it.next()
			return ImaginaryToken(b=number)
		elif peek in ('e', 'E'):
			return consume_exponent(it, number)
		else:
			return FloatToken(number)
	elif next in ('e', 'E') and recursive:
		return consume_exponent(it, int(digits))
	elif next.isalpha() or next == '_':
		raise lexer_error("invalid character following numberic literal")
	else:
		return IntegerToken(int(digits))


def try_consume_string(q, it, raw=False):
	if it.peek() == q:
		it.next()
		q2 = it.peek()
		if q2 == q:
			it.next()
			return consume_string(it, raw=raw, multiline=True, closing=q, closing_count=3)
		elif q2.isalpha() or q2 == '_':
			raise lexer_error("Expected one or three quotes at beginning of raw string")
		else:
			return StringToken('')
	else:
		return consume_string(it, raw=raw, closing=q)


def consume_string(it, raw=False, multiline=False, closing="'", closing_count=1):
	out = ''
	in_escape = False
	current_closing_count = 0
	while True:
		c = it.next()
		if c is EOFToken:
			raise lexer_error("EOF within string literal: %s" % out)
		if c == closing and not in_escape:
			current_closing_count += 1
			if current_closing_count == closing_count:
				break
			else:
				continue
		else:
			current_closing_count = 0
		if c == '\\' and not in_escape:
			in_escape = True
			# this is needed to reproduce real Python behavior
			# r'a\'' gives a string containing a, \, '
			if raw:
				out += c
			continue
		if c == '\n' and not multiline:
			raise lexer_error("Unexpected newline within string literal")
		if in_escape and raw:
			out += c
			in_escape = False
		elif in_escape:
			if c == 'n':
				out += '\n'
			elif c == 'r':
				out += '\r'
			elif c == 't':
				out += '\t'
			elif c == 'a':
				out += '\a'
			elif c == 'u':
				raise lexer_error("I'm too lazy to provide Unicode support")
			elif c in PUNCTUATION_CHARS:
				out += c
			else:
				raise lexer_error("Unrecognized escape sequence: \\%s" % c)
			in_escape = False
		else:
			out += c

	# reproduce bug in actual Python
	if raw and len(out) > 0 and out[-1] == '\\' and not (len(out) > 1 and out[-2] == '\\'):
		raise lexer_error("Can't have backslash at end of raw string: %s" % out)

	return StringToken(out)

def print_tokens(string):
	for tkn in tokenize(string):
		print tkn, repr(tkn)
