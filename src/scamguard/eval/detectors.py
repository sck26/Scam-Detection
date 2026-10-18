"""Reference detector implementations."""

import csv
import random
from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import cast

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

from scamguard.taxonomy import DangerLevel, TacticName


@dataclass(frozen=True, slots=True)
class Prediction:
    """One detector result."""

    danger_level: DangerLevel
    score: float
    tactics: tuple[TacticName, ...] = ()


class Detector(ABC):
    """Interface implemented by every evaluation detector."""

    name: str

    @abstractmethod
    def predict(self, texts: Sequence[str]) -> list[Prediction]:
        """Predict one result per input text."""


class AlwaysScamDetector(Detector):
    """Upper-recall, zero-discrimination sanity check."""

    name = "always_scam"

    def predict(self, texts: Sequence[str]) -> list[Prediction]:
        return [Prediction(DangerLevel.DANGEROUS, 1.0) for _ in texts]


class RandomDetector(Detector):
    """Deterministic random-score sanity check."""

    name = "random_seed_0"

    def predict(self, texts: Sequence[str]) -> list[Prediction]:
        generator = random.Random(0)
        results: list[Prediction] = []
        for _ in texts:
            score = generator.random()
            level = DangerLevel.DANGEROUS if score >= 0.5 else DangerLevel.SAFE
            results.append(Prediction(level, score))
        return results


def load_public_training_data(directory: Path) -> tuple[list[str], list[int]]:
    """Load every normalized public-data CSV, excluding evaluation data."""

    texts: list[str] = []
    labels: list[int] = []
    for path in sorted(directory.glob("*.csv")):
        with path.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            required = {"text", "label"}
            if not reader.fieldnames or not required.issubset(reader.fieldnames):
                continue
            for row in reader:
                if row["label"] not in {"scam", "legit"} or not row["text"].strip():
                    continue
                texts.append(row["text"])
                labels.append(1 if row["label"] == "scam" else 0)
    if not texts:
        raise FileNotFoundError(
            f"no normalized public training data found in {directory}; run make data"
        )
    if set(labels) != {0, 1}:
        raise ValueError("public training data must contain scam and legit labels")
    return texts, labels


class TfidfLogisticDetector(Detector):
    """Word/character TF-IDF with logistic regression."""

    name = "tfidf_logistic_regression"

    def __init__(self, training_directory: Path) -> None:
        texts, labels = load_public_training_data(training_directory)
        self.training_examples = len(texts)
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            ngram_range=(1, 2),
            min_df=2,
            max_features=50_000,
            sublinear_tf=True,
        )
        matrix = self.vectorizer.fit_transform(texts)
        self.classifier = LogisticRegression(
            max_iter=1_000,
            class_weight="balanced",
            random_state=0,
        )
        self.classifier.fit(matrix, labels)

    def predict(self, texts: Sequence[str]) -> list[Prediction]:
        matrix = self.vectorizer.transform(texts)
        probabilities = self.classifier.predict_proba(matrix)
        raw_scores = cast(
            np.ndarray[tuple[int], np.dtype[np.float64]], probabilities[:, 1]
        )
        results: list[Prediction] = []
        for raw_score in raw_scores:
            score = float(raw_score)
            if score >= 0.5:
                level = DangerLevel.DANGEROUS
            elif score >= 0.35:
                level = DangerLevel.SUSPICIOUS
            else:
                level = DangerLevel.SAFE
            results.append(Prediction(level, score))
        return results
