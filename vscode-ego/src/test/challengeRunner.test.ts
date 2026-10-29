import { test } from 'node:test';
import assert from 'node:assert/strict';
import { challengeCommandLine, challengeRunCommand, resolvePythonPath, shellQuote } from '../challengeRunner';

const BASE = { workspaceFolders: ['C:\\Work\\proj'], entry: 'main.py', hasPyproject: false, hasVenv: false };

test('a plain project runs python main.py with the configured interpreter', () => {
    assert.deepEqual(challengeRunCommand(BASE), { command: 'python', subArgs: [], display: 'python main.py' });
    assert.equal(challengeCommandLine(challengeRunCommand(BASE), 'main.py'), `python 'main.py'`);
});

test('a uv project runs through uv run python, a .venv project through its python', () => {
    const uv = challengeRunCommand({ ...BASE, hasPyproject: true });
    assert.deepEqual([uv.command, ...uv.subArgs], ['uv', 'run', 'python']);
    assert.equal(uv.display, 'uv run python main.py');
    const win = challengeRunCommand({ ...BASE, hasVenv: true, platform: 'win32' });
    assert.equal(win.command, '.venv\\Scripts\\python.exe');
    const posix = challengeRunCommand({ ...BASE, hasVenv: true, platform: 'linux' });
    assert.equal(posix.command, '.venv/bin/python');
});

test('ego.pythonPath wins over the python command and resolves workspace variables', () => {
    assert.equal(resolvePythonPath(undefined, ['C:\\w']), 'python');
    assert.equal(resolvePythonPath('  ', ['C:\\w']), 'python');
    assert.equal(resolvePythonPath('C:\\Python311\\python.exe', []), 'C:\\Python311\\python.exe');
    assert.equal(resolvePythonPath('${workspaceFolder}/.venv/bin/python', ['/home/u/proj']), '/home/u/proj/.venv/bin/python');
    assert.equal(resolvePythonPath('${workspaceFolder:proj}/py.exe', ['/a', '/b/proj']), '/b/proj/py.exe');
    assert.equal(resolvePythonPath('bin/python3', ['/home/u/proj/']), '/home/u/proj/bin/python3');
    const run = challengeRunCommand({ ...BASE, pythonPath: 'C:\\Python311\\python.exe', platform: 'win32' });
    assert.equal(run.command, 'C:\\Python311\\python.exe');
    // pyproject (uv) and an explicit path: the uv environment is the project's one.
    assert.equal(challengeRunCommand({ ...BASE, pythonPath: 'py', hasPyproject: true }).command, 'uv');
});

test('shell quoting keeps spaces and the entry file safe', () => {
    assert.equal(shellQuote('plain', 'win32'), 'plain');
    assert.equal(shellQuote('C:\\Program Files\\Python\\python.exe', 'win32'), '"C:\\Program Files\\Python\\python.exe"');
    assert.equal(shellQuote('my file.py', 'linux'), "'my file.py'");
    const cmd = challengeRunCommand({ ...BASE, pythonPath: 'C:\\Program Files\\Python\\python.exe', platform: 'linux' });
    assert.equal(challengeCommandLine(cmd, 'main.py', 'linux'), "'C:\\Program Files\\Python\\python.exe' 'main.py'");
    assert.equal(challengeCommandLine(cmd, "it's.py", 'linux'), "'C:\\Program Files\\Python\\python.exe' 'it''s.py'");
});
