from llama_cpp import Llama
import time

MODEL = r"G:\1\Vibe coding\Vibe-coding-router\DZ_18. Integration with external services\models\ministral-3b-instruct-q4\Ministral-3-3B-Instruct-2512-Q4_K_M.gguf"

print("Loading:", MODEL)

t0 = time.time()

llm = Llama(
    model_path=MODEL,
    n_ctx=4096,
    n_gpu_layers=-1,
    verbose=True,
)

print(f"Loaded in {time.time()-t0:.2f} sec")

result = llm.create_chat_completion(
    messages=[
        {
            "role": "user",
            "content": "Ответь одним предложением: что такое локальная LLM?"
        }
    ],
    temperature=0.7,
    top_p=0.9,
    max_tokens=128,
)

print()
print("ANSWER:")
print(result["choices"][0]["message"]["content"])
