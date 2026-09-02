<script lang="ts">
	import { onMount } from 'svelte';
	import { getStudentProgress, type ProgressRow } from '../api';

	let { studentId, username, onBack }: { studentId: string; username: string; onBack: () => void } = $props();

	let progress = $state<ProgressRow[]>([]);
	let loading = $state(true);
	let error = $state('');

	async function load() {
		loading = true;
		error = '';
		try {
			progress = await getStudentProgress(studentId);
		} catch (e) {
			error = (e as Error).message;
		} finally {
			loading = false;
		}
	}

	function statusColor(status: string): string {
		const s = (status || '').toLowerCase();
		if (s === 'passed') return 'green';
		if (s === 'partial') return 'yellow';
		return 'red';
	}

	function statusLabel(status: string): string {
		const s = (status || '').toLowerCase();
		if (s === 'passed') return 'PASS';
		if (s === 'partial') return 'PART';
		if (s === 'failed') return 'FAIL';
		return (status || '—').toUpperCase();
	}

	function timeAgo(iso: string): string {
		if (!iso) return '—';
		const t = new Date(iso).getTime();
		const s = Math.round((Date.now() - t) / 1000);
		if (s < 60) return `${s}s ago`;
		if (s < 3600) return `${Math.round(s / 60)}m ago`;
		if (s < 86400) return `${Math.round(s / 3600)}h ago`;
		return `${Math.round(s / 86400)}d ago`;
	}

	onMount(() => { load(); });
</script>

<div class="detail">
	<button class="back" type="button" onclick={onBack}>&larr; Back to students</button>
	<h2>Progress: {username}</h2>

	{#if loading}
		<div class="loading">Loading progress…</div>
	{:else if error}
		<div class="error">{error}</div>
	{:else if progress.length === 0}
		<div class="empty">No progress yet</div>
	{:else}
		<table>
			<thead>
				<tr>
					<th>Task</th>
					<th>Status</th>
					<th class="num">Score</th>
					<th class="num">Attempts</th>
					<th>Last run</th>
				</tr>
			</thead>
			<tbody>
				{#each progress as r (r.task_id + r.version)}
					<tr>
						<td>{r.task_id}</td>
						<td>
							<span class="dot {statusColor(r.status)}"></span>
							{statusLabel(r.status)}
						</td>
						<td class="num">{r.passed_tests}/{r.total_tests}</td>
						<td class="num">{r.attempts}</td>
						<td>{timeAgo(r.last_run_at)}</td>
					</tr>
				{/each}
			</tbody>
		</table>
	{/if}
</div>

<style>
	.back {
		display: inline-block; margin-bottom: 16px; color: #007acc;
		padding: 0; border: 0; background: transparent; cursor: pointer;
		font-family: inherit; font-size: 0.8rem; text-decoration: none;
	}
	.back:hover { text-decoration: underline; }
	h2 { font-size: 1rem; font-weight: 600; margin-bottom: 12px; }

	table { width: 100%; border-collapse: collapse; }
	th, td { text-align: left; padding: 6px 12px; border-bottom: 1px solid #3c3c3c; }
	th { font-size: 0.7rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: #858585; }
	.num { text-align: right; font-variant-numeric: tabular-nums; }

	.dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 6px; }
	.dot.green { background: #22c55e; }
	.dot.yellow { background: #eab308; }
	.dot.red { background: #f87171; }

	.loading, .empty, .error { padding: 24px; text-align: center; color: #858585; }
	.error { color: #f87171; }
</style>
