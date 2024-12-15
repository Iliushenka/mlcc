import sys


def error(token, output=""):
    data = open(token.filename, "r", encoding="UTF-8").read()[token.start_pos:token.end_pos]
    sys.exit(f"{output}\nНайдено {token.value}\nОшибка файла {token.filename}: {data}")
