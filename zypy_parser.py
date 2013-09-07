#!/opt/local/bin/python3.3

from lexer import *
from tokens import *
from peeking_iterator import peeking_iterator


class parse_error(Exception):
	pass

def ensure_newline(it, preceding=None, next=None):
	if next is None:
		next = it.next()
	if next is not NewlineToken and next is not EOFToken:
		print next
		msg = "Expected newline"
		if preceding:
			msg += " following %s" % preceding
		raise parse_error(msg)

def ensure_follows(it, token, msg=None):
	next = it.next()
	if next is not token:
		raise parse_error("%s: expected %s, got %s" % (msg, token, next))

def parse_expression(it):
	# TODO I suppose we need operators
	return parse_base_expression(it)

def parse_base_expression(it):
	next = it.next()
	if isinstance(next, Literal):
		return next
	elif isinstance(next, BarewordToken):
		return Variable(next.value)
	elif next is OpeningParenOperator:
		# parenthesized expression...
		next = it.peek()
		if next is ClosingParenOperator:
			return TupleLiteral([])
		expression = parse_expression(it)
		next = it.next()
		if next is ClosingParenOperator:
			return expression
		elif next is CommaOperator:
			tpl = TupleLiteral([expression])
			while True:
				tpl.value.append(parse_expression(it))
				next = it.next()
				if next is ClosingParenOperator:
					return tpl
				elif next is CommaOperator:
					continue
				else:
					raise parse_error("Unexpected token in tuple literal: %s" % next)
		elif next is ForKeyword:
			comprehend = parse_comprehension(it, closing=ClosingParenOperator, name="generator")
			return GeneratorExpression(expression, comprehend)
		else:
			raise parse_error("Unexpected token following opening parenthesis: %s" % next)
	elif next is OpeningCurlyBracketOperator:
		# dicts, sets
		pass
	elif next is OpeningSquareBracketOperator:
		# lists
		pass
	else:
		raise parse_error("Unexpected token in expression context: %s" % next)

def parse_comprehension(it, closing=None, name="comprehension"):
	'''Parse a generator expression, list comprehension, etc.'''
	clauses = []
	it.push_back(ForKeyword)

	while True:
		next = it.next()
		if next is closing:
			break
		elif next is ForKeyword:
			variable = parse_expression(it)
			ensure_follows(it, InKeyword, msg=name)
			collection = parse_expression(it)
			clauses.append(ComprehensionClause(ForKeyword, variable=variable, collection=collection))
		elif next is IfKeyword:
			condition = parse_expression(it)
			clauses.append(ComprehensionClause(IfKeyword, condition=condition))
		else:
			raise parse_error("Unexpected %s within %s" % (next, name))

	return clauses

def parse_lvalue(it):
	'''Parse an lvalue (e.g., "a, _", "a, (b, c)")'''
	# This is also what CPython does. A later stage in the implementation
	# will have to confirm it's a real lvalue.
	return parse_expression(it)

def parse_colon_and_statement_list(it, level=0):
	next = it.next()
	if next is not ColonOperator:
		raise parse_error("Expected colon, got %s" % next)

	statements = []
	next = it.peek()
	if next is not NewlineToken:
		# they put it on one line, grumble
		while True:
			append_parse_statement(statements, it, one_line=True)
			next = it.peek()
			if next is SemicolonOperator:
				it.next()
			elif next is NewlineToken:
				break
			else:
				raise parse_error("Expected newline or semicolon, got %s" % next)
	else:
		it.next()
		next = it.next()
		if not isinstance(next, IndentationToken):
			raise parse_error("Expected an indented block, got %s" % next)
		elif next.value <= level:
			raise parse_error("Continuation line must be indented at least as much as starting line")

		indented_level = next.value
		append_parse_statement(statements, it, level=indented_level)

		while True:
			next = it.peek()
			print locals()
			if next is EOFToken:
				break
			elif next is SemicolonOperator:
				while True:
					it.next()
					append_parse_statement(statements, it, one_line=True)
					next = it.peek()
					if next is not SemicolonOperator:
						break
			if next is NewlineToken:
				# TODO handle blank lines
				it.next()
				# check indentation; this must be > 0
				indentation = it.peek()
				if indentation is EOFToken:
					break
				elif indentation is NewlineToken:
					continue
				elif not isinstance(indentation, IndentationToken):
					if level == 0:
						break
					else:
						raise parse_error("Expected an indented block, got %s" % indentation)
				elif indentation.value <= level:
					break
				elif indentation.value < indented_level:
					raise parse_error("Statement in indented block indented less than previous statement")
				elif indentation.value > indented_level:
					raise parse_error("Statement in indented block indented more than previous statement")
				else:
					it.next()
			else:
				raise parse_error(str(next))
			append_parse_statement(statements, it, level=indented_level)

	return statements

def parse_closing_else_block(it, level=0):
	if level > 0:
		indentation = it.next()
		assert isinstance(indentation, IndentationToken), "expected indentation: %s" % indentation
		assert indentation.value <= level

	if (level == 0 or indentation.value == level) and it.peek() is ElseKeyword:
		it.next()
		return parse_colon_and_statement_list(it, level=level)
	else:
		it.push_back(indentation)
		it.push_back(NewlineToken)
		return None

def parse_imported_module_name(it):
	first = it.next()
	if not isinstance(first, BarewordToken):
		raise parse_error("Expected module name, got %s" % first)

	next = it.peek()
	if next is DotOperator:
		# more module
		it.next()
		return first.value + '.' + parse_imported_module_name(it)
	else:
		return first.value

