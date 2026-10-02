<script lang="ts">
  import { onMount } from 'svelte';
  import { getOverview, type OverviewDTO } from '../api';
  import Button from '../lib/components/ui/button/Button.svelte';
  import Card from '../lib/components/ui/card/Card.svelte';
  import Icon from '../lib/Icon.svelte';
  import { relativeTime, dateTime } from '../lib/format';

  let { isAdmin = false, onNavigate }: { isAdmin?: boolean; onNavigate: (view: 'students' | 'catalog' | 'student-ai') => void } = $props();
  let overview = $state<OverviewDTO | null>(null);
  let loading = $state(true);
  let error = $state('');
  let syncOk = $derived(overview?.latest_sync && ['ok', 'success'].includes(overview.latest_sync.status.toLowerCase()));
  let syncRunning = $derived(overview?.latest_sync?.status.toLowerCase() === 'running');
  async function load() {
    loading = true; error = '';
    try { overview = await getOverview(); }
    catch (failure) { error = (failure as Error).message; }
    finally { loading = false; }
  }
  onMount(() => { void load(); });
</script>

<div class="admin-stack">
  <div class="admin-section-head">
    <div><h2>Учебное пространство</h2><p class="admin-subtitle">Каталог, ученики и состояние сервиса на одном экране.</p></div>
    <div class="admin-actions">
      {#if overview}<span class="admin-badge" class:success={overview.server === 'ok'} class:danger={overview.server !== 'ok'}>{overview.server === 'ok' ? 'Сервер отвечает' : 'Проверь сервер'}</span>{/if}
      <Button variant="outline" size="sm" onclick={load} disabled={loading}><Icon name="refresh" size={15} />{loading ? 'Обновляю…' : 'Обновить'}</Button>
    </div>
  </div>
  {#if error}<div class="admin-notice error" role="alert">{error}</div>{/if}
  {#if loading && !overview}
    <div class="admin-state" role="status">Загружаю состояние сервиса…</div>
  {:else if overview}
    <div class="metrics">
      {#each [
        { title: 'Задачи', value: overview.counts.tasks, icon: 'catalog', note: 'В учебном каталоге' },
        { title: 'Ученики', value: overview.counts.students, icon: 'users', note: 'Зарегистрировано в системе' },
        { title: 'Проекты', value: overview.counts.projects, icon: 'book', note: 'Учебные направления' },
        { title: 'Папки', value: overview.counts.folders, icon: 'catalog', note: 'Разделы каталога' }
      ] as metric}
        <Card class="gap-0 p-5">
          <div class="metric-heading"><span>{metric.title}</span><Icon name={metric.icon} size={18} /></div>
          <strong class="metric-value">{metric.value}</strong><span class="metric-note">{metric.note}</span>
        </Card>
      {/each}
    </div>
    <div class="overview-columns">
      <Card class="gap-0 p-6">
        <div class="card-heading"><div><h3>Обновление каталога</h3><p>Последняя синхронизация задач</p></div><span class="admin-badge" class:success={!!syncOk} class:warning={!!syncRunning} class:danger={!!overview.latest_sync && !syncOk && !syncRunning}>{!overview.latest_sync ? 'Ещё не запускалась' : syncOk ? 'Готово' : syncRunning ? 'В процессе' : 'Есть ошибки'}</span></div>
        {#if overview.latest_sync}
          <p class="sync-time" title={dateTime(overview.latest_sync.finished_at || overview.latest_sync.started_at)}>{relativeTime(overview.latest_sync.finished_at || overview.latest_sync.started_at)}</p>
          <div class="sync-counts"><div><strong>{overview.latest_sync.added}</strong><span>Добавлено</span></div><div><strong>{overview.latest_sync.updated}</strong><span>Обновлено</span></div><div><strong>{overview.latest_sync.skipped}</strong><span>Без изменений</span></div></div>
          {#if overview.latest_sync.errors > 0}<p class="admin-notice error">Ошибок: {overview.latest_sync.errors}. Подробности доступны в журнале ниже.</p>{/if}
          <details class="sync-details"><summary>Подробности синхронизации</summary><dl>
            <div><dt>Источник</dt><dd>{({ startup: 'Запуск сервера', manual: 'Вручную', cron: 'По расписанию' } as Record<string, string>)[overview.latest_sync.source] || overview.latest_sync.source}</dd></div>
            <div><dt>Репозиторий</dt><dd>{overview.latest_sync.repo_url || 'Не указан'}</dd></div>
            {#if overview.latest_sync.git_sha}<div><dt>Коммит</dt><dd><code>{overview.latest_sync.git_sha}</code></dd></div>{/if}
            <div><dt>Начало</dt><dd>{dateTime(overview.latest_sync.started_at)}</dd></div><div><dt>Завершение</dt><dd>{dateTime(overview.latest_sync.finished_at)}</dd></div>
          </dl>{#if overview.latest_sync.error_details}<pre>{overview.latest_sync.error_details}</pre>{:else}<p>Ошибок нет.</p>{/if}</details>
        {:else}<p class="empty-sync">После первой синхронизации здесь появятся её время и результат.</p>{/if}
      </Card>
      <Card class="gap-0 p-6">
        <div class="card-heading"><div><h3>Продолжить работу</h3><p>Основные разделы пространства</p></div></div>
        <div class="quick-links">
          <button onclick={() => onNavigate('catalog')}><span class="quick-icon"><Icon name="catalog" /></span><span><strong>Каталог задач</strong><small>Условия, код и проверки</small></span><Icon name="arrow" size={16} /></button>
          <button onclick={() => onNavigate('students')}><span class="quick-icon"><Icon name="users" /></span><span><strong>Прогресс учеников</strong><small>Результаты и доступ к обучению</small></span><Icon name="arrow" size={16} /></button>
          {#if isAdmin}<button onclick={() => onNavigate('student-ai')}><span class="quick-icon"><Icon name="ai" /></span><span><strong>Студенческий AI</strong><small>Модели и проверка ответов</small></span><Icon name="arrow" size={16} /></button>{/if}
        </div>
      </Card>
    </div>
  {/if}
</div>

<style>
  .metrics { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 16px; }
  .metric-heading { display: flex; align-items: center; justify-content: space-between; gap: 12px; color: var(--muted-foreground); font-size: 13px; }
  .metric-value { margin-top: 18px; font-size: 32px; font-weight: 600; letter-spacing: -.04em; line-height: 1.2; font-variant-numeric: tabular-nums; }
  .metric-note { margin-top: 6px; color: var(--muted-foreground); font-size: 11px; }
  .overview-columns { display: grid; grid-template-columns: minmax(0, 1.2fr) minmax(0, 1fr); gap: 20px; align-items: start; }
  .card-heading { display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 14px; }
  h3 { font-size: 16px; font-weight: 600; letter-spacing: -.02em; margin: 0; }
  .card-heading p { font-size: 12px; line-height: 1.6; color: var(--muted-foreground); margin: 5px 0 0; }
  .sync-time { margin: 24px 0 20px; font-size: 22px; font-weight: 500; letter-spacing: -.025em; }
  .sync-counts { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; padding: 18px 0; border-top: 1px solid var(--border); border-bottom: 1px solid var(--border); }
  .sync-counts div { display: grid; gap: 4px; }.sync-counts strong { font-size: 20px; font-weight: 500; }.sync-counts span { color: var(--muted-foreground); font-size: 11px; }
  .sync-details { margin-top: 20px; font-size: 12px; color: var(--muted-foreground); }
  summary { cursor: pointer; color: var(--foreground); }
  dl { margin: 18px 0; display: grid; gap: 12px; } dl div { display: grid; grid-template-columns: 90px minmax(0, 1fr); gap: 12px; } dd { margin: 0; overflow-wrap: anywhere; color: var(--foreground); }
  pre { max-height: 220px; overflow: auto; white-space: pre-wrap; color: var(--destructive); }
  .empty-sync { margin: 26px 0 0; color: var(--muted-foreground); font-size: 13px; line-height: 1.7; }
  .quick-links { display: grid; gap: 4px; margin-top: 18px; }
  .quick-links button { display: flex; align-items: center; gap: 12px; padding: 14px 0; border: 0; background: transparent; text-align: left; }
  .quick-links button:hover { background: transparent; color: var(--ring); }
  .quick-icon { width: 40px; height: 40px; flex-shrink: 0; display: grid; place-items: center; border: 1px solid var(--border); border-radius: 10px; background: var(--secondary); color: var(--muted-foreground); }
  .quick-links button > span:nth-child(2) { min-width: 0; flex: 1; display: grid; gap: 4px; }
  .quick-links strong { font-size: 13px; font-weight: 500; }.quick-links small { color: var(--muted-foreground); font-size: 11px; }
  .admin-notice { margin-top: 16px; }
  @media (max-width: 1050px) { .metrics { grid-template-columns: repeat(2, minmax(0, 1fr)); } .overview-columns { grid-template-columns: 1fr; } }
  @media (max-width: 600px) { .metrics { gap: 10px; }.metric-value { font-size: 29px; }.metric-note { line-height: 1.5; } }
</style>
