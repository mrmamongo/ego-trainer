<script lang="ts">
  import { onMount } from 'svelte';
  import * as monaco from 'monaco-editor/esm/vs/editor/editor.api';
  import 'monaco-editor/esm/vs/basic-languages/markdown/markdown.contribution';
  import 'monaco-editor/esm/vs/basic-languages/python/python.contribution';
  import 'monaco-editor/esm/vs/editor/contrib/find/browser/findController';
  import 'monaco-editor/esm/vs/editor/contrib/folding/browser/folding';
  import 'monaco-editor/min/vs/editor/editor.main.css';

  type EditorLanguage = 'markdown' | 'python';
  type Props = {
    documentId: string;
    value: string;
    language: EditorLanguage;
    readOnly: boolean;
    onChange: (value: string) => void;
    onSave: () => void;
    onCursorChange?: (line: number, column: number) => void;
  };

  let {
    documentId,
    value,
    language,
    readOnly,
    onChange,
    onSave,
    onCursorChange,
  }: Props = $props();

  let host: HTMLDivElement;
  let editor: monaco.editor.IStandaloneCodeEditor | undefined;
  let editorReady = $state(false);
  let activeDocumentId: string | undefined;
  let suppressChange = false;
  let focusRequestId = 0;
  const models = new Map<string, monaco.editor.ITextModel>();
  const viewStates = new Map<string, monaco.editor.ICodeEditorViewState>();
  const workers = new Set<Worker>();

  function focusWhenVisible(id: string) {
    const requestId = ++focusRequestId;
    let attempts = 0;
    const tryFocus = () => {
      if (requestId !== focusRequestId || activeDocumentId !== id || !editor || !host?.isConnected) return;
      const bounds = host.getBoundingClientRect();
      if (bounds.width > 0 && bounds.height > 0) {
        editor.focus();
      } else if (++attempts < 30) {
        requestAnimationFrame(tryFocus);
      }
    };
    requestAnimationFrame(tryFocus);
  }

  function modelFor(id: string, initialValue: string, modelLanguage: EditorLanguage) {
    let model = models.get(id);
    if (!model || model.isDisposed()) {
      model = monaco.editor.createModel(
        initialValue,
        modelLanguage,
        monaco.Uri.parse(`ego:///${encodeURIComponent(id)}`),
      );
      models.set(id, model);
    }
    return model;
  }

  onMount(() => {
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

    const initialModel = modelFor(documentId, value, language);
    activeDocumentId = documentId;
    editor = monaco.editor.create(host, {
      model: initialModel,
      theme: 'vs-dark',
      automaticLayout: true,
      ariaLabel: 'Редактор содержимого задачи',
      readOnly,
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
    editorReady = true;

    const contentSubscription = editor.onDidChangeModelContent(() => {
      if (!suppressChange && editor) onChange(editor.getValue());
    });
    const cursorSubscription = editor.onDidChangeCursorPosition((event) => {
      onCursorChange?.(event.position.lineNumber, event.position.column);
    });
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, () => onSave());
    editor.layout();
    focusWhenVisible(documentId);

    return () => {
      focusRequestId++;
      contentSubscription.dispose();
      cursorSubscription.dispose();
      editor?.dispose();
      editor = undefined;
      editorReady = false;
      for (const model of models.values()) model.dispose();
      models.clear();
      viewStates.clear();
      for (const worker of workers) worker.terminate();
      workers.clear();
      if (environmentWindow.MonacoEnvironment === editorEnvironment) {
        environmentWindow.MonacoEnvironment = previousEnvironment;
      }
    };
  });

  $effect(() => {
    const nextId = documentId;
    const nextValue = value;
    const nextLanguage = language;
    const nextReadOnly = readOnly;
    if (!editorReady || !editor) return;

    let model = models.get(nextId);
    if (!model || model.isDisposed()) model = modelFor(nextId, nextValue, nextLanguage);
    const firstPopulation = model.getValue().length === 0 && nextValue.length > 0;

    if (model.getLanguageId() !== nextLanguage) {
      monaco.editor.setModelLanguage(model, nextLanguage);
    }
    if (model.getValue() !== nextValue) {
      suppressChange = true;
      model.setValue(nextValue);
      suppressChange = false;
    }

    const documentChanged = activeDocumentId !== nextId;
    if (documentChanged) {
      if (activeDocumentId) {
        const previousState = editor.saveViewState();
        if (previousState) viewStates.set(activeDocumentId, previousState);
      }
      activeDocumentId = nextId;
      editor.setModel(model);
      const savedState = viewStates.get(nextId);
      if (savedState) editor.restoreViewState(savedState);
    }

    editor.updateOptions({ readOnly: nextReadOnly });
    editor.layout();
    if (documentChanged || firstPopulation) focusWhenVisible(nextId);
  });
</script>

<div class="monaco-host" bind:this={host} role="region" aria-label="Редактор содержимого задачи"></div>

<style>
  .monaco-host {
    width: 100%;
    height: 100%;
    min-height: 0;
    overflow: hidden;
  }
</style>
