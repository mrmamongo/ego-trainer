<script lang="ts">
    import { taskViewData, checkResult } from './shared/store';
    import { postToHost } from './shared/api';
    import ResultsBody from './ResultsBody.svelte';
    import type { TaskHint, CheckResult } from './shared/types';
    let revealedLevels = $state<number[]>([]);
    let tab = $state<'statement' | 'results'>('statement');
    let previousId = '', previousResult: CheckResult | null = null;
    $effect(() => {
        const id = $taskViewData?.id || '';
        if (id !== previousId) { previousId = id; revealedLevels = []; tab = 'statement'; previousResult = null; }
    });
    $effect(() => {
        const result = $checkResult;
        if (result && result !== previousResult && result.task_id.toUpperCase() === $taskViewData?.id.toUpperCase()) {
            previousResult = result; tab = 'results';
        }
    });
    const HINT_LEVELS = [1, 2, 3] as const;
    function hintForLevel(hints: TaskHint[], level: number) { return hints.find(h => h.level === level); }
    function canRevealHint(hints: TaskHint[], level: number) {
        return !!hintForLevel(hints, level) && HINT_LEVELS.filter(previous => previous < level && hintForLevel(hints, previous))
            .every(previous => revealedLevels.includes(previous));
    }
    function revealHint(level: number) { if (!revealedLevels.includes(level)) revealedLevels = [...revealedLevels, level]; }
    function statusLabel(status: string) {
        return ({new:'Не начато',passed:'Пройдено',partial:'Частично',failed:'Есть ошибки',error:'Ошибка',timeout:'Таймаут'} as Record<string,string>)[status] || status;
    }
    function taskTitle(id: string, title: string) {
        return title.toUpperCase().startsWith(id.toUpperCase())
            ? title.slice(id.length).trim().replace(/^[:·—-]\s*/, '') || title : title;
    }
</script>

