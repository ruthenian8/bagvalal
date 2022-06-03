import sys
import argparse
import re

from bs4 import BeautifulSoup


def parse_file(content: str):
    soup = BeautifulSoup(content, "html.parser")
    paras = soup.find_all("w:p")
    lines = [(par := p.get_text()) for p in paras]
    processed_lines = []
    for idx, line in enumerate(lines):
        if not re.match(r"[ (]", line) or not re.search(r"[a-zA-Z]", line):
            continue
        line: str = line.strip()
        line = re.sub(r"([a-zɬːχ’])([A-Zа-яА-Я])", r"\1 \2", line)
        line = re.sub(r"\(.+?\) ", "", line) # remove parentheses
        line = re.sub(r"[А-Я]{2,}", "", line)
        line = re.sub(r"[!:,;“()\[\]”—]", "", line)
        line = re.sub(r"^– | – ", "", line)
        line = re.sub(r"(?<=[^=-])\?", "", line)
        line = line.strip()
        processed_lines.append(line)
    return processed_lines


def parse_lines(lines: list):
    pairs = []
    checked = dict()
    for idx, line in enumerate(lines):
        if idx in checked:
            continue
        tokens_current = re.split(r"[\t ]+", line.rstrip("."))
        tokens_next = re.split(r"[\t ]+", lines[idx+1].rstrip("."))
        if len(tokens_current) == len(tokens_next):
            if re.match(r"[A-Zа-яА-Я]", tokens_current[0])\
            or not re.match(r"[A-Zа-яА-Я]", tokens_next[0]): # latin tokens vs cyrillic
                continue
            for t_idx, token in enumerate(tokens_current):
                pairs.append(token + "," + tokens_next[t_idx])
            if line.endswith("."):
                pairs.append("<.>,<punct>")
            checked[idx] = True
            checked[idx + 1] = True
        elif (curlen := len(tokens_current) // 2) == 0:
            first_half = tokens_current[:curlen]
            second_half = tokens_current[curlen:]
            if re.match(r"[A-Zа-яА-Я]", tokens_current[0])\
            or not re.match(r"[A-Zа-яА-Я]", second_half[0]):
                continue
            for t_idx, token in enumerate(first_half):
                pairs.append(token + "," + second_half[t_idx])
            if line.endswith("."):
                pairs.append("<.>,<punct>")
            checked[idx] = True
        else:
            print(f"{str(idx)} {line}")
    return pairs


arg_parser = argparse.ArgumentParser()

arg_parser.add_argument("-i", type=str, required=True)
arg_parser.add_argument("-o", type=str, required=True)


if __name__ == "__main__":
    args = arg_parser.parse_args(sys.argv[1:])
    with open(args.i, "r", encoding="utf-8") as file:
        text_blob = file.read()
    lines = parse_file(text_blob)
    content = parse_lines(lines)
    with open(args.o, "w+", encoding="utf-8") as file:
        file.write("\n".join(content))
