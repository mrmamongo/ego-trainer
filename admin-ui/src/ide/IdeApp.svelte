<script lang="ts">
  import { onMount } from 'svelte';
  import * as monaco from 'monaco-editor/esm/vs/editor/editor.api';
  import 'monaco-editor/esm/vs/basic-languages/markdown/markdown.contribution';
  import 'monaco-editor/esm/vs/basic-languages/python/python.contribution';
  import 'monaco-editor/esm/vs/editor/contrib/find/browser/findController';
  import 'monaco-editor/esm/vs/editor/contrib/folding/browser/folding';
  import 'monaco-editor/min/vs/editor/editor.main.css';
  import {
    ideLogin,
    ideMe,
    listTasks,
    getTask,
    runCheck,
    setIdeToken,
    getIdeToken,
    clearIdeToken,
    authProviders,
    startForgejo,
    exchangeForgejo,
    type AuthProviders,
  } from './api';
  import { workspaceStore } from './workspace';
  import { readIdeRoute, findIdeFileForTask, findIdeTaskForId, ideRoomUrl } from './route.js';
  import { getShareRoom, createShareRoom } from './api';
  import {
    IdeCollabSession,
    collabRoomFor,
    type CollabStatus,
    type Peer,
  } from './collab';

  type Screen = 'boot' | 'login' | 'ready';

  type WorkspaceFile = {
    id: string;
    name: string;
    language: string;
    task_id?: string | null;
    content?: string;
    updated_at?: string;
  };

  type TaskMeta = {
    id?: number | string;
    task_id: string;
    title?: string;
    block?: string;
    slug?: string;
    tags?: string[];
  };

  type TaskFull = TaskMeta & { stub_py?: string | null };

  type TestItem = {
    description?: string;
    passed?: boolean;
    expected_repr?: string | null;
    actual_repr?: string | null;
    error?: string | null;
  };

  type CheckResult = {
    status?: string;
    passed_tests?: number;
    total_tests?: number;
    results?: TestItem[];
    error?: string | null;
    message?: string;
  };

  type MeResponse = { username?: string; user_id?: string | number; role?: string };

  const SEARCH_DEBOUNCE_MS = 300;
  const AUTOSAVE_DEBOUNCE_MS = 400;
  const ROUTE_NOTICE_MS = 4000;

  let screen = $state<Screen>('boot');
  let username = $state('');
  let loginValue = $state('');
  let passwordValue = $state('');
  let loginError = $state('');
  let loginBusy = $state(false);
  let providers = $state<AuthProviders | null>(null);
  let forgejoBusy = $state(false);
  let forgejoAttempt = 0;
  let forgejoPopup: Window | null = null;
  let forgejoChannel: BroadcastChannel | null = null;

  let files = $state<WorkspaceFile[]>([]);
  let filesError = $state('');
  let activeFileId = $state<string | null>(null);
  let activeFile = $derived(files.find((file) => file.id === activeFileId) ?? null);

  let newFileOpen = $state(false);
  let newFileName = $state('');
  let newFileBusy = $state(false);
  let newFileError = $state('');

  let renamingId = $state<string | null>(null);
  let renameValue = $state('');
  let renameBusy = $state(false);
  let renameError = $state('');

  let tasks = $state<TaskMeta[]>([]);
  let tasksError = $state('');
  let taskSearch = $state('');
  let taskSearchDebounced = $state('');
  let exportBusyId = $state<string | null>(null);
  let exportError = $state('');

  let testsOpen = $state(true);
  let checkRunning = $state(false);
  let checkResult = $state<CheckResult | null>(null);
  let checkError = $state('');
  let bindTaskId = $state('');

  let dirty = $state(false);
  let savedAt = $state<Date | null>(null);
  let storeNotice = $state('');

  // --- Deeplink /ide/task/<task_id> и /ide/room/<room_id> (ссылки) ---
  let pendingTaskId = $state<string | null>(null);
  let pendingRoomId = $state<string | null>(null);
  let routeNotice = $state('');
  let routeError = $state('');
  let routeNoticeTimer: ReturnType<typeof setTimeout> | undefined;
  // Активная share-комната: непрозрачный id + задача, к которой она привязана.
  let sharedRoomId = $state<string | null>(null);
  let sharedRoomTaskId = $state<string | null>(null);
  let sharedRoomTitle = $state('');

  let editorHost = $state<HTMLDivElement>();
  let editor: monaco.editor.IStandaloneCodeEditor | undefined;
  let editorReady = $state(false);
  let activeModelId: string | undefined;
  const models = new Map<string, monaco.editor.ITextModel>();
  const viewStates = new Map<string, monaco.editor.ICodeEditorViewState>();
  const workers = new Set<Worker>();
  let disposed = false;
  let searchTimer: ReturnType<typeof setTimeout> | undefined;
  let autosaveTimer: ReturnType<typeof setTimeout> | undefined;

  // --- Совместное редактирование (ADR-0017, P1) ---
  let collabEnabled = $state(true);
  let collabStatus = $state<CollabStatus>('off');
  let collabDetail = $state('');
  let peers = $state<Peer[]>([]);
  let collabPopoverOpen = $state(false);
  let collabSession: IdeCollabSession | null = null;
  let collabRoom = $state('');

  const filteredTasks = $derived.by(() => {
    const query = taskSearchDebounced.trim().toLowerCase();
    if (!query) return tasks;
    return tasks.filter((task) => {
      const title = (task.title ?? '').toLowerCase();
      const taskId = (task.task_id ?? '').toLowerCase();
      const block = (task.block ?? '').toLowerCase();
      const tags = Array.isArray(task.tags) ? task.tags.join(' ').toLowerCase() : '';
      return title.includes(query) || taskId.includes(query) || block.includes(query) || tags.includes(query);
    });
  });

  const statusTone = $derived.by(() => {
    const status = (checkResult?.status ?? '').toLowerCase();
    if (status === 'passed') return 'success';
    if (status === 'failed' || status === 'partial') return 'warning';
    if (status) return 'destructive';
    return '';
  });

  const statusLabel = $derived.by(() => {
    const status = (checkResult?.status ?? '').toLowerCase();
    if (!status) return '';
    if (status === 'passed') return 'Пройдено';
    if (status === 'failed') return 'Не пройдено';
    if (status === 'partial') return 'Частично пройдено';
    if (status === 'timeout') return 'Превышено время';
    return 'Ошибка';
  });

  const autosaveLabel = $derived.by(() => {
    if (dirty) return 'Есть несохранённые изменения';
    if (!savedAt) return 'Готово к работе';
    return `Сохранено ${savedAt.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })}`;
  });

  const collabStatusLabel = $derived.by(() => {
    if (collabStatus === 'connecting') return 'Подключаюсь…';
    if (collabStatus === 'syncing') return 'Синхронизация…';
    if (collabStatus === 'live') return `Онлайн · ${peers.length + 1}`;
    if (collabStatus === 'error') return 'Ошибка связи';
    return 'Совм. режим выключен';
  });

  const collabParticipants = $derived(peers.length + 1);

  function initials(name: string): string {
    const parts = name.trim().split(/\s+/).filter(Boolean);
    if (parts.length === 0) return '?';
    return parts.slice(0, 2).map((part) => part[0]).join('').toUpperCase();
  }

  function sanitizeName(value: string): string {
    return value
      .replace(/[^A-Za-z0-9_]/g, '_')
      .replace(/_{2,}/g, '_')
      .replace(/^_+/, '')
      .replace(/_+$/, '');
  }

  function formatUpdated(value?: string): string {
    if (!value) return '';
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return '';
    return date.toLocaleString('ru-RU', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' });
  }

  function modelFor(file: WorkspaceFile): monaco.editor.ITextModel {
    let model = models.get(file.id);
    if (!model || model.isDisposed()) {
      model = monaco.editor.createModel(
        file.content ?? '',
        file.language,
        monaco.Uri.parse(`ego-ide:///${encodeURIComponent(file.id)}`),
      );
      model.onWillDispose(() => { models.delete(file.id); });
      models.set(file.id, model);
    }
    return model;
  }

  function saveCurrentViewState() {
    if (!editor || !activeModelId) return;
    const previousModel = models.get(activeModelId);
    if (!previousModel || previousModel.isDisposed()) return;
    const previousState = editor.saveViewState();
    if (previousState) viewStates.set(activeModelId, previousState);
  }

  function swapModel(file: WorkspaceFile | null) {
    if (!editor) return;
    const documentChanged = activeModelId !== file?.id;
    if (!file) {
      if (documentChanged) saveCurrentViewState();
      activeModelId = undefined;
      editor.setModel(null);
      return;
    }
    const model = modelFor(file);
    if (documentChanged) {
      saveCurrentViewState();
      activeModelId = file.id;
      editor.setModel(model);
      const savedState = viewStates.get(file.id);
      if (savedState) editor.restoreViewState(savedState);
      // После смены файла перерассчитываем «грязь»: модель — источник истины.
      dirty = model.getValue() !== (file.content ?? '');
      editor.focus();
    }
  }

  function editorValue(): string {
    return editor?.getValue() ?? activeFile?.content ?? '';
  }

  async function persistContent(fileId: string, content: string) {
    try {
      await workspaceStore.updateFile(fileId, { content });
      if (disposed) return;
      files = files.map((item) => (item.id === fileId ? { ...item, content } : item));
      // «Грязь» пересчитываем только для активного файла: фоновый автосейв другого файла
      // не должен помечать текущий.
      if (activeFileId === fileId) dirty = editor ? editor.getValue() !== content : false;
      savedAt = new Date();
      storeNotice = '';
    } catch (e) {
      if (disposed) return;
      storeNotice = `Не удалось сохранить: ${(e as Error).message}`;
    }
  }

  function scheduleAutosave(fileId: string, content: string) {
    if (autosaveTimer) clearTimeout(autosaveTimer);
    autosaveTimer = setTimeout(() => {
      autosaveTimer = undefined;
      if (disposed) return;
      void persistContent(fileId, content);
    }, AUTOSAVE_DEBOUNCE_MS);
  }

  function onEditorContentChange() {
    dirty = true;
    storeNotice = '';
    const fileId = activeFileId;
    if (!fileId || !editor) return;
    // При живой коллаб-сессии источник истины — Y.Doc, а не модель Monaco:
    // MonacoBinding уже применил правку к ytext, персистим именно его.
    const content = collabSession?.isAttached() ? collabSession.getDocText() : editor.getValue();
    // Захватываем содержимое сразу: за 400 мс активный файл мог бы смениться.
    scheduleAutosave(fileId, content);
  }

  function saveNow() {
    const fileId = activeFileId;
    if (!fileId || !editor) return;
    if (autosaveTimer) { clearTimeout(autosaveTimer); autosaveTimer = undefined; }
    const content = collabSession?.isAttached() ? collabSession.getDocText() : editor.getValue();
    void persistContent(fileId, content);
  }

  function openFile(id: string) {
    if (id === activeFileId) return;
    const file = files.find((item) => item.id === id);
    if (!file) return;
    activeFileId = id;
    writeMeta(id);
    if (editorReady && editor) swapModel(file);
  }

  function writeMeta(id: string) {
    void workspaceStore.writeMeta({ lastOpenedFileId: id }).catch(() => { /* мета необязательна */ });
  }

  async function readMetaLastOpened(): Promise<string | null> {
    try {
      const meta = await workspaceStore.readMeta();
      return meta?.lastOpenedFileId ?? null;
    } catch {
      return null;
    }
  }

  async function refreshFiles(): Promise<WorkspaceFile[]> {
    const list = await workspaceStore.listFiles();
    if (disposed) return [];
    files = list;
    return list;
  }

  async function pickActiveFile(list: WorkspaceFile[]): Promise<WorkspaceFile | null> {
    const last = await readMetaLastOpened();
    if (last) {
      const restored = list.find((file) => file.id === last);
      if (restored) return restored;
    }
    return list[0] ?? null;
  }

  function startCreate() {
    newFileOpen = true;
    newFileName = '';
    newFileError = '';
    newFileBusy = false;
  }

  async function submitCreate() {
    const name = newFileName.trim();
    if (!name) { newFileError = 'Введи имя файла'; return; }
    newFileBusy = true; newFileError = '';
    try {
      const created = await workspaceStore.createFile({ name, language: 'python', content: '' });
      if (disposed) return;
      await refreshFiles();
      if (disposed) return;
      openFile(created.id);
      newFileOpen = false;
      newFileName = '';
    } catch (e) {
      if (!disposed) newFileError = (e as Error).message;
    } finally {
      if (!disposed) newFileBusy = false;
    }
  }

  function startRename(file: WorkspaceFile) {
    renamingId = file.id;
    renameValue = file.name;
    renameError = '';
    renameBusy = false;
  }

  async function submitRename() {
    const id = renamingId;
    const name = renameValue.trim();
    if (!id) return;
    if (!name) { renameError = 'Введи имя файла'; return; }
    renameBusy = true; renameError = '';
    try {
      await workspaceStore.updateFile(id, { name });
      if (disposed) return;
      await refreshFiles();
      if (!disposed) { renamingId = null; renameValue = ''; }
    } catch (e) {
      if (!disposed) renameError = (e as Error).message;
    } finally {
      if (!disposed) renameBusy = false;
    }
  }

  async function removeFile(file: WorkspaceFile) {
    if (!window.confirm(`Удалить файл «${file.name}»?`)) return;
    const wasActive = file.id === activeFileId;
    try {
      await workspaceStore.deleteFile(file.id);
      if (disposed) return;
      if (wasActive && editor) editor.setModel(null);
      const model = models.get(file.id);
      if (model && !model.isDisposed()) model.dispose();
      viewStates.delete(file.id);
      const list = await refreshFiles();
      if (disposed) return;
      if (wasActive) {
        const next = await pickActiveFile(list);
        if (disposed) return;
        activeFileId = next?.id ?? null;
        if (next && editorReady && editor) swapModel(next);
      }
    } catch (e) {
      if (!disposed) storeNotice = `Не удалось удалить: ${(e as Error).message}`;
    }
  }

  async function exportTask(task: TaskMeta) {
    const taskId = task.task_id;
    exportError = '';
    exportBusyId = taskId;
    try {
      const detail: TaskFull = await getTask(taskId);
      if (disposed) return;
      const block = sanitizeName(task.block ?? 'task');
      const slug = sanitizeName(task.slug ?? taskId);
      const created = await workspaceStore.importTaskFile({
        task_id: taskId,
        name: `${block}_${slug}.py`,
        language: 'python',
        content: detail.stub_py || '# нет стартового кода\n',
      });
      if (disposed) return;
      await refreshFiles();
      if (disposed) return;
      if (created && typeof created.id === 'string') openFile(created.id);
    } catch (e) {
      if (!disposed) exportError = (e as Error).message;
    } finally {
      if (!disposed) exportBusyId = null;
    }
  }

  // --- Deeplink /ide/task/<task_id>: открыть задачу по ссылке ---

  function clearRouteNotice() {
    routeNotice = '';
    if (routeNoticeTimer) { clearTimeout(routeNoticeTimer); routeNoticeTimer = undefined; }
  }

  function showRouteNotice(message: string) {
    routeNotice = message;
    if (routeNoticeTimer) clearTimeout(routeNoticeTimer);
    routeNoticeTimer = setTimeout(() => {
      routeNoticeTimer = undefined;
      if (!disposed) routeNotice = '';
    }, ROUTE_NOTICE_MS);
  }

  function cleanDeepLinkUrl() {
    try {
      history.replaceState(null, '', '/ide');
    } catch {
      /* история недоступна — не критично */
    }
  }

  /**
   * Разрешить ссылку вида /ide/task/<task_id> после загрузки файлов и задач.
   * Существующий файл открываем, иначе выгружаем заготовку через exportTask.
   */
  async function resolveDeepLink(taskId: string) {
    const task = findIdeTaskForId(tasks, taskId);
    if (!task) {
      routeError = `Задача «${taskId}» не найдена`;
      cleanDeepLinkUrl();
      return;
    }
    const existing = findIdeFileForTask(files, taskId);
    if (existing) {
      openFile(existing.id);
      showRouteNotice('Открыта задача из ссылки');
      cleanDeepLinkUrl();
      return;
    }
    await exportTask(task);
    if (disposed) return;
    if (exportError) {
      // Ошибка выгрузки уже показана в сайдбаре (exportError) — оставляем её.
      cleanDeepLinkUrl();
      return;
    }
    showRouteNotice('Задача выгружена по ссылке');
    cleanDeepLinkUrl();
  }

  /**
   * Разрешить ссылку вида /ide/room/<room_id>: проверить share-комнату,
   * найти/выгрузить файл её задачи и включить режим этой комнаты.
   */
  async function resolveRoomLink(roomId: string) {
    let share: Awaited<ReturnType<typeof getShareRoom>>;
    try {
      share = await getShareRoom(roomId);
    } catch (e) {
      routeError = `Комната не найдена или закрыта (${(e as Error).message})`;
      cleanDeepLinkUrl();
      return;
    }
    if (disposed) return;
    const task = findIdeTaskForId(tasks, share.task_id);
    if (!task) {
      routeError = `Задача комнаты «${share.task_id}» не найдена`;
      cleanDeepLinkUrl();
      return;
    }
    const existing = findIdeFileForTask(files, share.task_id);
    if (!existing) {
      await exportTask(task);
      if (disposed) return;
      if (exportError) {
        cleanDeepLinkUrl();
        return;
      }
    } else {
      openFile(existing.id);
    }
    if (disposed) return;
    // Файл задачи готов; после refreshFiles возьмём актуальный id.
    const list = await refreshFiles();
    if (disposed) return;
    const target = findIdeFileForTask(list, share.task_id);
    if (target) openFile(target.id);
    sharedRoomId = share.room_id;
    sharedRoomTaskId = share.task_id;
    sharedRoomTitle = share.title || share.task_id;
    showRouteNotice(`Ты в комнате: ${sharedRoomTitle}`);
    cleanDeepLinkUrl();
  }

  // --- Share-комната для активной задачи (ментор) ---

  let shareBusy = $state(false);
  let shareError = $state('');
  let shareCopied = $state(false);
  const shareRoomLink = $derived(sharedRoomId ? ideRoomUrl(sharedRoomId) : '');

  async function createRoomForActiveTask() {
    const task = activeFile;
    if (!task?.task_id || shareBusy) return;
    shareBusy = true;
    shareError = '';
    try {
      const share = await createShareRoom(task.task_id, task.name || task.task_id);
      if (disposed) return;
      sharedRoomId = share.room_id;
      sharedRoomTaskId = share.task_id;
      sharedRoomTitle = share.title || share.task_id;
      showRouteNotice(`Комната создана: скопируй ссылку в панели «Тесты»`);
    } catch (e) {
      if (!disposed) shareError = `Не удалось создать комнату: ${(e as Error).message}`;
    } finally {
      if (!disposed) shareBusy = false;
    }
  }

  async function copyShareLink() {
    try {
      await navigator.clipboard.writeText(location.origin + shareRoomLink);
      shareCopied = true;
      setTimeout(() => { if (!disposed) shareCopied = false; }, 2000);
    } catch {
      shareError = 'Не удалось скопировать — выдели ссылку и скопируй вручную.';
    }
  }

  async function submitBind() {    const file = activeFile;
    const taskId = bindTaskId.trim();
    if (!file || !taskId) return;
    checkError = '';
    try {
      await workspaceStore.updateFile(file.id, { task_id: taskId });
      if (disposed) return;
      bindTaskId = '';
      await refreshFiles();
    } catch (e) {
      if (!disposed) checkError = `Не удалось привязать: ${(e as Error).message}`;
    }
  }

  async function runTests() {
    const file = activeFile;
    if (!file?.task_id || checkRunning) return;
    checkRunning = true;
    checkError = '';
    checkResult = null;
    try {
      const result = await runCheck(file.task_id, editorValue());
      if (disposed) return;
      checkResult = result;
    } catch (e) {
      if (!disposed) checkError = (e as Error).message;
    } finally {
      if (!disposed) checkRunning = false;
    }
  }

  async function submitLogin(event: SubmitEvent) {
    event.preventDefault();
    if (!loginValue.trim() || !passwordValue) {
      loginError = 'Введи имя пользователя и пароль';
      return;
    }
    loginBusy = true;
    loginError = '';
    try {
      const data = await ideLogin(loginValue.trim(), passwordValue);
      if (disposed) return;
      setIdeToken(data.access_token);
      await enterWorkspace();
    } catch (e) {
      if (!disposed) loginError = (e as Error).message || 'Не удалось войти. Попробуй снова.';
    } finally {
      if (!disposed) loginBusy = false;
    }
  }

  function cancelForgejo() {
    forgejoAttempt++;
    forgejoPopup?.close();
    forgejoChannel?.close();
    forgejoPopup = null;
    forgejoChannel = null;
    forgejoBusy = false;
  }

  async function forgejoLogin() {
    const current = ++forgejoAttempt;
    loginError = '';
    forgejoBusy = true;
    forgejoPopup = window.open('about:blank', '_blank');
    if (!forgejoPopup) {
      forgejoBusy = false;
      loginError = 'Разреши открытие новой вкладки для входа через Forgejo.';
      return;
    }
    forgejoPopup.opener = null;
    const encode = (bytes: Uint8Array) =>
      btoa(String.fromCharCode(...bytes)).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
    try {
      const verifier = encode(crypto.getRandomValues(new Uint8Array(32)));
      const digest = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(verifier));
      const flow = await startForgejo(encode(new Uint8Array(digest)));
      if (current !== forgejoAttempt) return;
      if (new URL(flow.authorization_url).origin !== location.origin) {
        throw new Error('Адрес входа не совпадает с адресом сервиса. Проверь EGO_PUBLIC_URL.');
      }
      let ticket = '';
      let failed = false;
      forgejoChannel = new BroadcastChannel('ego-forgejo-' + flow.state);
      forgejoChannel.onmessage = (event: MessageEvent) => {
        if ((event.data as { error?: string })?.error === 'login_failed') failed = true;
        const value = (event.data as { ticket?: string })?.ticket;
        if (typeof value === 'string' && /^[A-Za-z0-9_-]{43}$/.test(value)) ticket = value;
      };
      forgejoPopup.location.href = flow.authorization_url;
      const deadline = Date.now() + flow.expires_in * 1000;
      while (current === forgejoAttempt && Date.now() < deadline) {
        await new Promise((resolve) => setTimeout(resolve, 1500));
        if (current !== forgejoAttempt) return;
        if (failed) throw new Error('Вход не завершён или регистрация закрыта. Попробуй снова или обратись к наставнику.');
        if (!ticket) continue;
        const result = await exchangeForgejo(flow.state, verifier, ticket);
        if (current !== forgejoAttempt) return;
        if (!result.pending) {
          cancelForgejo();
          if (disposed) return;
          setIdeToken(result.access_token!);
          await enterWorkspace();
          return;
        }
      }
      if (current === forgejoAttempt) throw new Error('Время входа истекло. Попробуй ещё раз.');
    } catch (e) {
      if (current === forgejoAttempt) {
        loginError = (e as Error).message;
        forgejoPopup?.close();
        forgejoPopup = null;
      }
    } finally {
      if (current === forgejoAttempt) {
        forgejoChannel?.close();
        forgejoChannel = null;
        forgejoBusy = false;
      }
    }
  }

  async function loadTasksOnce() {
    if (tasks.length > 0) return;
    try {
      const list = await listTasks();
      if (disposed) return;
      tasks = list;
    } catch (e) {
      if (!disposed) tasksError = `Не удалось загрузить задачи: ${(e as Error).message}`;
    }
  }

  async function enterWorkspace() {
    let me: MeResponse | null = null;
    try {
      me = await ideMe();
    } catch {
      if (disposed) return;
      clearIdeToken();
      screen = 'login';
      loginError = 'Сессия истекла. Войди снова.';
      return;
    }
    if (disposed) return;
    username = me?.username ?? '';
    screen = 'ready';
    try {
      const list = await refreshFiles();
      if (disposed) return;
      const target = await pickActiveFile(list);
      if (disposed) return;
      activeFileId = target?.id ?? null;
    } catch (e) {
      if (!disposed) filesError = `Не удалось загрузить файлы: ${(e as Error).message}`;
    }
    await loadTasksOnce();
    // Файлы и задачи загружены — можно разрешить ссылки /ide/task и /ide/room.
    const deepRoomId = pendingRoomId;
    if (deepRoomId && screen === 'ready') {
      pendingRoomId = null;
      await resolveRoomLink(deepRoomId);
      return;
    }
    const deepTaskId = pendingTaskId;
    if (deepTaskId && screen === 'ready') {
      pendingTaskId = null;
      await resolveDeepLink(deepTaskId);
    }
  }

  function resetWorkspaceState() {
    stopCollabSession();
    sharedRoomId = null;
    sharedRoomTaskId = null;
    sharedRoomTitle = '';
    pendingRoomId = null;
    files = [];
    activeFileId = null;
    checkResult = null;
    checkError = '';
    bindTaskId = '';
    dirty = false;
    savedAt = null;
    storeNotice = '';
    newFileOpen = false;
    newFileError = '';
    renamingId = null;
    renameError = '';
    exportError = '';
    pendingTaskId = null;
    clearRouteNotice();
    routeError = '';
  }

  function logout() {
    saveNow();
    if (autosaveTimer) { clearTimeout(autosaveTimer); autosaveTimer = undefined; }
    clearIdeToken();
    username = '';
    resetWorkspaceState();
    screen = 'login';
  }

  function handleSessionExpired() {
    if (screen !== 'ready') return;
    logout();
    loginError = 'Сессия истекла. Войди снова.';
  }

  // Коллаб-сессия живёт, пока экран ready и файл с задачей активен: при unmount
  // останавливаем её явно, чтобы не держать открытым websocket после ухода.
  $effect(() => {
    if (screen !== 'ready') stopCollabSession();
  });

  function createEditor(): () => void {
    const previousEnvironment = (window as typeof window & {
      MonacoEnvironment?: { getWorker?: (moduleId: string, label: string) => Worker };
    }).MonacoEnvironment;
    const environmentWindow = window as typeof window & {
      MonacoEnvironment?: { getWorker?: (moduleId: string, label: string) => Worker };
    };
    const editorEnvironment = {
      getWorker: () => {
        const worker = new Worker('/static/admin/workers/editor.worker.js', { type: 'module' });
        workers.add(worker);
        return worker;
      },
    };
    environmentWindow.MonacoEnvironment = editorEnvironment;

    monaco.editor.defineTheme('cogito-dark', {
      base: 'vs-dark',
      inherit: true,
      rules: [],
      colors: {
        'editor.background': '#111113',
        'editor.foreground': '#e4e4e7',
        'editorLineNumber.foreground': '#71717a',
        'editorLineNumber.activeForeground': '#fafafa',
        'editorCursor.foreground': '#60a5fa',
        'editor.selectionBackground': '#2563eb40',
        'editor.inactiveSelectionBackground': '#3f3f4660',
        'editor.lineHighlightBackground': '#18181b',
        'editorGutter.background': '#111113',
        'editorWidget.background': '#18181b',
        'editorWidget.border': '#3f3f46',
        'input.background': '#18181b',
        'input.border': '#3f3f46',
        'dropdown.background': '#18181b',
        'focusBorder': '#3b82f6',
        'scrollbarSlider.background': '#52525b80',
        'editorIndentGuide.background1': '#27272a',
        'editorIndentGuide.activeBackground1': '#52525b',
      },
    });

    const host = editorHost;
    if (!host) return () => {};
    editor = monaco.editor.create(host, {
      model: null,
      theme: 'cogito-dark',
      automaticLayout: true,
      ariaLabel: 'Редактор кода',
      readOnly: false,
      minimap: { enabled: false },
      lineNumbers: 'on',
      folding: true,
      scrollBeyondLastLine: false,
      tabSize: 4,
      fontFamily: 'Consolas, "Cascadia Code", "Courier New", monospace',
      fontSize: 13,
      wordWrap: 'on',
      glyphMargin: false,
    });

    const contentSubscription = editor.onDidChangeModelContent(() => {
      if (!disposed) onEditorContentChange();
    });
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, () => saveNow());
    activeModelId = undefined;
    editorReady = true;

    return () => {
      editorReady = false;
      contentSubscription.dispose();
      editor?.dispose();
      editor = undefined;
      for (const model of models.values()) model.dispose();
      models.clear();
      viewStates.clear();
      for (const worker of workers) worker.terminate();
      workers.clear();
      if (environmentWindow.MonacoEnvironment === editorEnvironment) {
        environmentWindow.MonacoEnvironment = previousEnvironment;
      }
    };
  }

  // Создаём редактор, когда хост-элемент действительно смонтирован (не в onMount: на маунте экран ещё boot/login).
  $effect(() => {
    if (screen !== 'ready' || !editorHost?.isConnected || editor) return;
    return createEditor();
  });

  // Дебаунс поиска задач: 300 мс, фильтрация клиентская.
  $effect(() => {
    const query = taskSearch;
    if (searchTimer) clearTimeout(searchTimer);
    searchTimer = setTimeout(() => {
      searchTimer = undefined;
      if (!disposed) taskSearchDebounced = query;
    }, SEARCH_DEBOUNCE_MS);
    return () => { if (searchTimer) { clearTimeout(searchTimer); searchTimer = undefined; } };
  });

  // Результаты тестов относятся к файлу, для которого их запустили: при смене файла сбрасываем.
  $effect(() => {
    void activeFileId;
    checkResult = null;
    checkError = '';
  });

  // Синхронизация модели Monaco с активным файлом. Модель — источник истины после создания,
  // поэтому содержимое из стора в неё не перезаписываем (иначе затираем правки пользователя).
  $effect(() => {
    if (!editorReady || !editor) return;
    const file = activeFile;
    if (!file) { swapModel(null); return; }
    const model = modelFor(file);
    if (model.getLanguageId() !== file.language && /^[a-z][a-z0-9-]*$/.test(file.language)) {
      monaco.editor.setModelLanguage(model, file.language);
    }
    swapModel(file);
    // Модель смонтирована — теперь безопасно привязывать коллаб-сессию
    // (эффект сессии стартует позже и мог не найти модель). Комнату считаем
    // из текущего файла: коллабRoom ещё держит старое значение при смене файла.
    if (collabSession && file.task_id && collabSession.room === collabRoomFor(file.task_id, file.id)) {
      collabSession.attachEditor(editor, model, file.content ?? '');
    }
  });

  // --- Совместное редактирование: сессия живёт, пока активен файл с задачей ---

  function stopCollabSession() {
    collabSession?.stop();
    collabSession = null;
    collabRoom = '';
    collabStatus = 'off';
    collabDetail = '';
    peers = [];
    collabPopoverOpen = false;
  }

  function continueSolo() {
    // Пользователь явно отказался от коллаба для этой сессии.
    collabEnabled = false;
    stopCollabSession();
  }

  $effect(() => {
    const file = activeFile;
    const taskId = file?.task_id ?? null;
    const fileId = file?.id ?? null;
    const ready = screen === 'ready' && editorReady;
    if (!ready || !taskId || !fileId || !collabEnabled) {
      stopCollabSession();
      return;
    }
    // Активная share-комната перекрывает pair-комнату для СВОЕЙ задачи;
    // файл другой задачи уходит в обычный pair-режим.
    // Грамматика сервера: share:<roomId>:<fileKey> — fileKey обязательный.
    const inSharedRoom = sharedRoomId !== null && sharedRoomTaskId === taskId;
    const room = inSharedRoom ? `share:${sharedRoomId}:main` : collabRoomFor(taskId, fileId);
    if (collabSession && collabSession.room === room) return; // файл не менялся
    stopCollabSession();
    collabRoom = room;
    const session = new IdeCollabSession({
      room,
      getToken: getIdeToken,
      userName: username || 'anon',
      userRole: '',
      onStatus: (status, detail) => {
        if (disposed) return;
        collabStatus = status;
        collabDetail = status === 'error' ? detail ?? '' : '';
      },
      onPeers: (list) => {
        if (disposed) return;
        peers = list;
      },
    });
    session.onTextChange((text) => {
      // Удалённые правки тоже попадают в автосейв — Y.Doc общий для всех.
      if (disposed) return;
      const currentId = activeFileId;
      if (!currentId) return;
      dirty = true;
      scheduleAutosave(currentId, text);
    });
    collabSession = session;
    session.start();
    // Привязка модели происходит в эффекте синхронизации модели (он владеет
    // swapModel и гарантирует актуальную модель); здесь только если модель
    // уже смонтирована этим же файлом.
    if (editor) {
      const model = editor.getModel();
      if (model) session.attachEditor(editor, model, file?.content ?? '');
    }
  });

  onMount(() => {
    const onSessionExpired = () => handleSessionExpired();
    window.addEventListener('ego:ide-session-expired', onSessionExpired);
    void authProviders()
      .then((value) => { if (!disposed) providers = value; })
      .catch(() => { if (!disposed) loginError = 'Не удалось получить способы входа. Обнови страницу.'; });
    // Ссылки /ide/task/<id> и /ide/room/<id> читаем один раз до входа;
    // разрешаем их в enterWorkspace после загрузки файлов и задач.
    const initialRoute = readIdeRoute(window.location);
    if (initialRoute.taskId) pendingTaskId = initialRoute.taskId;
    if (initialRoute.roomId) pendingRoomId = initialRoute.roomId;
    if (getIdeToken()) {
      void enterWorkspace();
    } else {
      screen = 'login';
    }
    return () => {
      disposed = true;
      cancelForgejo();
      stopCollabSession();
      if (searchTimer) clearTimeout(searchTimer);
      if (autosaveTimer) clearTimeout(autosaveTimer);
      if (routeNoticeTimer) clearTimeout(routeNoticeTimer);
      searchTimer = undefined;
      autosaveTimer = undefined;
      routeNoticeTimer = undefined;
      window.removeEventListener('ego:ide-session-expired', onSessionExpired);
    };
  });
