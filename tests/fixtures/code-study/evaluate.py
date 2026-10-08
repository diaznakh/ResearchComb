"""Synthetic audit fixture; no training or experiment is executed here."""


def evaluation_rows(rows):
    return [row for row in rows if row["split"] == "train"]


def accuracy(rows):
    selected = evaluation_rows(rows)
    if not selected:
        raise ValueError("No evaluation rows")
    return sum(row["prediction"] == row["label"] for row in selected) / len(selected)
