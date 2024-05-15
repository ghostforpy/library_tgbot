MAX_CHARS_COUNT = 2000


def paginate_string(s):
    if len(s) <= MAX_CHARS_COUNT:
        return [s]
    try:
        last_index = s[: MAX_CHARS_COUNT - 1].rindex("\n") + 1
    except ValueError:
        last_index = MAX_CHARS_COUNT
    result = [s[:last_index]]
    result.extend(paginate_string(s[last_index:]))
    return result
