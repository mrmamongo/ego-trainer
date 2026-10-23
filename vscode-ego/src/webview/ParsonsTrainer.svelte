<script lang="ts">
	/** Parsons trainer (tasks tagged `parsons`): drag, reorder and indent the body lines. */
	import { onMount } from 'svelte';
	import { trainerState } from './shared/store';
	import { onHostMessage, postToHost } from './shared/api';
	import type { ParsonsLine, ParsonsState } from './shared/types';

	let { kind = 'parsons', taskId = '' }: { kind?: 'trace' | 'parsons'; taskId?: string } = $props();

	const INDENT = 4;
	const MAX_LEVEL = 4;

	let lines = $state<ParsonsLine[]>([]);
	let dragId = $state<number | null>(null);
	let dropIndex = $state<number | null>(null);
	let error = $state('');
	let submitting = $state(false);
	let loadedFor = '';
	let listEl: HTMLOListElement | undefined = $state();

	const state = $derived.by((): ParsonsState | null => {
		const s = $trainerState;
		return s && s.supported && s.kind === 'parsons' ? s : null;
	});

	$effect(() => {
		const data = state;
		if (!data) return;
		const key = taskId + '|' + data.lines.map((l) => l.id + ':' + l.level).join(',');
		if (key === loadedFor) return;
		loadedFor = key;
		lines = data.lines.map((l) => ({ ...l }));
		error = '';
		submitting = false;
	});

	onMount(() => {
		const off = onHostMessage((msg) => {
			if (msg.type !== 'trainer.submitted' || msg.payload?.ok !== false) return;
			submitting = false;
			error = 'Не удалось собрать функцию: ' + (msg.payload.error ?? 'неизвестная ошибка');
		});
		postToHost({ type: 'trainer.load', kind, taskId });
		return off;
	});

	const preview = $derived(
		(state ? state.defLine + '\n' : '') +
			lines.map((line) => '    ' + ' '.repeat(INDENT * line.level) + line.text).join('\n')
	);

	function indexOf(id: number): number {
		return lines.findIndex((l) => l.id === id);
	}

	function move(id: number, delta: number) {
		const from = indexOf(id);
		const to = from + delta;
		if (from < 0 || to < 0 || to >= lines.length) return;
		const next = lines.slice();
		const [item] = next.splice(from, 1);
		next.splice(to, 0, item);
		lines = next;
		focus(id);
	}

	function changeLevel(id: number, delta: number) {
		const index = indexOf(id);
		if (index < 0) return;
		const next = lines.slice();
		const level = Math.max(0, Math.min(MAX_LEVEL, next[index].level + delta));
		if (level === next[index].level) return;
		next[index] = { ...next[index], level };
		lines = next;
		focus(id);
	}

	/** Keep keyboard focus on the moved line after the list re-renders. */
	function focus(id: number) {
		requestAnimationFrame(() => listEl?.querySelector<HTMLElement>(`li[data-id="${id}"] button.up`)?.focus());
	}

	function onDragStart(event: DragEvent, id: number) {
		dragId = id;
		dropIndex = null;
		event.dataTransfer?.setData('text/plain', String(id));
		if (event.dataTransfer) event.dataTransfer.effectAllowed = 'move';
	}

	function onDragOver(event: DragEvent, index: number) {
		if (dragId === null) return;
		event.preventDefault();
		if (event.dataTransfer) event.dataTransfer.dropEffect = 'move';
		const rect = (event.currentTarget as HTMLElement).getBoundingClientRect();
		dropIndex = event.clientY < rect.top + rect.height / 2 ? index : index + 1;
	}

	function onDrop(event: DragEvent) {
		event.preventDefault();
		const id = dragId ?? Number(event.dataTransfer?.getData('text/plain'));
		let target = dropIndex;
		dragId = null;
		dropIndex = null;
		if (!Number.isFinite(id) || target === null) return;
		const from = indexOf(id);
		if (from < 0) return;
		if (from < target) target -= 1; // removal of the dragged line shifts the target
		target = Math.max(0, Math.min(lines.length - 1, target));
		if (target === from) return;
		const next = lines.slice();
		const [item] = next.splice(from, 1);
		next.splice(target, 0, item);
		lines = next;
	}

	function onDragEnd() {
		dragId = null;
		dropIndex = null;
	}

	function reset() {
		const data = state;
		if (!data) return;
		lines = data.lines.map((l) => ({ ...l }));
		error = '';
	}

	function submit() {
		const data = state;
		if (!data) return;
		error = '';
		submitting = true;
		postToHost({
			type: 'trainer.submit',
			taskId,
			lines: lines.map((line) => ({ id: line.id, level: line.level }))
		});
	}
</script>

