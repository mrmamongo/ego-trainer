<script lang="ts">
  import { onMount, onDestroy, tick } from 'svelte';
  import { getCatalog, type CatalogTaskDTO } from '../api';
  import { getSettings, listChats, newChat, readChat, deleteChat, streamChat,
    type ChatSession, type ChatMessage, type ChatProposal, type SettingsDraft, type TaskDraft } from '../consoleApi';
  import ChatContent from './ChatContent.svelte';

  let { onSettings, onReviewSettings, onReviewTask, embedded = false, activeTaskId = '', activeTaskLabel = '' }: {
    onSettings: () => void; onReviewSettings: (draft: SettingsDraft) => void; onReviewTask: (draft: TaskDraft) => void;
    embedded?: boolean; activeTaskId?: string; activeTaskLabel?: string;
  } = $props();
  let chats = $state<ChatSession[]>([]); let messages = $state<ChatMessage[]>([]);
  let activeId = $state(''); let input = $state(''); let error = $state('');
  let loading = $state(true); let busy = $state(false); let ready = $state(false); let model = $state('');
  let taskId = $state(''); let tasks = $state<CatalogTaskDTO[]>([]); let status = $state('');
  let historyOpen = $state(false);
  let copied = $state(''); let scroll: HTMLDivElement; let follow = true;
  let controller: AbortController | null = null; let generation = 0;
  const suggestions = ['Что сейчас со здоровьем сервиса?', 'Помоги настроить сервис для закрытого пилота.', 'Найди задачу и предложи улучшения её тестов.'];

  async function init() {
    loading = true; error = '';
    const results = await Promise.allSettled([getSettings(), listChats(), getCatalog()]);
    const config = results[0]; const history = results[1]; const catalog = results[2];
    if (config.status === 'fulfilled') {
      ready = config.value.config.ai_enabled && !!config.value.config.ai_base_url && !!config.value.config.ai_model;
      model = config.value.config.ai_model;
    } else error = config.reason instanceof Error ? config.reason.message : 'Не удалось загрузить настройки AI.';
    if (history.status === 'fulfilled') chats = history.value;
    else error = history.reason instanceof Error ? history.reason.message : 'Не удалось загрузить диалоги.';
    if (catalog.status === 'fulfilled') tasks = catalog.value.projects.flatMap((p) => p.folders.flatMap((f) => f.tasks));
    loading = false;
    if (chats.length && !activeId) await select(chats[0].id);
  }
  async function select(id: string) {
    if (busy) return; const request = ++generation; error = ''; loading = true;
    try { const data = await readChat(id); if (request !== generation) return; activeId = id; messages = data.messages; follow = true; }
    catch (e) { if (request === generation) error = (e as Error).message; }
    finally { if (request === generation) loading = false; }
  }
  async function create() {
    if (busy || loading) return; error = ''; loading = true;
    try { const chat = await newChat(); chats = [chat, ...chats]; activeId = chat.id; messages = []; input = ''; taskId = ''; follow = true; }
    catch (e) { error = (e as Error).message; }
    finally { loading = false; }
  }
  async function remove(chat: ChatSession) {
    if (busy || !confirm(`Удалить диалог «${chat.title}»?`)) return;
    try { await deleteChat(chat.id); chats = chats.filter((c) => c.id !== chat.id); if (activeId === chat.id) { activeId = ''; messages = []; if (chats.length) await select(chats[0].id); } }
    catch (e) { error = (e as Error).message; }
  }
  async function send(text = input) {
    if (busy || !ready || !text.trim()) return;
    // Snapshot editor context before any async work. Switching tasks while a new
    // chat is being created or a response is streaming must not retarget it.
    const contextTaskId = embedded ? activeTaskId : taskId;
    if (!activeId) { await create(); if (!activeId) return; }
    const id = activeId; const content = text.trim(); busy = true; status = 'Подключаюсь…'; error = ''; follow = true;
    controller = new AbortController();
    const user: ChatMessage = { id: `local-user-${Date.now()}`, role: 'user', content, status: 'complete', created_at: new Date().toISOString(), proposals: [] };
    let assistant: ChatMessage = { id: 'pending', role: 'assistant', content: '', status: 'streaming', created_at: new Date().toISOString(), proposals: [] };
    messages = [...messages, user, assistant]; input = '';
    try {
      await streamChat(id, content, contextTaskId || undefined, controller.signal, (kind, data) => {
        if (kind === 'start') { assistant = { ...assistant, id: String(data.message_id) }; status = 'Пишет ответ…'; }
        if (kind === 'delta') assistant = { ...assistant, content: assistant.content + String(data.text || '') };
        if (kind === 'tool') status = `Читает данные: ${String(data.name)}`;
        if (kind === 'proposal') assistant = { ...assistant, proposals: [...assistant.proposals, data as unknown as ChatProposal] };
        if (kind === 'done') assistant = { ...assistant, status: String(data.status) };
        if (kind === 'error') { error = String(data.message); assistant = { ...assistant, status: 'error' }; }
        messages = [...messages.slice(0, -1), assistant];
      });
    } catch (e) {
      if ((e as Error).name === 'AbortError') status = 'Ответ остановлен';
      else { error = (e as Error).message; input = content; }
    } finally {
      controller = null;
      try {
        for (let attempt = 0; attempt < 15; attempt++) {
          const data = await readChat(id);
          if (activeId === id) messages = data.messages;
          if (!data.messages.some((message) => message.status === 'streaming')) break;
          await new Promise((resolve) => setTimeout(resolve, 100));
        }
        chats = await listChats();
      }
      catch (e) { if (!error) error = (e as Error).message; }
      if (!status.includes('остановлен')) status = '';
      busy = false;
    }
  }
  function stop() { controller?.abort(); }
  function keydown(e: KeyboardEvent) { if (e.key === 'Enter' && !e.shiftKey && !e.isComposing) { e.preventDefault(); void send(); } }
  function review(proposal: ChatProposal) { if (proposal.kind === 'settings') onReviewSettings(proposal.payload as SettingsDraft); else onReviewTask(proposal.payload as TaskDraft); }
  async function copy(message: ChatMessage) { try { await navigator.clipboard.writeText(message.content); copied = message.id; } catch { error = 'Не удалось скопировать ответ.'; } }
  $effect(() => { messages.map((m) => m.content.length + m.proposals.length).join(','); if (follow) void tick().then(() => { if (scroll) scroll.scrollTop = scroll.scrollHeight; }); });
  onMount(() => { void init(); });
  onDestroy(() => { generation++; controller?.abort(); });
