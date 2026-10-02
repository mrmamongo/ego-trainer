<script lang="ts">
    import { onMount, tick } from 'svelte';
    import { getVsCodeApi, type ExtMessage } from './shared/api';
    import type { AssistantData } from '../aiTypes';
    const host = getVsCodeApi();
    let data = $state<AssistantData | null>(null);
    let text = $state('');
    let sentText = '', previousTask = '';
    const drafts = new Map<string, string>();
    let messagesElement: HTMLElement;
    const canSend = $derived(!!data?.taskId && !!data?.account?.available && !data.busy
        && (!data.session || data.session.status === 'active'));
    function post(message: ExtMessage) { host.postMessage(message); }
    function sendText(value = text) {
        if (!canSend || !value.trim() || !data) return;
        sentText = value;
        post({ type: 'assistant.send', text: value, taskId: data.taskId });
    }
    function send(event: SubmitEvent) { event.preventDefault(); sendText(); }
    function keydown(event: KeyboardEvent) {
        if (event.key === 'Enter' && !event.shiftKey && !event.isComposing) {
            event.preventDefault(); sendText();
        }
    }
    function money(value: string) {
        return Number(value).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 6 });
    }
    function parts(content: string) {
        const blocks: { code: boolean; content: string; language?: string }[] = [];
        const fence = /```([a-z0-9_-]*)\n([\s\S]*?)```/gi;
        let start = 0, match: RegExpExecArray | null;
        while ((match = fence.exec(content))) {
            if (match.index > start) blocks.push({ code: false, content: content.slice(start, match.index) });
            blocks.push({ code: true, content: match[2].trimEnd(), language: match[1] });
            start = fence.lastIndex;
        }
        if (start < content.length) blocks.push({ code: false, content: content.slice(start) });
        return blocks;
    }
    function statusLabel(status: string) {
        return ({ confirmed: 'Понимание подтверждено', needs_review: 'Нужно ещё немного разобрать решение',
            active: 'Диалог продолжается' } as Record<string, string>)[status] || status;
    }
    $effect(() => {
        data?.session?.messages.length; data?.busy;
        void tick().then(() => { if (messagesElement) messagesElement.scrollTop = messagesElement.scrollHeight; });
    });
    onMount(() => {
        const listener = (event: MessageEvent) => {
            if (event.data?.type !== 'assistant.data') return;
            const next: AssistantData = event.data.payload;
            if (next.taskId !== previousTask) {
                drafts.set(previousTask, text); text = drafts.get(next.taskId) || '';
                previousTask = next.taskId; sentText = '';
            }
            data = next;
            if (sentText && !next.busy && !next.error) { text = ''; sentText = ''; }
        };
        window.addEventListener('message', listener);
        post({ type: 'ready' });
        return () => window.removeEventListener('message', listener);
    });
</script>

