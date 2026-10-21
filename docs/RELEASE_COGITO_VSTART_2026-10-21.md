# Cogito: ступень V «Переменные и присваивание» 2026-10-21

На `https://cogito.born-in-july.ru` выкачен образ `ego-trainer:vstart-b638972`.

- База: действовавший образ `ego-trainer:ai-77e91bb` (исходники `77e91bb`;
  `ego/testing.py` и `ego/checker.py` в образе совпали с коммитом по SHA-256).
- Надстройка: заменены только `ego/testing.py` и `ego/checker.py` из `b638972`
  (опциональный `@case(hide_expected=True)`). Остальные файлы образа не менялись.
- Контент: в `/opt/cogito/content` добавлен проект `python-start`
  (папка `01_variables`, задачи V01–V13), запись в `catalog.yaml`.

## Проверки

- Кандидат на копии живого контента: 13 задач START — эталон проходит,
  заготовка нет, ожидаемое значение везде `<скрыто>`; XL-A парсится и проходит.
- Sync живого сервера: `added=13, updated=0, skipped=27, errors=0`.
- Студенты, прогресс, попытки и настройки не изменились (13 / 5 / 12 / 1);
  задач 60 → 73.
- В живом контейнере заготовка V01 даёт `failed` с `<скрыто>`; health `healthy`,
  HTTPS `/health` 200.

## Откат

Бэкапы: `/opt/cogito/releases/vstart-b638972/backup` (`ego-pre-switch.db`,
`env.bak`, `catalog.yaml.bak`). Вернуть `COGITO_IMAGE=ego-trainer:ai-77e91bb`
в `.env`, пересоздать `cogito-server` через Compose; убрать `python-start`
из `content/catalog.yaml`, если нужно скрыть задачи.

Отчёты `RELEASE_COGITO_ADMIN/DASHBOARD_2026-10-02.md` устарели: до этого релиза
на проде работал `ai-77e91bb`, а контент уже был в формате каталога
(`xl-a` включён, `junior` выключен).
