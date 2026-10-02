<script lang="ts">
	import type { CheckResult, TaskRunSummary } from './shared/types';

	let {
		result = null,
		history = [],
		emptyMessage = 'No results yet.'
	}: {
		result?: CheckResult | null;
		history?: TaskRunSummary[];
		emptyMessage?: string;
	} = $props();

	const STATUS_COLORS: Record<string, string> = {
		passed: 'var(--vscode-testing-iconPassed, #22c55e)',
		partial: 'var(--vscode-charts-yellow, #eab308)',
		failed: 'var(--vscode-testing-iconFailed, #f87171)',
		error: 'var(--vscode-editorError-foreground, #f87171)',
		timeout: 'var(--vscode-charts-orange, #fb923c)',
		no_tests: 'var(--vscode-descriptionForeground, #9ca3af)'
	};

	const STATUS_LABELS: Record<string, string> = {
		passed: 'Пройдено',
		partial: 'Частично',
		failed: 'Есть ошибки',
		error: 'Ошибка',
		timeout: 'Таймаут',
		no_tests: 'Нет тестов'
	};

	function statusColor(status: string): string {
		return STATUS_COLORS[status.toLowerCase()] ?? 'var(--vscode-descriptionForeground, #9ca3af)';
	}

	function statusLabel(status: string): string {
		return STATUS_LABELS[status.toLowerCase()] ?? status.toUpperCase();
	}

	function breadcrumb(taskId: string): string {
		const match = taskId.match(/^([A-Za-z]+)(\d+)$/);
		return match ? `${match[1].toUpperCase()} > ${taskId.toUpperCase()}` : taskId;
	}

	function formatRunTime(run: TaskRunSummary): string {
		const date = new Date(run.finished_at || run.started_at);
		return Number.isNaN(date.getTime()) ? '—' : date.toLocaleString(undefined, { dateStyle: 'short', timeStyle: 'short' });
	}
</script>

