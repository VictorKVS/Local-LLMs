from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
EVAL = ROOT / "data" / "evaluated_results.csv"
RAW = ROOT / "data" / "raw_results.csv"

st.set_page_config(
    page_title="Local LLM Benchmark — DZ 1",
    layout="wide",
)

st.title("Local LLM Benchmark — DZ 1")
st.caption("Сравнение моделей и влияния temperature / top_p / max_new_tokens")

path = EVAL if EVAL.exists() else RAW
if not path.exists():
    st.warning("Результатов пока нет. Сначала запустите RUN_BENCHMARK.ps1.")
    st.stop()

df = pd.read_csv(path)
df = df[df["experiment"] != "__MODEL_ERROR__"].copy()

models = sorted(df["model"].dropna().unique().tolist())
questions = sorted(df["question_id"].dropna().unique().tolist())

c1, c2 = st.columns(2)
selected_models = c1.multiselect("Models", models, default=models)
selected_questions = c2.multiselect("Questions", questions, default=questions)

f = df[
    df["model"].isin(selected_models)
    & df["question_id"].isin(selected_questions)
].copy()

if f.empty:
    st.info("Нет данных для выбранных фильтров.")
    st.stop()

a, b, c, d = st.columns(4)
a.metric("Runs", len(f))
b.metric("Models", f["model"].nunique())
c.metric("Avg latency, sec", f["latency_sec"].mean().round(2))
d.metric("Avg tokens/sec", f["tokens_per_sec"].mean().round(2))

st.subheader("Скорость моделей")
speed = (
    f.groupby("model", as_index=False)
     .agg(latency_sec=("latency_sec", "mean"),
          tokens_per_sec=("tokens_per_sec", "mean"))
)
st.plotly_chart(
    px.bar(speed, x="model", y="tokens_per_sec",
           hover_data=["latency_sec"],
           title="Средняя скорость генерации, tokens/sec"),
    use_container_width=True,
)

st.subheader("Влияние temperature")
temp = f[
    f["experiment"].isin(
        ["temperature_low", "temperature_mid", "temperature_high"]
    )
].copy()
if not temp.empty:
    st.plotly_chart(
        px.line(
            temp,
            x="temperature",
            y="answer_chars",
            color="model",
            markers=True,
            facet_col="question_id",
            title="Длина ответа при разных temperature",
        ),
        use_container_width=True,
    )

st.subheader("Влияние top_p")
tp = f[
    f["experiment"].isin(["top_p_low", "top_p_mid", "top_p_high"])
].copy()
if not tp.empty:
    st.plotly_chart(
        px.line(
            tp,
            x="top_p",
            y="answer_chars",
            color="model",
            markers=True,
            facet_col="question_id",
            title="Длина ответа при разных top_p",
        ),
        use_container_width=True,
    )

st.subheader("Влияние max_new_tokens")
mt = f[
    f["experiment"].isin(["tokens_short", "tokens_mid", "tokens_long"])
].copy()
if not mt.empty:
    st.plotly_chart(
        px.line(
            mt,
            x="max_new_tokens",
            y="generated_tokens",
            color="model",
            markers=True,
            facet_col="question_id",
            title="Фактически сгенерированные токены",
        ),
        use_container_width=True,
    )

if "story_3_4_sentences" in f.columns:
    st.subheader("Следование требованию 3–4 предложения")
    story = f[f["question_id"] == "Q1_story"].copy()
    if not story.empty:
        score = story.groupby("model", as_index=False)["story_3_4_sentences"].mean()
        st.plotly_chart(
            px.bar(
                score,
                x="model",
                y="story_3_4_sentences",
                title="Доля ответов, где рассказ содержит 3–4 предложения",
            ),
            use_container_width=True,
        )

if "trap_logic_auto" in f.columns:
    st.subheader("Ловушечный вопрос — автоматический индикатор")
    trap = f[f["question_id"] == "Q2_trap"].copy()
    if not trap.empty:
        score = trap.groupby("model", as_index=False)["trap_logic_auto"].mean()
        st.plotly_chart(
            px.bar(
                score,
                x="model",
                y="trap_logic_auto",
                title="Доля ответов, уловивших ожидаемую логику Q2",
            ),
            use_container_width=True,
        )

manual_cols = [
    c for c in [
        "manual_creativity_1_5",
        "manual_coherence_1_5",
        "manual_instruction_1_5",
        "manual_logic_1_5",
    ] if c in f.columns
]
for c in manual_cols:
    f[c] = pd.to_numeric(f[c], errors="coerce")

if manual_cols and f[manual_cols].notna().any().any():
    st.subheader("Ручные оценки")
    long = f.melt(
        id_vars=["model"],
        value_vars=manual_cols,
        var_name="metric",
        value_name="score",
    ).dropna()
    if not long.empty:
        agg = long.groupby(["model", "metric"], as_index=False)["score"].mean()
        st.plotly_chart(
            px.bar(
                agg,
                x="model",
                y="score",
                color="metric",
                barmode="group",
                range_y=[0, 5],
            ),
            use_container_width=True,
        )

st.subheader("Все ответы")
show_cols = [
    "model", "experiment", "question_id",
    "temperature", "top_p", "max_new_tokens",
    "latency_sec", "generated_tokens", "tokens_per_sec", "answer"
]
show_cols = [c for c in show_cols if c in f.columns]
st.dataframe(f[show_cols], use_container_width=True, height=520)

csv = f.to_csv(index=False).encode("utf-8-sig")
st.download_button(
    "Скачать отфильтрованные результаты CSV",
    csv,
    "local_llm_filtered_results.csv",
    "text/csv",
)
