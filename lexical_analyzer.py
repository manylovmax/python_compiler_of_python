import string
from enum import Enum

TOKEN_ALLOWED_SYMBOLS = string.ascii_letters + string.digits + '_'
COMMENTS_START_SYMBOL = '#'
TOKENS_ADD_INDENT = ['if', 'elif']  # TODO: нужно дописать
PROGRAM_KEYWORDS = ('none', 'if', 'elif', 'else', 'foreach', 'print')  # TODO: нужно дописать
IDENTIFIER_SEPARATOR_SYMBOLS = (' ', '\n', '(', ')', '\'', '"', ',', '+', '-', '=')


class TokenConstructions(Enum):
    NEW_IDENTIFIER = 1
    IF_DECLARATION_START = 2
    ELIF_DECLARATION_START = 3
    FUNCTION_CALL_START = 4
    STRING_1 = 5
    STRING_2 = 6
    EQUATION = 7


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
    previous_identifier = ''
    current_identifier = ''
    equation_stack = []
    state_stack = []

    def set_state(self, new_state):
        self.previous_state = self.current_state
        self.current_state = new_state
        self.state_stack.append(new_state)

    def set_identifier(self, new_name):
        self.previous_identifier = self.current_identifier
        self.current_identifier = new_name

    def __init__(self, program_filename):
        self.program_filename = program_filename
        self.current_state = TokenConstructions.NEW_IDENTIFIER
        self.state_stack = [self.current_state]

    def check_identifier_not_keyword(self, identifier, line_number, current_character_number):
        if identifier in PROGRAM_KEYWORDS:
            raise SynthaxError(f"недопустимый идентификатор {identifier}", line_number, current_character_number)

    def analyze(self):
        with open(self.program_filename, 'r') as f:
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
                current_token = ''

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
                        if c not in string.ascii_letters and current_character_number == current_indent:
                            raise SynthaxError("недопустимый символ", line_number, current_character_number)
                        # сборка токена
                        if self.current_state == TokenConstructions.STRING_1 and c != '\''\
                                or self.current_state == TokenConstructions.STRING_2 and c != '"':
                            current_string += c
                            current_token += c
                        elif c not in IDENTIFIER_SEPARATOR_SYMBOLS:
                            self.current_identifier += c
                            current_token += c
                        elif c in IDENTIFIER_SEPARATOR_SYMBOLS:
                            current_token = c

                        #print(f'current token: {repr(current_token)}')
                        if current_token in IDENTIFIER_SEPARATOR_SYMBOLS:
                            current_token = ''

                        if (c == ' ' or c == '\n' or len(line_without_comments) == current_character_number
                            or c in IDENTIFIER_SEPARATOR_SYMBOLS) \
                                and self.current_identifier:
                            if self.current_state == TokenConstructions.NEW_IDENTIFIER:
                                pass
                            elif self.current_state == TokenConstructions.EQUATION:
                                self.equation_stack.append(self.current_identifier)
                                if len(line_without_comments) == current_character_number:
                                    self.set_state(TokenConstructions.NEW_IDENTIFIER)
                                    print(f'equation stack: {" ".join(self.equation_stack)}')
                            elif self.current_state == TokenConstructions.IF_DECLARATION_START:
                                self.check_identifier_not_keyword(self.current_identifier, line_number, current_character_number)
                            elif self.current_state == TokenConstructions.FUNCTION_CALL_START:
                                self.check_identifier_not_keyword(self.current_identifier, line_number, current_character_number)

                            self.set_identifier('')
                            print(f'new identifier: "{self.previous_identifier}"')

                        if c == '(' and self.current_state == TokenConstructions.NEW_IDENTIFIER:
                            self.set_state(TokenConstructions.FUNCTION_CALL_START)
                            print(f'function call: "{self.previous_identifier}"')
                            self.set_identifier('')
                        elif c == ')' and self.current_state == TokenConstructions.FUNCTION_CALL_START:
                            self.set_state(TokenConstructions.NEW_IDENTIFIER)
                            self.set_identifier('')
                        elif c == '"' and self.current_state != TokenConstructions.STRING_2:
                            self.set_state(TokenConstructions.STRING_2)
                            self.set_identifier('')
                        elif c == '"' and self.current_state == TokenConstructions.STRING_2:
                            self.set_state(TokenConstructions.NEW_IDENTIFIER)
                            self.set_identifier('')
                            print(f'string: "{current_string}"')
                            current_string = ''
                        elif c == '\'' and self.current_state != TokenConstructions.STRING_1:
                            self.set_state(TokenConstructions.STRING_1)
                            self.set_identifier('')
                        elif c == '\'' and self.current_state == TokenConstructions.STRING_1:
                            self.set_identifier('')
                            print(f'string: "{current_string}"')
                            #print(f'current token: "{current_token}"')
                            if self.previous_state == TokenConstructions.EQUATION:
                                self.equation_stack.append(repr(current_string))
                                print(f'equation stack: {" ".join(self.equation_stack)}')
                            self.set_state(TokenConstructions.NEW_IDENTIFIER)
                            current_string = ''
                        elif c == '=' and self.current_state == TokenConstructions.NEW_IDENTIFIER:
                            self.set_state(TokenConstructions.EQUATION)
                            self.equation_stack = [self.previous_identifier, '=']
                        elif c == '=' and self.current_state == TokenConstructions.EQUATION:
                            raise SynthaxError(f"недопустимый токен {self.previous_identifier}", line_number, current_character_number)
                        elif c == '+' and self.current_state == TokenConstructions.EQUATION:
                            self.equation_stack.append('+')
                        elif c == '-' and self.current_state == TokenConstructions.EQUATION:
                            self.equation_stack.append('-')


                    current_character_number += 1