{#if state}
	<section class="trainer parsons-trainer" aria-label="Тренажёр: собери функцию">
		<p class="intro">{state.intro}</p>
		{#if state.assembled}<p class="assembled">Тело уже собрано — строку <code>return None</code> заменил код.</p>{/if}

		<ol class="pool" bind:this={listEl} aria-label="Строки функции"
			ondragover={(e) => { if (dragId !== null) e.preventDefault(); }}>
			{#each lines as line, index (line.id)}
				<li class="line" class:dragging={dragId === line.id}
					class:drop-before={dropIndex === index && dragId !== null}
					class:drop-after={dropIndex === index + 1 && index === lines.length - 1 && dragId !== null}
					data-id={line.id} draggable="true"
					ondragstart={(e) => onDragStart(e, line.id)}
					ondragover={(e) => onDragOver(e, index)}
					ondrop={onDrop} ondragend={onDragEnd}>
					<span class="grip" aria-hidden="true">⋮⋮</span>
					<span class="code mono" style:padding-left="{INDENT * line.level}px"
						aria-label={line.level > 0 ? 'отступ ' + line.level * INDENT + ' пробелов' : undefined}>{line.text}</span>
					<span class="controls">
						<button type="button" class="up" title="Выше (Alt+↑)" aria-label="Поднять строку «{line.text}»"
							disabled={index === 0} onclick={() => move(line.id, -1)}>↑</button>
						<button type="button" title="Ниже (Alt+↓)" aria-label="Опустить строку «{line.text}»"
							disabled={index === lines.length - 1} onclick={() => move(line.id, 1)}>↓</button>
						<button type="button" title="Убрать отступ (Alt+←)" aria-label="Уменьшить отступ строки «{line.text}»"
							disabled={line.level === 0} onclick={() => changeLevel(line.id, -1)}>⇤</button>
						<button type="button" title="Добавить отступ (Alt+→)" aria-label="Увеличить отступ строки «{line.text}»"
							disabled={line.level >= MAX_LEVEL} onclick={() => changeLevel(line.id, 1)}>⇥</button>
					</span>
				</li>
			{/each}
		</ol>

		<div class="preview">
			<h3>Предпросмотр</h3>
			<pre class="mono">{preview || '…'}</pre>
		</div>

		<div class="actions">
			<button type="button" class="primary" disabled={submitting} onclick={submit}>Собрать и проверить</button>
			<button type="button" onclick={reset} disabled={submitting}>Сбросить порядок</button>
		</div>
		{#if error}<p class="error" role="alert">{error}</p>{/if}
	</section>
{/if}

<svelte:window onkeydown={(e) => {
	const target = e.target as HTMLElement | null;
	const li = target?.closest?.('li.line') as HTMLElement | null;
	if (!li || !e.altKey) return;
	const id = Number(li.dataset.id);
	if (!Number.isFinite(id)) return;
	const bindings: Record<string, () => void> = {
		ArrowUp: () => move(id, -1),
		ArrowDown: () => move(id, 1),
		ArrowLeft: () => changeLevel(id, -1),
		ArrowRight: () => changeLevel(id, 1)
	};
	const action = bindings[e.key];
	if (!action) return;
	e.preventDefault();
	action();
}} />

<style>
	.trainer { margin: 14px 0; }
	.intro { font-size: 12px; color: var(--vscode-descriptionForeground); margin: 0 0 8px; }
	.assembled { font-size: 11px; color: var(--vscode-descriptionForeground); margin: 0 0 8px; }
	.pool { list-style: none; margin: 0; padding: 0; border: 1px solid var(--vscode-panel-border, #333); border-radius: 6px; overflow: hidden; }
	.line { display: flex; align-items: center; gap: 6px; padding: 5px 8px; background: var(--vscode-textCodeBlock-background, rgba(128, 128, 128, 0.1)); border-bottom: 1px solid var(--vscode-panel-border, #333); cursor: grab; min-height: 30px; }
	.line:last-child { border-bottom: 0; }
	.line.dragging { opacity: 0.5; }
	.line.drop-before { box-shadow: inset 0 2px 0 var(--vscode-focusBorder, #3794ff); }
	.line.drop-after { box-shadow: inset 0 -2px 0 var(--vscode-focusBorder, #3794ff); }
	.grip { flex: 0 0 auto; color: var(--vscode-descriptionForeground); font-size: 11px; letter-spacing: -1px; user-select: none; }
	.code { flex: 1 1 auto; white-space: pre; overflow: hidden; text-overflow: ellipsis; font: var(--vscode-editor-font-size, 12px) var(--vscode-editor-font-family, monospace); }
	.mono { font-family: var(--vscode-editor-font-family, monospace); }
	.controls { flex: 0 0 auto; display: flex; gap: 2px; }
	.controls button { cursor: pointer; font: inherit; font-size: 11px; line-height: 1; padding: 4px 6px; border: 1px solid var(--vscode-panel-border, #444); border-radius: 4px; background: transparent; color: var(--vscode-foreground); }
	.controls button:disabled { opacity: 0.35; cursor: default; }
	.controls button:hover:not(:disabled) { background: var(--vscode-list-hoverBackground); }
	.controls button:focus-visible, .actions button:focus-visible { outline: 1px solid var(--vscode-focusBorder); outline-offset: 2px; }
	.preview { margin-top: 10px; }
	.preview h3 { font-size: 12px; font-weight: 600; margin: 0 0 4px; }
	.preview pre { margin: 0; padding: 10px; border: 1px solid var(--vscode-panel-border, #333); border-radius: 6px; background: var(--vscode-textCodeBlock-background, #202020); font-size: 12px; line-height: 1.55; overflow: auto; white-space: pre; }
	.actions { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 10px; }
	.actions button { cursor: pointer; font: inherit; font-size: 11px; border: 1px solid var(--vscode-panel-border, #444); border-radius: 5px; padding: 6px 10px; background: transparent; color: var(--vscode-foreground); }
	.actions button.primary { background: var(--vscode-button-background, #007acc); color: var(--vscode-button-foreground, #fff); border-color: transparent; }
	.actions button:disabled { opacity: 0.45; cursor: default; }
	.error { color: var(--vscode-errorForeground); font-size: 12px; margin: 6px 0 0; }
</style>
