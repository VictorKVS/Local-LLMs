from __future__ import annotations

import re
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw_results.csv"
OUT = ROOT / "data" / "evaluated_results.csv"


def sentence_count(text: str) -> int:
    parts = [x.strip() for x in re.split(r"[.!?]+", str(text)) if x.strip()]
    return len(parts)


def trap_score(answer: str) -> int:
    """
    Простая автоматическая метрика только для нашего Q2.
    1 = ответ улавливает смысл, что две погасшие свечи останутся.
    0 = иначе.

    Это не заменяет человеческую оценку.
    """
    t = str(answer).lower()
    mentions_two = bool(re.search(r"\b2\b|две|два", t))
    reasoning = any(x in t for x in ["погас", "сгор", "остан", "догор"])
    return int(mentions_two and reasoning)


def main():
    if not RAW.exists():
        raise SystemExit(f"Нет файла {RAW}. Сначала запустите benchmark.py")

    df = pd.read_csv(RAW)
    if "answer" not in df.columns:
        raise SystemExit("В CSV нет колонки answer.")

    df["sentence_count"] = df["answer"].fillna("").map(sentence_count)
    df["story_3_4_sentences"] = (
        (df["question_id"] == "Q1_story")
        & df["sentence_count"].between(3, 4)
    ).astype(int)

    df["trap_logic_auto"] = 0
    mask = df["question_id"] == "Q2_trap"
    df.loc[mask, "trap_logic_auto"] = (
        df.loc[mask, "answer"].fillna("").map(trap_score)
    )

    # Поля для ручной оценки преподавателем/студентом.
    for col in [
        "manual_creativity_1_5",
        "manual_coherence_1_5",
        "manual_instruction_1_5",
        "manual_logic_1_5",
        "manual_notes",
    ]:
        if col not in df.columns:
            df[col] = ""

    df.to_csv(OUT, index=False, encoding="utf-8-sig")
    print(f"Saved: {OUT}")


if __name__ == "__main__":
    main()
