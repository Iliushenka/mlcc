import sys
import json

from Tokens import Tokens
from Token import Token
from Error import error


class Id:
    EVENT: str = "DIAMOND_BLOCK"
    FUNC: str = "LAPIS_BLOCK"
    CYCLE: str = "EMERALD_BLOCK"
    VARIABLE: str = "IRON_BLOCK"


path = {"join": (0, 1),
        "leave": (0, 2),
        "multiply": (1, 1),
        "division": (1, 2),
        "plus": (1, 3),
        "minus": (1, 4),
        "assign": (1, 5)}


def get_path(value):
    if value not in path.keys():
        error(token, "Данного действия, события и тому подобного нет в компиляторе")
    else:
        return path[value]


class Parser:
    def __init__(self, lexer):
        self.lexer = lexer

        self.lines = list()
        self.line = list()
        self.token = self.next()

        self.filename = self.lexer.filename.replace(".ml", "")
        self.index = 0
        self.unique = f"{self.filename}_{self.index}"

    def parse(self):
        while self.token.type != Tokens.EOF:
            self.statement()
            self.lines.append(self.line)
            self.line = list()
            self.token = self.next()
        if '.ml' in self.lexer.filename:
            filename = self.lexer.filename.replace(".ml", ".json")
            filename = f"./output/{filename}"
            with open(filename, "w") as file:
                json.dump(self.lines, file, indent=3)
        else:
            sys.exit(f"Неправльный формат файла для {self.lexer.filename} требуется .ml")

    def statement(self):
        if self.token.match(Tokens.EVENT, Tokens.FUNC, Tokens.CYCLE):
            if self.token.match(Tokens.EVENT):
                event = self.token
                self.eat(Tokens.EVENT)
                self.eat(Tokens.LBRACKET)
                self.add_block(Id.EVENT, path_block=get_path(event.value))
                while not self.token.match(Tokens.RBRACKET):
                    self.statement()
                self.eat(Tokens.RBRACKET)
            elif self.token.match(Tokens.FUNC):
                pass # В будущем
            elif self.token.match(Tokens.CYCLE):
                pass # В будущем
        elif self.token.match(Tokens.VARIABLE):
            if self.token.match(Tokens.VARIABLE):
                self.expression()

    def expression(self):
        token = self.token
        self.eat(self.token.type)
        if token.type in (Tokens.VARIABLE, ):
            if self.token.match(Tokens.ASSIGN):
                self.eat(Tokens.ASSIGN)
                self.additive()
                self.line[-1]["values"][0] = token.value

    def additive(self):
        expr = self.multiplicative()
        equal_type, equal_value = [Tokens.VARIABLE], [self.unique]
        changes = 0
        if expr.match(Tokens.STRING) is False:
            if self.token.match(Tokens.PLUS):
                changes += 1
                types, values = equal_type, equal_value
                types += [expr.type]
                values += [expr.value]
                while self.token.match(Tokens.PLUS):
                    self.eat(Tokens.PLUS)
                    expr = self.multiplicative()
                    types += [expr.type]
                    values += [expr.value]
                self.add_block(Id.VARIABLE, get_path("plus"), types, values)
                equal_type, equal_value = [Tokens.VARIABLE], [self.unique]
                expr = Token(equal_type[0], equal_value[0], -1, -1, self.filename)
            if self.token.match(Tokens.MINUS):
                changes += 1
                types, values = equal_type, equal_value
                types += [expr.type]
                values += [expr.value]
                while self.token.match(Tokens.MINUS):
                    self.eat(Tokens.MINUS)
                    expr = self.multiplicative()
                    types += [expr.type]
                    values += [expr.value]
                self.add_block(Id.VARIABLE, get_path("minus"), types, values)
                equal_type, equal_value = [Tokens.VARIABLE], [self.unique]
                expr = Token(equal_type[0], equal_value[0], -1, -1, self.filename)
        else:
            if self.token.match(Tokens.STAR, Tokens.SLASH, Tokens.PLUS, Tokens.MINUS):
                error(self.token, "Нет операций сложения деления и так далее с типом String")
        if changes == 0 and expr.type in (Tokens.NUMBER, Tokens.VARIABLE, Tokens.STRING):
            equal_type, equal_value = equal_type + [expr.type], equal_value + [expr.value]
            self.add_block(Id.VARIABLE, get_path("assign"), equal_type, equal_value)
        else:
            self.next_unique()
        return expr

    def multiplicative(self):
        expr = self.primary()
        if expr.match(Tokens.STRING) is False:
            equal_type, equal_value = [Tokens.VARIABLE], [self.unique]
            if self.token.match(Tokens.STAR):
                types, values = equal_type, equal_value
                types += [expr.type]
                values += [expr.value]
                while self.token.match(Tokens.STAR):
                    self.eat(Tokens.STAR)
                    expr = self.primary()
                    types += [expr.type]
                    values += [expr.value]
                self.add_block(Id.VARIABLE, get_path("multiply"), types, values)
                equal_type, equal_value = [Tokens.VARIABLE], [self.unique]
                expr = Token(equal_type[0], equal_value[0], -1, -1, self.filename)
            if self.token.match(Tokens.SLASH):
                types, values = equal_type, equal_value
                types += [expr.type]
                values += [expr.value]
                while self.token.match(Tokens.SLASH):
                    self.eat(Tokens.SLASH)
                    expr = self.primary()
                    types += [expr.type]
                    values += [expr.value]
                self.add_block(Id.VARIABLE, get_path("division"), types, values)
                equal_type, equal_value = [Tokens.VARIABLE], [self.unique]
                expr = Token(equal_type[0], equal_value[0], -1, -1, self.filename)
        return expr

    def primary(self):
        token = self.token
        if token.match(Tokens.VARIABLE, Tokens.NUMBER, Tokens.STRING):
            self.next()
            return token
        elif token.match(Tokens.LPARENT):
            self.eat(Tokens.LPARENT)
            while not self.token.match(Tokens.RPARENT):
                token = self.additive()
            self.eat(Tokens.RPARENT)
            return Token(token.type, token.value, -1, -1, self.filename)


    def eat(self, type):
        if self.token.match(type) is True:
            self.token = self.next()
        else:
            error(self.token, "Ожидался другой тип токена")

    def next(self):
        self.token = self.lexer.next_token()
        return self.token

    def add_block(self, id_block, path_block=None, types=None, values=None):
        block = {"block": id_block,
                 "path": path_block,
                 "types": types,
                 "values": values}
        self.line += [block]

    def next_unique(self):
        self.index += 1
        self.unique = f"{self.filename}_{self.index}"
