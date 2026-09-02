<script lang="ts">
	import { onMount } from 'svelte';
	import { getToken, setToken, me, type AuthResponse } from './api';
	import Login from './components/Login.svelte';
	import StudentList from './components/StudentList.svelte';
	import StudentDetail from './components/StudentDetail.svelte';

	let loggedIn = $state(false);
	let userRole = $state('');
	let authError = $state('');
	let selectedStudent = $state<{ id: string; username: string } | null>(null);

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
	}

	function handleSelect(studentId: string, username: string) {
		selectedStudent = { id: studentId, username };
	}

	function handleBack() {
		selectedStudent = null;
	}
</script>

{#if !loggedIn}
	{#if authError}<p class="auth-error">{authError}</p>{/if}
	<Login onLogin={handleLogin} />
{:else}
	<main>
		<header>
			<h1>Ego Admin</h1>
			<div class="header-actions">
				<span class="role-pill">{userRole}</span>
				<button onclick={() => { setToken(null); loggedIn = false; userRole = ''; }}>Logout</button>
			</div>
		</header>

		{#if selectedStudent}
			<StudentDetail studentId={selectedStudent.id} username={selectedStudent.username} onBack={handleBack} />
		{:else}
			<StudentList {userRole} onSelect={handleSelect} />
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
	header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
	h1 { font-size: 1.2rem; font-weight: 700; }
	.header-actions { display: flex; align-items: center; gap: 12px; }
	.role-pill { color: #858585; font-size: 0.8rem; text-transform: capitalize; }
	header button {
		padding: 6px 12px; background: transparent; border: 1px solid #3c3c3c; border-radius: 4px;
		color: #858585; font-family: inherit; font-size: 0.8rem; cursor: pointer;
	}
	header button:hover { border-color: #007acc; color: #d4d4d4; }
	.auth-error { color: #f87171; text-align: center; margin: 16px 0; }
</style>
