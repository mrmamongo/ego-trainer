<script lang="ts">
	import { onMount } from 'svelte';
	import { getOverview, type OverviewDTO, type SyncLogRow } from '../api';

	let overview = $state<OverviewDTO | null>(null);
	let loading = $state(true);
	let error = $state('');

	async function load() {
		loading = true;
		error = '';
		try {
			overview = await getOverview();
		} catch (e) {
			error = (e as Error).message;
		} finally {
			loading = false;
		}
	}

	function timeAgo(iso: string | null): string {
		if (!iso) return '—';
		const t = new Date(iso).getTime();
		if (Number.isNaN(t)) return iso;
		const s = Math.round((Date.now() - t) / 1000);
		if (s < 0) return 'just now';
		if (s < 60) return `${s}s ago`;
		if (s < 3600) return `${Math.round(s / 60)}m ago`;
		if (s < 86400) return `${Math.round(s / 3600)}h ago`;
		return `${Math.round(s / 86400)}d ago`;
	}

	function syncStatusClass(s: SyncLogRow | null): string {
		if (!s) return 'none';
		const st = (s.status || '').toLowerCase();
		if (st === 'ok' || st === 'success') return 'ok';
		if (st === 'running') return 'running';
		return 'err';
	}

	function syncLabel(s: SyncLogRow | null): string {
		if (!s) return 'never';
		return (s.status || '—');
	}

	function errorSummary(s: SyncLogRow | null): string {
		if (!s) return '';
		if (s.errors <= 0 && !s.error_details) return 'No errors.';
		const parts: string[] = [];
		parts.push(`${s.errors} error(s)`);
		if (s.error_details) parts.push(s.error_details);
		return parts.join(' — ');
	}

	onMount(() => { load(); });
</script>

<div class="section">
	<div class="section-header">
		<h2>Overview</h2>
		<button class="btn" type="button" onclick={load} disabled={loading} aria-label="Refresh overview">
			{loading ? 'Refreshing…' : 'Refresh'}
		</button>
	</div>

	{#if loading && !overview}
		<div class="loading">Loading overview…</div>
	{:else if error}
		<div class="error">{error}</div>
	{:else if overview}
		<div class="grid">
			<div class="card">
				<span class="card-label">Server</span>
				<span class="card-value status-{overview.server === 'ok' ? 'ok' : 'err'}">{overview.server}</span>
			</div>
			<div class="card">
				<span class="card-label">Projects</span>
				<span class="card-value">{overview.counts.projects}</span>
			</div>
			<div class="card">
				<span class="card-label">Folders</span>
				<span class="card-value">{overview.counts.folders}</span>
			</div>
			<div class="card">
				<span class="card-label">Tasks</span>
				<span class="card-value">{overview.counts.tasks}</span>
			</div>
			<div class="card">
				<span class="card-label">Students</span>
				<span class="card-value">{overview.counts.students}</span>
			</div>
		</div>

		<div class="sync-block">
			<h3>Latest sync</h3>
			<dl>
				<div><dt>Status</dt><dd><span class="sync-pill {syncStatusClass(overview.latest_sync)}">{syncLabel(overview.latest_sync)}</span></dd></div>
				<div><dt>Source</dt><dd>{overview.latest_sync?.source ?? '—'}</dd></div>
				<div><dt>Repo</dt><dd>{overview.latest_sync?.repo_url || '—'}</dd></div>
				<div><dt>Git SHA</dt><dd>{overview.latest_sync?.git_sha ?? '—'}</dd></div>
				<div><dt>Started</dt><dd>{overview.latest_sync ? timeAgo(overview.latest_sync.started_at) : '—'}</dd></div>
				<div><dt>Finished</dt><dd>{overview.latest_sync ? timeAgo(overview.latest_sync.finished_at) : '—'}</dd></div>
				<div><dt>Added</dt><dd>{overview.latest_sync?.added ?? 0}</dd></div>
				<div><dt>Updated</dt><dd>{overview.latest_sync?.updated ?? 0}</dd></div>
				<div><dt>Skipped</dt><dd>{overview.latest_sync?.skipped ?? 0}</dd></div>
				<div><dt>Errors</dt><dd>{overview.latest_sync?.errors ?? 0}</dd></div>
				<div class="full"><dt>Error summary</dt><dd>{errorSummary(overview.latest_sync)}</dd></div>
			</dl>
		</div>
	{/if}
</div>

<style>
	.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
	h2 { font-size: 0.9rem; font-weight: 600; }
	h3 { font-size: 0.8rem; font-weight: 600; margin: 20px 0 10px; color: #858585; text-transform: uppercase; letter-spacing: 0.05em; }
	.btn {
		padding: 4px 12px; background: transparent; border: 1px solid #3c3c3c; border-radius: 4px;
		color: #d4d4d4; font-family: inherit; font-size: 0.8rem; cursor: pointer;
	}
	.btn:hover:not(:disabled) { border-color: #007acc; }
	.btn:disabled { opacity: 0.5; cursor: not-allowed; }

	.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 12px; }
	.card {
		display: flex; flex-direction: column; gap: 4px; padding: 14px 16px;
		background: #2d2d2d; border: 1px solid #3c3c3c; border-radius: 6px;
	}
	.card-label { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.05em; color: #858585; }
	.card-value { font-size: 1.4rem; font-weight: 700; font-variant-numeric: tabular-nums; }
	.status-ok { color: #22c55e; }
	.status-err { color: #f87171; }

	.sync-block { margin-top: 8px; }
	dl { display: grid; grid-template-columns: max-content 1fr; gap: 6px 16px; margin: 0; }
	dl div { display: contents; }
	dl .full { grid-column: 1 / -1; }
	dt { color: #858585; font-size: 0.75rem; }
	dd { margin: 0; font-size: 0.85rem; word-break: break-word; }

	.sync-pill {
		display: inline-block; padding: 1px 8px; border-radius: 10px; font-size: 0.7rem;
		border: 1px solid #3c3c3c; text-transform: capitalize;
	}
	.sync-pill.ok { color: #22c55e; border-color: #22c55e; }
	.sync-pill.running { color: #eab308; border-color: #eab308; }
	.sync-pill.err { color: #f87171; border-color: #f87171; }
	.sync-pill.none { color: #858585; }

	.loading, .error { padding: 24px; text-align: center; color: #858585; }
	.error { color: #f87171; }

	@media (max-width: 600px) {
		dl { grid-template-columns: 1fr; }
	}
</style>
