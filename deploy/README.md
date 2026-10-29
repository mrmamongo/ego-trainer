# Выкатка Cogito на прод

`deploy/release.py` — единственный поддерживаемый способ выкатить Cogito на боевой
сервер. Скрипт рассчитан на запуск **на самом сервере** (root `/opt/cogito`), нужен
только `python3` из стандартной библиотеки — ни `uv`, ни зависимостей проекта.

Ручной рецепт с `docker tag` / `docker push` / правкой `.env` из
[DEPLOYMENT.md](../docs/DEPLOYMENT.md#реестр-образов-и-откат-с-2026-10-24) остаётся
описанием отката «руками»; обычная выкатка идёт через этот скрипт.

## Что скрипт делает

1. **Блокировка.** Захватывает `/opt/cogito/releases/.lock` (`O_EXCL`); вторая
   параллельная выкатка завершается с кодом 3. Lock снимается в `finally` — даже
   при падении и Ctrl-C (там же останавливается и удаляется временный контейнер).
2. **Предусловия.** Проверяет, что на месте `.env`, `data/ego.db`, `content/`,
   `compose.yaml`, и что запущенный контейнер `cogito-cogito-server-1` использует
   ровно образ `--expect-current`. Если там другой образ — прерывается и печатает,
   что реально запущено (значит, `--expect-current` устарел или кто-то уже выкатил).
3. **Кандидат.** Поднимает новый образ (или новый контент) одноразовым контейнером
   `rel-candidate` на порту 18099 поверх **копий** живой БД (через SQLite backup API,
   без блокировки живого файла), `content/` и `data/extension`. Внутри прогоняет
   `ego-server admin sync-tasks` и проверяет:
   - `/health` → 200;
   - страницы `/`, `/panel`, `/ide`, `/student` → 200;
   - каждый `/static`-ассет, на который ссылаются эти страницы, → 200;
   - в `/static/student.css` есть `[data-theme="dark"]` (маркер тёмной темы;
     отключается `--no-dark-theme-check`);
   - счётчики students / progress / runs / service_settings не изменились;
   - число progress-строк со статусом `stale` не изменилось (sync не должен
     инвалидировать прогресс учеников);
   - счётчики каталога (`lessons`, `start_tasks`, …) на месте, а те, что заданы
     через `--expect key=value`, имеют ожидаемое значение.
4. **Бэкап.** `/opt/cogito/releases/<name>/backup/`: `ego-pre-release.db` (снимок
   через backup API), `env.bak`, заменяемые каталоги `content/<project>/`, при
   публикации расширения — `extension/`.
5. **Переключение.** Меняет `COGITO_IMAGE` в `.env` (атомарно: `.env.release-tmp` →
   rename), `docker compose up -d --no-deps cogito-server`, ждёт `/health` (до 60 с).
   Если контейнер не поднялся — откат.
6. **Проверки на живом порту.** Те же проверки (health, страницы, ассеты, тема,
   счётчики), плюс повторный `sync-tasks`. Любое расхождение — откат.
7. **Реестр.** Тегирует образ, который работал, как
   `git.born-in-july.ru/mrmamongo/cogito:<name>` и `...:v<name>`, пушит оба.
   Если задан `--publish-vsix`: кладёт файл в `/opt/cogito/data/incoming/<name>/cogito.vsix` (в контейнере это `/var/lib/ego/incoming/<name>/`),
   публикует через `ego-server admin publish-extension` и проверяет
   `/extension/latest`.
8. **Уборка.** Удаляет из локального стора все образы `ego-trainer:*` и `registry:*`,
   кроме работающего, плюс `docker image prune` и `docker builder prune`, печатает
   `df -h`. В конце — `DEPLOY OK`.

Откат при ошибке на шагах 5–6: возвращает `.env`, восстанавливает содержимое
каталогов из бэкапа, `compose up` и повторный `sync-tasks`. Если откат не удался,
печатается `ROLLBACK INCOMPLETE` — дальше вручную по
[DEPLOYMENT.md](../docs/DEPLOYMENT.md#реестр-образов-и-откат-с-2026-10-24).

Коды выхода: `0` — успех, `1` — прервано (с откатом, если уже переключались),
`2` — ошибка конфигурации, `3` — занят lock, `130` — прервано сигналом.

## Подготовка

### Образ

Гигиена обязательна: **образ собирается только из чистого checkout** — без
незакоммиченных правок в рабочей копии. Иначе на проде окажется код, которого нет
в git, и выкатку потом не воспроизвести.

```bash
# на машине сборки, в чистом checkout нужного коммита
git status --porcelain   # MUST be empty
docker build -t ego-trainer:<name> .
docker tag ego-trainer:<name> git.born-in-july.ru/mrmamongo/cogito:<name>
docker push git.born-in-july.ru/mrmamongo/cogito:<name>
```

Либо переиспользуйте уже опубликованный образ релиза:

```bash
# на сервере
docker pull git.born-in-july.ru/mrmamongo/cogito:<name>
docker tag  git.born-in-july.ru/mrmamongo/cogito:<name> ego-trainer:<name>
```

`--image` должен указывать на локально существующий образ (скрипт проверяет это
до любых изменений).

### Контент

Контент (каталог `ego-tasks`, ADR-0016) пакуется из того же чистого checkout:

```bash
git archive --format=tar.gz -o /tmp/content-<name>.tar.gz HEAD python-start/
scp /tmp/content-<name>.tar.gz server:/opt/cogito/incoming/
ssh server 'mkdir -p /opt/cogito/incoming/<name> && tar -xzf /opt/cogito/incoming/content-<name>.tar.gz -C /opt/cogito/incoming/<name>'
```

Каждый `--content PROJECT=DIR` целиком заменяет `/opt/cogito/content/projects/PROJECT`
(старый каталог сохраняется в бэкапе).

### Расширение VS Code (по желанию)

```bash
cd vscode-ego && npx @vscode/vsce package --allow-missing-repository
scp ego-trainer-<version>.vsix server:/opt/cogito/incoming/<name>/cogito-<version>.vsix  # --publish-vsix скопирует его в data/incoming
```

## Запуск

Сначала — план, без изменений (`--dry-run` ничего не выполняет и не пишет):

```bash
cd /opt/cogito && python3 release.py --dry-run --config release.json
```

Затем — реальная выкатка:

```bash
cd /opt/cogito
python3 release.py \
  --name release-abc1234 \
  --image ego-trainer:release-abc1234 \
  --expect-current ego-trainer:61f3a2b \
  --content python-start=/opt/cogito/incoming/release-abc1234/python-start \
  --expect start_tasks=239 --expect lessons=71
```

Только контент (образ не меняется, тегируется работающий):

```bash
python3 release.py \
  --name content-f610d0b \
  --content xl-a=/opt/cogito/incoming/content-f610d0b/xl-a \
  --expect-current ego-trainer:release-8bc6212
```

Вариант через JSON (ключи `name`, `image`, `content`, `expect_current`, `expect`,
`publish_vsix`, `notes`); флаги командной строки важнее файла:

```json
{
  "name": "release-abc1234",
  "image": "ego-trainer:release-abc1234",
  "content": {"python-start": "/opt/cogito/incoming/release-abc1234/python-start"},
  "expect_current": "ego-trainer:61f3a2b",
  "expect": {"start_tasks": 239, "lessons": 71},
  "publish_vsix": "/opt/cogito/incoming/release-abc1234/cogito.vsix",
  "notes": "catalog: project folders"
}
```

`--expect-current` берите из текущего `COGITO_IMAGE` в `/opt/cogito/.env`; если он
не совпадает с реально запущенным образом, скрипт остановится и напечатает
актуальное значение.

## Откат

- **Автоматически** — при неудачной проверке после переключения (см. выше).
- **Вручную** — по [DEPLOYMENT.md](../docs/DEPLOYMENT.md#реестр-образов-и-откат-с-2026-10-24):
  `docker pull` нужного тега из реестра, `COGITO_IMAGE` в `.env`, `compose up`.
- Данные откатывать не нужно: миграции только добавляют таблицы и колонки. Снимок
  БД до выкатки — `releases/<name>/backup/ego-pre-release.db`; старый контент —
  `releases/<name>/backup/content/<project>/`.

## От чего защищает каждая проверка

| Проверка | Что ловит |
|---|---|
| Lock-файл | две параллельные выкатки, одновременно правящие `.env` |
| `--expect-current` | выкатку поверх чужой, уже случившейся выкатки |
| Кандидат на копии БД | падение/ошибки новой версии — до того, как затронут прод |
| `/health` 200 | незапустившийся сервер (битый образ, конфликт порта) |
| Страницы `/`, `/panel`, `/ide`, `/student` | сломанный рендер, отсутствующий роутер |
| Все `/static`-ассеты | забытые при сборке или переименованные статические файлы |
| `[data-theme="dark"]` | регресс темы/стилей, который руками почти не заметен |
| Счётчики students/progress/runs/service_settings | миграция или sync, затронувшие пользовательские данные |
| Счётчик `stale` | sync, массово инвалидировавший прогресс учеников |
| `--expect` по каталогу | неполный или перепутанный контент (не тот коммит/каталог) |
| Бэкап перед переключением | потерю данных при откате |
| Откат `.env` + контента | «сломанный прод», который нельзя вернуть одной командой |
| Уборка образов | переполнение диска сервера старыми образами |

## Тесты

Чистые части инструмента покрыты юнит-тестами без Docker
(`tests/test_deploy_release.py`): разбор ссылок на ассеты из HTML, сравнение
счётчиков, подмена `COGITO_IMAGE` в `.env`, разбор конфигурации, поведение lock-файла.

```bash
uv run --all-extras pytest -q tests/test_deploy_release.py
```
