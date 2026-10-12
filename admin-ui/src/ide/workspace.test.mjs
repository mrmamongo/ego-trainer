import assert from 'node:assert/strict';
import test from 'node:test';

import {
  createWorkspaceStore,
  workspaceStore,
  DB_NAME,
  DB_VERSION,
  FILES_STORE,
  META_ID,
  DUPLICATE_NAME_MESSAGE,
  FILE_NAME_PATTERN
} from './workspace.js';

const UUID_PATTERN = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/;
const ISO_PATTERN = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$/;

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
const clone = (value) => (value === undefined ? undefined : structuredClone(value));

/** Minimal IDBRequest/IDBOpenRequest double: events fire via queueMicrotask. */
class FakeRequest {
  constructor() {
    this.result = undefined;
    this.error = null;
    this.onsuccess = null;
    this.onerror = null;
    this.onupgradeneeded = null;
    this.onblocked = null;
  }
}

/**
 * Minimal IDBObjectStore double. Counters live on the database-owned state,
 * so call counts accumulate across transactions.
 */
class FakeObjectStore {
  constructor(state, tx) {
    this.state = state;
    this.tx = tx;
    this.name = state.name;
  }

  /** @private schedule request success on the microtask queue */
  _request() {
    const request = new FakeRequest();
    this.tx.track(request);
    return request;
  }

  get(key) {
    this.state.calls.get += 1;
    const request = this._request();
    queueMicrotask(() => {
      const record = this.state.records.get(key);
      request.result = record === undefined ? undefined : clone(record);
      if (request.onsuccess) request.onsuccess({ type: 'success', target: request });
      this.tx.settled();
    });
    return request;
  }

  getAll() {
    this.state.calls.getAll += 1;
    const request = this._request();
    queueMicrotask(() => {
      request.result = Array.from(this.state.records.values(), clone);
      if (request.onsuccess) request.onsuccess({ type: 'success', target: request });
      this.tx.settled();
    });
    return request;
  }

  put(value) {
    this.state.calls.put += 1;
    const request = this._request();
    const failure = this.tx.db.consumeFailure('put');
    queueMicrotask(() => {
      if (failure) {
        request.error = new Error(failure);
        if (request.onerror) request.onerror({ type: 'error', target: request });
        this.tx.fireAbort(new Error(failure));
        return;
      }
      const key = value[this.state.keyPath];
      this.state.records.set(key, clone(value));
      request.result = key;
      if (request.onsuccess) request.onsuccess({ type: 'success', target: request });
      this.tx.settled();
    });
    return request;
  }

  add(value) {
    this.state.calls.add += 1;
    const request = this._request();
    queueMicrotask(() => {
      const key = value[this.state.keyPath];
      if (this.state.records.has(key)) {
        request.error = new Error('ConstraintError');
        if (request.onerror) request.onerror({ type: 'error', target: request });
        this.tx.fireAbort(new Error('ConstraintError'));
        return;
      }
      this.state.records.set(key, clone(value));
      request.result = key;
      if (request.onsuccess) request.onsuccess({ type: 'success', target: request });
      this.tx.settled();
    });
    return request;
  }

  delete(key) {
    this.state.calls.delete += 1;
    const request = this._request();
    const failure = this.tx.db.consumeFailure('delete');
    queueMicrotask(() => {
      if (failure) {
        request.error = new Error(failure);
        if (request.onerror) request.onerror({ type: 'error', target: request });
        this.tx.fireAbort(new Error(failure));
        return;
      }
      this.state.records.delete(key);
      request.result = undefined;
      if (request.onsuccess) request.onsuccess({ type: 'success', target: request });
      this.tx.settled();
    });
    return request;
  }

  createIndex(name, keyPath) {
    this.state.calls.createIndex += 1;
    this.state.indexes.push({ name, keyPath });
    return { name, keyPath };
  }
}

/** Minimal IDBTransaction double: completes after its requests settle. */
class FakeTransaction {
  constructor(db, names, mode) {
    this.db = db;
    this.mode = mode;
    this.oncomplete = null;
    this.onabort = null;
    this.onerror = null;
    this.aborted = false;
    this.pending = 0;
    this.completeQueued = false;
    this.stores = names.map((name) => {
      const state = db.storeStates.get(name);
      if (!state) throw new Error(`NotFoundError: no such store "${name}"`);
      return new FakeObjectStore(state, this);
    });
  }

