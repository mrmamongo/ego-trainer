export function mountTutor({ target, task, conversation, getAccount, submission, request,
  renderMarkdown, isCurrentStudent, onAccount, onDefense }) {
  const make = (tag, className, text) => {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (text) element.textContent = text;
    return element;
  };
  const tutor = make('section', 'tutor');
  tutor.setAttribute('aria-label', 'Учебный помощник');
  const header = make('div', 'tutor-head');
  const status = make('small');
  header.append(make('strong', '', 'Учебный помощник'), status);
  const modes = make('div', 'tutor-modes');
  const buttons = new Map();
  const restart = make('button', '', 'Новый диалог'); restart.type = 'button';
  restart.addEventListener('click', () => {
    if (conversation.busy || conversation.pending) return;
    conversation.session = null; conversation.error = ''; conversation.draft = ''; draw();
  });
  const chat = make('div', 'tutor-chat');
  chat.setAttribute('aria-live', 'polite');
  chat.setAttribute('aria-relevant', 'additions text');
  const codeField = make('details', 'tutor-code');
  codeField.append(make('summary', '', 'Добавить свой код к вопросу'));
  const code = make('textarea');
  code.rows = 6; code.maxLength = 24000; code.value = conversation.code;
  code.setAttribute('aria-label', 'Твой код для подсказки или объяснения');
  code.placeholder = 'Вставь код, который хочешь разобрать';
  code.addEventListener('input', () => { conversation.code = code.value; });
  codeField.append(code);
  const form = make('form', 'tutor-composer');
  const input = make('textarea');
  input.rows = 3; input.maxLength = 4000; input.value = conversation.draft;
  input.setAttribute('aria-label', 'Сообщение учебному помощнику');
  input.placeholder = 'Напиши вопрос или объясни ход своего решения…';
  input.addEventListener('input', () => { conversation.draft = input.value; });
  const send = make('button', 'tutor-send', 'Отправить'); send.type = 'submit';
  const error = make('p', 'tutor-error'); error.setAttribute('role', 'alert');
  const retry = make('button', 'tutor-retry', 'Повторить получение ответа'); retry.type = 'button';
  retry.addEventListener('click', () => { void sendMessage(); });
  form.append(input, send);
  tutor.append(header, modes, chat, codeField, error, retry, form);
  target.append(tutor);

  function draw() {
    if (!isCurrentStudent()) return;
    const access = getAccount();
    const session = conversation.session;
    const terminal = session && session.status !== 'active';
    status.textContent = conversation.busy ? 'Готовлю и проверяю ответ…'
      : terminal ? (session.status === 'confirmed' ? 'Понимание подтверждено' : 'Нужен разбор с наставником')
      : access?.available ? 'Подсказка · объяснение · защита' : (access?.reason || 'Сейчас недоступен');
    for (const [mode, button] of buttons) {
      button.disabled = conversation.busy || Boolean(conversation.pending) || !access?.available;
      button.setAttribute('aria-pressed', String(mode === conversation.mode));
    }
    codeField.hidden = conversation.mode === 'defend';
    restart.hidden = conversation.mode === 'defend' || !session;
    restart.disabled = conversation.busy || Boolean(conversation.pending) || !access?.available;
    code.disabled = conversation.busy || Boolean(conversation.pending) || !access?.available;
    input.disabled = conversation.busy || terminal || Boolean(conversation.pending) || !access?.available;
    send.disabled = input.disabled;
    send.textContent = conversation.busy ? 'Думаю…' : 'Отправить';
    retry.hidden = !conversation.pending || conversation.busy;
    error.hidden = !conversation.error;
    error.textContent = conversation.error;
    input.value = conversation.draft;
    chat.replaceChildren();
    if (!session?.messages.length) {
      chat.append(make('p', 'tutor-empty', conversation.mode === 'defend'
        ? 'Обсудим твой код из успешно проверенной попытки.'
        : 'Спроси о выбранной задаче. Помощник даст направление и поможет разобраться.'));
    }
    for (const message of session?.messages || []) {
      const item = make('article', 'tutor-message' + (message.role === 'user' ? ' user' : ''));
      item.append(make('strong', 'tutor-message-name', message.role === 'user' ? 'Ты' : 'Помощник'));
      const body = make('div', 'statement');
      renderMarkdown(message.content, body); item.append(body); chat.append(item);
    }
    chat.scrollTop = chat.scrollHeight;
  }
  conversation.changed = draw;

  async function ensureSession() {
    if (conversation.session) return;
    const session = await request('/ai/sessions', { method: 'POST', body: {
      task_id: task.id, mode: conversation.mode,
      ...(conversation.mode === 'defend' ? { submission_id: submission.id }
        : { student_code: conversation.code })
    } });
    if (!isCurrentStudent()) return;
    conversation.session = session;
  }

  async function refreshAccess() {
    try {
      const next = await request('/ai/me');
      if (!isCurrentStudent()) return;
      onAccount(next);
    } catch { /* The original request error remains visible. */ }
  }

  async function sendMessage(firstQuestion = false) {
    if (conversation.busy || !isCurrentStudent()) return;
    if (!firstQuestion && !conversation.pending && !conversation.draft.trim()) return;
    conversation.busy = true; conversation.error = ''; draw();
    try {
      await ensureSession();
      if (!isCurrentStudent()) return;
      // Reopening an existing defense must not buy another first question.
      if (firstQuestion && conversation.session.messages.length) return;
      if (!conversation.pending) {
        conversation.pending = { sessionId: conversation.session.id, body: {
          text: firstQuestion ? '' : conversation.draft.trim(), request_id: crypto.randomUUID(),
          ...(conversation.mode === 'defend' ? {} : { student_code: conversation.code })
        } };
      }
      const pending = conversation.pending;
      const session = await request(`/ai/sessions/${encodeURIComponent(pending.sessionId)}/messages`, {
        method: 'POST', body: pending.body
      });
      if (!isCurrentStudent()) return;
      conversation.session = session; conversation.pending = null; conversation.draft = '';
      onAccount(session.account);
      if (session.mode === 'defend' && session.status !== 'active') onDefense(session);
    } catch (failure) {
      if (!isCurrentStudent()) return;
      if (failure.status && failure.status !== 409) conversation.pending = null;
      conversation.error = conversation.pending
        ? 'Ответ пока не получен. Повтори получение: отправится тот же запрос без повторного списания.'
        : (failure.message || 'Помощник временно недоступен.');
      await refreshAccess();
    } finally {
      conversation.busy = false;
      if (isCurrentStudent()) conversation.changed?.();
    }
  }

  const addMode = (label, mode) => {
    const button = make('button', '', label); button.type = 'button';
    button.addEventListener('click', () => {
      if (conversation.busy || conversation.pending) return;
      if (conversation.mode !== mode) {
        conversation.mode = mode; conversation.session = null; conversation.error = '';
      }
      draw();
      if (mode === 'defend') void sendMessage(true);
    });
    modes.append(button); buttons.set(mode, button);
  };
  addMode('Подсказка', 'hint'); addMode('Объяснить', 'explain');
  if (submission && submission.understanding !== 'confirmed') addMode('Защитить решение', 'defend');
  modes.append(restart);
  form.addEventListener('submit', event => { event.preventDefault(); void sendMessage(); });
  draw();
}