def parse_import_statement(it, level=0):
	out = ImportsList()
	while True:
		module_name = parse_imported_module_name(it)
		next = it.peek()
		if next is AsKeyword:
			it.next()
			name = it.next()
			if not isinstance(name, BarewordToken):
				raise parse_error("Expected module name, got %s" % first)
			out.value.append(ImportStatement(module_name, as_name=name.value))
			next = it.peek()
		else:
			out.value.append(ImportStatement(module_name))
		if next is CommaOperator:
			it.next()
			continue
		return out

def parse_from_statement(it, level=0):
	def count_the_dots(it):
		count = 0
		while True:
			next = it.peek()
			if next is DotOperator:
				count += 1
				it.next()
			else:
				return count

	level = count_the_dots(it) - 1

	next = it.peek()
	if next is ImportKeyword:
		if level == -1:
			raise parse_error("Invalid relative import statement")
		# TODO: how do we handle this in the statement object? How does this kind of import even work?
		module_name = None
		it.next()
	else:
		module_name = parse_imported_module_name(it)
		next = it.next()
		if next is not ImportKeyword:
			raise parse_error("Expected 'import' in relative import statement")

	next = it.peek()
	needs_closing_paren = False
	if next is OpeningParenOperator:
		needs_closing_paren = True
		it.next()

	froms = []
	while True:
		name = it.next()
		if not isinstance(name, BarewordToken):
			raise parse_error("Expected bareword in relative import")
		next = it.peek()
		if next is AsKeyword:
			it.next()
			as_name = it.next()
			if not isinstance(as_name, BarewordToken):
				raise parse_error("Expected bareword in relative import")

			froms.append((name.value, as_name.value))
			next = it.peek()
		else:
			froms.append((name.value, None))

		if next is CommaOperator:
			continue
		if next is ClosingParenOperator:
			if needs_closing_paren:
				needs_closing_paren = False
				it.next()
			else:
				raise parse_error("Unexpected closing parenthesis in relative import statement")
		if needs_closing_paren:
			raise parse_error("Expected closing parenthesis in relative import statement")
		# we're done
		stmt = ImportStatement(module_name, level=level, from_list=froms)
		return ImportsList([stmt])

def parse_for_statement(it, level=0):
	lvalue = parse_lvalue(it)
	ensure_follows(it, InKeyword, "for loop")
	collection = parse_expression(it)
	body = parse_colon_and_statement_list(it, level=level)
	else_block = parse_closing_else_block(it, level=level)
	return ForStatement(lvalue, collection, body, else_block)

def parse_if_statement(it, level=0):
	pass

def parse_with_statement(it, level=0):
	pass

def parse_while_statement(it, level=0):
	condition = parse_expression(it)
	statements = parse_colon_and_statement_list(it, level=level)
	return WhileStatement(condition, statements)

def parse_class_statement(it, level=0):
	pass

def parse_def_statement(it, level=0):
	pass

def parse_try_statement(it, level=0):
	pass

def parse_print_statement(it, level=0):
	pass

def parse_exec_statement(it, level=0):
	pass

def parse_raise_statement(it, level=0):
	pass

def parse_break_statement(it, level=0):
	return BreakStatement

def parse_continue_statement(it, level=0):
	return ContinueStatement

def parse_return_statement(it, level=0):
	returned = parse_expression(it)
	return ReturnStatement(returned)

# these should not consume the following newline
one_line_keyworded_statements = {
	ImportKeyword: parse_import_statement,
	PrintKeyword: parse_print_statement,
	ExecKeyword: parse_exec_statement,
	RaiseKeyword: parse_raise_statement,
	BreakKeyword: parse_break_statement,
	ContinueKeyword: parse_continue_statement,
	ReturnKeyword: parse_return_statement,
	FromKeyword: parse_from_statement,
}

keyworded_statements = {
	ForKeyword: parse_for_statement,
	IfKeyword: parse_if_statement,
	WithKeyword: parse_with_statement,
	WhileKeyword: parse_while_statement,
	ClassKeyword: parse_class_statement,
	DefKeyword: parse_def_statement,
	TryKeyword: parse_try_statement,
}
multiline_keywords = set(keyworded_statements)
keyworded_statements.update(one_line_keyworded_statements)

def parse_statement(it, level=0, one_line=False):
	token = it.peek()
	statement_dict = one_line_keyworded_statements if one_line else keyworded_statements
	if token in statement_dict:
		it.next()
		statement = statement_dict[token](it, level=level)
		if token in multiline_keywords:
			# these will consume the newline
			it.push_back(NewlineToken)
			return statement
		next = it.peek()
		if next in (NewlineToken, SemicolonOperator, EOFToken):
			return statement
		else:
			raise parse_error("Expected newline or semicolon following statement, got %s" % next)
	elif token is NewlineToken:
		it.next()
		return None
	else:
		# assignment, or just an expression
		# ???
		print token, repr(token)
		raise NotImplementedError()

def append_parse_statement(list, it, **kwargs):
	stmt = parse_statement(it, **kwargs)
	if stmt is not None:
		list.append(stmt)

def parse_program(it):
	# TODO: detect encoding. Anything else weird in global scope?
	out = StatementList()
	while it.peek() not in (EOFToken, None):
		append_parse_statement(out.value, it)

	return out

def parse(str):
	tokenizer = tokenize(str)
	pi = peeking_iterator(tokenizer)
	program = parse_program(pi)
	return program

