'''Ridiculously incomplete'''

from tokens import *
import lexer

def lex_into_list(str):
	return [token for token in lexer.tokenize(str)]

def assert_lexes(str, lst):
	lst.append(EOFToken)
	lexed = lex_into_list(str)
	assert lexed == lst, "%s != %s" % (lexed, lst)

def test_lines():
	assert_lexes("import a", [ImportKeyword, BarewordToken("a")])

	assert_lexes("while True:", [WhileKeyword, BarewordToken("True"), ColonOperator])

	assert_lexes("'hello'", [StringToken("hello")])

	assert_lexes("a, _ = [1, 2]", [BarewordToken("a"), CommaOperator, UnderscoreKeyword, AssignmentOperator, OpeningSquareBracketOperator, IntegerToken(1), CommaOperator, IntegerToken(2), ClosingSquareBracketOperator])
