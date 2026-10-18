from scamguard.leakage import find_leaks, normalize_text


def _row(identifier: str, text: str) -> dict[str, str]:
    return {"id": identifier, "text": text}


def test_normalize_text_ignores_case_and_punctuation() -> None:
    assert normalize_text("  Urgent—PAY now! ") == "urgent pay now"


def test_leakage_finds_ids_exact_text_and_near_duplicates() -> None:
    pool = [
        _row("shared", "A separate sentence"),
        _row("pool_exact", "VERIFY your account now!"),
        _row("pool_near", "Your parcel needs a small delivery payment today"),
    ]
    evaluation = [
        _row("shared", "Completely unrelated words"),
        _row("eval_exact", "verify your account now"),
        _row("eval_near", "Your parcel needs a small delivery payment today please"),
    ]

    leaks = find_leaks(pool, evaluation, threshold=0.75)

    assert {leak.kind for leak in leaks} == {"id", "exact_text", "near_duplicate"}


def test_distinct_rows_have_no_leakage() -> None:
    assert not find_leaks(
        [_row("pool_1", "Team lunch moved to the west conference room")],
        [_row("eval_1", "Buy gift cards immediately to prevent arrest")],
    )

