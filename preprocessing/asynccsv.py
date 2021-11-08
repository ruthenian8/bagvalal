"""Produce a csv file with analyses"""
def read_file(filename):
    with open(filename, "r", encoding="utf-8") as f:
        contents = f.read()
        return contents

def main():
    """Read some lines with tab-separated values.
    Extract to a csv document.
    """
    content = read_file("gudtexts.txt")
    file = open("analyses.csv", "w+", encoding="utf-8")
    all_lines = content.splitlines()
    for i in range(0, len(all_lines), 2):
        line1, line2 = all_lines[i].split("\t"), all_lines[i+1].split("\t")
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

if __name__ == "__main__":
    main()