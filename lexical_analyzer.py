import string
from enum import Enum

TOKENS_ADD_INDENT = ['program', 'if']
TOKEN_ALLOWED_SYMBOLS = string.ascii_letters + string.digits + '_'
PROGRAM_KEYWORDS = ('program', 'implicit', 'none', 'integer', 'end')  # TODO: нужно дописать


class TokenConstructions(Enum):
    PROGRAM_DECLARATION = 1
    END_DECLARATION_START = 2
    NEW_TOKEN = 3
    IMPLICIT_TYPING = 4
    NEW_VARIABLE_INTEGER = 5
    NEW_VARIABLE_REAL = 6
    NEW_VARIABLE_COMPLEX = 7
    NEW_VARIABLE_CHARACTER = 8
    NEW_VARIABLE_LOGICAL = 9
    NEW_VARIABLE_SEPARATOR = 10


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
            # в текущей реализации в файле может быть только один модуль
            implicit_typing_declared = False
            first_variable_declared = False
            program_declared = False
            program_closed = False
            program_name = None
            current_indent = 0
            open_indent_blocks = []
            line_number = 0
            current_character_number = 0

            for line in lines:
                current_character_number = 0
                line_number += 1
                if program_closed:
                    raise SynthaxError('неверный токен - конец программы уже был объявлен', line_number, current_character_number)
                # очистить строку от комментариев
                line_without_comments = line.split('!')[0]
                # если вся строка это комментарий - пропустить строку
                if line.startswith('!'):
                    continue

                # обработка строки посимвольно
                current_token = ''
                current_token_number = 1
                for c in line_without_comments:
                    if current_indent and current_character_number < current_indent:
                        if c == 'e':
                            current_indent -= 2 # убираем отступ, чтобы корректно собрать токен
                            current_token += c
                            self.set_state(TokenConstructions.END_DECLARATION_START)
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
                                if current_token_lower == 'program':
                                    if program_declared and current_token_number == 1:
                                        raise SynthaxError("недопустимый символ", line_number, current_character_number)
                                    self.set_state(TokenConstructions.PROGRAM_DECLARATION)
                                elif current_token_lower == 'implicit':
                                    self.set_state(TokenConstructions.IMPLICIT_TYPING)
                                elif current_token_lower == 'integer':
                                    self.set_state(TokenConstructions.NEW_VARIABLE_INTEGER)

                            elif self.current_state == TokenConstructions.PROGRAM_DECLARATION:
                                if current_token_number == 2:
                                    program_name = current_token
                                    current_indent += 2
                                    open_indent_blocks.append('program')
                                    self.set_state(TokenConstructions.NEW_TOKEN)
                                else:
                                    raise SynthaxError("недопустимый символ", line_number, current_character_number)

                            elif self.current_state == TokenConstructions.END_DECLARATION_START:
                                if current_token_lower == 'end':
                                    pass
                                elif current_token_lower == 'program' and open_indent_blocks[-1] == 'program':  # end program
                                    pass
                                elif current_token_lower == program_name:  # end program <program_name>
                                    program_closed = True
                                    open_indent_blocks.pop()
                                elif current_token_lower == 'if' and open_indent_blocks[-1] == 'if':  # end if
                                    open_indent_blocks.pop()
                                    self.set_state(TokenConstructions.NEW_TOKEN)
                                else:
                                    raise SynthaxError("недопустимый символ", line_number, current_character_number)

                            elif self.current_state == TokenConstructions.IMPLICIT_TYPING:
                                if current_token_lower == 'none':
                                    self.set_state(TokenConstructions.NEW_TOKEN)
                                    implicit_typing_declared = True

                            elif self.current_state in [TokenConstructions.NEW_VARIABLE_INTEGER,
                                                        TokenConstructions.NEW_VARIABLE_CHARACTER,
                                                        TokenConstructions.NEW_VARIABLE_REAL,
                                                        TokenConstructions.NEW_VARIABLE_COMPLEX,
                                                        TokenConstructions.NEW_VARIABLE_LOGICAL]:
                                if current_token == '::':
                                    self.set_state(TokenConstructions.NEW_VARIABLE_SEPARATOR)
                                else:
                                    raise SynthaxError("недопустимый символ", line_number, current_character_number)

                            elif self.current_state == TokenConstructions.NEW_VARIABLE_SEPARATOR:
                                if current_token_lower not in PROGRAM_KEYWORDS:
                                    self.set_state(TokenConstructions.NEW_TOKEN)
                                    # TODO: нужно составить тут список имен переменных?
                                else:
                                    raise SynthaxError(f"недопустимый токен {current_token}", line_number, current_character_number)

                            current_token_number += 1
                            current_token = current_token_lower = ''

                    current_character_number += 1