  objectStore(name) {
    const store = this.stores.find((candidate) => candidate.name === name);
    if (!store) throw new Error(`NotFoundError: no such store "${name}"`);
    return store;
  }

  track() {
    this.pending += 1;
  }

  settled() {
    this.pending -= 1;
    if (this.pending === 0 && !this.aborted && !this.completeQueued) {
      this.completeQueued = true;
      queueMicrotask(() => {
        if (!this.aborted && this.oncomplete) this.oncomplete({ type: 'complete' });
      });
    }
  }

  fireAbort(error) {
    if (this.aborted) return;
    this.aborted = true;
    queueMicrotask(() => {
      if (this.onabort) this.onabort({ type: 'abort', target: this, error });
    });
  }
}

/** Minimal IDBDatabase double. */
class FakeDatabase {
  constructor(name, version) {
    this.name = name;
    this.version = version;
    this.storeStates = new Map();
    this.storeOptions = new Map();
    this.createObjectStoreCalls = [];
    this.inUpgrade = false;
    this.closeCount = 0;
    this.failures = [];
  }

  createObjectStore(name, options) {
    if (!this.inUpgrade) {
      throw new Error('InvalidStateError: createObjectStore outside upgradeneeded');
    }
    this.createObjectStoreCalls.push([name, options]);
    const state = {
      name,
      keyPath: options && options.keyPath ? options.keyPath : null,
      records: new Map(),
      calls: { get: 0, getAll: 0, put: 0, add: 0, delete: 0, createIndex: 0 },
      indexes: []
    };
    this.storeStates.set(name, state);
    this.storeOptions.set(name, options || {});
    return new FakeObjectStore(state, null);
  }

  transaction(names, mode = 'readonly') {
    const list = Array.isArray(names) ? names : [names];
    return new FakeTransaction(this, list, mode);
  }

  close() {
    this.closeCount += 1;
  }

  /** Queue a forced failure for the next `method` store call (aborts the tx). */
  failNext(method) {
    this.failures.push(method);
  }

  consumeFailure(method) {
    const index = this.failures.indexOf(method);
    if (index === -1) return null;
    this.failures.splice(index, 1);
    return `forced ${method} failure`;
  }
}

/** Minimal IDBFactory double preserving upgrade semantics across opens. */
class FakeFactory {
  constructor() {
    this.databases = new Map();
    this.openCalls = [];
    this.upgrades = [];
  }

  open(name, version) {
    this.openCalls.push({ name, version });
    const request = new FakeRequest();
    queueMicrotask(() => {
      let db = this.databases.get(name);
      if (!db) {
        db = new FakeDatabase(name, version);
        this.databases.set(name, db);
        this.runUpgrade(request, db, 0, version);
        return;
      }
      if (version > db.version) {
        const oldVersion = db.version;
        db.version = version;
        this.runUpgrade(request, db, oldVersion, version);
        return;
      }
      if (version === db.version) {
        request.result = db;
        if (request.onsuccess) request.onsuccess({ type: 'success', target: request });
        return;
      }
      request.error = new Error('VersionError');
      if (request.onerror) request.onerror({ type: 'error', target: request });
    });
    return request;
  }

  runUpgrade(request, db, oldVersion, newVersion) {
    this.upgrades.push({ name: db.name, oldVersion, newVersion });
    db.inUpgrade = true;
    request.result = db;
    try {
      if (request.onupgradeneeded) {
        request.onupgradeneeded({ type: 'upgradeneeded', oldVersion, newVersion, target: request });
      }
    } finally {
      db.inUpgrade = false;
    }
    if (request.onsuccess) request.onsuccess({ type: 'success', target: request });
  }
}

/** Fresh factory + workspace store under test. */
function makeStore() {
  const factory = new FakeFactory();
  const store = createWorkspaceStore(factory);
  return {
    factory,
    store,
    db: () => factory.databases.get(DB_NAME),
    filesState: () => factory.databases.get(DB_NAME).storeStates.get(FILES_STORE)
  };
}

test('first open creates the files schema via onupgradeneeded, later opens do not', async () => {
  const { store, factory, db, filesState } = makeStore();
  await store.readMeta();
  assert.ok(factory.openCalls.length >= 1);
  assert.deepEqual(factory.openCalls[0], { name: DB_NAME, version: DB_VERSION });
  assert.equal(factory.upgrades.length, 1);
  assert.deepEqual(factory.upgrades[0], { name: DB_NAME, oldVersion: 0, newVersion: DB_VERSION });
  assert.deepEqual(db().createObjectStoreCalls, [[FILES_STORE, { keyPath: 'id' }]]);
  assert.equal(filesState().keyPath, 'id');

  await store.listFiles();
  await store.createFile({ name: 'A.py' });
  assert.equal(factory.upgrades.length, 1, 'schema must be created exactly once');
});

