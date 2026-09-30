<script lang="ts">
  import { onDestroy } from 'svelte';
  import EditorWorkspace from './EditorWorkspace.svelte';
  import Assistant from './Assistant.svelte';
  import type { SettingsDraft, TaskDraft } from '../consoleApi';

  let { role, initialTaskId = '', draft = null, onSettings, onReviewSettings,
    onDirtyChange, onBusyChange, onActiveTask }: {
    role: string; initialTaskId?: string; draft?: TaskDraft | null;
    onSettings: () => void; onReviewSettings: (draft: SettingsDraft) => void;
    onDirtyChange?: (dirty: boolean) => void; onBusyChange?: (busy: boolean) => void;
    onActiveTask?: (id: string, label: string) => void;
  } = $props();

  function storedWidth() {
    try { return Math.max(280, Math.min(500, Number(localStorage.getItem('ego_editor_chat_width')) || 340)); }
    catch { return 340; }
  }
  let chatWidth = $state(storedWidth());
  let chatOpen = $state(window.innerWidth >= 1280);
  let activeTaskId = $state('');
  let activeTaskLabel = $state('');
  let incomingDraft = $state<TaskDraft | null>(null);
  let editorBusy = $state(false);
  let notice = $state('');
  let removeDragListeners: (() => void) | null = null;

  $effect(() => { if (draft) incomingDraft = draft; });
  function taskChanged(id: string, label: string) {
    activeTaskId = id; activeTaskLabel = label; onActiveTask?.(id, label);
  }
  function busyChanged(busy: boolean) { editorBusy = busy; onBusyChange?.(busy); }
  function reviewTask(candidate: TaskDraft) {
    if (editorBusy) { notice = 'Дождись завершения проверки или сохранения, затем открой предложение.'; return; }
    notice = ''; incomingDraft = candidate;
  }
  function rememberWidth() {
    try { localStorage.setItem('ego_editor_chat_width', String(chatWidth)); } catch {}
  }
  function resize(event: PointerEvent) {
    if (event.button !== 0) return;
    event.preventDefault();
    removeDragListeners?.();
    const startX = event.clientX; const startWidth = chatWidth;
    const move = (next: PointerEvent) => { chatWidth = Math.max(280, Math.min(500, startWidth + startX - next.clientX)); };
    const finish = () => { removeDragListeners?.(); removeDragListeners = null; rememberWidth(); };
    window.addEventListener('pointermove', move);
    window.addEventListener('pointerup', finish, { once: true });
    window.addEventListener('pointercancel', finish, { once: true });
    removeDragListeners = () => {
      window.removeEventListener('pointermove', move);
      window.removeEventListener('pointerup', finish);
      window.removeEventListener('pointercancel', finish);
    };
  }
  function resizeKey(event: KeyboardEvent) {
    if (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight') return;
    event.preventDefault();
    chatWidth = Math.max(280, Math.min(500, chatWidth + (event.key === 'ArrowLeft' ? 20 : -20)));
    rememberWidth();
  }
  onDestroy(() => { removeDragListeners?.(); onBusyChange?.(false); });
</script>

<section class="studio-frame" aria-label="Рабочее пространство редактора">
  <div class="workspace-bar">
    <div><strong>Материалы курса</strong><span>Дерево · файлы задач · редактор</span></div>
    {#if role === 'admin'}<button class:active={chatOpen} onclick={() => { chatOpen = !chatOpen; }} aria-expanded={chatOpen} aria-controls="editor-chat">✦ {chatOpen ? 'Скрыть чат' : 'Открыть чат'}</button>{/if}
  </div>
  {#if notice}<p class="notice" role="status">{notice}</p>{/if}
  <div class="studio-panes">
    <div class="editor-pane"><EditorWorkspace {role} {initialTaskId} draft={incomingDraft} {onDirtyChange} onBusyChange={busyChanged} onActiveTask={taskChanged} /></div>
    {#if role === 'admin'}
      <!-- svelte-ignore a11y_no_noninteractive_element_interactions, a11y_no_noninteractive_tabindex (ARIA splitter supports arrow keys and pointer resizing) -->
      <div class="chat-resize" class:closed={!chatOpen} role="separator" tabindex={chatOpen ? 0 : -1} aria-label="Ширина AI-чата" aria-orientation="vertical" aria-valuemin={280} aria-valuemax={500} aria-valuenow={chatWidth} onpointerdown={resize} onkeydown={resizeKey}></div>
      <aside id="editor-chat" class="chat-pane" class:closed={!chatOpen} style:width={`${chatWidth}px`} aria-label="AI-помощник в редакторе" aria-hidden={!chatOpen}>
        <div class="chat-heading"><div><span>✦</span><strong>AI-помощник</strong></div><button onclick={() => { chatOpen = false; }} aria-label="Закрыть боковой чат">×</button></div>
        <div class="chat-content"><Assistant embedded {activeTaskId} {activeTaskLabel} {onSettings} {onReviewSettings} onReviewTask={reviewTask} /></div>
      </aside>
    {/if}
  </div>
</section>

<style>
  .studio-frame { height: 100%; min-height: 0; display: flex; flex-direction: column; background: #171c23; }
  .workspace-bar { display: flex; justify-content: space-between; gap: 16px; align-items: center; padding: 10px 16px; border-bottom: 1px solid #303946; flex-shrink: 0; }
  .workspace-bar div { display: flex; gap: 14px; align-items: baseline; min-width: 0; } .workspace-bar strong { font-size: 12px; white-space: nowrap; } .workspace-bar span { color: #8898ae; font-size: 11px; }
  .workspace-bar button { font-size: 12px; padding: 6px 10px; } .workspace-bar button.active { background: #2c3b52; border-color: #405677; }
  .studio-panes { display: flex; position: relative; flex: 1; min-height: 0; overflow: hidden; }
  .editor-pane { flex: 1; min-width: 0; min-height: 0; overflow: hidden; }
  .chat-pane { flex: 0 0 auto; max-width: calc(100% - 32px); display: flex; flex-direction: column; min-height: 0; border-left: 1px solid #303946; background: #1b2027; }
  .chat-content { flex: 1; min-height: 0; overflow: hidden; }
  .chat-heading { display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; border-bottom: 1px solid #303946; height: 41px; flex-shrink: 0; }
  .chat-heading div { display: flex; align-items: center; gap: 9px; font-size: 12px; } .chat-heading span { color: #aac9fb; } .chat-heading button { background: transparent; border: 0; padding: 2px 8px; font-size: 18px; }
  .chat-resize { width: 5px; flex-shrink: 0; cursor: col-resize; background: #1b2027; touch-action: none; } .chat-resize:hover, .chat-resize:focus { background: #6b94c6; outline: none; }
  .closed { display: none; } .notice { margin: 0; padding: 8px 16px; color: #e8b86e; font-size: 12px; border-bottom: 1px solid #303946; }
  @media (max-width: 1150px) { .chat-pane { position: absolute; right: 0; top: 0; bottom: 0; z-index: 20; box-shadow: -15px 0 40px #0008; } .chat-resize { display: none; } }
  @media (max-width: 700px) { .workspace-bar span { display: none; } .workspace-bar { padding: 9px 10px; } .chat-pane { width: min(360px, calc(100% - 18px)) !important; } }
</style>
