<script lang="ts">
	import { dashboardData } from './shared/store';
	import { postToHost } from './shared/api';
	import type { DashboardRow, TaskState, TaskStatusFilter } from './shared/types';

	let projectKey = $state<string>('all');
	let blockFilter = $state('all');
	let statusFilter = $state<TaskStatusFilter>('all');
	let search = $state('');

	// Labels in the webview are local: the bundle must not import node-side code.
	// Labels (Russian, incl. server-side status names) come pre-rendered from
	// the host via the `cabinet` payload, so this bundle stays ASCII.
	const STATE_LABELS: Record<TaskState, string> = {
		passed: 'Решена',
		defense: 'Ждёт защиты понимания',
		started: 'В работе',
		failed: 'Есть ошибки',
		new: 'Не начата'
	};

	function normalizeStatus(status: string | undefined | null): string {
		return (status ?? '').trim().toLowerCase();
	}

	function isNewStatus(status: string): boolean {
		return status === '' || status === 'new';
	}

	function isFailedStatus(status: string): boolean {
		return status === 'failed' || status === 'error' || status === 'timeout';
	}

	/** Row state: computed by the host, or derived from the raw status (offline cache). */
	function stateOf(row: DashboardRow): TaskState {
		if (row.state) return row.state;
		const s = normalizeStatus(row.status);
		if (s === 'passed') return 'passed';
		if (isFailedStatus(s)) return 'failed';
		if (isNewStatus(s)) return 'new';
		return 'started';
	}

	function labelFor(row: DashboardRow): string {
		return STATE_LABELS[stateOf(row)];
	}

	function statusIcon(state: TaskState): string {
		if (state === 'passed') return '✓';
		if (state === 'defense') return '?';
		if (state === 'started') return '↻';
		if (state === 'failed') return '✗';
		return '○';
	}

	function matchesStatus(row: DashboardRow, filter: TaskStatusFilter): boolean {
		if (filter === 'all') return true;
		const state = stateOf(row);
		if (filter === 'new') return state === 'new';
		if (filter === 'failed') return state === 'failed';
		return state === filter;
	}

	function matchesSearch(row: DashboardRow, query: string): boolean {
		if (!query) return true;
		const haystack = `${row.id} ${row.title} ${row.block} ${row.project_name ?? ''} ${row.folder_name ?? ''}`.toLocaleLowerCase('ru');
		return haystack.includes(query);
	}

	function formatLastRun(value: string | null): string {
		if (!value) return '—';
		const date = new Date(value);
		if (Number.isNaN(date.getTime())) return '—';
		return date.toLocaleString('ru-RU', {
			dateStyle: 'short',
			timeStyle: 'short'
		});
	}

	function formatDate(value: string | null): string {
		if (!value) return '—';
		const date = new Date(value);
		if (Number.isNaN(date.getTime())) return '—';
		return date.toLocaleString('ru-RU', { dateStyle: 'medium', timeStyle: 'short' });
	}

	function plural(n: number, one: string, few: string, many: string): string {
		const mod100 = n % 100;
		if (mod100 >= 11 && mod100 <= 14) return many;
		const mod10 = n % 10;
		return mod10 === 1 ? one : mod10 >= 2 && mod10 <= 4 ? few : many;
	}

	function openTask(taskId: string) {
		postToHost({ type: 'dashboard.open', taskId });
	}

	function checkTask(taskId: string) {
		postToHost({ type: 'dashboard.check', taskId });
	}

	function hintsTask(taskId: string) {
		postToHost({ type: 'dashboard.hints', taskId });
	}

	function defendTask(taskId: string) {
		postToHost({ type: 'dashboard.defend', taskId });
	}

	function continueNext() {
		postToHost({ type: 'dashboard.next' });
	}

	function openAssistant() {
		postToHost({ type: 'dashboard.ai' });
	}

	function refresh() {
		postToHost({ type: 'dashboard.refresh' });
	}

	function pullAll() {
		postToHost({ type: 'dashboard.pullAll' });
	}

	function pushProgress() {
		postToHost({ type: 'dashboard.push' });
	}

	const rows = $derived.by(() => $dashboardData?.rows ?? []);
	const cabinet = $derived($dashboardData?.cabinet);
	const rowById = $derived(new Map(rows.map((row) => [row.id, row])));

	// Counters follow the per-task state (passed counts only confirmed solutions).
	const counts = $derived.by(() => {
		let passed = 0;
		let open = 0;
		let defense = 0;
		let failed = 0;
		for (const row of rows) {
			const state = stateOf(row);
			if (state === 'passed') passed++;
			else open++;
			if (state === 'defense') defense++;
			if (state === 'failed') failed++;
		}
		return { passed, open, defense, failed, total: rows.length };
	});

	const progressPct = $derived(counts.total > 0 ? Math.round((counts.passed / counts.total) * 100) : 0);

	// Project tabs: derived from rows so they match the server grouping even
	// when the cabinet payload is missing (cached data).
	const projectTabs = $derived.by(() => {
		const names = new Map<string, string>();
		for (const row of rows) {
			const key = row.project_id || `block:${row.block}`;
			if (!names.has(key)) names.set(key, row.project_name || `Блок ${row.block}`);
		}
		return [...names.entries()];
	});

	const nextRow = $derived.by(() => {
		const id = cabinet?.next_task_id;
		if (!id) return null;
		return rowById.get(id) ?? null;
	});

	const filteredRows = $derived.by(() => {
		const query = search.trim().toLocaleLowerCase('ru');
		return rows.filter((row) => {
			const key = row.project_id || `block:${row.block}`;
			const projectOk = projectKey === 'all' || key === projectKey;
			const blockOk = blockFilter === 'all' || row.block === blockFilter;
			return (
				projectOk &&
				blockOk &&
				matchesSearch(row, query) &&
				matchesStatus(row, statusFilter)
			);
		});
	});

	const shownProjects = $derived.by(() => {
		const projects = cabinet?.projects;
		if (!projects) return [];
		return projectKey === 'all' ? projects : projects.filter((p) => p.key === projectKey);
	});

	const understandingOpen = $derived(
		(cabinet?.understanding ?? []).filter((entry) => normalizeStatus(entry.status) !== 'confirmed')
	);

	const understandingAll = $derived(cabinet?.understanding ?? []);

	const recentAttempts = $derived(
		rows
			.filter((row) => !isNewStatus(normalizeStatus(row.status)))
			.sort((a, b) => (b.last_run_at || '').localeCompare(a.last_run_at || ''))
			.slice(0, 10)
	);

	const ai = $derived(cabinet?.ai ?? null);

	// Soft recommendations: a small card per project; nothing renders when the
	// server has no /projects (old server) or no recommendation is declared.
	const recommendationCards = $derived(cabinet?.recommendation_cards ?? []);
	const breakdownCard = $derived(cabinet?.breakdown ?? null);
