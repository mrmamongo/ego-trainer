<script lang="ts">
	import { onMount } from 'svelte';
	import {
		getTaskStudio,
		validateTaskStudio,
		saveTaskStudio,
		type TaskStudioDTO,
		type StudioValidateResponse,
		type StudioSaveResponse,
	} from '../api';

	type Tab = 'statement' | 'solution' | 'tests';

	let {
		taskId,
		taskLabel,
		role,
		onBack,
	}: {
		taskId: string;
		taskLabel: string;
		role: string;
		onBack: () => void;
	} = $props();

	// admin-only role may edit/validate/save; mentor is browse-only.
	const canEdit = $derived(role === 'admin');

	let studio = $state<TaskStudioDTO | null>(null);
	let loading = $state(true);
	let loadError = $state('');

	// editor buffers (kept separate from loaded server state to detect dirty)
	let mdBuffer = $state('');
	let solBuffer = $state('');
	let testsBuffer = $state('');
	let expectedVersion = $state('');

	let activeTab = $state<Tab>('statement');

	let validating = $state(false);
	let validateError = $state('');
	let validateResult = $state<StudioValidateResponse | null>(null);

	let saving = $state(false);
	let saveError = $state('');
	let saveResult = $state<StudioSaveResponse | null>(null);

	let notice = $state(''); // generic transient status (e.g. reloaded)

	function isDirty(): boolean {
		if (!studio) return false;
		return (
			mdBuffer !== studio.markdown ||
			solBuffer !== studio.solution_py ||
			testsBuffer !== studio.tests_py
		);
	}

	// writable gate: backend writable=false OR mentor role → read-only
	const editable = $derived(!!studio && studio.writable && canEdit);

	async function load() {
		loading = true;
		loadError = '';
		validateResult = null;
		validateError = '';
		saveResult = null;
		saveError = '';
		notice = '';
		try {
			const data = await getTaskStudio(taskId);
			studio = data;
			mdBuffer = data.markdown;
			solBuffer = data.solution_py;
			testsBuffer = data.tests_py;
			expectedVersion = data.version;
		} catch (e) {
			studio = null;
			loadError = (e as Error).message;
		} finally {
			loading = false;
		}
	}

	function resetBuffers() {
		if (!studio) return;
		mdBuffer = studio.markdown;
		solBuffer = studio.solution_py;
		testsBuffer = studio.tests_py;
		expectedVersion = studio.version;
		validateResult = null;
		validateError = '';
		saveResult = null;
		saveError = '';
		notice = 'Reverted to server state';
	}

	function selectTab(tab: Tab) {
		activeTab = tab;
	}

	async function doValidate() {
		if (!editable || !studio) return;
		validating = true;
		validateError = '';
		validateResult = null;
		notice = '';
		try {
			const res = await validateTaskStudio(taskId, {
				expected_version: expectedVersion,
				markdown: mdBuffer,
				solution_py: solBuffer,
				tests_py: testsBuffer,
			});
			validateResult = res;
		} catch (e) {
			validateError = (e as Error).message;
		} finally {
			validating = false;
		}
	}

	async function doSave() {
		if (!editable || !studio) return;
		saving = true;
		saveError = '';
		saveResult = null;
		validateResult = null;
		validateError = '';
		notice = '';
		try {
			const res = await saveTaskStudio(taskId, {
				expected_version: expectedVersion,
				markdown: mdBuffer,
				solution_py: solBuffer,
				tests_py: testsBuffer,
			});
			saveResult = res;
			// reload server state + update expected version to the new version
			await load();
			expectedVersion = res.new_version;
			notice = `Saved (v${res.new_version}) — reloaded from server`;
		} catch (e) {
			saveError = (e as Error).message;
		} finally {
			saving = false;
		}
	}

	onMount(() => { load(); });
</script>

