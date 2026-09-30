<script lang="ts">
	import { onDestroy, onMount, untrack } from 'svelte';
	import MonacoEditor from './MonacoEditor.svelte';
	import { getCatalog, getTaskStudio, validateTaskStudio, saveTaskStudio, type CatalogDTO, type CatalogTaskDTO, type StudioCandidateBody, type TaskStudioDTO, type StudioValidateResponse, type StudioSaveResponse } from '../api';
	import type { TaskDraft } from '../consoleApi';

	type FileKey = 'markdown' | 'solution_py' | 'tests_py';
	type OpenDoc = { taskId: string; file: FileKey; key: string };
	type TaskState = {
		taskId: string; task: CatalogTaskDTO | null; studio: TaskStudioDTO | null;
		buffers: Record<FileKey, string>; version: string; etag: string;
		loading: boolean; loadError: string; generation: number; saving: boolean; validating: boolean;
		saveError: string; validateError: string; result: StudioValidateResponse | null; saved: StudioSaveResponse | null;
		notice: string; draftConflict: string; pendingDraft: TaskDraft | null;
	};
	const fileInfo: Record<FileKey, { label: string; language: 'markdown' | 'python'; suffix: string }> = {
		markdown: { label: 'Условие', language: 'markdown', suffix: '.md' },
		solution_py: { label: 'Решение', language: 'python', suffix: '.solution.py' },
		tests_py: { label: 'Тесты', language: 'python', suffix: '.tests.py' },
	};
	const fileKeys: FileKey[] = ['markdown', 'solution_py', 'tests_py'];
	let { role, initialTaskId = '', draft = null, onDirtyChange, onBusyChange, onActiveTask }:
		{ role: string; initialTaskId?: string; draft?: TaskDraft | null; onDirtyChange?: (dirty: boolean) => void; onBusyChange?: (busy: boolean) => void; onActiveTask?: (id: string, label: string) => void } = $props();
	const canEdit = $derived(role === 'admin');
	let catalog = $state<CatalogDTO | null>(null);
	let catalogLoading = $state(true);
	let catalogError = $state('');
	let query = $state('');
	let expanded = $state<Record<string, boolean>>({});
	let taskStates = $state<Record<string, TaskState>>({});
	let opened = $state<OpenDoc[]>([]);
	let activeKey = $state('');
	let mobileExplorerOpen = $state(false);
	let catalogRequest = 0;
	let navigationRequest = 0;
	let loadRequests: Record<string, Promise<TaskState | null>> = {};
	let lastInitialTaskId = '';
	let lastDraft: TaskDraft | null = null;
	let lastActiveNotice = '';
	let disposed = false;
	let workspaceElement: HTMLDivElement;
	let currentDoc = $derived(opened.find((doc) => doc.key === activeKey) ?? null);
	let activeState = $derived(currentDoc ? taskStates[currentDoc.taskId] ?? null : null);
	let activeTask = $derived(activeState?.task ?? findTask(currentDoc?.taskId ?? ''));
	let activeDirty = $derived(!!activeState && isTaskDirty(activeState));
	let globalDirty = $derived(Object.values(taskStates).some(isTaskDirty));
	let activeBusy = $derived(!!activeState && (activeState.loading || activeState.saving || activeState.validating));
	let globalBusy = $derived(Object.values(taskStates).some((task) => task.saving || task.validating));
	let canWrite = $derived(!!activeState?.studio?.writable && canEdit && !activeState.draftConflict);
	let editorValue = $derived(activeState && currentDoc ? activeState.buffers[currentDoc.file] : '');
	let activePath = $derived(activeState && currentDoc ? pathFor(activeState, currentDoc.file) : '');
	let filteredProjects = $derived(filterCatalog(catalog?.projects ?? [], query));

	function allTasks(): CatalogTaskDTO[] {
		return (catalog?.projects ?? []).flatMap((project) => project.folders.flatMap((folder) => folder.tasks));
	}
	function findTask(id: string): CatalogTaskDTO | null {
		const tasks = allTasks();
		return tasks.find((task) => task.id === id) ?? tasks.find((task) => task.task_id === id) ?? null;
	}
	function filterCatalog(projects: CatalogDTO['projects'], raw: string) {
		const needle = raw.trim().toLocaleLowerCase();
		if (!needle) return projects;
		return projects.map((project) => {
			const projectMatch = `${project.name} ${project.id}`.toLocaleLowerCase().includes(needle);
			const folders = project.folders.map((folder) => {
				const folderMatch = `${folder.name} ${folder.code} ${folder.id}`.toLocaleLowerCase().includes(needle);
				const tasks = folder.tasks.filter((task) => projectMatch || folderMatch || `${task.title} ${task.task_id} ${task.id} ${task.slug}`.toLocaleLowerCase().includes(needle));
				return { ...folder, tasks };
			}).filter((folder) => folder.tasks.length > 0 || (!needle && folder.tasks.length === 0));
			return { ...project, folders };
		}).filter((project) => project.folders.some((folder) => folder.tasks.length > 0));
	}
	function isTaskDirty(task: TaskState): boolean {
		return !!task.draftConflict || (!!task.studio && (task.buffers.markdown !== task.studio.markdown || task.buffers.solution_py !== task.studio.solution_py || task.buffers.tests_py !== task.studio.tests_py));
	}
	function patchTask(taskId: string, patch: Partial<TaskState>) {
		const prior = taskStates[taskId];
		if (prior) taskStates = { ...taskStates, [taskId]: { ...prior, ...patch } };
	}
	function emptyState(taskId: string, task: CatalogTaskDTO | null): TaskState {
		return { taskId, task, studio: null, buffers: { markdown: '', solution_py: '', tests_py: '' }, version: '', etag: '', loading: false, loadError: '', generation: 0, saving: false, validating: false, saveError: '', validateError: '', result: null, saved: null, notice: '', draftConflict: '', pendingDraft: null };
	}
	function pathFor(state: TaskState, file: FileKey): string {
		const base = state.studio?.md_path || state.task?.md_path || `${state.task?.slug || state.task?.task_id || state.taskId}.md`;
		if (file === 'markdown') return base;
		return base.replace(/\.md$/i, fileInfo[file].suffix);
	}
	function docKey(taskId: string, file: FileKey) { return `${taskId}::${file}`; }
	function openDoc(task: CatalogTaskDTO | null, taskId: string, file: FileKey = 'markdown', focus = true) {
		const state = taskStates[taskId];
		if (!state) taskStates = { ...taskStates, [taskId]: emptyState(taskId, task) };
		else if (task && state.task !== task) patchTask(taskId, { task });
		const key = docKey(taskId, file);
		if (!opened.some((doc) => doc.key === key)) opened = [...opened, { taskId, file, key }];
		if (focus) {
			activeKey = key;
		}
	}
	async function loadCatalog() {
		const request = ++catalogRequest;
		catalogLoading = true; catalogError = '';
		try { const data = await getCatalog(); if (request === catalogRequest) catalog = data; }
		catch (error) { if (request === catalogRequest) catalogError = (error as Error).message; }
		finally { if (request === catalogRequest) catalogLoading = false; }
	}
	function bodyFor(state: TaskState): StudioCandidateBody {
		return { expected_version: state.version, expected_content_etag: state.etag, markdown: state.buffers.markdown, solution_py: state.buffers.solution_py, tests_py: state.buffers.tests_py };
	}
	async function ensureLoaded(taskId: string, task: CatalogTaskDTO | null, force = false): Promise<TaskState | null> {
		let state = taskStates[taskId];
		if (!state) { state = emptyState(taskId, task); taskStates = { ...taskStates, [taskId]: state }; }
		else if (task && state.task !== task) { patchTask(taskId, { task }); state = taskStates[taskId]; }
		if (!force && state.studio) return state;
		if (!force && loadRequests[taskId]) return loadRequests[taskId];
		const generation = state.generation + 1;
		patchTask(taskId, { loading: true, loadError: '', generation, notice: '', saveError: '', validateError: '' });
		const promise = (async () => {
			try {
				const data = await getTaskStudio(taskId);
				const current = taskStates[taskId];
				if (!current || current.generation !== generation || disposed) return current ?? null;
				const next: TaskState = { ...current, studio: data, task: current.task ?? task, buffers: { markdown: data.markdown, solution_py: data.solution_py, tests_py: data.tests_py }, version: data.version, etag: data.content_etag, loading: false, loadError: '', draftConflict: '', pendingDraft: null };
				taskStates = { ...taskStates, [taskId]: next };
				return next;
			} catch (error) {
				const current = taskStates[taskId];
				if (current?.generation === generation && !disposed) patchTask(taskId, { loading: false, loadError: (error as Error).message });
				return current ?? null;
			} finally { if (loadRequests[taskId] === promise) delete loadRequests[taskId]; }
		})();
		loadRequests[taskId] = promise;
		return promise;
	}
	async function focusTask(task: CatalogTaskDTO, file: FileKey = 'markdown') {
		mobileExplorerOpen = false;
		const request = ++navigationRequest;
		openDoc(task, task.id, file);
		const state = await ensureLoaded(task.id, task);
		if (request !== navigationRequest || !state) return;
		openDoc(task, task.id, file);
	}
	async function openExternal(targetId: string, incomingDraft: TaskDraft | null) {
		const lookupId = incomingDraft?.task_id || targetId;
		let task = findTask(lookupId);
		if (!task && catalogLoading) { await new Promise<void>((resolve) => { const check = () => !disposed && catalogLoading ? setTimeout(check, 20) : resolve(); check(); }); task = findTask(lookupId); }
		if (disposed) return;
		const taskId = task?.id ?? (lookupId || targetId);
		if (!taskId) return;
		const request = ++navigationRequest;
		openDoc(task, taskId, 'markdown');
		const state = await ensureLoaded(taskId, task);
		if (request !== navigationRequest || !state) return;
		if (incomingDraft) {
			const candidateIdMatches = incomingDraft.task_id === taskId || incomingDraft.task_id === task?.task_id;
			const matches = candidateIdMatches && incomingDraft.expected_version === state.version && incomingDraft.expected_content_etag === state.etag;
			patchTask(taskId, { pendingDraft: incomingDraft, draftConflict: matches ? '' : `Черновик AI основан на другой версии (${incomingDraft.expected_version}); сервер сейчас на v${state.version}. Содержимое сохранено для ручного просмотра.`, notice: 'Предложение AI готово к просмотру.' });
		}
		openDoc(task, taskId, 'markdown');
	}
	function applyPendingDraft(taskId: string) {
		const state = taskStates[taskId]; const draftToApply = state?.pendingDraft;
		if (!state || !draftToApply || !state.studio || state.loading || state.saving || state.validating) return;
		const replacesEdits = isTaskDirty(state);
		if (replacesEdits && !confirm('В задаче есть локальные изменения. Заменить все три файла черновиком AI?')) return;
		const identityMatches = draftToApply.task_id === taskId || draftToApply.task_id === state.task?.task_id;
		const versionMatches = draftToApply.expected_version === state.version && draftToApply.expected_content_etag === state.etag;
		if (!identityMatches || !versionMatches) {
			patchTask(taskId, { buffers: { markdown: draftToApply.markdown, solution_py: draftToApply.solution_py, tests_py: draftToApply.tests_py }, version: draftToApply.expected_version, etag: draftToApply.expected_content_etag, pendingDraft: null, draftConflict: `Черновик устарел: ожидалась версия v${draftToApply.expected_version}; текущая версия сервера — v${state.studio.version}. Текст сохранён, проверка и запись заблокированы.` });
			return;
		}
		patchTask(taskId, { buffers: { markdown: draftToApply.markdown, solution_py: draftToApply.solution_py, tests_py: draftToApply.tests_py }, pendingDraft: null, draftConflict: '', notice: 'Черновик AI применён. Проверь все файлы перед сохранением.' });
	}
	function editValue(value: string) {
		if (!activeState || !currentDoc || activeBusy || !canWrite) return;
		patchTask(activeState.taskId, { buffers: { ...activeState.buffers, [currentDoc.file]: value }, result: null, saved: null, saveError: '', validateError: '' });
	}
	function bumpPatchVersion() {
		const state = activeState;
		if (!state?.studio || !canWrite || activeBusy) return;
		const markdown = state.buffers.markdown;
		const frontmatter = /^(---)(\r?\n)([\s\S]*?)(\r?\n---)(?=\r?\n|$)/.exec(markdown);
		if (!frontmatter) {
			patchTask(state.taskId, { notice: 'Не найден YAML frontmatter; версию не изменила.' });
			return;
		}
		const newline = frontmatter[2];
		const contents = frontmatter[3];
		const versionLine = /^(\s*version\s*:\s*)(["']?)(\d+)\.(\d+)\.(\d+)(?:[-+][\w.-]+)?\2(\s*(?:#.*)?)$/m.exec(contents);
		let next: string;
		let updatedContents: string;
		if (versionLine) {
			next = `${versionLine[3]}.${versionLine[4]}.${Number(versionLine[5]) + 1}`;
			updatedContents = contents.replace(versionLine[0], `${versionLine[1]}${versionLine[2]}${next}${versionLine[2]}${versionLine[6]}`);
		} else {
			if (/^\s*version\s*:/m.test(contents)) {
				patchTask(state.taskId, { notice: 'Поле version в YAML имеет неподдерживаемый формат; версию не изменила.' });
				return;
			}
			const fallback = /^(\d+)\.(\d+)\.(\d+)(?:[-+][\w.-]+)?$/.exec(state.studio.version);
			if (!fallback) {
				patchTask(state.taskId, { notice: `Не удалось разобрать версию ${state.studio.version}; в frontmatter тоже нет корректного version.` });
				return;
			}
			next = `${fallback[1]}.${fallback[2]}.${Number(fallback[3]) + 1}`;
			updatedContents = `${contents}${contents ? newline : ''}version: ${next}`;
		}
		const updatedMarkdown = `${frontmatter[1]}${newline}${updatedContents}${frontmatter[4]}${markdown.slice(frontmatter[0].length)}`;
		patchTask(state.taskId, { buffers: { ...state.buffers, markdown: updatedMarkdown }, result: null, saved: null, notice: `Версия в YAML изменена на ${next}. Проверь diff и сохрани задачу отдельно.` });
	}
	function closeDoc(doc: OpenDoc) {
		const state = taskStates[doc.taskId];
		if (state?.loading || state?.saving || state?.validating) return;
		const dirty = !!state?.studio && state.buffers[doc.file] !== state.studio[doc.file];
		if (dirty && !confirm(`В файле ${pathFor(state!, doc.file)} есть изменения. Отбросить их и закрыть вкладку? Остальные файлы задачи останутся без изменений.`)) return;
		if (dirty && state?.studio) patchTask(doc.taskId, { buffers: { ...state.buffers, [doc.file]: state.studio[doc.file] }, notice: 'Изменения закрытого файла отброшены; остальные буферы сохранены.' });
		const index = opened.findIndex((item) => item.key === doc.key);
		const remaining = opened.filter((item) => item.key !== doc.key);
		opened = remaining;
		if (activeKey === doc.key) activeKey = remaining[Math.min(index, remaining.length - 1)]?.key ?? '';
	}
	async function reloadActive() {
		if (!activeState || activeBusy) return;
		if (isTaskDirty(activeState) && !confirm('Перезагрузить активную задачу с сервера и отбросить её локальные изменения?')) return;
		const taskId = activeState.taskId; const task = activeState.task;
		await ensureLoaded(taskId, task, true);
	}
	async function validateActive() {
		const state = activeState;
		if (!state?.studio || !canWrite || state.saving || state.validating || state.loading || !isTaskDirty(state)) return;
		const taskId = state.taskId; const snapshot = bodyFor(state);
		patchTask(taskId, { validating: true, validateError: '', result: null, notice: '' });
		try { const result = await validateTaskStudio(taskId, snapshot); if (taskStates[taskId]?.version === snapshot.expected_version && taskStates[taskId]?.etag === snapshot.expected_content_etag) patchTask(taskId, { result }); }
		catch (error) { patchTask(taskId, { validateError: (error as Error).message }); }
		finally { patchTask(taskId, { validating: false }); }
	}
	async function saveActive() {
		const state = activeState;
		if (!state?.studio || !canWrite || state.saving || state.validating || state.loading || !isTaskDirty(state)) return;
		const taskId = state.taskId; const snapshot = bodyFor(state);
		patchTask(taskId, { saving: true, saveError: '', saved: null, result: null, notice: '' });
		try {
			const saved = await saveTaskStudio(taskId, snapshot);
			patchTask(taskId, { saved });
			const result = await ensureLoaded(taskId, taskStates[taskId]?.task ?? null, true);
			if (result && !disposed) patchTask(taskId, { notice: result.loadError || result.loading
				? `Сохранено на сервере (v${saved.new_version}), но не удалось перечитать задачу. Буферы сохранены; повтори загрузку.`
				: `Сохранено (v${saved.new_version}); состояние перечитано с сервера.` });
		} catch (error) { patchTask(taskId, { saveError: (error as Error).message }); }
		finally { patchTask(taskId, { saving: false }); }
	}
	async function discardTaskDraft(taskId: string) {
		const state = taskStates[taskId];
		if (!state?.studio || state.saving || state.validating || !confirm('Отбросить все три локальных файла этой задачи и заново загрузить текущую версию сервера?')) return;
		const loaded = await ensureLoaded(taskId, state.task, true);
		if (loaded) patchTask(taskId, { pendingDraft: null, draftConflict: '', notice: 'Локальные изменения отброшены; содержимое перечитано с сервера.' });
	}
	function toggle(key: string) { expanded = { ...expanded, [key]: expanded[key] === false }; }
	function handleKeydown(event: KeyboardEvent) {
		if (!workspaceElement?.getClientRects().length) return;
		if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 's') { event.preventDefault(); void saveActive(); }
	}
	$effect(() => { const dirty = globalDirty; onDirtyChange?.(dirty); });
	$effect(() => { const busy = globalBusy; onBusyChange?.(busy); });
	$effect(() => {
		const doc = currentDoc;
		const task = doc ? taskStates[doc.taskId]?.task ?? findTask(doc.taskId) : null;
		const id = doc ? (task?.id ?? doc.taskId) : '';
		const label = doc ? (task?.task_id ?? task?.title ?? doc.taskId) : '';
		const identity = `${id}\u0000${label}`;
		if (identity === lastActiveNotice) return;
		lastActiveNotice = identity;
		const callback = onActiveTask;
		untrack(() => callback?.(id, label));
	});
	$effect(() => {
		const targetId = initialTaskId; const incoming = draft;
		if (targetId === lastInitialTaskId && incoming === lastDraft) return;
		const draftChanged = incoming !== lastDraft;
		lastInitialTaskId = targetId; lastDraft = incoming;
		void untrack(() => openExternal(targetId, draftChanged ? incoming : null));
	});
	onMount(() => { void loadCatalog(); window.addEventListener('keydown', handleKeydown); });
	onDestroy(() => { disposed = true; catalogRequest++; navigationRequest++; window.removeEventListener('keydown', handleKeydown); onDirtyChange?.(false); onBusyChange?.(false); });
</script>

<div class="workspace" bind:this={workspaceElement} aria-label="Редактор задач">
	<div class="mobile-toolbar"><button type="button" onclick={() => mobileExplorerOpen = !mobileExplorerOpen} aria-expanded={mobileExplorerOpen} aria-controls="task-explorer">{mobileExplorerOpen ? 'Закрыть файлы' : 'Файлы'}</button>{#if activeTask}<span>{activeTask.task_id}</span>{/if}</div>
	<aside id="task-explorer" class="explorer" class:mobile-open={mobileExplorerOpen} aria-label="Обозреватель каталога">
		<div class="explorer-head"><div><small>ПРОЕКТ</small><strong>Задачи</strong></div><button class="icon" type="button" onclick={() => void loadCatalog()} disabled={catalogLoading} aria-label="Обновить каталог" title="Обновить каталог">↻</button></div>
		<label class="search"><span aria-hidden="true">⌕</span><input type="search" bind:value={query} placeholder="Поиск задач" aria-label="Поиск по названиям и ID" /><kbd> / </kbd></label>
		{#if catalogLoading && !catalog}<p class="tree-state">Загружаю каталог…</p>
		{:else if catalogError}<div class="tree-state error" role="alert"><span>{catalogError}</span><button type="button" onclick={() => void loadCatalog()}>Повторить</button></div>
		{:else if filteredProjects.length === 0}<p class="tree-state">{query ? 'Совпадений нет.' : 'Каталог пуст.'}</p>
		{:else}
			<ul class="tree">
			{#each filteredProjects as project (project.id)}
				<li><button class="tree-row project" type="button" onclick={() => toggle(`p:${project.id}`)} aria-expanded={query ? true : expanded[`p:${project.id}`] !== false}><span class="chevron">{query || expanded[`p:${project.id}`] !== false ? '▾' : '▸'}</span><span class="node-icon">▰</span><span class="node-label">{project.name || project.id}</span></button>
				{#if query || expanded[`p:${project.id}`] !== false}<ul>
					{#each project.folders as folder (folder.id)}
						<li><button class="tree-row folder" type="button" onclick={() => toggle(`f:${folder.id}`)} aria-expanded={query ? true : expanded[`f:${folder.id}`] !== false}><span class="chevron">{query || expanded[`f:${folder.id}`] !== false ? '▾' : '▸'}</span><span class="node-icon">▱</span><span class="node-label">{folder.name || folder.code}</span></button>
						{#if query || expanded[`f:${folder.id}`] !== false}<ul>
							{#each folder.tasks as task (task.id)}
								{@const state = taskStates[task.id]}
								<li><button class="tree-row task" type="button" onclick={() => toggle(`t:${task.id}`)} aria-expanded={query || expanded[`t:${task.id}`] !== false} title={`${task.task_id} · ${task.title}`}><span class="chevron">{query || expanded[`t:${task.id}`] !== false ? '▾' : '▸'}</span><span class="node-icon task-icon">◇</span><span class="node-label"><strong>{task.task_id}</strong><small>{task.title || task.slug}</small></span>{#if state && isTaskDirty(state)}<span class="dirty-dot" aria-label="Есть несохранённые изменения">●</span>{/if}</button>
									{#if query || expanded[`t:${task.id}`] !== false}<ul class="files">{#each fileKeys as file}<li><button class="tree-row file" type="button" class:current={activeKey === docKey(task.id, file)} onclick={() => void focusTask(task, file)}><span class="chevron"></span><span class="file-icon">{file === 'markdown' ? 'M' : 'Py'}</span><span class="node-label">{pathFor(state ?? emptyState(task.id, task), file).split(/[\\/]/).pop()}</span>{#if opened.some((doc) => doc.key === docKey(task.id, file))}<span class="opened-dot">{state && state.buffers[file] !== state.studio?.[file] ? '●' : ''}</span>{/if}</button></li>{/each}</ul>{/if}
								</li>
							{/each}
						</ul>{/if}</li>
					{/each}
				</ul>{/if}</li>
			{/each}
			</ul>
		{/if}
	</aside>
	<section class="editor-area" aria-label="Содержимое задачи">
		{#if opened.length > 0}<div class="tabs" role="tablist" aria-label="Открытые файлы">{#each opened as doc (doc.key)}{@const state = taskStates[doc.taskId]}<div class="tab-wrap"><button type="button" role="tab" aria-selected={activeKey === doc.key} class:active={activeKey === doc.key} class="tab" onclick={() => { if (!state?.loading && !state?.saving && !state?.validating) activeKey = doc.key; }} disabled={state?.loading || state?.saving || state?.validating}><span class="tab-name">{state?.task?.task_id ?? doc.taskId} · {pathFor(state ?? emptyState(doc.taskId, null), doc.file).split(/[\\/]/).pop()}</span>{#if state && state.buffers[doc.file] !== state.studio?.[doc.file]}<span class="tab-dirty" aria-label="Несохранённые изменения">●</span>{/if}</button><button class="tab-close" type="button" onclick={() => closeDoc(doc)} disabled={state?.loading || state?.saving || state?.validating} aria-label={`Закрыть ${doc.file} для ${doc.taskId}`}>×</button></div>{/each}</div>{/if}
		{#if activeState?.studio && currentDoc}
			<header class="file-header"><div class="file-title"><small>{activeTask?.task_id ?? activeState.taskId} / {activeTask?.title ?? 'Задача'}</small><h2>{activePath}</h2></div><div class="file-meta"><span>v{activeState.studio.version}</span>{#if activeDirty}<span class="unsaved">● Изменено</span>{/if}<button type="button" onclick={() => void reloadActive()} disabled={activeBusy} aria-label="Перечитать активную задачу с сервера">↻</button></div></header>
			{#if activeState.loadError}<p class="inline-error" role="alert">Не удалось обновить серверное состояние: {activeState.loadError}</p>{/if}
			{#if !activeState.studio.writable}<p class="banner" role="status">Только чтение: {activeState.studio.read_only_reason || 'репозиторий контента закрыт для записи'}.</p>{:else if !canEdit}<p class="banner" role="status">Режим просмотра: наставник может читать содержимое задач, но не менять его.</p>{/if}
			{#if activeState.draftConflict}<div class="banner conflict" role="alert">{activeState.draftConflict}<button type="button" onclick={() => discardTaskDraft(activeState.taskId)} disabled={activeBusy}>Отбросить локальный черновик и перечитать версию сервера</button></div>{/if}
			{#if activeState.pendingDraft}<div class="banner proposal" role="status">Предложение AI ожидает проверки. Сверь идентификатор, версию и три файла перед применением.<button type="button" onclick={() => applyPendingDraft(activeState.taskId)} disabled={activeBusy}>Просмотреть и применить черновик</button></div>{/if}
			{#if activeState.notice}<p class="notice" role="status">{activeState.notice}</p>{/if}
			{#if activeState.saveError}<p class="inline-error" role="alert">Сохранение не удалось: {activeState.saveError}</p>{/if}
			{#if activeState.validateError}<p class="inline-error" role="alert">Проверка не удалась: {activeState.validateError}</p>{/if}
			{#if activeState.result}<p class="result" role="status">Проверка пройдена · кандидат v{activeState.result.candidate_version} · {activeState.result.version_policy}</p>{/if}
			{#if activeState.saved}<p class="result" role="status">Сохранено: v{activeState.saved.new_version} · синхронизация {activeState.saved.sync.status}</p>{/if}
		{/if}
		<div class="editor-canvas">
			{#if !currentDoc}<div class="welcome"><span class="welcome-mark">E</span><h2>Редактор каталога</h2><p>Выбери задачу слева. Её условие, решение и тесты откроются отдельными вкладками.</p><kbd>Ctrl / ⌘ + S</kbd> сохранить активную задачу</div>
			{:else if activeState?.loading && !activeState.studio}<div class="center-state">Загружаю файлы задачи…</div>
			{:else if activeState?.loadError && !activeState.studio}<div class="center-state error" role="alert"><p>{activeState.loadError}</p><button type="button" onclick={() => void ensureLoaded(activeState.taskId, activeState.task, true)}>Повторить загрузку</button></div>
			{/if}
			<div class="monaco-host" hidden={!activeState?.studio || !currentDoc}>
				<MonacoEditor documentId={currentDoc?.key ?? '__empty__'} value={editorValue} language={currentDoc ? fileInfo[currentDoc.file].language : 'markdown'} readOnly={!canWrite || activeBusy || !activeState?.studio} onChange={editValue} onSave={() => void saveActive()} />
			</div>
		</div>
		{#if activeState?.studio && currentDoc}<footer class="editor-footer"><span class="path-label" title={activePath}>{activePath}</span><span class="footer-right">{activeDirty ? 'Не сохранено' : 'Синхронизировано с сервером'} · v{activeState.studio.version}</span><div class="actions">{#if canEdit}<button type="button" onclick={bumpPatchVersion} disabled={!canWrite || activeBusy}>Версия +patch</button><button type="button" onclick={() => void validateActive()} disabled={!canWrite || activeBusy || !activeDirty}>{activeState.validating ? 'Проверяю…' : 'Проверить'}</button><button class="primary" type="button" onclick={() => void saveActive()} disabled={!canWrite || activeBusy || !activeDirty}>{activeState.saving ? 'Сохраняю…' : 'Сохранить'}</button><button type="button" onclick={() => void discardTaskDraft(activeState.taskId)} disabled={!activeDirty || activeBusy}>Отменить изменения</button>{/if}</div></footer>{/if}
	</section>
</div>

<style>
	.workspace { position: relative; width: 100%; height: 100%; min-height: 0; display: grid; grid-template-columns: minmax(245px, 285px) minmax(0, 1fr); overflow: hidden; color: #dce3ed; background: #171c23; border: 1px solid #303946; border-radius: 8px; }
	.mobile-toolbar { display: none; }
	.explorer { min-width: 0; min-height: 0; overflow: auto; background: #1a2029; border-right: 1px solid #303946; }
	.explorer-head { height: 57px; display: flex; align-items: center; justify-content: space-between; padding: 0 14px; border-bottom: 1px solid #303946; }
	.explorer-head div { display: grid; gap: 1px; }.explorer-head small { color: #8390a2; font-size: 9px; letter-spacing: .1em; }.explorer-head strong { font-size: 12px; }
	.icon, .file-meta button { padding: 3px 8px; color: #96a4b6; background: transparent; border: 0; font-size: 17px; }
	.search { display: flex; align-items: center; gap: 7px; margin: 10px; padding: 4px 8px; border: 1px solid #354151; border-radius: 5px; color: #8794a6; }.search input { min-width: 0; flex: 1; padding: 3px 0; border: 0; outline: 0; background: transparent; color: #dce3ed; font-size: 11px; }.search kbd,.welcome kbd { color: #8491a2; border: 1px solid #3c4755; border-radius: 3px; padding: 1px 4px; font: 10px inherit; }
	.tree,.tree ul { list-style: none; margin: 0; padding: 0; }.tree ul { padding-left: 13px; }.tree-row { width: 100%; min-width: 0; display: flex; align-items: center; gap: 6px; padding: 5px 10px; border: 0; border-radius: 0; text-align: left; background: transparent; color: #c5cfdd; font-size: 11px; }.tree-row:hover,.tree-row.current { background: #273344; }.tree-row.project { font-weight: 600; }.tree-row.folder { color: #aab6c6; }.chevron { flex: 0 0 10px; color: #748295; text-align: center; }.node-icon { flex: 0 0 14px; color: #8ba6cb; }.task-icon { color: #d4b879; }.node-label { min-width: 0; flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }.node-label small { display: block; overflow: hidden; color: #8390a2; text-overflow: ellipsis; white-space: nowrap; font-size: 9px; }.node-label strong { font-weight: 500; }.files { border-left: 1px solid #303946; margin-left: 17px!important; }.tree-row.file { gap: 7px; color: #aab5c4; font-size: 10px; padding-top: 4px; padding-bottom: 4px; }.file-icon { width: 16px; text-align: center; color: #98acd0; font-size: 9px; }.opened-dot,.dirty-dot { color: #e7b666; font-size: 9px; }
	.tree-state { padding: 18px 13px; color: #8d99aa; font-size: 11px; }.tree-state.error { display: grid; gap: 10px; color: #ffb4bb; }
	.editor-area { min-width: 0; min-height: 0; display: flex; flex-direction: column; background: #171c23; }.tabs { height: 38px; flex: 0 0 38px; display: flex; overflow-x: auto; background: #1b212a; border-bottom: 1px solid #303946; }.tab-wrap { display: flex; flex: 0 0 auto; align-items: center; border-right: 1px solid #303946; }.tab { height: 37px; max-width: 245px; display: flex; gap: 8px; align-items: center; padding: 0 10px; border: 0; border-radius: 0; background: transparent; color: #9ba7b8; font-size: 10px; }.tab.active { color: #edf2f9; background: #242c37; box-shadow: inset 0 1px #8baee0; }.tab-name { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }.tab-dirty { color: #e7b666; font-size: 9px; }.tab-close { padding: 2px 7px; border: 0; background: transparent; color: #7f8b9a; }.editor-canvas { position: relative; flex: 1; min-height: 0; display: flex; overflow: hidden; }.welcome,.center-state { min-height: 0; flex: 1; display: flex; flex-direction: column; justify-content: center; align-items: center; gap: 12px; padding: 26px; text-align: center; color: #8d99aa; font-size: 12px; }.welcome h2 { margin: 0; color: #cbd5e2; font-size: 15px; }.welcome p { max-width: 350px; margin: 0; }.welcome-mark { display: grid; place-items: center; width: 42px; height: 42px; border: 1px solid #3a4656; border-radius: 12px; color: #a8c5f0; font-size: 22px; }
	.file-header { min-height: 54px; display: flex; justify-content: space-between; align-items: center; gap: 14px; padding: 8px 15px; border-bottom: 1px solid #303946; }.file-title { min-width: 0; }.file-title small { color: #8390a2; font-size: 9px; }.file-title h2 { overflow: hidden; margin: 1px 0 0; color: #cbd5e2; font-size: 11px; font-weight: 500; text-overflow: ellipsis; white-space: nowrap; }.file-meta { display: flex; align-items: center; gap: 9px; color: #97a3b4; font-size: 10px; white-space: nowrap; }.unsaved { color: #e7b666; }.banner { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin: 8px 12px 0; padding: 7px 9px; border: 1px solid #47566b; border-radius: 4px; color: #a9bfdc; font-size: 10px; }.banner.conflict { border-color: #b66d67; color: #ffc1ba; }.banner.proposal { border-color: #6382a8; }.banner button { flex: 0 0 auto; padding: 4px 7px; font-size: 10px; }.notice,.inline-error,.result { margin: 5px 13px 0; font-size: 10px; }.notice { color: #9ab8df; }.inline-error { color: #ff9696; }.result { color: #86d5ae; }.monaco-host { width: 100%; height: 100%; min-height: 0; flex: 1; overflow: hidden; }.monaco-host[hidden] { display: none; }.editor-footer { display: flex; align-items: center; gap: 8px; min-height: 41px; padding: 5px 10px; background: #1c232c; border-top: 1px solid #303946; font-size: 9px; color: #91a0b3; }.path-label { min-width: 0; flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }.footer-right { white-space: nowrap; }.actions { display: flex; gap: 5px; }.actions button { padding: 4px 7px; font-size: 9px; white-space: nowrap; }.actions .primary { background: #aac9fb; color: #13223b; border-color: #aac9fb; }
	@media (max-width: 900px) { .workspace { grid-template-columns: 220px minmax(0,1fr); } .footer-right { display: none; } }
	@media (max-width: 650px) { .workspace { display: flex; flex-direction: column; }.mobile-toolbar { z-index: 31; height: 40px; flex: 0 0 40px; display: flex; align-items: center; gap: 10px; padding: 4px 8px; background: #1c232c; border-bottom: 1px solid #303946; }.mobile-toolbar button { padding: 4px 10px; font-size: 11px; }.mobile-toolbar span { overflow: hidden; color: #91a0b3; font-size: 10px; text-overflow: ellipsis; white-space: nowrap; }.explorer { display: none; position: absolute; inset: 40px 0 0; z-index: 30; width: 100%; border-right: 0; box-shadow: 10px 0 35px #0009; }.explorer.mobile-open { display: block; }.editor-area { flex: 1; }.tree-row { padding-left: 10px; padding-right: 10px; }.tree ul { padding-left: 13px; }.file-header { align-items: flex-start; }.file-meta { gap: 4px; }.editor-footer { flex-wrap: wrap; }.path-label { flex-basis: 100%; }.actions { width: 100%; justify-content: flex-end; flex-wrap: wrap; }.banner { align-items: flex-start; flex-direction: column; } }
</style>
