(() => {
  'use strict';

  const $ = (id) => document.getElementById(id);
  const L = window.StudentLogic;
  const markdown = window.StudentMarkdown;
  const root = $('view-content');
  const authScreen = $('auth-screen');
  const dashboard = $('dashboard');
  const authForm = $('auth-form');
  const authError = $('auth-error');
  const validViews = ['today', 'course', 'theory', 'vscode'];
  const state = {
    token: localStorage.getItem('ego_student_token'), user: null, providers: null,
    tasks: [], progress: [], understanding: [], evidenceByTask: new Map(),
    evidenceAvailable: false, account: null, lessons: [], lessonDetails: new Map(),
    extension: null, registering: false, epoch: 0, taskEpoch: 0,
    course: { query: '', openOnly: false, defenseOnly: false }, theoryQuery: '',
  };
  let attempt = 0;
  let popup = null;
  let channel = null;
  let toastTimer = null;

  class ApiError extends Error {
    constructor(message, status) { super(message); this.status = status; }
  }

  function h(tag, className, text) {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (text !== undefined && text !== null) element.textContent = String(text);
    return element;
  }

  function append(parent, ...children) {
    parent.append(...children.filter(Boolean));
    return parent;
  }

  function isPlainNavigation(event) {
    return event.button === 0 && !event.ctrlKey && !event.metaKey && !event.shiftKey && !event.altKey;
  }

  function plural(n, one, few, many) {
    const mod100 = Math.abs(n) % 100;
    if (mod100 >= 11 && mod100 <= 14) return many;
    const mod10 = mod100 % 10;
    return mod10 === 1 ? one : mod10 >= 2 && mod10 <= 4 ? few : many;
  }

  async function request(path, options = {}) {
    const headers = { Accept: 'application/json' };
    if (state.token && path !== '/auth/providers') headers.Authorization = `Bearer ${state.token}`;
    if (options.body !== undefined) headers['Content-Type'] = 'application/json';
    const response = await fetch(path, {
      method: options.method || 'GET', headers,
      body: options.body === undefined ? undefined : JSON.stringify(options.body),
    });
    const data = await response.json().catch(() => null);
    if (!response.ok) throw new ApiError(data?.detail || `Ошибка сервера: ${response.status}`, response.status);
    return data;
  }

  function showToast(message) {
    clearTimeout(toastTimer);
    $('toast').textContent = message;
    $('toast').classList.remove('hidden');
    toastTimer = setTimeout(() => $('toast').classList.add('hidden'), 3500);
  }

  function showAuth(error = '') {
    dashboard.classList.add('hidden');
    $('main-nav').classList.add('hidden');
    $('user-actions').classList.add('hidden');
    authScreen.classList.remove('hidden');
    authError.textContent = error;
    authError.classList.toggle('hidden', !error);
    document.title = 'Вход — Cogito';
  }

  function showCabinet() {
    authScreen.classList.add('hidden');
    dashboard.classList.remove('hidden');
    $('main-nav').classList.remove('hidden');
    $('user-actions').classList.remove('hidden');
    $('user-name').textContent = state.user?.username || '';
  }

  function setMode(registering) {
    state.registering = registering = Boolean(registering && state.providers?.local && state.providers?.registration);
    $('auth-title').textContent = registering ? 'Создай свой аккаунт' : 'Рад тебя видеть!';
    $('auth-description').textContent = registering
      ? 'Сохраняй прогресс и возвращайся к курсу с любого устройства.'
      : 'Войди, чтобы продолжить с того места, где остановился.';
    $('auth-submit').textContent = registering ? 'Создать аккаунт →' : 'Войти →';
    $('auth-switch').textContent = registering ? 'Уже есть аккаунт? Войти' : 'Ещё нет аккаунта? Создать';
    authForm.elements.password.autocomplete = registering ? 'new-password' : 'current-password';
    authForm.elements.password.minLength = registering ? 8 : 1;
    authForm.elements.username.minLength = registering ? 3 : 1;
    authError.classList.add('hidden');
  }

  function progressFor(task) {
    return state.progress.find((row) => row.task_id === task.id && row.version === task.version) || null;
  }

  function stateOf(task) {
    const required = L.effectiveDefenseRequired(state.account?.defense_required, state.evidenceAvailable);
    return L.taskState(task, progressFor(task), state.evidenceByTask.get(task.id), required);
  }

  function statusBadge(taskOrState) {
    const key = typeof taskOrState === 'string' ? taskOrState : stateOf(taskOrState);
    return h('span', `status-badge ${key}`, L.taskStateLabel(key));
  }

  function statusIcon(taskOrState) {
    const key = typeof taskOrState === 'string' ? taskOrState : stateOf(taskOrState);
    const symbols = { passed: '✓', defense: '!', started: '↻', failed: '!', new: '·' };
    const icon = h('span', `status-icon ${key}`, symbols[key]);
    icon.setAttribute('aria-hidden', 'true');
    return icon;
  }

  function groupCatalog(tasks = state.tasks) {
    return L.groupCatalog(tasks, (project, folder, task) => {
      if (stateOf(task) === 'passed') { project.passed++; folder.passed++; }
    });
  }

  function taskUrl(id) { return `/student/tasks/${encodeURIComponent(id)}`; }
  function viewUrl(view, lessonId = '') {
    const params = new URLSearchParams({ view });
    if (lessonId) params.set('lesson', lessonId);
    return `/student?${params}`;
  }
  function vscodeUrl(id) { return `vscode://ego-trainer.ego-trainer/open?task=${encodeURIComponent(id)}`; }

  function taskLink(task, className = 'task-link') {
    const anchor = h('a', className);
    anchor.href = taskUrl(task.id);
    anchor.dataset.taskLink = task.id;
    const title = h('span', 'item-title', task.title || task.task_id || task.id);
    title.append(h('span', 'item-meta', task.id));
    append(anchor, statusIcon(task), title, h('span', 'item-tail', stateOf(task) === 'defense' ? 'Защита' : stateOf(task) === 'passed' ? 'Готово' : 'Открыть →'));
    return anchor;
  }

  function lessonLink(lesson) {
    const anchor = h('a', 'lesson-link');
    anchor.href = viewUrl('theory', lesson.id);
    anchor.dataset.lessonLink = lesson.id;
    const title = h('span', 'item-title', lesson.title || lesson.id);
    title.append(h('span', 'item-meta', 'Карточка теории'));
    const icon = h('span', 'status-icon', '≡');
    icon.setAttribute('aria-hidden', 'true');
    append(anchor, icon, title, h('span', 'item-tail', 'Прочитать →'));
    return anchor;
  }

  function readRoute() {
    const prefix = '/student/tasks/';
    if (location.pathname.startsWith(prefix)) {
      let taskId = '';
      try { taskId = decodeURIComponent(location.pathname.slice(prefix.length)); } catch { /* invalid id */ }
      return { view: 'task', taskId, lessonId: '' };
    }
    const params = new URLSearchParams(location.search);
    const requested = params.get('view') || 'today';
    return { view: validViews.includes(requested) ? requested : 'today', taskId: '', lessonId: params.get('lesson') || '' };
  }

  function setActiveNav(route) {
    const active = route.view === 'task' ? 'course' : route.view;
    document.querySelectorAll('[data-nav]').forEach((anchor) => {
      if (anchor.dataset.nav === active) anchor.setAttribute('aria-current', 'page');
      else anchor.removeAttribute('aria-current');
    });
  }

  function navigate(url, { replace = false, focus = true } = {}) {
    if (replace) history.replaceState({}, '', url);
    else history.pushState({}, '', url);
    renderRoute({ focus });
  }

  function loading(message = 'Загружаю…') {
    const wrap = h('div', 'loading-state');
    wrap.setAttribute('role', 'status');
    append(wrap, h('span', 'loading-mark'), h('p', '', message));
    wrap.firstChild.setAttribute('aria-hidden', 'true');
    root.replaceChildren(wrap);
  }

  function errorState(error, retry) {
    const wrap = h('div', 'empty-state card');
    append(wrap, h('h2', '', 'Не получилось загрузить данные'), h('p', '', error?.message || 'Проверь соединение и попробуй ещё раз.'));
    const button = h('button', 'button button-primary', 'Попробовать ещё раз');
    button.type = 'button';
    button.addEventListener('click', retry);
    wrap.append(button);
    root.replaceChildren(wrap);
  }

  function heading(eyebrow, title, description, className = 'page-heading') {
    const section = h('section', className);
    const copy = h('div');
    append(copy, h('p', 'eyebrow', eyebrow), h('h1', '', title));
    if (description) copy.append(h('p', 'subheading', description));
    section.append(copy);
    return section;
  }

  function progressBar(passed, total, label) {
    const value = L.percent(passed, total);
    const track = h('div', 'progress-track');
    track.setAttribute('role', 'progressbar');
    track.setAttribute('aria-label', label);
    track.setAttribute('aria-valuemin', '0');
    track.setAttribute('aria-valuemax', '100');
    track.setAttribute('aria-valuenow', String(value));
    const fill = h('div', `progress-fill${value === 100 ? ' complete' : ''}`);
    fill.style.width = `${value}%`;
    track.append(fill);
    return track;
  }

  function renderToday() {
    document.title = 'Сегодня — Cogito';
    const fragment = document.createDocumentFragment();
    const name = state.user?.username || 'друг';
    fragment.append(heading('Твой курс на сегодня', `Привет, ${name}!`, 'Вот где ты остановился. Можно продолжить в VS Code или спокойно почитать здесь.', 'page-heading today-heading'));

    const grid = h('section', 'today-grid');
    const next = L.pickNextTask(state.tasks, stateOf);
    const nextCard = h('article', 'next-card card');
    if (next) {
      const nextState = stateOf(next);
      const top = h('div');
      append(top, h('p', 'eyebrow', nextState === 'defense' ? 'Остался последний шаг' : 'Следующий шаг'), statusBadge(nextState));
      const copy = h('div');
      copy.append(h('h2', '', `Продолжить: ${next.title || next.id}`));
      copy.append(h('p', 'next-meta', [next.project_name, next.folder_name, next.id].filter(Boolean).join(' · ')));
      const actions = h('div', 'next-actions');
      const open = h('a', 'button button-primary', nextState === 'defense' ? 'Защитить в VS Code ↗' : 'Открыть в VS Code ↗');
      open.href = vscodeUrl(next.id);
      const read = h('a', 'button button-secondary', 'Читать условие здесь');
      read.href = taskUrl(next.id);
      read.dataset.taskLink = next.id;
      append(actions, open, read);
      append(nextCard, top, copy, actions);
    } else if (state.tasks.length) {
      append(nextCard, h('p', 'eyebrow', 'Курс пройден'), h('h2', '', 'Все задачи решены. Отличная работа!'), h('p', 'next-meta', 'Можно вернуться к теории или повторить любую задачу.'));
      const actions = h('div', 'next-actions');
      const course = h('a', 'button button-primary', 'Открыть курс');
      course.href = viewUrl('course'); course.dataset.nav = 'course';
      actions.append(course); nextCard.append(actions);
    } else {
      append(nextCard, h('p', 'eyebrow', 'Скоро начнём'), h('h2', '', 'Задачи появятся здесь'), h('p', 'next-meta', 'Пока можно установить расширение и подготовить VS Code.'));
    }

    const passed = state.tasks.filter((task) => stateOf(task) === 'passed').length;
    const total = state.tasks.length;
    const overall = h('article', 'overall-card card');
    const overallTop = h('div');
    append(overallTop, h('p', 'eyebrow', 'Общий прогресс'), h('div', 'overall-number', `${L.percent(passed, total)}%`), h('p', 'overall-caption', total ? `${passed} ${plural(passed, 'задача решена', 'задачи решены', 'задач решено')} из ${total}` : 'Задач пока нет'));
    const overallBottom = h('div');
    overallBottom.append(progressBar(passed, total, 'Общий прогресс по курсу'));
    const foot = h('div', 'overall-foot');
    append(foot, h('span', '', `Решено: ${passed}`), h('span', '', `Осталось: ${Math.max(0, total - passed)}`));
    overallBottom.append(foot);
    append(overall, overallTop, overallBottom);
    append(grid, nextCard, overall);
    fragment.append(grid);

    const defenseTasks = state.tasks.filter((task) => stateOf(task) === 'defense');
    if (defenseTasks.length) {
      const panel = h('section', 'defense-panel panel');
      const title = h('div', 'section-title');
      const copy = h('div');
      append(copy, h('h2', '', 'Ждут защиты понимания'), h('p', '', 'Тесты уже пройдены. Осталось объяснить своё решение в VS Code.'));
      title.append(copy); panel.append(title);
      const list = h('div', 'defense-list');
      for (const task of defenseTasks) {
        const item = h('div', 'defense-item');
        const info = h('div');
        const titleLink = h('a', 'item-title', task.title || task.id);
        titleLink.href = taskUrl(task.id); titleLink.dataset.taskLink = task.id;
        info.append(titleLink, h('p', '', task.id));
        const action = h('a', 'button button-small button-soft', 'Защитить в VS Code ↗');
        action.href = vscodeUrl(task.id);
        append(item, statusIcon('defense'), info, action);
        list.append(item);
      }
      panel.append(list); fragment.append(panel);
    }

    const lower = h('div', 'today-lower');
    const progressPanel = h('section', 'panel');
    const progressTitle = h('div', 'section-title');
    const progressCopy = h('div');
    append(progressCopy, h('h2', '', 'Прогресс по папкам'), h('p', '', 'Каждая полоса — ещё один пройденный кусочек курса.'));
    const courseLink = h('a', '', 'Весь курс →');
    courseLink.href = viewUrl('course'); courseLink.dataset.nav = 'course';
    append(progressTitle, progressCopy, courseLink); progressPanel.append(progressTitle);
    const folderList = h('div', 'folder-progress-list progress-scroll');
    let previousProject = '';
    for (const project of groupCatalog().projects) {
      for (const folder of project.folders) {
        if (project.name !== previousProject) {
          folderList.append(h('div', 'folder-project-label', project.name));
          previousProject = project.name;
        }
        const row = h('div', 'folder-progress');
        const head = h('div', 'folder-progress-head');
        append(head, h('span', '', folder.name), h('strong', '', `${folder.passed}/${folder.total}`));
        append(row, head, progressBar(folder.passed, folder.total, `${folder.name}: ${folder.passed} из ${folder.total}`));
        folderList.append(row);
      }
    }
    if (!total) folderList.append(h('p', 'muted', 'Как только появятся задачи, здесь будет виден прогресс.'));
    progressPanel.append(folderList);

    const extension = h('section', 'extension-teaser card');
    append(extension, h('div', 'mini-mark', '</>'), h('h2', '', 'Решай в VS Code'), h('p', '', 'Условие, код и автопроверка — в одном окне. Расширение подскажет, что делать дальше.'));
    const steps = h('ol', 'steps-mini');
    for (const [index, text] of ['Скачай расширение', 'Установи его в VS Code', 'Войди и открой задачу'].entries()) {
      const item = h('li'); append(item, h('span', '', index + 1), document.createTextNode(text)); steps.append(item);
    }
    const setup = h('a', 'button button-small button-soft', 'Как начать →');
    setup.href = viewUrl('vscode'); setup.dataset.nav = 'vscode';
    append(extension, steps, setup);
    append(lower, progressPanel, extension);
    fragment.append(lower);
    root.replaceChildren(fragment);
  }

  function filteredTasks() {
    const query = state.course.query.trim().toLocaleLowerCase('ru');
    return state.tasks.filter((task) => {
      if (query && !`${task.id} ${task.task_id || ''} ${task.title || ''}`.toLocaleLowerCase('ru').includes(query)) return false;
      const taskState = stateOf(task);
      if (state.course.openOnly && !L.isOpenState(taskState)) return false;
      if (state.course.defenseOnly && taskState !== 'defense') return false;
      return true;
    });
  }

  function lessonsForFolder(folder, tasks) {
    const block = tasks[0]?.block;
    const query = state.course.query.trim().toLocaleLowerCase('ru');
    return state.lessons.filter((lesson) => (folder.id ? lesson.folder_id === folder.id : lesson.block === block)
      && (!query || `${lesson.id} ${lesson.title}`.toLocaleLowerCase('ru').includes(query)));
  }

  function drawCourseCatalog(container, countLabel) {
    const tasks = filteredTasks();
    countLabel.textContent = `${tasks.length} ${plural(tasks.length, 'задача', 'задачи', 'задач')}`;
    if (!tasks.length) {
      const empty = h('div', 'empty-state course-empty');
      append(empty, h('h2', '', state.tasks.length ? 'Ничего не нашлось' : 'Задачи пока не добавлены'), h('p', '', state.tasks.length ? 'Попробуй изменить запрос или сбросить фильтры.' : 'Загляни сюда чуть позже.'));
      if (state.tasks.length) {
        const reset = h('button', 'button button-secondary', 'Сбросить фильтры');
        reset.type = 'button';
        reset.addEventListener('click', () => {
          state.course = { query: '', openOnly: false, defenseOnly: false };
          renderCourse();
        });
        empty.append(reset);
      }
      container.replaceChildren(empty);
      return;
    }
    const catalog = groupCatalog(tasks);
    const next = L.pickNextTask(state.tasks, stateOf);
    const hasFilters = Boolean(state.course.query || state.course.openOnly || state.course.defenseOnly);
    const fragment = document.createDocumentFragment();
    for (const project of catalog.projects) {
      const projectSection = h('section', 'catalog-project card');
      const projectHead = h('div', 'project-heading');
      append(projectHead, h('h2', '', project.name), h('span', '', `${project.passed}/${project.total} решено`));
      projectSection.append(projectHead);
      for (const folder of project.folders) {
        const details = h('details', 'folder-block');
        details.open = hasFilters || Boolean(next && folder.tasks.some((task) => task.id === next.id));
        const summary = h('summary');
        const mini = h('span', 'folder-mini-progress');
        const miniFill = h('span'); miniFill.style.width = `${L.percent(folder.passed, folder.total)}%`; mini.append(miniFill);
        append(summary, h('span', 'folder-name', folder.name), mini, h('span', 'folder-count', `${folder.passed}/${folder.total}`));
        const items = h('div', 'folder-items');
        for (const lesson of lessonsForFolder(folder, folder.tasks)) items.append(lessonLink(lesson));
        for (const task of folder.tasks) items.append(taskLink(task));
        details.append(summary, items);
        projectSection.append(details);
      }
      fragment.append(projectSection);
    }
    container.replaceChildren(fragment);
  }

  function renderCourse() {
    document.title = 'Курс — Cogito';
    const fragment = document.createDocumentFragment();
    const head = heading('Весь учебный путь', 'Курс', 'Теория идёт перед задачами. Открывай папки в своём темпе — прогресс уже сохранён.');
    const actions = h('div', 'heading-actions');
    const refresh = h('button', 'button button-small button-secondary', 'Обновить');
    refresh.type = 'button';
    refresh.addEventListener('click', async () => {
      refresh.disabled = true;
      try { await loadDashboard(); showToast('Прогресс обновлён'); }
      catch (error) { showToast(error.message); }
      finally { refresh.disabled = false; }
    });
    actions.append(refresh); head.append(actions); fragment.append(head);
    const toolbar = h('section', 'course-toolbar');
    const search = h('div', 'search-box');
    const input = h('input'); input.type = 'search'; input.value = state.course.query;
    input.placeholder = 'Номер или название задачи'; input.setAttribute('aria-label', 'Поиск задачи по номеру и названию');
    search.append(input);
    const filters = h('div', 'filter-chips');
    filters.setAttribute('aria-label', 'Фильтры задач');
    const open = h('button', 'filter-chip', 'Нерешённые');
    const defense = h('button', 'filter-chip', 'Требуют защиты');
    for (const button of [open, defense]) button.type = 'button';
    open.setAttribute('aria-pressed', String(state.course.openOnly));
    defense.setAttribute('aria-pressed', String(state.course.defenseOnly));
    append(filters, open, defense); append(toolbar, search, filters); fragment.append(toolbar);
    const count = h('div', 'catalog-count'); fragment.append(count);
    const catalog = h('div'); fragment.append(catalog);
    const redraw = () => drawCourseCatalog(catalog, count);
    input.addEventListener('input', () => { state.course.query = input.value; redraw(); });
    open.addEventListener('click', () => { state.course.openOnly = !state.course.openOnly; open.setAttribute('aria-pressed', String(state.course.openOnly)); redraw(); });
    defense.addEventListener('click', () => { state.course.defenseOnly = !state.course.defenseOnly; defense.setAttribute('aria-pressed', String(state.course.defenseOnly)); redraw(); });
    root.replaceChildren(fragment);
    redraw();
  }

  function lessonCard(lesson, open = false) {
    const details = h('details', 'lesson-card card');
    details.dataset.lessonCard = lesson.id;
    details.open = open;
    const summary = h('summary');
    const icon = h('span', 'status-icon', '≡'); icon.setAttribute('aria-hidden', 'true');
    const title = h('span', 'lesson-card-title', lesson.title || lesson.id);
    title.append(h('span', 'lesson-card-id', lesson.id));
    append(summary, icon, title);
    const body = h('div', 'lesson-body');
    append(details, summary, body);
    details.addEventListener('toggle', () => { if (details.open) void loadLessonInto(lesson, body); });
    return { details, body };
  }

  async function loadLessonInto(lesson, body) {
    if (body.dataset.loaded === 'true' || body.dataset.loading === 'true') return;
    body.dataset.loading = 'true';
    const cached = state.lessonDetails.get(lesson.id);
    if (cached) {
      markdown.render(cached.body_md || 'В этой карточке пока нет текста.', body);
      body.dataset.loaded = 'true'; delete body.dataset.loading;
      return;
    }
    body.replaceChildren(h('p', 'muted', 'Открываю карточку…'));
    try {
      const full = await request(`/lessons/${encodeURIComponent(lesson.id)}`);
      if (!body.isConnected) return;
      state.lessonDetails.set(lesson.id, full);
      markdown.render(full.body_md || 'В этой карточке пока нет текста.', body);
      body.dataset.loaded = 'true';
    } catch (error) {
      if (!body.isConnected) return;
      const message = h('div', 'message message-error', error.message);
      const retry = h('button', 'button button-small button-secondary', 'Повторить');
      retry.type = 'button'; retry.addEventListener('click', () => void loadLessonInto(lesson, body));
      body.replaceChildren(message, retry);
    } finally { delete body.dataset.loading; }
  }

  function theoryFolders(lessons) {
    const folders = new Map();
    for (const lesson of lessons) {
      const key = lesson.folder_id || `block:${lesson.block}`;
      if (!folders.has(key)) folders.set(key, { key, lessons: [], sample: null });
      const folder = folders.get(key);
      folder.lessons.push(lesson);
      if (!folder.sample) folder.sample = state.tasks.find((task) => lesson.folder_id ? task.folder_id === lesson.folder_id : task.block === lesson.block);
    }
    const sample = (folder) => folder.sample || { id: '', block: folder.lessons[0]?.block || '' };
    return [...folders.values()].sort((a, b) => L.compareProjectOrder(sample(a), sample(b)) || L.compareCatalogOrder(sample(a), sample(b)));
  }

  function drawTheoryLibrary(container) {
    const query = state.theoryQuery.trim().toLocaleLowerCase('ru');
    const lessons = state.lessons.filter((lesson) => !query || `${lesson.id} ${lesson.title}`.toLocaleLowerCase('ru').includes(query));
    if (!lessons.length) {
      const empty = h('div', 'empty-state course-empty');
      append(empty, h('h2', '', state.lessons.length ? 'Такой карточки не нашлось' : 'Теория пока не добавлена'), h('p', '', state.lessons.length ? 'Попробуй другое слово или номер карточки.' : 'Условия задач по-прежнему доступны в разделе «Курс».'));
      container.replaceChildren(empty);
      return;
    }
    const fragment = document.createDocumentFragment();
    for (const folder of theoryFolders(lessons)) {
      const section = h('section', 'theory-folder');
      const title = h('h2', '', folder.sample?.folder_name || (folder.lessons[0].block ? `Блок ${folder.lessons[0].block}` : 'Теория'));
      title.append(h('span', '', `${folder.lessons.length} ${plural(folder.lessons.length, 'карточка', 'карточки', 'карточек')}`));
      const list = h('div', 'lesson-list');
      folder.lessons.sort((a, b) => (a.order || 0) - (b.order || 0) || L.naturalCompare(a.id, b.id));
      for (const lesson of folder.lessons) {
        const card = lessonCard(lesson, Boolean(readRoute().lessonId === lesson.id));
        list.append(card.details);
      }
      append(section, title, list); fragment.append(section);
    }
    container.replaceChildren(fragment);
    const selectedId = readRoute().lessonId;
    if (selectedId) {
      const selected = [...container.querySelectorAll('[data-lesson-card]')].find((node) => node.dataset.lessonCard === selectedId);
      if (selected) {
        selected.scrollIntoView({ block: 'start' });
        const body = selected.querySelector('.lesson-body');
        const lesson = state.lessons.find((item) => item.id === selectedId);
        if (lesson) void loadLessonInto(lesson, body);
      }
    }
  }

  function renderTheory() {
    document.title = 'Теория — Cogito';
    const fragment = document.createDocumentFragment();
    fragment.append(heading('Библиотека курса', 'Теория под рукой', 'Короткие карточки с примерами и ответами для самопроверки. Удобно перечитать с телефона.', 'page-heading theory-intro'));
    const search = h('div', 'search-box theory-search');
    const input = h('input'); input.type = 'search'; input.value = state.theoryQuery;
    input.placeholder = 'Найти тему или карточку'; input.setAttribute('aria-label', 'Поиск по теории');
    search.append(input); fragment.append(search);
    const library = h('div'); fragment.append(library);
    input.addEventListener('input', () => { state.theoryQuery = input.value; drawTheoryLibrary(library); });
    root.replaceChildren(fragment);
    drawTheoryLibrary(library);
  }

  function safeDownloadUrl(release) {
    const value = release?.download_url || '/extension/download';
    return value.startsWith('/') && !value.startsWith('//') ? value : '/extension/download';
  }

  function renderVSCode() {
    document.title = 'VS Code — Cogito';
    const fragment = document.createDocumentFragment();
    fragment.append(heading('Рабочее место', 'Как начать в VS Code', 'Три шага — и можно писать код, запускать проверку и продолжать курс с того же места.'));
    const hero = h('section', 'vscode-hero');
    const intro = h('article', 'vscode-intro card');
    append(intro, h('p', 'eyebrow', 'Всё для практики'), h('h2', '', 'Не просто читать — писать настоящий код'), h('p', '', 'Расширение Cogito показывает задачи и теорию рядом с редактором. Проверка запускается прямо в VS Code, а результат появляется здесь автоматически.'));
    const download = h('article', 'download-card card');
    const release = state.extension;
    const version = release?.version || '';
    download.append(h('span', 'version-pill', version ? `Версия ${version}` : 'Расширение Cogito'));
    download.append(h('h2', '', version ? 'Готово к установке' : 'Установочный пакет'));
    download.append(h('p', '', version ? 'Скачай один файл — больше ничего настраивать не нужно.' : 'Если файл пока недоступен, загляни сюда немного позже.'));
    if (version) {
      const link = h('a', 'button button-primary button-full', 'Скачать расширение ↓');
      link.href = safeDownloadUrl(release); link.setAttribute('download', ''); download.append(link);
    }
    append(hero, intro, download); fragment.append(hero);

    const section = h('section', 'install-section');
    const title = h('div', 'section-title'); title.append(h('h2', '', 'Три шага до первой проверки')); section.append(title);
    const steps = h('div', 'install-steps');
    const stepData = [
      ['Скачай пакет', version ? `Сохрани файл cogito-${version}.vsix на компьютер.` : 'Скачай установочный файл расширения, когда он станет доступен.'],
      ['Добавь в VS Code', 'Открой «Расширения» → «⋯» → «Install from VSIX…» и выбери скачанный файл.'],
      ['Войди в курс', 'Выполни команду «Cogito: Войти», затем скачай задачи и открой первую.'],
    ];
    stepData.forEach(([stepTitle, text], index) => {
      const step = h('article', 'install-step card');
      append(step, h('span', 'step-number', index + 1), h('h3', '', stepTitle), h('p', '', text)); steps.append(step);
    });
    section.append(steps); fragment.append(section);
    const note = h('section', 'note-card card');
    const noteCopy = h('div'); append(noteCopy, h('h3', '', 'Обновления придут сами'), h('p', '', 'После установки расширение проверяет новые версии. Тебе не нужно следить за релизами.'));
    append(note, h('span', 'note-icon', '✓'), noteCopy); fragment.append(note);
    const deep = h('section', 'deeplink-explainer panel');
    append(deep, h('h2', '', 'Переходы из кабинета'), h('p', '', 'Кнопка «Открыть в VS Code» запускает установленное расширение и сразу показывает выбранную задачу. Если ничего не произошло, сначала установи расширение по шагам выше.'));
    fragment.append(deep);
    root.replaceChildren(fragment);
  }

  function attemptLabel(progress, taskStatus) {
    if (!progress) return 'Проверок пока не было';
    if (taskStatus === 'defense') return 'Тесты пройдены, ждёт защиты';
    if (taskStatus === 'passed') return 'Все тесты пройдены';
    if (['failed', 'error', 'timeout'].includes(L.normalizeStatus(progress.status))) return 'Есть ошибки — можно попробовать ещё раз';
    return 'Попытка сохранена';
  }

  function renderTaskPage(meta, detail, hints) {
    const fragment = document.createDocumentFragment();
    const taskState = stateOf(meta);
    const breadcrumbs = h('nav', 'breadcrumbs'); breadcrumbs.setAttribute('aria-label', 'Хлебные крошки');
    const back = h('a', '', '← Курс'); back.href = viewUrl('course'); back.dataset.nav = 'course';
    append(breadcrumbs, back, h('span', '', '/'), h('span', '', meta.id)); fragment.append(breadcrumbs);
    const header = h('header', 'task-header');
    const copy = h('div');
    append(copy, h('p', 'eyebrow', [meta.project_name, meta.folder_name].filter(Boolean).join(' · ') || 'Задача курса'), h('h1', '', detail.title || meta.title || meta.id), h('p', 'task-header-meta', `${meta.id} · версия ${meta.version}`));
    append(header, copy, statusBadge(taskState)); fragment.append(header);
    const actions = h('div', 'task-actionbar card');
    const open = h('a', 'button button-primary', taskState === 'defense' ? 'Защитить в VS Code ↗' : 'Открыть в VS Code ↗'); open.href = vscodeUrl(meta.id);
    const install = h('a', 'download-note', 'Нет расширения? Скачай'); install.href = viewUrl('vscode'); install.dataset.nav = 'vscode';
    append(actions, open, install); fragment.append(actions);
    const layout = h('div', 'task-layout');
    const statement = h('article', 'task-statement card');
    const body = h('div'); markdown.render(detail.statement_md || 'У этой задачи пока нет описания.', body); statement.append(body);
    const aside = h('aside', 'task-aside');
    const progress = progressFor(meta);
    const attempt = h('section', 'attempt-card card');
    const attemptStatus = h('div', 'attempt-status');
    attemptStatus.append(statusBadge(taskState));
    attempt.append(h('h2', '', 'Последняя попытка'), attemptStatus);
    const statusText = h('p', 'muted', attemptLabel(progress, taskState)); statusText.style.fontSize = '12px'; statusText.style.margin = '0 0 15px'; attempt.append(statusText);
    const stats = h('div', 'attempt-stats');
    const tests = h('div', 'attempt-stat'); append(tests, h('strong', '', progress ? `${progress.passed_tests}/${progress.total_tests}` : '—'), h('span', '', 'тестов пройдено'));
    const attempts = h('div', 'attempt-stat'); append(attempts, h('strong', '', progress?.attempts ?? '0'), h('span', '', plural(progress?.attempts || 0, 'попытка', 'попытки', 'попыток')));
    append(stats, tests, attempts); attempt.append(stats);
    if (progress?.last_run_at) {
      const date = new Date(progress.last_run_at);
      if (!Number.isNaN(date.valueOf())) attempt.append(h('p', 'attempt-date', `Последняя проверка: ${date.toLocaleString('ru-RU')}`));
    }
    const note = h('section', 'task-aside-note card');
    append(note, h('h3', '', taskState === 'defense' ? 'Объясни своё решение' : 'Где решать?'), h('p', '', taskState === 'defense' ? 'Тесты уже пройдены. Открой задачу в VS Code и пройди короткую защиту понимания.' : 'Код пишется в VS Code. Там же расширение запускает тесты и сохраняет результат в твоём кабинете.'));
    append(aside, attempt, note); append(layout, statement, aside); fragment.append(layout);

    const theoryIds = Array.isArray(detail.theory) ? detail.theory : (meta.theory || []);
    if (theoryIds.length) {
      const theory = h('section', 'task-theory card');
      const title = h('div', 'section-title'); const titleCopy = h('div');
      append(titleCopy, h('h2', '', 'Теория к этой задаче'), h('p', '', 'Сначала можно освежить правило, потом вернуться к условию.'));
      title.append(titleCopy); theory.append(title);
      const list = h('div', 'lesson-list');
      for (const id of theoryIds) {
        const lesson = state.lessons.find((item) => item.id === id) || { id, title: id, order: 0 };
        const card = lessonCard(lesson, true);
        list.append(card.details);
        void loadLessonInto(lesson, card.body);
      }
      theory.append(list); fragment.append(theory);
    }

    const hintsPanel = h('section', 'task-hints card');
    const hintsTitle = h('div', 'section-title'); const hintsCopy = h('div');
    append(hintsCopy, h('h2', '', 'Подсказки'), h('p', '', 'Открывай по одной, если хочешь немного направления без готового решения.'));
    hintsTitle.append(hintsCopy); hintsPanel.append(hintsTitle);
    if (hints.length) {
      const list = h('div', 'hint-list');
      for (const hint of hints) {
        const item = h('details', 'hint-item');
        item.append(h('summary', '', `${hint.level}. ${hint.title}`));
        const content = h('div'); markdown.render(hint.content || '', content); item.append(content); list.append(item);
      }
      hintsPanel.append(list);
    } else hintsPanel.append(h('p', 'muted', 'Для этой задачи пока нет отдельных подсказок. Попробуй перечитать пример и теорию выше.'));
    fragment.append(hintsPanel);
    root.replaceChildren(fragment);
  }

  async function renderTask(route) {
    const meta = state.tasks.find((task) => task.id.toLowerCase() === route.taskId.toLowerCase());
    document.title = `${meta?.title || route.taskId || 'Задача'} — Cogito`;
    if (!meta) {
      const empty = h('div', 'empty-state card');
      append(empty, h('h2', '', 'Такой задачи не нашлось'), h('p', '', 'Возможно, ссылка устарела. Все доступные задачи собраны в курсе.'));
      const back = h('a', 'button button-primary', 'Перейти к курсу'); back.href = viewUrl('course'); back.dataset.nav = 'course'; empty.append(back);
      root.replaceChildren(empty); return;
    }
    const current = ++state.taskEpoch;
    loading('Открываю условие задачи…');
    const [detailResult, hintsResult] = await Promise.allSettled([
      request(`/tasks/${encodeURIComponent(meta.id)}`),
      request(`/tasks/${encodeURIComponent(meta.id)}/hints?level=3`),
    ]);
    if (current !== state.taskEpoch || readRoute().view !== 'task' || readRoute().taskId !== route.taskId) return;
    if (detailResult.status === 'rejected') {
      errorState(detailResult.reason, () => void renderTask(route));
      return;
    }
    renderTaskPage(meta, detailResult.value, hintsResult.status === 'fulfilled' ? (hintsResult.value.hints || []) : []);
  }

  function renderRoute({ focus = false } = {}) {
    if (!state.user) return;
    const route = readRoute();
    setActiveNav(route);
    if (route.view === 'task') void renderTask(route);
    else if (route.view === 'course') renderCourse();
    else if (route.view === 'theory') renderTheory();
    else if (route.view === 'vscode') renderVSCode();
    else renderToday();
    if (focus) {
      window.scrollTo({ top: 0, behavior: 'instant' });
      root.focus({ preventScroll: true });
    }
  }

  function clearStudentData() {
    state.user = null; state.tasks = []; state.progress = []; state.understanding = [];
    state.evidenceByTask = new Map(); state.evidenceAvailable = false; state.account = null;
    state.lessons = []; state.lessonDetails = new Map(); state.taskEpoch++;
    root.replaceChildren();
  }

  async function loadDashboard() {
    const epoch = state.epoch;
    loading('Собираю твой курс…');
    const [tasks, progress] = await Promise.all([request('/tasks'), request('/progress/me')]);
    const optional = await Promise.allSettled([
      request('/progress/me/understanding'), request('/ai/me'), request('/lessons'),
    ]);
    if (epoch !== state.epoch || !state.token) return;
    state.tasks = Array.isArray(tasks) ? tasks : [];
    state.progress = Array.isArray(progress) ? progress : [];
    const [understanding, account, lessons] = optional;
    state.evidenceAvailable = understanding.status === 'fulfilled' && Array.isArray(understanding.value);
    state.understanding = state.evidenceAvailable ? understanding.value : [];
    state.evidenceByTask = L.newestEvidenceByTask(state.understanding);
    state.account = account.status === 'fulfilled' ? account.value : null;
    state.lessons = lessons.status === 'fulfilled' && Array.isArray(lessons.value) ? lessons.value : [];
    renderRoute();
  }

  async function enter(token) {
    const epoch = ++state.epoch;
    clearStudentData();
    state.token = token;
    localStorage.setItem('ego_student_token', token);
    try {
      const user = await request('/auth/me');
      if (epoch !== state.epoch || state.token !== token) return;
      state.user = user;
      showCabinet();
      try { await loadDashboard(); }
      catch (error) {
        if (epoch !== state.epoch) return;
        if (error.status === 401) {
          localStorage.removeItem('ego_student_token'); state.token = null; clearStudentData();
          showAuth('Сессия закончилась. Войди ещё раз.');
        } else errorState(error, () => void loadDashboard().catch((failure) => errorState(failure, () => location.reload())));
      }
    } catch (error) {
      if (epoch !== state.epoch || state.token !== token) return;
      if (error.status === 401) {
        localStorage.removeItem('ego_student_token'); state.token = null;
        showAuth('Сессия закончилась. Войди ещё раз.');
      } else showAuth(error.message);
    }
  }

  authForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    if (!state.providers?.local) return;
    const fields = new FormData(authForm);
    const body = { username: String(fields.get('username')).trim(), password: String(fields.get('password')) };
    const button = $('auth-submit');
    button.disabled = true; button.textContent = state.registering ? 'Создаю…' : 'Вхожу…';
    authError.classList.add('hidden');
    try {
      const result = await request(state.registering ? '/auth/register' : '/auth/login', { method: 'POST', body });
      authForm.reset(); setMode(false); await enter(result.access_token);
    } catch (error) {
      authError.textContent = error.status === 401 ? 'Логин или пароль не подошли.' : error.status === 409 ? 'Такой логин уже занят.' : error.message;
      authError.classList.remove('hidden');
    } finally {
      button.disabled = false; button.textContent = state.registering ? 'Создать аккаунт →' : 'Войти →';
    }
  });

  $('auth-switch').addEventListener('click', () => setMode(!state.registering));
  $('logout').addEventListener('click', () => {
    state.epoch++; cancelForgejo(); clearStudentData();
    state.token = null; localStorage.removeItem('ego_student_token');
    setMode(false); showAuth();
  });

  function cancelForgejo() {
    attempt++; popup?.close(); channel?.close(); popup = channel = null;
    $('forgejo-login').disabled = false; $('forgejo-login').textContent = 'Войти через Forgejo →';
    $('forgejo-cancel').classList.add('hidden');
  }

  async function forgejoLogin() {
    const current = ++attempt;
    popup = window.open('about:blank', '_blank');
    if (!popup) { showAuth('Разреши новую вкладку для входа через Forgejo.'); return; }
    popup.opener = null;
    $('forgejo-login').disabled = true; $('forgejo-login').textContent = 'Ожидаю вход…';
    $('forgejo-cancel').classList.remove('hidden');
    const encode = (bytes) => btoa(String.fromCharCode(...bytes)).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
    try {
      const verifier = encode(crypto.getRandomValues(new Uint8Array(32)));
      const digest = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(verifier));
      const flow = await request('/auth/forgejo/start', { method: 'POST', body: { client: 'browser', code_challenge: encode(new Uint8Array(digest)) } });
      if (current !== attempt) return;
      if (new URL(flow.authorization_url).origin !== location.origin) throw new Error('Проверь адрес сервиса для входа через Forgejo.');
      let ticket = '';
      let failed = false;
      channel = new BroadcastChannel(`ego-forgejo-${flow.state}`);
      channel.onmessage = (event) => {
        if (event.data?.error === 'login_failed') failed = true;
        if (typeof event.data?.ticket === 'string' && /^[A-Za-z0-9_-]{43}$/.test(event.data.ticket)) ticket = event.data.ticket;
      };
      popup.location.href = flow.authorization_url;
      const deadline = Date.now() + flow.expires_in * 1000;
      while (current === attempt && Date.now() < deadline) {
        await new Promise((resolve) => setTimeout(resolve, 1000));
        if (current !== attempt) return;
        if (failed) throw new Error('Вход не завершён или регистрация закрыта. Попробуй другой способ входа.');
        if (!ticket) continue;
        const result = await request('/auth/forgejo/exchange', { method: 'POST', body: { state: flow.state, code_verifier: verifier, ticket } });
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

  document.addEventListener('click', (event) => {
    const taskAnchor = event.target.closest('[data-task-link]');
    if (taskAnchor && isPlainNavigation(event)) {
      event.preventDefault(); navigate(taskUrl(taskAnchor.dataset.taskLink)); return;
    }
    const lessonAnchor = event.target.closest('[data-lesson-link]');
    if (lessonAnchor && isPlainNavigation(event)) {
      event.preventDefault(); navigate(viewUrl('theory', lessonAnchor.dataset.lessonLink)); return;
    }
    const navAnchor = event.target.closest('[data-nav]');
    if (navAnchor && isPlainNavigation(event)) {
      event.preventDefault(); navigate(viewUrl(navAnchor.dataset.nav));
    }
  });
  window.addEventListener('popstate', () => renderRoute({ focus: true }));

  request('/auth/providers').then((providers) => {
    state.providers = providers;
    $('forgejo-login').classList.toggle('hidden', !providers.forgejo);
    $('local-fields').classList.toggle('hidden', !providers.local);
    $('auth-switch').classList.toggle('hidden', !providers.local || !providers.registration);
    $('provider-divider').classList.toggle('hidden', !providers.local || !providers.forgejo);
    setMode(false);
    if (!providers.local && !providers.forgejo) showAuth('Вход пока не настроен. Попробуй заглянуть позже.');
  }).catch((error) => showAuth(error.message));

  fetch('/extension/latest', { headers: { Accept: 'application/json' } })
    .then((response) => response.ok ? response.json() : null)
    .then((release) => {
      if (release && /^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?$/.test(release.version || '')) {
        state.extension = release;
        if (state.user && readRoute().view === 'vscode') renderVSCode();
      }
    }).catch(() => {});

  fetch('/static/branding/brand.json', { headers: { Accept: 'application/json' } })
    .then((response) => response.ok ? response.json() : null)
    .then((brand) => {
      if (!brand) return;
      document.querySelectorAll('[data-brand-name]').forEach((node) => { node.textContent = brand.name || 'Cogito'; });
      if (brand.logo_url && brand.logo_url.startsWith('/static/branding/')) {
        document.querySelectorAll('.brand-mark').forEach((image) => { image.src = '/static/branding/cogito-mark.png'; });
      }
    }).catch(() => {});

  if (state.token) void enter(state.token);
  else showAuth();
})();
