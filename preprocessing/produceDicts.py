import pandas as pd
import re
import sys
from binSearch import index

def extract_entry(item):
    """Extract word & analysis from a lexd line"""
    full_entry = re.match("^.+?(?=:)", item).group()
    word = re.match("^.+?(?=<)", item).group()
    return dict(full=full_entry, word=word)

def parse_lexd(filename):
    """Extract words & analyses from a lexd file"""
    with open("merged.lexd", encoding="utf-8") as file:
        contents = file.read()
    not_a_comment = lambda x: True if x and not x.startswith("#") and ":" in x else False # assert that line is not a comment
    not_a_rule = lambda x: True if "(" not in x and re.match(r"^[а-я]", x) else False # assert that line starts with letters, e.g. not a rule
    valid_strings = sorted([i for i in filter(all([not_a_comment(x), not_a_rule(x)]), contents.splitlines())])
    valid_dicts = [i for i in map(extract_entry, valid_strings)]
    valid_words = [i["word"] for i in valid_dicts]
    return valid_words, valid_dicts

def main(filename):
    words, dicts = parse_lexd(filename)

if __name__ == "__main__":
    file = sys.argv[1]
    main(file)