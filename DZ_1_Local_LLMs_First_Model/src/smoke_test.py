from __future__ import annotations

import gc
import json
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

ROOT = Path(__file__).resolve().parents[1]
cfg = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
m = next(x for x in cfg["models"] if x["short_name"] == "Qwen1.5-7B")
model_id = m["id"]

if not torch.cuda.is_available():
    raise SystemExit("CUDA unavailable. Run SETUP_GPU.ps1 first.")

print("GPU:", torch.cuda.get_device_name(0))
print("PyTorch CUDA:", torch.version.cuda)
print("Model:", model_id)

tokenizer = AutoTokenizer.from_pretrained(
    model_id,
    trust_remote_code=bool(m.get("trust_remote_code", False)),
)

if tokenizer.pad_token_id is None:
    tokenizer.pad_token_id = tokenizer.eos_token_id

qconfig = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
)

model = AutoModelForCausalLM.from_pretrained(
    model_id,
    device_map="auto",
    quantization_config=qconfig,
    trust_remote_code=bool(m.get("trust_remote_code", False)),
    low_cpu_mem_usage=True,
)
model.eval()

question = "Ответь одним предложением: что такое локальная LLM?"
messages = [
    {"role": "system", "content": cfg["system_prompt"]},
    {"role": "user", "content": question},
]

try:
    prompt = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
except Exception:
    prompt = f"System: {cfg['system_prompt']}\nUser: {question}\nAssistant:"

inputs = tokenizer(prompt, return_tensors="pt")
dev = model.get_input_embeddings().weight.device
inputs = {k: v.to(dev) for k, v in inputs.items()}

with torch.inference_mode():
    out = model.generate(
        **inputs,
        do_sample=True,
        temperature=0.7,
        top_p=0.9,
        max_new_tokens=64,
        pad_token_id=tokenizer.pad_token_id,
        eos_token_id=tokenizer.eos_token_id,
    )

new_tokens = out[0][inputs["input_ids"].shape[-1]:]
answer = tokenizer.decode(new_tokens, skip_special_tokens=True).strip()

print("")
print("=== SMOKE TEST ANSWER ===")
print(answer)
print("")
print("GPU allocated GB:", round(torch.cuda.memory_allocated()/1024**3, 2))
print("GPU reserved GB:", round(torch.cuda.memory_reserved()/1024**3, 2))
print("SMOKE TEST: OK")

del model, tokenizer
gc.collect()
torch.cuda.empty_cache()
