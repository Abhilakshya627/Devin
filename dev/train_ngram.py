import os
import argparse
from dev.toy_ngram import NGramLM


def main():
    ap = argparse.ArgumentParser(description="Train a simple n-gram LM from local .txt files")
    ap.add_argument("data_dir", help="Folder containing .txt files for training")
    ap.add_argument("out_json", help="Output JSON path for the trained model")
    ap.add_argument("--n", type=int, default=3, help="Order of n-gram (default: 3)")
    args = ap.parse_args()

    lm = NGramLM(n=args.n)
    lm.train_from_files(args.data_dir)
    os.makedirs(os.path.dirname(os.path.abspath(args.out_json)), exist_ok=True)
    lm.save(args.out_json)
    print(f"Saved n-gram model to {args.out_json}")


if __name__ == "__main__":
    main()
