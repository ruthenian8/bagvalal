import re
import os
import subprocess
import sys
import argparse


def transducer_lookup(target_transducer: str, request_text: str):
    target_transducer_file = target_transducer
    echo_process = subprocess.Popen(
        ["echo", request_text],
        stdout=subprocess.PIPE
    )
    ana_process = subprocess.run(
        ["hfst-lookup", target_transducer_file],
        stdin=echo_process.stdout,
        capture_output=True
    )
    returncode = ana_process.returncode
    response_text = ana_process.stdout
    return returncode, response_text 


def main(args: argparse.Namespace):
    counter = {
        "correct": 0,
        "no_translation": 0,
        "incorrect": 0
    }
    
    buffer = open(args.i, "r", encoding="utf-8")
    for idx, line in enumerate(buffer):
        surface_form, glosses = line.split(",")
        _, parsed = transducer_lookup(args.analyzer, surface_form)
        parsing_options = parsed.decode("utf-8").split("\n")
        _, transformed_glosses = transducer_lookup(args.gloss_corrector, glosses)
        transformed_glosses = transformed_glosses.decode("utf-8")
        
        gloss_chains = re.findall(r'<[^а-яёЁйЙА-Я]+>', transformed_glosses)
        translation = x.group() if (x := re.search(r"[а-яёЁйЙА-Я]+", transformed_glosses)) else "NaN"
        correctly_glossed = list(filter(
            lambda x: all([i in x for i in gloss_chains]),
            parsing_options
        ))
        if not correctly_glossed:
            counter["incorrect"] += 1
            continue
        correctly_translated = list(filter(
            lambda x: translation in x,
            correctly_glossed
        ))
        if correctly_translated:
            counter["correct"] += 1
            continue
        counter["no_translation"] += 1

    buffer.close()
    return counter


parser = argparse.ArgumentParser()

parser.add_argument("-i", type=str, required=True)
parser.add_argument("-o", type=str, required=False)
parser.add_argument("--gloss_corrector", default="../bilingual/merged.tr.bag_rus.hfst")
parser.add_argument("--analyzer", default="gloss_mapping.hfst")

if __name__ == "__main__":
    args = parser.parse_args(sys.argv[1:])
    result = main(args)
    if args.o:
        with open(args.o, "w+", encoding="utf-8") as file:
            file.write("\n".join(result.items()))
    else:
        print(result)