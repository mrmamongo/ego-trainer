<script lang="ts">
	import { onMount } from 'svelte';
	import {
		listStudents,
		deleteUser,
		updateRole,
		resetPassword,
		createUser,
		type StudentSummary,
	} from '../api';

	let students = $state<StudentSummary[]>([]);
	let loading = $state(true);
	let error = $state('');
	let showForm = $state(false);

	let { onSelect, userRole }: { onSelect: (studentId: string, username: string) => void; userRole: string } = $props();
	let isAdmin = $derived(userRole === 'admin');

	async function load() {
		loading = true;
		error = '';
		try {
			students = await listStudents();
		} catch (e) {
			error = (e as Error).message;
		} finally {
			loading = false;
		}
	}

	async function handleDelete(student: StudentSummary) {
		if (!confirm(`Delete ${student.username}? This removes their progress too.`)) return;
		try {
			await deleteUser(student.student_id);
			await load();
		} catch (e) {
			alert((e as Error).message);
		}
	}

	async function handleRoleChange(student: StudentSummary, newRole: string) {
		if (newRole === student.role) return;
		try {
			await updateRole(student.student_id, newRole);
			await load();
		} catch (e) {
			alert((e as Error).message);
		}
	}

	async function handleResetPassword(student: StudentSummary) {
		const pw = prompt(`New password for ${student.username}:`);
		if (!pw) return;
		try {
			await resetPassword(student.student_id, pw);
			alert('Password updated.');
		} catch (e) {
			alert((e as Error).message);
		}
	}

	async function handleCreate(e: Event) {
		e.preventDefault();
		const form = e.target as HTMLFormElement;
		const fd = new FormData(form);
		const username = fd.get('username') as string;
		const password = fd.get('password') as string;
		const role = fd.get('role') as string;
		if (!username || !password) return;
		try {
			await createUser(username, password, role);
			form.reset();
			showForm = false;
			await load();
		} catch (err) {
			alert((err as Error).message);
		}
	}

	function statusColor(status: string): string {
		const s = (status || '').toLowerCase();
		if (s === 'passed') return 'green';
		if (s === 'partial') return 'yellow';
		return 'red';
	}

	function timeAgo(iso: string | null): string {
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

<div class="section">
	<div class="section-header">
		<h2>Students</h2>
		{#if isAdmin}
			<button class="btn" onclick={() => { showForm = !showForm; }}>
				{showForm ? 'Cancel' : '+ Add user'}
			</button>
		{/if}
	</div>

	{#if isAdmin && showForm}
		<form class="create-form" onsubmit={handleCreate}>
			<input name="username" placeholder="Username" required />
			<input name="password" type="password" placeholder="Password" required />
			<select name="role">
				<option value="student">student</option>
				<option value="mentor">mentor</option>
				<option value="admin">admin</option>
			</select>
			<button type="submit" class="btn primary">Create</button>
		</form>
	{/if}

	{#if loading}
		<div class="loading">Loading students…</div>
	{:else if error}
		<div class="error">{error}</div>
	{:else if students.length === 0}
		<div class="empty">No students yet</div>
	{:else}
		<table>
			<thead>
				<tr>
					<th>Student</th>
					<th>Role</th>
					<th class="num">Total</th>
					<th class="num">Passed</th>
					<th class="num">Partial</th>
					<th class="num">Failed</th>
					<th>Last activity</th>
					{#if isAdmin}<th></th>{/if}
				</tr>
			</thead>
			<tbody>
				{#each students as s (s.student_id)}
					<tr class="student-row" onclick={() => onSelect(s.student_id, s.username)}>
						<td>{s.username}</td>
						<td>
							{#if isAdmin}
								<select
									class="role-select"
									value={s.role}
									onchange={(e) => handleRoleChange(s, (e.target as HTMLSelectElement).value)}
									onclick={(e) => e.stopPropagation()}
								>
									<option value="student">student</option>
									<option value="mentor">mentor</option>
									<option value="admin">admin</option>
								</select>
							{:else}
								{s.role}
							{/if}
						</td>
						<td class="num">{s.tasks_total}</td>
						<td class="num" style="color:#22c55e">{s.tasks_passed}</td>
						<td class="num" style="color:#eab308">{s.tasks_partial}</td>
						<td class="num" style="color:#f87171">{s.tasks_failed}</td>
						<td>{timeAgo(s.last_activity)}</td>
						{#if isAdmin}
							<td class="actions">
								<button onclick={(e) => { e.stopPropagation(); handleResetPassword(s); }} title="Reset password">pw</button>
								<button onclick={(e) => { e.stopPropagation(); handleDelete(s); }} title="Delete" class="danger">×</button>
							</td>
						{/if}
					</tr>
				{/each}
			</tbody>
		</table>
	{/if}
</div>

<style>
	.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
	h2 { font-size: 0.9rem; font-weight: 600; }
	.btn {
		padding: 4px 12px; background: transparent; border: 1px solid #3c3c3c; border-radius: 4px;
		color: #d4d4d4; font-family: inherit; font-size: 0.8rem; cursor: pointer;
	}
	.btn:hover { border-color: #007acc; }
	.btn.primary { background: #007acc; color: #fff; border-color: transparent; }
	.btn.primary:hover { opacity: 0.9; }
	.create-form { display: flex; gap: 8px; margin-bottom: 16px; }
	.create-form input, .create-form select {
		padding: 6px 10px; background: #2d2d2d; border: 1px solid #3c3c3c; border-radius: 4px;
		color: #d4d4d4; font-family: inherit; font-size: 0.8rem;
	}
	.create-form input { flex: 1; }

	table { width: 100%; border-collapse: collapse; }
	th, td { text-align: left; padding: 6px 12px; border-bottom: 1px solid #3c3c3c; }
	th { font-size: 0.7rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: #858585; }
	tr:hover td { background: rgba(255,255,255,0.03); }
	.num { text-align: right; font-variant-numeric: tabular-nums; }

	.student-row { cursor: pointer; }
	.student-row:hover td { background: rgba(0,122,204,0.08); }

	.role-select {
		background: #2d2d2d; border: 1px solid #3c3c3c; border-radius: 3px;
		color: #d4d4d4; font-family: inherit; font-size: 0.75rem; padding: 2px 6px;
	}

	.actions { white-space: nowrap; }
	.actions button {
		padding: 2px 8px; background: transparent; border: 1px solid #3c3c3c; border-radius: 3px;
		color: #858585; font-family: inherit; font-size: 0.7rem; cursor: pointer; margin-left: 4px;
	}
	.actions button:hover { border-color: #007acc; color: #d4d4d4; }
	.actions .danger:hover { border-color: #f87171; color: #f87171; }

	.loading, .empty, .error { padding: 24px; text-align: center; color: #858585; }
	.error { color: #f87171; }
</style>
