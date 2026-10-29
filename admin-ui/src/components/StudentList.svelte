<script lang="ts">
	import { onMount } from 'svelte';
	import Button from '../lib/components/ui/button/Button.svelte';
	import Icon from '../lib/Icon.svelte';
	import { relativeTime, dateTime, roleLabel } from '../lib/format';
	import {
		listStudents,
		deleteUser,
		updateRole,
		resetPassword,
		createUser,
		authProviders,
		type StudentSummary,
	} from '../api';

	let students = $state<StudentSummary[]>([]);
	let loading = $state(true);
	let error = $state('');
	let actionError = $state('');
	let showForm = $state(false);
	let localAuthEnabled = $state(false);
	let search = $state('');
	let page = $state(1);
	const pageSize = 25;

	let { onSelect, userRole }: { onSelect: (studentId: string, username: string) => void; userRole: string } = $props();
	let isAdmin = $derived(userRole === 'admin');
	let filteredStudents = $derived.by(() => {
		const needle = search.trim().toLocaleLowerCase();
		if (!needle) return students;
		return students.filter((student) =>
			student.username.toLocaleLowerCase().includes(needle)
			|| student.student_id.toLocaleLowerCase().includes(needle),
		);
	});
	let pageCount = $derived(Math.max(1, Math.ceil(filteredStudents.length / pageSize)));
	let visibleStudents = $derived(filteredStudents.slice((page - 1) * pageSize, page * pageSize));

	async function load() {
		loading = true;
		error = '';
		actionError = '';
		try {
			students = await listStudents();
			page = 1;
		} catch (e) {
			error = (e as Error).message;
		} finally {
			loading = false;
		}
	}

	async function handleDelete(student: StudentSummary) {
		if (!confirm(`Удалить пользователя ${student.username}? Его прогресс тоже будет удалён.`)) return;
		try {
			await deleteUser(student.student_id);
			await load();
		} catch (e) {
			actionError = `Не удалось удалить ${student.username}: ${(e as Error).message}`;
		}
	}

	async function handleRoleChange(student: StudentSummary, newRole: string) {
		if (newRole === student.role) return;
		if (newRole === 'mentor' && !confirm(`Назначить ${student.username} наставником? Он сможет назначать других наставников.`)) return;
		try {
			await updateRole(student.student_id, newRole);
			await load();
		} catch (e) {
			actionError = `Не удалось изменить роль: ${(e as Error).message}`;
		}
	}

	async function handleResetPassword(student: StudentSummary) {
		const pw = prompt(`Новый пароль для ${student.username}:`);
		if (!pw) return;
		try {
			await resetPassword(student.student_id, pw);
			alert('Пароль обновлён.');
		} catch (e) {
			actionError = `Не удалось изменить пароль: ${(e as Error).message}`;
		}
	}

	async function handleCreate(e: Event) {
		e.preventDefault();
		const form = e.target as HTMLFormElement;
		const fd = new FormData(form);
		const username = fd.get('username') as string;
		const password = fd.get('password') as string;
		const role = fd.get('role') as string;
		if (!username || !password) return;
		try {
			await createUser(username, password, role);
			form.reset();
			showForm = false;
			await load();
		} catch (err) {
			actionError = `Не удалось создать пользователя: ${(err as Error).message}`;
		}
	}

	onMount(() => { void load(); void authProviders().then(value => localAuthEnabled = value.local).catch(() => {}); });
</script>

