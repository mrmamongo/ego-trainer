<script lang="ts">
	import { taskViewData, checkResult } from './shared/store';
	import { postToHost } from './shared/api';
	import ResultsBody from './ResultsBody.svelte';
	import type { TaskHint } from './shared/types';

	let revealedLevels = $state<number[]>([]);

	$effect(() => {
		// Reset revealed hints when task data changes (including id switch).
		$taskViewData;
		revealedLevels = [];
	});

	function hintForLevel(hints: TaskHint[], level: number): TaskHint | undefined {
		return hints.find((h) => h.level === level);
	}

	function revealHint(level: number) {
		if (!revealedLevels.includes(level)) {
			revealedLevels = [...revealedLevels, level];
		}
	}

	function statusLabel(status: string): string {
		const s = (status ?? '').trim().toLowerCase();
		if (!s || s === 'new') return 'new';
		return s;
	}

	function check() {
		postToHost({ type: 'taskView.check' });
	}

	function openPy() {
		postToHost({ type: 'taskView.openPy' });
	}

	const HINT_LEVELS = [1, 2, 3] as const;
</script>

<main class="task-view">
	{#if $taskViewData === null}
		<div class="loading">Loading task…</div>
	{:else}
		{@const data = $taskViewData}
		{@const offline = data.mode === 'offline'}

		<header class="header">
			<div class="title-row">
				<h1 class="title">
					<span class="id">{data.id}</span><span class="sep">:</span>
					<span class="name">{data.title}</span>
				</h1>
				<span class="badge status" data-status={statusLabel(data.status)}>
					{statusLabel(data.status)}
				</span>
				{#if offline}
					<span class="badge mode offline" title="Offline mode">offline</span>
				{/if}
			</div>
			{#if data.version}
				<p class="meta">v{data.version}</p>
			{/if}
		</header>

		<section class="section" aria-label="Statement">
			<h2 class="section-title">Statement</h2>
			<div class="statement">
				<!-- Host-rendered task markdown (trusted content from extension). -->
				{@html data.statement_html}
			</div>
		</section>

		<section class="section" aria-label="Hints">
			<h2 class="section-title">Hints</h2>
			<div class="hint-actions">
				{#each HINT_LEVELS as level (level)}
					{@const hint = hintForLevel(data.hints, level)}
					<button
						type="button"
						class="btn"
						disabled={!hint}
						onclick={() => revealHint(level)}
					>
						Hint {level}
					</button>
				{/each}
			</div>
			{#if revealedLevels.length > 0}
				<div class="hints-revealed">
					{#each revealedLevels as level (level)}
						{@const hint = hintForLevel(data.hints, level)}
						{#if hint}
							<article class="hint">
								<h3 class="hint-title">Hint {level}: {hint.title}</h3>
								<p class="hint-content">{hint.content}</p>
							</article>
						{/if}
					{/each}
				</div>
			{/if}
		</section>

		<section class="section actions" aria-label="Actions">
			<button type="button" class="btn primary" onclick={check}>Check</button>
			<button type="button" class="btn" onclick={openPy}>Open .py</button>
		</section>

		<section class="section results" aria-label="Results">
			<h2 class="section-title">Results</h2>
			<ResultsBody result={$checkResult} emptyMessage="Run Check to see results." />
		</section>
	{/if}
</main>

<style>
	:global(html),
	:global(body) {
		margin: 0;
		height: 100%;
		font-family: var(--vscode-font-family, 'Segoe UI', sans-serif);
		font-size: var(--vscode-font-size, 13px);
		color: var(--vscode-foreground);
		background: var(--vscode-editor-background);
	}

	:global(#app) {
		height: 100%;
	}

	.task-view {
		box-sizing: border-box;
		min-height: 100%;
		padding: 0.85rem 1rem 1.25rem;
		display: flex;
		flex-direction: column;
		gap: 0.85rem;
	}

	.loading {
		flex: 1;
		display: flex;
		align-items: center;
		justify-content: center;
		opacity: 0.65;
	}

	.header {
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
	}

	.title-row {
		display: flex;
		align-items: baseline;
		flex-wrap: wrap;
		gap: 0.45rem 0.65rem;
	}

	.title {
		margin: 0;
		font-size: 1.15rem;
		font-weight: 650;
		letter-spacing: -0.01em;
		line-height: 1.25;
	}

	.id {
		font-family: var(--vscode-editor-font-family, ui-monospace, monospace);
		font-size: 0.95em;
	}

	.sep {
		opacity: 0.55;
		margin: 0 0.15rem;
	}

	.name {
		font-weight: 650;
	}

	.badge {
		font-size: 0.7rem;
		font-weight: 600;
		letter-spacing: 0.02em;
		text-transform: uppercase;
		padding: 0.12rem 0.4rem;
		border: 1px solid color-mix(in srgb, var(--vscode-foreground) 18%, transparent);
		color: var(--vscode-descriptionForeground, var(--vscode-foreground));
		background: color-mix(in srgb, var(--vscode-foreground) 6%, transparent);
	}

	.badge.status[data-status='passed'] {
		border-color: color-mix(in srgb, #22c55e 55%, transparent);
		color: #22c55e;
		background: color-mix(in srgb, #22c55e 12%, transparent);
	}

	.badge.status[data-status='partial'] {
		border-color: color-mix(in srgb, #f59e0b 55%, transparent);
		color: #f59e0b;
		background: color-mix(in srgb, #f59e0b 12%, transparent);
	}

	.badge.status[data-status='failed'],
	.badge.status[data-status='error'],
	.badge.status[data-status='timeout'] {
		border-color: color-mix(in srgb, #ef4444 55%, transparent);
		color: #ef4444;
		background: color-mix(in srgb, #ef4444 12%, transparent);
	}

	.badge.mode.offline {
		opacity: 0.75;
		font-weight: 500;
	}

	.meta {
		margin: 0;
		font-size: 0.75rem;
		opacity: 0.65;
		font-variant-numeric: tabular-nums;
	}

	.section {
		display: flex;
		flex-direction: column;
		gap: 0.45rem;
	}

	.section-title {
		margin: 0;
		font-size: 0.72rem;
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.04em;
		opacity: 0.7;
	}

	.statement {
		line-height: 1.55;
		overflow-wrap: anywhere;
	}

	.statement :global(h1),
	.statement :global(h2),
	.statement :global(h3) {
		margin: 0.85em 0 0.35em;
		line-height: 1.3;
		font-weight: 650;
	}

	.statement :global(h1) {
		font-size: 1.2rem;
	}

	.statement :global(h2) {
		font-size: 1.05rem;
	}

	.statement :global(h3) {
		font-size: 0.95rem;
	}

	.statement :global(p) {
		margin: 0.45em 0;
	}

	.statement :global(ul),
	.statement :global(ol) {
		margin: 0.4em 0;
		padding-left: 1.35rem;
	}

	.statement :global(li) {
		margin: 0.15em 0;
	}

	.statement :global(pre) {
		margin: 0.55em 0;
		padding: 0.55rem 0.7rem;
		overflow-x: auto;
		border-radius: 2px;
		background: var(--vscode-textCodeBlock-background, color-mix(in srgb, var(--vscode-foreground) 8%, transparent));
		font-family: var(--vscode-editor-font-family, ui-monospace, monospace);
		font-size: 0.9em;
		line-height: 1.45;
	}

	.statement :global(code) {
		font-family: var(--vscode-editor-font-family, ui-monospace, monospace);
		font-size: 0.9em;
	}

	.statement :global(:not(pre) > code) {
		padding: 0.08em 0.3em;
		border-radius: 2px;
		background: var(--vscode-textCodeBlock-background, color-mix(in srgb, var(--vscode-foreground) 8%, transparent));
	}

	.hint-actions,
	.actions {
		display: flex;
		flex-wrap: wrap;
		gap: 0.4rem;
	}

	.hints-revealed {
		display: flex;
		flex-direction: column;
		gap: 0.55rem;
		margin-top: 0.15rem;
	}

	.hint {
		padding: 0.45rem 0;
		border-top: 1px solid color-mix(in srgb, var(--vscode-foreground) 12%, transparent);
	}

	.hint-title {
		margin: 0 0 0.25rem;
		font-size: 0.85rem;
		font-weight: 600;
	}

	.hint-content {
		margin: 0;
		opacity: 0.9;
		white-space: pre-wrap;
		line-height: 1.5;
	}

	.results :global(.waiting) {
		min-height: 6rem;
		padding: 0.75rem 0;
	}

	.btn {
		appearance: none;
		border: 1px solid color-mix(in srgb, var(--vscode-foreground) 18%, transparent);
		border-radius: 2px;
		padding: 0.28rem 0.55rem;
		font: inherit;
		font-size: 0.8rem;
		cursor: pointer;
		background: var(--vscode-button-secondaryBackground, transparent);
		color: var(--vscode-button-secondaryForeground, var(--vscode-foreground));
		transition:
			background-color 0.12s ease,
			border-color 0.12s ease,
			opacity 0.12s ease;
	}

	.btn:hover:not(:disabled) {
		background: var(
			--vscode-list-hoverBackground,
			color-mix(in srgb, var(--vscode-foreground) 8%, transparent)
		);
	}

	.btn:focus-visible {
		outline: 1px solid var(--vscode-focusBorder, var(--vscode-button-background));
		outline-offset: 1px;
	}

	.btn:disabled {
		opacity: 0.45;
		cursor: not-allowed;
	}

	.btn.primary {
		background: var(--vscode-button-background);
		color: var(--vscode-button-foreground);
		border-color: transparent;
	}

	.btn.primary:hover:not(:disabled) {
		background: var(--vscode-button-hoverBackground, var(--vscode-button-background));
	}
</style>
