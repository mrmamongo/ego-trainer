<script lang="ts">
    import { onMount } from 'svelte';
    import { getVsCodeApi, type ExtMessage } from './shared/api';
    import type { AssistantData } from '../aiTypes';

    const host = getVsCodeApi();
    let data = $state<AssistantData | null>(null);
    let text = $state('');
    let sentText = '';
    function post(message: ExtMessage) { host.postMessage(message); }
    function send(event: SubmitEvent) {
        event.preventDefault();
        if (!text.trim() || data?.busy) return;
        sentText = text;
        post({ type: 'assistant.send', text });
    }
    function label(status: string) {
        return ({ confirmed: 'Понимание подтверждено', needs_review: 'Есть пробел: нужен повторный разбор',
            active: 'Диалог продолжается' } as Record<string, string>)[status] || status;
    }
    onMount(() => {
        const listener = (event: MessageEvent) => {
            if (event.data?.type !== 'assistant.data') return;
            data = event.data.payload;
            if (sentText && !data?.busy && !data?.error) { text = ''; sentText = ''; }
        };
        window.addEventListener('message', listener);
        post({ type: 'ready' });
        return () => window.removeEventListener('message', listener);
    });
</script>

<main>
    <header><h1>Учебный ассистент · {data?.taskId || ''}</h1>
        <button onclick={() => post({ type: 'assistant.refresh' })} disabled={data?.busy}>Обновить доступ</button>
    </header>
    {#if data?.account}
        <p>{data.account.reason} · Остаток ${data.account.balance_usd} · Расход ${data.account.spent_usd}</p>
        <p class="muted">Помощь и объяснение кода. После успешных тестов — защита решения.</p>
        <nav aria-label="Режим ассистента">
            <button disabled={!data.account.available || data.busy} onclick={() => post({ type: 'assistant.start', mode: 'hint' })}>Подсказать</button>
            <button disabled={!data.account.available || data.busy} onclick={() => post({ type: 'assistant.start', mode: 'explain' })}>Объяснить код</button>
            <button disabled={!data.account.available || !data.submissionId || data.busy} onclick={() => post({ type: 'assistant.start', mode: 'defend' })}>Проверить понимание</button>
        </nav>
        {#if data.account.defense_required && !data.submissionId}
            <p class="muted">Для защиты текущий код должен пройти серверные тесты.</p>
        {/if}
    {/if}
    {#if data?.session}
        <p class="status">{label(data.session.status)}{data.session.mode === 'defend' ? ` · ${data.session.stage}` : ''}</p>
        <section class="messages" aria-live="polite">
            {#each data.session.messages as message, i (i)}
                <article class:user={message.role === 'user'}>
                    <strong>{message.role === 'user' ? 'Ты' : 'Помощница'}</strong>
                    <div class="content">{message.content}</div>
                </article>
            {/each}
        </section>
    {/if}
    {#if data?.error}<p class="error" role="alert">{data.error}</p>{/if}
    {#if data?.busy}<p aria-live="polite">Готовлю ответ…</p>{/if}
    <form onsubmit={send}>
        <label for="message">Твой вопрос или ответ</label>
        <textarea id="message" bind:value={text} maxlength="4000" rows="5"
            disabled={!data?.account?.available || data.busy || (data.session && data.session.status !== 'active')}
            placeholder="Объясни ход мысли или укажи, где застрял"></textarea>
        <button type="submit" disabled={!text.trim() || !data?.account?.available || data.busy || (data.session && data.session.status !== 'active')}>Отправить</button>
    </form>
</main>

<style>
    :global(body) { font-family: var(--vscode-font-family); color: var(--vscode-foreground); background: var(--vscode-editor-background); }
    main { max-width: 800px; margin: auto; padding: 16px; }
    h1 { font-size: 18px; } header { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
    nav { display: flex; flex-wrap: wrap; gap: 8px; } button { color: var(--vscode-button-foreground); background: var(--vscode-button-background); border: 0; padding: 8px 12px; border-radius: 4px; cursor: pointer; }
    button:disabled { opacity: .5; cursor: default; } article { margin: 12px 0; padding: 14px; background: var(--vscode-textBlockQuote-background); border-left: 3px solid var(--vscode-focusBorder); }
    article.user { border-color: var(--vscode-descriptionForeground); } .content { white-space: pre-wrap; overflow-wrap: anywhere; margin-top: 8px; }
    textarea { box-sizing: border-box; width: 100%; margin: 8px 0; color: var(--vscode-input-foreground); background: var(--vscode-input-background); border: 1px solid var(--vscode-input-border); padding: 10px; resize: vertical; }
    .muted { color: var(--vscode-descriptionForeground); } .error { color: var(--vscode-errorForeground); } .status { margin-top: 20px; font-weight: 600; }
</style>
