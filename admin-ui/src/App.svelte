<script lang="ts">
	import { onMount } from 'svelte';
	import { getToken, setToken, me, type AuthResponse, type CatalogTaskDTO } from './api';
	import Login from './components/Login.svelte';
	import Overview from './components/Overview.svelte';
	import StudentList from './components/StudentList.svelte';
	import StudentDetail from './components/StudentDetail.svelte';
	import Catalog from './components/Catalog.svelte';
	import TaskStudio from './components/TaskStudio.svelte';

	type View = 'overview' | 'students' | 'catalog';

	let loggedIn = $state(false);
	let userRole = $state('');
	let authError = $state('');
	let view = $state<View>('overview');
	let selectedStudent = $state<{ id: string; username: string } | null>(null);
	let selectedTask = $state<CatalogTaskDTO | null>(null);

	async function restoreSession() {
		if (!getToken()) return;
		try {
			const data = await me();
			if (data.role === 'student') {
				setToken(null);
				authError = 'Access denied: students cannot use the admin panel.';
				return;
			}
			authError = '';
			userRole = data.role;
			loggedIn = true;
		} catch {
			setToken(null);
			loggedIn = false;
		}
	}

	onMount(() => { restoreSession(); });

	function handleLogin(data: AuthResponse) {
		if (data.role === 'student') {
			setToken(null);
			authError = 'Access denied: students cannot use the admin panel.';
			return;
		}
		setToken(data.access_token);
		authError = '';
		userRole = data.role;
		loggedIn = true;
		view = 'overview';
	}

	function handleSelect(studentId: string, username: string) {
		selectedStudent = { id: studentId, username };
	}

	function handleBack() {
		selectedStudent = null;
	}

	function handleSelectTask(task: CatalogTaskDTO) {
		selectedTask = task;
	}

	function handleBackToCatalog() {
		selectedTask = null;
	}

	function navTo(next: View) {
		view = next;
		selectedStudent = null;
		selectedTask = null;
	}

	function logout() {
		setToken(null);
		loggedIn = false;
		userRole = '';
		selectedStudent = null;
		selectedTask = null;
	}
</script>

{#if !loggedIn}
	{#if authError}<p class="auth-error">{authError}</p>{/if}
	<Login onLogin={handleLogin} />
{:else}
	<main>
		<header>
			<h1>Ego Admin</h1>
			<nav aria-label="Primary">
				<button class="nav-btn" class:active={view === 'overview'} onclick={() => navTo('overview')} aria-current={view === 'overview' ? 'page' : undefined}>Overview</button>
				<button class="nav-btn" class:active={view === 'students'} onclick={() => navTo('students')} aria-current={view === 'students' ? 'page' : undefined}>Students</button>
				<button class="nav-btn" class:active={view === 'catalog'} onclick={() => navTo('catalog')} aria-current={view === 'catalog' ? 'page' : undefined}>Catalog</button>
			</nav>
			<div class="header-actions">
				<span class="role-pill" title="Your role">{userRole}</span>
				<button onclick={logout} aria-label="Log out">Logout</button>
			</div>
		</header>

		{#if view === 'overview'}
			<Overview />
		{:else if view === 'students'}
			{#if selectedStudent}
				<StudentDetail studentId={selectedStudent.id} username={selectedStudent.username} onBack={handleBack} />
			{:else}
				<StudentList {userRole} onSelect={handleSelect} />
			{/if}
		{:else if view === 'catalog'}
			{#if selectedTask}
				<TaskStudio
					taskId={selectedTask.id}
					taskLabel={selectedTask.task_id}
					role={userRole}
					onBack={handleBackToCatalog}
				/>
			{:else}
				<Catalog onSelectTask={handleSelectTask} />
			{/if}
		{/if}
	</main>
{/if}

<style>
	:global(html), :global(body) {
		margin: 0; height: 100%;
		font-family: 'JetBrains Mono', 'Cascadia Code', 'Fira Code', 'Consolas', monospace;
		background: #1e1e1e; color: #d4d4d4; font-size: 14px; line-height: 1.5;
	}
	:global(#app) { height: 100%; }

	main { max-width: 960px; margin: 0 auto; padding: 24px; }
	header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; gap: 16px; flex-wrap: wrap; }
	h1 { font-size: 1.2rem; font-weight: 700; }
	nav { display: flex; gap: 4px; flex: 1 1 auto; }
	.nav-btn {
		padding: 6px 14px; background: transparent; border: 1px solid transparent; border-radius: 4px;
		color: #858585; font-family: inherit; font-size: 0.8rem; cursor: pointer;
	}
	.nav-btn:hover { color: #d4d4d4; }
	.nav-btn.active { color: #d4d4d4; border-color: #3c3c3c; background: #2d2d2d; }
	.header-actions { display: flex; align-items: center; gap: 12px; }
	.role-pill { color: #858585; font-size: 0.8rem; text-transform: capitalize; }
	header button:not(.nav-btn) {
		padding: 6px 12px; background: transparent; border: 1px solid #3c3c3c; border-radius: 4px;
		color: #858585; font-family: inherit; font-size: 0.8rem; cursor: pointer;
	}
	header button:not(.nav-btn):hover { border-color: #007acc; color: #d4d4d4; }
	.auth-error { color: #f87171; text-align: center; margin: 16px 0; }

	@media (max-width: 600px) {
		header { flex-direction: column; align-items: stretch; }
		nav { flex-wrap: wrap; }
	}
</style>
