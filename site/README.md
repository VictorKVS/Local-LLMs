# Local LLMs Course Portal

Публичная витрина курса и frontend-полигон для Makar.

## Страницы

- `index.html` — обзор курса;
- `lab.html` — локальный runtime и telemetry;
- `models.html` — Model Zoo;
- `architecture.html` — архитектура;
- `dz1.html` — ДЗ №1;
- `roadmap.html` — дальнейшее развитие.

## Локальный запуск

```powershell
cd "G:\1\Local LLMs"
python -m http.server 8080 --directory site
```

Открыть:

```text
http://127.0.0.1:8080/
```

## Screenshot mode

К любой странице добавить:

```text
?shot=1
```

Например:

```text
http://127.0.0.1:8080/dz1.html?shot=1
```

Рекомендованный viewport:

```text
1440 × 900
zoom 100%
```

## GitHub Pages

Workflow: `.github/workflows/pages.yml`.

После включения **Settings → Pages → Source: GitHub Actions** портал будет доступен по адресу:

```text
https://victorkvs.github.io/Local-LLMs/
```
