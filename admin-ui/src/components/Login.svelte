<script lang="ts">
	import { login, type AuthResponse } from '../api';

	let username = $state('');
	let password = $state('');
	let error = $state('');
	let loading = $state(false);

	let { onLogin }: { onLogin: (data: AuthResponse) => void } = $props();

	async function submit() {
		if (!username.trim() || !password) {
			error = 'Enter username and password';
			return;
		}
		error = '';
		loading = true;
		try {
			const data = await login(username.trim(), password);
			onLogin(data);
		} catch (e) {
			error = (e as Error).message;
		} finally {
			loading = false;
		}
	}
</script>

<div class="login">
	<h1>Ego Admin</h1>
	<p class="sub">Sign in with admin/mentor account</p>
	<form onsubmit={(e) => { e.preventDefault(); submit(); }}>
		<input type="text" bind:value={username} placeholder="Username" autocomplete="username" />
		<input type="password" bind:value={password} placeholder="Password" autocomplete="current-password" />
		<button type="submit" disabled={loading}>
			{loading ? 'Signing in…' : 'Sign in'}
		</button>
		{#if error}<div class="error">{error}</div>{/if}
	</form>
</div>

<style>
	.login { max-width: 320px; margin: 80px auto; }
	h1 { font-size: 1.2rem; font-weight: 700; margin-bottom: 4px; }
	.sub { color: #858585; font-size: 0.8rem; margin-bottom: 24px; }
	input {
		width: 100%; padding: 8px 12px; margin-bottom: 12px;
		background: #2d2d2d; border: 1px solid #3c3c3c; border-radius: 4px;
		color: #d4d4d4; font-family: inherit; font-size: 14px;
	}
	input:focus { outline: none; border-color: #007acc; }
	button {
		width: 100%; padding: 8px; background: #007acc; color: #fff;
		border: none; border-radius: 4px; font-family: inherit; font-size: 14px; cursor: pointer;
	}
	button:hover:not(:disabled) { opacity: 0.9; }
	button:disabled { opacity: 0.5; cursor: not-allowed; }
	.error { color: #f87171; font-size: 0.8rem; margin-top: 8px; }
</style>