<section class="admin-stack">
  <div class="admin-section-head">
    <div><h2>Все пользователи</h2><p class="admin-subtitle">Открой профиль, чтобы посмотреть прогресс и настроить доступ к ассистенту.</p></div>
    <div class="admin-actions">
      <Button variant="outline" onclick={load} disabled={loading}><Icon name="refresh" size={15} />{loading ? 'Обновляю…' : 'Обновить'}</Button>
      {#if isAdmin && localAuthEnabled}<Button variant={showForm ? 'outline' : 'default'} onclick={() => { showForm = !showForm; }}><Icon name="plus" size={16} />{showForm ? 'Отменить' : 'Добавить пользователя'}</Button>{/if}
    </div>
  </div>
  {#if actionError}<p class="admin-notice error" role="alert">{actionError}</p>{/if}
  {#if isAdmin && localAuthEnabled && showForm}
    <form class="create-form admin-panel" onsubmit={handleCreate}>
      <label class="admin-field">Логин<input name="username" autocomplete="off" placeholder="Имя пользователя" required /></label>
      <label class="admin-field">Пароль<input name="password" type="password" autocomplete="new-password" placeholder="Временный пароль" required /></label>
      <label class="admin-field">Роль<select name="role"><option value="student">Ученик</option><option value="admin">Администратор</option></select></label>
      <Button type="submit">Создать</Button>
    </form>
  {/if}
  {#if loading}
    <div class="admin-state" role="status">Загружаю пользователей…</div>
  {:else if error}
    <div class="admin-notice error" role="alert">{error}</div><div><Button variant="outline" onclick={load}>Повторить загрузку</Button></div>
  {:else if students.length === 0}
    <div class="admin-state"><strong>Пользователей пока нет</strong><p>Новые ученики появятся здесь после регистрации или создания аккаунта.</p></div>
  {:else}
    <div class="list-toolbar"><label class="search-field" for="student-search"><span>Поиск пользователей</span><input id="student-search" type="search" bind:value={search} oninput={() => { page = 1; }} placeholder="Логин или ID пользователя" /></label><span class="result-count" role="status">Найдено {filteredStudents.length} из {students.length}</span></div>
    {#if filteredStudents.length === 0}
      <div class="admin-state">По запросу «{search}» ничего не нашлось.<div class="empty-action"><Button variant="outline" onclick={() => { search = ''; page = 1; }}>Сбросить поиск</Button></div></div>
    {:else}
      <div class="admin-table-wrap"><table class="admin-table">
        <thead><tr><th>Пользователь</th><th>Роль</th><th class="num">Задач</th><th class="num">Решено</th><th class="num">Частично</th><th class="num">Не пройдено</th><th>Активность</th>{#if isAdmin}<th><span class="sr-only">Действия</span></th>{/if}</tr></thead>
        <tbody>{#each visibleStudents as student (student.student_id)}
          <tr>
            <td><button class="user-link" onclick={() => onSelect(student.student_id, student.username)}><span class="avatar" aria-hidden="true">{student.username.slice(0, 1).toLocaleUpperCase()}</span><span>{student.username}</span></button></td>
            <td>{#if isAdmin}
              <select class="role-select" aria-label={`Роль пользователя ${student.username}`} value={student.role} onchange={(event) => handleRoleChange(student, (event.target as HTMLSelectElement).value)}>
                <option value="student">Ученик</option>{#if student.role === 'mentor'}<option value="mentor" disabled>Наставник</option>{/if}<option value="admin">Администратор</option>
              </select>
            {:else if userRole === 'mentor' && student.role === 'student'}<Button variant="outline" size="sm" onclick={() => handleRoleChange(student, 'mentor')}>Назначить наставником</Button>
            {:else}<span class="admin-badge">{roleLabel(student.role)}</span>{/if}</td>
            <td class="num">{student.tasks_total}</td><td class="num" class:passed={student.tasks_passed > 0}>{student.tasks_passed}</td><td class="num" class:partial={student.tasks_partial > 0}>{student.tasks_partial}</td><td class="num" class:failed={student.tasks_failed > 0}>{student.tasks_failed}</td>
            <td class="activity" title={student.last_activity ? dateTime(student.last_activity) : undefined}>{relativeTime(student.last_activity)}</td>
            {#if isAdmin}<td><div class="row-actions">{#if localAuthEnabled}<Button variant="ghost" size="sm" onclick={() => handleResetPassword(student)} aria-label={`Изменить пароль пользователя ${student.username}`}>Пароль</Button>{/if}<Button variant="destructive" size="sm" onclick={() => handleDelete(student)} aria-label={`Удалить пользователя ${student.username}`}>Удалить</Button></div></td>{/if}
          </tr>
        {/each}</tbody>
      </table></div>
      {#if pageCount > 1}<nav class="pagination" aria-label="Страницы списка пользователей"><Button variant="outline" size="sm" onclick={() => page = Math.max(1, page - 1)} disabled={page === 1}>Назад</Button><span>Страница {page} из {pageCount}</span><Button variant="outline" size="sm" onclick={() => page = Math.min(pageCount, page + 1)} disabled={page === pageCount}>Далее</Button></nav>{/if}
    {/if}
  {/if}
</section>

<style>
  .create-form { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr) 170px auto; align-items: end; gap: 16px; }
  .list-toolbar { display: flex; justify-content: space-between; align-items: end; gap: 20px; }
  .search-field { display: grid; gap: 8px; width: min(380px, 100%); font-size: 12px; color: var(--muted-foreground); }
  .search-field input { width: 100%; font-size: 13px; }
  .result-count { padding-bottom: 10px; color: var(--muted-foreground); font-size: 12px; white-space: nowrap; }
  table { min-width: 810px; }
  .user-link { display: flex; align-items: center; gap: 10px; border: 0; padding: 0; background: transparent; text-align: left; font-weight: 500; }
  .user-link:hover { background: transparent; color: var(--ring); }
  .avatar { width: 34px; height: 34px; flex-shrink: 0; display: grid; place-items: center; border: 1px solid var(--border); border-radius: 50%; background: var(--secondary); color: var(--muted-foreground); font-size: 12px; }
  .role-select { width: 150px; padding: 7px 9px; border-color: var(--border); font-size: 12px; }
  .row-actions { display: flex; gap: 2px; justify-content: flex-end; }
  .activity { color: var(--muted-foreground); font-size: 12px; white-space: nowrap; }
  .passed { color: var(--success); }.partial { color: var(--warning); }.failed { color: var(--destructive); }
  .pagination { display: flex; justify-content: flex-end; align-items: center; gap: 14px; color: var(--muted-foreground); font-size: 12px; }
  .empty-action { margin-top: 16px; }
  .admin-state strong { color: var(--foreground); font-size: 15px; font-weight: 500; }.admin-state p { margin: 6px 0 0; }
  @media (max-width: 1050px) { .create-form { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
  @media (max-width: 600px) { .create-form { grid-template-columns: 1fr; }.list-toolbar { align-items: stretch; flex-direction: column; gap: 10px; }.search-field { width: 100%; }.result-count { padding: 0; }.pagination { justify-content: center; } }
</style>
