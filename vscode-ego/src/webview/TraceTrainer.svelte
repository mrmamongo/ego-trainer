<script lang="ts">
	/** Trace trainer (tasks tagged `trace`): numbered code + one answer input per variable. */
	import { onMount } from 'svelte';
	import { trainerState } from './shared/store';
	import { onHostMessage, postToHost } from './shared/api';
	import type { TraceState } from './shared/types';

	let { kind = 'trace', taskId = '' }: { kind?: 'trace' | 'parsons'; taskId?: string } = $props();

	let draft = $state<Record<string, string>>({});
	let focusLine = $state<string | null>(null);
	let error = $state('');
	let submitting = $state(false);
	let loadedFor = '';

	const state = $derived.by((): TraceState | null => {
		const s = $trainerState;
		return s && s.supported && s.kind === 'trace' ? s : null;
	});

	// Seed the draft from the parsed values whenever a trace state arrives.
	$effect(() => {
		const data = state;
		if (!data) return;
		const key = taskId + '|' + data.answers.map((a) => a.name + '=' + a.value).join(',');
		if (key === loadedFor) return;
		loadedFor = key;
		const next: Record<string, string> = {};
		for (const answer of data.answers) next[answer.name] = answer.value;
		draft = next;
		error = '';
		submitting = false;
	});

	onMount(() => {
		const off = onHostMessage((msg) => {
			if (msg.type !== 'trainer.submitted' || msg.payload?.ok !== false) return;
			submitting = false;
			error = 'Не удалось сохранить ответы: ' + (msg.payload.error ?? 'неизвестная ошибка');
		});
		postToHost({ type: 'trainer.load', kind, taskId });
		return off;
	});

	/** Accepts int, float, 'string' / "string", True/False; returns a Russian reason otherwise. */
	function literalProblem(raw: string): string | null {
		const text = raw.trim();
		if (text === '') return 'Впиши значение';
		if (text === 'None') return 'Нужно значение, а не None';
		if (text === 'True' || text === 'False') return null;
		if (/^[+-]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][+-]?\d+)?$/.test(text)) return null;
		if (text[0] === "'" || text[0] === '"') {
			const quote = text[0];
			if (text.length < 2 || text[text.length - 1] !== quote) return 'Не хватает закрывающей кавычки';
			const inner = text.slice(1, -1);
			if (inner.includes(quote) && !inner.includes('\\' + quote)) return 'Закрой строку кавычкой';
			return null;
		}
		if (/^[A-Za-z_][A-Za-z0-9_]*$/.test(text) || /^[^\s"'()[\]{}=+\-*/%<>!&|^~,.:;]+$/.test(text)) {
			return "Строку пишут в кавычках: '" + text + "'";
		}
		return 'Нужен литерал Python: число, строка в кавычках или True/False';
	}

	const problems = $derived.by(() => {
		const out: Record<string, string> = {};
		for (const answer of state?.answers ?? []) {
			const problem = literalProblem(draft[answer.name] ?? '');
			if (problem) out[answer.name] = problem;
		}
		return out;
	});
	const invalidCount = $derived(Object.keys(problems).length);

	function focusAnswer(answer: { name: string; line: string | null }) {
		focusLine = answer.line;
	}

	function submit() {
		const data = state;
		if (!data || invalidCount > 0) return;
		const answers: Record<string, string> = {};
		for (const answer of data.answers) answers[answer.name] = (draft[answer.name] ?? '').trim();
		error = '';
		submitting = true;
		postToHost({ type: 'trainer.submit', taskId, answers });
	}
</script>

