import { mountTaskPage } from './student-task-page.js';
import { readStudentRoute, studentTaskUrl, studentCatalogUrl, isPlainNavigation } from './student-navigation.js';

(() => {
  const $ = (id) => document.getElementById(id);
  const state = { ready: false, details: new Map(), pageController: null, pageTaskKey: null, catalogUrl: '/student', token: localStorage.getItem('ego_student_token'), user: null, tasks: [], progress: [], selectedId: null, registering: false, understanding: [], account: null, providers: null, epoch: 0, taskEpoch: 0, tutors: new Map() };
  const authScreen = $('auth-screen');
  const dashboard = $('dashboard');
  const workspace = $('student-workspace');
  history.scrollRestoration = 'manual';
  const authError = $('auth-error');
  let attempt = 0, popup = null, channel = null;
  const authForm = $('auth-form');

  class ApiError extends Error {
    constructor(message, status) { super(message); this.status = status; }
  }

  async function request(path, options = {}) {
    const headers = { Accept: 'application/json' };
    const requestToken = path === '/auth/providers' ? null : state.token;
    if (requestToken) headers.Authorization = `Bearer ${requestToken}`;
    if (options.body !== undefined) headers['Content-Type'] = 'application/json';
    let response;
    try {
      response = await fetch(path, { method: options.method || 'GET', headers, body: options.body === undefined ? undefined : JSON.stringify(options.body) });
    } catch {
      throw new ApiError('Не удалось связаться с сервером. Проверь подключение и повтори попытку.', 0);
    }
    const data = await response.json().catch(() => null);
    if (!response.ok) {
      if (response.status === 401 && requestToken && state.user && requestToken === state.token) {
        state.epoch++; clearStudentData(); state.token = null;
        localStorage.removeItem('ego_student_token');
        showAuth('Сессия закончилась. Войди ещё раз — вернёшься к этой странице.');
      }
      const message = typeof data?.detail === 'string' ? data.detail : `Ошибка сервера: ${response.status}`;
      throw new ApiError(message, response.status);
    }
    return data;
  }

  function showAuth(error = '') {
    $('content-skip').href = '#auth-form';
    workspace.classList.add('hidden');
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
      if (state.tasks.length) {
        const reset = document.createElement('button'); reset.className = 'quiet-button'; reset.type = 'button'; reset.textContent = 'Сбросить фильтры';
        reset.addEventListener('click', () => { applyFilters({}); changeFilters(); }); empty.append(reset);
      }
      list.append(empty);
      return;
    }
    const fragment = document.createDocumentFragment();
    tasks.forEach((task) => {
      const status = taskState(task);
      const progress = progressFor(task);
      const button = document.createElement('a');
      button.href = studentTaskUrl(task.id);
      button.className = 'task-row';
      const symbol = document.createElement('span');
      symbol.className = `task-symbol ${status}`;
      symbol.textContent = status === 'passed' ? '✓' : status === 'defense' ? '?' : status === 'started' ? '↻' : '·';
      symbol.setAttribute('aria-hidden', 'true');
      const info = document.createElement('span');
      info.className = 'task-name';
      const title = document.createElement('span');
      title.className = 'task-title';
      title.textContent = task.title || task.task_id || task.id;
      const meta = document.createElement('span');
      meta.className = 'task-meta';
      const levels = { easy: 'Базовый', medium: 'Средний', hard: 'Сложный' };
      meta.textContent = [`${task.block ? `Блок ${task.block}` : 'Без блока'}${task.task_id ? ` · ${task.task_id}` : ''}`, levels[task.level] || task.level].filter(Boolean).join(' · ');
      info.append(title, meta);
      const score = document.createElement('span');
      score.className = 'task-score';
      score.textContent = status === 'defense' ? 'Тесты пройдены · нужна защита'
        : progress ? `${stateLabel(status)} · ${progress.passed_tests}/${progress.total_tests} тестов` : stateLabel(status);
      const arrow = document.createElement('span'); arrow.className = 'task-arrow'; arrow.textContent = '→'; arrow.setAttribute('aria-hidden', 'true');
      button.append(symbol, info, score, arrow);
      button.addEventListener('click', event => {
        if (!isPlainNavigation(event)) return;
        event.preventDefault();
        history.replaceState({ ...history.state, scrollY: window.scrollY }, '', location.href);
        history.pushState({ catalogUrl: studentCatalogUrl(currentFilters()), fromCatalog: true }, '', button.href);
        void renderRoute({ focus: true });
      });
      fragment.append(button);
    });
    list.append(fragment);
  }

  function currentFilters() {
    return { q: $('search').value, block: $('block-filter').value, status: $('status-filter').value };
  }

  function applyFilters(filters) {
    $('search').value = filters.q || '';
    $('block-filter').value = filters.block || '';
    $('status-filter').value = filters.status || '';
  }

  function changeFilters() {
    state.catalogUrl = studentCatalogUrl(currentFilters());
    $('catalog-home').href = state.catalogUrl;
    history.replaceState({ ...history.state }, '', state.catalogUrl);
    drawTasks();
  }

  function backToCatalog() {
    if (history.state?.fromCatalog) { history.back(); return; }
    history.pushState({}, '', state.catalogUrl);
    void renderRoute({ focus: true });
  }

  function submissionFor(task) {
    const progress = progressFor(task);
    return state.understanding.find(row => row.task_id === task.id
      && row.version === task.version && row.solution_hash === progress?.solution_hash) || null;
  }

  function conversationFor(task, kind, submission) {
    const key = JSON.stringify([task.id, task.version, task.content_hash, kind, submission?.id]);
    if (!state.tutors.has(key)) state.tutors.set(key, {
      mode: kind === 'defense' ? 'defend' : 'hint', session: null, pending: null,
      busy: false, draft: '', code: '', error: ''
    });
    return state.tutors.get(key);
  }

  function showTaskError(message, retry = false) {
    const panel = $('task-page'); panel.replaceChildren();
    const back = document.createElement('a'); back.className = 'back-link'; back.href = state.catalogUrl; back.textContent = '← Все задачи';
    back.addEventListener('click', event => { if (isPlainNavigation(event)) { event.preventDefault(); backToCatalog(); } });
    const box = document.createElement('div'); box.className = 'empty-state'; box.setAttribute('role', 'alert');
    const heading = document.createElement('h1'); heading.textContent = 'Задача недоступна';
    const text = document.createElement('p'); text.className = 'muted'; text.textContent = message;
    box.append(heading, text);
    if (retry) {
      const button = document.createElement('button'); button.className = 'quiet-button'; button.type = 'button'; button.textContent = 'Повторить загрузку';
      button.addEventListener('click', () => { void renderRoute({ force: true }); }); box.append(button);
    }
    panel.append(back, box);
  }

  async function renderRoute({ focus = false, force = false, restoreScroll = false } = {}) {
    if (!state.ready || !state.user) return;
    const route = readStudentRoute(location);
    const epoch = state.epoch, selection = ++state.taskEpoch;
    const panel = $('task-page');
    dashboard.hidden = route.taskId !== null; panel.hidden = route.taskId === null;
    if (route.taskId === null) {
      state.selectedId = null; state.pageController = null; state.pageTaskKey = null;
      state.catalogUrl = studentCatalogUrl(route.filters);
      $('catalog-home').href = state.catalogUrl;
      applyFilters(route.filters); drawTasks();
      document.title = 'Мой прогресс — Cogito';
      if (focus) $('catalog-title').focus({ preventScroll: true });
      window.scrollTo(0, restoreScroll ? (history.state?.scrollY || 0) : 0);
      return;
    }
    if (history.state?.catalogUrl) {
      const saved = new URL(history.state.catalogUrl, location.origin);
      state.catalogUrl = studentCatalogUrl(readStudentRoute(saved).filters);
    }
    $('catalog-home').href = state.catalogUrl;
    state.selectedId = route.taskId;
    const task = state.tasks.find(value => value.id === route.taskId);
    if (!task) {
      state.pageController = null; state.pageTaskKey = null;
      document.title = 'Задача недоступна — Cogito';
      showTaskError('Такой задачи нет в твоём каталоге. Возможно, ссылка устарела или доступ изменился.');
      return;
    }
    document.title = `${task.title || task.task_id} — Cogito`;
    const key = JSON.stringify([task.id, task.version, task.content_hash]);
    if (state.pageTaskKey === key && state.pageController && !force) {
      state.pageController.activateTab(route.tab, { notify: false }); return;
    }
    state.pageController = null; state.pageTaskKey = null;
    const loading = document.createElement('p'); loading.className = 'loading'; loading.setAttribute('role', 'status'); loading.textContent = 'Открываю задачу…';
    panel.replaceChildren(loading);
    try {
      const detail = state.details.get(key) || await request(`/tasks/${encodeURIComponent(task.id)}`);
      if (epoch !== state.epoch || selection !== state.taskEpoch) return;
      state.details.set(key, detail);
      state.pageController = mountTaskPage({ root: panel, task, detail, initialTab: route.tab,
        catalogUrl: state.catalogUrl, onBack: backToCatalog, onRefresh: refreshData,
        onTab: tab => history.replaceState({ ...history.state }, '', studentTaskUrl(task.id, tab)),
        getProgress: () => progressFor(task), getSubmission: () => submissionFor(task),
        getAccount: () => state.account, getStatus: () => ({ key: taskState(task), label: stateLabel(taskState(task)) }),
        conversationFor: (kind, submission) => conversationFor(task, kind, submission), request, renderMarkdown,
        isCurrentStudent: () => epoch === state.epoch && Boolean(state.token),
        onAccount: value => {
          state.account = value; updateAIStatus(); updateOverview(); drawTasks();
          for (const conversation of state.tutors.values()) conversation.changed?.();
        },
        onDefense: session => {
          const row = state.understanding.find(value => value.id === session.submission_id);
          if (row) { row.understanding = session.status; row.evidence = session.evidence || []; }
          updateOverview(); drawTasks();
        }
      });
      state.pageTaskKey = key;
      if (focus) $('task-title').focus({ preventScroll: true });
      window.scrollTo(0, restoreScroll ? (history.state?.scrollY || 0) : 0);
    } catch (error) {
      if (epoch === state.epoch && selection === state.taskEpoch) showTaskError(error.message, error.status !== 404);
    }
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

  function showWorkspaceError(error) {
    if (!state.user) return;
    $('app-error-message').textContent = error.message || 'Не удалось обновить данные.';
    $('app-error').classList.remove('hidden');
  }

  async function loadDashboard() {
    const epoch = state.epoch;
    $('app-error').classList.add('hidden');
    $('workspace-loading').hidden = state.ready;
    try {
      const [tasks, progress, understanding, account] = await Promise.all([
        request('/tasks'), request('/progress/me'), request('/progress/me/understanding'), request('/ai/me')]);
      if (epoch !== state.epoch || !state.token) return;
      state.understanding = understanding; state.account = account;
      state.tasks = tasks; state.progress = progress; state.ready = true;
      updateAIStatus(); populateBlocks(); updateOverview();
      await renderRoute({ force: true });
    } finally {
      if (epoch === state.epoch) $('workspace-loading').hidden = true;
    }
  }

  function updateAIStatus() {
    const account = state.account;
    $('ai-access').classList.toggle('available', Boolean(account?.available));
    $('ai-access').textContent = account?.available
      ? `Учебный помощник доступен · баланс ${new Intl.NumberFormat('ru-RU', { style: 'currency', currency: 'USD', maximumFractionDigits: 4 }).format(Number(account.balance_usd))}. Вопросы и защита — на странице задачи.`
      : `Учебный помощник: ${account?.reason || 'Сейчас недоступен'}. Если нужен доступ, обратись к наставнику.`;
  }

  function clearStudentData() {
    state.user = null; state.tasks = []; state.progress = []; state.understanding = [];
    state.account = null; state.selectedId = null; state.taskEpoch++; state.tutors.clear();
    state.details.clear(); state.ready = false; state.pageController = null; state.pageTaskKey = null;
    $('task-list').replaceChildren(); $('task-page').replaceChildren();
    dashboard.hidden = true; $('task-page').hidden = true;
    $('app-error').classList.add('hidden');
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
      $('content-skip').href = '#student-workspace';
      $('hello-name').textContent = state.user.username;
      $('user-name').textContent = state.user.username;
      authScreen.classList.add('hidden');
      workspace.classList.remove('hidden');
      $('user-actions').classList.remove('hidden');
      await loadDashboard();
    } catch (error) {
      if (epoch !== state.epoch || state.token !== token) return;
      if (error.status === 401) {
        localStorage.removeItem('ego_student_token');
        state.token = null;
        showAuth('Сессия закончилась. Войди ещё раз.');
      } else if (state.user) {
        showWorkspaceError(error);
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
  $('search').addEventListener('input', changeFilters);
  $('block-filter').addEventListener('change', changeFilters);
  $('status-filter').addEventListener('change', changeFilters);
  async function refreshData(event) {
    const button = event.currentTarget; button.disabled = true;
    const currentUrl = location.href, scrollY = window.scrollY;
    try {
      await loadDashboard();
    }
    catch (error) { showWorkspaceError(error); }
    finally {
      button.disabled = false;
      if (state.user && location.href === currentUrl) {
        const target = button.hasAttribute('data-refresh-progress')
          ? $('task-page').querySelector('[data-refresh-progress]') : button;
        target?.focus({ preventScroll: true }); window.scrollTo(0, scrollY);
      }
    }
  }
  $('refresh').addEventListener('click', refreshData);
  $('retry-data').addEventListener('click', refreshData);
  $('catalog-home').addEventListener('click', event => {
    if (!isPlainNavigation(event) || !state.ready) return;
    event.preventDefault();
    if (readStudentRoute(location).taskId !== null) backToCatalog();
    else window.scrollTo(0, 0);
  });
  window.addEventListener('popstate', () => { void renderRoute({ focus: true, restoreScroll: true }); });

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
  }).catch(error => { if (state.user) showWorkspaceError(error); else showAuth(error.message); });

  if (state.token) enter(state.token);
  else showAuth();
})();
