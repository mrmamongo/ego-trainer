/**
 * Per-user IDE workspace persisted entirely in the browser via IndexedDB.
 *
 * The server is a stateless event/data provider, so all workspace documents
 * live client-side. This module is a hand-rolled promise wrapper over
 * IndexedDB with an injected factory (`createWorkspaceStore`) so it can be
 * unit-tested in Node against a fake in-memory IDB implementation.
 *
 * @module ide/workspace
 */

/** @typedef {'python' | 'markdown' | 'plaintext'} FileLanguage */

/**
 * A workspace file document stored in the `files` object store.
 * @typedef {object} FileRecord
 * @property {string} id uuid (crypto.randomUUID with fallback)
 * @property {string} name unique human-readable name, e.g. 'F2.py'
 * @property {FileLanguage} language
 * @property {string} content editor text
 * @property {string|null} task_id catalog task this file was created from
 * @property {string} created_at ISO timestamp
 * @property {string} updated_at ISO timestamp
 */

/**
 * Singleton meta record (same store, id === '::meta').
 * @typedef {object} WorkspaceMeta
 * @property {string|null} lastOpenedFileId
 * @property {string|null} updatedAt ISO timestamp of the last meta write
 */

/** @typedef {'readonly' | 'readwrite'} IDBModeLike */

/**
 * Minimal indexedDB-compatible factory required by this module.
 * @typedef {object} IDBFactoryLike
 * @property {(name: string, version: number) => IDBOpenRequestLike} open
 */

/**
 * Minimal IDBRequest/IDBOpenRequest shape consumed here.
 * @typedef {object} IDBRequestLike
 * @property {unknown} result
 * @property {((event: unknown) => void) | null} [onsuccess]
 * @property {((event: unknown) => void) | null} [onerror]
 * @property {((event: unknown) => void) | null} [onupgradeneeded]
 * @property {((event: unknown) => void) | null} [onblocked]
 */

/**
 * Minimal IDBTransaction shape consumed here.
 * @typedef {object} IDBTransactionLike
 * @property {IDBModeLike} mode
 * @property {((event: unknown) => void) | null} [oncomplete]
 * @property {((event: unknown) => void) | null} [onabort]
 * @property {((event: unknown) => void) | null} [onerror]
 * @property {(name: string) => IDBObjectStoreLike} objectStore
 */

/**
 * Minimal IDBObjectStore shape consumed here.
 * @typedef {object} IDBObjectStoreLike
 * @property {(key: unknown) => IDBRequestLike} get
 * @property {() => IDBRequestLike} getAll
 * @property {(value: FileRecord | WorkspaceMetaRecord) => IDBRequestLike} put
 * @property {(key: unknown) => IDBRequestLike} delete
 */

/**
 * Minimal IDBDatabase shape consumed here.
 * @typedef {object} IDBDatabaseLike
 * @property {(names: string | string[], mode?: IDBModeLike) => IDBTransactionLike} transaction
 * @property {(name: string, options?: { keyPath?: string }) => unknown} createObjectStore
 * @property {() => void} close
 */

/** Database name. */
export const DB_NAME = 'ego-ide';
/** Database schema version. */
export const DB_VERSION = 1;
/** The single object store holding file records plus the meta singleton. */
export const FILES_STORE = 'files';
/** key of the singleton meta record inside {@link FILES_STORE}. */
export const META_ID = '::meta';
/** Allowed file names: letters (latin/cyrillic), digits, `._ -`, 1..64 chars. */
export const FILE_NAME_PATTERN = /^[A-Za-z0-9А-Яа-яёЁ._ -]{1,64}$/;
/** Error message used when a file name is already taken. */
export const DUPLICATE_NAME_MESSAGE = 'Файл с таким именем уже существует';
/** Supported editor languages. */
export const FILE_LANGUAGES = ['python', 'markdown', 'plaintext'];

const KNOWN_ERROR = Symbol('ego-ide-known-error');

/**
 * @typedef {object} WorkspaceMetaRecord
 * @property {typeof META_ID} id
 * @property {string|null} lastOpenedFileId
 * @property {string|null} updatedAt
 */

/**
 * Create an error that is rethrown verbatim instead of being wrapped into a
 * generic storage failure (validation errors, "not found", missing IDB).
 * @param {string} message
 * @returns {Error}
 */
function knownError(message) {
  const error = new Error(message);
  error[KNOWN_ERROR] = true;
  return error;
}

/**
 * @param {unknown} error
 * @returns {boolean}
 */
