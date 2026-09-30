<script lang="ts">
  import { onMount } from 'svelte';
  import { getToken, setToken, me, type AuthResponse, type CatalogTaskDTO } from './api';
  import { getSettings, type SettingsSnapshot, type SettingsDraft, type TaskDraft } from './consoleApi';
  import Login from './components/Login.svelte'; import Overview from './components/Overview.svelte';
  import StudentList from './components/StudentList.svelte'; import StudentDetail from './components/StudentDetail.svelte';
  import StudioWorkspace from './components/StudioWorkspace.svelte';
  import Settings from './components/Settings.svelte'; import Assistant from './components/Assistant.svelte';
  type View = 'overview' | 'students' | 'catalog' | 'settings' | 'assistant';
  const titles: Record<View, string> = { overview: 'Обзор сервиса', students: 'Пользователи', catalog: 'Редактор задач', settings: 'Настройки сервиса', assistant: 'AI-помощник' };
  let view = $state<View>((Object.keys(titles).includes(location.hash.slice(1)) ? location.hash.slice(1) : 'overview') as View);
  let loggedIn = $state(false); let sessionSeen = $state(false); let checking = $state(true);
  let userRole = $state(''); let username = $state(''); let userId = $state(''); let authError = $state('');
  let serviceName = $state('Ego Trainer'); let version = $state(''); let dirty = $state(false); let workBusy = $state(false);
  let selectedStudent = $state<{ id: string; username: string } | null>(null);
  let selectedTask = $state<Pick<CatalogTaskDTO, 'id' | 'task_id'> | null>(null);
  let settingsDraft = $state<SettingsDraft | null>(null); let taskDraft = $state<TaskDraft | null>(null);
  const isAdmin = $derived(userRole === 'admin');
  async function brand() { if (userRole !== 'admin') return; try { const data = await getSettings(); saved(data); } catch {} }
  function saved(data: SettingsSnapshot) { serviceName = data.config.service_name; version = data.runtime.version; }
  function accept(data: { user_id: string; username: string; role: string }) {
    if (data.role === 'student') { setToken(null); authError = 'Админка доступна наставникам и администраторам.'; return; }
    if (userId && userId !== data.user_id) { selectedTask = null; selectedStudent = null; taskDraft = null; settingsDraft = null; dirty = false; view = 'overview'; }
    userId = data.user_id; username = data.username; userRole = data.role; authError = ''; loggedIn = true; sessionSeen = true;
    if (userRole !== 'admin' && (view === 'settings' || view === 'assistant')) view = 'overview';
    void brand();
  }
  async function restoreSession() { try { if (getToken()) accept(await me()); } catch { setToken(null); } finally { checking = false; } }
  function handleLogin(data: AuthResponse) { if (data.role !== 'student') setToken(data.access_token); accept(data); }
  function navTo(next: View): boolean {
    if (workBusy) return false;
    if (next === view) return true;
    if (dirty && !confirm('Есть несохранённые изменения. Перейти и отбросить их?')) return false;
    dirty = false; view = next; selectedStudent = null; selectedTask = null; settingsDraft = null; taskDraft = null;
    history.replaceState(null, '', '#' + next); return true;
  }
  function logout() { if (workBusy || (dirty && !confirm('Есть несохранённые изменения. Выйти и отбросить их?'))) return; dirty = false; selectedTask = null; selectedStudent = null; taskDraft = null; settingsDraft = null; view = 'overview'; history.replaceState(null, '', '#overview'); setToken(null); loggedIn = false; sessionSeen = false; userRole = ''; username = ''; userId = ''; }
  function reviewSettings(draft: SettingsDraft) { if (navTo('settings')) settingsDraft = draft; }
  function reviewTask(draft: TaskDraft) { if (view === 'catalog' || navTo('catalog')) { selectedTask = { id: draft.task_id, task_id: draft.task_id }; taskDraft = draft; } }
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
    <aside class="sidebar"><div class="brand"><span class="logo">e</span><div><strong>{serviceName}</strong><small>Панель управления</small></div></div>
      <p class="nav-caption">Рабочее пространство</p><nav aria-label="Навигация админки">
        <button class:active={view === 'overview'} disabled={workBusy} onclick={() => navTo('overview')} aria-current={view === 'overview' ? 'page' : undefined}><span>◫</span> Обзор</button>
        <button class:active={view === 'students'} disabled={workBusy} onclick={() => navTo('students')} aria-current={view === 'students' ? 'page' : undefined}><span>♙</span> Пользователи</button>
        <button class:active={view === 'catalog'} disabled={workBusy} onclick={() => navTo('catalog')} aria-current={view === 'catalog' ? 'page' : undefined}><span>▤</span> Каталог задач</button>
        {#if isAdmin}<p class="nav-caption">Администрирование</p><button class:active={view === 'assistant'} disabled={workBusy} onclick={() => navTo('assistant')} aria-current={view === 'assistant' ? 'page' : undefined}><span>✦</span> AI-помощник</button><button class:active={view === 'settings'} disabled={workBusy} onclick={() => navTo('settings')} aria-current={view === 'settings' ? 'page' : undefined}><span>⚙</span> Настройки</button>{/if}
      </nav>
      <div class="account"><strong>{username}</strong><small>{isAdmin ? 'Администратор' : 'Наставник'}{version ? ` · v${version}` : ''}</small><button disabled={workBusy} onclick={logout}>Выйти из аккаунта</button></div>
    </aside>
    <section class="workspace" class:editor-mode={view === 'catalog'}><header class="page-header"><div><p class="eyebrow">{serviceName}</p><h1>{selectedTask ? `Редактор · ${selectedTask.task_id}` : selectedStudent ? `Прогресс: ${selectedStudent.username}` : titles[view]}</h1></div><div class="header-status">{#if dirty}<span class="unsaved">● Несохранённые изменения</span>{:else}<span class="online">●</span> Сервис доступен{/if}</div></header>
      <div class="page-body" class:editor-page={view === 'catalog'}>
        {#if view === 'overview'}<Overview />
        {:else if view === 'students'}{#if selectedStudent}<StudentDetail studentId={selectedStudent.id} username={selectedStudent.username} onBack={() => { selectedStudent = null; }} />{:else}<StudentList {userRole} onSelect={(id, name) => { selectedStudent = { id, username: name }; }} />{/if}
        {:else if view === 'catalog'}<StudioWorkspace role={userRole} initialTaskId={taskDraft?.task_id || ''} draft={taskDraft} onSettings={() => navTo('settings')} onReviewSettings={reviewSettings} onBusyChange={(value) => { workBusy = value; }} onDirtyChange={(value) => { dirty = value; }} onActiveTask={(id, label) => { selectedTask = id ? { id, task_id: label } : null; }} />
        {:else if view === 'settings' && isAdmin}<Settings draft={settingsDraft} onBusyChange={(value) => { workBusy = value; }} onDirtyChange={(value) => { dirty = value; }} onSaved={saved} />
        {:else if view === 'assistant' && isAdmin}<Assistant onSettings={() => navTo('settings')} onReviewSettings={reviewSettings} onReviewTask={reviewTask} />{/if}
      </div>
    </section>
  </main>
{/if}

<style>
  :global(html), :global(body) { margin: 0; min-height: 100%; background: #171b21; color: #dce3ed; font: 14px/1.5 'Segoe UI', system-ui, sans-serif; }
  :global(*) { box-sizing: border-box; } :global(button), :global(input), :global(select), :global(textarea) { font: inherit; }
  :global(button) { padding: 8px 12px; border: 1px solid #3b4654; border-radius: 6px; background: #252d38; color: #dce3ed; cursor: pointer; }
  :global(button:hover:not(:disabled)) { border-color: #8cbaff; background: #2d394b; } :global(button:disabled) { opacity: .5; cursor: not-allowed; }
  :global(button.primary) { background: #aac9fb; color: #13223b; border-color: #aac9fb; font-weight: 600; } :global(button.primary:hover:not(:disabled)) { background: #c1d8ff; }
  :global(input), :global(select), :global(textarea) { background: #202731; color: #e7edf6; border: 1px solid #3b4654; border-radius: 6px; padding: 10px 12px; }
  :global(input:focus), :global(select:focus), :global(textarea:focus) { outline: 2px solid #8cbaff; outline-offset: 1px; }
  .shell { display: grid; grid-template-columns: 224px minmax(0, 1fr); min-height: 100vh; } .shell[hidden] { display: none; }
  .sidebar { position: sticky; top: 0; height: 100vh; background: #191e26; border-right: 1px solid #303946; display: flex; flex-direction: column; padding: 26px 16px 18px; }
  .brand { display: flex; gap: 10px; align-items: center; padding: 0 8px 30px; } .brand strong { font-size: 15px; letter-spacing: -.02em; display: block; } .brand small { color: #8e9aaa; font-size: 11px; }
  .logo { font-size: 24px; line-height: 36px; width: 36px; text-align: center; color: #18283f; background: #aac9fb; font-weight: 700; border-radius: 10px; }
  .nav-caption { font-size: 10px; text-transform: uppercase; letter-spacing: .1em; color: #7f8a9c; padding: 0 10px; margin: 8px 0 12px; }
  nav { display: grid; gap: 5px; } nav button { display: flex; gap: 11px; align-items: center; background: transparent; border-color: transparent; text-align: left; padding: 11px 12px; color: #a6b3c7; }
  nav button span { width: 18px; font-size: 17px; } nav button.active { background: #2c3b52; color: #d4e5ff; border-color: #405677; } nav .nav-caption { margin-top: 25px; }
  .account { margin-top: auto; display: grid; gap: 7px; padding: 18px 8px 0; border-top: 1px solid #303946; } .account small { color: #8e9aaa; } .account button { margin-top: 6px; font-size: 11px; }
  .workspace { min-width: 0; }
  .shell.editor-mode { height: 100dvh; overflow: hidden; grid-template-columns: 184px minmax(0, 1fr); }
  .workspace.editor-mode { min-height: 0; display: flex; flex-direction: column; }
  .workspace.editor-mode .page-header { flex-shrink: 0; padding: 14px 20px; }
  .page-body.editor-page { flex: 1; min-height: 0; width: 100%; max-width: none; margin: 0; padding: 0; overflow: hidden; }
  .shell.editor-mode .brand { padding-left: 0; gap: 8px; }
  .shell.editor-mode .brand strong { font-size: 13px; }
  .shell.editor-mode .sidebar { padding-left: 10px; padding-right: 10px; }
  .shell.editor-mode nav button { font-size: 12px; padding: 10px 8px; gap: 7px; }
  :global(.monaco-editor textarea.inputarea) { border: 0; padding: 0; outline: none; }  .page-header { display: flex; justify-content: space-between; align-items: center; gap: 20px; padding: 22px 32px; border-bottom: 1px solid #303946; }
  .eyebrow { color: #8e9aaa; font-size: 11px; margin: 0 0 5px; } h1 { font-size: 22px; letter-spacing: -.025em; margin: 0; font-weight: 600; }
  .page-body { padding: 26px 32px; max-width: 1600px; margin: 0 auto; } .header-status { font-size: 11px; color: #8e9aaa; white-space: nowrap; } .online { color: #76c4aa; padding-right: 6px; } .unsaved { color: #e8b86e; }
  .boot { text-align: center; padding: 20vh 20px; color: #a6b3c7; } .auth-error { color: #ffb4bb; text-align: center; margin: 25px 20px 0; }
  @media (max-width: 1000px) { .shell { grid-template-columns: 190px minmax(0, 1fr); } .page-body, .page-header { padding: 20px; } .header-status { display: none; } }
  @media (max-width: 700px) { .shell { display: block; } .sidebar { height: auto; position: static; padding: 14px; border-right: 0; border-bottom: 1px solid #303946; } .brand { padding-bottom: 12px; } nav { display: flex; flex-wrap: wrap; gap: 4px; } nav button { padding: 8px; font-size: 12px; } .nav-caption, nav .nav-caption, .account small { display: none; } .account { margin-top: 10px; display: flex; justify-content: space-between; align-items: center; padding-top: 10px; } .account button { margin-top: 0; } .page-header { padding: 18px 14px; } .page-body { padding: 14px; } h1 { font-size: 20px; } }
  @media (max-width: 700px) { .shell.editor-mode { display: flex; flex-direction: column; min-height: 100dvh; } .shell.editor-mode .sidebar { height: auto; flex-shrink: 0; } .workspace.editor-mode { flex: 1; } .workspace.editor-mode .page-header { padding: 10px 14px; } .workspace.editor-mode .page-header h1 { font-size: 16px; } .shell.editor-mode .brand { padding-bottom: 6px; } .shell.editor-mode .account { margin-top: 6px; padding-top: 6px; } }
</style>
