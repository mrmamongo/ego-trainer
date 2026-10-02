<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { login, authProviders, startForgejo, exchangeForgejo, type AuthResponse, type AuthProviders } from '../api';
	import Button from '../lib/components/ui/button/Button.svelte';

	let username = $state('');
	let password = $state('');
	let error = $state('');
	let loading = $state(false);
	let providers = $state<AuthProviders | null>(null);
	let attempt = 0;
	let popup: Window | null = null;
	let channel: BroadcastChannel | null = null;

	let { onLogin }: { onLogin: (data: AuthResponse) => void } = $props();
	onMount(() => { void authProviders().then(value => providers = value).catch(() => error = 'Не удалось получить способы входа. Обнови страницу.'); });
	onDestroy(() => { attempt++; popup?.close(); channel?.close(); });
	function cancel() { attempt++; popup?.close(); channel?.close(); popup = null; loading = false; }
	async function forgejoLogin() {
		const current = ++attempt;
		error = ''; loading = true;
		popup = window.open('about:blank', '_blank');
		if (!popup) { loading = false; error = 'Разреши открытие новой вкладки для входа через Forgejo.'; return; }
		popup.opener = null;
		try {
			const bytes = crypto.getRandomValues(new Uint8Array(32));
			const encode = (data: Uint8Array) => btoa(String.fromCharCode(...data)).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
			const verifier = encode(bytes);
			const digest = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(verifier));
			const flow = await startForgejo(encode(new Uint8Array(digest)));
			if (current !== attempt) return;
			if (new URL(flow.authorization_url).origin !== location.origin) throw new Error('Адрес входа не совпадает с адресом сервиса. Проверь EGO_PUBLIC_URL.');
			let ticket = '';
			let failed = false;
			channel = new BroadcastChannel('ego-forgejo-' + flow.state);
			channel.onmessage = (event: MessageEvent) => {
				if (event.data?.error === 'login_failed') failed = true;
				if (typeof event.data?.ticket === 'string' && /^[A-Za-z0-9_-]{43}$/.test(event.data.ticket)) ticket = event.data.ticket;
			};
			popup!.location.href = flow.authorization_url;
			const deadline = Date.now() + flow.expires_in * 1000;
			while (current === attempt && Date.now() < deadline) {
				await new Promise(resolve => setTimeout(resolve, 1500));
				if (current !== attempt) return;
				if (failed) throw new Error('Вход не завершён или регистрация закрыта. Попробуй снова или обратись к наставнику.');
				if (!ticket) continue;
				const result = await exchangeForgejo(flow.state, verifier, ticket);
				if (current !== attempt) return;
				if (!('pending' in result)) { popup?.close(); popup = null; onLogin(result); return; }
			}
			if (current === attempt) throw new Error('Время входа истекло. Попробуй ещё раз.');
		} catch (e) {
			if (current === attempt) { error = (e as Error).message; popup?.close(); popup = null; }
		} finally { if (current === attempt) { loading = false; channel?.close(); channel = null; } }
	}

	async function submit() {
		if (!username.trim() || !password) {
			error = 'Введи имя пользователя и пароль';
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
	<img class="logo" src="/static/branding/cogito-mark.svg" alt="Cogito" width="48" height="48">
	<h1>Панель управления</h1>
	<p class="sub">Вход для администратора или наставника</p>
	{#if providers?.forgejo}
		<Button class="w-full" disabled={loading} onclick={forgejoLogin}>{loading ? 'Ожидаю вход в Forgejo…' : 'Войти через Forgejo'}</Button>
		{#if loading}<Button class="mt-2 w-full" variant="outline" onclick={cancel}>Отменить вход</Button>{/if}
	{/if}
	{#if providers?.local}
	<form onsubmit={(e) => { e.preventDefault(); submit(); }}>
		<input type="text" bind:value={username} placeholder="Имя пользователя" autocomplete="username" />
		<input type="password" bind:value={password} placeholder="Пароль" autocomplete="current-password" />
		<Button class="w-full" type="submit" disabled={loading}>
			{loading ? 'Вхожу…' : 'Войти'}
		</Button>
	</form>
	{/if}
	{#if providers && !providers.forgejo && !providers.local}<p>Вход пока не настроен. Обратись к администратору.</p>{/if}
	{#if error}<div class="error" role="alert">{error}</div>{/if}
	<Button href="/student" variant="link" class="mt-4 w-full">Учебный кабинет →</Button>
</div>

<style>
	.login { max-width: 320px; margin: 80px auto; }
	.logo { display: block; margin-bottom: 16px; }
	h1 { font-size: 1.2rem; font-weight: 700; margin-bottom: 4px; }
	.sub { color: #858585; font-size: 0.8rem; margin-bottom: 24px; }
	input {
		width: 100%; padding: 8px 12px; margin-bottom: 12px;
		background: #18181b; border: 1px solid #3f3f46; border-radius: 4px;
		color: #fafafa; font-family: inherit; font-size: 14px;
	}
	input:focus { outline: none; border-color: #007acc; }
	.error { color: #f87171; font-size: 0.8rem; margin-top: 8px; }
</style>
