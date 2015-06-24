import sys

import lexer
import zypy_parser

if __name__ == '__main__':
	cmd = sys.argv[1]
	input = ' '.join(sys.argv[2:])
	if cmd == 'lex':
		lexer.print_tokens(input)
	elif cmd == 'parse':
		print zypy_parser.parse(input)
	elif cmd == 'parsefile':
		file = open(sys.argv[2]).read()
		print zypy_parser.parse(file)
	elif cmd == 'lexfile':
		file = open(sys.argv[2]).read()
		print lexer.print_tokens(file)