test('createFile happy path persists a record with uuid id and ISO timestamps', async () => {
  const { store, filesState } = makeStore();
  const file = await store.createFile({ name: 'F2.py', language: 'python', content: 'print(1)' });

  assert.match(file.id, UUID_PATTERN);
  assert.equal(file.name, 'F2.py');
  assert.equal(file.language, 'python');
  assert.equal(file.content, 'print(1)');
  assert.equal(file.task_id, null);
  assert.match(file.created_at, ISO_PATTERN);
  assert.equal(file.updated_at, file.created_at);

  const persisted = await store.getFile(file.id);
  assert.deepEqual(persisted, file);

  const plain = await store.createFile({ name: 'Заметка 1.md' });
  assert.equal(plain.language, 'plaintext');
  assert.equal(plain.content, '');
  assert.equal(plain.task_id, null);

  const state = filesState();
  assert.equal(state.calls.put, 2);
  assert.ok(state.calls.getAll >= 1);
  assert.equal(state.calls.createIndex, 0);
  assert.ok(state.records.has(file.id));
  assert.ok(state.records.has(plain.id));
});

test('listFiles sorts by name and never leaks the ::meta singleton', async () => {
  const { store } = makeStore();
  await store.createFile({ name: 'B.py' });
  await store.createFile({ name: 'A.py' });
  await store.writeMeta({ lastOpenedFileId: 'nowhere' });
  const listed = await store.listFiles();
  assert.deepEqual(listed.map((file) => file.name), ['A.py', 'B.py']);
  assert.ok(listed.every((file) => file.id !== META_ID));
});

test('duplicate names are rejected with the Russian message', async () => {
  const { store } = makeStore();
  await store.createFile({ name: 'F2.py' });
  await assert.rejects(() => store.createFile({ name: 'F2.py' }), {
    message: DUPLICATE_NAME_MESSAGE
  });
  await assert.rejects(() => store.importTaskFile({ task_id: 'F2', name: 'F2.py' }), {
    message: DUPLICATE_NAME_MESSAGE
  });
  // exact match only — a different name still works after the rejections
  const other = await store.createFile({ name: 'F2 копия.py' });
  assert.equal(other.name, 'F2 копия.py');
});

test('file name validation rejects bad names and accepts the documented charset', async () => {
  const { store } = makeStore();
  for (const bad of ['bad/name', '', 'a\\b', 'x'.repeat(65), 'drop*all', null, 42]) {
    await assert.rejects(
      () => store.createFile({ name: bad }),
      { message: 'Недопустимое имя файла' },
      `expected rejection for ${JSON.stringify(bad)}`
    );
  }
  assert.equal(FILE_NAME_PATTERN.test('F2.py'), true);
  assert.equal(FILE_NAME_PATTERN.test('Заметка №1.md'), false);
  const good = await store.createFile({ name: 'Заметка - блок 1.md' });
  assert.equal(good.name, 'Заметка - блок 1.md');
});

test('getFileByName and getFile resolve records or undefined', async () => {
  const { store } = makeStore();
  const file = await store.createFile({ name: 'F2.py' });
  assert.deepEqual(await store.getFileByName('F2.py'), file);
  assert.equal(await store.getFileByName('missing.py'), undefined);
  assert.equal(await store.getFile('00000000-0000-4000-8000-000000000000'), undefined);
});

test('updateFile bumps updated_at, enforces uniqueness against other files', async () => {
  const { store } = makeStore();
  const a = await store.createFile({ name: 'A.py', content: 'x' });
  const b = await store.createFile({ name: 'B.py' });
  await sleep(5);

  const updated = await store.updateFile(a.id, { content: 'y', task_id: 'F2' });
  assert.equal(updated.content, 'y');
  assert.equal(updated.task_id, 'F2');
  assert.equal(updated.name, 'A.py');
  assert.equal(updated.created_at, a.created_at);
  assert.ok(updated.updated_at > a.updated_at, 'updated_at must advance');
  assert.deepEqual(await store.getFile(a.id), updated);

  await assert.rejects(() => store.updateFile(a.id, { name: 'B.py' }), {
    message: DUPLICATE_NAME_MESSAGE
  });
  await assert.rejects(() => store.updateFile(a.id, { name: 'bad/name' }), {
    message: 'Недопустимое имя файла'
  });

  // renaming to the file's own name is not a collision
  const renamed = await store.updateFile(b.id, { name: 'B.py', language: 'markdown' });
  assert.equal(renamed.name, 'B.py');
  assert.equal(renamed.language, 'markdown');

  const fresh = await store.updateFile(a.id, { name: 'A2.py' });
  assert.equal(fresh.name, 'A2.py');

  await assert.rejects(() => store.updateFile('missing-id', { content: 'z' }), {
    message: 'Файл не найден'
  });
});

