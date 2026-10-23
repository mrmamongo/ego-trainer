/** Interactive trainers (task tags `trace` / `parsons`): pure parsing, validation and patching.
 *
 * The student .py file stays the single source of truth. Both trainers touch as
 * little as possible and keep every other byte (comments, frame code, CRLF/LF
 * endings, BOM):
 *  - trace:   patches only the `name = <value>` answer lines inside the trace function;
 *  - parsons: replaces the `return None  # собери ...` placeholder with the assembled body.
 *
 * No `vscode` imports here: node:test covers this module directly and
 * `trainerHost.ts` reuses it on the extension side.
 */

// === Types (mirrored for the webview in webview/shared/types.ts) ===

export type TrainerKind = 'trace' | 'parsons';

export interface TraceLine {
    /** Label from the comment block: "1", "A2", "10". */
    label: string;
    /** Code after the `|`, Python indentation kept. */
    code: string;
}

export interface TraceAnswer {
    name: string;
    /** Human label: `a после строки 3`, `x в конце`, otherwise the name itself. */
    label: string;
    /** Prefilled Python literal; '' when the value is still None. */
    value: string;
    /** Trace line the label refers to, if any. */
    line: string | null;
}

export interface TraceState {
    kind: 'trace';
    supported: true;
    /** Comment text that explains the trace, shown under the code. */
    intro: string;
    lines: TraceLine[];
    answers: TraceAnswer[];
}

export interface ParsonsLine {
    id: number;
    /** Trimmed line as written in the pool. */
    text: string;
    /** Nesting level the student gave it (0 = directly in the function body). */
    level: number;
}

export interface ParsonsState {
    kind: 'parsons';
    supported: true;
    /** `def name(args):` as written in the file. */
    defLine: string;
    intro: string;
    /** Current arrangement, always a permutation of the pool. */
    lines: ParsonsLine[];
    /** True when the placeholder is gone and the body was parsed back. */
    assembled: boolean;
}

export interface UnsupportedState {
    kind: TrainerKind | null;
    supported: false;
    reason: string;
}

export type TrainerState = TraceState | ParsonsState | UnsupportedState;

export type TraceAnswers = Record<string, string>;

export interface ParsonsArrangement {
    /** Line ids in display order. */
    order: number[];
    /** Nesting level per line id. */
    levels: Record<number, number>;
}

/** One indentation step, in spaces, inside the function body. */
export const PARSONS_INDENT = '    ';

const TRACE_CAPTION = /Код для трассировки/i;
// `#   3 | a = 7` or `#  10 | ...`: the line content keeps its Python indentation.
const TRACE_HEADER = /^# +(\d+) \|(?: (.*))?$/;
const TRACE_ANSWER_COMMENT = /^#\s*([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.+)$/;
// A line starting a function at column 0 (comments are checked separately).
const DEF_LINE = /^(?:async\s+)?def\s+[A-Za-z_][A-Za-z0-9_]*\s*\(/;
const PARSONS_HEADER = /^#\s*Собери/u;
// Pool lines are written as `#   code` (comment + at least two spaces + code).
const PARSONS_POOL_LINE = /^# {2,}(.*)$/;
/** `return None  # собери ...`: the line the assembled body replaces. */
const PLACEHOLDER_LINE = /^return None\s*(?:#.*)?$/;
const PY_NAME = /^[A-Za-z_][A-Za-z0-9_]*$/;
const PY_NUMBER = /^[+-]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][+-]?\d+)?$/;

// === Line access helpers (byte preserving) ===

interface SplitText {
    /** Lines without CR/LF. */
    lines: string[];
    /** Terminator after each line: '\r\n', '\n' or '' for the last one. */
    eols: string[];
    bom: boolean;
}

/** Split a file keeping its own line endings so a patch stays byte-identical. */
export function splitKeepEol(text: string): SplitText {
    const bom = text.startsWith('\uFEFF');
    const body = bom ? text.slice(1) : text;
    const lines: string[] = [];
    const eols: string[] = [];
    const re = /\r\n|\n/g;
    let start = 0;
    let match: RegExpExecArray | null;
    while ((match = re.exec(body)) !== null) {
        lines.push(body.slice(start, match.index));
        eols.push(match[0]);
        start = match.index + match[0].length;
    }
    if (start < body.length) {
        lines.push(body.slice(start));
        eols.push('');
    }
    return { lines, eols, bom };
}

