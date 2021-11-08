"""Map entries from a ready lexd file to their equivalents in russian, avar etc.
"""
from bs4 import BeautifulSoup
from bs4.element import Tag
import pandas as pd
import re
from binSearch import index
from typing import List, Dict, Tuple


def get_analysis(tag) -> Dict[str, str]:
    """Extract word & analysis from an Apertium xml file"""

    word = tag.text
    analysis = "<" + "><".join([n.get("n") for n in tag.find_all("s")]) + ">"
    return dict(word=word, analysis=analysis)


def extract_entry(item: str) -> Dict[str, str]:
    """Extract word & full string from a lexd line"""

    full_entry = re.match("^.+?(?=:)", item).group()
    word = re.match("^.+?(?=<)", item).group()
    return dict(full=full_entry, word=word)


def parse_xml(filename: str) -> pd.DataFrame:
    """Read Apertium Language pair, produce a DataFrame"""

    with open(filename, encoding="utf-8") as file:
        contents = file.read()
    bs = BeautifulSoup(contents, "html.parser")
    es:List[Tag] = bs.find_all("e")
    l_tags: List[Dict[str, str]]
    r_tags: List[Dict[str, str]]
    l_tags, r_tags = ([], [])
    for e_tag in es:
        l_tags.append(get_analysis(e_tag.find("l")))
        r_tags.append(get_analysis(e_tag.find("r")))
    data = pd.DataFrame.from_records(l_tags)
    data["word_right"] = [item["word"] for item in r_tags]
    data["analysis_right"] = [item["analysis"] for item in r_tags]
    filter_bool = data.apply(
        lambda x: x["word"] != "" and x["word_right"] != "", 
        axis=1
    )
    data = data.loc[filter_bool]
    data.sort_values(ignore_index=True, by=["word"], inplace=True)
    return data

def parse_lexd(filename: str) -> Tuple[List[str], List[Dict[str, str]]]:
    """Extract words & analyses from a lexd file"""

    with open(filename, encoding="utf-8") as file:
        contents = file.read()
    not_a_comment = lambda x: True if x and not x.startswith("#") and ":" in x else False # assert that line is not a comment
    not_a_rule = lambda x: True if "(" not in x and re.match(r"^[а-я]", x) else False # assert that line starts with letters, e.g. not a rule
    valid_strings = sorted([i for i in filter(all([not_a_comment(x), not_a_rule(x)]), contents.splitlines())])
    valid_dicts = [i for i in map(extract_entry, valid_strings)]
    valid_words = [i["word"] for i in valid_dicts]
    return valid_words, valid_dicts


def find_mapping(
    source: pd.DataFrame,
    target: pd.DataFrame,
    target_key: Union[str, int]=10
) -> pd.DataFrame:
    """Find translation pairs by russian translation"""

    assert target.shape[1] == 3
    target = target.copy()
    target["analysis"] = ""
    target["word_right"] = ""
    target["analysis_right"] = ""
    assert target.shape[1] == 6
    idx = 0
    for _, line in target.iterrows():
        idx += 1
        try:
            newindex = index(source["word"], line[target_key])
            source_line = source.iloc[newindex,:]
            target.iloc[idx-1,-3] = source_line["analysis"]
            target.iloc[idx-1,-2] = source_line["word_right"]
            target.iloc[idx-1,-1] = source_line["analysis_right"] 
        except KeyError:
            continue
    return target


def non_empty_rows(
    target: pd.DataFrame,
    filter_key: Union[str, int],
    target_key: Union[str, int]
) -> pd.DataFrame:
    """Leave rows where the value of a column is non-empty + sort"""

    target = target.copy()
    boolean = target[target_key].apply(lambda x: bool(x))
    new_target = target.loc[boolean]
    new_target.sort_values(ignore_index=True,
                            by=["analysis", target_key],
                            inplace=True)
    return new_target


def write_to_list(
    df:pd.DataFrame,
    src_list:list,
    src_dicts:list,
    key:str="word",
) -> List[Dict[str, str]]:
    """Create a list of word+analysis strings"""

    res_list = []
    for _, line in df.iterrows():
        try:
            source_idx = index(src_list, line[key])
            entry = src_dicts[source_idx]["full"]
            res_list.append(dict(
                orig=entry,
                rus=line["ru_word"]+line["analysis"],
                other=line["word_right"]+line["analysis_right"]
            ))
        except KeyError:
            continue
    return res_list


def write_to_lexd(
    filename:str,
    source: List[Dict[str, str]],
    lang1:str,
    lang2:str
) -> None:

    with open(filename, "w+", encoding="utf-8") as file:
        for item in source:
            file.write(":".join([item[lang1], item[lang2]]) + "\n")


if __name__ == "__main__":
    words, dicts = parse_lexd("merged.lexd") # read lexd
    
    rus_ava_df = parse_xml("apertium-ava-rus.ava-rus.dix") # read & convert xml for a lang pair
    rus_ava_df.to_excel("rus-avar.xlsx") # ...

    m_dict = pd.read_excel("Magomedova_dict.xlsx") # read parsed vocabularies
    k_dict = pd.read_excel("Kibrik_dict.xlsx") # ...

    m_mapping = non_empty_rows(target=find_mapping(rus_ava_df, m_dict),
        filter_key="word_right",
        target_key="word") # find matches by translation for vocabulary 1
    assert m_mapping.shape[1] == 6 # ensure the format is correct
    m_mapping.to_excel("Magomedova-rus-ava.xlsx") # save

    k_mapping = non_empty_rows(target=find_mapping(rus_ava_df, k_dict, "meaning"),
        filter_key="word_right",
        target_key="word") # find matches by translation for vocabulary 2
    assert k_mapping.shape[1] == 6 # ...
    k_mapping.to_excel("Kibrik-rus-ava.xlsx") # ...

    k_pairs = write_to_list(k_mapping, words, dicts) # create lexd-like strings
    m_pairs = write_to_list(m_mapping, words, dicts) # ...
    saves = [{
        "filename":"k_ava.lexd",
        "source":k_pairs,
        "lang1":"orig",
        "lang2":"other"
    }, {
        "filename":"k_rus.lexd",
        "source":k_pairs,
        "lang1":"orig",
        "lang2":"rus"
    }, {
        "filename":"m_ava.lexd",
        "source":m_pairs,
        "lang1":"orig",
        "lang2":"other"
    }, {
        "filename":"m_rus.lexd",
        "source":m_pairs,
        "lang1":"orig",
        "lang2":"rus"
    }]
    for save in saves:
        write_to_lexd(**save) # save lexd files