function isKnownError(error) {
  return error instanceof Error && Boolean(error[KNOWN_ERROR]);
}

/**
 * Generate a record id: crypto.randomUUID when available, fallback otherwise.
 * @returns {string}
 */
export function generateFileId() {
  const globalCrypto = typeof crypto !== 'undefined' ? crypto : null;
  if (globalCrypto && typeof globalCrypto.randomUUID === 'function') {
    return globalCrypto.randomUUID();
  }
  return 'file-' + Date.now().toString(36) + '-' + Math.random().toString(36).slice(2, 10);
}

/**
 * Current timestamp as an ISO string.
 * @returns {string}
 */
function nowIso() {
  return new Date().toISOString();
}

/**
 * Validate a file name against {@link FILE_NAME_PATTERN}.
 * @param {unknown} name
 * @returns {string} the validated name
 * @throws {Error} 'Недопустимое имя файла' when empty or malformed
 */
export function validateFileName(name) {
  if (typeof name !== 'string' || !FILE_NAME_PATTERN.test(name)) {
    throw knownError('Недопустимое имя файла');
  }
  return name;
}

/**
 * @param {unknown} language
 * @returns {FileLanguage}
 * @throws {Error} 'Недопустимый язык файла' when not in {@link FILE_LANGUAGES}
 */
function normalizeLanguage(language) {
  if (!FILE_LANGUAGES.includes(language)) {
    throw knownError('Недопустимый язык файла');
  }
  return language;
}

/**
 * @param {object} object
 * @param {string} key
 * @returns {boolean}
 */
function has(object, key) {
  return Object.prototype.hasOwnProperty.call(object, key);
}

/**
 * True file records only — the '::meta' singleton must never leak into
 * listings or uniqueness checks.
 * @param {unknown} record
 * @returns {boolean}
 */
function isFileRecord(record) {
  return Boolean(record) && typeof record === 'object' && has(record, 'name') && record.id !== META_ID;
}

/**
 * Wrap an IDB request into a promise.
 * @param {IDBRequestLike} request
 * @param {string} failureMessage message used when the request errors out
 * @returns {Promise<unknown>}
 */
function promisifyRequest(request, failureMessage) {
  return new Promise((resolve, reject) => {
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(knownError(failureMessage));
  });
}

/**
 * Resolve when the transaction completes; reject on abort/error so that
 * aborted writes surface as Russian storage failures.
 * @param {IDBTransactionLike} tx
 * @param {string} failureMessage
 * @returns {Promise<void>}
 */
function transactionDone(tx, failureMessage) {
  return new Promise((resolve, reject) => {
    tx.oncomplete = () => resolve();
    tx.onabort = () => reject(knownError(failureMessage));
    tx.onerror = () => reject(knownError(failureMessage));
  });
}

/**
 * Open (or upgrade) the `ego-ide` database. The `files` store is created in
 * onupgradeneeded when the version goes 0 -> 1.
 * @param {IDBFactoryLike} idbFactory
 * @returns {Promise<IDBDatabaseLike>}
 */
function openDatabase(idbFactory) {
  return new Promise((resolve, reject) => {
    /** @type {IDBRequestLike} */
    let request;
    try {
      request = idbFactory.open(DB_NAME, DB_VERSION);
    } catch {
      reject(knownError('Не удалось открыть базу данных'));
      return;
    }
    request.onupgradeneeded = (event) => {
      const oldVersion = Number(event && event.oldVersion) || 0;
      if (oldVersion < DB_VERSION) {
        /** @type {IDBDatabaseLike} */ (request.result)
          .createObjectStore(FILES_STORE, { keyPath: 'id' });
      }
    };
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(knownError('Не удалось открыть базу данных'));
    request.onblocked = () => reject(knownError('База данных заблокирована другим подключением'));
  });
}

/**
 * Run `executor` inside a transaction scoped to the `files` store and wait
 * for both the request result and transaction completion.
 *
 * @param {IDBFactoryLike} idbFactory
 * @param {IDBModeLike} mode
 * @param {(store: IDBObjectStoreLike) => IDBRequestLike} executor
 * @param {string} failureMessage message used when anything below rejects
 * @returns {Promise<unknown>} request result
 */