function joinKeepEol(split: SplitText): string {
    let out = split.bom ? '\uFEFF' : '';
    for (let i = 0; i < split.lines.length; i++) out += split.lines[i] + split.eols[i];
    return out;
}

/** Terminator used for lines inserted into `text` (CRLF wins when present). */
export function dominantEol(text: string): string {
    return text.includes('\r\n') ? '\r\n' : '\n';
}

function indentOf(line: string): number {
    return line.length - line.trimStart().length;
}

/** Trim the end only: leading spaces matter inside `#   code` comments. */
function trimEnd(line: string): string {
    return line.replace(/\s+$/, '');
}

/** Drop the Python indentation in front of a `#` comment. */
function trimIndent(line: string): string {
    return line.slice(indentOf(line));
}

function stripHashComment(trimmed: string): string {
    const m = /^#\s?(.*)$/.exec(trimmed);
    return m ? m[1].trim() : trimmed;
}

/** Trailing `# ...` of a code line, quote aware; '' when there is none. */
function trailingComment(code: string): string {
    let quote: string | null = null;
    for (let i = 0; i < code.length; i++) {
        const ch = code[i];
        if (quote) {
            if (ch === '\\') { i++; continue; }
            if (ch === quote) quote = null;
            continue;
        }
        if (ch === "'" || ch === '"') { quote = ch; continue; }
        if (ch === '#') return code.slice(i).trimEnd();
    }
    return '';
}

// === Python literal validation (webview inputs) ===

