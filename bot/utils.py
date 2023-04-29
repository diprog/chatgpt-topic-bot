import constants


def is_main_admin(user_id: int):
    return user_id in (constants.DEVELOPER_ID, constants.MAIN_ADMIN_ID)


def prepare_markdown(string):
    # Define characters that need to be escaped with a preceding '\'
    escape_chars = '_*[]()~`>#-|=+{}.!\\'

    # Define characters that need to be escaped in specific contexts
    pre_code_escape_chars = '`\\'
    link_emoji_escape_chars = ')\\'

    # Define character to use in place of ambiguous italic and underline entities
    ambiguity_char = '\r'

    # Escape all necessary characters with a preceding '\'
    escaped_string = ''
    i = 0
    while i < len(string):
        char = string[i]
        if char == '\\':
            # Escape character with a preceding '\'
            next_char = string[i + 1] if i + 1 < len(string) else ''
            if next_char in (escape_chars + pre_code_escape_chars + link_emoji_escape_chars):
                escaped_string += next_char
                i += 1
            else:
                escaped_string += char
        elif char in escape_chars:
            # Escape character with a preceding '\'
            escaped_string += '\\' + char
        elif char == '`':
            # Check if in pre or code entity, and escape if necessary
            if '`' in escaped_string[-3:] or '`' in string[i + 1:i + 4]:
                escaped_string += '\\' + char
            else:
                escaped_string += char
        elif char == '(':
            # Check if in link or emoji definition, and escape ')' and '\' if necessary
            if '[' in escaped_string[-3:] and ']' not in escaped_string[-3:]:
                j = i + 1
                while j < len(string):
                    if string[j] == ']':
                        break
                    elif string[j] == ')':
                        escaped_string += '\\' + string[j]
                        i = j
                        break
                    elif string[j] == '\\':
                        escaped_string += '\\' + string[j]
                        j += 1
                    else:
                        escaped_string += string[j]
                        j += 1
                else:
                    escaped_string += char
            else:
                escaped_string += char
        elif char == '_':
            # Check if ambiguous italic or underline entity, and add ambiguity character if necessary
            if '_' in escaped_string[-3:] or '_' in string[i + 1:i + 4]:
                escaped_string += ambiguity_char
            else:
                escaped_string += char
        else:
            escaped_string += char
        i += 1

    return escaped_string