</script>

{#if screen === 'boot'}
  <div class="ide-boot" role="status">Проверяю сессию…</div>
{:else if screen === 'login'}
  <div class="login-page">
    <header class="login-topbar">
      <div class="login-brand">
        <img src="/static/branding/cogito-mark.svg" alt="" width="35" height="35" />
        <span>Cogito<small>Учебная платформа</small></span>
      </div>
    </header>
    <div class="login-content">
      <form class="login-card" onsubmit={submitLogin}>
        <div class="login-icon" aria-hidden="true"><span class="login-glyph">&lt;/&gt;</span></div>
        <h1>Cogito Workspace</h1>
        <p class="sub">Пиши код, запускай тесты и следи за прогрессом — в одном окне.</p>
        {#if providers?.forgejo}
          <button class="login-submit forgejo" type="button" onclick={() => void forgejoLogin()} disabled={forgejoBusy || loginBusy}>
            {forgejoBusy ? 'Ожидаю вход в Forgejo…' : 'Войти через Forgejo'}
          </button>
          {#if forgejoBusy}
            <button class="login-submit ghost" type="button" onclick={cancelForgejo}>Отменить вход</button>
          {/if}
        {/if}
        {#if providers?.forgejo && providers?.local}
          <div class="login-divider"><span>или по логину</span></div>
        {/if}
        {#if providers?.local !== false}
          <label class="admin-field">Логин<input type="text" bind:value={loginValue} placeholder="Имя пользователя" autocomplete="username" required disabled={loginBusy || forgejoBusy} /></label>
          <label class="admin-field">Пароль<input type="password" bind:value={passwordValue} placeholder="Твой пароль" autocomplete="current-password" required disabled={loginBusy || forgejoBusy} /></label>
          <button class="login-submit" type="submit" disabled={loginBusy || forgejoBusy}>{loginBusy ? 'Вхожу…' : 'Войти'}</button>
        {/if}
        {#if providers && !providers.forgejo && !providers.local}
          <p class="sub">Вход пока не настроен. Обратись к наставнику.</p>
        {/if}
        {#if loginError}<div class="login-error" role="alert">{loginError}</div>{/if}
      </form>
    </div>
  </div>
{:else}
  <main class="ide">
    <header class="ide-topbar">
      <div class="brand">
        <img src="/static/branding/cogito-mark.svg" alt="" width="30" height="30" />
        <div><strong>Cogito Workspace</strong><small>Учебная среда</small></div>
      </div>
      <div class="topbar-collab">
        <button
          class="collab-chip {collabStatus}"
          onclick={() => (collabPopoverOpen = !collabPopoverOpen)}
          aria-expanded={collabPopoverOpen}
          title={collabStatusLabel}
        >
          <span class="collab-dot {collabStatus}"></span>
          <span class="collab-label">{collabStatusLabel}</span>
          {#if collabStatus === 'live'}
            <span class="collab-avatars">
              {#each peers as peer (peer.clientID)}
                <span class="peer-avatar" style="background:{peer.color}" title="{peer.name}{peer.role ? ' · ' + peer.role : ''}">{initials(peer.name)}</span>
              {/each}
            </span>
          {/if}
        </button>
        {#if collabPopoverOpen}
          <div class="collab-popover">
            {#if collabRoom}
              <div class="collab-room" title={collabRoom}>Комната: {collabRoom}</div>
            {:else}
              <div class="collab-room muted">Совместный режим не активен</div>
            {/if}
            <ul class="collab-peer-list">
              <li><span class="peer-avatar self" style="background:var(--primary)">{initials(username || 'anon')}</span><span class="peer-name">{username || 'anon'} (вы)</span></li>
              {#each peers as peer (peer.clientID)}
                <li><span class="peer-avatar" style="background:{peer.color}">{initials(peer.name)}</span><span class="peer-name">{peer.name}{peer.role ? ` · ${peer.role}` : ''}</span></li>
              {/each}
            </ul>
          </div>
        {/if}
      </div>
      <div class="account">
        {#if username}<span class="account-name">{username}</span>{/if}
        <button class="logout-btn" onclick={logout}>Выйти</button>
      </div>
    </header>

    <div class="ide-body">
      <aside class="sidebar">
        <section class="side-section">
          <div class="side-head">
            <h2>Мои файлы</h2>
            <button class="mini-btn" onclick={() => (newFileOpen ? (newFileOpen = false) : startCreate())} aria-expanded={newFileOpen} title="Новый файл">+ Новый файл</button>
          </div>
          {#if newFileOpen}
            <div class="inline-row">
              <input type="text" bind:value={newFileName} placeholder="например solution.py" onkeydown={(event) => { if (event.key === 'Enter') { event.preventDefault(); void submitCreate(); } if (event.key === 'Escape') newFileOpen = false; }} disabled={newFileBusy} />
              <button class="mini-btn primary" onclick={() => void submitCreate()} disabled={newFileBusy || !newFileName.trim()}>Создать</button>
            </div>
            {#if newFileError}<p class="side-error" role="alert">{newFileError}</p>{/if}
          {/if}
          {#if filesError}<p class="side-error" role="alert">{filesError}</p>{/if}
          {#if files.length === 0 && !filesError}
            <p class="side-empty">Пока нет файлов. Создай новый или выгрузи задачу из каталога.</p>
          {:else}
            <ul class="file-list">
              {#each files as file (file.id)}
                <li class:active={file.id === activeFileId}>
                  {#if renamingId === file.id}
                    <div class="inline-row">
                      <input type="text" bind:value={renameValue} onkeydown={(event) => { if (event.key === 'Enter') { event.preventDefault(); void submitRename(); } if (event.key === 'Escape') renamingId = null; }} disabled={renameBusy} />
                      <button class="mini-btn primary" onclick={() => void submitRename()} disabled={renameBusy || !renameValue.trim()}>ОК</button>
                    </div>
                    {#if renameError}<p class="side-error" role="alert">{renameError}</p>{/if}
                  {:else}
                    <button class="file-open" onclick={() => openFile(file.id)} title={file.name}>
                      <span class="file-name">{file.name}</span>
                      {#if file.updated_at}<small class="file-date">{formatUpdated(file.updated_at)}</small>{/if}
                    </button>
                    <span class="file-actions">
                      {#if file.task_id}<span class="file-task" title="Привязан к задаче">{file.task_id}</span>{/if}
                      <button class="icon-btn" onclick={() => startRename(file)} title="Переименовать" aria-label="Переименовать {file.name}">✎</button>
                      <button class="icon-btn danger" onclick={() => void removeFile(file)} title="Удалить" aria-label="Удалить {file.name}">×</button>
                    </span>
                  {/if}
                </li>
              {/each}
            </ul>
          {/if}
        </section>

        <section class="side-section grow">
          <div class="side-head"><h2>Задачи</h2></div>
          <input class="task-search" type="search" bind:value={taskSearch} placeholder="Поиск задач…" aria-label="Поиск задач" />
          {#if tasksError}<p class="side-error" role="alert">{tasksError}</p>{/if}
          {#if exportError}<p class="side-error" role="alert">{exportError}</p>{/if}
          {#if filteredTasks.length === 0 && !tasksError}
            <p class="side-empty">{tasks.length === 0 ? 'Задачи ещё не загружены.' : 'Ничего не найдено.'}</p>
          {:else}
            <ul class="task-list">
              {#each filteredTasks as task (task.task_id)}
                <li class="task-item">
                  <div class="task-info">
                    {#if task.block}<span class="task-badge">{task.block}</span>{/if}
                    <span class="task-title" title={task.title ?? task.task_id}>{task.title ?? task.task_id}</span>
                  </div>
                  <button class="mini-btn" disabled={exportBusyId === task.task_id} onclick={() => void exportTask(task)}>{exportBusyId === task.task_id ? 'Выгружаю…' : 'Выгрузить'}</button>
                </li>
              {/each}
            </ul>
          {/if}
        </section>
      </aside>

      <section class="editor-pane">
        {#if routeNotice || routeError}
          <div class="route-banner" class:error={!!routeError} role={routeError ? 'alert' : 'status'}>
            {routeError || routeNotice}
          </div>
        {/if}
        {#if activeFile}
          <div class="editor-tabs">
            <span class="editor-tab active"><span class="tab-name">{activeFile.name}</span>{#if dirty}<span class="tab-dirty" title="Есть несохранённые изменения">•</span>{/if}</span>
            {#if !activeFile.task_id}<span class="tab-collab-hint" title="Совместное редактирование доступно только для файлов, привязанных к задаче">Привяжи задачу, чтобы включить совместный режим</span>{/if}
          </div>
        {/if}
        <div class="editor-stack">
          <div class="monaco-host" bind:this={editorHost} role="region" aria-label="Редактор кода"></div>
          {#if !activeFile}
            <div class="editor-empty">
              <p>Нет открытого файла.</p>
              <p class="hint">Создай файл слева или выгрузи стартовый код задачи из раздела «Задачи».</p>
            </div>
          {/if}
        </div>
      </section>

      <aside class="tests-panel" class:collapsed={!testsOpen}>
        <div class="tests-head">
          <h2>Тесты</h2>
          <button class="icon-btn" onclick={() => (testsOpen = !testsOpen)} aria-expanded={testsOpen} title={testsOpen ? 'Свернуть' : 'Развернуть'}>{testsOpen ? '▾' : '▸'}</button>
        </div>
        {#if testsOpen}
          <div class="tests-body">
            {#if collabStatus === 'error'}
              <div class="collab-error-banner" role="alert">
                <span>Совместное редактирование недоступно: {collabDetail || 'нет соединения'}</span>
                <button class="mini-btn" onclick={continueSolo}>Продолжить одному</button>
              </div>
            {/if}
            {#if sharedRoomId && activeFile?.task_id === sharedRoomTaskId}
              <div class="share-room-card">
                <div class="share-room-title" title={sharedRoomTitle}>Комната: {sharedRoomTitle}</div>
                <div class="share-room-link-row">
                  <input class="share-room-link" readonly value={shareRoomLink} onfocus={(e) => (e.target as HTMLInputElement).select()} aria-label="Ссылка на комнату" />
                  <button class="mini-btn" onclick={copyShareLink}>{shareCopied ? 'Скопировано' : 'Копировать'}</button>
                </div>
                <p class="share-room-hint">Студент попадёт в совместный режим только по этой ссылке.</p>
              </div>
            {:else if activeFile?.task_id}
              <div class="share-room-create">
                <button class="mini-btn" onclick={() => void createRoomForActiveTask()} disabled={shareBusy}>{shareBusy ? 'Создаю…' : 'Создать комнату со ссылкой'}</button>
                {#if shareError}<p class="side-error" role="alert">{shareError}</p>{/if}
              </div>
            {/if}
            {#if collabStatus === 'live'}
              <p class="collab-live-hint">Совместное редактирование: {collabParticipants} участник{collabParticipants === 1 ? '' : collabParticipants < 5 ? 'а' : 'ов'}</p>
            {/if}
            {#if !activeFile}
              <p class="side-empty">Открой файл, чтобы работать с тестами.</p>
            {:else if activeFile.task_id}
              <div class="test-run-row">
                <button class="run-btn" onclick={() => void runTests()} disabled={checkRunning}>{checkRunning ? 'Запускаю…' : 'Запустить тесты'}</button>
                <span class="task-ref" title={activeFile.task_id}>{activeFile.task_id}</span>
              </div>
              {#if checkError}<p class="side-error" role="alert">{checkError}</p>{/if}
              {#if checkResult}
                <div class="check-summary">
                  {#if statusTone}<span class="status-badge {statusTone}">{statusLabel}</span>{/if}
                  {#if typeof checkResult.passed_tests === 'number'}
                    <span class="check-score">{checkResult.passed_tests}/{checkResult.total_tests} тестов пройдено</span>
                  {/if}
                </div>
                {#if checkResult.error}<pre class="check-error">{checkResult.error}</pre>{/if}
                {#if Array.isArray(checkResult.results) && checkResult.results.length > 0}
                  <ul class="test-list">
                    {#each checkResult.results as test, index (index)}
                      <li class="test-item">
                        <div class="test-item-head">
                          <span class="test-dot" class:passed={test.passed !== false} class:failed={test.passed === false}></span>
                          <span class="test-desc">{test.description ?? `Тест ${index + 1}`}</span>
                        </div>
                        {#if test.expected_repr != null || test.actual_repr != null}
                          <div class="test-diff">
                            {#if test.expected_repr != null}<div><small>Ожидалось</small><pre>{test.expected_repr}</pre></div>{/if}
                            {#if test.actual_repr != null}<div><small>Получено</small><pre>{test.actual_repr}</pre></div>{/if}
                          </div>
                        {/if}
                        {#if test.error}<pre class="check-error">{test.error}</pre>{/if}
                      </li>
                    {/each}
                  </ul>
                {/if}
              {/if}
            {:else}
              <p class="bind-hint">Файл не привязан к задаче</p>
              <div class="bind-row">
                <select bind:value={bindTaskId} aria-label="Выбрать задачу">
                  <option value="">— выбери задачу —</option>
                  {#each filteredTasks as task (task.task_id)}
                    <option value={task.task_id}>{[task.block, task.title ?? task.task_id].filter(Boolean).join(' · ')}</option>
                  {/each}
                </select>
                <button class="mini-btn primary" onclick={() => void submitBind()} disabled={!bindTaskId}>Привязать</button>
              </div>
              {#if checkError}<p class="side-error" role="alert">{checkError}</p>{/if}
            {/if}
          </div>
        {/if}
      </aside>
    </div>

    <footer class="status-line">
      <span class:warn={dirty}>{autosaveLabel}</span>
      {#if storeNotice}<span class="side-error" role="alert">{storeNotice}</span>{/if}
    </footer>
  </main>
{/if}

<style>
  .ide-boot { min-height: 100dvh; display: grid; place-items: center; color: var(--muted-foreground); }

  /* ---------- Вход ---------- */
  .login-page { min-height: 100dvh; }
  .login-topbar { height: 72px; padding: 0 max(24px, calc((100vw - 1120px) / 2)); display: flex; align-items: center; border-bottom: 1px solid var(--border); background: var(--card); }
  .login-brand { display: flex; align-items: center; gap: 11px; color: var(--foreground); font-size: 17px; font-weight: 650; letter-spacing: -.03em; }
  .login-brand small { display: block; color: var(--muted-foreground); font-size: 11px; font-weight: 400; letter-spacing: 0; }
  .login-content { min-height: calc(100dvh - 72px); display: grid; place-items: center; padding: 40px 20px; }
  .login-card { width: min(440px, 100%); padding: 30px 28px; display: grid; gap: 18px; background: var(--card); border: 1px solid var(--border); border-radius: 14px; }
  .login-icon { display: grid; place-items: center; width: 46px; height: 46px; border: 1px solid var(--border); border-radius: 12px; background: var(--secondary); color: var(--muted-foreground); }
  .login-glyph { font-family: Consolas, 'Cascadia Code', 'Courier New', monospace; font-size: 15px; }
  .login-card h1 { margin: 0; font-size: 26px; line-height: 1.25; font-weight: 600; letter-spacing: -.04em; }
  .login-card .sub { margin: 0 0 6px; color: var(--muted-foreground); font-size: 14px; line-height: 1.65; }
  .admin-field { display: grid; gap: 7px; font-size: 12px; font-weight: 500; color: var(--muted-foreground); }
  .login-submit { padding: 11px 16px; border: 1px solid transparent; border-radius: 8px; background: var(--primary); color: var(--primary-foreground); font-size: 14px; font-weight: 600; cursor: pointer; }
  .login-submit:hover:not(:disabled) { filter: brightness(1.08); }
  .login-submit:disabled { opacity: .55; cursor: default; }
  .login-submit.ghost { background: transparent; border-color: var(--border); color: var(--foreground); font-weight: 500; }
  .login-divider { display: flex; align-items: center; gap: 14px; color: var(--muted-foreground); font-size: 11px; }
  .login-divider::before, .login-divider::after { content: ''; height: 1px; flex: 1; background: var(--border); }
  .login-error { padding: 10px 12px; border: 1px solid var(--destructive); border-radius: 8px; background: color-mix(in srgb, var(--destructive) 12%, transparent); color: var(--destructive); font-size: 13px; }
  @media (max-width: 600px) { .login-topbar { padding: 0 20px; } .login-content { padding: 28px 16px; } }

  /* ---------- Каркас IDE ---------- */
  .ide { height: 100dvh; display: grid; grid-template-rows: auto minmax(0, 1fr) auto; background: var(--background); overflow: hidden; }
  .ide-topbar { display: flex; align-items: center; justify-content: space-between; gap: 16px; padding: 10px 16px; background: var(--card); border-bottom: 1px solid var(--border); }
  .brand { display: flex; align-items: center; gap: 11px; }
  .brand strong { display: block; font-size: 15px; letter-spacing: -.03em; }
  .brand small { display: block; color: var(--muted-foreground); font-size: 11px; }
  .account { display: flex; align-items: center; gap: 12px; }
  .account-name { font-size: 13px; font-weight: 600; }
  .logout-btn { padding: 7px 14px; border: 1px solid var(--border); border-radius: 8px; background: transparent; color: var(--foreground); font-size: 12px; font-weight: 500; cursor: pointer; }
  .logout-btn:hover { background: var(--secondary); }

  .ide-body { display: grid; grid-template-columns: 300px minmax(0, 1fr) 340px; min-height: 0; min-width: 0; }
  .ide-body:has(> .tests-panel.collapsed) { grid-template-columns: 300px minmax(0, 1fr) auto; }

  /* ---------- Сайдбар ---------- */
  .sidebar { display: flex; flex-direction: column; min-height: 0; min-width: 0; overflow-y: auto; background: var(--card); border-right: 1px solid var(--border); }
  .side-section { display: flex; flex-direction: column; min-height: 0; padding: 14px 12px 16px; }
  .side-section.grow { flex: 1; }
  .side-head { display: flex; align-items: center; justify-content: space-between; gap: 8px; margin-bottom: 10px; }
  .side-head h2 { margin: 0; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: .06em; color: var(--muted-foreground); }
  .mini-btn { padding: 5px 10px; border: 1px solid var(--border); border-radius: 7px; background: transparent; color: var(--foreground); font-size: 11px; font-weight: 500; cursor: pointer; white-space: nowrap; }
  .mini-btn:hover:not(:disabled) { background: var(--secondary); }
  .mini-btn.primary { background: var(--primary); border-color: transparent; color: var(--primary-foreground); }
  .mini-btn.primary:hover:not(:disabled) { filter: brightness(1.08); background: var(--primary); }
  .mini-btn:disabled { opacity: .55; cursor: default; }
  .inline-row { display: flex; gap: 6px; margin-bottom: 8px; width: 100%; }
  .inline-row input { flex: 1; min-width: 0; padding: 6px 9px; font-size: 12px; }
  .side-error { margin: 6px 0 0; color: var(--destructive); font-size: 12px; overflow-wrap: anywhere; }
  .side-empty { margin: 4px 0 0; color: var(--muted-foreground); font-size: 12px; line-height: 1.6; }

  .file-list { list-style: none; margin: 0; padding: 0; display: grid; gap: 3px; }
  .file-list li { position: relative; display: flex; align-items: center; gap: 6px; border-radius: 8px; }
  .file-list li:hover { background: var(--secondary); }
  .file-list li.active { background: var(--secondary); box-shadow: inset 2px 0 var(--primary); }
  .file-open { flex: 1; min-width: 0; display: grid; gap: 2px; padding: 7px 9px; background: transparent; border: 0; text-align: left; cursor: pointer; color: var(--foreground); }
  .file-name { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-size: 13px; }
  .file-date { color: var(--muted-foreground); font-size: 10px; }
  .file-actions { display: none; align-items: center; gap: 2px; padding-right: 6px; }
  .file-list li:hover .file-actions, .file-list li.active .file-actions { display: flex; }
  .file-task { max-width: 90px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color: var(--muted-foreground); font-size: 10px; }
  .icon-btn { display: grid; place-items: center; width: 22px; height: 22px; padding: 0; border: 0; border-radius: 6px; background: transparent; color: var(--muted-foreground); font-size: 13px; line-height: 1; cursor: pointer; }
  .icon-btn:hover { background: var(--border); color: var(--foreground); }
  .icon-btn.danger:hover { color: var(--destructive); }

  .task-search { width: 100%; padding: 8px 11px; font-size: 12px; }
  .task-list { list-style: none; margin: 10px 0 0; padding: 0; display: grid; gap: 4px; }
  .task-item { display: flex; align-items: center; justify-content: space-between; gap: 8px; padding: 7px 8px; border-radius: 8px; }
  .task-item:hover { background: var(--secondary); }
  .task-info { min-width: 0; display: flex; align-items: center; gap: 7px; }
  .task-badge { flex-shrink: 0; padding: 2px 6px; border: 1px solid var(--border); border-radius: 5px; background: var(--secondary); color: var(--muted-foreground); font-size: 10px; font-weight: 600; text-transform: uppercase; }
  .task-title { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-size: 12px; }

  /* ---------- Редактор ---------- */
  .editor-pane { display: flex; flex-direction: column; min-width: 0; min-height: 0; }
  .editor-stack { position: relative; flex: 1 1 auto; min-height: 0; }
  .route-banner, .editor-tabs { flex-shrink: 0; }
  .route-banner { padding: 6px 14px; background: var(--card); border-bottom: 1px solid var(--border); color: var(--muted-foreground); font-size: 12px; overflow-wrap: anywhere; }
  .route-banner.error { color: var(--destructive); }
  .editor-tabs { display: flex; align-items: stretch; background: var(--card); border-bottom: 1px solid var(--border); }
  .editor-tab { display: flex; align-items: center; gap: 7px; padding: 8px 14px; font-size: 12px; color: var(--muted-foreground); border-right: 1px solid var(--border); background: var(--card); }
  .editor-tab.active { color: var(--foreground); box-shadow: inset 0 -2px var(--primary); }
  .tab-dirty { color: var(--warning); }
  .monaco-host { position: absolute; inset: 0; overflow: hidden; }
  .editor-empty { position: absolute; inset: 0; display: grid; place-content: center; justify-items: center; gap: 8px; padding: 40px; background: var(--background); color: var(--muted-foreground); text-align: center; }
  .editor-empty p { margin: 0; font-size: 15px; }
  .editor-empty .hint { font-size: 12px; }

  /* ---------- Тесты ---------- */
  .tests-panel { display: flex; flex-direction: column; min-height: 0; min-width: 0; overflow-y: auto; background: var(--card); border-left: 1px solid var(--border); }
  .tests-panel.collapsed { overflow: hidden; }
  .tests-head { display: flex; align-items: center; justify-content: space-between; gap: 8px; padding: 12px 14px; position: sticky; top: 0; background: var(--card); border-bottom: 1px solid var(--border); }
  .tests-head h2 { margin: 0; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: .06em; color: var(--muted-foreground); }
  .tests-body { display: flex; flex-direction: column; gap: 12px; padding: 12px 14px 16px; }
  .test-run-row { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
  .run-btn { padding: 9px 16px; border: 1px solid transparent; border-radius: 8px; background: var(--primary); color: var(--primary-foreground); font-size: 13px; font-weight: 600; cursor: pointer; }
  .run-btn:hover:not(:disabled) { filter: brightness(1.08); }
  .run-btn:disabled { opacity: .55; cursor: default; }
  .task-ref { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color: var(--muted-foreground); font-size: 11px; }
  .check-summary { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
  .status-badge { padding: 4px 10px; border-radius: 999px; font-size: 11px; font-weight: 600; border: 1px solid transparent; }
  .status-badge.success { color: var(--success); border-color: var(--success); background: color-mix(in srgb, var(--success) 12%, transparent); }
  .status-badge.warning { color: var(--warning); border-color: var(--warning); background: color-mix(in srgb, var(--warning) 12%, transparent); }
  .status-badge.destructive { color: var(--destructive); border-color: var(--destructive); background: color-mix(in srgb, var(--destructive) 12%, transparent); }
  .check-score { color: var(--muted-foreground); font-size: 12px; }
  .check-error, .test-diff pre { margin: 0; padding: 9px 11px; border: 1px solid var(--border); border-radius: 8px; background: var(--secondary); color: var(--foreground); font-family: Consolas, 'Cascadia Code', 'Courier New', monospace; font-size: 12px; white-space: pre-wrap; overflow-wrap: anywhere; }
  .check-error { border-color: color-mix(in srgb, var(--destructive) 45%, var(--border)); color: var(--destructive); }
  .test-list { list-style: none; margin: 0; padding: 0; display: grid; gap: 10px; }
  .test-item { display: grid; gap: 7px; padding: 10px 11px; border: 1px solid var(--border); border-radius: 10px; }
  .test-item-head { display: flex; align-items: center; gap: 8px; }
  .test-dot { width: 8px; height: 8px; border-radius: 999px; background: var(--muted-foreground); flex-shrink: 0; }
  .test-dot.passed { background: var(--success); }
  .test-dot.failed { background: var(--destructive); }
  .test-desc { font-size: 13px; font-weight: 500; overflow-wrap: anywhere; }
  .test-diff { display: grid; gap: 7px; }
  .test-diff small { display: block; margin-bottom: 3px; color: var(--muted-foreground); font-size: 10px; text-transform: uppercase; letter-spacing: .05em; }
  .bind-hint { margin: 0; color: var(--muted-foreground); font-size: 12px; }
  .bind-row { display: flex; gap: 8px; }
  .bind-row select { flex: 1; min-width: 0; padding: 8px 10px; font-size: 12px; }

  /* ---------- Совместное редактирование ---------- */
  .topbar-collab { position: relative; display: flex; align-items: center; }
  .collab-chip { display: inline-flex; align-items: center; gap: 8px; padding: 6px 12px; border: 1px solid var(--border); border-radius: 999px; background: var(--secondary); color: var(--foreground); font-size: 12px; font-weight: 500; cursor: pointer; }
  .collab-chip:hover { border-color: color-mix(in srgb, var(--primary) 45%, var(--border)); }
  .collab-dot { width: 8px; height: 8px; border-radius: 999px; background: var(--muted-foreground); flex-shrink: 0; }
  .collab-dot.connecting { background: var(--warning); animation: collab-pulse 1.2s ease-in-out infinite; }
  .collab-dot.syncing { background: var(--warning); }
  .collab-dot.live { background: var(--success); }
  .collab-dot.error { background: var(--destructive); }
  @keyframes collab-pulse { 0%, 100% { opacity: 1; } 50% { opacity: .35; } }
  .collab-label { white-space: nowrap; }
  .collab-avatars { display: inline-flex; margin-left: 2px; }
  .peer-avatar { display: inline-grid; place-items: center; width: 22px; height: 22px; border-radius: 999px; color: #0b0b0d; font-size: 10px; font-weight: 700; border: 2px solid var(--card); margin-left: -6px; }
  .peer-avatar.self { border-color: var(--border); }
  .collab-popover { position: absolute; top: calc(100% + 8px); left: 0; z-index: 40; min-width: 240px; padding: 12px; display: grid; gap: 10px; background: var(--card); border: 1px solid var(--border); border-radius: 10px; box-shadow: 0 10px 30px rgb(0 0 0 / .35); }
  .collab-room { color: var(--muted-foreground); font-size: 11px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .collab-peer-list { list-style: none; margin: 0; padding: 0; display: grid; gap: 6px; }
  .collab-peer-list li { display: flex; align-items: center; gap: 8px; }
  .collab-peer-list .peer-avatar { margin-left: 0; }
  .peer-name { font-size: 12px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .collab-error-banner { display: flex; align-items: center; justify-content: space-between; gap: 10px; flex-wrap: wrap; padding: 9px 11px; border: 1px solid color-mix(in srgb, var(--destructive) 45%, var(--border)); border-radius: 8px; background: color-mix(in srgb, var(--destructive) 10%, transparent); color: var(--destructive); font-size: 12px; }
  .collab-error-banner .mini-btn { flex-shrink: 0; }
  .collab-live-hint { margin: 0; color: var(--muted-foreground); font-size: 11px; }
  .share-room-card { display: grid; gap: 7px; padding: 10px; border: 1px solid var(--border); border-radius: 8px; background: var(--secondary); }
  .share-room-title { font-size: 12px; font-weight: 600; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .share-room-link-row { display: flex; gap: 6px; align-items: center; }
  .share-room-link { flex: 1; min-width: 0; padding: 6px 8px; border: 1px solid var(--border); border-radius: 6px; background: var(--background); color: var(--foreground); font-size: 11px; font-family: inherit; }
  .share-room-hint { margin: 0; color: var(--muted-foreground); font-size: 11px; }
  .share-room-create { padding: 2px 0 6px; }
  .tab-collab-hint { display: inline-flex; align-items: center; padding: 0 12px; color: var(--muted-foreground); font-size: 11px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

  /* ---------- Статусная строка ---------- */
  .status-line { display: flex; align-items: center; gap: 16px; padding: 6px 16px; background: var(--card); border-top: 1px solid var(--border); color: var(--muted-foreground); font-size: 11px; }
  .status-line .warn { color: var(--warning); }

  @media (max-width: 1100px) {
    .ide-body { grid-template-columns: 260px minmax(0, 1fr) 300px; }
  }
  /* Узкие экраны: один столбец, каждая панель ограничена и скроллит себя,
     страница целиком не скроллится (иначе сайдбар «вылезает» на всю высоту). */
  @media (max-width: 900px) {
    .ide { height: 100dvh; overflow: hidden; }
    .ide-topbar { flex-wrap: wrap; row-gap: 6px; padding: 8px 12px; min-width: 0; }
    .brand { min-width: 0; }
    .topbar-collab { min-width: 0; }
    .topbar-collab button { max-width: 100%; }
    .account { min-width: 0; }
    .account-name { max-width: 26vw; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .ide-body { grid-template-columns: minmax(0, 1fr); grid-template-rows: minmax(0, 1fr) auto auto; }
    .sidebar { grid-column: 1; grid-row: 2; max-height: 34dvh; min-height: 0; border-right: 0; border-top: 1px solid var(--border); overflow-y: auto; }
    .editor-pane { grid-column: 1; grid-row: 1; min-height: 0; }
    .tests-panel, .tests-panel.collapsed { grid-column: 1; grid-row: 3; border-left: 0; border-top: 1px solid var(--border); max-height: 26dvh; }
  }
</style>
