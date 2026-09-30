<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import {
		exportDeployment,
		getSettings,
		listModels,
		saveSettings,
		syncContent,
		syncLog,
		testAI,
		type ConsoleConfig,
		type SettingsDraft,
		type SettingsSnapshot,
	} from '../consoleApi';

	let {
		draft = null,
		onDirtyChange,
		onSaved,
		onBusyChange,
	}: {
		draft?: SettingsDraft | null;
		onDirtyChange?: (dirty: boolean) => void;
		onSaved?: (snapshot: SettingsSnapshot) => void;
		onBusyChange?: (busy: boolean) => void;
	} = $props();

	type Tab = 'general' | 'content' | 'ai' | 'deployment';
	let activeTab = $state<Tab>('general');
	let snapshot = $state<SettingsSnapshot | null>(null);
	let config = $state<ConsoleConfig | null>(null);
	let loading = $state(true);
	let loadError = $state('');
	let saving = $state(false);
	let actionError = $state('');
	let apiKey = $state('');
	let clearApiKey = $state(false);
	let revisionConflict = $state(false);
	let pendingProposal = $state<SettingsDraft | null>(null);
	let appliedDraft: SettingsDraft | null = null;
	let models = $state<string[]>([]);
	let modelsLoading = $state(false);
	let modelsError = $state('');
	let aiTest = $state<{ ok: boolean; model: string; latency_ms: number; answer: string } | null>(null);
	let aiTestError = $state('');
	let aiTesting = $state(false);
	let syncBusy = $state(false);
	let syncError = $state('');
	let syncResult = $state<{ added: number; updated: number; skipped: number; errors: number; status: string } | null>(null);
	let logsOpen = $state(false);
	let logsLoading = $state(false);
	let logsError = $state('');
	let logs = $state<Array<{ id: number; status: string; finished_at: string; errors: number; error_details: string }> | null>(null);
	let deploymentLoading = $state(false);
	let deploymentError = $state('');
	let deploymentText = $state('');
	let deploymentReady = $state(false);

	let dirty = $derived(Boolean(snapshot && config && (
		JSON.stringify(config) !== JSON.stringify(snapshot.config) || apiKey.length > 0 || clearApiKey
	)));

	function copyConfig(source: ConsoleConfig): ConsoleConfig {
		return { ...source };
	}

	function setBaseline(data: SettingsSnapshot) {
		snapshot = data;
		config = copyConfig(data.config);
		apiKey = '';
		clearApiKey = false;
		revisionConflict = false;
		actionError = '';
		aiTest = null;
		aiTestError = '';
	}

	async function loadSettings(discardDirty = false) {
		if (dirty && !discardDirty && !window.confirm('Есть несохранённые изменения. Перезагрузить настройки и потерять их?')) return;
		loading = true;
		loadError = '';
		try {
			const data = await getSettings();
			setBaseline(data);
			pendingProposal = null;
			appliedDraft = null;
		} catch (error) {
			loadError = (error as Error).message || 'Не удалось загрузить настройки.';
		} finally {
			loading = false;
		}
	}

	function isRevisionConflict(error: unknown): boolean {
		const e = error as { status?: number; message?: string };
		return e?.status === 409 || /\b409\b|revision|revision conflict|верси.{0,20}(измен|конфликт)|конфликт/i.test(e?.message || '');
	}

	function isLocked(field: string): boolean {
		return Boolean(snapshot?.locked_fields?.[field]);
	}

	function lockMessage(field: string): string {
		const variable = snapshot?.locked_fields?.[field];
		return variable ? `Задано переменной окружения ${variable}; изменить здесь нельзя.` : '';
	}

	function handleIncomingDraft(incoming: SettingsDraft | null | undefined) {
		if (!incoming || incoming === appliedDraft || !snapshot || !config) return;
		if (dirty) {
			pendingProposal = incoming;
			return;
		}
		if (incoming.expected_revision !== snapshot.revision) {
			pendingProposal = incoming;
			return;
		}
		config = copyConfig(incoming.config);
		pendingProposal = null;
		appliedDraft = incoming;
	}

	$effect(() => {
		handleIncomingDraft(draft);
	});

	$effect(() => {
		onDirtyChange?.(dirty);
	});

	function beforeUnload(event: BeforeUnloadEvent) {
		if (!dirty) return;
		event.preventDefault();
		event.returnValue = '';
	}

	onMount(() => {
		void loadSettings(true);
		window.addEventListener('beforeunload', beforeUnload);
		return () => window.removeEventListener('beforeunload', beforeUnload);
	});

	async function save(andTest = false) {
		if (!snapshot || !config || saving) return;
		saving = true;
		actionError = '';
		if (andTest) { aiTest = null; aiTestError = ''; }
		try {
			const saved = await saveSettings({ expected_revision: snapshot.revision, config: copyConfig(config) }, apiKey || undefined, clearApiKey);
			setBaseline(saved);
			pendingProposal = null;
			appliedDraft = null;
			onSaved?.(saved);
			if (andTest) {
				aiTesting = true;
				try {
					aiTest = await testAI();
				} catch (error) {
					aiTestError = (error as Error).message || 'Проверка подключения завершилась ошибкой.';
				} finally {
					aiTesting = false;
				}
			}
		} catch (error) {
			if (isRevisionConflict(error)) {
				revisionConflict = true;
				actionError = 'Настройки на сервере уже изменились. Твои поля сохранены в форме; обнови данные и перенеси изменения вручную.';
			} else {
				actionError = (error as Error).message || 'Не удалось сохранить настройки.';
			}
		} finally {
			saving = false;
		}
	}

	function revert() {
		if (!snapshot || !dirty) return;
		if (!window.confirm('Отменить все несохранённые изменения?')) return;
		config = copyConfig(snapshot.config);
		apiKey = '';
		clearApiKey = false;
		actionError = '';
		revisionConflict = false;
		pendingProposal = null;
	}

	function acceptProposal() {
		if (!pendingProposal || !snapshot || !config) return;
		if (pendingProposal.expected_revision !== snapshot.revision) {
			revisionConflict = true;
			return;
		}
		if (dirty && !window.confirm('Заменить текущие несохранённые поля черновиком помощника?')) return;
		config = copyConfig(pendingProposal.config);
		appliedDraft = pendingProposal;
		pendingProposal = null;
		revisionConflict = false;
	}

	async function loadModels() {
		modelsLoading = true;
		modelsError = '';
		try { models = await listModels(); }
		catch (error) { modelsError = (error as Error).message || 'Не удалось загрузить модели.'; }
		finally { modelsLoading = false; }
	}

	async function showLogs() {
		logsOpen = !logsOpen;
		if (!logsOpen || logs) return;
		logsLoading = true;
		logsError = '';
		try { logs = await syncLog(); }
		catch (error) { logsError = (error as Error).message || 'Не удалось загрузить журнал синхронизации.'; }
		finally { logsLoading = false; }
	}

	async function runSync() {
		if (!snapshot || dirty || syncBusy) return;
		syncBusy = true;
		syncError = '';
		syncResult = null;
		try {
			syncResult = await syncContent(snapshot.config.content_path);
			logs = null;
		} catch (error) { syncError = (error as Error).message || 'Не удалось синхронизировать контент.'; }
		finally { syncBusy = false; }
	}

	function redactSecrets(text: string): string {
		return text.replace(/^([A-Z0-9_]*(?:API[_-]?KEY|TOKEN|SECRET|PASSWORD)[A-Z0-9_]*)\s*=.*$/gim, '$1=');
	}

	async function prepareDeployment() {
		deploymentLoading = true;
		deploymentError = '';
		try {
			deploymentText = redactSecrets(await exportDeployment());
			deploymentReady = true;
		} catch (error) { deploymentError = (error as Error).message || 'Не удалось подготовить файл окружения.'; }
		finally { deploymentLoading = false; }
	}

	function downloadDeployment() {
		const blob = new Blob([deploymentText], { type: 'text/plain;charset=utf-8' });
		const url = URL.createObjectURL(blob);
		const anchor = document.createElement('a');
		anchor.href = url;
		anchor.download = '.env.example';
		anchor.click();
		URL.revokeObjectURL(url);
	}

	function setTemperatureEnabled(event: Event) {
		if (!config) return;
		const enabled = (event.currentTarget as HTMLInputElement).checked;
		config.ai_temperature = enabled ? 0.7 : null;
	}
  $effect(() => { onBusyChange?.(saving || syncBusy || aiTesting); });
  onDestroy(() => { onBusyChange?.(false); });
