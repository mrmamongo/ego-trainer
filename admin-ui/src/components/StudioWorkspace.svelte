<script lang="ts">
  import { onDestroy } from 'svelte';
  import EditorWorkspace from './EditorWorkspace.svelte';
  import type { TaskDraft } from '../consoleApi';

  let { role, initialTaskId = '', draft = null,
    onDirtyChange, onBusyChange, onActiveTask }: {
    role: string; initialTaskId?: string; draft?: TaskDraft | null;
    onDirtyChange?: (dirty: boolean) => void; onBusyChange?: (busy: boolean) => void;
    onActiveTask?: (id: string, label: string) => void;
  } = $props();

  let incomingDraft = $state<TaskDraft | null>(null);

  $effect(() => { if (draft) incomingDraft = draft; });
  function taskChanged(id: string, label: string) {
    onActiveTask?.(id, label);
  }
  function busyChanged(busy: boolean) { onBusyChange?.(busy); }
  onDestroy(() => { onBusyChange?.(false); });
</script>

<section class="studio-frame" aria-label="Рабочее пространство редактора">
  <div class="workspace-bar">
    <div><strong>Материалы курса</strong><span>Дерево · файлы задач · редактор</span></div>
  </div>
  <div class="studio-panes">
    <div class="editor-pane"><EditorWorkspace {role} {initialTaskId} draft={incomingDraft} {onDirtyChange} onBusyChange={busyChanged} onActiveTask={taskChanged} /></div>
  </div>
</section>

<style>
  .studio-frame { height: 100%; min-height: 0; display: flex; flex-direction: column; background: #09090b; }
  .workspace-bar { display: flex; justify-content: space-between; gap: 16px; align-items: center; padding: 10px 16px; border-bottom: 1px solid #27272a; flex-shrink: 0; }
  .workspace-bar div { display: flex; gap: 14px; align-items: baseline; min-width: 0; } .workspace-bar strong { font-size: 12px; white-space: nowrap; } .workspace-bar span { color: #a1a1aa; font-size: 11px; }
  .studio-panes { display: flex; position: relative; flex: 1; min-height: 0; overflow: hidden; }
  .editor-pane { flex: 1; min-width: 0; min-height: 0; overflow: hidden; }
  @media (max-width: 700px) { .workspace-bar span { display: none; } .workspace-bar { padding: 9px 10px; } }
</style>
