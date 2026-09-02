<script lang="ts">
	import { onMount } from 'svelte';
	import { getCatalog, type CatalogDTO, type CatalogProjectDTO, type CatalogTaskDTO } from '../api';

	let {
		onSelectTask,
	}: { onSelectTask: (task: CatalogTaskDTO) => void } = $props();

	let catalog = $state<CatalogDTO | null>(null);
	let loading = $state(true);
	let error = $state('');
	let query = $state('');
	let activeQuery = $state('');
	let debounce: ReturnType<typeof setTimeout> | null = null;

	async function load(q: string) {
		loading = true;
		error = '';
		try {
			catalog = await getCatalog(q);
			activeQuery = q;
		} catch (e) {
			error = (e as Error).message;
		} finally {
			loading = false;
		}
	}

	function onInput(e: Event) {
		query = (e.target as HTMLInputElement).value;
		if (debounce) clearTimeout(debounce);
		debounce = setTimeout(() => load(query), 250);
	}

	function clearSearch() {
		query = '';
		load('');
	}

	function taskCount(p: CatalogProjectDTO): number {
		return p.folders.reduce((n, f) => n + f.tasks.length, 0);
	}

	function totalTasks(): number {
		if (!catalog) return 0;
		return catalog.projects.reduce((n, p) => n + taskCount(p), 0);
	}

	onMount(() => { load(''); });
</script>

<div class="section">
	<div class="section-header">
		<h2>Catalog</h2>
		<button class="btn" type="button" onclick={() => load(query)} disabled={loading} aria-label="Refresh catalog">
			{loading ? 'Refreshing…' : 'Refresh'}
		</button>
	</div>

	<div class="search">
		<input
			type="search"
			value={query}
			oninput={onInput}
			placeholder="Search projects, folders, tasks…"
			aria-label="Search catalog"
		/>
		{#if query}
			<button class="btn" type="button" onclick={clearSearch} aria-label="Clear search">Clear</button>
		{/if}
	</div>

	{#if loading && !catalog}
		<div class="loading">Loading catalog…</div>
	{:else if error}
		<div class="error">{error}</div>
	{:else if catalog && catalog.projects.length === 0}
		<div class="empty">{activeQuery ? `No matches for "${activeQuery}"` : 'Catalog is empty — run a sync to populate.'}</div>
	{:else if catalog}
		<p class="count">
			{catalog.projects.length} project{catalog.projects.length === 1 ? '' : 's'}
			· {totalTasks()} task{totalTasks() === 1 ? '' : 's'}
			{#if activeQuery}<span class="filtered"> · filtered by "{activeQuery}"</span>{/if}
		</p>

		<ul class="tree">
			{#each catalog.projects as p (p.id)}
				<li class="project">
					<div class="node project-node">
						<span class="caret">▾</span>
						<span class="name">{p.name || p.id}</span>
						<span class="meta">{p.id} · v{p.version}</span>
						<span class="badge">{taskCount(p)} task{taskCount(p) === 1 ? '' : 's'}</span>
					</div>
					<ul class="sub">
						{#each p.folders as f (f.id)}
							<li class="folder">
								<div class="node folder-node">
									<span class="caret">▾</span>
									<span class="name">{f.name || f.code}</span>
									<span class="meta">{f.code}{f.level ? ` · ${f.level}` : ''}</span>
									<span class="badge">{f.tasks.length}</span>
								</div>
								<ul class="sub">
									{#each f.tasks as t (t.id)}
										<li class="task">
											<button
												class="node task-node"
												type="button"
												onclick={() => onSelectTask(t)}
												aria-label={`Open task ${t.task_id}: ${t.title}`}
											>
												<span class="task-id">{t.task_id}</span>
												<span class="task-title">{t.title || t.slug}</span>
												<span class="task-tags">
													{#if t.block}<span class="tag">{t.block}</span>{/if}
													{#if t.level}<span class="tag">{t.level}</span>{/if}
													{#if t.breaking}<span class="tag warn">breaking</span>{/if}
													<span class="tag">v{t.version}</span>
												</span>
											</button>
										</li>
									{/each}
								</ul>
							</li>
						{/each}
					</ul>
				</li>
			{/each}
		</ul>
	{/if}
</div>

<style>
	.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
	h2 { font-size: 0.9rem; font-weight: 600; }
	.btn {
		padding: 4px 12px; background: transparent; border: 1px solid #3c3c3c; border-radius: 4px;
		color: #d4d4d4; font-family: inherit; font-size: 0.8rem; cursor: pointer;
	}
	.btn:hover:not(:disabled) { border-color: #007acc; }
	.btn:disabled { opacity: 0.5; cursor: not-allowed; }

	.search { display: flex; gap: 8px; margin-bottom: 14px; }
	.search input {
		flex: 1; padding: 6px 10px; background: #2d2d2d; border: 1px solid #3c3c3c; border-radius: 4px;
		color: #d4d4d4; font-family: inherit; font-size: 0.8rem;
	}
	.search input:focus { outline: none; border-color: #007acc; }

	.count { font-size: 0.75rem; color: #858585; margin: 0 0 12px; }
	.filtered { color: #007acc; }

	.tree, .sub { list-style: none; margin: 0; padding: 0; }
	.sub { padding-left: 20px; border-left: 1px solid #3c3c3c; margin-left: 8px; }
	.project > .sub, .folder > .sub { margin-top: 2px; }

	.node { display: flex; align-items: center; gap: 8px; padding: 4px 8px; border-radius: 4px; }
	.project-node { font-weight: 600; }
	.folder-node { color: #d4d4d4; }
	.task-node {
		width: 100%; text-align: left; background: transparent; border: 1px solid transparent;
		color: #d4d4d4; font-family: inherit; font-size: 0.8rem; cursor: pointer;
	}
	.task-node:hover { background: rgba(0,122,204,0.08); border-color: #3c3c3c; }

	.caret { color: #858585; width: 12px; font-size: 0.7rem; }
	.name { flex: 0 1 auto; }
	.meta { color: #858585; font-size: 0.7rem; }
	.badge {
		margin-left: auto; padding: 1px 8px; border: 1px solid #3c3c3c; border-radius: 10px;
		font-size: 0.7rem; color: #858585;
	}

	.task-id { color: #007acc; font-family: inherit; flex: 0 0 auto; }
	.task-title { flex: 1 1 auto; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
	.task-tags { display: inline-flex; gap: 4px; flex: 0 0 auto; }
	.tag {
		padding: 0 6px; border: 1px solid #3c3c3c; border-radius: 3px; font-size: 0.65rem; color: #858585;
	}
	.tag.warn { color: #eab308; border-color: #eab308; }

	.loading, .empty, .error { padding: 24px; text-align: center; color: #858585; }
	.error { color: #f87171; }

	@media (max-width: 600px) {
		.sub { padding-left: 12px; }
		.task-title { white-space: normal; }
	}
</style>
