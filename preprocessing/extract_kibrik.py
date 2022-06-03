# usr/bin/python3
import argparse
import zipfile
import re
import os
import pandas as pd
from bs4 import BeautifulSoup
from typing import List, Dict, Union
import sys
from transliterate import transliterate


def read_docx(filename: str) -> BeautifulSoup:
    with open(filename, "r", encoding="utf-8") as file:
        content: str = file.read()
    soup = BeautifulSoup(content, "html.parser")
    return soup


def get_entry_strings(soup: BeautifulSoup) -> List[str]:
    """Get meaningful strings from a vocabulary soup"""

    paras = soup.find_all("w:p")
    strings = []
    for para in paras[4:]:
        text_chunks = para.find_all("w:t")
        if len(text_chunks) <= 1:
            continue
        strings.append("".join([t.text for t in text_chunks if t.text]))

    expell_numbers = lambda x: re.sub(r"\d", "", x.replace("‘", "’"))
    return [item for item in map(expell_numbers, strings)]


def strings_to_records(ent_strings: List[str]) -> List[Dict[str, str]]:
    """read lines from docx with Kibrik vocabulary. Produce a table of format {word/pos/entry}"""

    records = []
    for string in ent_strings:
        if not re.match(
            r"[^а-я ]+", string
        ):  # assert that the line starts with a latin entry
            continue
        try:
            entry = re.match(r"[^а-я]+?(?= [A-Z])", string)
            entrytext = entry.group().strip().split(" || ")
            entryend = entry.span()[1]
            meanings = re.search(r" [а-я\., ]+ *", string).group().strip().split(", ")

            declension = ""
            category = ""

            POS = (
                re.search(r" [A-Z][^а-я]*? (?=[а-я])", string[entryend:])
                .group()
                .strip()
            )

            if POS == "V":
                for key, value in mapping.items():
                    if re.search(value["regex_filter"], string):
                        category = key
            elif POS == "N":
                decl_search = re.search(r"; (gen.+?)$", string)
                if decl_search:
                    declension = decl_search.group(1)

            for et in entrytext:
                tr_et = transliterate(et)
                for m in meanings:
                    records.append(dict(
                        word=tr_et, 
                        original=et, ru_word=m, POS=POS, category=category, declension=declension
                    ))
        except AttributeError:
            continue
    return records


mapping = {
    "nouns": {
        "pos_filter": " N ",
        "regex_filter": "^.+(?= N )",
        "cut_filter": "^.+?(?= N )",
    },
    "adj": {
        "pos_filter": " Adj ",
        "regex_filter": "^.*?(?= (Adj|PronAdj))",
        "cut_filter": "^.*?(?= Adj)",
    },
    "adv": {
        "pos_filter": "(Adv|PronAdv)",
        "regex_filter": "^.*?(?= (Adv|PronAdv))",
        "cut_filter": "^.*?(?= (Adv|PronAdv))",
    },
    "verbIa": {
        "pos_filter": " V ",
        "regex_filter": "[uū]̃* V.*",
        "cut_filter": "^.*?(?= V)",
    },
    "verbIb": {
        "pos_filter": " V ",
        "regex_filter": "[iĩ] V.*?conv.*?[rn]āχ.*?[aāãã],",
        "cut_filter": "^.*?(?= V)",
    },
    "verbIIa": {
        "pos_filter": " V ",
        "regex_filter": "[^iĩ] V.*?conv.*?i.āχ",
        "cut_filter": "^.*?(?= V)",
    },
    "verbIIb": {
        "pos_filter": " V ",
        "regex_filter": "[^iĩ] V.*?conv.*?u.āχ",
        "cut_filter": "^.*?(?= V)",
    },
    "verbIII": {
        "pos_filter": " V ",
        "regex_filter": "inf āla",
        "cut_filter": "^.*?(?= V)",
    },
    "verbIV": {
        "pos_filter": " V ",
        "regex_filter": "conv.*?[^r]ā.+inf {1,2}ā",
        "cut_filter": "^.*?(?= V)",
    },
    "verbV": {
        "pos_filter": " V ",
        "regex_filter": "conv.*?r.+inf.*?rā",
        "cut_filter": "^.*?(?= V)",
    },
}


def write_slice_to_file(
    name: str,
    strings: List[str],
    pos_filter: str,
    regex_filter: Union[str, re.Pattern],
    cut_filter: Union[str, re.Pattern],
) -> None:
    """Write a subset of the vocabulary to a text file"""

    pos_slice = [i for i in filter(lambda x: pos_filter in x, strings)]
    with open(f"kibrik_{name}.txt", "w+", encoding="UTF-8") as file:
        for item in pos_slice:
            if re.search(regex_filter, item):
                file.write(transliterate(re.search(cut_filter, item).group()) + "\n")


def write_slice_to_stdout(
    name: str,
    strings: List[str],
    pos_filter: str,
    regex_filter: Union[str, re.Pattern],
    cut_filter: Union[str, re.Pattern],
) -> None:
    """Write a subset of the vocabulary to the standart output as a lexicon"""

    pos_slice = [i for i in filter(lambda x: pos_filter in x, strings)]
    outs: List[str] = []
    for item in pos_slice:
        if re.search(regex_filter, item):
            found = re.search(cut_filter, item).group().split(" || ")
            for new_word in found:
                outs.append(transliterate(new_word))
    sys.stdout.write("\n".join([f"LEXICON {name}", *outs]))


parser = argparse.ArgumentParser()
parser.add_argument("--infile", help="file to read")
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument("--outfile", help="File to write the complete table to.")
group.add_argument("--slice", choices=list(mapping.keys()), help="Name of the slice to get from the file.")

if __name__ == "__main__":
    parsed = parser.parse_args(sys.argv[1:])
    soup = read_docx(parsed.infile)
    ent_list = get_entry_strings(soup)
    rec_list = strings_to_records(ent_list)
    if parsed.outfile is not None:
        k_dict = pd.DataFrame.from_records(rec_list)
        k_dict.to_csv(parsed.outfile, header=False, index=False, sep=";", encoding="utf-8", quotechar='"')
    elif parsed.slice is not None:
        write_slice_to_stdout(parsed.slice, ent_list, **mapping[parsed.slice])
    else:
        sys.exit(1)
