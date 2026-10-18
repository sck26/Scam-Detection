from pathlib import Path

import pytest

from scamguard.distill import _smoke_onnx


def test_exported_student_scores_a_sample() -> None:
    pytest.importorskip("onnxruntime")
    model = Path("artifacts/student/student.onnx")
    if not model.exists():
        pytest.skip("student export has not been generated")

    probabilities = _smoke_onnx(model)

    assert len(probabilities) == 2
    assert sum(probabilities) == pytest.approx(1.0, abs=1e-5)


def test_exported_coreml_head_scores_a_vector() -> None:
    pytest.importorskip("coremltools")
    import coremltools as ct
    import numpy as np

    model_path = Path("artifacts/student/student-linear.mlmodel")
    if not model_path.exists():
        pytest.skip("Core ML linear head has not been generated")
    try:
        model = ct.models.MLModel(str(model_path))
        output = model.predict({"tfidf": np.zeros(1650, dtype=np.float64)})
    except RuntimeError as error:
        pytest.skip(f"Core ML runtime unavailable: {error}")

    assert float(output["scam_probability"][0]) == pytest.approx(0.5611003)
