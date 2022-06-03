import sys
import re
import argparse
import pickle
from functools import partial

from gensim.models import FastText
import sklearn_crfsuite
from sklearn_crfsuite import metrics


def token_to_features(word: str, vector_model: object) -> dict:
    vector = vector_model.wv[word]
    features = dict()
    for idx, item in enumerate(vector):
        features[f"feat_{str(idx)}"] = item
    return features


def read_data(filename: str) -> list:
    with open(filename, "r", encoding="utf-8") as file:
        data = file.read().splitlines()
    # debug_set = set()
    sequences = []
    for line in data:
        morphs, glosses = line.split(",")
        morph_tokens = list(map(ascii, re.split(r"[=-]", morphs)))
        gloss_tokens = list(map(ascii, re.split(r"[=-]", glosses)))
        if not len(morph_tokens) == len(gloss_tokens):
            continue
        for idx in range(len(gloss_tokens)):
            if re.match(r"[А-Яа-яё]+", gloss_tokens[idx]):
                gloss_tokens[idx] = "<root>"
        # debug_set.update(set(morph_tokens))
        sequences.append({"tokens": morph_tokens, "glosses": gloss_tokens})
    # print(len(debug_set))
    return sequences


def load_models(vector_path: str, crf_path: str):
    vector_model = FastText.load(vector_path)
    with open(crf_path, "rb") as file:
        crf_model = pickle.load(file)
    return vector_model, crf_model


def train_models(
    data: object,
    vector_size: int = 256,
    vector_epochs: int = 12,
    crf_iterations: int = 100,
    vector_model: object = None
):
    if vector_model is None:
        vector_model = FastText(
            vector_size=vector_size,
            window=3,
            min_count=1,
            max_vocab_size=1500
        )
        tokens = [item["tokens"] for item in data]
        num_tokens = 0
        for t in tokens:
            num_tokens += len(t)
        
        vector_model.build_vocab(tokens)
        vector_model.train(
            corpus_iterable=tokens,
            total_words=num_tokens,
            epochs=vector_epochs
        )

    glosses = [item["glosses"] for item in data]
    morph_to_features = partial(token_to_features, vector_model=vector_model)
    
    vectorized_tokens = [
        list(map(morph_to_features, item)) for item in tokens
    ]
    
    crf_model = sklearn_crfsuite.CRF(
        algorithm='lbfgs',
        c1=0.1,
        c2=0.1,
        max_iterations=crf_iterations,
    )
    crf_model.fit(vectorized_tokens, glosses)    
    return vector_model, crf_model


def test_models(vector_model: object, crf_model: object, data: list):
    morph_to_features = partial(token_to_features, vector_model=vector_model)
    tokens = [item["tokens"] for item in data]
    glosses = [item["glosses"] for item in data]
    vectorized_tokens = [
        list(map(morph_to_features, item)) for item in tokens
    ]
    try:
        print(f"vector size: {str(vectorized_tokens[0][0].size)}")
        print(f"vector size: {str(len(vectorized_tokens[0][0]))}")
    except Exception:
        pass
    pred_glosses = crf_model.predict(vectorized_tokens)
    f1_metric = metrics.flat_f1_score(glosses, pred_glosses,
        average='weighted', labels=list(crf_model.classes_))
    return f1_metric


def main(args: object):
    test_data = read_data(args.test_file)
    # sys.exit(0)
    if args.train_file:
        train_data = read_data(args.train_file)
        if args.vector_load_path:
            vector_model = FastText.load(args.vector_load_path)
        else:
            vector_model = None
        vector_model, crf_model = train_models(
            data=train_data,
            vector_size=args.vector_size,
            vector_epochs=args.vector_epochs,
            crf_iterations=args.crf_iterations,
            vector_model=vector_model
        )
    else:
        vector_model, crf_model = load_models(args.vector_load_path, args.model_load_path)
    print("Training complete, starting inference")
    vector_model.save(args.vector_save_path)
    with open(args.model_save_path, "wb+") as file:
        pickle.dump(crf_model, file)    
    f1_score = test_models(vector_model, crf_model, test_data)
    message = """
    Vector size: {}
    Vector training epochs: {}
    CRF iterations: {}
    ---
    F-1 score: {}
    """.format(
        str(args.vector_size), str(args.vector_epochs), str(args.crf_iterations), str(f1_score)
    )
    if args.results_file:
        with open(args.results_file, "w+", encoding="utf-8") as file:
            file.write(message)
    else:
        print(message)
    sys.exit(1)


parser = argparse.ArgumentParser()

parser.add_argument("--model_save_path", type=str, required=True, help="Path to save the CRF model to.")
parser.add_argument("--vector_save_path", type=str, required=True, help="Path to save the trained vectors to.")

parser.add_argument("--model_load_path", type=str, required=False, help="Path to load the CRF model from.")
parser.add_argument("--vector_load_path", type=str, required=False, help="Path to load the trained vectors from.")
parser.add_argument("--train_file", type=str, required=False, help="CSV file with training data.")

parser.add_argument("--test_file", type=str, required=True, help="CSV file with testing data")
parser.add_argument("--vector_size", type=int, required=False, default=256)
parser.add_argument("--vector_epochs", type=int, required=False, default=12)
parser.add_argument("--crf_iterations", type=str, default=100, required=False)
parser.add_argument("--results_file", type=str, required=False)

if __name__ == "__main__":
    args = parser.parse_args(sys.argv[1:])
    print(args)
    main(args=args)