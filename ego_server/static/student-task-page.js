import { mountTutor } from './student-tutor.js';
import { isPlainNavigation, taskTabs } from './student-navigation.js';

export function mountTaskPage({ root, task, detail, initialTab, catalogUrl, onBack, onTab,
  getProgress, getSubmission, getAccount, getStatus, conversationFor, request,
  renderMarkdown, isCurrentStudent, onAccount, onDefense, onRefresh }) {
  root.innerHTML = `
    <a class="back-link" href="/student">← Все задачи</a>
    <header class="task-heading">
      <div><p class="eyebrow" data-task-meta></p><h1 id="task-title" tabindex="-1"></h1></div>
      <span class="badge" data-task-status></span>
    </header>
    <div class="task-overview"><p data-task-progress></p><div class="code-actions"><button class="quiet-button" data-refresh-progress type="button" aria-label="Обновить статус задачи">Обновить</button><button class="primary-button compact" data-task-next type="button"></button></div></div>
    <div class="task-tabs" role="tablist" aria-label="Разделы задачи">
      <button id="task-tab-statement" role="tab" aria-controls="task-panel-statement" type="button">Условие</button>
      <button id="task-tab-code" role="tab" aria-controls="task-panel-code" type="button">Стартовый код</button>
      <button id="task-tab-help" role="tab" aria-controls="task-panel-help" type="button">Помощник</button>
      <button id="task-tab-defense" role="tab" aria-controls="task-panel-defense" type="button">Защита</button>
    </div>
    <section id="task-panel-statement" class="task-panel" role="tabpanel" aria-labelledby="task-tab-statement" tabindex="0">
      <div class="statement"></div><div class="panel-footer"><button class="quiet-button" data-open-code type="button">К стартовому коду →</button></div>
    </section>
    <section id="task-panel-code" class="task-panel" role="tabpanel" aria-labelledby="task-tab-code" tabindex="0" hidden>
      <div class="section-heading"><div><h2>Стартовый код</h2><p class="muted">Решай задачу в VS Code и запускай проверку в расширении Cogito.</p></div><span class="badge">Python</span></div>
      <pre class="code-block" tabindex="0"><code></code></pre>
      <div class="code-actions"><button class="quiet-button" data-copy-code type="button">Копировать код</button><span role="status" class="muted" data-copy-status></span></div>
      <div class="panel-footer"><p class="muted">Нужен разбор? Во вкладке «Помощник» можно задать вопрос и приложить свой код.</p><button class="quiet-button" data-open-help type="button">К помощнику →</button></div>
    </section>
    <section id="task-panel-help" class="task-panel" role="tabpanel" aria-labelledby="task-tab-help" tabindex="0" hidden></section>
    <section id="task-panel-defense" class="task-panel" role="tabpanel" aria-labelledby="task-tab-defense" tabindex="0" hidden></section>`;
  const find = selector => root.querySelector(selector);
  const heading = find('#task-title');
  const copyStatus = find('[data-copy-status]');
  const make = (tag, className, text) => {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (text) element.textContent = text;
    return element;
  };
  const back = find('.back-link'); back.href = catalogUrl;
  back.addEventListener('click', event => { if (isPlainNavigation(event)) { event.preventDefault(); onBack(); } });
  heading.textContent = task.title || task.task_id;
  find('[data-task-meta]').textContent = `${task.block ? `Блок ${task.block} · ` : ''}${task.task_id || task.id} · версия ${task.version}`;
  renderMarkdown(detail.statement_md || 'У этой задачи пока нет описания.', find('#task-panel-statement .statement'));
  const stub = detail.stub_py || '';
  find('.code-block code').textContent = stub || 'Для этой задачи стартовый код не задан.';
  find('[data-copy-code]').disabled = !stub;
  find('[data-copy-code]').addEventListener('click', async () => {
    try { await navigator.clipboard.writeText(stub); copyStatus.textContent = 'Код скопирован'; }
    catch { copyStatus.textContent = 'Не удалось скопировать. Выдели код и скопируй его вручную.'; }
  });
  const panels = new Map(taskTabs.map(name => [name, find(`#task-panel-${name}`)]));
  const tabs = new Map(taskTabs.map(name => [name, find(`#task-tab-${name}`)]));
  let selected = 'statement';
  let helpMounted = false;
  let defenseMounted = false;

  function tutorOptions(target, kind, submission = null) {
    return { target, task, submission, getAccount, request, renderMarkdown, isCurrentStudent, onAccount,
      conversation: conversationFor(kind, submission),
      allowedModes: kind === 'defense' ? ['defend'] : ['hint', 'explain'],
      title: kind === 'defense' ? 'Диалог о твоём решении' : 'Разберём задачу вместе',
      onDefense: session => { onDefense(session); refreshProgress(); }
    };
  }

  function mountHelp() {
    if (helpMounted) return;
    helpMounted = true;
    const panel = panels.get('help');
    panel.append(make('h2', '', 'Помощь с задачей'), make('p', 'muted', 'Опиши, где застрял. Можно попросить подсказку или объяснение и приложить свой код.'));
    mountTutor(tutorOptions(panel, 'help'));
    const hints = make('details', 'reference-hints');
    hints.append(make('summary', '', 'Подсказки к условию'));
    const content = make('div', 'hints'); hints.append(content); panel.append(hints);
    let loaded = false, loading = false;
    async function loadHints() {
      if (loading || loaded || !isCurrentStudent()) return;
      loading = true; content.textContent = 'Загружаю подсказки…';
      try {
        const data = await request(`/tasks/${encodeURIComponent(task.id)}/hints?level=3`);
        if (!isCurrentStudent()) return;
        content.replaceChildren();
        for (const hint of data.hints || []) {
          const item = make('section', 'hint-item'); item.append(make('h3', '', hint.title));
          const body = make('div', 'statement'); renderMarkdown(hint.content, body); item.append(body); content.append(item);
        }
        if (!data.hints?.length) content.textContent = 'Отдельных подсказок к этой задаче пока нет.';
        loaded = true;
      } catch (failure) {
        content.replaceChildren(make('p', 'error', failure.message));
        const retry = make('button', 'quiet-button', 'Повторить'); retry.type = 'button';
        retry.addEventListener('click', loadHints); content.append(retry);
      } finally { loading = false; }
    }
    hints.addEventListener('toggle', () => { if (hints.open) void loadHints(); });
  }

  function mountDefense() {
    if (defenseMounted) return;
    defenseMounted = true;
    const panel = panels.get('defense'); panel.replaceChildren();
    const progress = getProgress(), submission = getSubmission();
    panel.append(make('h2', '', 'Проверка понимания'), make('p', 'muted', 'Объясни механизм своего решения, разбери пример и примени идею к новому случаю. Агент задаёт по одному вопросу.'));
    const steps = make('ol', 'defense-steps');
    for (const label of ['Объяснить код', 'Проследить выполнение', 'Разобрать новый случай']) steps.append(make('li', '', label));
    panel.append(steps);
    if (submission?.understanding === 'confirmed') {
      const result = make('div', 'result-card');
      result.append(make('h3', '', 'Понимание подтверждено'), make('p', 'muted', 'Ты прошёл защиту этой проверенной версии решения.'));
      for (const evidence of submission.evidence || []) {
        const quote = make('blockquote', '', evidence.quote); result.append(quote);
      }
      panel.append(result); return;
    }
    if (progress?.status !== 'passed' || !submission) {
      const empty = make('div', 'empty-state');
      empty.append(make('h3', '', 'Сначала пройди проверку кода'), make('p', 'muted', progress?.status === 'passed'
        ? 'Для этой попытки ещё нет материала для защиты. Повтори серверную проверку в расширении Cogito и обнови страницу.'
        : 'Реши задачу в VS Code и запусти «Проверить» в Cogito. После успешных тестов здесь появится защита твоего решения.'));
      const action = make('button', 'quiet-button', 'Посмотреть стартовый код'); action.type = 'button';
      action.addEventListener('click', () => activateTab('code', { focus: true })); empty.append(action); panel.append(empty); return;
    }
    if (submission.understanding === 'needs_review') panel.append(make('p', 'notice', 'В прошлой защите остались вопросы. Разбери их с помощником или наставником, затем попробуй ещё раз.'));
    panel.append(make('p', 'muted', 'Обсуждаем код из последней успешно проверенной попытки этой версии задачи.'));
    mountTutor(tutorOptions(panel, 'defense', submission));
  }

  function activateTab(name, { notify = true, focus = false } = {}) {
    selected = taskTabs.includes(name) ? name : 'statement';
    if (selected === 'help') mountHelp();
    if (selected === 'defense') mountDefense();
    for (const [key, button] of tabs) {
      button.setAttribute('aria-selected', String(key === selected)); button.tabIndex = key === selected ? 0 : -1;
      panels.get(key).hidden = key !== selected;
    }
    if (focus) tabs.get(selected).focus({ preventScroll: true });
    if (focus) tabs.get(selected).scrollIntoView({ block: 'nearest', inline: 'nearest' });
    if (notify) onTab(selected);
  }
  for (const [name, button] of tabs) {
    button.addEventListener('click', () => activateTab(name));
    button.addEventListener('keydown', event => {
      const index = taskTabs.indexOf(name);
      const target = event.key === 'ArrowRight' ? (index + 1) % taskTabs.length
        : event.key === 'ArrowLeft' ? (index + taskTabs.length - 1) % taskTabs.length
        : event.key === 'Home' ? 0 : event.key === 'End' ? taskTabs.length - 1 : -1;
      if (target < 0) return;
      event.preventDefault(); activateTab(taskTabs[target], { focus: true });
    });
  }
  find('[data-open-code]').addEventListener('click', () => activateTab('code', { focus: true }));
  find('[data-open-help]').addEventListener('click', () => activateTab('help', { focus: true }));
  find('[data-task-next]').addEventListener('click', () => activateTab(getStatus().key === 'defense' ? 'defense' : 'code', { focus: true }));
  find('[data-refresh-progress]').addEventListener('click', onRefresh);

  function refreshProgress() {
    // A tutor reply may arrive after another task has replaced this page.
    if (!root.contains(heading)) return;
    const progress = getProgress(), status = getStatus();
    find('[data-task-status]').className = `badge ${status.key}`;
    find('[data-task-status]').textContent = status.label;
    find('[data-task-progress]').textContent = progress
      ? `${progress.passed_tests}/${progress.total_tests} тестов · попыток: ${progress.attempts}` : 'Проверок кода пока нет';
    find('[data-task-next]').textContent = status.key === 'defense' ? 'К защите →' : 'К стартовому коду →';
    find('[data-task-next]').hidden = status.key === 'passed';
    defenseMounted = false;
    if (selected === 'defense') mountDefense();
  }
  refreshProgress(); activateTab(initialTab, { notify: false });
  return { activateTab, refreshProgress };
}
