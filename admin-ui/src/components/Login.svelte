<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { login, authProviders, startForgejo, exchangeForgejo, type AuthResponse, type AuthProviders } from '../api';
	import Button from '../lib/components/ui/button/Button.svelte';
	import Card from '../lib/components/ui/card/Card.svelte';
	import Icon from '../lib/Icon.svelte';

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

<div class="login-page">
  <header class="login-topbar"><a href="/" class="login-brand"><img src="/static/branding/cogito-mark.svg" alt="" width="35" height="35"><span>Cogito<small>Учебная платформа</small></span></a></header>
  <div class="login-content">
    <Card class="login-card gap-0 p-7 sm:p-8">
      <div class="login-icon"><Icon name="book" size={24} /></div>
      <h1>Панель управления</h1>
      <p class="sub">Задачи, ученики и обучение — в одном рабочем пространстве.</p>
      {#if !providers && !error}<p class="auth-loading" role="status">Загружаю способы входа…</p>{/if}
      {#if providers?.forgejo}
        <Button class="h-11 w-full" disabled={loading} onclick={forgejoLogin}>{loading ? 'Ожидаю вход в Forgejo…' : 'Войти через Forgejo'}<Icon name="arrow" size={16} /></Button>
        {#if loading}<Button class="mt-3 w-full" variant="outline" onclick={cancel}>Отменить вход</Button>{/if}
      {/if}
      {#if providers?.local}
        {#if providers.forgejo}<div class="login-divider"><span>или по логину</span></div>{/if}
        <form onsubmit={(event) => { event.preventDefault(); void submit(); }}>
          <label class="admin-field">Логин<input type="text" bind:value={username} placeholder="Имя пользователя" autocomplete="username" required disabled={loading} /></label>
          <label class="admin-field">Пароль<input type="password" bind:value={password} placeholder="Твой пароль" autocomplete="current-password" required disabled={loading} /></label>
          <Button class="h-11 w-full" variant={providers.forgejo ? 'outline' : 'default'} type="submit" disabled={loading}>{loading ? 'Вхожу…' : 'Войти'}</Button>
        </form>
      {/if}
      {#if providers && !providers.forgejo && !providers.local}<p class="admin-notice">Вход пока не настроен. Обратись к администратору.</p>{/if}
      {#if error}<div class="admin-notice error login-error" role="alert">{error}</div>{/if}
      <div class="login-footer"><p>Здесь работают наставники и администраторы</p><Button href="/student" variant="link" class="h-auto p-0">Учебный кабинет<Icon name="arrow" size={14} /></Button></div>
    </Card>
  </div>
</div>

<style>
  .login-page { min-height: 100dvh; }
  .login-topbar { height: 72px; padding: 0 max(24px, calc((100vw - 1120px) / 2)); display: flex; align-items: center; border-bottom: 1px solid var(--border); background: var(--card); }
  .login-brand { display: flex; align-items: center; gap: 11px; color: var(--foreground); text-decoration: none; font-size: 17px; font-weight: 650; letter-spacing: -.03em; }
  .login-brand small { display: block; color: var(--muted-foreground); font-size: 11px; font-weight: 400; letter-spacing: 0; }
  .login-content { min-height: calc(100dvh - 72px); display: grid; place-items: center; padding: 40px 20px; }
  .login-content :global(.login-card) { width: min(440px, 100%); }
  .login-icon { display: grid; place-items: center; width: 46px; height: 46px; border: 1px solid var(--border); border-radius: 12px; background: var(--secondary); color: var(--muted-foreground); margin-bottom: 24px; }
  h1 { margin: 0 0 10px; font-size: 26px; line-height: 1.25; font-weight: 600; letter-spacing: -.04em; }
  .sub { color: var(--muted-foreground); font-size: 14px; line-height: 1.65; margin: 0 0 26px; }
  form { display: grid; gap: 18px; }
  .login-divider { display: flex; align-items: center; gap: 14px; margin: 24px 0; color: var(--muted-foreground); font-size: 11px; }
  .login-divider::before, .login-divider::after { content: ''; height: 1px; flex: 1; background: var(--border); }
  .login-footer { margin-top: 26px; padding-top: 22px; border-top: 1px solid var(--border); text-align: center; }
  .login-footer p { margin: 0 0 10px; font-size: 11px; color: var(--muted-foreground); }
  .login-error { margin-top: 20px; }
  .auth-loading { color: var(--muted-foreground); font-size: 13px; }
  @media (max-width: 600px) { .login-topbar { padding: 0 20px; } .login-content { padding: 28px 16px; } h1 { font-size: 24px; } }
</style>