/** Null when `raw` is an acceptable Python literal, otherwise a Russian reason. */
export function literalError(raw: string): string | null {
    const text = raw.trim();
    if (text === '') return 'Впиши значение';
    if (text === 'None') return 'Нужно значение, а не None';
    if (text === 'True' || text === 'False') return null;
    if (PY_NUMBER.test(text)) return null;
    if (text[0] === "'" || text[0] === '"') {
        const quote = text[0];
        if (text.length < 2 || text[text.length - 1] !== quote) return 'Не хватает закрывающей кавычки';
        const inner = text.slice(1, -1);
        if (inner.includes(quote) && !inner.includes('\\' + quote)) return 'Закрой строку кавычкой';
        return null;
    }
    if (PY_NAME.test(text)) return "Строку пишут в кавычках: '" + text + "'";
    if (/^[^\s"'()[\]{}=+\-*/%<>!&|^~,.:;]+$/.test(text)) return "Строку пишут в кавычках: '" + text + "'";
    return 'Нужен литерал Python: число, строка в кавычках или True/False';
}

// === Trace ===

interface TraceBlock {
    /** `# Код для трассировки ...` caption line. */
    captionIndex: number;
    /** Line of the first code header (`#   1 | ...`). */
    introStart: number;
    lines: TraceLine[];
}

function findTraceBlock(lines: string[]): TraceBlock | null {
    let captionIndex = -1;
    for (let i = 0; i < lines.length; i++) {
        if (TRACE_CAPTION.test(lines[i]) && /^\s*#/.test(lines[i])) { captionIndex = i; break; }
    }
    if (captionIndex < 0) return null;
    let first = -1;
    for (let i = captionIndex + 1; i < lines.length; i++) {
        if (TRACE_HEADER.test(trimEnd(trimIndent(lines[i])))) { first = i; break; }
        if (lines[i].trim() !== '' && !/^\s*#/.test(lines[i])) return null;
    }
    if (first < 0) return null;
    const parsed: TraceLine[] = [];
    let i = first;
    for (; i < lines.length; i++) {
        const m = TRACE_HEADER.exec(trimEnd(trimIndent(lines[i])));
        if (!m) break;
        parsed.push({ label: m[1], code: (m[2] ?? '').trimEnd() });
    }
    return { captionIndex, introStart: first, lines: parsed };
}

interface Assignment {
    index: number;
    indent: string;
    name: string;
    value: string;
}

function topLevelDef(lines: string[]): number {
    for (let i = 0; i < lines.length; i++) {
        if (DEF_LINE.test(lines[i])) return i;
    }
    return -1;
}

/** Plain `name = value` lines inside the trace function before its `return`. */
function findTraceAssignments(lines: string[]): Assignment[] {
    const defIndex = topLevelDef(lines);
    if (defIndex < 0) return [];
    const found: Assignment[] = [];
    for (let i = defIndex + 1; i < lines.length; i++) {
        const line = lines[i];
        const trimmed = line.trim();
        if (trimmed === '') continue;
        if (!/^\s/.test(line)) break;            // next top-level statement
        if (trimmed.startsWith('#')) continue;   // comment
        if (/^return\b/.test(trimmed)) break;    // frame line: answers end here
        const m = /^(\s+)([A-Za-z_][A-Za-z0-9_]*)\s*=(?!=)\s*(.*)$/.exec(line);
        if (!m) continue;
        found.push({ index: i, indent: m[1], name: m[2], value: m[3].trimEnd() });
    }
    return found;
}

/** `# name: explanation` comments that name an answer variable. */
function commentLabels(lines: string[], before: number): Map<string, string> {
    const labels = new Map<string, string>();
    for (let i = 0; i < before; i++) {
        const m = TRACE_ANSWER_COMMENT.exec(lines[i].trim());
        if (m && !labels.has(m[1])) labels.set(m[1], m[2].trim());
    }
    return labels;
}

/** Multi-line `# name: ...` explanation immediately above the answer line. */
function inlineAnswerComment(lines: string[], index: number, name: string): string | undefined {
    const first = TRACE_ANSWER_COMMENT.exec(lines[index - 1]?.trim() ?? '');
    if (!first || first[1] !== name) return undefined;
    return first[2].trim();
}

/**
 * Comment text between the code block and the answers. `# name: ...` comments
 * that only describe answer variables are left out (they become input labels).
 */
function traceIntro(lines: string[], block: TraceBlock): string {
    const parts: string[] = [];
    for (let i = lines.length - 1; i > block.captionIndex; i--) {
        const raw = lines[i];
        if (!/^\s*#/.test(raw)) continue;                              // code / blank line
        const trimmed = trimEnd(trimIndent(raw));
        if (TRACE_HEADER.test(trimmed) || TRACE_CAPTION.test(trimmed)) continue; // code lines / caption
        const content = stripHashComment(trimmed);
        if (content === '') continue;                                  // `#` separator
        const answerComment = TRACE_ANSWER_COMMENT.exec(trimmed);
        // `# name: ...` lines describe one input; `# Впиши вместо None ...` is the task text.
        if (answerComment && !/^Впиши\b/.test(answerComment[1])) continue;
        parts.unshift(content);
    }
    return parts.join(' ').replace(/\s+/g, ' ').trim();
}

function answerLabel(name: string): { label: string; line: string | null } {
    const before = /^(.+)_before_(.+)$/.exec(name);
    if (before) return { label: before[1] + ' до строки ' + before[2], line: before[2] };
    const after = /^(.+)_after_(.+)$/.exec(name);
    if (after) return { label: after[1] + ' после строки ' + after[2], line: after[2] };
    if (name.endsWith('_final') && name.length > '_final'.length) {
        return { label: name.slice(0, -'_final'.length) + ' в конце', line: null };
    }
    return { label: name, line: null };
}

/** Parse a `trace` task from the student's .py text. */
export function parseTrace(text: string): TraceState | UnsupportedState {
    const lines = splitKeepEol(text).lines;
    const block = findTraceBlock(lines);
    if (!block) {
        return { kind: 'trace', supported: false, reason: 'Не найден блок с кодом для трассировки.' };
    }
    const assignments = findTraceAssignments(lines);
    if (assignments.length === 0) {
        return { kind: 'trace', supported: false, reason: 'Не найдены строки с ответами (переменные = None).' };
    }
    const comments = commentLabels(lines, lines.length);
    const answers: TraceAnswer[] = assignments.map((a) => {
        const named = answerLabel(a.name);
        const comment = inlineAnswerComment(lines, a.index, a.name) ?? comments.get(a.name);
        return {
            name: a.name,
            label: comment ? a.name + ' — ' + comment : named.label,
            value: a.value === 'None' ? '' : a.value,
            line: named.line,
        };
    });
    return { kind: 'trace', supported: true, intro: traceIntro(lines, block), lines: block.lines, answers };
}

/**
 * Replace only the given answer assignments: indentation, name, `=` and any
 * trailing comment stay as they are; every other line stays byte-identical.
 */
export function patchTrace(text: string, answers: TraceAnswers): string {
    const split = splitKeepEol(text);
    const found = findTraceAssignments(split.lines);
    if (found.length === 0) throw new Error('В файле больше нет строк с ответами.');
    for (const answer of found) {
        if (!Object.prototype.hasOwnProperty.call(answers, answer.name)) continue;
        const value = answers[answer.name].trim();
        if (literalError(value) !== null) throw new Error('Значение «' + answers[answer.name] + '» не похоже на литерал Python.');
        const rest = split.lines[answer.index].slice(answer.indent.length + answer.name.length);
        const eq = /^[ \t]*=(?!=)[ \t]*/.exec(rest);
        if (!eq) continue;
        const comment = trailingComment(answer.value);
        split.lines[answer.index] =
            answer.indent + answer.name + eq[0] + value + (comment ? '  ' + comment : '');
    }
    return joinKeepEol(split);
}

// === Parsons ===

interface ParsonsSource {
    defIndex: number;
    defIndent: string;
    defLine: string;
    headerIndex: number;
    pool: string[];
    /** Index of the `return None  # собери ...` line, when still present. */
    placeholderIndex: number | null;
    /** Body lines (dedented, no placeholder) once the task was assembled. */
    body: string[];
}

function parseParsonsSource(text: string): ParsonsSource | UnsupportedState {
    const lines = splitKeepEol(text).lines;
    let defIndex = -1;
    for (let i = 0; i < lines.length; i++) {
        if (!/^\s*#/.test(lines[i]) && DEF_LINE.test(lines[i])) { defIndex = i; break; }
    }
    if (defIndex < 0) return { kind: 'parsons', supported: false, reason: 'Не найдена функция, тело которой нужно собрать.' };
    const defIndent = lines[defIndex].slice(0, indentOf(lines[defIndex]));
    let headerIndex = -1;
    for (let i = defIndex + 1; i < lines.length; i++) {
        if (PARSONS_HEADER.test(trimEnd(trimIndent(lines[i])))) { headerIndex = i; break; }
        if (lines[i].trim() !== '' && !/^\s*#/.test(lines[i])) break;
    }
    if (headerIndex < 0) return { kind: 'parsons', supported: false, reason: 'Не найден комментарий «Собери...» со строками функции.' };
    // Pool: `#   code` lines after the header (blank `#` comments around it are fine),
    // ending at the first non-comment line — the placeholder or the assembled body.
    const pool: string[] = [];
    let bodyStart = headerIndex + 2; // skip the `# Собери ...` header itself
    for (; bodyStart < lines.length; bodyStart++) {
        const trimmed = trimEnd(trimIndent(lines[bodyStart]));
        if (trimmed === '#') continue;
        const m = PARSONS_POOL_LINE.exec(trimmed);
        if (!m) break;
        pool.push(m[1].trimEnd());
    }
    if (pool.length === 0) return { kind: 'parsons', supported: false, reason: 'В комментарии нет строк для сборки.' };
    // Placeholder and/or the assembled body right after the comment block.
    while (bodyStart < lines.length && /^\s+#/.test(lines[bodyStart])) bodyStart++;
    let placeholderIndex: number | null = null;
    const body: string[] = [];
    for (let i = bodyStart; i < lines.length; i++) {
        const line = lines[i];
        const trimmed = line.trim();
        if (trimmed === '') { body.push(''); continue; }
        if (!/^\s/.test(line)) break; // next top-level statement closes the function
        if (placeholderIndex === null && body.every((b) => b === '') && PLACEHOLDER_LINE.test(trimmed)) {
            placeholderIndex = i;
            continue;
        }
        if (trimmed.startsWith('#')) break; // trailing comment: body ended
        body.push(line.slice(defIndent.length).trimEnd());
    }
    while (body.length && body[body.length - 1] === '') body.pop();
    return { defIndex, defIndent, defLine: lines[defIndex].trim(), headerIndex, pool, placeholderIndex, body };
}

function poolInitial(pool: string[]): ParsonsLine[] {
    return pool.map((text, id) => ({ id, text, level: 0 }));
}

function isUnsupported(value: ParsonsSource | UnsupportedState): value is UnsupportedState {
    return 'supported' in value;
}

/**
 * Map body lines (relative to `def`, so every line has at least one step) back
 * to pool ids when they are a permutation of the pool.
 */
export function bodyToArrangement(pool: string[], body: string[]): ParsonsArrangement | null {
    const used = new Set<number>();
    const order: number[] = [];
    const levels: Record<number, number> = {};
    for (const raw of body) {
        const indent = indentOf(raw);
        if (indent % 4 !== 0 || indent === 0) return null; // must sit inside the function
        const text = raw.trim();
        const id = pool.findIndex((line, index) => line === text && !used.has(index));
        if (id < 0) return null;
        used.add(id);
        order.push(id);
        levels[id] = indent / 4 - 1;
    }
    return order.length === pool.length ? { order, levels } : null;
}

/** Apply an arrangement to the pool. */
export function arrangeLines(pool: string[], arrangement: ParsonsArrangement): ParsonsLine[] {
    return arrangement.order.map((id) => ({
        id,
        text: pool[id],
        level: Math.max(0, Math.trunc(arrangement.levels[id] ?? 0)),
    }));
}

/**
 * Parse a `parsons` task. The pool order is the starting arrangement; when the
 * placeholder is gone the current body is parsed back and ids follow the pool.
 */
export function parseParsons(text: string): ParsonsState | UnsupportedState {
    const source = parseParsonsSource(text);
    if (isUnsupported(source)) return source;
    if (source.placeholderIndex === null && source.body.length > 0) {
        const arrangement = bodyToArrangement(source.pool, source.body);
        if (!arrangement) {
            return { kind: 'parsons', supported: false, reason: 'Собранное тело не совпадает со строками из комментария.' };
        }
        return {
            kind: 'parsons',
            supported: true,
            defLine: source.defLine,
            intro: parsonsIntro(text, source),
            lines: arrangeLines(source.pool, arrangement),
            assembled: true,
        };
    }
    return {
        kind: 'parsons',
        supported: true,
        defLine: source.defLine,
        intro: parsonsIntro(text, source),
        lines: poolInitial(source.pool),
        assembled: false,
    };
}

/** The `# Собери ...` header plus the plain comment line that often follows it. */
function parsonsIntro(text: string, source: ParsonsSource): string {
    const lines = splitKeepEol(text).lines;
    const parts: string[] = [];
    for (let i = source.headerIndex; i < lines.length; i++) {
        const raw = lines[i];
        if (!/^\s*#/.test(raw)) break;
        const trimmed = trimEnd(trimIndent(raw));
        if (trimmed === '#' || PARSONS_POOL_LINE.test(trimmed)) break; // pool reached
        parts.push(stripHashComment(trimmed));
    }
    const intro = parts.join(' ').replace(/\s+/g, ' ').trim();
    return intro || 'Расставь строки в правильном порядке и задай отступы.';
}

/** Body lines to insert instead of the placeholder (relative indent starts with one step). */
export function buildParsonsBody(lines: ParsonsLine[]): string[] {
    return lines.map((line) => PARSONS_INDENT + PARSONS_INDENT.repeat(Math.max(0, line.level)) + line.text);
}

/** Replace the placeholder line with the assembled body; keep everything else as is. */
export function patchParsons(text: string, lines: ParsonsLine[]): string {
    const split = splitKeepEol(text);
    const source = parseParsonsSource(text);
    if (isUnsupported(source)) throw new Error(source.reason);
    if (source.placeholderIndex === null) throw new Error('Тело уже собрано: строка return None заменена кодом.');
    // Body lines are relative to the `def`; keep any extra indentation of a nested def.
    const prefix = split.lines[source.placeholderIndex].slice(0, indentOf(split.lines[source.defIndex]));
    const body = buildParsonsBody(lines).map((line) => prefix + line);
    if (body.length > 1) {
        const eol = split.eols[source.placeholderIndex] || dominantEol(text);
        split.eols.splice(source.placeholderIndex, 1, ...body.map(() => eol));
    }
    split.lines.splice(source.placeholderIndex, 1, ...body);
    return joinKeepEol(split);
}

// === Dispatcher ===

/** Parse by task tag (`trace` / `parsons`); unknown kinds stay unsupported. */
export function parseTrainer(kind: TrainerKind | null | undefined, text: string): TrainerState {
    if (kind === 'trace') return parseTrace(text);
    if (kind === 'parsons') return parseParsons(text);
    return { kind: null, supported: false, reason: 'Это задание не поддерживает тренажёр.' };
}
