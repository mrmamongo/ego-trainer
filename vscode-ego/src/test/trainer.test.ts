import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import {
    parseTrace,
    patchTrace,
    parseParsons,
    patchParsons,
    parseTrainer,
    literalError,
    splitKeepEol,
    buildParsonsBody,
    bodyToArrangement,
    type TraceState,
    type ParsonsState,
    type ParsonsLine,
} from '../trainer';
import { handleTrainerMessage, runTrainerMessage, TRAINER_MSG, trainerKindFromTags } from '../trainerHost';

// Real content from the monorepo (docs/tasks/START): out/test -> vscode-ego -> repo root.
const FOLDERS = join(__dirname, '..', '..', '..', 'docs', 'tasks', 'START', 'catalog', 'projects',
    'python-start', 'folders');

function readTask(rel: string): string {
    // Checkouts differ (core.autocrlf); these cases are written for CRLF input, so force it.
    return readFileSync(join(FOLDERS, rel), 'utf-8').replace(/\r\n/g, '\n').replace(/\n/g, '\r\n');
}

function toCrlf(text: string): string {
    return text.replace(/\r\n/g, '\n').replace(/\n/g, '\r\n');
}

function traceState(text: string): TraceState {
    const state = parseTrace(text);
    assert.equal(state.supported, true);
    return state as TraceState;
}

function parsonsState(text: string): ParsonsState {
    const state = parseParsons(text);
    assert.equal(state.supported, true);
    return state as ParsonsState;
}

function at(lines: ParsonsLine[], ...texts: [string, number][]): ParsonsLine[] {
    return lines.map((line, index) => ({ ...line, ...(texts.length > index ? { level: texts[index][1] } : {}) }));
}

// Real files are all CRLF on disk; LF variants are derived with `.replace(/\r\n/g, '\n')`.
const V01 = '01_variables/task_v01.student.py';
const V12 = '01_variables/task_v12.student.py';
const FN01 = '02_functions/task_fn01.student.py';
const FN02 = '02_functions/task_fn02.student.py';
const FN09 = '02_functions/task_fn09.student.py';
const FN10 = '02_functions/task_fn10.student.py';
const L10 = '03_loops/task_l10.student.py';
const L23 = '03_loops/task_l23.student.py';

// === Trace parsing ===

test('trace: v01 code lines and after-labels', () => {
    const state = traceState(readTask(V01));
    assert.deepEqual(state.lines, [
        { label: '1', code: 'a = 10' },
        { label: '2', code: 'b = 4' },
        { label: '3', code: 'a = 7' },
        { label: '4', code: 'b = 1' },
    ]);
    assert.deepEqual(state.answers.map((a) => [a.name, a.label, a.value, a.line]), [
        ['a_after_1', 'a после строки 1', '', '1'],
        ['b_after_2', 'b после строки 2', '', '2'],
        ['a_after_3', 'a после строки 3', '', '3'],
        ['b_after_3', 'b после строки 3', '', '3'],
        ['a_after_4', 'a после строки 4', '', '4'],
        ['b_after_4', 'b после строки 4', '', '4'],
    ]);
    assert.match(state.intro, /Впиши вместо None/);
    assert.doesNotMatch(state.intro, /не меняй и не запускай/);
});

test('trace: v12 keeps free-form names as labels', () => {
    const state = traceState(readTask(V12));
    assert.deepEqual(state.lines.map((l) => l.label), ['1', '2', '3']);
    assert.deepEqual(state.answers.map((a) => [a.name, a.label, a.line]), [
        ['error_line', 'error_line', null],
        ['missing_name', 'missing_name', null],
    ]);
});

test('trace: fn01 _final labels', () => {
    const state = traceState(readTask(FN01));
    assert.deepEqual(state.answers.map((a) => a.label), ['a в конце', 'b в конце', 'c в конце']);
    assert.equal(state.lines.length, 6);
    assert.equal(state.lines[1].code, '    result = n * 2');
});