{#if history && history.length > 0}
	<section class="history" aria-label="Previous attempts">
		<h3>Предыдущие попытки</h3>
		<table>
			<thead><tr><th>Время</th><th>Статус</th><th>Тесты</th></tr></thead>
			<tbody>
				{#each history as run (run.id)}
					<tr>
						<td>{formatRunTime(run)}</td>
						<td><span class="dot" style:background={statusColor(run.status)}></span>{statusLabel(run.status)}</td>
						<td>{run.passed_tests}/{run.total_tests}</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</section>
{/if}

{#if result === null}
	<div class="waiting">{emptyMessage}</div>
{:else}
	{@const color = statusColor(result.status)}

	<div
		class="header"
		style:--status-color={color}
		style:background="color-mix(in srgb, {color} 14%, transparent)"
		style:border-color="color-mix(in srgb, {color} 50%, transparent)"
	>
		<div class="crumb">{breadcrumb(result.task_id)}</div>
		<div class="title-row">
			<span class="badge" style:background={color}>{statusLabel(result.status)}</span>
			<span class="title">{result.passed_tests} из {result.total_tests} тестов · {result.task_id}</span>
		</div>
	</div>

	{#if result.understanding}
        <p>Тесты пройдены. {result.understanding.status === 'confirmed'
            ? 'Понимание решения подтверждено.' : 'Следующий этап — защита решения в ассистенте.'}</p>
    {/if}
	{#if result.total_tests === 0}
		<div class="no-tests">У задания пока нет тестов.</div>
	{:else}
		{#each result.results as tr, i (i)}
			{@const rowColor = statusColor(tr.passed ? 'passed' : 'failed')}
			<div class="test-row" style:border-left-color={rowColor}>
				<div class="test-header">
					<span class="test-tag" style:background={rowColor}>
						{tr.passed ? '✓' : '✕'}
					</span>
					<span>{tr.description}</span>
				</div>
				{#if !tr.passed}
					<div class="detail">
						<div>
							<span class="label">Ожидалось:</span>
							<code>{tr.expected_repr}</code>
						</div>
						{#if tr.actual_repr !== null}
							<div>
								<span class="label">Получено:</span>
								<code>{tr.actual_repr}</code>
							</div>
						{/if}
						{#if tr.error}
							<div class="error">
								<span class="label">Ошибка:</span>
								<pre>{tr.error}</pre>
							</div>
						{/if}
					</div>
				{/if}
			</div>
		{/each}
	{/if}

	{#if result.log?.trim()}
		<details class="log">
			<summary>Подробный лог</summary>
			<pre>{result.log}</pre>
		</details>
	{/if}
{/if}

<style>
	.history {
		margin-bottom: 0.85rem;
		border-top: 1px solid color-mix(in srgb, var(--vscode-foreground) 12%, transparent);
		border-bottom: 1px solid color-mix(in srgb, var(--vscode-foreground) 12%, transparent);
	}

	.history h3 {
		margin: 0;
		padding: 0.45rem 0;
		font-size: 0.75rem;
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.04em;
		opacity: 0.75;
	}

	.history table {
		width: 100%;
		border-collapse: collapse;
		font-size: 0.8rem;
	}

	.history th,
	.history td {
		padding: 0.3rem 0.4rem;
		text-align: left;
		border-top: 1px solid color-mix(in srgb, var(--vscode-foreground) 8%, transparent);
	}

	.history th {
		font-size: 0.7rem;
		font-weight: 600;
		opacity: 0.65;
	}

	.history td:last-child {
		font-variant-numeric: tabular-nums;
		text-align: right;
	}

	.dot {
		display: inline-block;
		width: 8px;
		height: 8px;
		margin-right: 6px;
		border-radius: 50%;
	}

	.waiting {
		display: flex;
		align-items: center;
		justify-content: center;
		min-height: 40vh;
		opacity: 0.6;
		text-align: center;
	}

	.header {
		display: flex;
		flex-direction: column;
		gap: 6px;
		padding: 12px 14px;
		border-radius: 6px;
		border: 1px solid;
		margin-bottom: 14px;
	}

	.crumb {
		font-size: 0.7rem;
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.06em;
		opacity: 0.6;
	}

	.title-row {
		display: flex;
		align-items: center;
		flex-wrap: wrap;
		gap: 8px;
	}

	.badge {
		font-size: 0.7rem;
		font-weight: 700;
		letter-spacing: 0.04em;
		padding: 2px 7px;
		border-radius: 3px;
		color: var(--vscode-editor-background, #0a0a0a);
	}

	.title {
		font-size: 0.9rem;
		font-weight: 600;
	}

	.test-row {
		border-left: 3px solid;
		padding: 8px 12px;
		margin: 4px 0;
		background: var(--vscode-editor-inactiveSelectionBackground, transparent);
		border-radius: 0 4px 4px 0;
	}

	.test-header {
		display: flex;
		align-items: center;
		gap: 8px;
	}

	.test-tag {
		font-size: 0.65rem;
		font-weight: 700;
		letter-spacing: 0.04em;
		padding: 1px 6px;
		border-radius: 3px;
		min-width: 36px;
		text-align: center;
		color: var(--vscode-editor-background, #0a0a0a);
	}

	.detail {
		margin-top: 8px;
		padding-left: 24px;
		font-size: 13px;
		overflow-wrap: anywhere;
	}

	.detail .label {
		font-weight: 600;
		opacity: 0.7;
	}

	.detail code {
		background: var(--vscode-textCodeBlock-background, transparent);
		padding: 2px 6px;
		border-radius: 3px;
		font-family: var(--vscode-editor-font-family, monospace);
	}

	.detail .error pre {
		margin-top: 4px;
		padding: 8px;
		background: color-mix(in srgb, var(--vscode-editorError-foreground, #f87171) 12%, transparent);
		border-radius: 4px;
		font-size: 12px;
		overflow-x: auto;
		white-space: pre-wrap;
	}

	.no-tests {
		padding: 24px;
		text-align: center;
		opacity: 0.6;
	}

	.log {
		margin-top: 12px;
		border-top: 1px solid color-mix(in srgb, var(--vscode-foreground) 12%, transparent);
		padding-top: 8px;
	}

	.log summary {
		cursor: pointer;
		font-size: 0.75rem;
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.04em;
		opacity: 0.7;
		user-select: none;
	}

	.log pre {
		margin: 8px 0 0;
		padding: 8px 10px;
		overflow-x: auto;
		white-space: pre-wrap;
		border-radius: 4px;
		background: var(--vscode-textCodeBlock-background, color-mix(in srgb, var(--vscode-foreground) 8%, transparent));
		font-family: var(--vscode-editor-font-family, ui-monospace, monospace);
		font-size: 12px;
		line-height: 1.45;
	}
</style>
