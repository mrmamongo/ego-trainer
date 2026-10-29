<script lang="ts">
    import { onMount } from 'svelte';
    import Button from '../lib/components/ui/button/Button.svelte';
    import Card from '../lib/components/ui/card/Card.svelte';
    import { dollars } from '../lib/format';
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

<section class="admin-stack ai-student">
  <div class="admin-section-head"><div><h2>Ассистент и защита</h2><p class="admin-subtitle">Доступ к помощи, бюджет запросов и результаты проверки понимания.</p></div>{#if account}<span class="admin-badge" class:success={account.available}>{account.reason}</span>{/if}</div>
  {#if error}<div class="admin-notice error" role="alert">{error}</div>{/if}
  {#if account}
    <div class="access-grid">
      <Card class="gap-5 p-6"><h3>Доступ к обучению</h3><label class="admin-toggle"><input type="checkbox" bind:checked={enabled} disabled={busy} /><span><strong>Учебный ассистент</strong><small>Подсказки и объяснения к задачам ученика.</small></span></label><label class="admin-toggle"><input type="checkbox" bind:checked={required} disabled={busy} /><span><strong>Обязательная защита</strong><small>Проверять понимание после успешных тестов.</small></span></label><div><Button variant="outline" disabled={busy} onclick={() => action(() => updateAIAccess(studentId, enabled, required))}>Сохранить доступ</Button></div></Card>
      <Card class="gap-5 p-6"><div class="budget-title"><h3>Бюджет запросов</h3><Button variant="ghost" size="sm" disabled={busy} onclick={() => action(async () => {})}>Обновить</Button></div><strong class="balance">{dollars(account.balance_usd)}</strong><div class="budget-meta"><span>В резерве <strong>{dollars(account.reserved_usd)}</strong></span><span>Израсходовано <strong>{dollars(account.spent_usd)}</strong></span></div><div class="credit"><label class="admin-field">Пополнение, USD<input type="number" min="0.000001" max="10000" step="0.000001" bind:value={amount} disabled={busy} /></label><Button disabled={busy || !amount || amount <= 0} onclick={() => action(credit)}>Пополнить</Button></div></Card>
    </div>
    <div class="admin-panel"><h3>Проверки понимания</h3>{#if !submissions.length}<p class="section-empty">Ученик ещё не проходил защиту решения.</p>{/if}
      {#each submissions as submission (submission.id)}<details class="defense-result"><summary><span>{submission.task_id} · версия {submission.version}</span><span class="admin-badge" class:success={submission.understanding === 'confirmed'} class:warning={submission.understanding === 'needs_review'}>{status(submission.understanding)}</span></summary>{#each submission.evidence as evidence}<blockquote><strong>{({ mechanism: 'Объяснение', trace: 'Разбор выполнения', transfer: 'Новый случай' } as Record<string, string>)[evidence.stage] || evidence.stage}</strong><p>{evidence.quote}</p></blockquote>{/each}</details>{/each}
    </div>
    <div><h3 class="usage-title">Последние расходы</h3>{#if !usage.length}<div class="admin-state">Платных запросов пока нет.</div>{:else}<div class="admin-table-wrap"><table class="admin-table"><thead><tr><th>Модель</th><th>Назначение</th><th>Вход / выход</th><th class="num">Стоимость</th><th>Результат</th></tr></thead><tbody>{#each usage as row (row.id)}<tr><td>{row.model}</td><td>{row.purpose === 'guard' ? 'Проверка ответа' : 'Ассистент'}</td><td>{row.input_tokens} / {row.output_tokens}{row.estimated ? ' (оценка)' : ''}</td><td class="num">{dollars(row.cost_usd)}</td><td>{row.outcome}</td></tr>{/each}</tbody></table></div>{/if}</div>
  {:else if error}<div><Button variant="outline" disabled={busy} onclick={() => action(async () => {})}>Повторить загрузку</Button></div>{:else}<div class="admin-state" role="status">Загружаю доступ и бюджет…</div>{/if}
</section>

<style>
  .ai-student { margin-top: 8px; padding-top: 28px; border-top: 1px solid var(--border); }
  .access-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 20px; }
  h3 { margin: 0; font-size: 16px; font-weight: 600; letter-spacing: -.02em; }
  .budget-title { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
  .balance { font-size: 30px; line-height: 1.2; letter-spacing: -.03em; font-weight: 600; font-variant-numeric: tabular-nums; }
  .budget-meta { display: flex; flex-wrap: wrap; gap: 8px 20px; color: var(--muted-foreground); font-size: 12px; }.budget-meta strong { margin-left: 4px; color: var(--foreground); font-weight: 500; }
  .credit { display: flex; gap: 12px; align-items: end; border-top: 1px solid var(--border); padding-top: 20px; }.credit label { min-width: 0; flex: 1; }
  .section-empty { margin: 14px 0 0; color: var(--muted-foreground); font-size: 13px; line-height: 1.6; }
  .defense-result { margin-top: 16px; padding-top: 16px; border-top: 1px solid var(--border); }
  summary { display: flex; justify-content: space-between; flex-wrap: wrap; gap: 10px; cursor: pointer; font-size: 13px; }
  blockquote { border-left: 2px solid var(--primary); margin: 16px 0 0; padding-left: 14px; font-size: 13px; }blockquote strong { font-size: 12px; font-weight: 500; }blockquote p { color: var(--muted-foreground); margin: 6px 0 0; }
  .usage-title { margin-bottom: 16px; }table { min-width: 600px; }
  @media (max-width: 1050px) { .access-grid { grid-template-columns: 1fr; } }
</style>
