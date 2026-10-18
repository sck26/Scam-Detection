"""Deterministic development/held-out splitting for the committed eval set."""

import random
from collections import defaultdict
from collections.abc import Sequence
from math import floor

Row = dict[str, str]


def _allocated_counts(group_sizes: dict[str, int], target: int) -> dict[str, int]:
    counts = {name: floor(size * 0.6) for name, size in group_sizes.items()}
    remaining = target - sum(counts.values())
    ranked = sorted(
        group_sizes,
        key=lambda name: ((group_sizes[name] * 0.6) % 1, name),
        reverse=True,
    )
    for name in ranked[:remaining]:
        counts[name] += 1
    return counts


def stratified_split(
    rows: Sequence[Row], seed: int = 20261017
) -> tuple[list[Row], list[Row]]:
    """Split 60/40 while preserving label, category, and channel marginals."""

    generator = random.Random(seed)
    by_label: defaultdict[str, list[Row]] = defaultdict(list)
    for row in rows:
        by_label[row["label"]].append(dict(row))

    development: list[Row] = []
    test: list[Row] = []
    for label, label_rows in sorted(by_label.items()):
        grouping_field = "scam_category" if label == "scam" else "channel"
        groups: defaultdict[str, list[Row]] = defaultdict(list)
        for row in label_rows:
            groups[row[grouping_field]].append(row)
        target = round(len(label_rows) * 0.6)
        counts = _allocated_counts(
            {name: len(group) for name, group in groups.items()}, target
        )
        for name, group in sorted(groups.items()):
            generator.shuffle(group)
            development.extend(group[: counts[name]])
            test.extend(group[counts[name] :])

    generator.shuffle(development)
    generator.shuffle(test)
    return development, test