async function withStore(idbFactory, mode, executor, failureMessage) {
  const db = await openDatabase(idbFactory);
  try {
    const tx = db.transaction(FILES_STORE, mode);
    const store = tx.objectStore(FILES_STORE);
    const request = executor(store);
    const done = transactionDone(tx, failureMessage);
    // The transaction also reports request failures (they bubble); when the
    // request promise already rejected, keep this one from becoming an
    // unhandled rejection.
    done.catch(() => {});
    const result = await promisifyRequest(request, failureMessage);
    await done;
    return result;
  } finally {
    try {
      db.close();
    } catch {
      /* closing is best-effort */
    }
  }
}

/**
 * Build a workspace store bound to an injected indexedDB-compatible factory.
 * Every method is async; all timestamps are ISO strings.
 *
 * @param {IDBFactoryLike | null} idbFactory
 * @returns {{
 *   listFiles: () => Promise<FileRecord[]>,
 *   createFile: (input: {name?: string, language?: FileLanguage, content?: string, task_id?: string | null}) => Promise<FileRecord>,
 *   getFile: (id: string) => Promise<FileRecord | undefined>,
 *   getFileByName: (name: string) => Promise<FileRecord | undefined>,
 *   updateFile: (id: string, patch: {name?: string, language?: FileLanguage, content?: string, task_id?: string | null}) => Promise<FileRecord>,
 *   deleteFile: (id: string) => Promise<void>,
 *   importTaskFile: (input: {task_id?: string, name?: string, language?: FileLanguage, content?: string}) => Promise<FileRecord>,
 *   readMeta: () => Promise<WorkspaceMeta>,
 *   writeMeta: (patch: {lastOpenedFileId?: string | null}) => Promise<void>
 * }}
 */