<main>
    <header>
        <div class="context">
            <span class="eyebrow">COGITO / АССИСТЕНТ</span>
            <button class="icon" title="Обновить доступ" aria-label="Обновить доступ"
                onclick={() => post({ type: 'assistant.refresh' })} disabled={data?.busy}>↻</button>
        </div>
        <h1>{data?.taskId ? 'Разбираем ' + data.taskId : 'Разберём вместе'}</h1>
        {#if data?.taskId}<p class="file"><span aria-hidden="true">⌘</span> task_{data.taskId.replace(/\./g, '_').toLowerCase()}.py</p>{/if}
        {#if data?.account}
            <div class="account"><span class:available={data.account.available} class="access-dot"></span>
                <span>{data.account.available ? 'Ассистент доступен' : 'Пока недоступен'}</span>
                <span class="balance" title="Доступный бюджет">$&#8202;{money(data.account.balance_usd)}</span>
            </div>
        {/if}
    </header>

    {#if data?.taskId}
        <nav aria-label="Режим ассистента">
            {#each [{id:'hint', label:'Подсказка'}, {id:'explain', label:'Разбор кода'}, {id:'defend', label:'Защита'}] as mode}
                <button class:chosen={(data.session?.mode || 'hint') === mode.id}
                    aria-pressed={(data.session?.mode || 'hint') === mode.id}
                    disabled={!data.account?.available || data.busy || (mode.id === 'defend' && !data.submissionId)}
                    title={mode.id === 'defend' ? 'Проверить понимание после успешных тестов' : mode.label}
                    onclick={() => post({ type:'assistant.start', mode:mode.id as 'hint'|'explain'|'defend', taskId:data!.taskId })}>{mode.label}</button>
            {/each}
        </nav>
    {/if}

    <section class="messages" bind:this={messagesElement} aria-label="Диалог" aria-live="polite">
        {#if !data?.taskId}
            <div class="empty"><span class="mark" aria-hidden="true">✦</span><h2>Код — твой.<br>Разбор — вместе.</h2>
                <p>Открой задачу слева или её Python файл. Я помогу с идеей, объясню код и проверю понимание.</p>
                <button class="secondary" onclick={() => post({ type:'assistant.tasks' })}>Выбрать задачу</button>
            </div>
        {:else if data.offline}
            <div class="notice"><h2>Подключись к Cogito</h2><p>Сейчас ты решаешь задачи локально. Чат появится при подключении к серверу.</p>
                <button class="secondary" onclick={() => post({ type:'assistant.connect' })}>Подключиться</button></div>
        {:else if data.account && !data.account.available}
            <div class="notice"><h2>Помощь пока недоступна</h2><p>{data.account.reason}</p>
                <p class="muted">Наставник управляет доступом и бюджетом. Тесты и подсказки задания доступны отдельно.</p></div>
        {:else if !data.session?.messages.length && !data.busy}
            <div class="empty"><span class="mark" aria-hidden="true">✦</span><h2>Где ты сейчас застрял?</h2>
                <p>Можем наметить первый шаг или разобрать твой код. После тестов — короткая защита решения.</p>
                <div class="suggestions">
                    <button disabled={!canSend} onclick={() => sendText('Помоги понять, с чего начать эту задачу.')}>С чего начать?</button>
                    <button disabled={!canSend} onclick={() => sendText('Помоги разобраться, где ошибка в моём коде.')}>Где ошибка в коде?</button>
                </div>
            </div>
        {/if}
        {#if data?.session}
            {#each data.session.messages as message, i (i)}
                <article class:user={message.role === 'user'}>
                    <div class="speaker"><span class="avatar" aria-hidden="true">{message.role === 'user' ? 'Т' : '✦'}</span>{message.role === 'user' ? 'Ты' : 'Cogito'}</div>
                    {#each parts(message.content) as part}
                        {#if part.code}<div class="code-block"><span>{part.language || 'Код'}</span><pre><code>{part.content}</code></pre></div>
                        {:else}<div class="content">{part.content}</div>{/if}
                    {/each}
                </article>
            {/each}
            {#if data.session.mode === 'defend' || data.session.status !== 'active'}
                <p class="status">{statusLabel(data.session.status)}{data.session.mode === 'defend' ? ' · Проверяем сданное решение' : ''}</p>
            {/if}
        {/if}
        {#if data?.error}<div class="error" role="alert"><p>{data.error}</p>
            {#if !data.account}<button class="secondary" onclick={() => post({type:'assistant.login'})}>Войти в Cogito</button>{/if}
        </div>{/if}
        {#if data?.busy}<p class="thinking" aria-live="polite"><span>●</span> Готовлю ответ…</p>{/if}
    </section>

    <form onsubmit={send} class="composer">
        <label for="message" class="sr-only">Твой вопрос или ответ</label>
        <textarea id="message" bind:value={text} onkeydown={keydown} maxlength="4000" rows="3"
            disabled={!canSend} placeholder={data?.taskId ? 'Спроси о задаче или объясни свой ход мысли…' : 'Сначала выбери задачу…'}></textarea>
        <div class="composer-bottom"><span>Enter ↵ · Shift+Enter — строка</span>
            <button type="submit" class="send" aria-label="Отправить" disabled={!text.trim() || !canSend}>↑</button></div>
        {#if data?.account}<details class="cost"><summary>Бюджет и расходы</summary>
            <p>Остаток ${money(data.account.balance_usd)} · Потрачено ${money(data.account.spent_usd)}</p></details>{/if}
    </form>
</main>

<style>
    :global(html), :global(body) { margin:0; height:100%; font-family:var(--vscode-font-family,system-ui,sans-serif); font-size:var(--vscode-font-size,13px); color:var(--vscode-foreground); background:var(--vscode-sideBar-background,var(--vscode-editor-background)); }
    :global(#app) { height:100%; } :global(*) { box-sizing:border-box; }
    main { height:100%; display:flex; flex-direction:column; overflow:hidden; }
    header { flex:none; padding:16px 16px 12px; border-bottom:1px solid var(--vscode-panel-border,#333); }
    .context,.account { display:flex; align-items:center; gap:7px; } .context { justify-content:space-between; }
    .eyebrow { font-size:10px; letter-spacing:.12em; color:var(--vscode-descriptionForeground); }
    h1 { font-size:18px; font-weight:600; margin:8px 0; } .file { font-family:var(--vscode-editor-font-family,monospace); font-size:11px; color:var(--vscode-descriptionForeground); margin:0 0 12px; overflow-wrap:anywhere; }
    .account { font-size:11px; color:var(--vscode-descriptionForeground); } .balance { margin-left:auto; color:var(--vscode-foreground); font-variant-numeric:tabular-nums; }
    .access-dot { width:6px; height:6px; border-radius:50%; background:var(--vscode-descriptionForeground); } .available { background:var(--vscode-testing-iconPassed,#73c991); }
    button { font:inherit; color:inherit; cursor:pointer; } button:disabled { opacity:.45; cursor:default; } button:focus-visible, textarea:focus { outline:1px solid var(--vscode-focusBorder,#3794ff); outline-offset:2px; }
    .icon { border:0; background:transparent; font-size:20px; line-height:1; padding:2px; color:var(--vscode-descriptionForeground); }
    nav { display:flex; flex:none; padding:12px 14px 0; gap:4px; } nav button { flex:1; min-width:0; font-size:11px; padding:7px 3px; border:1px solid transparent; border-radius:5px; background:transparent; color:var(--vscode-descriptionForeground); }
    nav button.chosen { color:var(--vscode-foreground); background:var(--vscode-list-hoverBackground,#2a2d2e); border-color:var(--vscode-panel-border,#444); }
    .messages { flex:1; min-height:0; overflow:auto; padding:12px 16px; } .empty { padding:28px 0 16px; } .mark { color:var(--vscode-focusBorder,#3794ff); font-size:26px; }
    h2 { font-size:18px; font-weight:500; line-height:1.4; margin:12px 0; } p { line-height:1.6; font-size:12px; } .empty p,.muted { color:var(--vscode-descriptionForeground); }
    .secondary,.suggestions button { background:transparent; border:1px solid var(--vscode-panel-border,#444); border-radius:6px; padding:9px 12px; font-size:12px; }
    .suggestions { display:flex; flex-direction:column; gap:8px; margin-top:20px; } .suggestions button { text-align:left; } .suggestions button:hover:not(:disabled) { background:var(--vscode-list-hoverBackground); }
    .notice { padding:12px 0; } .notice h2 { font-size:15px; } article { padding:14px 0; border-bottom:1px solid color-mix(in srgb,var(--vscode-foreground) 8%,transparent); }
    article.user { background:color-mix(in srgb,var(--vscode-foreground) 3%,transparent); margin:0 -6px; padding:12px 6px; border-radius:6px; }
    .speaker { display:flex; gap:8px; align-items:center; font-size:11px; font-weight:600; margin-bottom:8px; } .avatar { color:var(--vscode-focusBorder,#3794ff); } article.user .avatar { color:var(--vscode-descriptionForeground); }
    .content { white-space:pre-wrap; overflow-wrap:anywhere; line-height:1.65; font-size:13px; } .code-block { margin:12px 0; border:1px solid var(--vscode-panel-border,#444); border-radius:6px; overflow:hidden; }
    .code-block>span { display:block; font-size:10px; color:var(--vscode-descriptionForeground); padding:6px 10px; border-bottom:1px solid var(--vscode-panel-border,#444); }
    pre { margin:0; padding:10px; overflow:auto; background:var(--vscode-textCodeBlock-background); font:12px/1.6 var(--vscode-editor-font-family,monospace); }
    .error { color:var(--vscode-errorForeground); } .status { color:var(--vscode-descriptionForeground); border-left:2px solid var(--vscode-focusBorder); padding-left:10px; }
    .thinking { color:var(--vscode-descriptionForeground); } .thinking span { color:var(--vscode-focusBorder); margin-right:7px; }
    .composer { flex:none; margin:8px 12px 12px; padding:10px; border:1px solid var(--vscode-input-border,var(--vscode-panel-border,#444)); border-radius:9px; background:var(--vscode-input-background); }
    textarea { display:block; width:100%; resize:vertical; min-height:58px; max-height:160px; border:0; background:transparent; color:var(--vscode-input-foreground); font:13px/1.5 var(--vscode-font-family,system-ui,sans-serif); padding:2px; }
    .composer-bottom { display:flex; justify-content:space-between; align-items:center; gap:4px; padding-top:7px; color:var(--vscode-descriptionForeground); font-size:10px; }
    .send { border:0; border-radius:5px; background:var(--vscode-button-background,#007acc); color:var(--vscode-button-foreground,#fff); width:29px; height:29px; font-size:20px; }
    .cost { font-size:10px; color:var(--vscode-descriptionForeground); margin-top:8px; } .cost summary { cursor:pointer; } .cost p { margin:6px 0 0; font-size:11px; }
    .sr-only { position:absolute; width:1px; height:1px; overflow:hidden; clip-path:inset(50%); }
    @media(max-width:280px) { header,.messages { padding-left:10px; padding-right:10px; } .composer-bottom>span { display:none; } nav { padding-left:8px; padding-right:8px; } }
</style>
