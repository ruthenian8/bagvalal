#usr/bin/python3
import zipfile
import re
import os
import pandas as pd
from bs4 import BeautifulSoup
from typing import List, Dict, Union
import sys
from transliterate import transliterate


def read_docx(filename:str) -> BeautifulSoup:
    with zipfile.ZipFile(filename, "r") as zipf:
        zipf.extractall(os.getcwd())
    with open(os.path.join(os.getcwd(), "word/document.xml"), "r", encoding="utf-8") as file:
        content:str = file.read()
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
        if not re.match(r"[^а-я ]+", string): #assert that the line starts with a latin entry
            continue
        try:
            entry = re.match(r"[^а-я]+?(?= [A-Z])", string)
            entrytext = entry.group().strip().split(" || ")
            entryend = entry.span()[1]
            meanings = re.search(r" [а-я\., ]+ *", string).group().strip().split(", ")
            POS = re.search(r" [A-Z][^а-я]*? (?=[а-я])", string[entryend:]).group().strip()
            for et in entrytext:
                et = transliterate(et)
                for m in meanings:
                    records.append(dict(
                        word=et,
                        ru_word=m,
                        POS=POS
                    ))
        except AttributeError:
            continue
    return records

mapping = {
    "nouns":{
        "pos_filter":" N ",
        "regex_filter":"^.+(?= N )",
        "cut_filter":"^.+?(?= N )"
    },
    "adj":{
        "pos_filter":" Adj ",
        "regex_filter":"^.*?(?= Adj)",
        "cut_filter":"^.*?(?= Adj)"
    },
    "adv":{
        "pos_filter":"(Adv|PronAdv)", 
        "regex_filter":"^.*?(?= (Adv|PronAdv))", 
        "cut_filter":"^.*?(?= (Adv|PronAdv))"
    },
    "verbIa":{
        "pos_filter":" V ", 
        "regex_filter":"[uū]̃* V.*", 
        "cut_filter":"^.*?(?= V)"
    },
    "verbIb":{
        "pos_filter":" V ", 
        "regex_filter":"[iĩ] V.*?conv.*?[rn]āχ.*?[aāãã],", 
        "cut_filter":"^.*?(?= V)"
    },
    "verbIIa":{
        "pos_filter":" V ", 
        "regex_filter":"[^iĩ] V.*?conv.*?i.āχ", 
        "cut_filter":"^.*?(?= V)"
    },
    "verbIIb":{
        "pos_filter":" V ", 
        "regex_filter":"[^iĩ] V.*?conv.*?u.āχ", 
        "cut_filter":"^.*?(?= V)"
    },
    "verbIII":{
        "pos_filter":" V ", 
        "regex_filter":"inf āla", 
        "cut_filter":"^.*?(?= V)"
    },
    "verbIV":{
        "pos_filter":" V ", 
        "regex_filter":"conv.*?[^r]ā.+inf {1,2}ā", 
        "cut_filter":"^.*?(?= V)"
    },
    "verbV":{
        "pos_filter":" V ", 
        "regex_filter":"conv.*?r.+inf.*?rā", 
        "cut_filter":"^.*?(?= V)"
    }
}

def write_slice_to_file(
    name: str,
    strings: List[str],
    pos_filter: str,
    regex_filter: Union[str, re.Pattern],
    cut_filter: Union[str, re.Pattern]
) -> None:
    """Write a subset of the vocabulary to a text file"""

    pos_slice = [i for i in filter(lambda x: pos_filter in x, strings)]
    with open(f'kibrik_{name}.txt', "w+", encoding="UTF-8") as file:
        for item in pos_slice:
            if re.search(regex_filter, item):
                file.write(transliterate(re.search(cut_filter, item).group()) + "\n")


def write_slice_to_stdout(
    name: str,
    strings: List[str],
    pos_filter: str,
    regex_filter: Union[str, re.Pattern],
    cut_filter: Union[str, re.Pattern]
) -> None:
    """Write a subset of the vocabulary to the standart output as a lexicon"""

    pos_slice = [i for i in filter(lambda x: pos_filter in x, strings)]
    outs:List[str] = []
    for item in pos_slice:
        if re.search(regex_filter, item):
            found = re.search(cut_filter, item).group().split(" || ")
            for new_word in found:
                outs.append(transliterate(new_word))
    sys.stdout.write("\n".join([f"LEXICON {name}", *outs]))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Expected arguments: <save> | <nouns/adj/adv/verbI/verbII>")
        sys.exit(1)
    soup = read_docx("bag.docx")
    ent_list = get_entry_strings(soup)
    rec_list = strings_to_records(ent_list)
    goal = sys.argv[1]     
    if goal == "save":
        k_dict = pd.DataFrame.from_records(rec_list)
        k_dict.to_excel("Kibrik_dict.xlsx", index=False)
    elif goal in mapping:
        write_slice_to_stdout(goal, ent_list, **mapping[goal])
    else:
        sys.exit(1)