export function createWorkspaceStore(idbFactory) {
  const available = Boolean(idbFactory) && typeof idbFactory.open === 'function';

  function assertAvailable() {
    if (!available) {
      throw knownError('IndexedDB недоступен в этом окружении');
    }
  }

  /**
   * @template T
   * @param {IDBModeLike} mode
   * @param {(store: IDBObjectStoreLike) => IDBRequestLike} executor
   * @param {string} failureMessage
   * @returns {Promise<T>}
   */
  async function run(mode, executor, failureMessage) {
    assertAvailable();
    try {
      return /** @type {T} */ (await withStore(idbFactory, mode, executor, failureMessage));
    } catch (error) {
      if (isKnownError(error)) {
        throw error;
      }
      throw knownError(failureMessage);
    }
  }

  /**
   * @returns {Promise<FileRecord[]>}
   */
  function loadFiles() {
    return /** @type {Promise<FileRecord[]>} */ (run(
      'readonly',
      (s) => s.getAll(),
      'Не удалось прочитать файлы'
    ).then((records) => (Array.isArray(records) ? records : []).filter(isFileRecord)));
  }

  /**
   * All files sorted by name.
   * @returns {Promise<FileRecord[]>}
   */
  async function listFiles() {
    assertAvailable();
    const files = await loadFiles();
    return files.slice().sort((a, b) => a.name.localeCompare(b.name));
  }

  /**
   * Create a file. Names must be unique.
   *
   * @param {{name?: string, language?: FileLanguage, content?: string, task_id?: string | null}} [input]
   * @returns {Promise<FileRecord>}
   * @throws {Error} 'Недопустимое имя файла', 'Файл с таким именем уже существует',
   *   'Не удалось сохранить файл'
   */
  async function createFile(input = {}) {
    assertAvailable();
    const name = validateFileName(input.name);
    const language = normalizeLanguage(has(input, 'language') ? input.language : 'plaintext');
    const content = typeof input.content === 'string' ? input.content : '';
    const taskId = input.task_id ?? null;
    const existing = await loadFiles();
    if (existing.some((file) => file.name === name)) {
      throw knownError(DUPLICATE_NAME_MESSAGE);
    }
    const timestamp = nowIso();
    /** @type {FileRecord} */
    const record = {
      id: generateFileId(),
      name,
      language,
      content,
      task_id: taskId,
      created_at: timestamp,
      updated_at: timestamp
    };
    await run('readwrite', (store) => store.put(record), 'Не удалось сохранить файл');
    return record;
  }

  /**
   * @param {string} id
   * @returns {Promise<FileRecord | undefined>}
   */
  async function getFile(id) {
    assertAvailable();
    const record = await run('readonly', (store) => store.get(id), 'Не удалось прочитать файл');
    return isFileRecord(record) ? /** @type {FileRecord} */ (record) : undefined;
  }

  /**
   * @param {string} name
   * @returns {Promise<FileRecord | undefined>}
   */
  async function getFileByName(name) {
    assertAvailable();
    const files = await loadFiles();
    return files.find((file) => file.name === name);
  }

  /**
   * Patch a file (name/language/content/task_id) and bump updated_at.
   *
   * @param {string} id
   * @param {{name?: string, language?: FileLanguage, content?: string, task_id?: string | null}} patch
   * @returns {Promise<FileRecord>}
   * @throws {Error} 'Файл не найден', name validation / uniqueness errors,
   *   'Не удалось сохранить файл'
   */
  async function updateFile(id, patch = {}) {
    assertAvailable();
    const current = await getFile(id);
    if (!current) {
      throw knownError('Файл не найден');
    }
    /** @type {FileRecord} */
    const next = { ...current };
    if (has(patch, 'name')) {
      next.name = validateFileName(patch.name);
    }
    if (has(patch, 'language')) {
      next.language = normalizeLanguage(patch.language);
    }
    if (has(patch, 'content')) {
      if (typeof patch.content !== 'string') {
        throw knownError('Содержимое файла должно быть строкой');
      }
      next.content = patch.content;
    }
    if (has(patch, 'task_id')) {
      next.task_id = patch.task_id ?? null;
    }
    if (next.name !== current.name) {
      const others = await loadFiles();
      if (others.some((file) => file.id !== id && file.name === next.name)) {
        throw knownError(DUPLICATE_NAME_MESSAGE);
      }
    }
    next.updated_at = nowIso();
    await run('readwrite', (store) => store.put(next), 'Не удалось сохранить файл');
    return next;
  }

  /**
   * Delete a file; clears meta.lastOpenedFileId when it pointed at it.
   * @param {string} id
   * @returns {Promise<void>}
   * @throws {Error} 'Не удалось удалить файл'
   */
  async function deleteFile(id) {
    assertAvailable();
    await run('readwrite', (store) => store.delete(id), 'Не удалось удалить файл');
    const meta = await readMeta();
    if (meta.lastOpenedFileId === id) {
      await writeMeta({ lastOpenedFileId: null });
    }
  }

  /**
   * Pull a task stub into the workspace: createFile with task_id and
   * language defaulting to 'python'.
   *
   * @param {{task_id?: string, name?: string, language?: FileLanguage, content?: string}} input
   * @returns {Promise<FileRecord>}
   */
  async function importTaskFile(input = {}) {
    return createFile({
      name: input.name,
      language: has(input, 'language') ? input.language : 'python',
      content: input.content,
      task_id: input.task_id ?? null
    });
  }

  /**
   * Read the meta singleton; defaults when the store has no meta record.
   * @returns {Promise<WorkspaceMeta>}
   */
  async function readMeta() {
    assertAvailable();
    const record = await run(
      'readonly',
      (store) => store.get(META_ID),
      'Не удалось прочитать настройки'
    );
    if (!record || typeof record !== 'object') {
      return { lastOpenedFileId: null, updatedAt: null };
    }
    const meta = /** @type {WorkspaceMetaRecord} */ (record);
    return {
      lastOpenedFileId: meta.lastOpenedFileId ?? null,
      updatedAt: meta.updatedAt ?? null
    };
  }

  /**
   * Merge `patch` over the existing meta singleton and persist it.
   * @param {{lastOpenedFileId?: string | null}} patch
   * @returns {Promise<void>}
   * @throws {Error} 'Не удалось сохранить настройки'
   */
  async function writeMeta(patch = {}) {
    assertAvailable();
    const existing = await run(
      'readonly',
      (store) => store.get(META_ID),
      'Не удалось прочитать настройки'
    );
    const base = existing && typeof existing === 'object'
      ? /** @type {WorkspaceMetaRecord} */ (existing)
      : { lastOpenedFileId: null, updatedAt: null };
    /** @type {WorkspaceMetaRecord} */
    const record = {
      ...base,
      ...patch,
      id: META_ID,
      updatedAt: nowIso()
    };
    await run('readwrite', (store) => store.put(record), 'Не удалось сохранить настройки');
  }

  return {
    listFiles,
    createFile,
    getFile,
    getFileByName,
    updateFile,
    deleteFile,
    importTaskFile,
    readMeta,
    writeMeta
  };
}

/**
 * Browser singleton. Created with `null` outside browsers; every method then
 * rejects with a Russian 'IndexedDB недоступен' error instead of crashing.
 */
export const workspaceStore = createWorkspaceStore(
  typeof indexedDB !== 'undefined' ? indexedDB : null
);
