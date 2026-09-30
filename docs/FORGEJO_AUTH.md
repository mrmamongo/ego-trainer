# Вход через Forgejo

Принятые правила: все пользователи входят через наш Forgejo
`https://git.born-in-july.ru`; новый аккаунт получает `student`.
Роли принадлежат ego-trainer. Только действующий `mentor` может повысить
`student` до `mentor` через панель пользователей. `admin` управляет сервисом
и другими ролями, но не назначает наставников через HTTP. Первого наставника
создаёт оператор через доверенную серверную CLI.

## Поток входа

Сервер использует OAuth2 Authorization Code с S256 PKCE и confidential client.
Личность получает из `/login/oauth/userinfo` по HTTPS, используя выданный
Forgejo access token. Непроверенные claims из ID token не используются.
Forgejo access/refresh tokens не сохраняются и не передаются клиенту.
OAuth scopes в Forgejo пока не ограничивают полномочия токена: `openid profile`
выражает назначение запроса, но не является границей доступа.
Источник: [Forgejo OAuth2 provider](https://forgejo.org/docs/latest/user/authentication/oauth2-provider/).

`GET /auth/providers` сообщает доступные способы входа.
`POST /auth/forgejo/start` принимает клиентский PKCE challenge.
Клиент открывает возвращённый адрес `/auth/forgejo/authorize`: сервер создаёт
HttpOnly SameSite=Lax cookie и перенаправляет браузер в Forgejo.
Callback проверяет state, cookie и однократность запроса, обменивает code
и связывает подтверждённый `(issuer, sub)` с локальным пользователем.

После callback клиенту нужны две независимые проверки: его исходный verifier
и одноразовый ticket завершения. В админке ticket передаётся через
BroadcastChannel той же browser origin; для VSCode — на временный локальный
HTTP listener `127.0.0.1`. Callback никогда не перенаправляет на произвольный
клиентский URL. Пересылка ссылки входа другому человеку не позволяет удалённому
инициатору получить его токен.

`POST /auth/forgejo/exchange` выдаёт обычный ego JWT после обеих проверок.
Срок попытки — 5 минут; завершённая попытка потребляется атомарно.
Состояние хранится в SQLite и совместимо с несколькими server workers.
Новые таблицы добавляются при обычной миграции; существующий прогресс сохраняется.

Имена и email не связывают аккаунты автоматически. Если Forgejo username
совпадает с локальным, создаётся отдельный student. Переименование в Forgejo
обновляет external identity metadata и сохраняет локальный ID, роль и прогресс.
Первоначальное локальное имя остаётся стабильным.

## Настройка после запуска Forgejo

1. В Forgejo зайти под обычным пользователем и открыть
   `/user/settings/applications`. Создать OAuth2 application `Ego Trainer`,
   confidential client. Instance-wide admin application не требуется.
2. Указать точный redirect URI сервера ego-trainer:
   `<EGO_PUBLIC_URL>/auth/forgejo/callback`. Например, для локального пилота:
   `http://127.0.0.1:18081/auth/forgejo/callback`.
3. Сохранить client ID и secret в приватной конфигурации развёртывания.
   Secret не хранить в Git или браузерных настройках.
4. Настроить сервер и перезапустить его:

```dotenv
EGO_FORGEJO_ENABLED=true
EGO_FORGEJO_URL=https://git.born-in-july.ru
EGO_FORGEJO_CLIENT_ID=<client-id>
EGO_FORGEJO_CLIENT_SECRET=<client-secret>
EGO_PUBLIC_URL=http://127.0.0.1:18081
EGO_LOCAL_AUTH_ENABLED=false
```

В production обе origin должны быть HTTPS. Пути, credentials, query и fragment
в origin не допускаются. Для разработки разрешён HTTP только на loopback.
Параметры закрепляются при запуске сервера; OAuth credentials не редактируются
через live service settings. Пока Forgejo не настроен, defaults сохраняют
рабочий локальный вход пилота (`forgejo_enabled=false`, `local_auth_enabled=true`).

Настройка `registration_enabled` также управляет созданием новых Forgejo identities.
Для допуска новых пользователей включить её в Settings либо явно задать
`EGO_REGISTRATION_ENABLED=true`. Закрытая регистрация разрешает вход уже связанным
аккаунтам. У production без явного выбора регистрация по умолчанию закрыта.

## Первый наставник и перенос существующих пользователей

После первого Forgejo входа оператор находит локальный ID:

```console
ego-server admin list-users
ego-server admin set-role --user-id <local-id> --role mentor
```

Дальше ментор назначает наставников в разделе «Пользователи».
Каждое такое назначение записывает actor ID, target ID и время в `mentor_grants`.
HTTP-проверка использует текущую роль в БД: старый JWT пониженного пользователя
не сохраняет право назначать наставников.

Чтобы сохранить существующий локальный аккаунт и его прогресс, оператор
проверяет Forgejo user ID (`sub` в UserInfo) и явно связывает его **до первого
Forgejo входа**:

```console
ego-server admin link-forgejo --user-id <existing-local-id> --subject <verified-forgejo-id>
```

Повторное или конфликтующее связывание отклоняется. CLI требует доверенного
доступа к серверу. В Forgejo режиме password login/registration, создание
локальных password accounts через admin API и reset password закрыты.
Для переноса ранее выданных сессий оператор может ротировать JWT signing secret
после связывания нужных аккаунтов; отдельный settings encryption key сохраняется.

## Проверка подключения

Админка предлагает «Войти через Forgejo», VSCode использует браузер из
`Ego: Login` и мастера подключения к серверу. JWT расширения хранится в
VSCode SecretStorage. Browser admin по-прежнему допускает только mentor/admin.

Перед включением на реальном инстансе проверить: вход нового student,
bootstrap первого mentor, назначение второго mentor, вход существующего
привязанного admin, отмену согласия, повторный вход и закрытую регистрацию.
Проверки с mock provider подтверждают контракт клиента и сервера, но не
заменяют этот smoke на выбранной версии Forgejo.

Текущий native поток предназначен для локального desktop VSCode. Remote SSH,
Codespaces и web extension требуют отдельного callback transport.
Блокировка аккаунта в Forgejo закрывает новые входы; уже выданная ego-сессия
действует до её срока либо удаления локального пользователя. Роль всегда
перечитывается из локальной БД. Изоляция ученического кода перед публичным
запуском остаётся отдельной задачей `ego-trainer-41s`.

Проверено 2026-09-30 на Windows/Python 3.11: 149 серверных тестов прошли,
2 пропущены; расширение собрано, 48 unit-тестов прошли, VSIX упакован.
Полный browser flow с локальным mock Forgejo прошёл 4 сценария без pageerror:
mentor login + promotion, admin login, student rejection, consent cancellation.
Новые OAuth-модули прошли Ruff; `git diff --check` чист.
Подключение реального инстанса отслеживается в `ego-trainer-i2h`.
