"""Detect identity, exact-text, and near-duplicate leakage across datasets."""

import argparse
import csv
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass(frozen=True, slots=True)
class Leak:
    kind: str
    pool_id: str
    eval_id: str
    similarity: float


def normalize_text(text: str) -> str:
    """Normalize text for exact and fuzzy comparisons."""

    normalized = unicodedata.normalize("NFKC", text).casefold()
    return " ".join(re.findall(r"[a-z0-9]+", normalized))


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def find_leaks(
    pool_rows: list[dict[str, str]],
    eval_rows: list[dict[str, str]],
    threshold: float = 0.88,
) -> list[Leak]:
    """Return cross-dataset ID, exact-text, and high-similarity collisions."""

    leaks: list[Leak] = []
    eval_ids = {row["id"]: row for row in eval_rows}
    eval_texts = {normalize_text(row["text"]): row for row in eval_rows}
    blocked_pairs: set[tuple[str, str]] = set()
    for pool_row in pool_rows:
        if pool_row["id"] in eval_ids:
            eval_row = eval_ids[pool_row["id"]]
            pair = (pool_row["id"], eval_row["id"])
            blocked_pairs.add(pair)
            leaks.append(Leak("id", *pair, 1.0))
        normalized = normalize_text(pool_row["text"])
        if normalized in eval_texts:
            eval_row = eval_texts[normalized]
            pair = (pool_row["id"], eval_row["id"])
            blocked_pairs.add(pair)
            leaks.append(Leak("exact_text", *pair, 1.0))

    all_rows = [*pool_rows, *eval_rows]
    texts = [normalize_text(row["text"]) for row in all_rows]
    vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5))
    matrix = vectorizer.fit_transform(texts)
    pool_count = len(pool_rows)
    similarities = cosine_similarity(matrix[:pool_count], matrix[pool_count:])
    for pool_index, eval_index in zip(*similarities.nonzero(), strict=True):
        similarity = float(similarities[pool_index, eval_index])
        pool_id = pool_rows[pool_index]["id"]
        eval_id = eval_rows[eval_index]["id"]
        if similarity >= threshold and (pool_id, eval_id) not in blocked_pairs:
            leaks.append(Leak("near_duplicate", pool_id, eval_id, similarity))
    return sorted(
        leaks,
        key=lambda leak: (-leak.similarity, leak.pool_id, leak.eval_id),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Check pool/evaluation leakage")
    parser.add_argument("--pool", type=Path, required=True)
    parser.add_argument("--eval", type=Path, required=True)
    parser.add_argument("--threshold", type=float, default=0.88)
    args = parser.parse_args()
    leaks = find_leaks(load_rows(args.pool), load_rows(args.eval), args.threshold)
    if leaks:
        for leak in leaks:
            print(
                f"{leak.kind}: {leak.pool_id} <-> {leak.eval_id} "
                f"similarity={leak.similarity:.3f}"
            )
        raise SystemExit(f"leakage check failed with {len(leaks)} collision(s)")
    print("Leakage check passed: no cross-dataset collisions found")


if __name__ == "__main__":
    main()
