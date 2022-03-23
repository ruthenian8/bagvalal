"""
A script to process and resave a dictionary from Garik's table
""" 
import pandas as pd
import re
from typing import Callable, List, Union

def lower_strategy(item: str) -> str:
    return item.lower()


def transform_strategy(item: str) -> str:
    replacements = {
        "i": "Ӏ",
        "a": "а",
        "á": "а",
        "ā": "а",
        "é": "е",
        "ē": "е",
        "ó": "о",
        "ō": "о",
        "x̄": "x̄",
        "x": "х"
    }
    for key in replacements.keys():
        item = item.replace(key, replacements[key])
    return item


def substitute_strategy(item: str) -> str:
    return re.sub(r"(?<=^)Ӏ", "лъ", item)


def clear_strategy(item: str) -> str:
    return re.sub(r"[^а-яᴴ\-\–Ӏ/̄]", "", item).replace("/", "")


class Pipe():
    """Stack for funcs to apply to entries"""
    def __init__(self, funcs: List[Callable]=None) -> None:
        self.strats: List[Callable] = []
        if not funcs:
            return
        self.strats.extend(funcs)

    def __call__(self, item: str) -> str:
        for func in self.strats:
            item = func(item)
        return item


def main(
    filename: str,
    out_file: str,
    word_col_id: Union[str, int]=3,
    pos_col_id: Union[str, int]=8,
    trans_col_id: Union[str, int]=10,
) -> None:

    bag = pd.read_csv(filename, sep=";", index_col=0, header=None)
    pipe = Pipe([lower_strategy, transform_strategy, substitute_strategy, clear_strategy])
    bag[word_col_id] = bag[word_col_id].apply(lambda x: pipe(x))
    bag = bag.loc[bag[trans_col_id].isna() == False]
    bag = bag[[word_col_id, pos_col_id, trans_col_id]]
    bag.columns = ["word", "POS", "ru_word"]
    bag.to_excel(out_file)


if __name__ == "__main__":
    main("b_upd.csv", "Magomedova_dict.xlsx")