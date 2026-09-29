# Model Inventory

Машиночитаемый реестр локальных моделей.

Здесь хранятся **metadata и manifests**, но не веса моделей.

Рекомендуемые поля:

| Поле | Назначение |
|---|---|
| model_id | стабильный ID |
| family | семейство |
| params | размер модели |
| format | GGUF / HF |
| quantization | Q4_K_M и т.п. |
| local_path | локальный путь |
| role | fast / general / analysis / reasoning |
| runtime | llama.cpp / transformers |
| status | registered / tested / benchmarked |
| notes | ограничения / особенности |

Реестр является источником данных для будущего Model Zoo и Router.
