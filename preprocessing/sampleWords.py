"""Import word-annotation csv (first argument) and sample 100 random words"""
import random
import sys


def read_file(filename):
    with open(filename, "r", encoding="utf-8") as f:
        contents = f.read()
        return contents


def write_lines(lines, filename):
    with open(filename, "w+", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main(filename):
    content = read_file(filename)
    all_lines = content.splitlines()
    random.seed(42)
    chosen_lines = random.sample(all_lines, 100)
    write_lines(chosen_lines, "chosen.csv")


if __name__ == "__main__":
    file = sys.argv[1]
    main(file)
