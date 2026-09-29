# DZ_1_Local_LLMs_First_Model

**Курс:** Local LLMs — AI University  
**Тема:** Введение в локальные LLM. Запуск первой локальной модели  
**Расширение ДЗ:** сравнение нескольких локальных LLM + интерактивный dashboard.

## Что требует ДЗ

Базовая часть сохраняет условия преподавателя:

- два одинаковых вопроса для всех запусков;
- эксперимент с `temperature`;
- эксперимент с `top_p`;
- эксперимент с `max_new_tokens`;
- сохранение всех ответов;
- анализ креативности, связности, завершённости, логической корректности,
  стабильности и негативных эффектов экстремальных значений.

## Что добавлено сверх минимума

Один и тот же эксперимент можно прогнать на нескольких моделях из урока:

1. `Qwen/Qwen1.5-7B-Chat`
2. `deepseek-ai/deepseek-llm-7b-chat`
3. `mistralai/Mistral-7B-Instruct-v0.3`
4. `IlyaGusev/saiga_llama3_8b`
5. `openchat/openchat-3.6-8b-20240522`

По умолчанию в конфигурации включены первые три. Остальные можно включить одной
галочкой в `config.json`, если хватает диска/VRAM.

## Вопросы

### Вопрос 1 — обязательный

> Напиши короткий рассказ (3–4 предложения) о том, как ты нашел загадочную записку в неожиданном месте.

### Вопрос 2 — ловушечный

> В комнате горят 5 свечей. Две свечи погасли. Сколько свечей останется к утру? Объясни ответ.

Для второго вопроса ожидаемый смысл: погасшие две свечи сохранятся, остальные три
продолжат гореть и могут сгореть. Это позволяет сравнивать не только стиль, но и
устойчивость рассуждения.

## Матрица экспериментов

| Эксперимент | Изменяем | Значения | Остальное фиксировано |
|---|---|---|---|
| Temperature | `temperature` | `0.1`, `0.7`, `1.2` | `top_p=0.9`, `max_new_tokens=128` |
| Top-p | `top_p` | `0.1`, `0.8`, `0.99` | `temperature=0.7`, `max_new_tokens=128` |
| Length | `max_new_tokens` | `64`, `128`, `512` | `temperature=0.7`, `top_p=0.9` |

Итого на одну модель: **9 конфигураций × 2 вопроса = 18 ответов**.

Для 3 моделей: **54 ответа**.  
Для 5 моделей: **90 ответов**.

## Структура

```text
DZ_1_Local_LLMs_First_Model/
├── README.md
├── config.json
├── requirements.txt
├── RUN_BENCHMARK.ps1
├── RUN_DASHBOARD.ps1
├── materials/
├── notebooks/
│   └── DZ_1_LLM_Parameter_Experiments.ipynb
├── src/
│   ├── benchmark.py
│   └── evaluator.py
├── dashboard/
│   └── app.py
├── data/
│   ├── raw_results.csv
│   └── evaluated_results.csv
├── reports/
│   └── DZ_1_Report_Template.md
└── screenshots/
```

## Быстрый запуск

```powershell
cd "G:\1\Local LLMs\DZ_1_Local_LLMs_First_Model"

python -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -r requirements.txt

.\RUN_BENCHMARK.ps1
```

После получения результатов:

```powershell
.\RUN_DASHBOARD.ps1
```

Dashboard откроется через Streamlit.

## Важное про ресурсы

7B/8B-модели тяжёлые. Не запускайте пять моделей одновременно. Стенд загружает
модели **по одной**, выполняет все эксперименты, сохраняет CSV, освобождает память
и только затем переходит к следующей модели.

Если VRAM мало, начните с одной модели, затем включайте остальные по очереди.

## Что сдавать

Минимальная часть ДЗ может быть оформлена по одной выбранной модели. Сравнение
нескольких моделей и dashboard оформляются отдельным разделом
**Bonus research: Cross-model comparison**.

Это позволяет не подменять исходные условия задания, но показать расширенное
исследование.


## Hardware profile used for this DZ

Test machine:

- GPU: NVIDIA GeForce RTX 3060 12 GB
- RAM: ~32 GB
- OS: Windows
- Strategy: one model at a time
- Quantization: 4-bit NF4 through bitsandbytes
- Compute dtype: FP16

Recommended order:

1. `SETUP_GPU.ps1`
2. `RUN_SMOKE_TEST.ps1`
3. `RUN_QWEN_ONLY.ps1`
4. Inspect CSV and GPU stability
5. `RUN_BENCHMARK.ps1` for all enabled models
6. `RUN_DASHBOARD.ps1`
