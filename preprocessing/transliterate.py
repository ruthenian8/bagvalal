"""Transliterate words suppressing errors"""
import subprocess
import sys


def transliterate(word: str) -> str:
    """Transliterate a single word. Linux-only"""

    echo = subprocess.Popen(["echo", word], stdout=subprocess.PIPE)
    translit = subprocess.Popen(
        ["hfst-lookup", "../translit/kibrik-translit.hfst"],
        stdin=echo.stdout,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    out = translit.stdout.readlines()
    result = out[0].decode().split("\t")[1]
    return result


if __name__ == "__main__":
    inp = sys.stdin.readlines()
    processed = [transliterate(item) for item in inp]
    sys.stdout.write("\n".join(processed))
    sys.exit(0)