</script>

<div class="assistant-layout" class:embedded>
  <aside class="history" class:embedded-history={embedded} id="assistant-history" aria-label="История AI-диалогов" hidden={embedded && !historyOpen}>
    <button class="primary" onclick={create} disabled={busy || loading}>＋ Новый диалог</button>
    <p class="eyebrow">История</p>
    {#each chats as chat (chat.id)}
      <div class="chat-row" class:active={chat.id === activeId}>
        <button class="chat-title" onclick={() => select(chat.id)} disabled={busy || loading} title={chat.title}>{chat.title}<small>{new Date(chat.updated_at).toLocaleDateString('ru')}</small></button>
        <button class="delete" onclick={() => remove(chat)} disabled={busy || loading} aria-label={`Удалить ${chat.title}`}>×</button>
      </div>
    {/each}
    {#if !chats.length && !loading}<p class="muted">Диалоги появятся здесь после первого сообщения.</p>{/if}
    <div class="history-footer"><span class="model" title={model}>{model || 'AI не подключён'}</span><button onclick={onSettings}>Настройки AI →</button></div>
  </aside>
  <section class="conversation" aria-label="Чат с AI-помощником">
    {#if embedded}
      <div class="embedded-toolbar">
        <button class="history-toggle" aria-expanded={historyOpen} aria-controls="assistant-history" onclick={() => historyOpen = !historyOpen}>{historyOpen ? 'Скрыть диалоги' : 'Диалоги'} · {chats.length}</button>
        <div class="context"><span class="context-dot"></span><span class="context-copy">Контекст: {activeTaskId ? (activeTaskLabel || activeTaskId) : 'сервис и каталог'}</span></div>
      </div>
      <div class="context-note">Передаю помощнику только сохранённое содержимое задачи с сервера; несохранённый текст редактора не передаётся.</div>
    {:else}
      <div class="context"><span class="context-dot"></span> Контекст: сервис, настройки и каталог <span class="muted">· изменения через проверяемые черновики</span></div>
    {/if}
    <div class="messages" bind:this={scroll} onscroll={() => { if (scroll) follow = scroll.scrollHeight - scroll.scrollTop - scroll.clientHeight < 100; }} aria-live="polite">
      {#if loading}<p class="muted">Загружаю диалог…</p>{/if}
      {#if !ready && !loading}<div class="empty-state"><h2>Подключи своего AI-провайдера</h2><p>Укажи URL API, модель и ключ в настройках. Диалоги и черновики будут храниться на сервере.</p><button class="primary" onclick={onSettings}>Открыть настройки</button></div>
      {:else if !messages.length && !loading}<div class="empty-state"><span class="assistant-mark">✦</span><h2>Что разберём в сервисе?</h2><p>Могу проверить состояние, найти задачу, подготовить настройки и предложить правку текста или тестов.</p><div class="suggestions">{#each suggestions as suggestion}<button onclick={() => send(suggestion)}>{suggestion}</button>{/each}</div></div>{/if}
      {#each messages as message (message.id)}
        <article class="message" class:user={message.role === 'user'} class:failed={message.status === 'error'}>
          <div class="message-heading"><strong>{message.role === 'user' ? 'Ты' : 'Помощник'}</strong><span>{message.role === 'assistant' && message.status !== 'complete' ? ({ streaming: 'Отвечает…', interrupted: 'Ответ остановлен', truncated: 'Достигнут лимит ответа', error: 'Ошибка' }[message.status] || message.status) : ''}</span>{#if message.content}<button onclick={() => copy(message)}>{copied === message.id ? 'Скопировано' : 'Копировать'}</button>{/if}</div>
          <ChatContent content={message.content || (busy ? '…' : 'Ответ не завершён. Можно повторить запрос.')} />
          {#each message.proposals as proposal (proposal.id)}<div class="proposal"><div><small>Черновик · требуется проверка</small><strong>{proposal.title}</strong><span>{proposal.kind === 'settings' ? 'Настройки сервиса' : 'Содержимое задачи'}</span></div><button class="primary" disabled={busy || loading} onclick={() => review(proposal)}>Проверить изменения →</button></div>{/each}
        </article>
      {/each}
    </div>
    <div class="composer">
      {#if error}<div class="inline-error" role="alert">{error}</div>{/if}
      {#if !embedded}<label class="attachment">Задача в контексте <select bind:value={taskId} disabled={busy || loading}><option value="">Общий контекст сервиса</option>{#each tasks as task (task.id)}<option value={task.id}>{task.task_id} · {task.title}</option>{/each}</select></label>{/if}
      <div class="input-box"><textarea bind:value={input} onkeydown={keydown} placeholder="Напиши, что нужно проверить или подготовить…" aria-label="Сообщение помощнику" maxlength="8000" disabled={!ready || loading}></textarea><div class="composer-actions"><small>{busy ? status : 'Enter — отправить · Shift+Enter — новая строка'}</small>{#if busy}<button onclick={stop}>■ Остановить</button>{:else}<button class="primary" onclick={() => send()} disabled={!ready || loading || !input.trim()}>Отправить ↑</button>{/if}</div></div>
    </div>
  </section>
</div>

<style>
  .assistant-layout.embedded, .assistant-layout.embedded * { box-sizing: border-box; }
  .assistant-layout { display: grid; grid-template-columns: 230px minmax(0, 1fr); height: calc(100vh - 140px); min-height: 550px; border: 1px solid #343a44; border-radius: 12px; overflow: hidden; background: #1b2026; }
  .history { padding: 16px; border-right: 1px solid #343a44; display: flex; flex-direction: column; gap: 6px; overflow: auto; background: #191d23; }
  .eyebrow { color: #8e9aaa; font-size: 11px; text-transform: uppercase; letter-spacing: .1em; margin: 18px 4px 8px; }
  .chat-row { display: flex; border-radius: 7px; } .chat-row.active { background: #2c3848; }
  .chat-title { border: 0; background: transparent; text-align: left; flex: 1; min-width: 0; padding: 10px; text-overflow: ellipsis; overflow: hidden; white-space: nowrap; }
  .chat-title small { display: block; color: #8e9aaa; font-size: 11px; margin-top: 4px; } .delete { background: transparent; border: 0; color: #8e9aaa; padding: 8px; }
  .history-footer { margin-top: auto; padding-top: 22px; display: grid; gap: 8px; } .model { overflow: hidden; text-overflow: ellipsis; color: #a5b2c2; font-size: 12px; }
  .conversation { display: flex; flex-direction: column; min-height: 0; } .context { padding: 13px 20px; border-bottom: 1px solid #343a44; font-size: 12px; color: #a5b2c2; }
  .context-dot { display: inline-block; width: 6px; height: 6px; border-radius: 100%; background: #76c4aa; margin-right: 6px; }
  .messages { flex: 1; overflow: auto; padding: 24px 30px; } .empty-state { max-width: 550px; margin: 45px auto; text-align: center; color: #a5b2c2; }
  h2 { color: #ecf0f6; font-size: 24px; letter-spacing: -.03em; } .assistant-mark { font-size: 34px; color: #a9c9ff; }
  .suggestions { display: grid; gap: 9px; margin-top: 24px; text-align: left; } .suggestions button { text-align: left; background: #242b34; }
  .message { padding: 18px 0 24px; border-bottom: 1px solid #30363f; } .message.user { background: #252d38; border: 0; border-radius: 9px; padding: 16px 20px; margin: 12px 0; }
  .message.failed { border-left: 2px solid #dc8188; padding-left: 14px; } .message-heading { display: flex; gap: 14px; align-items: center; color: #b9c5d6; font-size: 12px; margin-bottom: 12px; }
  .message-heading strong { color: #e8edf5; } .message-heading button { margin-left: auto; border: 0; background: transparent; padding: 3px; color: #8e9aaa; font-size: 11px; }
  .proposal { display: flex; gap: 16px; align-items: center; justify-content: space-between; background: #263546; border: 1px solid #405d7c; border-radius: 8px; padding: 14px; margin-top: 16px; }
  .proposal div { display: grid; gap: 5px; } .proposal small, .proposal span { font-size: 11px; color: #afc0d7; }
  .composer { padding: 14px 22px 18px; border-top: 1px solid #343a44; background: #1b2026; } .attachment { display: flex; gap: 12px; align-items: center; font-size: 11px; color: #a5b2c2; margin-bottom: 10px; }
  .attachment select { padding: 5px 8px; max-width: 400px; font-size: 12px; } .input-box { border: 1px solid #475262; background: #242b34; border-radius: 10px; padding: 10px 12px; }
  textarea { resize: vertical; min-height: 65px; max-height: 200px; padding: 6px; width: 100%; box-sizing: border-box; border: 0; background: transparent; font-family: inherit; color: inherit; font-size: 14px; }
  textarea:focus { outline: none; } .composer-actions { display: flex; align-items: center; justify-content: space-between; gap: 10px; } .composer-actions small { color: #8e9aaa; font-size: 11px; }
  .muted { color: #8e9aaa; } .inline-error { padding: 10px; color: #ffb4bb; background: #41262c; border-radius: 6px; margin-bottom: 10px; }
  .assistant-layout.embedded { display: flex; flex-direction: column; width: 100%; height: 100%; min-height: 0; border: 0; border-radius: 0; overflow: hidden; }
  .embedded-history { flex: 0 1 auto; min-height: 0; max-height: 210px; padding: 8px 10px; border-right: 0; border-bottom: 1px solid #343a44; }
  .embedded-history[hidden] { display: none; }
  .embedded-history .eyebrow { margin: 7px 4px 4px; }
  .embedded-history .history-footer { margin-top: 8px; padding-top: 8px; }
  .embedded-toolbar { display: flex; align-items: center; gap: 8px; min-width: 0; padding: 7px 9px; border-bottom: 1px solid #343a44; }
  .history-toggle { flex: 0 0 auto; padding: 6px 8px; font-size: 11px; }
  .embedded .context { min-width: 0; padding: 4px 0; border: 0; overflow-wrap: anywhere; }
  .context-copy { min-width: 0; }
  .context-note { padding: 5px 10px; color: #8e9aaa; font-size: 10px; line-height: 1.35; border-bottom: 1px solid #343a44; overflow-wrap: anywhere; }
  .embedded .conversation { width: 100%; flex: 1 1 auto; min-width: 0; min-height: 0; }
  .embedded .messages { min-width: 0; padding: 10px; overflow-wrap: anywhere; }
  .embedded .empty-state { margin: 18px auto; }
  .embedded h2 { font-size: 19px; }
  .embedded .message { min-width: 0; overflow-wrap: anywhere; }
  .embedded .message.user { padding: 12px; }
  .embedded .proposal { flex-direction: column; align-items: stretch; gap: 10px; padding: 10px; min-width: 0; }
  .embedded .composer { padding: 8px; min-width: 0; }
  .embedded .input-box { min-width: 0; padding: 8px; }
  .embedded textarea { min-height: 58px; max-height: 150px; font-size: 13px; }
  .embedded .composer-actions { flex-wrap: wrap; }
  .embedded .composer-actions small { min-width: 0; overflow-wrap: anywhere; }
  .embedded .composer-actions button { flex: 0 0 auto; }
  .embedded .inline-error { overflow-wrap: anywhere; }
  @media (max-width: 1000px) { .assistant-layout { grid-template-columns: 180px minmax(0, 1fr); } .messages { padding: 16px; } .context .muted { display: none; } }
  @media (max-width: 700px) { .assistant-layout { grid-template-columns: 1fr; height: calc(100vh - 180px); min-height: 600px; } .history { max-height: 150px; border-right: 0; border-bottom: 1px solid #343a44; } .history-footer, .history .eyebrow { display: none; } .conversation { min-height: 480px; } .attachment select { max-width: 100%; } .composer { padding: 10px; } .proposal { flex-direction: column; align-items: flex-start; } .attachment { flex-wrap: wrap; } .composer-actions small { max-width: 55%; } }
</style>
