<script lang="ts">
	import { dashboardData } from './shared/store';
	import { postToHost } from './shared/api';
	import type { DashboardRow, TaskStatusFilter } from './shared/types';

	let blockFilter = $state('all');
	let statusFilter = $state<TaskStatusFilter>('all');

	function normalizeStatus(status: string | undefined | null): string {
		return (status ?? '').trim().toLowerCase();
	}

	function isNewStatus(status: string): boolean {
		return status === '' || status === 'new';
	}

	function isFailedStatus(status: string): boolean {
		return status === 'failed' || status === 'error' || status === 'timeout';
	}

	function matchesStatus(status: string, filter: TaskStatusFilter): boolean {
		if (filter === 'all') return true;
		if (filter === 'new') return isNewStatus(status);
		if (filter === 'failed') return isFailedStatus(status);
		return status === filter;
	}

	function statusIcon(status: string): string {
		const s = normalizeStatus(status);
		if (s === 'passed') return '✓';
		if (s === 'partial') return '◐';
		if (isFailedStatus(s)) return '✗';
		return '○';
	}

	function statusLabel(status: string): string {
		const s = normalizeStatus(status);
		if (isNewStatus(s)) return 'new';
		if (s === 'error' || s === 'timeout') return s;
		return s || 'new';
	}

	function formatLastRun(value: string | null): string {
		if (!value) return '—';
		const date = new Date(value);
		if (Number.isNaN(date.getTime())) return '—';
		return date.toLocaleString(undefined, {
			dateStyle: 'short',
			timeStyle: 'short'
		});
	}

	function openTask(taskId: string) {
		postToHost({ type: 'dashboard.open', taskId });
	}

	function checkTask(taskId: string) {
		postToHost({ type: 'dashboard.check', taskId });
	}

	function hintsTask(taskId: string) {
		postToHost({ type: 'dashboard.hints', taskId });
	}

	function refresh() {
		postToHost({ type: 'dashboard.refresh' });
	}

	function pullAll() {
		postToHost({ type: 'dashboard.pullAll' });
	}

	function pushProgress() {
		postToHost({ type: 'dashboard.push' });
	}

	const filteredRows = $derived.by(() => {
		const data = $dashboardData;
		if (!data) return [] as DashboardRow[];
		return data.rows.filter((row) => {
			const blockOk = blockFilter === 'all' || row.block === blockFilter;
			const statusOk = matchesStatus(normalizeStatus(row.status), statusFilter);
			return blockOk && statusOk;
		});
	});

	const progressPct = $derived.by(() => {
		const data = $dashboardData;
		if (!data || data.summary.total <= 0) return 0;
		return Math.round((data.summary.passed / data.summary.total) * 100);
	});
</script>