test('deleteFile removes the record and clears a dangling meta pointer', async () => {
  const { store } = makeStore();
  const x = await store.createFile({ name: 'X.py' });
  const y = await store.createFile({ name: 'Y.py' });
  await store.writeMeta({ lastOpenedFileId: x.id });

  await store.deleteFile(y.id);
  let meta = await store.readMeta();
  assert.equal(meta.lastOpenedFileId, x.id, 'pointer to another file must survive');

  await store.deleteFile(x.id);
  assert.equal(await store.getFile(x.id), undefined);
  meta = await store.readMeta();
  assert.equal(meta.lastOpenedFileId, null);
  assert.deepEqual((await store.listFiles()).map((file) => file.name), []);
});

test('readMeta returns defaults when the store has no meta record', async () => {
  const { store } = makeStore();
  await store.createFile({ name: 'A.py' });
  assert.deepEqual(await store.readMeta(), { lastOpenedFileId: null, updatedAt: null });
});

test('writeMeta merges over the existing singleton record and persists', async () => {
  const { store, filesState } = makeStore();
  await store.writeMeta({ lastOpenedFileId: 'abc' });
  let meta = await store.readMeta();
  assert.equal(meta.lastOpenedFileId, 'abc');
  assert.match(meta.updatedAt, ISO_PATTERN);
  const firstUpdatedAt = meta.updatedAt;

  await sleep(5);
  await store.writeMeta({});
  meta = await store.readMeta();
  assert.equal(meta.lastOpenedFileId, 'abc', 'empty patch must keep existing value');
  assert.ok(meta.updatedAt > firstUpdatedAt);

  const raw = filesState().records.get(META_ID);
  assert.equal(raw.id, META_ID);
  assert.equal(raw.lastOpenedFileId, 'abc');

  await store.writeMeta({ lastOpenedFileId: null });
  meta = await store.readMeta();
  assert.equal(meta.lastOpenedFileId, null);
});

test('importTaskFile creates a python file bound to the task', async () => {
  const { store } = makeStore();
  const file = await store.importTaskFile({
    task_id: 'block_f/F2',
    name: 'F2.py',
    content: 'def solve():\n    pass\n'
  });
  assert.equal(file.language, 'python');
  assert.equal(file.task_id, 'block_f/F2');
  assert.equal(file.content, 'def solve():\n    pass\n');
  assert.deepEqual(await store.getFileByName('F2.py'), file);
});

test('aborted transactions reject with Russian storage errors', async () => {
  const { store, db, filesState } = makeStore();
  await store.readMeta(); // ensure the database exists before forcing a failure
  db().failNext('put');
  await assert.rejects(() => store.createFile({ name: 'A.py' }), {
    message: 'Не удалось сохранить файл'
  });
  assert.equal(filesState().records.size, 0, 'nothing may persist after an abort');

  const saved = await store.createFile({ name: 'B.py' });
  db().failNext('delete');
  await assert.rejects(() => store.deleteFile(saved.id), { message: 'Не удалось удалить файл' });
  assert.ok(await store.getFile(saved.id), 'record must survive a failed delete');
});

test('workspace store degrades gracefully without indexedDB', async () => {
  const offline = createWorkspaceStore(null);
  const expected = { message: 'IndexedDB недоступен в этом окружении' };
  await assert.rejects(() => offline.listFiles(), expected);
  await assert.rejects(() => offline.createFile({ name: 'A.py' }), expected);
  await assert.rejects(() => offline.getFile('x'), expected);
  await assert.rejects(() => offline.updateFile('x', {}), expected);
  await assert.rejects(() => offline.deleteFile('x'), expected);
  await assert.rejects(() => offline.readMeta(), expected);
  await assert.rejects(() => offline.writeMeta({}), expected);

  // the singleton is built with null in Node and must not throw on import/use
  await assert.rejects(() => workspaceStore.listFiles(), expected);
});
