import string
from enum import Enum

TOKEN_ALLOWED_SYMBOLS = string.ascii_letters + string.digits + '_'
COMMENTS_START_SYMBOL = '#'
TOKENS_ADD_INDENT = ['if', 'elif']  # TODO: нужно дописать
PROGRAM_KEYWORDS = ('none', 'if', 'elif', 'else', 'foreach', 'print')  # TODO: нужно дописать
TOKEN_SEPARATOR_SYMBOLS = (' ', '\n', '(', ')', '\'', '"', ',', '+', '-', '=')


class TokenConstructions(Enum):
    NEW_TOKEN = 1
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
    equation_stack = []

    def set_state(self, new_state):
        self.previous_state = self.current_state
        self.current_state = new_state

    def __init__(self, program_filename):
        self.program_filename = program_filename
        self.current_state = TokenConstructions.NEW_TOKEN

    def check_token_not_keyword(self, token, line_number, current_character_number):
        if token in PROGRAM_KEYWORDS:
            raise SynthaxError(f"недопустимый токен {token}", line_number, current_character_number)

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
                current_token = ''
                current_token_number = 1
                # variable for storing strings
                current_string = ''

                for c in line_without_comments:
                    if current_indent and current_character_number < current_indent:
                        # if c == 'e':
                        #     current_indent -= 2 # убираем отступ, чтобы корректно собрать токен
                        #     current_token += c
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
                        elif c not in TOKEN_SEPARATOR_SYMBOLS:
                            current_token += c

                        if (c == ' ' or c == '\n' or len(line_without_comments) == current_character_number
                            or c in TOKEN_SEPARATOR_SYMBOLS) \
                                and current_token:
                            if self.current_state == TokenConstructions.NEW_TOKEN:
                                pass
                            elif self.current_state == TokenConstructions.EQUATION:
                                self.equation_stack.append(current_token)
                                if len(line_without_comments) == current_character_number:
                                    self.current_state = TokenConstructions.NEW_TOKEN
                                    print(f'equation stack: {" ".join(self.equation_stack)}')
                            elif self.current_state == TokenConstructions.IF_DECLARATION_START:
                                self.check_token_not_keyword(current_token, line_number, current_character_number)
                            elif self.current_state == TokenConstructions.FUNCTION_CALL_START:
                                self.check_token_not_keyword(current_token, line_number, current_character_number)

                            current_token_number += 1
                            print(f'new token: "{current_token}"')
                            current_token = ''

                        if c == '(' and self.current_state == TokenConstructions.NEW_TOKEN:
                            self.set_state(TokenConstructions.FUNCTION_CALL_START)
                            print(f'function call: "{current_token}"')
                            current_token = ''
                        elif c == ')' and self.current_state == TokenConstructions.FUNCTION_CALL_START:
                            self.set_state(TokenConstructions.NEW_TOKEN)
                            current_token = ''
                        elif c == '"' and self.current_state != TokenConstructions.STRING_2:
                            self.current_state = TokenConstructions.STRING_2
                            current_token = ''
                        elif c == '"' and self.current_state == TokenConstructions.STRING_2:
                            self.set_state(TokenConstructions.NEW_TOKEN)
                            current_token = ''
                            print(f'string: "{current_string}"')
                            current_string = ''
                        elif c == '\'' and self.current_state != TokenConstructions.STRING_1:
                            self.current_state = TokenConstructions.STRING_1
                            current_token = ''
                        elif c == '\'' and self.current_state == TokenConstructions.STRING_1:
                            self.set_state(TokenConstructions.NEW_TOKEN)
                            current_token = ''
                            print(f'string: "{current_string}"')
                            current_string = ''
                        elif c == '=' and self.current_state == TokenConstructions.NEW_TOKEN:
                            current_token_number += 1
                            current_token = ''
                            self.set_state(TokenConstructions.EQUATION)
                            self.equation_stack = []
                        elif c == '=' and self.current_state == TokenConstructions.EQUATION:
                            raise SynthaxError(f"недопустимый токен {current_token}", line_number, current_character_number)
                        elif c == '+' and self.current_state == TokenConstructions.EQUATION:
                            self.equation_stack.append('+')
                        elif c == '-' and self.current_state == TokenConstructions.EQUATION:
                            self.equation_stack.append('-')


                    current_character_number += 1
