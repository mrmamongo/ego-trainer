<script lang="ts">
  import { onMount } from 'svelte';
  import { getToken, setToken, me, type AuthResponse, type CatalogTaskDTO } from './api';
  import { getSettings, type SettingsSnapshot } from './consoleApi';
  import Icon from './lib/Icon.svelte';
  import Login from './components/Login.svelte'; import Overview from './components/Overview.svelte';
  import StudentList from './components/StudentList.svelte'; import StudentDetail from './components/StudentDetail.svelte';
  import StudioWorkspace from './components/StudioWorkspace.svelte';
  import AISettings from './components/AISettings.svelte';
  import Settings from './components/Settings.svelte';
  type View = 'overview' | 'students' | 'catalog' | 'settings' | 'student-ai';
  const titles: Record<View, string> = { overview: 'Обзор сервиса', students: 'Пользователи', catalog: 'Редактор задач', settings: 'Настройки сервиса', 'student-ai': 'Студенческий ассистент' };
  let view = $state<View>((Object.keys(titles).includes(location.hash.slice(1)) ? location.hash.slice(1) : 'overview') as View);
  let loggedIn = $state(false); let sessionSeen = $state(false); let checking = $state(true);
  let userRole = $state(''); let username = $state(''); let userId = $state(''); let authError = $state('');
  let serviceName = $state('Cogito'); let version = $state(''); let dirty = $state(false); let workBusy = $state(false);
  let selectedStudent = $state<{ id: string; username: string } | null>(null);
  let selectedTask = $state<Pick<CatalogTaskDTO, 'id' | 'task_id'> | null>(null);
  const isAdmin = $derived(userRole === 'admin');
  async function brand() { if (userRole !== 'admin') return; try { const data = await getSettings(); saved(data); } catch {} }
  function saved(data: SettingsSnapshot) { serviceName = data.config.service_name; version = data.runtime.version; }
  function accept(data: { user_id: string; username: string; role: string }) {
    if (data.role === 'student') {
      const token = getToken();
      if (token) localStorage.setItem('ego_student_token', token);
      setToken(null); location.assign('/student'); return;
    }
    if (userId && userId !== data.user_id) { selectedTask = null; selectedStudent = null; dirty = false; view = 'overview'; }
    userId = data.user_id; username = data.username; userRole = data.role; authError = ''; loggedIn = true; sessionSeen = true;
    if (userRole !== 'admin' && (view === 'settings' || view === 'student-ai')) view = 'overview';
    void brand();
  }
  async function restoreSession() { try { if (getToken()) accept(await me()); } catch { setToken(null); } finally { checking = false; } }
  function handleLogin(data: AuthResponse) { setToken(data.access_token); accept(data); }
  function navTo(next: View): boolean {
    if (workBusy) return false;
    if (next === view) return true;
    if (dirty && !confirm('Есть несохранённые изменения. Перейти и отбросить их?')) return false;
    dirty = false; view = next; selectedStudent = null; selectedTask = null;
    history.replaceState(null, '', '#' + next); return true;
  }
  function logout() { if (workBusy || (dirty && !confirm('Есть несохранённые изменения. Выйти и отбросить их?'))) return; dirty = false; selectedTask = null; selectedStudent = null; view = 'overview'; history.replaceState(null, '', '#overview'); setToken(null); loggedIn = false; sessionSeen = false; userRole = ''; username = ''; userId = ''; }
  function sessionExpired() { if (loggedIn) { loggedIn = false; authError = 'Сессия истекла. Войди снова — открытый черновик сохранён в этой вкладке.'; } }
  onMount(() => {
    void restoreSession();
    const beforeUnload = (e: BeforeUnloadEvent) => { if (dirty) { e.preventDefault(); e.returnValue = ''; } };
    const hashChange = () => { const next = location.hash.slice(1) as View; if (next in titles && !navTo(next)) history.replaceState(null, '', '#' + view); };
    window.addEventListener('ego:session-expired', sessionExpired); window.addEventListener('beforeunload', beforeUnload); window.addEventListener('hashchange', hashChange);
    return () => { window.removeEventListener('ego:session-expired', sessionExpired); window.removeEventListener('beforeunload', beforeUnload); window.removeEventListener('hashchange', hashChange); };
  });
</script>

