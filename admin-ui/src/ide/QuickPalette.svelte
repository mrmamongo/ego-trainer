<script lang="ts">
	import type { PaletteItem } from './paletteItems';

	type Props = {
		open: boolean;
		items: PaletteItem[];
		onSelect: (item: PaletteItem) => void;
		onClose: () => void;
		onQuery: (q: string) => void;
	};

	const { open, items, onSelect, onClose, onQuery }: Props = $props();

	// Локальный запрос сбрасывается при каждом открытии палитры.
	let query = $state('');
	let activeIndex = $state(0);
	let inputEl = $state<HTMLInputElement | null>(null);
	let queryTimer: ReturnType<typeof setTimeout> | undefined;

	$effect(() => {
		if (open) {
			query = '';
			activeIndex = 0;
			onQuery('');
		}
	});

	// Фокус в поле при каждом открытии (автофокус через рендер-цикл ненадёжен).
	$effect(() => {
		if (open && inputEl) {
			inputEl.focus();
		}
	});

	// Родитель владеет фильтрацией — ему уходит только текущий запрос.
	$effect(() => {
		if (!open) return;
		clearTimeout(queryTimer);
		const q = query;
		queryTimer = setTimeout(() => onQuery(q), 80);
		return () => clearTimeout(queryTimer);
	});

	// Активная строка не должна указывать мимо списка.
	$effect(() => {
		if (items.length === 0) {
			activeIndex = 0;
		} else if (activeIndex > items.length - 1) {
			activeIndex = items.length - 1;
		}
	});

	const KIND_ICONS: Record<PaletteItem['kind'], string> = {
		file: '📄',
		task: '🧩',
		command: '⚡',
	};

	function onKeydown(event: KeyboardEvent) {
		if (items.length > 0) {
			if (event.key === 'ArrowDown') {
				event.preventDefault();
				activeIndex = (activeIndex + 1) % items.length;
			} else if (event.key === 'ArrowUp') {
				event.preventDefault();
				activeIndex = (activeIndex - 1 + items.length) % items.length;
			} else if (event.key === 'Enter') {
				event.preventDefault();
				const item = items[activeIndex];
				if (item) onSelect(item);
			}
		}
		if (event.key === 'Escape') {
			event.preventDefault();
			onClose();
		}
	}
</script>

{#if open}
	<!-- svelte-ignore a11y_click_events_have_key_events -->
	<div
		class="qp-overlay"
		role="dialog"
		aria-label="Быстрый поиск"
		tabindex="-1"
		onclick={(e) => { if (e.target === e.currentTarget) onClose(); }}
		onkeydown={onKeydown}
	>
		<div class="qp-card">
			<input
				bind:this={inputEl}
				class="qp-input"
				type="text"
				placeholder="Найти файл, задачу или команду…"
				bind:value={query}
			/>
			{#if items.length === 0}
				{#if query.trim() !== ''}
					<div class="qp-empty">Ничего не найдено</div>
				{/if}
			{:else}
				<ul class="qp-list" role="listbox">
					{#each items as item, i (item.id)}
						<li
							class="qp-row"
							class:qp-active={i === activeIndex}
							role="option"
							aria-selected={i === activeIndex}
							onmouseenter={() => { activeIndex = i; }}
							onclick={() => onSelect(item)}
						>
							<span class="qp-icon" aria-hidden="true">{KIND_ICONS[item.kind]}</span>
							<span class="qp-label">{item.label}</span>
							{#if item.hint}
								<span class="qp-hint">{item.hint}</span>
							{/if}
						</li>
					{/each}
				</ul>
			{/if}
		</div>
	</div>
{/if}

<style>
	.qp-overlay {
		position: fixed;
		inset: 0;
		z-index: 50;
		display: flex;
		justify-content: center;
		align-items: flex-start;
		background: rgba(0, 0, 0, 0.5);
	}

	.qp-card {
		width: 100%;
		max-width: 560px;
		margin-top: 18dvh;
		border: 1px solid var(--border);
		border-radius: 12px;
		background: var(--card);
		color: var(--foreground);
		box-shadow: 0 16px 48px rgba(0, 0, 0, 0.45);
		overflow: hidden;
	}

	.qp-input {
		width: 100%;
		box-sizing: border-box;
		padding: 14px 16px;
		border: none;
		border-bottom: 1px solid var(--border);
		border-radius: 0;
		background: transparent;
		color: var(--foreground);
		font-size: 15px;
		outline: none;
	}

	.qp-input:focus {
		outline: none;
	}

	.qp-list {
		margin: 0;
		padding: 6px;
		list-style: none;
		max-height: 320px;
		overflow-y: auto;
	}

	.qp-row {
		display: flex;
		align-items: center;
		gap: 10px;
		padding: 9px 12px;
		border-radius: 8px;
		cursor: pointer;
		font-size: 14px;
	}

	.qp-active {
		background: var(--secondary);
	}

	.qp-icon {
		flex-shrink: 0;
	}

	.qp-label {
		flex: 1;
		min-width: 0;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.qp-hint {
		flex-shrink: 0;
		color: var(--muted-foreground);
		font-size: 12px;
	}

	.qp-empty {
		padding: 24px 16px;
		text-align: center;
		color: var(--muted-foreground);
		font-size: 14px;
	}
</style>
