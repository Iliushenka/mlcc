import sys

from Tokens import Tokens
from Token import Token
from Error import error


class Lexer:
    def __init__(self, filename):
        self.filename = filename
        self.source = open(filename, "r", encoding="UTF-8").read()
        self.size = len(self.source)

        self.pos = 0

    def next_token(self):
        while self.peek(0) in (" ", "\n", "\t"):
            self.next()
        start_pos = self.pos
        char = self.peek(0)
        if char.isalpha() or char == "_":
            return self.tokenizeCode(start_pos)
        elif char == "#":
            self.skipComment()
            return self.next_token()
        elif char.isdigit() or char == "." or char == "-":
            return self.tokenizeNumber(start_pos)
        elif char == "`":
            return self.tokenizeVariable(start_pos)
        elif self.peek(0) == "":
            return Token(Tokens.EOF, "EOF", start_pos, self.pos, self.filename)
        else:
            return self.tokenizeSimple(start_pos)

    def skipComment(self):
        char = self.next()
        while char != "\n" and char != "":
            char = self.next()

    def tokenizeVariable(self, start_pos):
        token_value = ""
        char = self.next()
        while char != "`" and char != "":
            token_value += char
            char = self.next()
        self.next()
        token = Token(Tokens.VARIABLE, token_value, start_pos, self.pos, self.filename)
        return token

    def tokenizeNumber(self, start_pos):
        token_value = ""
        char = self.peek(0)
        while char.isdigit() or char == "." or char == "-":
            token_value += char
            char = self.next()
        try:
            token_value = float(token_value)
            token = Token(Tokens.NUMBER, token_value, start_pos, self.pos, self.filename)
            return token
        except ValueError:
            if token_value == "-":
                self.pos -= 1
                return self.tokenizeSimple(start_pos)
            else:
                token = Token(Tokens.NUMBER, token_value, start_pos, self.pos, self.filename)
                error(token)

    def tokenizeSimple(self, start_pos):
        char = self.peek(0)
        next_char = self.next()
        if next_char == "=":
            self.next()
            if char == "-":
                return Token(Tokens.MINUS_ASSIGN, "-=", start_pos, self.pos, self.filename)
            if char == "+":
                return Token(Tokens.PLUS_ASSIGN, "+=", start_pos, self.pos, self.filename)
        else:
            if char == "-":
                return Token(Tokens.MINUS, char, start_pos, self.pos, self.filename)
            elif char == "+":
                return Token(Tokens.PLUS, char, start_pos, self.pos, self.filename)
            elif char == "*":
                return Token(Tokens.STAR, char, start_pos, self.pos, self.filename)
            elif char == "/":
                return Token(Tokens.SLASH, char, start_pos, self.pos, self.filename)
            elif char == "{":
                return Token(Tokens.LBRACKET, char, start_pos, self.pos, self.filename)
            elif char == "}":
                return Token(Tokens.RBRACKET, char, start_pos, self.pos, self.filename)
            elif char == "(":
                return Token(Tokens.LPARENT, char, start_pos, self.pos, self.filename)
            elif char == ")":
                return Token(Tokens.RPARENT, char, start_pos, self.pos, self.filename)
            elif char == "=":
                return Token(Tokens.ASSIGN, char, start_pos, self.pos, self.filename)
        return Token(Tokens.NONE, "Unknown char", start_pos, self.pos, self.filename)

    def tokenizeCode(self, start_pos):
        token_type = ""
        char = self.peek(0)
        while char.isalnum() or char == "_":
            token_type += char
            char = self.next()
        if token_type == "event":
            while self.peek(0) in (" ", "\n", "\t"):
                self.next()
            if self.peek(0) == "<":
                char = self.next()
                token_value = ""
                while char != ">" and char != "":
                    token_value += char
                    char = self.next()
                token = Token(Tokens.EVENT, token_value, start_pos, self.pos, self.filename)
                self.next()
                return token
            else:
                token = Token(Tokens.EVENT, "", start_pos, self.pos, self.filename)
                error(token)
        elif token_type == "func":
            pass
        elif token_type == "cycle":
            pass

    def peek(self, relative_position):
        position = relative_position + self.pos
        if position >= self.size:
            return ""
        return self.source[position]

    def next(self):
        self.pos += 1
        return self.peek(0)