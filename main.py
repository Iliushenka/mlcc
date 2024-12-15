from Lexer import Lexer
from Parser import Parser

lexer = Lexer("code.ml")
parser = Parser(lexer)
parser.parse()