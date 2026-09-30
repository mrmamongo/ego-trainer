<script lang="ts">
    import { onMount } from 'svelte';
    import { getAIAccount, updateAIAccess, creditAIAccount, getAIUsage, getAISubmissions,
        type AIAccount, type AIUsage, type AISubmission } from '../api';
    let { studentId }: { studentId: string } = $props();
    let account = $state<AIAccount | null>(null);
    let usage = $state<AIUsage[]>([]);
    let submissions = $state<AISubmission[]>([]);
    let enabled = $state(false);
    let required = $state(true);
    let amount = $state(1);
    let busy = $state(false);
    let error = $state('');
    let creditId = '';
    let creditAmount = 0;
    async function load() {
        const values = await Promise.all([getAIAccount(studentId), getAIUsage(studentId), getAISubmissions(studentId)]);
        account = values[0]; usage = values[1]; submissions = values[2];
        enabled = account.enabled; required = account.defense_required;
    }
    onMount(() => { load().catch((e) => error = e.message); });
    async function action(fn: () => Promise<unknown>) {
        busy = true; error = '';
        try { await fn(); await load(); }
        catch (e) { error = (e as Error).message; }
        finally { busy = false; }
    }
    async function credit() {
        if (!creditId || creditAmount !== amount) { creditId = crypto.randomUUID(); creditAmount = amount; }
        await creditAIAccount(studentId, amount, creditId);
        creditId = '';
    }
    function status(value: string) {
        return ({ pending: 'Ожидает защиты', confirmed: 'Подтверждено', needs_review: 'Нужен разбор' } as Record<string, string>)[value] || value;
    }
</script>

<section>
    <h2>Ассистент и баланс</h2>
    {#if error}<p class="error" role="alert">{error}</p>{/if}
    {#if account}
        <p>{account.reason} · Баланс ${account.balance_usd} · Зарезервировано ${account.reserved_usd} · Расход ${account.spent_usd}</p>
        <div class="controls">
            <label><input type="checkbox" bind:checked={enabled} /> Дать доступ к ассистенту</label>
            <label><input type="checkbox" bind:checked={required} /> Обязательная защита после успешных тестов</label>
            <button disabled={busy} onclick={() => action(() => updateAIAccess(studentId, enabled, required))}>Сохранить доступ</button>
        </div>
        <div class="controls">
            <label>Пополнение в USD <input type="number" min="0.000001" max="10000" step="0.000001" bind:value={amount} /></label>
            <button disabled={busy || !amount || amount <= 0} onclick={() => action(credit)}>Пополнить</button>
            <button disabled={busy} onclick={() => action(async () => {})}>Обновить</button>
        </div>
        <h3>Проверки понимания</h3>
        {#if !submissions.length}<p>Проверок пока нет</p>{/if}
        {#each submissions as submission (submission.id)}
            <details><summary>{submission.task_id} · v{submission.version} · {status(submission.understanding)}</summary>
                {#each submission.evidence as evidence}<p>{evidence.stage}: {evidence.quote}</p>{/each}
            </details>
        {/each}
        <h3>Последние расходы</h3>
        <table><thead><tr><th>Модель</th><th>Назначение</th><th>Токены вход / выход</th><th>USD</th><th>Результат</th></tr></thead>
            <tbody>{#each usage as row (row.id)}<tr><td>{row.model}</td><td>{row.purpose === 'guard' ? 'Проверка ответа' : 'Ассистент'}</td><td>{row.input_tokens} / {row.output_tokens}{row.estimated ? ' (оценка)' : ''}</td><td>{row.cost_usd}</td><td>{row.outcome}</td></tr>{/each}</tbody>
        </table>
    {/if}
</section>

<style>
    section { margin: 24px 0; padding-top: 12px; border-top: 1px solid #555; } .controls { display: flex; align-items: center; flex-wrap: wrap; gap: 12px; margin: 16px 0; }
    input[type=number] { width: 100px; background: #252526; color: #d4d4d4; padding: 6px; border: 1px solid #555; }
    button { padding: 7px 12px; color: white; background: #007acc; border: 0; border-radius: 4px; cursor: pointer; } button:disabled { opacity: .5; } table { width: 100%; border-collapse: collapse; } th,td { text-align: left; padding: 8px; border-bottom: 1px solid #444; } .error { color: #f87171; } details { margin: 8px 0; } summary { cursor: pointer; }
</style>
