from __future__ import annotations

import argparse
import gc
import json
import random
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config.json"
OUT_PATH = ROOT / "data" / "raw_results.csv"


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def load_config() -> dict:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def gpu_memory() -> str:
    if not torch.cuda.is_available():
        return "CUDA unavailable"
    allocated = torch.cuda.memory_allocated() / 1024**3
    reserved = torch.cuda.memory_reserved() / 1024**3
    total = torch.cuda.get_device_properties(0).total_memory / 1024**3
    return f"GPU memory allocated={allocated:.2f} GB, reserved={reserved:.2f} GB, total={total:.2f} GB"


def build_prompt(tokenizer, system_prompt: str, question: str) -> str:
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question},
    ]

    try:
        if hasattr(tokenizer, "apply_chat_template") and tokenizer.chat_template:
            return tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
            )
    except Exception:
        pass

    return f"System: {system_prompt}\nUser: {question}\nAssistant:"


def load_model(model_cfg: dict):
    if not torch.cuda.is_available():
        raise RuntimeError(
            "CUDA is unavailable in PyTorch. Run SETUP_GPU.ps1 and verify the CUDA build."
        )

    model_id = model_cfg["id"]
    trust = bool(model_cfg.get("trust_remote_code", False))

    print(f"\n=== Loading {model_id} in 4-bit NF4 ===")

    try:
        tokenizer = AutoTokenizer.from_pretrained(
            model_id,
            trust_remote_code=trust,
            use_fast=True,
        )
    except Exception:
        tokenizer = AutoTokenizer.from_pretrained(
            model_id,
            trust_remote_code=trust,
            use_fast=False,
        )

    if tokenizer.pad_token_id is None:
        tokenizer.pad_token_id = tokenizer.eos_token_id

    quant_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
    )

    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        device_map="auto",
        quantization_config=quant_config,
        trust_remote_code=trust,
        low_cpu_mem_usage=True,
    )
    model.eval()

    print(gpu_memory())
    return tokenizer, model


def input_device(model):
    try:
        return model.get_input_embeddings().weight.device
    except Exception:
        return next(model.parameters()).device


def generate_once(
    tokenizer,
    model,
    prompt: str,
    temperature: float,
    top_p: float,
    max_new_tokens: int,
):
    inputs = tokenizer(prompt, return_tensors="pt")
    dev = input_device(model)
    inputs = {k: v.to(dev) for k, v in inputs.items()}

    input_tokens = int(inputs["input_ids"].shape[-1])

    torch.cuda.synchronize()
    start = time.perf_counter()

    with torch.inference_mode():
        output = model.generate(
            **inputs,
            do_sample=True,
            temperature=temperature,
            top_p=top_p,
            max_new_tokens=max_new_tokens,
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )

    torch.cuda.synchronize()
    elapsed = time.perf_counter() - start

    generated = output[0][input_tokens:]
    generated_tokens = int(generated.shape[-1])
    answer = tokenizer.decode(generated, skip_special_tokens=True).strip()
    tokens_per_sec = generated_tokens / elapsed if elapsed > 0 else 0.0

    return {
        "answer": answer,
        "latency_sec": round(elapsed, 4),
        "input_tokens": input_tokens,
        "generated_tokens": generated_tokens,
        "tokens_per_sec": round(tokens_per_sec, 3),
        "answer_chars": len(answer),
    }


def save_rows(rows: list[dict]) -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(OUT_PATH, index=False, encoding="utf-8-sig")


def select_models(cfg: dict, selected_models: list[str] | None):
    if not selected_models:
        return [m for m in cfg["models"] if m.get("enabled", False)]

    wanted = {x.lower() for x in selected_models}
    return [
        m for m in cfg["models"]
        if m["short_name"].lower() in wanted or m["id"].lower() in wanted
    ]


def main(selected_models: list[str] | None = None):
    cfg = load_config()
    seed = int(cfg.get("seed", 42))
    models = select_models(cfg, selected_models)

    if not models:
        raise SystemExit("No models selected.")

    rows = []

    for model_cfg in models:
        tokenizer = model = None
        try:
            seed_everything(seed)
            tokenizer, model = load_model(model_cfg)

            for exp in cfg["experiments"]:
                for q in cfg["questions"]:
                    seed_everything(seed)

                    prompt = build_prompt(
                        tokenizer,
                        cfg["system_prompt"],
                        q["text"],
                    )

                    print(
                        f"[{model_cfg['short_name']}] "
                        f"{exp['name']} / {q['id']} | "
                        f"T={exp['temperature']} "
                        f"P={exp['top_p']} "
                        f"N={exp['max_new_tokens']}"
                    )

                    result = generate_once(
                        tokenizer,
                        model,
                        prompt,
                        temperature=float(exp["temperature"]),
                        top_p=float(exp["top_p"]),
                        max_new_tokens=int(exp["max_new_tokens"]),
                    )

                    rows.append({
                        "model_id": model_cfg["id"],
                        "model": model_cfg["short_name"],
                        "experiment": exp["name"],
                        "question_id": q["id"],
                        "question": q["text"],
                        "temperature": exp["temperature"],
                        "top_p": exp["top_p"],
                        "max_new_tokens": exp["max_new_tokens"],
                        "seed": seed,
                        **result,
                        "error": "",
                    })
                    save_rows(rows)

        except Exception as exc:
            print(f"ERROR [{model_cfg['short_name']}]: {type(exc).__name__}: {exc}")
            rows.append({
                "model_id": model_cfg["id"],
                "model": model_cfg["short_name"],
                "experiment": "__MODEL_ERROR__",
                "question_id": "",
                "question": "",
                "temperature": None,
                "top_p": None,
                "max_new_tokens": None,
                "seed": seed,
                "answer": "",
                "latency_sec": None,
                "input_tokens": None,
                "generated_tokens": None,
                "tokens_per_sec": None,
                "answer_chars": None,
                "error": f"{type(exc).__name__}: {exc}",
            })
            save_rows(rows)

        finally:
            if model is not None:
                del model
            if tokenizer is not None:
                del tokenizer
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                print(gpu_memory())

    print(f"\nDone. Results: {OUT_PATH}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--models",
        nargs="*",
        help="Short names or HF model ids. Omit to use enabled=true in config.json.",
    )
    args = parser.parse_args()
    main(args.models)