</script>

<main class="dashboard">
	{#if $dashboardData === null}
		<div class="loading" aria-live="polite">Загружаю личный кабинет…</div>
	{:else}
		{@const data = $dashboardData}
		{@const offline = data.mode === 'offline'}

		<header class="header">
			<div class="brand-row">
				<h1 class="brand">Личный кабинет</h1>
				<span class="mode" class:offline data-mode={data.mode}>
					{data.mode === 'server' ? 'Сервер' : 'Локально'}
				</span>
			</div>
			<p class="subheading">Задачи, попытки, защита понимания и ассистент — всё в одном месте.</p>
		</header>

		{#if data.error}
			<p class="error" role="alert">{data.error}</p>
		{/if}

		{#if counts.total > 0}
			<section class="summary" aria-label="Сводка прогресса">
				<div class="metric-row">
					<div class="metric">
						<span class="metric-value">{counts.total}</span>
						<span class="metric-label">{plural(counts.total, 'задача', 'задачи', 'задач')} всего</span>
					</div>
					<div class="metric passed">
						<span class="metric-value">{counts.passed}</span>
						<span class="metric-label">решено</span>
					</div>
					<div class="metric">
						<span class="metric-value">{counts.open}</span>
						<span class="metric-label">в работе и новых</span>
					</div>
					{#if counts.defense > 0}
						<div class="metric defense">
							<span class="metric-value">{counts.defense}</span>
							<span class="metric-label">ждут защиты</span>
						</div>
					{/if}
				</div>
				<div class="progress" aria-label="Решено {progressPct}%">
					<div class="progress-track" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow={progressPct}>
						<div class="progress-fill" style:width="{progressPct}%"></div>
					</div>
					<span class="progress-label">{progressPct}%</span>
				</div>
			</section>

			<section class="continue" aria-label="Продолжить">
				{#if nextRow}
					<div class="continue-text">
						<span class="continue-eyebrow">Продолжить</span>
						<strong class="continue-title">{nextRow.id} · {nextRow.title}</strong>
						<span class="continue-meta">
							{nextRow.project_name || `Блок ${nextRow.block}`}
							{#if nextRow.folder_name} · {nextRow.folder_name}{/if}
							· {labelFor(nextRow)}
						</span>
					</div>
					<button type="button" class="btn primary" onclick={continueNext}>Открыть задачу →</button>
				{:else}
					<div class="continue-text">
						<span class="continue-eyebrow">Продолжить</span>
						<strong class="continue-title">Все задачи пройдены</strong>
						<span class="continue-meta">Отличная работа — загляни в раздел защиты понимания.</span>
					</div>
				{/if}
			</section>
		{/if}

		{#if recommendationCards.length > 0 || breakdownCard}
			<section class="recommendations" aria-label="Рекомендации по курсам">
				<div class="section-heading">
					<h2>Рекомендации по курсам</h2>
					<span class="section-count">это совет, а не ограничение</span>
				</div>
				<div class="recommendation-grid">
					{#each recommendationCards as card (card.id)}
						<article class="recommendation-card" class:unmet={card.unmet} data-project={card.id}>
							<div class="recommendation-head">
								<strong class="recommendation-name">{card.name}</strong>
								<span class="mono muted">{card.progress_label}</span>
							</div>
							{#if card.unmet && card.readiness_label}
								<span class="recommendation-readiness">{card.readiness_label}</span>
								{#if card.per_kind_label}
									<span class="recommendation-kinds">{card.per_kind_label}</span>
								{/if}
								{#if card.note}
									<span class="recommendation-note">{card.note}</span>
								{/if}
							{:else}
								<span class="recommendation-done">можно начинать — рекомендации выполнены или не заданы</span>
							{/if}
						</article>
					{/each}
					{#if breakdownCard}
						<article class="recommendation-card breakdown" data-project={breakdownCard.project_id}>
							<div class="recommendation-head">
								<strong class="recommendation-name">Разбивка «{breakdownCard.project_name}»</strong>
								<span class="mono muted">по видам задач</span>
							</div>
							<ul class="breakdown-list">
								{#each breakdownCard.rows as row (row.key)}
									{#if row.total > 0}
										<li class="breakdown-row">
											<span class="breakdown-label">{row.label}</span>
											<span class="bar small" aria-label="{row.label}: {row.passed} из {row.total}">
												<span class="bar-fill" style:width="{row.percent}%"></span>
											</span>
											<span class="folder-count mono">{row.passed}/{row.total}</span>
										</li>
									{/if}
								{/each}
							</ul>
						</article>
					{/if}
				</div>
			</section>
		{/if}

		{#if ai}
			<section class="ai" aria-label="Учебный ассистент">
				<div class="ai-text">
					<strong>Учебный ассистент</strong>
					<span class="ai-status" class:available={ai.available}>
						{ai.available ? 'Доступен' : 'Недоступен'}
						{#if cabinet?.ai_reason_label} · {cabinet.ai_reason_label}{/if}
					</span>
					<span class="ai-meta">
						Баланс ${ai.balance_usd} · потрачено ${ai.spent_usd}
						{#if ai.defense_required}· защита понимания обязательна{/if}
					</span>
				</div>
				<button type="button" class="btn" onclick={openAssistant}>Открыть ассистента</button>
			</section>
		{/if}

		{#if cabinet?.understanding !== null && cabinet !== undefined}
			<section class="understanding" aria-label="Защита понимания">
				<div class="section-heading">
					<h2>Защита понимания</h2>
					{#if understandingAll.length > 0}
						<span class="section-count">{understandingOpen.length} {plural(understandingOpen.length, 'решение', 'решения', 'решений')} без подтверждения</span>
					{/if}
				</div>
				{#if understandingAll.length === 0}
					<p class="empty-note">
						Пока проверенных решений нет. Пройди тесты задачи — после этого станет доступна защита понимания.
					</p>
				{:else}
					<ul class="understanding-list">
						{#each understandingAll as entry (entry.task_id + entry.status + entry.at)}
							{@const confirmed = normalizeStatus(entry.status) === 'confirmed'}
							{@const canOpen = rowById.has(entry.task_id)}
							<li class="understanding-row">
								<span class="state-dot" data-status={entry.status} aria-hidden="true">{confirmed ? '✓' : '?'}</span>
								<span class="understanding-main">
									<button
										type="button"
										class="link"
										disabled={!canOpen}
										title={canOpen ? 'Открыть задачу' : 'Задачи больше нет в каталоге'}
										onclick={() => openTask(entry.task_id)}
									>
										{entry.task_id} · {entry.task_title}
									</button>
									<span class="understanding-label">{entry.status_label}</span>
								</span>
								<span class="muted">{formatDate(entry.at)}</span>
								{#if !confirmed && canOpen}
									<button type="button" class="btn" onclick={() => defendTask(entry.task_id)}>Пройти защиту</button>
								{/if}
							</li>
						{/each}
					</ul>
				{/if}
			</section>
		{/if}

		{#if shownProjects.length > 0}
			<section class="projects" aria-label="Прогресс по проектам">
				<div class="section-heading">
					<h2>Прогресс по проектам</h2>
					{#if projectKey !== 'all'}
						<button type="button" class="btn" onclick={() => (projectKey = 'all')}>Показать все проекты</button>
					{/if}
				</div>
				{#each shownProjects as project (project.key)}
					<article class="project">
						<div class="project-head">
							<button
								type="button"
								class="project-name"
								title="Показать задачи проекта"
								onclick={() => (projectKey = projectKey === project.key ? 'all' : project.key)}
							>
								{project.name}
							</button>
							<span class="project-count mono">{project.passed}/{project.total}</span>
						</div>
						<div class="bar" aria-label="{project.name}: решено {project.passed} из {project.total}">
							<div class="bar-fill" style:width="{project.percent}%"></div>
						</div>
						<ul class="folders">
							{#each project.folders as folder (folder.key)}
								<li class="folder">
									<span class="folder-name">{folder.name}</span>
									<span class="bar small" aria-label="{folder.name}: решено {folder.passed} из {folder.total}">
										<span class="bar-fill" style:width="{folder.percent}%"></span>
									</span>
									<span class="folder-count mono">{folder.passed}/{folder.total}</span>
								</li>
							{/each}
						</ul>
					</article>
				{/each}
			</section>
		{/if}

		<section class="filters" aria-label="Фильтры">
			<label class="filter">
				<span class="filter-label">Проект</span>
				<select bind:value={projectKey}>
					<option value="all">Все проекты</option>
					{#each projectTabs as [key, name] (key)}
						<option value={key}>{name}</option>
					{/each}
				</select>
			</label>
			<label class="filter">
				<span class="filter-label">Блок</span>
				<select bind:value={blockFilter}>
					<option value="all">Все блоки</option>
					{#each data.blocks as block (block)}
						<option value={block}>Блок {block}</option>
					{/each}
				</select>
			</label>
			<label class="filter">
				<span class="filter-label">Статус</span>
				<select bind:value={statusFilter}>
					<option value="all">Любой</option>
					<option value="new">Не начата</option>
					<option value="started">В работе</option>
					<option value="defense">Ждёт защиты</option>
					<option value="passed">Решена</option>
					<option value="failed">Есть ошибки</option>
				</select>
			</label>
			<label class="filter grow">
				<span class="filter-label">Поиск</span>
				<input type="search" placeholder="Найти задачу…" bind:value={search} />
			</label>
		</section>

		<section class="table-wrap" aria-label="Задачи">
			<div class="table-head">
				<h2>Задачи</h2>
				<span class="section-count">{filteredRows.length} из {rows.length}</span>
			</div>
			<table class="tasks">
				<thead>
					<tr>
						<th>Задача</th>
						<th>Название</th>
						<th>Где</th>
						<th>Статус</th>
						<th>Тесты</th>
						<th>Попытки</th>
						<th>Последняя</th>
						<th>Действия</th>
					</tr>
				</thead>
				<tbody>
					{#if filteredRows.length === 0}
						<tr>
							<td colspan="8" class="empty">Под текущие фильтры задачи не подходят.</td>
						</tr>
					{:else}
						{#each filteredRows as row (row.id)}
							{@const state = stateOf(row)}
							<tr class:next={row.id === cabinet?.next_task_id}>
								<td class="mono">{row.id}</td>
								<td>{row.title}</td>
								<td class="muted where">
									{row.project_name || `Блок ${row.block}`}
									{#if row.folder_name}<span class="folder-hint">› {row.folder_name}</span>{/if}
								</td>
								<td>
									<span class="status" data-status={state}>
										<span class="status-icon" aria-hidden="true">{statusIcon(state)}</span>
										{STATE_LABELS[state]}
									</span>
									{#if row.stale}<span class="stale" title="Прогресс относится к другой версии задачи">устар.</span>{/if}
								</td>
								<td class="mono">{row.passed_tests}/{row.total_tests}</td>
								<td class="mono">{row.attempts}</td>
								<td class="muted">{formatLastRun(row.last_run_at)}</td>
								<td class="actions">
									<button type="button" class="btn" onclick={() => openTask(row.id)}>{state === 'new' ? 'Открыть' : 'Продолжить'}</button>
									<button type="button" class="btn" onclick={() => checkTask(row.id)}>Проверить</button>
									{#if state === 'defense'}
										<button type="button" class="btn primary" onclick={() => defendTask(row.id)}>Защита</button>
									{:else}
										<button type="button" class="btn" onclick={() => hintsTask(row.id)}>Подсказки</button>
									{/if}
								</td>
							</tr>
						{/each}
					{/if}
				</tbody>
			</table>
		</section>

		{#if recentAttempts.length > 0}
			<section class="recent" aria-label="Последние попытки">
				<div class="section-heading">
					<h2>Последние попытки</h2>
				</div>
				<ul class="recent-list">
					{#each recentAttempts as row (row.id)}
						{@const state = stateOf(row)}
						<li class="recent-row">
							<span class="state-dot" data-status={state} aria-hidden="true">{statusIcon(state)}</span>
							<span class="recent-title">
								<button type="button" class="link" onclick={() => openTask(row.id)}>{row.id} · {row.title}</button>
							</span>
							<span class="status" data-status={state}>{STATE_LABELS[state]}</span>
							<span class="mono">{row.passed_tests}/{row.total_tests}</span>
							<span class="muted">{plural(row.attempts, 'попытка', 'попытки', 'попыток')}</span>
							<span class="muted">{formatLastRun(row.last_run_at)}</span>
						</li>
					{/each}
				</ul>
			</section>
		{/if}

		<footer class="footer">
			<button type="button" class="btn primary" onclick={pullAll} disabled={offline} title={offline ? 'Недоступно в локальном режиме' : 'Скачать все задачи'}>
				Загрузить задачи
			</button>
			<button
				type="button"
				class="btn primary"
				onclick={pushProgress}
				disabled={offline}
				title={offline ? 'Недоступно в локальном режиме — переключись на «Сервер»' : 'Отправить локальный прогресс на сервер'}
			>
				Отправить прогресс
			</button>
			<button type="button" class="btn" onclick={refresh}>Обновить</button>
		</footer>
	{/if}
</main>

<style>
	:global(html),
	:global(body) {
		margin: 0;
		height: 100%;
		font-family: 'JetBrains Mono', 'Cascadia Code', 'Fira Code', 'Consolas', 'Courier New', monospace;
		font-size: var(--vscode-font-size, 13px);
		color: var(--vscode-foreground);
		background: var(--vscode-editor-background);
	}

	:global(#app) {
		height: 100%;
	}

	.dashboard {
		box-sizing: border-box;
		min-height: 100%;
		padding: 1rem 1.25rem 1.25rem;
		display: flex;
		flex-direction: column;
		gap: 0.9rem;
	}

	.loading {
		flex: 1;
		display: flex;
		align-items: center;
		justify-content: center;
		opacity: 0.65;
	}

	.header {
		animation: header-in 0.45s ease-out both;
	}

	.brand-row {
		display: flex;
		align-items: baseline;
		gap: 0.75rem;
		flex-wrap: wrap;
	}

	.brand {
		margin: 0;
		font-size: 1.35rem;
		font-weight: 700;
		letter-spacing: -0.02em;
		line-height: 1.2;
	}

	.subheading {
		margin: 0.25rem 0 0;
		font-size: 0.85rem;
		opacity: 0.7;
	}

	.mode {
		font-size: 0.75rem;
		font-weight: 600;
		letter-spacing: 0.02em;
		text-transform: uppercase;
		padding: 0.15rem 0.45rem;
		border: 1px solid color-mix(in srgb, var(--vscode-focusBorder, var(--vscode-button-background)) 55%, transparent);
		color: var(--vscode-descriptionForeground, var(--vscode-foreground));
		background: color-mix(in srgb, var(--vscode-button-background) 12%, transparent);
	}

	.mode.offline {
		border-color: color-mix(in srgb, var(--vscode-foreground) 22%, transparent);
		background: color-mix(in srgb, var(--vscode-foreground) 6%, transparent);
	}

	.error {
		margin: 0;
		padding: 0.5rem 0.65rem;
		border-left: 3px solid var(--vscode-inputValidation-errorBorder, #f14c4c);
		background: color-mix(in srgb, var(--vscode-inputValidation-errorBackground, #f14c4c) 18%, transparent);
		color: var(--vscode-errorForeground, var(--vscode-foreground));
	}

	.summary {
		display: flex;
		flex-direction: column;
		gap: 0.55rem;
	}

	.metric-row {
		display: flex;
		flex-wrap: wrap;
		gap: 0.35rem 1.25rem;
	}

	.metric {
		display: flex;
		align-items: baseline;
		gap: 0.35rem;
		min-width: 4.5rem;
	}

	.metric-value {
		font-weight: 650;
		font-variant-numeric: tabular-nums;
	}

	.metric.passed .metric-value {
		color: var(--vscode-testing-iconPassed, #73c991);
	}

	.metric.defense .metric-value {
		color: var(--vscode-testing-iconQueued, #cca700);
	}

	.metric-label {
		font-size: 0.8rem;
		opacity: 0.7;
	}

	.progress {
		display: flex;
		align-items: center;
		gap: 0.65rem;
	}

	.progress-track {
		flex: 1;
		height: 0.35rem;
		border-radius: 2px;
		background: color-mix(in srgb, var(--vscode-foreground) 12%, transparent);
		overflow: hidden;
	}

	.progress-fill {
		height: 100%;
		border-radius: 2px;
		background: var(--vscode-button-background);
		transition: width 0.35s ease;
	}

	.progress-label {
		flex-shrink: 0;
		font-size: 0.8rem;
		opacity: 0.75;
		font-variant-numeric: tabular-nums;
	}

	.continue,
	.ai {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 1rem;
		padding: 0.7rem 0.85rem;
		border-left: 3px solid var(--vscode-focusBorder, var(--vscode-button-background));
		background: color-mix(in srgb, var(--vscode-button-background) 10%, transparent);
	}

	.continue-text,
	.ai-text {
		display: flex;
		flex-direction: column;
		gap: 0.15rem;
		min-width: 0;
	}

	.continue-eyebrow {
		font-size: 0.72rem;
		text-transform: uppercase;
		letter-spacing: 0.06em;
		opacity: 0.7;
	}

	.continue-title {
		font-size: 0.95rem;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.continue-meta,
	.ai-meta {
		font-size: 0.78rem;
		opacity: 0.75;
	}

	.ai-status {
		font-size: 0.85rem;
		color: var(--vscode-testing-iconFailed, #f14c4c);
	}

	.ai-status.available {
		color: var(--vscode-testing-iconPassed, #73c991);
	}

	.section-heading,
	.table-head {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 0.75rem;
	}

	h2 {
		margin: 0;
		font-size: 0.95rem;
		letter-spacing: -0.01em;
	}

	.section-count {
		font-size: 0.78rem;
		opacity: 0.7;
	}

	.empty-note {
		margin: 0.25rem 0 0;
		font-size: 0.82rem;
		opacity: 0.7;
	}

	.understanding-list,
	.folders,
	.recent-list {
		list-style: none;
		margin: 0.4rem 0 0;
		padding: 0;
	}

	.understanding-row,
	.recent-row {
		display: flex;
		align-items: center;
		gap: 0.6rem;
		padding: 0.35rem 0;
		border-bottom: 1px solid color-mix(in srgb, var(--vscode-foreground) 8%, transparent);
		flex-wrap: wrap;
	}

	.understanding-main {
		display: flex;
		flex-direction: column;
		gap: 0.1rem;
		min-width: 0;
		flex: 1;
	}

	.understanding-label {
		font-size: 0.78rem;
		opacity: 0.75;
	}

	.link {
		appearance: none;
		border: 0;
		background: none;
		padding: 0;
		color: var(--vscode-textLink-foreground, #3794ff);
		font: inherit;
		font-size: 0.85rem;
		text-align: left;
		cursor: pointer;
	}

	.link:hover:not(:disabled) {
		text-decoration: underline;
	}

	.link:disabled {
		color: var(--vscode-foreground);
		opacity: 0.6;
		cursor: default;
	}

	.state-dot {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		width: 1.1rem;
		height: 1.1rem;
		flex-shrink: 0;
		font-weight: 700;
		font-size: 0.75rem;
		border: 1px solid color-mix(in srgb, var(--vscode-foreground) 25%, transparent);
		border-radius: 50%;
	}

	.state-dot[data-status='passed'],
	.state-dot[data-status='confirmed'] {
		color: var(--vscode-testing-iconPassed, #73c991);
		border-color: currentColor;
	}

	.state-dot[data-status='defense'],
	.state-dot[data-status='pending'],
	.state-dot[data-status='active'],
	.state-dot[data-status='needs_review'] {
		color: var(--vscode-testing-iconQueued, #cca700);
		border-color: currentColor;
	}

	.state-dot[data-status='failed'] {
		color: var(--vscode-testing-iconFailed, #f14c4c);
		border-color: currentColor;
	}

	.projects {
		display: flex;
		flex-direction: column;
		gap: 0.6rem;
	}

	.recommendations {
		display: flex;
		flex-direction: column;
		gap: 0.6rem;
	}

	.recommendation-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(16rem, 1fr));
		gap: 0.6rem;
	}

	.recommendation-card {
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
		padding: 0.5rem 0.65rem;
		border: 1px solid color-mix(in srgb, var(--vscode-foreground) 14%, transparent);
		font-size: 0.8rem;
	}

	.recommendation-card.unmet {
		border-left: 3px solid var(--vscode-testing-iconQueued, #cca700);
		background: color-mix(in srgb, var(--vscode-testing-iconQueued, #cca700) 8%, transparent);
	}

	.recommendation-head {
		display: flex;
		align-items: baseline;
		justify-content: space-between;
		gap: 0.6rem;
	}

	.recommendation-name {
		font-size: 0.85rem;
		font-weight: 650;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.recommendation-readiness {
		color: var(--vscode-testing-iconQueued, #cca700);
		font-weight: 600;
	}

	.recommendation-kinds,
	.recommendation-note,
	.recommendation-done {
		font-size: 0.76rem;
		opacity: 0.78;
	}

	.recommendation-done {
		opacity: 0.6;
	}

	.breakdown-list {
		list-style: none;
		margin: 0.2rem 0 0;
		padding: 0;
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
	}

	.breakdown-row {
		display: flex;
		align-items: center;
		gap: 0.6rem;
	}

	.breakdown-label {
		flex: 0 0 6.5rem;
		opacity: 0.85;
	}

	.project {
		padding: 0.5rem 0.65rem;
		border: 1px solid color-mix(in srgb, var(--vscode-foreground) 14%, transparent);
	}

	.project-head {
		display: flex;
		align-items: baseline;
		justify-content: space-between;
		gap: 0.75rem;
	}

	.project-name {
		appearance: none;
		border: 0;
		background: none;
		padding: 0;
		font: inherit;
		font-weight: 650;
		color: var(--vscode-foreground);
		cursor: pointer;
		text-align: left;
	}

	.project-name:hover {
		color: var(--vscode-textLink-foreground, #3794ff);
	}

	.project-count,
	.folder-count {
		font-size: 0.8rem;
		opacity: 0.85;
	}

	.bar {
		display: block;
		height: 0.4rem;
		margin: 0.35rem 0;
		border-radius: 2px;
		background: color-mix(in srgb, var(--vscode-foreground) 12%, transparent);
		overflow: hidden;
	}

	.bar.small {
		flex: 1;
		height: 0.25rem;
		margin: 0;
	}

	.bar-fill {
		display: block;
		height: 100%;
		background: var(--vscode-testing-iconPassed, var(--vscode-button-background));
		transition: width 0.35s ease;
	}

	.folders {
		margin-top: 0.3rem;
		display: flex;
		flex-direction: column;
		gap: 0.2rem;
	}

	.folder {
		display: flex;
		align-items: center;
		gap: 0.6rem;
		font-size: 0.8rem;
	}

	.folder-name {
		flex: 0 0 12rem;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
		opacity: 0.85;
	}

	.filters {
		display: flex;
		flex-wrap: wrap;
		gap: 0.75rem 1rem;
	}

	.filter {
		display: flex;
		align-items: center;
		gap: 0.4rem;
	}

	.filter.grow {
		flex: 1;
		min-width: 12rem;
	}

	.filter-label {
		font-size: 0.8rem;
		opacity: 0.75;
	}

	select,
	input[type='search'] {
		appearance: none;
		min-width: 9rem;
		padding: 0.25rem 0.5rem;
		border: 1px solid var(--vscode-dropdown-border, var(--vscode-input-border, transparent));
		border-radius: 2px;
		background: var(--vscode-dropdown-background, var(--vscode-input-background));
		color: var(--vscode-dropdown-foreground, var(--vscode-input-foreground, var(--vscode-foreground)));
		font: inherit;
	}

	.filter.grow input[type='search'] {
		flex: 1;
		width: 100%;
	}

	select:focus-visible,
	input[type='search']:focus-visible {
		outline: 1px solid var(--vscode-focusBorder, var(--vscode-button-background));
		outline-offset: 1px;
	}

	.table-wrap {
		overflow-x: auto;
		border-top: 1px solid color-mix(in srgb, var(--vscode-foreground) 14%, transparent);
		border-bottom: 1px solid color-mix(in srgb, var(--vscode-foreground) 14%, transparent);
	}

	.table-head {
		padding: 0.45rem 0;
	}

	.tasks {
		width: 100%;
		border-collapse: collapse;
		min-width: 44rem;
	}

	th,
	td {
		padding: 0.4rem 0.55rem;
		text-align: left;
		vertical-align: middle;
		white-space: nowrap;
	}

	th {
		font-size: 0.75rem;
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.03em;
		opacity: 0.7;
		border-bottom: 1px solid color-mix(in srgb, var(--vscode-foreground) 16%, transparent);
	}

	tbody tr {
		transition: background-color 0.12s ease;
	}

	tbody tr:hover {
		background: var(--vscode-list-hoverBackground, color-mix(in srgb, var(--vscode-foreground) 6%, transparent));
	}

	tbody tr.next {
		box-shadow: inset 2px 0 var(--vscode-focusBorder, var(--vscode-button-background));
	}

	td {
		border-bottom: 1px solid color-mix(in srgb, var(--vscode-foreground) 8%, transparent);
	}

	.where {
		max-width: 16rem;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	.folder-hint {
		margin-left: 0.3rem;
		opacity: 0.7;
	}

	.mono {
		font-family: var(--vscode-editor-font-family, ui-monospace, monospace);
		font-size: 0.9em;
		font-variant-numeric: tabular-nums;
	}

	.muted {
		opacity: 0.75;
	}

	.stale {
		display: inline-block;
		margin-left: 0.35rem;
		font-family: var(--vscode-font-family, sans-serif);
		font-size: 0.68rem;
		font-weight: 500;
		color: var(--vscode-descriptionForeground, var(--vscode-foreground));
		opacity: 0.8;
	}

	.empty {
		text-align: center;
		opacity: 0.65;
		padding: 1.25rem 0.55rem;
		white-space: normal;
	}

	.status {
		display: inline-flex;
		align-items: center;
		gap: 0.3rem;
	}

	[data-status='passed']:not(.state-dot) {
		color: var(--vscode-testing-iconPassed, inherit);
	}

	[data-status='defense']:not(.state-dot) {
		color: var(--vscode-testing-iconQueued, inherit);
	}

	[data-status='failed']:not(.state-dot) {
		color: var(--vscode-testing-iconFailed, inherit);
	}

	.status-icon {
		font-weight: 700;
		opacity: 0.9;
	}

	.actions {
		display: flex;
		gap: 0.3rem;
	}

	.recent-title {
		flex: 1;
		min-width: 10rem;
	}

	.footer {
		display: flex;
		flex-wrap: wrap;
		gap: 0.45rem;
		padding-top: 0.15rem;
	}

	.btn {
		appearance: none;
		border: 1px solid color-mix(in srgb, var(--vscode-foreground) 18%, transparent);
		border-radius: 2px;
		padding: 0.28rem 0.55rem;
		font: inherit;
		font-size: 0.8rem;
		cursor: pointer;
		background: var(--vscode-button-secondaryBackground, transparent);
		color: var(--vscode-button-secondaryForeground, var(--vscode-foreground));
		transition:
			background-color 0.12s ease,
			border-color 0.12s ease,
			opacity 0.12s ease;
	}

	.btn:hover:not(:disabled) {
		background: var(--vscode-list-hoverBackground, color-mix(in srgb, var(--vscode-foreground) 8%, transparent));
	}

	.btn:focus-visible {
		outline: 1px solid var(--vscode-focusBorder, var(--vscode-button-background));
		outline-offset: 1px;
	}

	.btn:disabled {
		opacity: 0.45;
		cursor: not-allowed;
	}

	.btn.primary {
		background: var(--vscode-button-background);
		color: var(--vscode-button-foreground);
		border-color: transparent;
	}

	.btn.primary:hover:not(:disabled) {
		background: var(--vscode-button-hoverBackground, var(--vscode-button-background));
	}

	@keyframes header-in {
		from {
			opacity: 0;
			transform: translateY(-0.25rem);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}

	@media (max-width: 720px) {
		.continue,
		.ai {
			flex-direction: column;
			align-items: flex-start;
		}

		.folder-name {
			flex-basis: 7rem;
		}
	}

	@media (prefers-reduced-motion: reduce) {
		.header {
			animation: none;
		}

		.progress-fill,
		.bar-fill,
		tbody tr {
			transition: none;
		}
	}
</style>
