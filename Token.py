class Token:
    def __init__(self, type, value, start_pos, end_pos, filename):
        self.type = type
        self.value = value

        self.start_pos = start_pos
        self.end_pos = end_pos
        self.filename = filename

    def set_error(self, start_pos, end_pos, filename):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.filename = filename

    def match(self, *type):
        if self.type in type:
            return True
        return False

    def __str__(self):
        return f"Token({self.type}, {self.value})"

    def __repr__(self):
        return self.__str__()
