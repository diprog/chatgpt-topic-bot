import aiofiles

default_language = 'ru'
locale: dict[str, dict[str, str]] = {}


async def init():
    """
    Иницииализация модуля. Обязательно нужно вызвать на старте скрипта, иначе не от куда будет получать строки.
    """
    working_key = None
    lang = None
    async with aiofiles.open('locale/locale.loc', 'r', encoding='utf-8') as f:
        for line in await f.readlines():
            if line[0] == '/':
                pass
            elif line[0] == '#':
                working_key = line.replace('#', '').replace(' ', '')[:-1]
                lang = None
            elif working_key:
                if not locale.get(working_key):
                    locale[working_key] = {}
                if line.startswith('___'):
                    lang = line.replace('_', '')[:-1]
                    locale[working_key][lang] = ''
                elif lang:
                    locale[working_key][lang] += line

    # Убираем лишние пробелы и управляющие символы в конце и в начале строк.
    for key in locale.keys():
        for lang in locale[key].keys():
            locale[key][lang] = locale[key][lang].strip()


def clear():
    global locale
    locale = {}


def loc(key: str, *args):
    if not locale:
        raise Exception('Не выполнен метод init()')
    string = locale[key][default_language]
    return string.format(*args) if args else string