{#if checking}<div class="boot">Проверяю сессию…</div>{:else if !loggedIn}{#if authError}<p class="auth-error" role="alert">{authError}</p>{/if}<Login onLogin={handleLogin} />{/if}
{#if sessionSeen}
  <main class="shell" class:editor-mode={view === 'catalog'} hidden={!loggedIn}>
    <aside class="sidebar"><div class="brand"><img class="logo" src="/static/branding/cogito-mark.svg" alt="" width="36" height="36"><div><strong>{serviceName}</strong><small>Панель управления</small></div></div>
      <p class="nav-caption">Обучение</p><nav aria-label="Навигация админки">
        <button class:active={view === 'overview'} disabled={workBusy} onclick={() => navTo('overview')} aria-current={view === 'overview' ? 'page' : undefined}><Icon name="overview" size={18} /> Обзор</button>
        <button class:active={view === 'students'} disabled={workBusy} onclick={() => navTo('students')} aria-current={view === 'students' ? 'page' : undefined}><Icon name="users" size={18} /> Пользователи</button>
        <button class:active={view === 'catalog'} disabled={workBusy} onclick={() => navTo('catalog')} aria-current={view === 'catalog' ? 'page' : undefined}><Icon name="catalog" size={18} /> Каталог задач</button>
        {#if isAdmin}<button class:active={view === 'student-ai'} disabled={workBusy} onclick={() => navTo('student-ai')} aria-current={view === 'student-ai' ? 'page' : undefined}><Icon name="ai" size={18} /> Студенческий AI</button><p class="nav-caption">Администрирование</p><button class:active={view === 'settings'} disabled={workBusy} onclick={() => navTo('settings')} aria-current={view === 'settings' ? 'page' : undefined}><Icon name="settings" size={18} /> Настройки</button>{/if}
      </nav>
      <div class="account"><strong>{username}</strong><small>{isAdmin ? 'Администратор' : 'Наставник'}{version ? ` · v${version}` : ''}</small><button disabled={workBusy} onclick={logout}><Icon name="logout" size={16} /> Выйти</button></div>
    </aside>
    <section class="workspace" class:editor-mode={view === 'catalog'}><header class="page-header"><div><p class="eyebrow">{serviceName}</p><h1>{selectedTask ? `Редактор · ${selectedTask.task_id}` : selectedStudent ? `Прогресс: ${selectedStudent.username}` : titles[view]}</h1></div><div class="header-status">{#if dirty}<span class="admin-badge warning">Несохранённые изменения</span>{:else}<span class="admin-badge">{isAdmin ? 'Администратор' : 'Наставник'}</span>{/if}</div></header>
      <div class="page-body" class:editor-page={view === 'catalog'}>
        {#if view === 'overview'}<Overview {isAdmin} onNavigate={(next) => { navTo(next); }} />
        {:else if view === 'students'}{#if selectedStudent}<StudentDetail studentId={selectedStudent.id} username={selectedStudent.username} {userRole} onBack={() => { selectedStudent = null; }} />{:else}<StudentList {userRole} onSelect={(id, name) => { selectedStudent = { id, username: name }; }} />{/if}
        {:else if view === 'catalog'}<StudioWorkspace role={userRole} onBusyChange={(value) => { workBusy = value; }} onDirtyChange={(value) => { dirty = value; }} onActiveTask={(id, label) => { selectedTask = id ? { id, task_id: label } : null; }} />
        {:else if view === 'student-ai' && isAdmin}<AISettings onBusyChange={(value) => { workBusy = value; }} onDirtyChange={(value) => { dirty = value; }} />
        {:else if view === 'settings' && isAdmin}<Settings onBusyChange={(value) => { workBusy = value; }} onDirtyChange={(value) => { dirty = value; }} onSaved={saved} />{/if}
      </div>
    </section>
  </main>
{/if}

<style>
  :global(.monaco-editor textarea.inputarea) { border: 0; padding: 0; outline: none; }
  .shell { display: grid; grid-template-columns: 244px minmax(0, 1fr); min-height: 100dvh; }
  .shell[hidden] { display: none; }
  .sidebar { position: sticky; top: 0; height: 100dvh; overflow-y: auto; display: flex; flex-direction: column; padding: 28px 16px 20px; background: var(--card); border-right: 1px solid var(--border); }
  .brand { display: flex; align-items: center; gap: 12px; padding: 0 10px 32px; }
  .brand strong { display: block; font-size: 17px; letter-spacing: -.035em; }
  .brand small { display: block; color: var(--muted-foreground); font-size: 11px; margin-top: 2px; }
  .logo { flex-shrink: 0; }
  .nav-caption { margin: 8px 12px 10px; font-size: 11px; font-weight: 500; color: var(--muted-foreground); }
  nav { display: grid; gap: 5px; }
  nav button { display: flex; align-items: center; gap: 11px; padding: 11px 12px; background: transparent; border: 1px solid transparent; color: var(--muted-foreground); text-align: left; font-size: 13px; font-weight: 500; }
  nav button:hover:not(:disabled) { background: var(--secondary); color: var(--foreground); }
  nav button.active { background: var(--secondary); color: var(--foreground); border-color: var(--border); box-shadow: inset 2px 0 var(--primary); }
  nav button.active :global(svg) { color: var(--ring); }
  nav button :global(svg) { flex-shrink: 0; }
  nav .nav-caption { margin-top: 28px; }
  .account { margin-top: auto; padding: 24px 10px 0; display: grid; gap: 4px; border-top: 1px solid var(--border); }
  .account strong { overflow-wrap: anywhere; font-size: 13px; font-weight: 600; }
  .account small { color: var(--muted-foreground); font-size: 11px; }
  .account button { display: flex; justify-content: center; align-items: center; gap: 8px; margin-top: 14px; font-size: 12px; }
  .workspace { min-width: 0; }
  .page-header { display: flex; justify-content: space-between; align-items: center; gap: 24px; padding: 28px 36px; border-bottom: 1px solid var(--border); background: var(--background); }
  .eyebrow { margin: 0 0 6px; font-size: 12px; color: var(--muted-foreground); }
  h1 { margin: 0; font-size: clamp(23px, 2.2vw, 29px); line-height: 1.25; letter-spacing: -.035em; font-weight: 600; overflow-wrap: anywhere; }
  .page-body { max-width: 1380px; padding: 32px 36px 48px; margin: 0 auto; }
  .header-status { flex-shrink: 0; }
  .boot { text-align: center; padding: 20vh 20px; color: var(--muted-foreground); }
  .auth-error { color: var(--destructive); text-align: center; margin: 24px 16px 0; }
  .shell.editor-mode { height: 100dvh; overflow: hidden; grid-template-columns: 208px minmax(0, 1fr); }
  .workspace.editor-mode { min-height: 0; display: flex; flex-direction: column; }
  .workspace.editor-mode .page-header { flex-shrink: 0; padding: 16px 22px; }
  .workspace.editor-mode h1 { font-size: 20px; }
  .page-body.editor-page { flex: 1; min-height: 0; width: 100%; max-width: none; margin: 0; padding: 0; overflow: hidden; }
  .shell.editor-mode .sidebar { padding-left: 12px; padding-right: 12px; }
  .shell.editor-mode .brand { padding: 0 2px 26px; }
  .shell.editor-mode nav button { padding: 10px 8px; gap: 8px; font-size: 12px; }
  @media (max-width: 1100px) { .shell { grid-template-columns: 210px minmax(0, 1fr); } .page-header { padding: 24px; } .page-body { padding: 24px; } }
  @media (max-width: 700px) {
    .shell { display: block; }
    .sidebar { height: auto; position: static; padding: 16px; border-right: 0; border-bottom: 1px solid var(--border); }
    .brand { padding: 0 0 16px; }
    .nav-caption, nav .nav-caption { display: none; }
    nav { display: flex; flex-wrap: wrap; gap: 6px; }
    nav button { padding: 8px 10px; gap: 7px; font-size: 12px; }
    .account { margin-top: 16px; padding: 12px 0 0; grid-template-columns: 1fr auto; align-items: center; }
    .account small { grid-column: 1; }
    .account button { grid-column: 2; grid-row: 1 / 3; margin: 0; }
    .page-header { padding: 22px 16px; }
    .page-body { padding: 22px 16px 32px; }
    .header-status { display: none; }
    .shell.editor-mode { display: flex; flex-direction: column; min-height: 100dvh; }
    .shell.editor-mode .sidebar { height: auto; flex-shrink: 0; padding: 12px; }
    .shell.editor-mode .brand { padding-bottom: 12px; }
    .shell.editor-mode .account { display: none; }
    .workspace.editor-mode { flex: 1; }
    .workspace.editor-mode .page-header { padding: 12px 16px; }
    .workspace.editor-mode .page-header h1 { font-size: 17px; }
    .workspace.editor-mode .eyebrow { display: none; }
  }
</style>