</script>

<section class="settings-page" aria-labelledby="settings-title">
	<div class="page-heading">
		<div>
			<h2 id="settings-title">Настройки сервиса</h2>
			<p class="muted">Общие параметры, контент, AI и конфигурация развёртывания.</p>
		</div>
		{#if snapshot}<span class="revision">Версия настроек · {snapshot.revision}</span>{/if}
	</div>

	{#if loading && !snapshot}
		<div class="state-card" role="status">Загружаю настройки сервиса…</div>
	{:else if loadError && !snapshot}
		<div class="state-card error" role="alert">
			<p>{loadError}</p>
			<button type="button" onclick={() => void loadSettings(true)}>Повторить загрузку</button>
		</div>
	{:else if snapshot && config}
        <fieldset class="settings-fields" disabled={saving || syncBusy || aiTesting}>
		{#if pendingProposal}
			<div class="notice conflict" role="alert">
				<div>
					<strong>Черновик помощника требует сверки</strong>
					<p>
						{#if pendingProposal.expected_revision !== snapshot.revision}
							Он создан для версии {pendingProposal.expected_revision}, а загружена версия {snapshot.revision}.
						{:else}
							В форме уже есть несохранённые изменения.
						{/if}
						Предложение сохранено отдельно; текущие поля формы не изменены.
					</p>
					{#if pendingProposal.changes}
						<details><summary>Посмотреть предложенные изменения</summary><pre>{JSON.stringify(pendingProposal.changes, null, 2)}</pre></details>
					{:else}
						<details><summary>Посмотреть конфигурацию черновика</summary><pre>{JSON.stringify(pendingProposal.config, null, 2)}</pre></details>
					{/if}
				</div>
				<div class="actions">
					<button type="button" onclick={acceptProposal} disabled={pendingProposal.expected_revision !== snapshot.revision}>Применить черновик</button>
					<button type="button" onclick={() => { pendingProposal = null; }}>Отклонить</button>
				</div>
			</div>
		{/if}

		{#if revisionConflict}
			<div class="notice conflict" role="alert">
				<div><strong>Конфликт сохранения</strong><p>{actionError || 'Сервер сообщил, что revision изменился. Локальные поля сохранены.'}</p></div>
				<button type="button" onclick={() => void loadSettings()}>Загрузить актуальные настройки</button>
			</div>
		{:else if actionError}
			<div class="notice error" role="alert">{actionError}</div>
		{/if}

		{#if dirty}
			<div class="dirty-bar">
				<span>Есть несохранённые изменения</span>
				<div class="actions">
					<button type="button" onclick={revert}>Отменить</button>
					<button type="button" onclick={() => void loadSettings()} disabled={loading}>Перезагрузить</button>
					<button class="primary" type="button" onclick={() => void save()} disabled={saving}>{saving ? 'Сохраняю…' : 'Сохранить'}</button>
				</div>
			</div>
		{/if}

		<nav class="tabs" aria-label="Категории настроек">
			<button class:active={activeTab === 'general'} type="button" onclick={() => activeTab = 'general'}>Общие</button>
			<button class:active={activeTab === 'content'} type="button" onclick={() => activeTab = 'content'}>Контент</button>
			<button class:active={activeTab === 'ai'} type="button" onclick={() => activeTab = 'ai'}>AI</button>
			<button class:active={activeTab === 'deployment'} type="button" onclick={() => activeTab = 'deployment'}>Развёртывание</button>
		</nav>

		{#if activeTab === 'general'}
			<div class="panel">
				<div class="section-title"><h3>Общие параметры</h3><p>Настройки регистрации и ограничения выполнения задач.</p></div>
				<label class="field">
					<span>Название сервиса</span><input bind:value={config.service_name} disabled={isLocked('service_name')} />
					{#if isLocked('service_name')}<small>{lockMessage('service_name')}</small>{/if}
				</label>
				<label class="toggle"><input type="checkbox" bind:checked={config.registration_enabled} disabled={isLocked('registration_enabled')} /><span><strong>Открытая регистрация</strong><small>Разрешить новым пользователям создавать аккаунт самостоятельно.</small></span></label>
				{#if isLocked('registration_enabled')}<p class="lock-note">{lockMessage('registration_enabled')}</p>{/if}
				<div class="form-grid">
					<label class="field"><span>Длительность сессии, минут</span><input type="number" min="15" max="43200" bind:value={config.session_minutes} disabled={isLocked('session_minutes')} />{#if isLocked('session_minutes')}<small>{lockMessage('session_minutes')}</small>{/if}</label>
					<label class="field"><span>Тайм-аут проверки, секунд</span><input type="number" min="1" max="30" step="0.5" bind:value={config.check_timeout_seconds} disabled={isLocked('check_timeout_seconds')} />{#if isLocked('check_timeout_seconds')}<small>{lockMessage('check_timeout_seconds')}</small>{/if}</label>
					<label class="field"><span>Максимальный размер кода, символов</span><input type="number" min="1000" max="500000" bind:value={config.max_code_chars} disabled={isLocked('max_code_chars')} />{#if isLocked('max_code_chars')}<small>{lockMessage('max_code_chars')}</small>{/if}</label>
				</div>
			</div>
		{:else if activeTab === 'content'}
			<div class="panel">
				<div class="section-title"><h3>Контент задач</h3><p>Путь к репозиторию и ручная синхронизация его содержимого.</p></div>
			<label class="field">
				<span>Путь к контенту</span><input bind:value={config.content_path} disabled={isLocked('content_path')} />
				{#if isLocked('content_path')}<small>{lockMessage('content_path')}</small>{:else}<small>Изменение пути вступит в силу после сохранения.</small>{/if}
			</label>
			<div class="subsection">
				<div><h4>Синхронизация</h4><p class="muted">Запускается по сохранённому пути и недоступна, пока форма изменена.</p></div>
				<div class="actions">
					<button type="button" onclick={() => void runSync()} disabled={dirty || syncBusy || !snapshot.config.content_path}>{syncBusy ? 'Синхронизирую…' : 'Синхронизировать сейчас'}</button>
					<button type="button" onclick={() => void showLogs()}>{logsOpen ? 'Скрыть журнал' : 'Журнал синхронизации'}</button>
				</div>
			</div>
			{#if dirty}<p class="muted">Сначала сохрани изменения, чтобы синхронизация использовала новый путь.</p>{/if}
			{#if syncError}<p class="inline-error" role="alert">{syncError}</p>{/if}
			{#if syncResult}<div class="result-card" role="status"><strong>Синхронизация завершена</strong><span>Добавлено: {syncResult.added} · обновлено: {syncResult.updated} · пропущено: {syncResult.skipped} · ошибок: {syncResult.errors}</span></div>{/if}
			{#if logsOpen}
				<div class="log-box">
					{#if logsLoading}<p class="muted">Загружаю журнал…</p>
					{:else if logsError}<p class="inline-error" role="alert">{logsError}</p>
					{:else if logs && logs.length === 0}<p class="muted">Записей синхронизации пока нет.</p>
					{:else if logs}<ul>{#each logs as item (item.id)}<li><strong>{item.status}</strong><span>{item.finished_at || 'Время не указано'}</span><span>Ошибок: {item.errors}</span>{#if item.error_details}<small>{item.error_details}</small>{/if}</li>{/each}</ul>{/if}
				</div>
			{/if}
			</div>
		{:else if activeTab === 'ai'}
			<div class="panel">
				<div class="section-title"><h3>Подключение AI</h3><p>Настрой совместимый API. Ключ хранится отдельно и никогда не возвращается сервером.</p></div>
				<label class="toggle"><input type="checkbox" bind:checked={config.ai_enabled} disabled={isLocked('ai_enabled')} /><span><strong>Включить AI-помощника</strong><small>При отключении запросы к AI не выполняются.</small></span></label>
				{#if isLocked('ai_enabled')}<p class="lock-note">{lockMessage('ai_enabled')}</p>{/if}
				<div class="form-grid">
					<label class="field"><span>Совместимый API base URL</span><input type="url" bind:value={config.ai_base_url} placeholder="https://api.example.com/v1" disabled={isLocked('ai_base_url')} />{#if isLocked('ai_base_url')}<small>{lockMessage('ai_base_url')}</small>{/if}</label>
					<label class="field"><span>Модель</span><div class="input-action"><input list="ai-model-options" bind:value={config.ai_model} placeholder="Например, gpt-4.1-mini" disabled={isLocked('ai_model')} /><datalist id="ai-model-options">{#each models as model}<option value={model}></option>{/each}</datalist><button type="button" onclick={() => void loadModels()} disabled={modelsLoading}>{modelsLoading ? 'Загрузка…' : 'Загрузить модели'}</button></div>{#if isLocked('ai_model')}<small>{lockMessage('ai_model')}</small>{/if}{#if modelsError}<small class="inline-error">{modelsError}</small>{/if}</label>
					<label class="field"><span>Тайм-аут AI, секунд</span><input type="number" min="5" max="180" bind:value={config.ai_timeout_seconds} disabled={isLocked('ai_timeout_seconds')} />{#if isLocked('ai_timeout_seconds')}<small>{lockMessage('ai_timeout_seconds')}</small>{/if}</label>
					<label class="field"><span>Лимит токенов ответа</span><input type="number" min="256" max="16384" bind:value={config.ai_max_tokens} disabled={isLocked('ai_max_tokens')} />{#if isLocked('ai_max_tokens')}<small>{lockMessage('ai_max_tokens')}</small>{/if}</label>
				</div>
				<label class="field"><span>Имя параметра лимита токенов</span><select bind:value={config.ai_token_limit_parameter} disabled={isLocked('ai_token_limit_parameter')}><option value="max_tokens">max_tokens</option><option value="max_completion_tokens">max_completion_tokens</option></select><small>Выбери формат, который принимает API-провайдер.</small></label>
				{#if isLocked('ai_token_limit_parameter')}<p class="lock-note">{lockMessage('ai_token_limit_parameter')}</p>{/if}
				<label class="toggle"><input type="checkbox" checked={config.ai_temperature !== null} onchange={setTemperatureEnabled} disabled={isLocked('ai_temperature')} /><span><strong>Задать temperature вручную</strong><small>Если выключено, используется значение провайдера по умолчанию.</small></span></label>
				{#if config.ai_temperature !== null}<label class="field compact"><span>Temperature</span><input type="number" min="0" max="2" step="0.1" bind:value={config.ai_temperature} disabled={isLocked('ai_temperature')} /></label>{/if}
				{#if isLocked('ai_temperature')}<p class="lock-note">{lockMessage('ai_temperature')}</p>{/if}
				<label class="toggle"><input type="checkbox" bind:checked={config.ai_tools_enabled} disabled={isLocked('ai_tools_enabled')} /><span><strong>Разрешить инструменты</strong><small>Передавать поддерживаемые tools/function calls AI-провайдеру.</small></span></label>
				{#if isLocked('ai_tools_enabled')}<p class="lock-note">{lockMessage('ai_tools_enabled')}</p>{/if}
				<label class="field"><span>Системная инструкция</span><textarea rows="7" bind:value={config.ai_system_prompt} disabled={isLocked('ai_system_prompt')}></textarea>{#if isLocked('ai_system_prompt')}<small>{lockMessage('ai_system_prompt')}</small>{/if}</label>
				<div class="key-panel">
					<div><strong>API-ключ</strong><p class="muted">{snapshot.api_key_configured ? 'Ключ настроен. Поле пустое — оставить текущий ключ.' : 'Ключ ещё не задан.'} Введённое значение сервер не покажет повторно.</p></div>
					<label class="field"><span>{snapshot.api_key_configured ? 'Новый ключ (необязательно)' : 'Ключ'}</span><input type="password" autocomplete="new-password" bind:value={apiKey} placeholder={snapshot.api_key_configured ? 'Оставь пустым, чтобы сохранить текущий' : 'Введи API-ключ'} disabled={isLocked('api_key')} /></label>
					{#if isLocked('api_key')}<p class="lock-note">{lockMessage('api_key')}</p>{/if}
					{#if snapshot.api_key_error}<p class="inline-error">Ошибка ключа: {snapshot.api_key_error}</p>{/if}
					{#if snapshot.api_key_configured}<label class="toggle danger-toggle"><input type="checkbox" bind:checked={clearApiKey} disabled={isLocked('api_key')} /><span><strong>Удалить сохранённый ключ</strong><small>Будет применено при сохранении; пустое поле само по себе ключ не очищает.</small></span></label>{/if}
				</div>
				<div class="actions footer-actions">
					<button class="primary" type="button" onclick={() => void save(true)} disabled={saving || aiTesting}>{saving ? 'Сохраняю…' : aiTesting ? 'Проверяю…' : 'Сохранить и проверить AI'}</button>
					{#if aiTest}<span class:success={aiTest.ok} class:failure={!aiTest.ok} class="test-status">{aiTest.ok ? 'Подключение успешно' : 'Провайдер вернул ошибку'} · {aiTest.latency_ms} мс · {aiTest.model}</span>{/if}
					{#if aiTestError}<span class="inline-error" role="alert">{aiTestError}</span>{/if}
				</div>
			</div>
		{:else}
			<div class="panel">
				<div class="section-title"><h3>Развёртывание</h3><p>Параметры работающего процесса доступны только для чтения.</p></div>
			<div class="notice info"><div><strong>Применение через окружение и перезапуск</strong><p>Изменения runtime-параметров задаются переменными окружения и вступают в силу после перезапуска сервиса.</p></div></div>
			<div class="runtime-grid">
				{#each Object.entries({ Версия: snapshot.runtime.version, Окружение: snapshot.runtime.environment, 'Путь к БД': snapshot.runtime.db_path, 'Адрес привязки': snapshot.runtime.bind_host, Порт: snapshot.runtime.bind_port, Воркеры: snapshot.runtime.workers, 'JWT secret задан': snapshot.runtime.jwt_secret_configured ? 'Да' : 'Нет', 'Allowed hosts': snapshot.runtime.allowed_hosts.join(', ') || '—', 'CORS origins': snapshot.runtime.cors_origins.join(', ') || '—' }) as [label, value]}
					<div><small>{label}</small><strong>{value}</strong></div>
				{/each}
			</div>
			<div class="subsection deployment-export">
				<div><h4>Файл окружения</h4><p class="muted">Генерируется без секретов. Перед скачиванием можно отредактировать.</p></div>
				<div class="actions"><button type="button" onclick={() => void prepareDeployment()} disabled={deploymentLoading}>{deploymentLoading ? 'Готовлю…' : 'Подготовить .env.example'}</button>{#if deploymentReady}<button class="primary" type="button" onclick={downloadDeployment}>Скачать .env.example</button>{/if}</div>
			</div>
			{#if deploymentError}<p class="inline-error" role="alert">{deploymentError}</p>{/if}
			{#if deploymentReady}<label class="field"><span>Текст файла .env.example</span><textarea class="code" rows="14" bind:value={deploymentText} spellcheck="false"></textarea></label>{/if}
			</div>
		{/if}
        </fieldset>
	{:else}
		<div class="state-card">Настройки ещё не загружены.</div>
	{/if}
</section>

<style>
    .settings-fields { border: 0; margin: 0; padding: 0; min-width: 0; display: grid; gap: 16px; }
	.settings-page { display: grid; gap: 16px; min-width: 0; }
	.page-heading { display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; }
	h2, h3, h4, p { margin: 0; }
	h2 { font-size: 1.1rem; }
	h3 { font-size: 0.95rem; }
	h4 { font-size: 0.82rem; }
	.muted, .section-title p { color: #858585; font-size: 0.76rem; }
	.page-heading .muted { margin-top: 4px; }
	.revision { color: #858585; font-size: 0.72rem; white-space: nowrap; }
	.tabs { display: flex; gap: 4px; border-bottom: 1px solid #3c3c3c; overflow-x: auto; }
	.tabs button { padding: 8px 12px; background: transparent; color: #858585; border: 0; border-bottom: 2px solid transparent; white-space: nowrap; }
	.tabs button.active { color: #d4d4d4; border-bottom-color: #007acc; }
	.panel { display: grid; gap: 16px; min-width: 0; }
	.section-title { display: grid; gap: 3px; padding-bottom: 4px; }
	.form-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; }
	.field { display: grid; gap: 5px; min-width: 0; }
	.field > span { font-size: 0.77rem; font-weight: 600; }
	.field small, .toggle small { color: #858585; font-size: 0.7rem; line-height: 1.4; }
	.field input, .field select, .field textarea { width: 100%; box-sizing: border-box; min-width: 0; }
	.field textarea { resize: vertical; }
	.field input:disabled, .field select:disabled, .field textarea:disabled { opacity: 0.62; cursor: not-allowed; }
	.compact { max-width: 260px; }
	.toggle { display: flex; align-items: flex-start; gap: 9px; }
	.toggle input { margin-top: 3px; }
	.toggle > span { display: grid; gap: 2px; }
	.lock-note { color: #d0a85c; font-size: 0.7rem; margin-top: -10px; }
	.notice, .dirty-bar, .result-card, .state-card { padding: 12px 14px; border: 1px solid #3c3c3c; border-radius: 6px; background: #252526; }
	.notice { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; }
	.notice p { margin-top: 3px; color: #a0a0a0; font-size: 0.75rem; }
	.notice.conflict { border-color: #9a6b2f; }
	.notice.info { border-color: #36556a; }
	.notice.error, .state-card.error { color: #f87171; border-color: #704040; }
	.notice details { margin-top: 8px; }
	.notice summary { font-size: 0.72rem; cursor: pointer; }
	.notice pre { max-height: 240px; overflow: auto; white-space: pre-wrap; font-size: 0.7rem; color: #c6c6c6; }
	.actions { display: flex; align-items: center; flex-wrap: wrap; gap: 8px; }
	.dirty-bar { display: flex; align-items: center; justify-content: space-between; gap: 10px; border-color: #886828; }
	.dirty-bar > span { font-size: 0.78rem; color: #e4c477; }
	.primary { border-color: #007acc !important; color: #fff !important; background: #0e639c !important; }
	.subsection { display: flex; justify-content: space-between; align-items: center; gap: 14px; padding-top: 12px; border-top: 1px solid #333; }
	.subsection > div:first-child { display: grid; gap: 3px; }
	.result-card { display: flex; flex-wrap: wrap; gap: 8px 16px; font-size: 0.76rem; }
	.result-card span { color: #a0a0a0; }
	.log-box { border: 1px solid #333; border-radius: 5px; padding: 10px; }
	.log-box ul { list-style: none; padding: 0; margin: 0; display: grid; gap: 8px; }
	.log-box li { display: grid; grid-template-columns: auto 1fr auto; gap: 8px; align-items: baseline; font-size: 0.72rem; }
	.log-box li span { color: #858585; }
	.log-box li small { grid-column: 1 / -1; color: #f87171; }
	.input-action { display: flex; gap: 6px; }
	.input-action input { flex: 1; }
	.key-panel { display: grid; gap: 10px; padding: 14px; border: 1px solid #3c3c3c; border-radius: 5px; }
	.key-panel > div:first-child { display: grid; gap: 3px; }
	.danger-toggle strong { color: #f0a0a0; }
	.footer-actions { border-top: 1px solid #333; padding-top: 14px; }
	.test-status { font-size: 0.75rem; }
	.success { color: #75c687; }
	.failure, .inline-error { color: #f87171; }
	.runtime-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 8px; }
	.runtime-grid > div { min-width: 0; padding: 9px 10px; display: grid; gap: 4px; border: 1px solid #333; border-radius: 4px; }
	.runtime-grid small { color: #858585; font-size: 0.68rem; }
	.runtime-grid strong { overflow-wrap: anywhere; font-size: 0.75rem; font-weight: 500; }
	.deployment-export { margin-top: 4px; }
	.field textarea.code { font-family: 'JetBrains Mono', 'Cascadia Code', 'Fira Code', 'Consolas', monospace; font-size: 0.75rem; }
	.state-card { color: #a0a0a0; text-align: center; }
	.state-card p { margin-bottom: 10px; }

	@media (max-width: 700px) {
		.form-grid, .runtime-grid { grid-template-columns: 1fr; }
		.page-heading, .dirty-bar, .subsection, .notice { align-items: stretch; flex-direction: column; }
		.revision { white-space: normal; }
		.log-box li { grid-template-columns: 1fr; }
	}
</style>
