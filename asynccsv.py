"""Produce a csv file with analyses"""
import sys
import argparse

def read_file(filename):
    with open(filename, "r", encoding="utf-8") as f:
        contents = f.read()
        return contents


def main(input_file: str, output_file: str):
    """
    Read some lines with tab-separated values.
    Extract to a csv document.
    """
    content = read_file(input_file)
    file = open(output_file, "w+", encoding="utf-8")
    all_lines = content.splitlines()
    for i in range(0, len(all_lines), 2):
        line1, line2 = all_lines[i].split("\t"), all_lines[i + 1].split("\t")
        try:
            assert len(line1) == len(line2)
        except AssertionError:
            print("Incorrect pair:")
            print(line1)
            print(line2)
            continue
        for item, item2 in zip(line1, line2):
            file.write(item + "," + item2 + "\n")
    file.close()


parser = argparse.ArgumentParser()
parser.add_argument("--input_file", type="str", required=True)
parser.add_argument("--output_file", type="str", required=True)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Target files should be passed as parameters.")
        sys.exit(1)
    parser.parse_args(sys.argv[1:])
    main(parser.input_file, parser.output_file)
