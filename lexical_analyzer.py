import string
from enum import Enum

TOKEN_ALLOWED_SYMBOLS = string.ascii_letters + string.digits + '_'
TOKEN_ALLOWED_FIRST_SYMBOL = string.ascii_letters + '_'
COMMENTS_START_SYMBOL = '#'
TOKENS_ADD_INDENT = {'if', 'elif'}  # TODO: нужно дописать
PROGRAM_KEYWORDS = {'none', 'if', 'elif', 'else', 'foreach', 'print'}  # TODO: нужно дописать
EQUATION_SYMBOLS = {'+', '-', '/', '*'}
IDENTIFIER_SEPARATOR_SYMBOLS = {' ', '\n', '(', ')', '\'', '"', ',', '='} | EQUATION_SYMBOLS
IDENTIFIER_SEPARATOR_SYMBOLS_PARTIAL = IDENTIFIER_SEPARATOR_SYMBOLS - {' ', '\n'}


class TokenConstructions(Enum):
    NEW_IDENTIFIER = 1
    IF_DECLARATION_START = 2
    ELIF_DECLARATION_START = 3
    FUNCTION_CALL_START = 4
    STRING_1 = 5
    STRING_2 = 6
    EQUATION = 7
    END_OF_CONSTRUCTION = 8
    EQUATION_NEW_IDENTIFIER = 9
    EQUATION_NEW_OPERATOR = 10
    FUNCTION_CALL_NEW_ARGUMENT = 11
    NEW_CONSTANT_INTEGER = 12
    NEW_CONSTANT_FLOAT = 13


class SynthaxError(Exception):
    error_text = None
    line_number = None
    symbol_number = None

    def __init__(self, error_text, line_number, current_character_number):
        self.error_text = error_text
        self.line_number = line_number
        self.current_character_number = current_character_number

    def __str__(self):
        return f'строка {self.line_number} символ {self.current_character_number}: Синтаксическая ошибка: {self.error_text}'