test('trace: fn02 keeps inline `name: explanation` comments as labels', () => {
    const state = traceState(readTask(FN02));
    const fee = state.answers[3];
    assert.equal(fee.name, 'fee_exists_outside');
    assert.match(fee.label, /^fee_exists_outside — True или False/);
    assert.equal(state.answers[0].label, 'x в конце');
});

test('trace: l23 parses two-digit line numbers', () => {
    const state = traceState(readTask(L23));
    assert.deepEqual(state.lines.map((l) => l.label),
        ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']);
    assert.equal(state.lines[9].code, '    return a, b, c');
    assert.deepEqual(state.answers.map((a) => a.name),
        ['role_of_a', 'role_of_b', 'role_of_c', 'role_of_d']);
});

test('trace: CRLF input parses like LF', () => {
    for (const rel of [V01, FN01, L23]) {
        const lf = readTask(rel);
        const crlf = toCrlf(lf);
        assert.equal(crlf.includes('\r\n'), true);
        assert.deepEqual(parseTrace(crlf), parseTrace(lf));
    }
});

test('trace: unsupported when the comment block or answers are missing', () => {
    const noBlock = 'def task_x_trace():\n    a = None\n    return a\n';
    assert.equal(parseTrace(noBlock).supported, false);
    const noAnswers = 'def task_x_trace():\n    #   1 | a = 1\n    return 1\n';
    const state = parseTrace(noAnswers);
    assert.equal(state.supported, false);
    assert.equal(state.kind, 'trace');
});

// === Trace patching ===

test('trace: patches only the answer lines (LF)', () => {
    const source = readTask(V01).replace(/\r\n/g, '\n');
    const patched = patchTrace(source, { a_after_1: '10', b_after_2: '4', a_after_3: '7' });
    const before = source.split('\n');
    const after = patched.split('\n');
    assert.equal(after.length, before.length);
    const changed = before.map((line, i) => (line === after[i] ? null : i)).filter((i) => i !== null);
    assert.deepEqual(changed, [10, 11, 12]);
    assert.equal(after[10], '    a_after_1 = 10');
    assert.equal(after[11], '    b_after_2 = 4');
    assert.equal(after[12], '    a_after_3 = 7');
    assert.equal(after[13], '    b_after_3 = None');
    assert.equal(traceState(patched).answers[0].value, '10');
});

test('trace: keeps CRLF endings byte-for-byte', () => {
    const source = readTask(V01);
    const patched = patchTrace(source, { a_after_1: '10', a_after_3: '7', b_after_4: '1' });
    assert.doesNotMatch(patched.replace(/\r\n/g, ''), /\n/);
    assert.equal(patched.split('\r\n').length, source.split('\r\n').length);
    assert.equal(patched, source
        .replace('    a_after_1 = None', '    a_after_1 = 10')
        .replace('    a_after_3 = None', '    a_after_3 = 7')
        .replace('    b_after_4 = None', '    b_after_4 = 1'));
});

test('trace: idempotent and tolerates falsy answers (0, False, empty string)', () => {
    const source = readTask(V01).replace(/\r\n/g, '\n');
    const once = patchTrace(source, { a_after_1: '0', b_after_2: 'False', a_after_3: "''" });
    assert.match(once, /    a_after_1 = 0\n/);
    assert.match(once, /    b_after_2 = False\n/);
    assert.match(once, /    a_after_3 = ''\n/);
    assert.equal(patchTrace(once, { a_after_1: '0', b_after_2: 'False', a_after_3: "''" }), once);
});

test('trace: keeps BOM and trailing comments, normalizes spaced assignment', () => {
    const source = '\uFEFFdef task_x_trace():\n    #   1 | a = 1\n\n    a_after_1  =  None  # ответ\n    ok = None\n\n    return a_after_1, ok\n';
    const patched = patchTrace(source, { a_after_1: "'да'", ok: 'True' });
    assert.equal(patched,
        '\uFEFFdef task_x_trace():\n    #   1 | a = 1\n\n    a_after_1  =  \'да\'  # ответ\n    ok = True\n\n    return a_after_1, ok\n');
});

test('trace: rejects invalid literals and unknown files', () => {
    const source = readTask(V01).replace(/\r\n/g, '\n');
    assert.throws(() => patchTrace(source, { a_after_1: 'abc' }), /литерал/);
    assert.throws(() => patchTrace(source, { a_after_1: 'None' }), /None/);
    assert.throws(() => patchTrace('def f():\n    pass\n', { a: '1' }), /строк с ответами/);
});

test('literal validation accepts Python scalars only', () => {
    for (const ok of ['1', '-2', '+3', '1.5', '.5', '2e3', "'x'", '"x"', "''", 'True', 'False', "'нечётное'"]) {
        assert.equal(literalError(ok), null, ok);
    }
    for (const bad of ['', 'abc', 'None', 'x + 1', '[1]', "'x", 'накопитель']) {
        assert.notEqual(literalError(bad), null, JSON.stringify(bad));
    }
    assert.equal(literalError('абв'), "Строку пишут в кавычках: 'абв'");
});

// === Parsons parsing ===

test('parsons: fn09 pool, def line and placeholder', () => {
    const state = parsonsState(readTask(FN09));
    assert.equal(state.defLine, 'def task_fn09_parity(n):');
    assert.equal(state.assembled, false);
    assert.deepEqual(state.lines, [
        { id: 0, text: 'return "нечётное"', level: 0 },
        { id: 1, text: 'if n % 2 == 0:', level: 0 },
        { id: 2, text: 'return "чётное"', level: 0 },
        { id: 3, text: 'else:', level: 0 },
    ]);
    assert.match(state.intro, /порядок и отступы/);
});

test('parsons: l10 CRLF input parses like LF', () => {
    const lf = readTask(L10);
    assert.deepEqual(parseParsons(toCrlf(lf)), parseParsons(lf));
    assert.equal(parsonsState(lf).lines.length, 5);
});

test('parsons: unsupported without the pool or the function', () => {
    assert.equal(parseParsons('def f():\n    return None\n').supported, false);
    const noPool = 'def f():\n    # Собери тело функции.\n    #\n    return None\n';
    assert.equal(parseParsons(noPool).supported, false);
});

// === Parsons patching ===

test('parsons: fn09 replaces the placeholder with the indented body (LF)', () => {
    const source = readTask(FN09).replace(/\r\n/g, '\n');
    const state = parsonsState(source);
    // return "нечётное" / if n % 2 == 0: / return "чётное" / else:
    const arranged = at(state.lines, ['x', 1], ['y', 0], ['x', 2], ['y', 0]);
    const patched = patchParsons(source, arranged);
    assert.equal(patched, [
        'def task_fn09_parity(n):',
        '    # Собери тело функции из строк ниже. Они перемешаны и записаны без отступов:',
        '    # порядок и отступы придётся расставить самому. Лишних строк нет.',
        '    #',
        '    #   return "нечётное"',
        '    #   if n % 2 == 0:',
        '    #   return "чётное"',
        '    #   else:',
        '    #',
        '        return "нечётное"',
        '    if n % 2 == 0:',
        '            return "чётное"',
        '    else:',
        '',
    ].join('\n'));
});

test('parsons: fn10 keeps CRLF byte-for-byte', () => {
    const source = readTask(FN10);
    assert.ok(source.includes('\r\n'));
    const state = parsonsState(source);
    // result = b / return result / if a > b: / result = a / else:
    const arranged = at(state.lines, ['x', 1], ['x', 2], ['y', 0], ['x', 2], ['y', 0]);
    const patched = patchParsons(source, arranged);
    assert.doesNotMatch(patched.replace(/\r\n/g, ''), /\n/);
    assert.equal(patched, source.replace(
        '    return None  # собери тело функции из строк выше\r\n',
        ['        result = b', '            return result', '    if a > b:', '            result = a', '    else:']
            .map((line) => line + '\r\n').join('')));
});

test('parsons: parses an assembled file back into a permutation of the pool', () => {
    const source = readTask(FN09).replace(/\r\n/g, '\n');
    const state = parsonsState(source);
    const arranged = at(state.lines, ['x', 1], ['y', 0], ['x', 2], ['y', 0]);
    const assembledText = patchParsons(source, arranged);
    const back = parsonsState(assembledText);
    assert.equal(back.assembled, true);
    assert.deepEqual(back.lines, arranged);
    assert.equal(back.defLine, state.defLine);
    // Patching an assembled file again is refused, the file stays untouched.
    assert.throws(() => patchParsons(assembledText, arranged), /уже собрано/);
});

test('parsons: assembled body that is not a permutation is unsupported', () => {
    const source = readTask(FN09).replace(/\r\n/g, '\n');
    const edited = patchParsons(source, at(parsonsState(source).lines, ['x', 1], ['x', 0], ['y', 0], ['y', 0]))
        .replace('return "чётное"', 'return "четное"');
    const state = parseParsons(edited);
    assert.equal(state.supported, false);
});

test('parsons: bodyToArrangement checks indentation and the pool', () => {
    const pool = ['a = 1', 'return a'];
    // Body lines are relative to `def`: each line has at least the function step.
    assert.deepEqual(bodyToArrangement(pool, ['    return a', '        a = 1']), { order: [1, 0], levels: { 0: 1, 1: 0 } });
    assert.equal(bodyToArrangement(pool, ['return a', '    a = 1']), null); // not indented under def
    assert.equal(bodyToArrangement(pool, ['    return a', '  a = 1']), null); // 2-space step
    assert.equal(bodyToArrangement(pool, ['return a']), null);
    assert.equal(bodyToArrangement(pool, ['return a', 'a = 2']), null);
});

test('parsons: nested indentation uses 4-space steps', () => {
    const state = parsonsState(readTask(L10));
    // return result / if number % 2 == 0: / result = [] / result.append(number) / for number in numbers:
    const arranged = at(state.lines, ['a', 0], ['b', 0], ['c', 1], ['d', 2], ['e', 1]);
    // buildParsonsBody is relative to `def`; the file gets one more step for the body.
    assert.deepEqual(buildParsonsBody(arranged), [
        '    return result',
        '    if number % 2 == 0:',
        '        result = []',
        '            result.append(number)',
        '        for number in numbers:',
    ]);
    assert.match(patchParsons(readTask(L10), arranged),
        /    return result\r\n    if number % 2 == 0:\r\n        result = \[\]\r\n            result\.append\(number\)\r\n        for number in numbers:\r\n$/);
    // Levels survive a round trip through the file (nested `def` indentation included).
    const back = parsonsState(patchParsons(readTask(L10), arranged));
    assert.deepEqual(back.lines, arranged);
    assert.equal(back.assembled, true);
});

// === Host handler ===

function hostHarness(initial: string) {
    const disk = { text: initial, writes: 0 };
    const posted: { type: string; payload?: unknown }[] = [];
    let checks = 0;
    const ctx = {
        pyUri: { toString: () => 'file:///task_v01.py' },
        readFile: async () => disk.text,
        writeFile: async (text: string) => { disk.text = text; disk.writes += 1; },
        runCheck: async () => { checks += 1; },
        post: (message: { type: string; payload?: unknown }) => { posted.push(message); },
    };
    return { ctx, disk, posted, checks: () => checks };
}

test('host: ignores unrelated messages', async () => {
    const h = hostHarness(readTask(V01));
    assert.equal(await handleTrainerMessage({ type: 'taskView.check' }, h.ctx), false);
    assert.equal(h.posted.length, 0);
});

test('host: load parses and posts trainer.state', async () => {
    const h = hostHarness(readTask(FN09));
    assert.equal(await handleTrainerMessage({ type: TRAINER_MSG.load, kind: 'parsons', taskId: 'FN09' }, h.ctx), true);
    assert.equal(h.posted.length, 1);
    assert.equal(h.posted[0].type, TRAINER_MSG.state);
    const state = (h.posted[0].payload as { state: ParsonsState }).state;
    assert.equal(state.kind, 'parsons');
    assert.equal(state.lines.length, 4);
});

test('host: trace submit patches, writes, posts and runs the check', async () => {
    const source = readTask(V01);
    const h = hostHarness(source);
    const answers: Record<string, string> = {};
    for (const a of traceState(source).answers) answers[a.name] = '1';
    const result = await runTrainerMessage({ type: TRAINER_MSG.submit, kind: 'trace', answers }, h.ctx);
    assert.equal(result.handled, true);
    assert.equal(h.disk.writes, 1);
    assert.equal(h.disk.text.split('\r\n').length, source.split('\r\n').length);
    assert.equal(h.checks(), 1);
    assert.deepEqual(h.posted.map((m) => m.type), [TRAINER_MSG.state, TRAINER_MSG.submitted]);
    assert.deepEqual(h.posted[1].payload, { ok: true });
    assert.equal((h.posted[0].payload as { state: TraceState }).state.answers[0].value, '1');
});

test('host: parsons submit applies the arrangement and keeps the comment block', async () => {
    const source = readTask(FN09);
    const h = hostHarness(source);
    const state = parsonsState(source);
    const lines = [state.lines[1], state.lines[2], state.lines[3], state.lines[0]].map((l, i) =>
        ({ id: l.id, level: i === 1 || i === 3 ? 1 : 0 }));
    await handleTrainerMessage({ type: TRAINER_MSG.submit, kind: 'parsons', lines }, h.ctx);
    assert.equal(h.checks(), 1);
    assert.match(h.disk.text, /#   return "нечётное"/);
    // The body is indented one step under `def`, the student's levels add to it.
    assert.match(h.disk.text,
        /    if n % 2 == 0:\r\n        return "чётное"\r\n    else:\r\n        return "нечётное"\r\n$/);
    const back = parseParsons(h.disk.text) as ParsonsState;
    assert.equal(back.assembled, true);
    assert.deepEqual(back.lines.map((l) => [l.id, l.level]), [[1, 0], [2, 1], [3, 0], [0, 1]]);
});

test('host: invalid submit reports an error without writing or checking', async () => {
    const h = hostHarness(readTask(V01));
    await handleTrainerMessage({ type: TRAINER_MSG.submit, kind: 'trace', answers: { a_after_1: 'nope' } }, h.ctx);
    assert.equal(h.disk.writes, 0);
    assert.equal(h.checks(), 0);
    const submitted = h.posted.find((m) => m.type === TRAINER_MSG.submitted);
    assert.equal((submitted?.payload as { ok: boolean }).ok, false);
});

test('host: unknown kinds and unreadable files stay unsupported', async () => {
    const h = hostHarness(readTask(V01));
    await handleTrainerMessage({ type: TRAINER_MSG.load, kind: undefined }, h.ctx);
    const state = (h.posted[0].payload as { state: { supported: boolean } }).state;
    assert.equal(state.supported, false);
    const broken = { ...h.ctx, readFile: async () => { throw new Error('EACCES'); } };
    assert.equal(await handleTrainerMessage({ type: TRAINER_MSG.load, kind: 'trace' }, broken), true);
});

test('tags pick the trainer kind', () => {
    assert.equal(trainerKindFromTags(['variables', 'trace', 'order']), 'trace');
    assert.equal(trainerKindFromTags(['functions', 'parsons', 'if-else']), 'parsons');
    assert.equal(trainerKindFromTags(['loops', 'write']), undefined);
    assert.equal(trainerKindFromTags(undefined), undefined);
});

test('parseTrainer dispatches by kind', () => {
    assert.equal(parseTrainer('trace', readTask(V01)).kind, 'trace');
    assert.equal(parseTrainer('parsons', readTask(FN09)).kind, 'parsons');
    assert.equal(parseTrainer(undefined, readTask(V01)).supported, false);
    assert.equal(parseTrainer('trace', readTask(FN09)).supported, false);
});

test('splitKeepEol keeps mixed terminators and BOM', () => {
    const split = splitKeepEol('\uFEFFa\r\nb\nc');
    assert.deepEqual(split, { lines: ['a', 'b', 'c'], eols: ['\r\n', '\n', ''], bom: true });
});
