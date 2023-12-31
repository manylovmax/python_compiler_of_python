import string
from enum import Enum

TOKEN_ALLOWED_SYMBOLS = string.ascii_letters + string.digits + '_'
TOKEN_ALLOWED_FIRST_SYMBOL = string.ascii_letters + '_'
COMMENTS_START_SYMBOL = '#'
TOKENS_ADD_INDENT = {'if', 'elif'}  # TODO: нужно дописать
LOGICAL_VALUES = {'True', 'False'}
PROGRAM_KEYWORDS = {'None', 'if', 'elif', 'else', 'for', 'print', 'pass', 'not'} | LOGICAL_VALUES  # TODO: нужно дописать
EQUATION_SYMBOLS = {'+', '-', '/', '*'}
IDENTIFIER_SEPARATOR_SYMBOLS = {' ', '\n', '(', ')', '\'', '"', ',', '=', ':'} | EQUATION_SYMBOLS
IDENTIFIER_SEPARATOR_SYMBOLS_PARTIAL = IDENTIFIER_SEPARATOR_SYMBOLS - {' ', '\n'}
INDENTATION_NUMBER_OF_WHITESPACES = 4


class TokenConstructions(Enum):
    NEW_IDENTIFIER = 1
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
    END_OF_IDENTIFIER = 14
    IF_DECLARATION_START = 2
    IF_DECLARATION_EXPRESSION_IDENTIFIER = 15
    IF_DECLARATION_EXPRESSION_IDENTIFIER_END = 16
    IF_DECLARATION_INSTRUCTIONS = 17
    IF_DECLARATION_EXPRESSION = 23
    ELSE_DECLARATION = 18
    ELIF_DECLARATION_START = 3
    ELIF_DECLARATION_EXPRESSION_IDENTIFIER = 19
    ELIF_DECLARATION_EXPRESSION_IDENTIFIER_END = 20
    ELIF_DECLARATION_INSTRUCTIONS = 21
    ELIF_DECLARATION_EXPRESSION = 22
    ELIF_DECLARATION_EXPRESSION_NOT_OPERATOR = 23


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
    last_identifier = None
    equation_stack = []
    state_stack = []
    identifier_table = dict()
    is_logical_expression = False
    is_indent_obliged = False

    def set_state(self, new_state):
        self.previous_state = self.current_state
        self.current_state = new_state
        self.state_stack.append(new_state)

    def set_identifier(self, new_name):
        self.previous_identifier = self.last_identifier
        self.last_identifier = new_name

    def __init__(self, program_filename):
        self.program_filename = program_filename
        self.current_state = None
        self.state_stack = []

    def check_identifier_not_keyword(self, identifier, line_number, current_character_number):
        if identifier in PROGRAM_KEYWORDS:
            raise SynthaxError(f"недопустимый идентификатор {identifier}", line_number, current_character_number)

    def check_identifier_declared(self, identifier, line_number, current_character_number):
        if identifier not in self.identifier_table.keys() and identifier not in LOGICAL_VALUES:
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
                    # проверка на правильность расположения отступов (начала строки)
                    if current_indent and current_character_number <= current_indent * INDENTATION_NUMBER_OF_WHITESPACES:
                        if c not in {' ', '\n'} and self.is_indent_obliged:
                            raise SynthaxError("недопустимый символ", line_number, current_character_number)
                        elif c not in {' ', '\n', 'e'}:
                            if current_character_number < (current_indent - 1) * INDENTATION_NUMBER_OF_WHITESPACES:
                                raise SynthaxError("недопустимый символ", line_number, current_character_number)
                            else:
                                current_indent -= 1
                        else:
                            if c == 'e':
                                self.set_state(TokenConstructions.ELIF_DECLARATION_START)
                                current_indent -= 1
                                current_identifier += c

                            current_character_number += 1
                            continue

                    # проверка первого символа
                    if c not in TOKEN_ALLOWED_FIRST_SYMBOL \
                            and current_character_number == current_indent * INDENTATION_NUMBER_OF_WHITESPACES:
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
                    elif c == '=' and self.current_state in {TokenConstructions.NEW_IDENTIFIER,
                                                             TokenConstructions.END_OF_IDENTIFIER}:
                        if current_identifier:
                            self.set_identifier(current_identifier)
                        self.check_identifier_not_keyword(self.last_identifier, line_number, current_character_number)
                        self.set_state(TokenConstructions.EQUATION)
                        self.equation_stack.append(self.last_identifier)
                        self.equation_stack.append(c)
                        current_identifier = ''
                    elif c == '=' and self.current_state == TokenConstructions.EQUATION:
                        raise SynthaxError(f"недопустимый токен {c}", line_number, current_character_number)
                    elif c == '+' and self.current_state == TokenConstructions.EQUATION_NEW_IDENTIFIER:
                        if current_identifier:
                            self.set_identifier(current_identifier)
                        if current_identifier in LOGICAL_VALUES:
                            raise SynthaxError(f"недопустимый токен {current_identifier}", line_number, current_character_number)
                        self.check_identifier_declared(current_identifier, line_number, current_character_number)
                        self.equation_stack.append(current_identifier)
                        self.equation_stack.append(c)
                        self.set_state(TokenConstructions.EQUATION_NEW_OPERATOR)
                        current_identifier = ''
                    elif c == '-' and self.current_state == TokenConstructions.EQUATION_NEW_IDENTIFIER:
                        if current_identifier:
                            self.set_identifier(current_identifier)
                        if current_identifier in LOGICAL_VALUES:
                            raise SynthaxError(f"недопустимый токен {current_identifier}", line_number, current_character_number)
                        self.check_identifier_declared(current_identifier, line_number, current_character_number)
                        self.equation_stack.append(current_identifier)
                        self.equation_stack.append(c)
                        self.set_state(TokenConstructions.EQUATION_NEW_OPERATOR)
                        current_identifier = ''
                    elif c == '*' and self.current_state == TokenConstructions.EQUATION_NEW_IDENTIFIER:
                        if current_identifier:
                            self.set_identifier(current_identifier)
                        if current_identifier in LOGICAL_VALUES:
                            raise SynthaxError(f"недопустимый токен {current_identifier}", line_number, current_character_number)
                        self.check_identifier_declared(current_identifier, line_number, current_character_number)
                        self.equation_stack.append(current_identifier)
                        self.equation_stack.append(c)
                        self.set_state(TokenConstructions.EQUATION_NEW_OPERATOR)
                        current_identifier = ''
                        self.set_state(TokenConstructions.EQUATION_NEW_OPERATOR)
                    elif c == '/' and self.current_state == TokenConstructions.EQUATION_NEW_IDENTIFIER:
                        if current_identifier:
                            self.set_identifier(current_identifier)
                        if current_identifier in LOGICAL_VALUES:
                            raise SynthaxError(f"недопустимый токен {current_identifier}", line_number, current_character_number)
                        self.check_identifier_declared(current_identifier, line_number, current_character_number)
                        self.equation_stack.append(current_identifier)
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
                        elif self.current_state == TokenConstructions.NEW_IDENTIFIER:
                            if current_identifier == 'if':
                                self.set_state(TokenConstructions.IF_DECLARATION_EXPRESSION)
                                self.is_logical_expression = True
                                self.is_indent_obliged = True
                            else:
                                self.set_state(TokenConstructions.END_OF_IDENTIFIER)
                                self.set_identifier(current_identifier)
                        elif self.current_state == TokenConstructions.ELIF_DECLARATION_EXPRESSION_IDENTIFIER:
                            if current_identifier == 'not':
                                self.set_state(TokenConstructions.ELIF_DECLARATION_EXPRESSION_NOT_OPERATOR)
                            else:
                                self.set_state(TokenConstructions.ELIF_DECLARATION_EXPRESSION_IDENTIFIER_END)
                        elif self.current_state == TokenConstructions.ELIF_DECLARATION_START:
                            if current_identifier != 'elif':
                                raise SynthaxError(f"недопустимый токен {current_identifier}", line_number,
                                                   current_character_number)
                            self.set_state(TokenConstructions.ELIF_DECLARATION_EXPRESSION)
                            self.is_indent_obliged = True

                        current_identifier = ''

                    elif c in TOKEN_ALLOWED_FIRST_SYMBOL and self.current_state == TokenConstructions.IF_DECLARATION_START:
                        self.set_state(TokenConstructions.IF_DECLARATION_EXPRESSION)
                    elif c in TOKEN_ALLOWED_FIRST_SYMBOL and self.current_state == TokenConstructions.IF_DECLARATION_EXPRESSION:
                        self.set_state(TokenConstructions.IF_DECLARATION_EXPRESSION_IDENTIFIER)
                    elif c in TOKEN_ALLOWED_FIRST_SYMBOL and self.current_state == TokenConstructions.ELIF_DECLARATION_EXPRESSION_NOT_OPERATOR:
                        self.set_state(TokenConstructions.ELIF_DECLARATION_EXPRESSION_IDENTIFIER)
                    elif c in TOKEN_ALLOWED_SYMBOLS and self.current_state == TokenConstructions.IF_DECLARATION_EXPRESSION_IDENTIFIER:
                        pass
                    elif c in TOKEN_ALLOWED_FIRST_SYMBOL and self.current_state == TokenConstructions.ELIF_DECLARATION_START:
                        pass
                    elif c in TOKEN_ALLOWED_FIRST_SYMBOL and self.current_state == TokenConstructions.ELIF_DECLARATION_EXPRESSION:
                        self.set_state(TokenConstructions.ELIF_DECLARATION_EXPRESSION_IDENTIFIER)
                    elif c in TOKEN_ALLOWED_SYMBOLS and self.current_state == TokenConstructions.ELIF_DECLARATION_EXPRESSION_IDENTIFIER:
                        pass
                    elif c == ':' and self.current_state in {TokenConstructions.IF_DECLARATION_EXPRESSION_IDENTIFIER_END,
                                                             TokenConstructions.IF_DECLARATION_EXPRESSION_IDENTIFIER,}:
                        self.check_identifier_declared(current_identifier, line_number, current_character_number)
                        self.set_state(TokenConstructions.IF_DECLARATION_INSTRUCTIONS)
                        open_indent_blocks.append('if')
                        current_indent += 1
                    elif c == ':' and self.current_state in {TokenConstructions.ELIF_DECLARATION_EXPRESSION_IDENTIFIER_END,
                                                             TokenConstructions.ELIF_DECLARATION_EXPRESSION_IDENTIFIER,}:
                        self.check_identifier_declared(current_identifier, line_number, current_character_number)
                        self.set_state(TokenConstructions.ELIF_DECLARATION_INSTRUCTIONS)
                        open_indent_blocks.pop()
                        open_indent_blocks.append('elif')
                        current_indent += 1
                    elif c == '.' and self.current_state == TokenConstructions.NEW_CONSTANT_INTEGER:
                        self.set_state(TokenConstructions.NEW_CONSTANT_FLOAT)
                    elif c in string.digits and self.current_state == TokenConstructions.NEW_CONSTANT_FLOAT:
                        pass
                    elif c == '\n':
                        pass  # обработка ниже
                    else:
                        print(repr(self.current_state))
                        raise SynthaxError(f"недопустимый символ", line_number, current_character_number)

                    # обработка последнего символа должна быть вынесена в параллельный блок
                    if c == '\n' or len(line_without_comments) == current_character_number:
                        # сброс обязательности отступа после условного оператора
                        if self.is_indent_obliged:
                            self.is_indent_obliged = False
                            self.is_logical_expression = False

                        if self.current_state in {TokenConstructions.NEW_IDENTIFIER,
                                                  TokenConstructions.EQUATION_NEW_IDENTIFIER,
                                                  TokenConstructions.NEW_CONSTANT_INTEGER,
                                                  TokenConstructions.NEW_CONSTANT_FLOAT}:
                            if self.current_state == TokenConstructions.EQUATION_NEW_IDENTIFIER:
                                self.check_identifier_declared(current_identifier, line_number, current_character_number)
                            self.equation_stack.append(current_identifier)

                        if self.current_state in {TokenConstructions.EQUATION_NEW_IDENTIFIER,
                                                  TokenConstructions.NEW_CONSTANT_INTEGER,
                                                  TokenConstructions.NEW_CONSTANT_FLOAT,
                                                  TokenConstructions.END_OF_CONSTRUCTION}  \
                            and len(self.equation_stack):
                            # print(f'equation stack: {" ".join(self.equation_stack)}')
                            if self.equation_stack[0] not in self.identifier_table.keys():
                                self.identifier_table[self.equation_stack[0]] = self.equation_stack[2:]
                        self.set_state(None)

                        current_identifier = ''
                        self.equation_stack.clear()

                    current_character_number += 1

            print("------- identifier table -------")
            for k, v in self.identifier_table.items():
                print(f"{k} = {v}")
            print("------- ---------------- -------")