<main class="dashboard">
	{#if $dashboardData === null}
		<div class="loading">Loading…</div>
	{:else}
		{@const data = $dashboardData}
		{@const offline = data.mode === 'offline'}

		<header class="header">
			<div class="brand-row">
				<h1 class="brand">Ego Trainer</h1>
				<span class="mode" class:offline data-mode={data.mode}>
					{data.mode === 'server' ? 'Server' : 'Offline'}
				</span>
			</div>
		</header>

		{#if data.error}
			<p class="error" role="alert">{data.error}</p>
		{/if}

		<section class="summary" aria-label="Progress summary">
			<div class="metrics">
				<div class="metric">
					<span class="metric-value">{data.summary.passed}</span>
					<span class="metric-label">passed</span>
				</div>
				<div class="metric">
					<span class="metric-value">{data.summary.partial}</span>
					<span class="metric-label">partial</span>
				</div>
				<div class="metric">
					<span class="metric-value">{data.summary.new}</span>
					<span class="metric-label">new</span>
				</div>
				<div class="metric">
					<span class="metric-value">{data.summary.failed}</span>
					<span class="metric-label">failed</span>
				</div>
				<div class="metric">
					<span class="metric-value">{data.summary.total}</span>
					<span class="metric-label">total</span>
				</div>
			</div>
			<div class="progress" aria-label="{progressPct}% passed">
				<div class="progress-track">
					<div class="progress-fill" style:width="{progressPct}%"></div>
				</div>
				<span class="progress-label">{progressPct}% passed</span>
			</div>
		</section>

		<section class="filters" aria-label="Filters">
			<label class="filter">
				<span class="filter-label">Block</span>
				<select bind:value={blockFilter}>
					<option value="all">All blocks</option>
					{#each data.blocks as block (block)}
						<option value={block}>{block}</option>
					{/each}
				</select>
			</label>
			<label class="filter">
				<span class="filter-label">Status</span>
				<select bind:value={statusFilter}>
					<option value="all">all</option>
					<option value="passed">passed</option>
					<option value="partial">partial</option>
					<option value="new">new</option>
					<option value="failed">failed</option>
				</select>
			</label>
		</section>

		<section class="table-wrap" aria-label="Tasks">
			<table class="tasks">
				<thead>
					<tr>
						<th>Task</th>
						<th>Title</th>
						<th>Status</th>
						<th>Tests</th>
						<th>Attempts</th>
						<th>Last run</th>
						<th>Actions</th>
					</tr>
				</thead>
				<tbody>
					{#if filteredRows.length === 0}
						<tr>
							<td colspan="7" class="empty">No tasks match the current filters.</td>
						</tr>
					{:else}
						{#each filteredRows as row (row.id)}
							{@const status = normalizeStatus(row.status)}
							<tr>
								<td class="mono">{row.id}</td>
								<td>{row.title}</td>
								<td>
									<span class="status" data-status={statusLabel(status)}>
										<span class="status-icon" aria-hidden="true">{statusIcon(status)}</span>
										{statusLabel(status)}
									</span>
								</td>
								<td class="mono">{row.passed_tests}/{row.total_tests}</td>
								<td class="mono">{row.attempts}</td>
								<td class="muted">{formatLastRun(row.last_run_at)}</td>
								<td class="actions">
									<button type="button" class="btn" onclick={() => openTask(row.id)}>Open</button>
									<button type="button" class="btn" onclick={() => checkTask(row.id)}>Check</button>
									<button type="button" class="btn" onclick={() => hintsTask(row.id)}>Hints</button>
								</td>
							</tr>
						{/each}
					{/if}
				</tbody>
			</table>
		</section>

		<footer class="footer">
			<button type="button" class="btn primary" onclick={pullAll} disabled={offline} title={offline ? 'Unavailable offline' : 'Pull all tasks'}>
				Pull All
			</button>
			<button
				type="button"
				class="btn primary"
				onclick={pushProgress}
				disabled={offline}
				title={offline ? 'Unavailable offline — switch to Server mode' : 'Push local progress to server'}
			>
				Push Progress
			</button>
			<button type="button" class="btn" onclick={refresh}>Refresh</button>
		</footer>
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

	.dashboard {
		box-sizing: border-box;
		min-height: 100%;
		padding: 1rem 1.25rem 1.25rem;
		display: flex;
		flex-direction: column;
		gap: 0.9rem;
	}

	.loading {
		flex: 1;
		display: flex;
		align-items: center;
		justify-content: center;
		opacity: 0.65;
	}

	.header {
		animation: header-in 0.45s ease-out both;
	}

	.brand-row {
		display: flex;
		align-items: baseline;
		gap: 0.75rem;
		flex-wrap: wrap;
	}

	.brand {
		margin: 0;
		font-size: 1.35rem;
		font-weight: 700;
		letter-spacing: -0.02em;
		line-height: 1.2;
	}

	.mode {
		font-size: 0.75rem;
		font-weight: 600;
		letter-spacing: 0.02em;
		text-transform: uppercase;
		padding: 0.15rem 0.45rem;
		border: 1px solid color-mix(in srgb, var(--vscode-focusBorder, var(--vscode-button-background)) 55%, transparent);
		color: var(--vscode-descriptionForeground, var(--vscode-foreground));
		background: color-mix(in srgb, var(--vscode-button-background) 12%, transparent);
	}

	.mode.offline {
		border-color: color-mix(in srgb, var(--vscode-foreground) 22%, transparent);
		background: color-mix(in srgb, var(--vscode-foreground) 6%, transparent);
	}

	.error {
		margin: 0;
		padding: 0.5rem 0.65rem;
		border-left: 3px solid var(--vscode-inputValidation-errorBorder, #f14c4c);
		background: color-mix(
			in srgb,
			var(--vscode-inputValidation-errorBackground, #f14c4c) 18%,
			transparent
		);
		color: var(--vscode-errorForeground, var(--vscode-foreground));
	}

	.summary {
		display: flex;
		flex-direction: column;
		gap: 0.55rem;
	}

	.metrics {
		display: flex;
		flex-wrap: wrap;
		gap: 0.35rem 1.25rem;
	}

	.metric {
		display: flex;
		align-items: baseline;
		gap: 0.35rem;
		min-width: 4.5rem;
	}

	.metric-value {
		font-weight: 650;
		font-variant-numeric: tabular-nums;
	}

	.metric-label {
		font-size: 0.8rem;
		opacity: 0.7;
		text-transform: lowercase;
	}

	.progress {
		display: flex;
		align-items: center;
		gap: 0.65rem;
	}

	.progress-track {
		flex: 1;
		height: 0.35rem;
		border-radius: 2px;
		background: color-mix(in srgb, var(--vscode-foreground) 12%, transparent);
		overflow: hidden;
	}

	.progress-fill {
		height: 100%;
		border-radius: 2px;
		background: var(--vscode-button-background);
		box-shadow: inset 0 0 0 1px color-mix(in srgb, var(--vscode-focusBorder, transparent) 40%, transparent);
		transition: width 0.35s ease;
	}

	.progress-label {
		flex-shrink: 0;
		font-size: 0.8rem;
		opacity: 0.75;
		font-variant-numeric: tabular-nums;
	}

	.filters {
		display: flex;
		flex-wrap: wrap;
		gap: 0.75rem 1rem;
	}

	.filter {
		display: flex;
		align-items: center;
		gap: 0.4rem;
	}

	.filter-label {
		font-size: 0.8rem;
		opacity: 0.75;
	}

	select {
		appearance: none;
		min-width: 9rem;
		padding: 0.25rem 0.5rem;
		border: 1px solid var(--vscode-dropdown-border, var(--vscode-input-border, transparent));
		border-radius: 2px;
		background: var(--vscode-dropdown-background, var(--vscode-input-background));
		color: var(--vscode-dropdown-foreground, var(--vscode-input-foreground, var(--vscode-foreground)));
		font: inherit;
	}

	select:focus-visible {
		outline: 1px solid var(--vscode-focusBorder, var(--vscode-button-background));
		outline-offset: 1px;
	}

	.table-wrap {
		overflow-x: auto;
		border-top: 1px solid color-mix(in srgb, var(--vscode-foreground) 14%, transparent);
		border-bottom: 1px solid color-mix(in srgb, var(--vscode-foreground) 14%, transparent);
	}

	.tasks {
		width: 100%;
		border-collapse: collapse;
		min-width: 44rem;
	}

	th,
	td {
		padding: 0.4rem 0.55rem;
		text-align: left;
		vertical-align: middle;
		white-space: nowrap;
	}

	th {
		font-size: 0.75rem;
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.03em;
		opacity: 0.7;
		border-bottom: 1px solid color-mix(in srgb, var(--vscode-foreground) 16%, transparent);
	}

	tbody tr {
		transition: background-color 0.12s ease;
	}

	tbody tr:hover {
		background: var(
			--vscode-list-hoverBackground,
			color-mix(in srgb, var(--vscode-foreground) 6%, transparent)
		);
	}

	td {
		border-bottom: 1px solid color-mix(in srgb, var(--vscode-foreground) 8%, transparent);
	}

	.mono {
		font-family: var(--vscode-editor-font-family, ui-monospace, monospace);
		font-size: 0.9em;
		font-variant-numeric: tabular-nums;
	}

	.muted {
		opacity: 0.75;
	}

	.empty {
		text-align: center;
		opacity: 0.65;
		padding: 1.25rem 0.55rem;
	}

	.status {
		display: inline-flex;
		align-items: center;
		gap: 0.3rem;
		text-transform: lowercase;
	}

	.status-icon {
		font-weight: 700;
		opacity: 0.9;
	}

	.actions {
		display: flex;
		gap: 0.3rem;
	}

	.footer {
		display: flex;
		flex-wrap: wrap;
		gap: 0.45rem;
		padding-top: 0.15rem;
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

	@keyframes header-in {
		from {
			opacity: 0;
			transform: translateY(-0.25rem);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}

	@media (prefers-reduced-motion: reduce) {
		.header {
			animation: none;
		}

		.progress-fill,
		tbody tr {
			transition: none;
		}
	}
</style>
