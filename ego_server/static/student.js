import { mountTutor } from './student-tutor.js';

(() => {
  const $ = (id) => document.getElementById(id);
  const state = { token: localStorage.getItem('ego_student_token'), user: null, tasks: [], progress: [], selectedId: null, registering: false, understanding: [], account: null, providers: null, epoch: 0, taskEpoch: 0, tutors: new Map() };
  const authScreen = $('auth-screen');
  const dashboard = $('dashboard');
  const authError = $('auth-error');
  let attempt = 0, popup = null, channel = null;
  const authForm = $('auth-form');

  class ApiError extends Error {
    constructor(message, status) { super(message); this.status = status; }
  }

  async function request(path, options = {}) {
    const headers = { Accept: 'application/json' };
    if (state.token && path !== '/auth/providers') headers.Authorization = `Bearer ${state.token}`;
    if (options.body !== undefined) headers['Content-Type'] = 'application/json';
    const response = await fetch(path, { method: options.method || 'GET', headers, body: options.body === undefined ? undefined : JSON.stringify(options.body) });
    const data = await response.json().catch(() => null);
    if (!response.ok) throw new ApiError(data?.detail || `Ошибка сервера: ${response.status}`, response.status);
    return data;
  }

  function showAuth(error = '') {
    dashboard.classList.add('hidden');
    $('user-actions').classList.add('hidden');
    authScreen.classList.remove('hidden');
    authError.textContent = error;
    authError.classList.toggle('hidden', !error);
  }

  function setMode(registering) {
    state.registering = registering = !!(registering && state.providers?.local && state.providers?.registration);
    $('auth-title').textContent = registering ? 'Создай аккаунт' : 'С возвращением!';
    $('auth-description').textContent = registering
      ? 'Аккаунт нужен, чтобы сохранять прогресс и возвращаться к задачам.'
      : 'Войди, чтобы открыть задачи и продолжить с того места, где остановился.';
    $('auth-submit').textContent = registering ? 'Зарегистрироваться' : 'Войти';
    $('auth-switch').textContent = registering ? 'Уже есть аккаунт? Войти' : 'Ещё нет аккаунта? Создать';
    authForm.elements.password.autocomplete = registering ? 'new-password' : 'current-password';
    authForm.elements.password.minLength = registering ? 8 : 1;
    authForm.elements.username.minLength = registering ? 3 : 1;
    authError.classList.add('hidden');
  }

  function progressFor(task) {
    return state.progress.find((row) => row.task_id === task.id && row.version === task.version) || null;
  }

  function taskState(task) {
    const row = progressFor(task);
    if (!row) return 'new';
    if (row.status !== 'passed') return 'started';
    const evidence = state.understanding.find(s => s.task_id === task.id && s.version === task.version && s.solution_hash === row.solution_hash);
    return state.account?.enabled && state.account.defense_required && evidence?.understanding !== 'confirmed' ? 'defense' : 'passed';
  }

  function stateLabel(status) {
    if (status === 'passed') return 'Решена';
    if (status === 'defense') return 'Проверка понимания';
    if (status === 'started') return 'В работе';
    return 'Не начата';
  }

  function updateOverview() {
    const passed = state.tasks.filter((task) => taskState(task) === 'passed').length;
    const active = state.tasks.filter((task) => ['started', 'defense'].includes(taskState(task))).length;
    const total = state.tasks.length;
    const percent = total ? Math.round((passed / total) * 100) : 0;
    $('total-count').textContent = total;
    $('passed-count').textContent = passed;
    $('active-count').textContent = active;
    $('percent').textContent = `${percent}%`;
    $('progress-fill').style.width = `${percent}%`;
    $('progress-fill').parentElement.setAttribute('aria-valuenow', String(percent));
    $('progress-caption').textContent = total ? `Решено ${passed} из ${total}. Осталось ${total - passed}.` : 'Пока задач нет — загляни сюда чуть позже.';
    $('updated').textContent = `Обновлено ${new Date().toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })}`;
  }

  function populateBlocks() {
    const select = $('block-filter');
    const current = select.value;
    select.replaceChildren(new Option('Все блоки', ''));
    [...new Set(state.tasks.map((task) => task.block).filter(Boolean))].sort().forEach((block) => {
      select.add(new Option(`Блок ${block}`, block));
    });
    select.value = current;
  }

  function visibleTasks() {
    const query = $('search').value.trim().toLocaleLowerCase('ru');
    const block = $('block-filter').value;
    const status = $('status-filter').value;
    return state.tasks.filter((task) => {
      const matchesQuery = !query || `${task.id} ${task.task_id} ${task.title} ${task.block}`.toLocaleLowerCase('ru').includes(query);
      return matchesQuery && (!block || task.block === block) && (!status || taskState(task) === status);
    });
  }

  function drawTasks() {
    const list = $('task-list');
    const tasks = visibleTasks();
    $('task-count').textContent = `${tasks.length} ${plural(tasks.length, 'задача', 'задачи', 'задач')}`;
    list.replaceChildren();
    if (!tasks.length) {
      const empty = document.createElement('div');
      empty.className = 'empty';
      empty.textContent = state.tasks.length ? 'По этим фильтрам ничего не нашлось.' : 'Задачи пока не загружены.';
      list.append(empty);
      return;
    }
    const fragment = document.createDocumentFragment();
    tasks.forEach((task) => {
      const status = taskState(task);
      const progress = progressFor(task);
      const button = document.createElement('button');
      button.type = 'button';
      button.className = `task-row${state.selectedId === task.id ? ' selected' : ''}`;
      button.setAttribute('aria-pressed', String(state.selectedId === task.id));
      const symbol = document.createElement('span');
      symbol.className = `task-symbol ${status}`;
      symbol.textContent = status === 'passed' ? '✓' : status === 'started' ? '↻' : '·';
      const info = document.createElement('span');
      info.className = 'task-name';
      const title = document.createElement('span');
      title.className = 'task-title';
      title.textContent = task.title || task.task_id || task.id;
      const meta = document.createElement('span');
      meta.className = 'task-meta';
      meta.textContent = [`${task.block || 'Без блока'}${task.task_id ? ` · ${task.task_id}` : ''}`, task.level].filter(Boolean).join(' · ');
      info.append(title, meta);
      const score = document.createElement('span');
      score.className = 'task-score';
      score.textContent = status === 'defense' ? 'Нужна защита' : progress ? `${progress.passed_tests}/${progress.total_tests} тестов` : stateLabel(status);
      button.append(symbol, info, score);
      button.addEventListener('click', () => openTask(task));
      fragment.append(button);
    });
    list.append(fragment);
  }

  async function openTask(task) {
    const epoch = state.epoch;
    const selection = ++state.taskEpoch;
    state.selectedId = task.id;
    drawTasks();
    const panel = $('task-detail');
    const loading = document.createElement('div');
    loading.className = 'loading';
    loading.textContent = 'Открываю задачу…';
    panel.replaceChildren(loading);
    try {
      const detail = await request(`/tasks/${encodeURIComponent(task.id)}`);
      if (epoch !== state.epoch || selection !== state.taskEpoch) return;
      drawTaskDetail(detail, task);
    } catch (error) {
      if (epoch === state.epoch && selection === state.taskEpoch) showPanelError(error);
    }
  }

  function drawTaskDetail(detail, meta) {
    const panel = $('task-detail');
    const wrap = document.createElement('div');
    wrap.className = 'detail-content';
    const top = document.createElement('div');
    top.className = 'detail-top';
    const id = document.createElement('span');
    id.className = 'detail-id';
    id.textContent = `${meta.block ? `Блок ${meta.block} · ` : ''}${meta.task_id || meta.id}`;
    const badge = document.createElement('span');
    const status = taskState(meta);
    badge.className = `badge ${status}`;
    badge.textContent = stateLabel(status);
    top.append(id, badge);
    const title = document.createElement('h2');
    title.textContent = detail.title || meta.title || meta.task_id;
    const body = document.createElement('div');
    body.className = 'statement';
    renderMarkdown(detail.statement_md || 'У этой задачи пока нет описания.', body);
    wrap.append(top, title);
    const progress = progressFor(meta);
    if (progress) {
      const summary = document.createElement('div');
      summary.className = 'attempt-summary';
      const lastRun = progress.last_run_at ? new Date(progress.last_run_at).toLocaleString('ru-RU') : '—';
      summary.textContent = `${progress.passed_tests}/${progress.total_tests} тестов · ${progress.attempts} ${plural(progress.attempts, 'попытка', 'попытки', 'попыток')} · последняя попытка ${lastRun}`;
      wrap.append(summary);
    }
    if (status === 'defense') {
      const notice = document.createElement('p'); notice.className = 'notice';
      notice.textContent = 'Тесты пройдены. Защити решение ниже: объясни его механизм, проследи выполнение и разбери новый пример.';
      wrap.append(notice);
    }
    wrap.append(body);
    if (detail.stub_py) {
      const divider = document.createElement('div');
      divider.className = 'detail-divider';
      const details = document.createElement('details');
      const summary = document.createElement('summary');
      summary.textContent = 'Показать стартовый код';
      const code = document.createElement('div');
      code.className = 'stub-box';
      const pre = document.createElement('pre');
      pre.textContent = detail.stub_py;
      code.append(pre);
      details.append(summary, code);
      wrap.append(divider, details);
    }
    const hintsButton = document.createElement('button');
    hintsButton.type = 'button';
    hintsButton.className = 'hint-button';
    hintsButton.textContent = 'Показать подсказки';
    const hints = document.createElement('div');
    hints.className = 'hints';
    hintsButton.addEventListener('click', async () => {
      hints.textContent = 'Ищу подсказки…';
      hintsButton.disabled = true;
      try {
        const response = await request(`/tasks/${encodeURIComponent(meta.id)}/hints?level=3`);
        hints.replaceChildren();
        if (!response.hints?.length) hints.textContent = 'Подсказок для этой задачи пока нет.';
        (response.hints || []).forEach((hint) => {
          const item = document.createElement('div');
          item.className = 'hint-item';
          const label = document.createElement('strong');
          label.textContent = `${hint.level}. ${hint.title}: `;
          item.append(label);
          const content = document.createElement("div");
          renderMarkdown(hint.content, content); item.append(content);
          hints.append(item);
        });
      } catch (error) { hints.textContent = error.message; }
      finally { hintsButton.disabled = false; }
    });
    wrap.append(hintsButton, hints);
    const key = `${meta.id}@${meta.version}`;
    if (!state.tutors.has(key)) state.tutors.set(key, {
      mode: 'hint', session: null, pending: null, busy: false, draft: '', code: '', error: ''
    });
    const epoch = state.epoch;
    const submission = state.understanding.find(row => row.task_id === meta.id
      && row.version === meta.version && row.solution_hash === progress?.solution_hash);
    mountTutor({ target: wrap, task: meta, conversation: state.tutors.get(key),
      getAccount: () => state.account, submission, request, renderMarkdown,
      isCurrentStudent: () => epoch === state.epoch && Boolean(state.token),
      onAccount: value => { state.account = value; updateAIStatus(); },
      onDefense: session => {
        const row = state.understanding.find(value => value.id === session.submission_id);
        if (row) row.understanding = session.status;
        updateOverview(); drawTasks();
        if (state.selectedId === meta.id && panel.contains(wrap)) {
          const current = taskState(meta);
          badge.className = `badge ${current}`; badge.textContent = stateLabel(current);
          if (current === 'passed') wrap.querySelector('.notice')?.remove();
        }
      }
    });
    panel.replaceChildren(wrap);
  }

  function renderMarkdown(source, target) {
    const fragment = document.createDocumentFragment();
    const lines = source.replace(/\r/g, '').split('\n');
    let i = 0;
    while (i < lines.length) {
      const line = lines[i];
      if (!line.trim()) { i++; continue; }
      if (/^\s*```/.test(line)) {
        i++;
        const code = [];
        while (i < lines.length && !/^\s*```/.test(lines[i])) code.push(lines[i++]);
        if (i < lines.length) i++;
        const pre = document.createElement('pre');
        const codeElement = document.createElement('code');
        codeElement.textContent = code.join('\n');
        pre.append(codeElement);
        fragment.append(pre);
        continue;
      }
      const heading = line.match(/^\s{0,3}(#{1,6})\s+(.+)$/);
      if (heading) {
        const element = document.createElement(`h${heading[1].length}`);
        appendInline(heading[2], element);
        fragment.append(element);
        i++;
        continue;
      }
      if (/^\s*>/.test(line)) {
        const quote = document.createElement('blockquote');
        while (i < lines.length && /^\s*>/.test(lines[i])) appendInline(lines[i++].replace(/^\s*>\s?/, ''), quote);
        fragment.append(quote);
        continue;
      }
      if (/^\s*[-*+]\s+/.test(line) || /^\s*\d+[.)]\s+/.test(line)) {
        const ordered = /^\s*\d+[.)]\s+/.test(line);
        const list = document.createElement(ordered ? 'ol' : 'ul');
        const pattern = ordered ? /^\s*\d+[.)]\s+/ : /^\s*[-*+]\s+/;
        while (i < lines.length && pattern.test(lines[i])) {
          const item = document.createElement('li');
          appendInline(lines[i++].replace(pattern, ''), item);
          list.append(item);
        }
        fragment.append(list);
        continue;
      }
      const paragraph = document.createElement('p');
      const parts = [];
      while (i < lines.length && lines[i].trim() && !/^\s*```/.test(lines[i]) && !/^\s{0,3}#{1,6}\s/.test(lines[i]) && !/^\s*>/.test(lines[i]) && !/^\s*[-*+]\s+/.test(lines[i])) parts.push(lines[i++]);
      appendInline(parts.join(' '), paragraph);
      fragment.append(paragraph);
    }
    target.replaceChildren(fragment);
  }

  function appendInline(source, target) {
    const pattern = /(\[[^\]]+\]\(https?:\/\/[^)]+\)|`[^`]+`|\*\*[^*]+\*\*|\*[^*]+\*)/g;
    let cursor = 0;
    for (const match of source.matchAll(pattern)) {
      target.append(document.createTextNode(source.slice(cursor, match.index)));
      const value = match[0];
      const link = value.match(/^\[([^\]]+)\]\((https?:\/\/[^)]+)\)$/);
      if (link) {
        const anchor = document.createElement('a');
        anchor.href = link[2];
        anchor.rel = 'noopener noreferrer';
        anchor.target = '_blank';
        anchor.textContent = link[1];
        target.append(anchor);
      } else if (value.startsWith('`')) {
        const code = document.createElement('code');
        code.textContent = value.slice(1, -1);
        target.append(code);
      } else if (value.startsWith('**')) {
        const strong = document.createElement('strong');
        strong.textContent = value.slice(2, -2);
        target.append(strong);
      } else {
        const emphasis = document.createElement('em');
        emphasis.textContent = value.slice(1, -1);
        target.append(emphasis);
      }
      cursor = match.index + value.length;
    }
    target.append(document.createTextNode(source.slice(cursor)));
  }

  function plural(n, one, few, many) {
    const mod100 = n % 100;
    if (mod100 >= 11 && mod100 <= 14) return many;
    const mod10 = n % 10;
    return mod10 === 1 ? one : mod10 >= 2 && mod10 <= 4 ? few : many;
  }

  function showPanelError(error) {
    const panel = $('task-detail');
    const message = document.createElement('div');
    message.className = 'error';
    message.textContent = error.message || 'Не удалось загрузить задачу.';
    panel.replaceChildren(message);
  }

  async function loadDashboard() {
    const epoch = state.epoch;
    const [tasks, progress, understanding, account] = await Promise.all([
      request('/tasks'), request('/progress/me'), request('/progress/me/understanding'), request('/ai/me')]);
    if (epoch !== state.epoch || !state.token) return;
    state.understanding = understanding; state.account = account;
    updateAIStatus();
    state.tasks = tasks;
    state.progress = progress;
    populateBlocks();
    updateOverview();
    drawTasks();
    if (state.selectedId) {
      const selected = state.tasks.find((task) => task.id === state.selectedId);
      if (selected) await openTask(selected);
    }
  }

  function updateAIStatus() {
    const account = state.account;
    $('ai-access').classList.toggle('available', Boolean(account?.available));
    $('ai-access').textContent = account?.available
      ? `Учебный помощник доступен · баланс $${account.balance_usd}. Открой задачу, чтобы задать вопрос или защитить решение.`
      : `Учебный помощник: ${account?.reason || 'Сейчас недоступен'}. Если нужен доступ, обратись к наставнику.`;
  }

  function clearStudentData() {
    state.user = null; state.tasks = []; state.progress = []; state.understanding = [];
    state.account = null; state.selectedId = null; state.taskEpoch++; state.tutors.clear();
    $('task-list').replaceChildren(); $('task-detail').replaceChildren();
    const placeholder = document.createElement('div');
    placeholder.className = 'detail-placeholder';
    placeholder.textContent = 'Выбери задачу — покажу условие, стартовый код и учебного помощника.';
    $('task-detail').append(placeholder);
    for (const id of ['total-count', 'passed-count', 'active-count', 'percent']) $(id).textContent = '—';
    $('progress-fill').style.width = '0%'; $('ai-access').textContent = '';
  }

  async function enter(token) {
    const epoch = ++state.epoch;
    clearStudentData();
    state.token = token;
    localStorage.setItem('ego_student_token', token);
    try {
      const user = await request('/auth/me');
      if (epoch !== state.epoch || state.token !== token) return;
      if (user.role !== 'student') {
        localStorage.setItem('ego_admin_token', token);
        localStorage.removeItem('ego_student_token');
        location.assign('/'); return;
      }
      state.user = user;
      $('hello-name').textContent = state.user.username;
      $('user-name').textContent = state.user.username;
      authScreen.classList.add('hidden');
      dashboard.classList.remove('hidden');
      $('user-actions').classList.remove('hidden');
      await loadDashboard();
    } catch (error) {
      if (epoch !== state.epoch || state.token !== token) return;
      if (error.status === 401) {
        localStorage.removeItem('ego_student_token');
        state.token = null;
        showAuth('Сессия закончилась. Войди ещё раз.');
      } else {
        showAuth(error.message);
      }
    }
  }

  authForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    if (!state.providers?.local) return;
    const fields = new FormData(authForm);
    const body = { username: String(fields.get('username')).trim(), password: String(fields.get('password')) };
    const button = $('auth-submit');
    button.disabled = true;
    button.textContent = state.registering ? 'Создаю…' : 'Вхожу…';
    authError.classList.add('hidden');
    try {
      const result = await request(state.registering ? '/auth/register' : '/auth/login', { method: 'POST', body });
      authForm.reset();
      setMode(false);
      await enter(result.access_token);
    } catch (error) {
      authError.textContent = error.status === 401 ? 'Логин или пароль не подошли.' : error.status === 409 ? 'Такой логин уже занят.' : error.message;
      authError.classList.remove('hidden');
    } finally {
      button.disabled = false;
      button.textContent = state.registering ? 'Зарегистрироваться' : 'Войти';
    }
  });

  $('auth-switch').addEventListener('click', () => setMode(!state.registering));
  $('logout').addEventListener('click', () => {
    state.epoch++; cancelForgejo(); clearStudentData();
    state.token = null;
    state.user = null;
    state.understanding = []; state.account = null;
    state.tasks = [];
    state.progress = [];
    state.selectedId = null;
    localStorage.removeItem('ego_student_token');
    setMode(false);
    showAuth();
  });
  $('search').addEventListener('input', drawTasks);
  $('block-filter').addEventListener('change', drawTasks);
  $('status-filter').addEventListener('change', drawTasks);
  $('refresh').addEventListener('click', async () => {
    const button = $('refresh');
    button.disabled = true;
    try { await loadDashboard(); }
    catch (error) { showPanelError(error); }
    finally { button.disabled = false; }
  });

  function cancelForgejo() {
    attempt++; popup?.close(); channel?.close(); popup = channel = null;
    $('forgejo-login').disabled = false; $('forgejo-login').textContent = 'Войти через Forgejo';
    $('forgejo-cancel').classList.add('hidden');
  }

  async function forgejoLogin() {
    const current = ++attempt;
    popup = window.open('about:blank', '_blank');
    if (!popup) { showAuth('Разреши новую вкладку для входа через Forgejo.'); return; }
    popup.opener = null;
    $('forgejo-login').disabled = true; $('forgejo-login').textContent = 'Ожидаю вход…';
    $('forgejo-cancel').classList.remove('hidden');
    const encode = bytes => btoa(String.fromCharCode(...bytes)).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
    try {
      const verifier = encode(crypto.getRandomValues(new Uint8Array(32)));
      const digest = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(verifier));
      const flow = await request('/auth/forgejo/start', {method: 'POST', body: {client: 'browser', code_challenge: encode(new Uint8Array(digest))}});
      if (current !== attempt) return;
      if (new URL(flow.authorization_url).origin !== location.origin) throw new Error('Проверь адрес сервиса для входа через Forgejo.');
      let ticket = '', failed = false;
      channel = new BroadcastChannel('ego-forgejo-' + flow.state);
      channel.onmessage = event => {
        if (event.data?.error === 'login_failed') failed = true;
        if (typeof event.data?.ticket === 'string' && /^[A-Za-z0-9_-]{43}$/.test(event.data.ticket)) ticket = event.data.ticket;
      };
      popup.location.href = flow.authorization_url;
      const deadline = Date.now() + flow.expires_in * 1000;
      while (current === attempt && Date.now() < deadline) {
        await new Promise(resolve => setTimeout(resolve, 1000));
        if (current !== attempt) return;
        if (failed) throw new Error('Вход не завершён или регистрация закрыта. Обратись к наставнику.');
        if (!ticket) continue;
        const result = await request('/auth/forgejo/exchange', {method: 'POST', body: {state: flow.state, code_verifier: verifier, ticket}});
        if (current !== attempt) return;
        if (!result.pending) { cancelForgejo(); await enter(result.access_token); return; }
      }
      if (current === attempt) throw new Error('Время входа истекло. Попробуй ещё раз.');
    } catch (error) { if (current === attempt) showAuth(error.message); }
    finally { if (current === attempt) cancelForgejo(); }
  }
  $('forgejo-login').addEventListener('click', forgejoLogin);
  $('forgejo-cancel').addEventListener('click', cancelForgejo);
  window.addEventListener('pagehide', cancelForgejo);
  request('/auth/providers').then(providers => {
    state.providers = providers;
    $('forgejo-login').classList.toggle('hidden', !providers.forgejo);
    $('local-fields').classList.toggle('hidden', !providers.local);
    $('auth-switch').classList.toggle('hidden', !providers.local || !providers.registration);
    setMode(false);
    if (!providers.local && !providers.forgejo) showAuth('Вход пока не настроен. Обратись к наставнику.');
  }).catch(error => showAuth(error.message));

  if (state.token) enter(state.token);
  else showAuth();
})();