{#if state}
	{@const data = state}
	<section class="trainer trace-trainer" aria-label="Тренажёр: трассировка">
		<div class="code" role="table" aria-label="Код для трассировки">
			{#each data.lines as line (line.label)}
				<div class="row" class:active={focusLine === line.label} role="row" data-line={line.label}
					aria-current={focusLine === line.label ? 'true' : undefined}>
					<span class="num" role="rowheader">{line.label}</span>
					<pre class="code-text" role="cell">{line.code}</pre>
				</div>
			{/each}
		</div>
		{#if data.intro}<p class="intro">{data.intro}</p>{/if}

		<form class="answers" onsubmit={(e) => { e.preventDefault(); submit(); }}>
			<h3>Значения</h3>
			{#each data.answers as answer (answer.name)}
				{@const problem = problems[answer.name]}
				<label class="answer" class:invalid={!!problem} data-name={answer.name}>
					<span class="label">{answer.label}</span>
					<input type="text" spellcheck="false" autocomplete="off" class="mono"
						data-name={answer.name} placeholder="None"
						aria-invalid={problem ? 'true' : 'false'}
						aria-describedby={problem ? 'trace-problem-' + answer.name : undefined}
						bind:value={draft[answer.name]}
						onfocus={() => focusAnswer(answer)}
						onblur={() => { if (focusLine === answer.line) focusLine = null; }} />
					{#if problem}<span class="problem" id={'trace-problem-' + answer.name} role="alert">{problem}</span>{/if}
				</label>
			{/each}
			<div class="actions">
				<button type="submit" class="primary" disabled={submitting || invalidCount > 0}>Проверить ответы</button>
				{#if invalidCount > 0}<span class="hint">{invalidCount} {invalidCount === 1 ? 'поле с ошибкой' : 'поля с ошибкой'}</span>{/if}
			</div>
			{#if error}<p class="error" role="alert">{error}</p>{/if}
		</form>
	</section>
{/if}

<style>
	.trainer { margin: 14px 0; }
	.code { border: 1px solid var(--vscode-panel-border, #333); border-radius: 6px; overflow: auto; background: var(--vscode-textCodeBlock-background, rgba(128, 128, 128, 0.1)); padding: 6px 0; }
	.row { display: flex; align-items: stretch; min-width: max-content; transition: background-color 0.12s ease; }
	.row.active { background: var(--vscode-editor-lineHighlightBackground, var(--vscode-list-hoverBackground, rgba(255, 200, 0, 0.16))); }
	.num { flex: 0 0 auto; min-width: 2.2em; padding: 0 8px 0 6px; text-align: right; font: var(--vscode-editor-font-size, 12px) var(--vscode-editor-font-family, monospace); color: var(--vscode-descriptionForeground, #888); user-select: none; font-variant-numeric: tabular-nums; }
	.code-text { margin: 0; padding: 0 10px 0 0; font: var(--vscode-editor-font-size, 12px)/1.5 var(--vscode-editor-font-family, monospace); color: var(--vscode-foreground); white-space: pre; }
	.intro { font-size: 12px; color: var(--vscode-descriptionForeground); margin: 10px 0 0; }
	.answers { margin-top: 12px; display: flex; flex-direction: column; gap: 8px; }
	.answers h3 { font-size: 12px; font-weight: 600; margin: 0 0 2px; }
	.answer { display: grid; grid-template-columns: 1fr; gap: 3px; font-size: 12px; }
	.answer .label { color: var(--vscode-foreground); }
	.answer .mono, input.mono { font-family: var(--vscode-editor-font-family, monospace); font-size: 12px; }
	input { width: 100%; box-sizing: border-box; padding: 5px 7px; border: 1px solid var(--vscode-input-border, transparent); border-radius: 3px; background: var(--vscode-input-background); color: var(--vscode-input-foreground); }
	input:focus-visible { outline: 1px solid var(--vscode-focusBorder); outline-offset: -1px; }
	.answer.invalid input { border-color: var(--vscode-inputValidation-errorBorder, #f14c4c); }
	.problem { color: var(--vscode-errorForeground, #f48771); font-size: 11px; }
	.actions { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin-top: 4px; }
	button { cursor: pointer; font: inherit; font-size: 11px; border: 1px solid var(--vscode-panel-border, #444); border-radius: 5px; padding: 6px 10px; background: transparent; color: var(--vscode-foreground); }
	button.primary { background: var(--vscode-button-background, #007acc); color: var(--vscode-button-foreground, #fff); border-color: transparent; }
	button:disabled { opacity: 0.45; cursor: default; }
	button:focus-visible { outline: 1px solid var(--vscode-focusBorder); outline-offset: 2px; }
	.hint { font-size: 11px; color: var(--vscode-descriptionForeground); }
	.error { color: var(--vscode-errorForeground); font-size: 12px; margin: 4px 0 0; }
	@media (prefers-reduced-motion: reduce) { .row { transition: none; } }
</style>