class LexicalAnalyzer:
    program_filename = None
    current_state = None
    previous_state = None
    previous_identifier = None
    current_identifier = None
    equation_stack = []
    state_stack = []
    identifier_table = dict()

    def set_state(self, new_state):
        self.previous_state = self.current_state
        self.current_state = new_state
        self.state_stack.append(new_state)

    def set_identifier(self, new_name):
        self.previous_identifier = self.current_identifier
        self.current_identifier = new_name

    def __init__(self, program_filename):
        self.program_filename = program_filename
        self.current_state = None
        self.state_stack = []

    def check_identifier_not_keyword(self, identifier, line_number, current_character_number):
        if identifier in PROGRAM_KEYWORDS:
            raise SynthaxError(f"недопустимый идентификатор {identifier}", line_number, current_character_number)

    def check_identifier_declared(self, identifier, line_number, current_character_number):
        if identifier not in self.identifier_table.keys():
            raise SynthaxError(f"недопустимый необъявленный идентификатор {identifier}", line_number,
                               current_character_number)

    def analyze(self):
        with (open(self.program_filename, 'r') as f):
            lines = f.readlines()

            current_indent = 0
            open_indent_blocks = []
            line_number = 0
            current_character_number = 0

            for line in lines:
                current_character_number = 1
                line_number += 1
                # очистить строку от комментариев
                line_without_comments = line.split(COMMENTS_START_SYMBOL)[0]
                # если вся строка это комментарий - пропустить строку
                if line.startswith(COMMENTS_START_SYMBOL):
                    continue

                # обработка строки посимвольно
                # variable for storing strings
                current_string = ''
                current_identifier = ''

                for c in line_without_comments:
                    if current_indent and current_character_number < current_indent:
                        # if c == 'e':
                        #     current_indent -= 2 # убираем отступ, чтобы корректно собрать токен
                        #     current_identifier += c
                        #     self.set_state(TokenConstructions.ELIF_DECLARATION_START)
                        # else:
                        pass     # TODO: обработка
                    else:
                        # проверка первого символа
                        if c not in string.ascii_letters and current_character_number - 1 == current_indent:
                            raise SynthaxError("недопустимый символ", line_number, current_character_number)
                        # сборка токена
                        if self.current_state == TokenConstructions.END_OF_CONSTRUCTION:
                            if c == '\n' or len(line_without_comments) == current_character_number:
                                pass
                            else:
                                raise SynthaxError("недопустимый символ", line_number, current_character_number)

                        if self.current_state == TokenConstructions.STRING_1 and c != '\''\
                                or self.current_state == TokenConstructions.STRING_2 and c != '"':
                            current_string += c
                            current_identifier += c
                        elif c not in IDENTIFIER_SEPARATOR_SYMBOLS:
                            current_identifier += c

                        #print(f'current token: {repr(current_identifier)}')
                        # if current_identifier in IDENTIFIER_SEPARATOR_SYMBOLS:
                        #     current_identifier = ''


                        # переключение автомата на другое состояние (матрица переходов)
                        if c == '(' and self.current_state == TokenConstructions.NEW_IDENTIFIER:
                            self.set_state(TokenConstructions.FUNCTION_CALL_START)
                            print(f'function call: "{self.previous_identifier}"')
                        elif c == ')' and self.current_state in (TokenConstructions.FUNCTION_CALL_NEW_ARGUMENT,
                                                                 TokenConstructions.FUNCTION_CALL_START):
                            self.set_state(TokenConstructions.END_OF_CONSTRUCTION)
                        elif c == '"' and self.current_state == TokenConstructions.EQUATION:
                            self.set_state(TokenConstructions.STRING_2)
                        elif c == '"' and self.current_state == TokenConstructions.STRING_2:
                            print(f'string: "{current_string}"')
                            if self.previous_state == TokenConstructions.EQUATION:
                                self.equation_stack.append(repr(current_string))
                            self.set_state(TokenConstructions.END_OF_CONSTRUCTION)
                            current_string = ''
                        elif c == '\'' and self.current_state == TokenConstructions.EQUATION:
                            self.set_state(TokenConstructions.STRING_1)
                        elif c == '\'' and self.current_state == TokenConstructions.STRING_1:
                            print(f'string: "{current_string}"')
                            if self.previous_state == TokenConstructions.EQUATION:
                                self.equation_stack.append(repr(current_string))
                            self.set_state(TokenConstructions.END_OF_CONSTRUCTION)
                            current_string = ''
                        elif c == '=' and self.current_state == TokenConstructions.NEW_IDENTIFIER:
                            self.set_identifier(current_identifier)
                            self.set_state(TokenConstructions.EQUATION)
                            self.equation_stack.append(self.current_identifier)
                            self.equation_stack.append(c)
                            current_identifier = ''
                        elif c == '=' and self.current_state == TokenConstructions.EQUATION:
                            raise SynthaxError(f"недопустимый токен {self.previous_identifier}", line_number, current_character_number)
                        elif c == '+' and self.current_state == TokenConstructions.EQUATION_NEW_IDENTIFIER:
                            self.set_identifier(current_identifier)
                            self.check_identifier_declared(current_identifier, line_number, current_character_number)
                            self.equation_stack.append(self.current_identifier)
                            self.equation_stack.append(c)
                            self.set_state(TokenConstructions.EQUATION_NEW_OPERATOR)
                            current_identifier = ''
                        elif c == '-' and self.current_state == TokenConstructions.EQUATION_NEW_IDENTIFIER:
                            self.set_identifier(current_identifier)
                            self.check_identifier_declared(current_identifier, line_number, current_character_number)
                            self.equation_stack.append(self.current_identifier)
                            self.equation_stack.append(c)
                            self.set_state(TokenConstructions.EQUATION_NEW_OPERATOR)
                            current_identifier = ''
                        elif c == '*' and self.current_state == TokenConstructions.EQUATION_NEW_IDENTIFIER:
                            self.set_identifier(current_identifier)
                            self.check_identifier_declared(current_identifier, line_number, current_character_number)
                            self.equation_stack.append(self.current_identifier)
                            self.equation_stack.append(c)
                            self.set_state(TokenConstructions.EQUATION_NEW_OPERATOR)
                            current_identifier = ''
                            self.set_state(TokenConstructions.EQUATION_NEW_OPERATOR)
                        elif c == '/' and self.current_state == TokenConstructions.EQUATION_NEW_IDENTIFIER:
                            self.set_identifier(current_identifier)
                            self.check_identifier_declared(current_identifier, line_number, current_character_number)
                            self.equation_stack.append(self.current_identifier)
                            self.equation_stack.append(c)
                            self.set_state(TokenConstructions.EQUATION_NEW_OPERATOR)
                            current_identifier = ''
                        elif c in TOKEN_ALLOWED_SYMBOLS and self.current_state in (TokenConstructions.NEW_IDENTIFIER,
                                                                                   TokenConstructions.EQUATION_NEW_IDENTIFIER,
                                                                                   TokenConstructions.FUNCTION_CALL_NEW_ARGUMENT):
                            pass
                        elif c in TOKEN_ALLOWED_FIRST_SYMBOL and self.current_state in {TokenConstructions.EQUATION_NEW_OPERATOR,
                                                                                   TokenConstructions.EQUATION}:
                            self.set_state(TokenConstructions.EQUATION_NEW_IDENTIFIER)
                        elif self.current_state is None and c in TOKEN_ALLOWED_FIRST_SYMBOL:
                            self.set_state(TokenConstructions.NEW_IDENTIFIER)
                        elif c in string.digits and self.current_state == TokenConstructions.EQUATION:
                            self.set_state(TokenConstructions.NEW_CONSTANT_INTEGER)
                        elif c in string.digits and self.current_state == TokenConstructions.NEW_CONSTANT_INTEGER:
                            pass
                        elif c != '\'' and self.current_state == TokenConstructions.STRING_1:
                            pass
                        elif c != '"' and self.current_state == TokenConstructions.STRING_2:
                            pass
                        elif c in ' ':
                            if self.current_state in {TokenConstructions.NEW_CONSTANT_INTEGER,
                                                      TokenConstructions.NEW_CONSTANT_FLOAT}:
                                self.set_state(TokenConstructions.END_OF_CONSTRUCTION)
                            else:
                                pass
                        elif c == '.' and self.current_state == TokenConstructions.NEW_CONSTANT_INTEGER:
                            self.set_state(TokenConstructions.NEW_CONSTANT_FLOAT)
                        elif c in string.digits and self.current_state == TokenConstructions.NEW_CONSTANT_FLOAT:
                            pass
                        elif c in string.digits and self.current_state == TokenConstructions.NEW_CONSTANT_FLOAT:
                            pass
                        elif c == '\n':
                            pass  # обработка ниже
                        else:
                            raise SynthaxError(f"недопустимый символ", line_number, current_character_number)

                        # обработка последнего символа должна быть вынесена в параллельный блок
                        if c == '\n' or len(line_without_comments) == current_character_number:
                            if self.current_state in {TokenConstructions.NEW_IDENTIFIER,
                                                      TokenConstructions.EQUATION_NEW_IDENTIFIER,
                                                      TokenConstructions.NEW_CONSTANT_INTEGER,
                                                      TokenConstructions.NEW_CONSTANT_FLOAT}:
                                if self.current_state == TokenConstructions.EQUATION_NEW_IDENTIFIER:
                                    self.check_identifier_declared(current_identifier, line_number, current_character_number)
                                self.equation_stack.append(current_identifier)
                                # self.set_identifier(current_identifier)
                            # elif self.current_state == TokenConstructions.NEW_IDENTIFIER:
                            #     if self.previous_state == TokenConstructions.NEW_IDENTIFIER:
                            #         raise SynthaxError(f"недопустимый токен {current_identifier}", line_number, current_character_number)
                            # elif self.current_state == TokenConstructions.EQUATION_NEW_IDENTIFIER:
                            #     if c not in EQUATION_SYMBOLS:
                            #         raise SynthaxError("недопустимый символ", line_number, current_character_number)
                            # elif self.current_state == TokenConstructions.IF_DECLARATION_START:
                            #     self.check_identifier_not_keyword(self.current_identifier, line_number, current_character_number)
                            # elif self.current_state == TokenConstructions.FUNCTION_CALL_START:
                            #     self.check_identifier_not_keyword(self.current_identifier, line_number, current_character_number)
                            if self.current_state in {TokenConstructions.EQUATION_NEW_IDENTIFIER,
                                                      TokenConstructions.NEW_CONSTANT_INTEGER,
                                                      TokenConstructions.NEW_CONSTANT_FLOAT,
                                                      TokenConstructions.END_OF_CONSTRUCTION}  \
                                and len(self.equation_stack):
                                # print(f'equation stack: {" ".join(self.equation_stack)}')
                                self.identifier_table[self.equation_stack[0]] = self.equation_stack[2:]
                            self.set_state(None)

                            current_identifier = ''
                            self.equation_stack.clear()

                    current_character_number += 1

            print("------- identifier table -------")
            for k, v in self.identifier_table.items():
                print(f"{k} = {v}")
            print("------- ---------------- -------")
