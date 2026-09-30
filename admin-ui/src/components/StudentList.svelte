<script lang="ts">
	import { onMount } from 'svelte';
	import {
		listStudents,
		deleteUser,
		updateRole,
		resetPassword,
		createUser,
		authProviders,
		type StudentSummary,
	} from '../api';

	let students = $state<StudentSummary[]>([]);
	let loading = $state(true);
	let error = $state('');
	let actionError = $state('');
	let showForm = $state(false);
	let localAuthEnabled = $state(false);
	let search = $state('');
	let page = $state(1);
	const pageSize = 25;

	let { onSelect, userRole }: { onSelect: (studentId: string, username: string) => void; userRole: string } = $props();
	let isAdmin = $derived(userRole === 'admin');
	let filteredStudents = $derived.by(() => {
		const needle = search.trim().toLocaleLowerCase();
		if (!needle) return students;
		return students.filter((student) =>
			student.username.toLocaleLowerCase().includes(needle)
			|| student.student_id.toLocaleLowerCase().includes(needle),
		);
	});
	let pageCount = $derived(Math.max(1, Math.ceil(filteredStudents.length / pageSize)));
	let visibleStudents = $derived(filteredStudents.slice((page - 1) * pageSize, page * pageSize));

	async function load() {
		loading = true;
		error = '';
		actionError = '';
		try {
			students = await listStudents();
			page = 1;
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
			actionError = `Could not delete ${student.username}: ${(e as Error).message}`;
		}
	}

	async function handleRoleChange(student: StudentSummary, newRole: string) {
		if (newRole === student.role) return;
		if (newRole === 'mentor' && !confirm(`Назначить ${student.username} наставником? Он сможет назначать других наставников.`)) return;
		try {
			await updateRole(student.student_id, newRole);
			await load();
		} catch (e) {
			actionError = `Could not update role: ${(e as Error).message}`;
		}
	}

	async function handleResetPassword(student: StudentSummary) {
		const pw = prompt(`New password for ${student.username}:`);
		if (!pw) return;
		try {
			await resetPassword(student.student_id, pw);
			alert('Password updated.');
		} catch (e) {
			actionError = `Could not reset password: ${(e as Error).message}`;
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
			actionError = `Could not create user: ${(err as Error).message}`;
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

	onMount(() => { void load(); void authProviders().then(value => localAuthEnabled = value.local).catch(() => {}); });
</script>

<div class="section">
	<div class="section-header">
		<h2>Students</h2>
		<div class="header-actions">
			<button class="btn" type="button" onclick={load} disabled={loading}>{loading ? 'Refreshing…' : 'Refresh'}</button>
			{#if isAdmin && localAuthEnabled}
				<button class="btn" type="button" onclick={() => { showForm = !showForm; }}>
					{showForm ? 'Cancel' : '+ Add user'}
				</button>
			{/if}
		</div>
	</div>

	{#if actionError}<p class="error" role="alert">{actionError}</p>{/if}

	{#if isAdmin && localAuthEnabled && showForm}
		<form class="create-form" onsubmit={handleCreate}>
			<input name="username" placeholder="Username" required />
			<input name="password" type="password" placeholder="Password" required />
			<select name="role">
				<option value="student">student</option>
				<option value="admin">admin</option>
			</select>
			<button type="submit" class="btn primary">Create</button>
		</form>
	{/if}

	{#if loading}
		<div class="loading">Loading students…</div>
	{:else if error}
		<div class="error" role="alert">{error}</div>
		<button class="btn" type="button" onclick={load}>Retry</button>
	{:else if students.length === 0}
		<div class="empty">No students yet</div>
	{:else}
		<div class="list-toolbar">
			<label for="student-search">Search students</label>
			<input id="student-search" type="search" bind:value={search} oninput={() => { page = 1; }} placeholder="Username or ID" />
			<span>{filteredStudents.length} of {students.length}</span>
		</div>
		{#if filteredStudents.length === 0}
			<div class="empty">No students match “{search}”.</div>
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
				{#each visibleStudents as s (s.student_id)}
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
									<option value="admin">admin</option>
								</select>
							{:else if userRole === 'mentor'}
								<button type="button" onclick={(e) => { e.stopPropagation(); handleRoleChange(s, 'mentor'); }}>Назначить наставником</button>
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
								{#if localAuthEnabled}<button onclick={(e) => { e.stopPropagation(); handleResetPassword(s); }} title="Reset password">pw</button>{/if}
								<button onclick={(e) => { e.stopPropagation(); handleDelete(s); }} title="Delete" class="danger">×</button>
							</td>
						{/if}
					</tr>
				{/each}
			</tbody>
		</table>
			{#if pageCount > 1}
				<div class="pagination" aria-label="Student list pages">
					<button class="btn" type="button" onclick={() => page = Math.max(1, page - 1)} disabled={page === 1}>Previous</button>
					<span>Page {page} of {pageCount}</span>
					<button class="btn" type="button" onclick={() => page = Math.min(pageCount, page + 1)} disabled={page === pageCount}>Next</button>
				</div>
			{/if}
		{/if}
	{/if}
</div>

<style>
	.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
	.header-actions { display: flex; gap: 8px; }
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
	.list-toolbar { display: flex; align-items: center; gap: 8px; margin-bottom: 12px; color: #858585; font-size: 0.75rem; }
	.list-toolbar input { flex: 1; min-width: 120px; padding: 6px 10px; background: #2d2d2d; border: 1px solid #3c3c3c; border-radius: 4px; color: #d4d4d4; font: inherit; }
	.list-toolbar input:focus { outline: none; border-color: #007acc; }

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
	.pagination { display: flex; justify-content: center; align-items: center; gap: 12px; margin-top: 12px; font-size: 0.75rem; color: #858585; }

	.loading, .empty, .error { padding: 24px; text-align: center; color: #858585; }
	.error { color: #f87171; }
	@media (max-width: 600px) {
		.list-toolbar { align-items: stretch; flex-direction: column; }
		.create-form { flex-wrap: wrap; }
		table { display: block; overflow-x: auto; white-space: nowrap; }
	}
</style>