<div class="section">
	<div class="section-header">
		<button class="btn back" type="button" onclick={onBack} aria-label="Back to Catalog">← Catalog</button>
		<h2>Task Studio</h2>
		<button class="btn" type="button" onclick={load} disabled={loading} aria-label="Reload task studio">
			{loading ? 'Reloading…' : 'Reload'}
		</button>
	</div>

	{#if loading && !studio}
		<div class="loading">Loading task studio…</div>
	{:else if loadError}
		<div class="error">{loadError}</div>
		<button class="btn" type="button" onclick={load} aria-label="Retry loading">Retry</button>
	{:else if studio}
		<dl class="meta">
			<div><dt>Task</dt><dd><strong>{taskLabel || studio.task_id}</strong></dd></div>
			<div><dt>ID</dt><dd><code>{taskId}</code></dd></div>
			<div><dt>Version</dt><dd><code>v{studio.version}</code>{#if isDirty()} <span class="dirty" title="Unsaved changes">● dirty</span>{/if}</dd></div>
			<div><dt>Canonical path</dt><dd><code>{studio.md_path || '—'}</code></dd></div>
		</dl>

		{#if !studio.writable}
			<div class="readonly-banner" role="alert">
				Read-only: {studio.read_only_reason || 'content repo is not writable'}
			</div>
		{:else if !canEdit}
			<div class="readonly-banner" role="alert">
				Browse-only: mentors may view but not edit task content.
			</div>
		{/if}

		<div class="tabs" role="tablist" aria-label="Task content">
			<button
				role="tab"
				id="tab-statement"
				aria-selected={activeTab === 'statement'}
				aria-controls="panel-statement"
				class:active={activeTab === 'statement'}
				onclick={() => selectTab('statement')}
				type="button"
			>Statement Markdown</button>
			<button
				role="tab"
				id="tab-solution"
				aria-selected={activeTab === 'solution'}
				aria-controls="panel-solution"
				class:active={activeTab === 'solution'}
				onclick={() => selectTab('solution')}
				type="button"
			>Reference Solution</button>
			<button
				role="tab"
				id="tab-tests"
				aria-selected={activeTab === 'tests'}
				aria-controls="panel-tests"
				class:active={activeTab === 'tests'}
				onclick={() => selectTab('tests')}
				type="button"
			>Tests</button>
		</div>

		<div
			id="panel-statement"
			role="tabpanel"
			aria-labelledby="tab-statement"
			hidden={activeTab !== 'statement'}
		>
			<textarea
				class="editor"
				spellcheck="false"
				wrap="off"
				value={mdBuffer}
				oninput={(e) => (mdBuffer = (e.target as HTMLTextAreaElement).value)}
				disabled={!editable}
				aria-label="Statement markdown (full, including frontmatter)"
			></textarea>
		</div>
		<div
			id="panel-solution"
			role="tabpanel"
			aria-labelledby="tab-solution"
			hidden={activeTab !== 'solution'}
		>
			<textarea
				class="editor"
				spellcheck="false"
				wrap="off"
				value={solBuffer}
				oninput={(e) => (solBuffer = (e.target as HTMLTextAreaElement).value)}
				disabled={!editable}
				aria-label="Reference solution Python"
			></textarea>
		</div>
		<div
			id="panel-tests"
			role="tabpanel"
			aria-labelledby="tab-tests"
			hidden={activeTab !== 'tests'}
		>
			<textarea
				class="editor"
				spellcheck="false"
				wrap="off"
				value={testsBuffer}
				oninput={(e) => (testsBuffer = (e.target as HTMLTextAreaElement).value)}
				disabled={!editable}
				aria-label="Tests Python"
			></textarea>
		</div>

		{#if notice}<p class="notice" role="status" aria-live="polite">{notice}</p>{/if}
		{#if validateError}<p class="error" role="alert">Validate failed: {validateError}</p>{/if}
		{#if saveError}<p class="error" role="alert">Save failed: {saveError}</p>{/if}
		{#if validateResult}
			<p class="success" role="status">
				Valid ✓ — task {validateResult.task_id},
				current v{validateResult.current_version},
				candidate v{validateResult.candidate_version},
				{validateResult.content_changed ? 'content changed' : 'no content change'},
				policy: {validateResult.version_policy}
			</p>
		{/if}
		{#if saveResult}
			<p class="success" role="status">
				Saved ✓ — task {saveResult.task_id}, new version v{saveResult.new_version},
				sync: {saveResult.sync.status}
				(+{saveResult.sync.added}/~{saveResult.sync.updated}/={saveResult.sync.skipped},
				{saveResult.sync.errors} error{saveResult.sync.errors === 1 ? '' : 's'})
			</p>
		{/if}

		<div class="actions">
			{#if canEdit}
				<button
					class="btn primary"
					type="button"
					onclick={doValidate}
					disabled={!editable || validating || saving || !isDirty()}
					aria-label="Validate candidate"
				>{validating ? 'Validating…' : 'Validate'}</button>
				<button
					class="btn primary"
					type="button"
					onclick={doSave}
					disabled={!editable || saving || validating || !isDirty()}
					aria-label="Save candidate to canonical files"
				>{saving ? 'Saving…' : 'Save'}</button>
				<button
					class="btn"
					type="button"
					onclick={resetBuffers}
					disabled={!editable || saving || validating || !isDirty()}
					aria-label="Revert to server state"
				>Revert</button>
			{:else}
			<span class="hint">Mentor role: browse-only. No write actions available.</span>
			{/if}
		</div>
	{/if}
</div>

<style>
	.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; gap: 8px; }
	h2 { font-size: 0.9rem; font-weight: 600; }
	.btn {
		padding: 4px 12px; background: transparent; border: 1px solid #3c3c3c; border-radius: 4px;
		color: #d4d4d4; font-family: inherit; font-size: 0.8rem; cursor: pointer;
	}
	.btn:hover:not(:disabled) { border-color: #007acc; }
	.btn:disabled { opacity: 0.5; cursor: not-allowed; }
	.btn.primary { border-color: #007acc; color: #007acc; }
	.btn.primary:hover:not(:disabled) { background: rgba(0,122,204,0.12); }
	.btn.back { border-color: transparent; color: #858585; }
	.btn.back:hover:not(:disabled) { color: #d4d4d4; }

	.meta {
		display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
		gap: 8px 16px; margin: 0 0 12px; padding: 12px; background: #2d2d2d;
		border: 1px solid #3c3c3c; border-radius: 6px;
	}
	.meta div { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
	.meta dt { font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.05em; color: #858585; }
	.meta dd { margin: 0; font-size: 0.8rem; word-break: break-all; }
	.meta code { font-family: inherit; color: #d4d4d4; }
	.dirty { color: #eab308; font-size: 0.7rem; }

	.readonly-banner {
		padding: 8px 12px; margin-bottom: 12px; background: rgba(234,179,8,0.08);
		border: 1px solid #eab308; border-radius: 4px; color: #eab308; font-size: 0.8rem;
	}

	.tabs { display: flex; gap: 2px; border-bottom: 1px solid #3c3c3c; margin-bottom: 0; }
	.tabs button {
		padding: 6px 14px; background: transparent; border: 1px solid transparent; border-bottom: none;
		border-radius: 4px 4px 0 0; color: #858585; font-family: inherit; font-size: 0.8rem; cursor: pointer;
	}
	.tabs button:hover { color: #d4d4d4; }
	.tabs button.active { color: #d4d4d4; background: #2d2d2d; border-color: #3c3c3c; }
	.tabs button[aria-selected="true"] { color: #d4d4d4; }

	div[role="tabpanel"] { margin: 0; }

	.editor {
		width: 100%; min-height: 420px; box-sizing: border-box; resize: vertical;
		padding: 12px; background: #1e1e1e; border: 1px solid #3c3c3c; border-radius: 0 4px 4px 4px;
		color: #d4d4d4; font-family: 'JetBrains Mono', 'Cascadia Code', 'Fira Code', 'Consolas', monospace;
		font-size: 0.8rem; line-height: 1.5; white-space: pre; overflow: auto;
	}
	.editor:focus { outline: none; border-color: #007acc; }
	.editor:disabled { opacity: 0.85; cursor: not-allowed; background: #252525; }

	.actions { display: flex; gap: 8px; margin-top: 12px; flex-wrap: wrap; align-items: center; }
	.hint { color: #858585; font-size: 0.75rem; }

	.notice { color: #858585; font-size: 0.75rem; margin: 12px 0 0; }
	.success { color: #4ade80; font-size: 0.78rem; margin: 12px 0 0; word-break: break-word; }
	.error { color: #f87171; font-size: 0.78rem; margin: 12px 0 0; word-break: break-word; }
	.loading { padding: 24px; text-align: center; color: #858585; }

	@media (max-width: 600px) {
		.meta { grid-template-columns: 1fr; }
		.tabs button { padding: 6px 10px; font-size: 0.75rem; }
		.editor { min-height: 320px; }
	}
</style>
