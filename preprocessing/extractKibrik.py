import zipfile
import re
import os
import pandas as pd
from bs4 import BeautifulSoup
from typing import List, Dict
import sys

def read_docx(filename:str) -> BeautifulSoup:
    with zipfile.ZipFile(filename, "r") as zipf:
        zipf.extractall(os.getcwd())
    with open(os.path.join(os.getcwd(), "word/document.xml"), "r", encoding="utf-8") as file:
        content:str = file.read()
    soup = BeautifulSoup(content, "html.parser")
    return soup

def get_entry_strings(soup: BeautifulSoup) -> List[str]:
    paras = soup.find_all("w:p")
    strings = []
    for para in paras[4:]:
        text_chunks = para.find_all("w:t")
        if len(text_chunks) <= 1:
            continue
        strings.append("".join([t.text for t in text_chunks if t.text]))
    return [re.sub("‘", "’", string) for string in strings]

def strings_to_records(ent_strings: List[str]) -> List[Dict[str, str]]:
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
                for m in meanings:
                    records.append(dict(
                        entry=et,
                        meaning=m,
                        POS=POS
                    ))
        except AttributeError:
            continue
    return records

mapping = {
    "nouns":{"pos_filter":"", "regex_filter":"", "cut_filter":""},
    "adj":{"pos_filter":"", "regex_filter":"", "cut_filter":""},
    "adv":{"pos_filter":"", "regex_filter":"", "cut_filter":""},
    "verbI":{"pos_filter":"", "regex_filter":"", "cut_filter":""},
    "verbII":{"pos_filter":"", "regex_filter":"", "cut_filter":""}
}

def write_slice(filename, strings, pos_filter, regex_filter, cut_filter) -> None:
    pos_slice = [i for i in filter(lambda x: pos_filter in x, strings)]
    with open(f'kibrik_{filename}.txt', "w+", encoding="UTF-8") as file:
        for item in pos_slice:
            if re.search(regex_filter, item):
                file.write(re.search(cut_filter, item).group() + "\n")

if __name__ == "__main__":
    soup = read_docx("bag.docx")
    ent_list = get_entry_strings(soup)
    rec_list = strings_to_records(ent_list)
        if sys.argv[1] == "save":
            k_dict = pd.DataFrame.from_records(rec_list)
            k_dict.to_excel("Kibrik_dict.xlsx", index=False)
        elif sys.argv[1] in mapping:
            pass
        else:
            print("Expected arguments: <save> | <nouns/adj/adv/verbI/verbII>")
            sys.exit(1)