<main class="task-view">
    {#if !$taskViewData}
        <div class="empty"><span aria-hidden="true">⌘</span><h1>Выбери задачу</h1>
            <p>Открой задачу в списке выше или её Python файл. Здесь появятся условие, подсказки и результаты.</p></div>
    {:else}
        {@const data = $taskViewData}
        <header>
            <div class="meta"><span class="task-id">{data.id}</span><span class="status" data-status={data.status}>{statusLabel(data.status)}</span>
                {#if data.mode === 'offline' && !data.loading}<span class="offline" title="Локальная проверка">Локально</span>{/if}</div>
            <h1>{taskTitle(data.id, data.title)}</h1>
            <div class="toolbar"><button class="primary" disabled={data.loading} onclick={() => postToHost({type:'taskView.check',taskId:data.id})}>▶ Проверить</button>
                <button onclick={() => postToHost({type:'taskView.openPy',taskId:data.id})}>Открыть код</button>
                {#if data.ai_available}<button title="Обсудить решение справа" onclick={() => postToHost({type:'taskView.assistant',taskId:data.id})}>✦ Чат</button>{/if}
            </div>
            <nav aria-label="Раздел задания"><button class:active={tab === 'statement'} aria-pressed={tab === 'statement'} onclick={() => tab='statement'}>Условие</button>
                <button class:active={tab === 'results'} aria-pressed={tab === 'results'} onclick={() => tab='results'}>Проверка
                    {#if $checkResult}<span class="score">{$checkResult.passed_tests}/{$checkResult.total_tests}</span>{/if}</button>
            </nav>
        </header>
        {#if data.loading}<p class="loading" aria-live="polite">Загружаю {data.id}…</p>
        {:else if tab === 'statement'}
            <section class="statement" aria-label="Условие">{@html data.statement_html}</section>
            {#if data.hints.length}
                <details class="hints"><summary>Подсказки <span>Открывай постепенно</span></summary>
                    <div class="hint-actions">
                        {#each HINT_LEVELS as level}
                            {@const hint = hintForLevel(data.hints, level)}
                            {#if hint}
                                <button class:revealed={revealedLevels.includes(level)} disabled={!canRevealHint(data.hints, level)}
                                    title={hint.title} onclick={() => revealHint(level)}>
                                    {revealedLevels.includes(level) ? '✓' : level > 1 && !canRevealHint(data.hints, level) ? '◇' : level} Подсказка {level}
                                </button>
                            {/if}
                        {/each}
                    </div>
                    {#each revealedLevels as level}
                        {@const hint = hintForLevel(data.hints, level)}
                        {#if hint}<article class="hint"><h3>{hint.title}</h3><div class="statement">{@html hint.content}</div></article>{/if}
                    {/each}
                </details>
            {/if}
            <p class="version">Версия {data.version} · {data.id}</p>
        {:else}
            <section class="results" aria-label="Результаты проверки">
                <ResultsBody result={$checkResult} history={data.history} emptyMessage="Нажми «Проверить», чтобы увидеть результаты." />
            </section>
        {/if}
    {/if}
</main>

<style>
    :global(html),:global(body) { margin:0; height:100%; font-family:var(--vscode-font-family,system-ui,sans-serif); font-size:var(--vscode-font-size,13px); color:var(--vscode-foreground); background:var(--vscode-sideBar-background,var(--vscode-editor-background)); }
    :global(*) { box-sizing:border-box; } .task-view { padding:0 14px 18px; line-height:1.6; }
    header { position:sticky; top:0; z-index:1; background:var(--vscode-sideBar-background,var(--vscode-editor-background)); padding-top:14px; }
    .meta { display:flex; align-items:center; flex-wrap:wrap; gap:8px; font-size:10px; }
    .task-id { font:600 11px var(--vscode-editor-font-family,monospace); color:var(--vscode-textLink-foreground,#3794ff); }
    .status { color:var(--vscode-descriptionForeground); } .status[data-status='passed'] { color:var(--vscode-testing-iconPassed,#73c991); }
    .status[data-status='failed'],.status[data-status='error'] { color:var(--vscode-errorForeground,#f48771); } .offline { margin-left:auto; color:var(--vscode-descriptionForeground); }
    h1 { font-size:17px; line-height:1.35; font-weight:600; margin:9px 0 14px; overflow-wrap:anywhere; }
    .toolbar { display:flex; flex-wrap:wrap; gap:6px; } button { cursor:pointer; font:inherit; font-size:11px; border:1px solid var(--vscode-panel-border,#444); border-radius:5px; padding:7px 9px; background:transparent; color:var(--vscode-foreground); }
    button:disabled { opacity:.45; cursor:default; } button:hover:not(:disabled) { background:var(--vscode-list-hoverBackground); } button:focus-visible,summary:focus-visible { outline:1px solid var(--vscode-focusBorder); outline-offset:2px; }
    button.primary { background:var(--vscode-button-background,#007acc); color:var(--vscode-button-foreground,#fff); border-color:transparent; } button.primary:hover { background:var(--vscode-button-hoverBackground); }
    nav { display:flex; gap:14px; margin-top:14px; border-bottom:1px solid var(--vscode-panel-border,#333); }
    nav button { border:0; border-bottom:2px solid transparent; border-radius:0; padding:8px 1px; color:var(--vscode-descriptionForeground); }
    nav button.active { color:var(--vscode-foreground); border-bottom-color:var(--vscode-focusBorder,#3794ff); }
    .score { background:var(--vscode-badge-background); color:var(--vscode-badge-foreground); border-radius:8px; padding:1px 5px; font-size:10px; margin-left:4px; }
    .statement { margin:14px 0; overflow-wrap:anywhere; } .statement :global(h1),.statement :global(h2),.statement :global(h3) { font-size:14px; line-height:1.4; margin:20px 0 8px; font-weight:600; }
    .statement :global(p) { margin:8px 0; } .statement :global(ul),.statement :global(ol) { padding-left:20px; margin:8px 0; } .statement :global(li) { margin:5px 0; }
    .statement :global(pre) { padding:12px; background:var(--vscode-textCodeBlock-background,#202020); border:1px solid var(--vscode-panel-border,#333); border-radius:6px; overflow:auto; line-height:1.55; font-size:12px; }
    .statement :global(code) { font-family:var(--vscode-editor-font-family,monospace); font-size:12px; } .statement :global(:not(pre)>code) { padding:1px 4px; border-radius:3px; background:var(--vscode-textCodeBlock-background); color:var(--vscode-textPreformat-foreground); }
    .statement :global(a) { color:var(--vscode-textLink-foreground); }
    .statement :global(.tok-kw) { color:var(--vscode-symbolIcon-keywordForeground,#c586c0); } .statement :global(.tok-string) { color:var(--vscode-symbolIcon-stringForeground,#ce9178); }
    .statement :global(.tok-comment) { color:var(--vscode-descriptionForeground,#6a9955); } .statement :global(.tok-num) { color:var(--vscode-symbolIcon-numberForeground,#b5cea8); }
    .hints { border-top:1px solid var(--vscode-panel-border,#333); padding-top:12px; margin-top:18px; } summary { cursor:pointer; font-size:12px; font-weight:600; } summary>span { display:block; font-weight:400; font-size:10px; color:var(--vscode-descriptionForeground); margin:3px 0 0 14px; }
    .hint-actions { display:flex; flex-wrap:wrap; gap:6px; margin:12px 0; } .hint-actions button { font-size:10px; } .hint-actions .revealed { border-color:var(--vscode-focusBorder); }
    .hint { border-left:2px solid var(--vscode-focusBorder); padding:1px 0 1px 12px; margin:12px 0; } .hint h3 { font-size:12px; margin:8px 0; } .hint .statement { margin:0; }
    .version { font-size:10px; color:var(--vscode-descriptionForeground); margin-top:20px; } .results { margin:16px 0; } .loading { color:var(--vscode-descriptionForeground); }
    .empty { padding-top:30px; } .empty>span { color:var(--vscode-textLink-foreground); font-size:28px; } .empty p { font-size:12px; color:var(--vscode-descriptionForeground); }
    @media(max-width:280px) { .task-view { padding-left:10px; padding-right:10px; } .toolbar button { flex-grow:1; } }
</style>
