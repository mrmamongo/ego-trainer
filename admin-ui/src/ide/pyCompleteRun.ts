/**
 * Registers the offline Python completion provider on a Monaco editor.
 *
 * Kept separate from pyComplete.ts so the data stays Node-testable without
 * importing monaco (the runtime glue lives only here).
 */

import * as monaco from 'monaco-editor/esm/vs/editor/editor.api';
import {
	PY_BUILTINS,
	PY_KEYWORDS,
	PY_MODULES,
	PY_SNIPPETS,
	moduleBeforeDot,
	wordsFromDocument,
} from './pyComplete';

type Suggest = monaco.languages.CompletionItem;
type SuggestResult = monaco.languages.CompletionList;

const MODULES_LOWER = new Map<string, string[]>(
	Object.entries(PY_MODULES).map(([k, v]) => [k.toLowerCase(), v]),
);

export function registerPythonCompletion(
	monacoNs: typeof monaco,
	editor: monaco.editor.IStandaloneCodeEditor,
): monaco.IDisposable {
	return monacoNs.languages.registerCompletionItemProvider('python', {
		triggerCharacters: ['.', ' '],
		provideCompletionItems(model, position): SuggestResult {
			const word = model.getWordUntilPosition(position);
			const line = model.getLineContent(position.lineNumber).slice(0, position.column - 1);
			// Текст до каретки, заканчивающийся на текущее слово.
			const prefix = line.slice(0, line.length - word.word.length) + word.word;

			const range: monaco.IRange = {
				startLineNumber: position.lineNumber,
				endLineNumber: position.lineNumber,
				startColumn: word.startColumn,
				endColumn: word.endColumn,
			};

			const kind = monacoNs.languages.CompletionItemKind;
			const out: Suggest[] = [];

			// 1) `module.` → методы stdlib-модуля/типа.
			const mod = moduleBeforeDot(prefix);
			if (mod && !word.word) {
				const members = MODULES_LOWER.get(mod) ?? [];
				for (const m of members) {
					out.push({ label: m, kind: kind.Method, insertText: m, range });
				}
				return { suggestions: out };
			}

			// 2) Сниппеты.
			for (const [label, insert, detail] of PY_SNIPPETS) {
				if (label.startsWith(word.word.toLowerCase())) {
					out.push({
						label,
						kind: kind.Snippet,
						insertText: insert,
						insertTextRules: monacoNs.languages.CompletionItemInsertTextRule.InsertAsSnippet,
						detail,
						range,
					});
				}
			}

			// 3) Builtins.
			for (const [label, detail] of PY_BUILTINS) {
				const name = label.split('(')[0];
				if (name.startsWith(word.word.toLowerCase())) {
					out.push({ label, kind: kind.Function, insertText: label, detail, range });
				}
			}

			// 4) Ключевые слова.
			for (const kw of PY_KEYWORDS) {
				if (kw.startsWith(word.word.toLowerCase())) {
					out.push({ label: kw, kind: kind.Keyword, insertText: kw, range });
				}
			}

			// 5) Слова из текущего документа.
			const docWords = wordsFromDocument(model.getValue());
			const wordLower = word.word.toLowerCase();
			for (const w of docWords) {
				if (w !== word.word && w.toLowerCase().startsWith(wordLower)) {
					out.push({ label: w, kind: kind.Variable, insertText: w, range });
				}
			}

			return { suggestions: out };
		},
	});
}
