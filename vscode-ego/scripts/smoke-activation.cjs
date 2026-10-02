const Module = require('module');
const path = require('path');
const { pathToFileURL } = require('url');

const extensionPath = path.join(__dirname, '..', 'out', 'extension.cjs');
const originalLoad = Module._load;

function createUri(filePath) {
  return {
    fsPath: filePath,
    path: filePath,
    toString: () => pathToFileURL(filePath).toString(),
  };
}

function createDisposable() {
  return { dispose() {} };
}

// --- Minimal VSCode mock for extension smoke test ---

// Utility: explicit error for unknown APIs
function throwUnknown(name) {
  return new Proxy(() => {}, {
    get: (_, k) => throwUnknown(name + '.' + k),
    apply: () => { throw new Error(`vscode mock: attempted to call unknown API '${name}'`); },
  });
}

// TreeItem class (mimics vscode.TreeItem)
class TreeItem {
  constructor(label, collapsibleState) {
    this.label = label;
    this.collapsibleState = collapsibleState;
  }
}

// EventEmitter class
class EventEmitter {
  constructor() {
    this._listeners = [];
    this.event = (listener) => {
      this._listeners.push(listener);
      return { dispose: () => {
        const idx = this._listeners.indexOf(listener);
        if (idx !== -1) this._listeners.splice(idx, 1);
      }};
    };
  }
  fire(val) { for (const l of this._listeners) l(val); }
  dispose() { this._listeners = []; }
}

// ThemeIcon class
class ThemeIcon {
  constructor(id) { this.id = id; }
}

// Uri mock
const Uri = {
  file: (filePath) => createUri(filePath),
  joinPath: (...args) => createUri(path.join(...args.map(u => (typeof u === 'string' ? u : u.fsPath))))
};

// Enums/constants
const FileType = { File: 1, Directory: 2, SymbolicLink: 64, Unknown: 0 };
const TreeItemCollapsibleState = { None: 0, Collapsed: 1, Expanded: 2 };
const StatusBarAlignment = { Left: 1, Right: 2 };
const ProgressLocation = { SourceControl: 1, Window: 10, Notification: 15 };

const vscode = {
  TreeItem,
  EventEmitter,
  ThemeIcon,
  Uri,
  FileType,
  TreeItemCollapsibleState,
  StatusBarAlignment,
  ProgressLocation,

  workspace: {
    getConfiguration() {
      return { get: (_key, fallback) => fallback };
    },
    asRelativePath(filePath) {
      return filePath;
    },
    onWillSaveTextDocument() {
      return createDisposable();
    },
    get workspaceFolders() { return undefined; },
    fs: {
      stat: async () => { return Promise.reject(new Error('No workspace')); },
    },
    findFiles: async () => [],
    onDidChangeConfiguration: () => createDisposable(),
    onDidChangeWorkspaceFolders: () => createDisposable(),
  },
  window: {
    createTreeView() {
      return { dispose() {} };
    },
    createStatusBarItem() {
      return {
        show() {}, hide() {}, dispose() {}, text: '', alignment: StatusBarAlignment.Left, command: undefined,
      };
    },
    createOutputChannel() {
      return { appendLine() {}, show() {}, dispose() {} };
    },
    registerWebviewViewProvider() { return createDisposable(); },
    registerUriHandler() { return createDisposable(); },
    onDidChangeActiveTextEditor() { return createDisposable(); },
    showErrorMessage() {},
    showWarningMessage() {},
    showInformationMessage() {},
    showQuickPick: async () => undefined,
    showOpenDialog: async () => [],
    showSaveDialog: async () => undefined,
    showInputBox: async () => undefined,
    activeTextEditor: undefined,
  },
  commands: {
    registerCommand() { return createDisposable(); },
    executeCommand: async () => undefined,
  },
  env: {
    openExternal: async () => undefined,
  },
  secrets: {
    get: async () => undefined,
    store: async () => undefined,
    delete: async () => undefined,
  },
};

// Defensive: unknown APIs throw
for (const ns of ['languages','tasks','notebook','comments','debug','extensions','scm','tests','authentication']) {
  vscode[ns] = throwUnknown('vscode.' + ns);
}

vscode.ExtensionContext = function ExtensionContext() {};

Module._load = function patchedLoad(request, parent, isMain) {
  if (request === 'vscode') return vscode;
  return originalLoad.call(this, request, parent, isMain);
};

async function main() {
  try {
    const mod = require(extensionPath);
    if (!mod || typeof mod.activate !== 'function') {
      throw new Error('out/extension.cjs does not export activate()');
    }

    const context = {
      extensionPath: path.dirname(extensionPath),
      extensionUri: createUri(path.dirname(extensionPath)),
      subscriptions: [],
      globalState: { get: () => undefined, update: async () => undefined },
      workspaceState: { get: () => undefined, update: async () => undefined },
      secrets: vscode.secrets,
      asAbsolutePath: (relPath) => path.join(path.dirname(extensionPath), relPath),
    };

    await mod.activate(context);
    for (const disposable of context.subscriptions) {
      if (disposable && typeof disposable.dispose === 'function') disposable.dispose();
    }
    console.log('smoke: activate() succeeded');
  } finally {
    Module._load = originalLoad;
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
