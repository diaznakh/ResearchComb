"""MIT-licensed synthetic local benchmark; no downloads, training, or dependencies."""

import argparse
import json
from pathlib import Path


def accuracy(rows, threshold):
    if not rows:
        raise ValueError("The evaluation dataset is empty")
    if any(row["label"] not in (0, 1) for row in rows):
        raise ValueError("Labels must be binary")
    correct = sum(int(row["x"] >= threshold) == row["label"] for row in rows)
    return correct / len(rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--threshold", type=float, required=True)
    args = parser.parse_args()
    rows = json.loads((Path(__file__).parent / "data.json").read_text())
    print(json.dumps({"threshold": args.threshold, "accuracy": accuracy(rows, args.threshold), "sample_size": len(rows)}))
