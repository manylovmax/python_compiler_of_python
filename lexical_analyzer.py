import string
from enum import Enum

TOKEN_ALLOWED_SYMBOLS = string.ascii_letters + string.digits + '_'
TOKENS_ADD_INDENT = ['if', 'elif']  # TODO: нужно дописать
PROGRAM_KEYWORDS = ('none',)  # TODO: нужно дописать


class TokenConstructions(Enum):
    NEW_TOKEN = 1
    IF_DECLARATION_START = 2
    ELIF_DECLARATION_START = 3


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

    def set_state(self, new_state):
        self.previous_state = self.current_state
        self.current_state = new_state

    def __init__(self, program_filename):
        self.program_filename = program_filename
        self.current_state = TokenConstructions.NEW_TOKEN

    def analyze(self):
        with open(self.program_filename, 'r') as f:
            lines = f.readlines()

            current_indent = 0
            open_indent_blocks = []
            line_number = 0
            current_character_number = 0

            for line in lines:
                current_character_number = 0
                line_number += 1
                # очистить строку от комментариев
                line_without_comments = line.split('#')[0]
                # если вся строка это комментарий - пропустить строку
                if line.startswith('#'):
                    continue

                # обработка строки посимвольно
                current_token = ''
                current_token_number = 1
                for c in line_without_comments:
                    if current_indent and current_character_number < current_indent:
                        if c == 'e':
                            current_indent -= 2 # убираем отступ, чтобы корректно собрать токен
                            current_token += c
                            self.set_state(TokenConstructions.ELIF_DECLARATION_START)
                        else:
                            pass
                    else:
                        # проверка первого символа
                        if c not in string.ascii_letters and current_character_number == current_indent:
                            raise SynthaxError("недопустимый символ", line_number, current_character_number)
                        # сборка токена
                        if c != ' ' and c != '\n':
                            current_token += c
                        elif (c == ' ' or c == '\n') and current_token:
                            current_token_lower = current_token.lower()

                            if self.current_state == TokenConstructions.NEW_TOKEN:
                                pass
                                # if current_token_lower == 'program':
                                #     if program_declared and current_token_number == 1:
                                #         raise SynthaxError("недопустимый символ", line_number, current_character_number)


                            current_token_number += 1
                            current_token = current_token_lower = ''

                    current_character_number += 1
