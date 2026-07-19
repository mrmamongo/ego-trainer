<script lang="ts">
	import type { CheckResult } from './shared/types';

	let {
		result = null,
		emptyMessage = 'No results yet.'
	}: {
		result?: CheckResult | null;
		emptyMessage?: string;
	} = $props();

	const STATUS_COLORS: Record<string, string> = {
		passed: '#22c55e',
		partial: '#f59e0b',
		failed: '#ef4444',
		error: '#ef4444',
		timeout: '#ef4444',
		no_tests: '#6b7280'
	};

	const STATUS_ICONS: Record<string, string> = {
		passed: '✓',
		partial: '◐',
		failed: '✗',
		error: '⚠',
		timeout: '⏱',
		no_tests: '○'
	};

	function statusColor(status: string): string {
		return STATUS_COLORS[status] ?? '#6b7280';
	}

	function statusIcon(status: string): string {
		return STATUS_ICONS[status] ?? '?';
	}
</script>

{#if result === null}
	<div class="waiting">{emptyMessage}</div>
{:else}
	{@const color = statusColor(result.status)}

	<div
		class="header"
		style:--status-color={color}
		style:background="{color}22"
		style:border-color={color}
	>
		<span class="icon">{statusIcon(result.status)}</span>
		<div>
			<div class="title">
				Task {result.task_id} — {result.status.toUpperCase()}
			</div>
			<div class="summary">
				{result.passed_tests}/{result.total_tests} tests passed
			</div>
		</div>
	</div>

	{#if result.total_tests === 0}
		<div class="no-tests">No tests available for this task.</div>
	{:else}
		{#each result.results as tr, i (i)}
			{@const rowColor = tr.passed ? '#22c55e' : '#ef4444'}
			<div class="test-row" style:border-left-color={rowColor}>
				<div class="test-header">
					<span class="test-icon" style:color={rowColor}>
						{tr.passed ? '✓' : '✗'}
					</span>
					<span>{tr.description}</span>
				</div>
				{#if !tr.passed}
					<div class="detail">
						<div>
							<span class="label">Expected:</span>
							<code>{tr.expected_repr}</code>
						</div>
						{#if tr.actual_repr !== null}
							<div>
								<span class="label">Got:</span>
								<code>{tr.actual_repr}</code>
							</div>
						{/if}
						{#if tr.error}
							<div class="error">
								<span class="label">Error:</span>
								<pre>{tr.error}</pre>
							</div>
						{/if}
					</div>
				{/if}
			</div>
		{/each}
	{/if}
{/if}

<style>
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
		align-items: center;
		gap: 12px;
		padding: 16px;
		border-radius: 8px;
		border: 1px solid;
		margin-bottom: 16px;
	}

	.header .icon {
		font-size: 28px;
		color: var(--status-color);
	}

	.header .title {
		font-size: 18px;
		font-weight: 600;
	}

	.header .summary {
		font-size: 14px;
		opacity: 0.8;
	}

	.test-row {
		border-left: 3px solid;
		padding: 8px 12px;
		margin: 4px 0;
		background: var(--vscode-editor-inactive-selection-background, #f5f5f5);
	}

	.test-header {
		display: flex;
		align-items: center;
		gap: 8px;
	}

	.test-icon {
		font-weight: bold;
	}

	.detail {
		margin-top: 8px;
		padding-left: 24px;
		font-size: 13px;
	}

	.detail .label {
		font-weight: 600;
		opacity: 0.7;
	}

	.detail code {
		background: var(--vscode-textCodeBlock-background, #eee);
		padding: 2px 6px;
		border-radius: 3px;
		font-family: var(--vscode-editor-font-family, monospace);
	}

	.detail .error pre {
		margin-top: 4px;
		padding: 8px;
		background: color-mix(in srgb, #ef4444 12%, var(--vscode-editor-background, #fff));
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
</style>
