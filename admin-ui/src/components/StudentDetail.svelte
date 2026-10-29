<script lang="ts">
	import { onMount } from 'svelte';
	import { getStudentProgress, type ProgressRow } from '../api';
	import AIStudent from './AIStudent.svelte';
	import Button from '../lib/components/ui/button/Button.svelte';
	import Icon from '../lib/Icon.svelte';
	import { relativeTime, dateTime } from '../lib/format';

	let { studentId, username, userRole = '', onBack }: { studentId: string; username: string; userRole?: string; onBack: () => void } = $props();

	let progress = $state<ProgressRow[]>([]);
	let loading = $state(true);
	let error = $state('');

	async function load() {
		loading = true;
		error = '';
		try {
			progress = await getStudentProgress(studentId);
		} catch (e) {
			error = (e as Error).message;
		} finally {
			loading = false;
		}
	}

  function statusLabel(value: string): string {
    return ({ passed: 'Пройдено', partial: 'Частично', failed: 'Не пройдено', error: 'Ошибка', timeout: 'Тайм-аут' } as Record<string, string>)[value] || value;
  }
	onMount(() => { load(); });
</script>

<section class="admin-stack">
  <div><Button variant="ghost" class="-ml-3" onclick={onBack}><Icon name="back" size={16} />Все пользователи</Button></div>
  <div class="admin-section-head"><div><h2>Результаты проверок</h2><p class="admin-subtitle">Попытки и прохождение задач · {username}</p></div><Button variant="outline" onclick={load} disabled={loading}><Icon name="refresh" size={15} />{loading ? 'Обновляю…' : 'Обновить'}</Button></div>
  {#if loading}<div class="admin-state" role="status">Загружаю прогресс…</div>
  {:else if error}<div class="admin-notice error" role="alert">{error}</div><div><Button variant="outline" onclick={load}>Повторить загрузку</Button></div>
  {:else if progress.length === 0}<div class="admin-state">Ученик ещё не отправлял решения на проверку.</div>
  {:else}<div class="admin-table-wrap"><table class="admin-table"><thead><tr><th>Задача</th><th>Результат</th><th class="num">Тесты</th><th class="num">Попытки</th><th>Последняя проверка</th></tr></thead><tbody>
    {#each progress as row (row.task_id + row.version)}<tr><td><strong>{row.task_id}</strong><small class="version">Версия {row.version}</small></td><td><span class="admin-badge" class:success={row.status === 'passed'} class:warning={row.status === 'partial'} class:danger={!['passed', 'partial'].includes(row.status)}>{statusLabel(row.status)}</span></td><td class="num">{row.passed_tests} / {row.total_tests}</td><td class="num">{row.attempts}</td><td class="activity" title={dateTime(row.last_run_at)}>{relativeTime(row.last_run_at)}</td></tr>{/each}
  </tbody></table></div>{/if}
  {#if userRole === 'admin'}<AIStudent {studentId} />{/if}
</section>

<style>
  table { min-width: 570px; }
  td strong { font-weight: 500; }
  .version { display: block; margin-top: 4px; color: var(--muted-foreground); font-size: 11px; }
  .activity { color: var(--muted-foreground); font-size: 12px; }
</style>
