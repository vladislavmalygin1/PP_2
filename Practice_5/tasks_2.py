import re
def match_ab_zero(text):
    pattern = r'ab*'
    return bool(re.search(pattern, text))


def match_ab_range(text):
    pattern = r'ab{2,3}'
    return bool(re.search(pattern, text))



def find_underscore_sequences(text):
    pattern = r'[a-z]+_[a-z]+'
    return re.findall(pattern, text)


def find_upper_lower(text):
    pattern = r'[A-Z][a-z]+'
    return re.findall(pattern, text)


def match_a_to_b(text):
    pattern = r'a.*b$'
    return bool(re.search(pattern, text))


def replace_with_colon(text):
    return re.sub(r'[ ,.]', ':', text)


def snake_to_camel(text):
    return re.sub(r'_([a-z])', lambda x: x.group(1).upper(), text)




def split_at_uppercase(text):
    return re.split(r'(?=[A-Z])', text)



def insert_spaces(text):
    return re.sub(r'(?<!^)(?=[A-Z])', ' ', text)


def camel_to_snake(text):
    str1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', str1).lower()