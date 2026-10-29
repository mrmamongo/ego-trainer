/** Interpreter of «Запустить» for a challenge project (ADR-0018 D18.6).
 *
 * Same resolution as `pythonSetup.setupPythonEnv`: a pyproject.toml in the
 * project folder means a uv environment, so the program starts with
 * `uv run python <entry>`. Otherwise a local `.venv` is used when present,
 * and finally the python under the configured `ego.pythonPath` (the
 * `python` command when it is empty).
 */

/** Setting with the python executable (absolute path or a command name). */
export const PYTHON_PATH_SETTING = 'pythonPath';

export interface ChallengeCommandInput {
    /** The `workspace.workspaceFolders` roots (a relative pythonPath resolves against the first). */
    workspaceFolders: readonly string[];
    /** `workspace.entry` of the challenge (default `main.py`). */
    entry: string;
    /** Value of `ego.pythonPath`. */
    pythonPath?: string;
    hasPyproject: boolean;
    /** A local `.venv` directory exists in the project folder. */
    hasVenv: boolean;
    platform?: NodeJS.Platform | string;
}

export interface ChallengeCommand {
    /** The executable (`uv`, the venv python, the interpreter). */
    command: string;
    /** Executable arguments (`run`, `python`) that are not the program. */
    subArgs: string[];
    /** Display form: `uv run python main.py`. */
    display: string;
}

/** Quote one shell argument for Windows cmd / POSIX sh. */
export function shellQuote(arg: string, platform: NodeJS.Platform | string = process.platform): string {
    if (platform === 'win32') {
        if (arg === '' || /[\s"&<>|^()]/.test(arg)) return `"${arg.replace(/"/g, '""')}"`;
        return arg;
    }
    if (arg === '' || /[^\w\-./:=@%+]/.test(arg)) return `'${arg.replace(/'/g, `'\\''`)}'`;
    return arg;
}

/** Resolve `ego.pythonPath`: absolute, `${workspaceFolder}…`-relative or a command. */
export function resolvePythonPath(pythonPath: string | undefined, workspaceFolders: readonly string[]): string {
    let value = (pythonPath ?? '').trim();
    if (!value) return 'python';
    const first = workspaceFolders[0];
    if (value.startsWith('${workspaceFolder}') && first) {
        value = first + value.slice('${workspaceFolder}'.length);
    } else if (value.startsWith('${workspaceFolder:')) {
        // `${workspaceFolder:name}` — the folder whose basename is `name`.
        const end = value.indexOf('}');
        const name = value.slice('${workspaceFolder:'.length, end);
        const match = workspaceFolders.find((folder) => folder.replace(/[\\/]+$/, '').split(/[\\/]/).pop() === name);
        if (match && end > 0) value = match + value.slice(end + 1);
    }
    if (/^(\/|[A-Za-z]:[\\/]|\\\\)/.test(value) || !/[\\/]/.test(value)) return value;
    return first ? `${first.replace(/[\\/]+$/, '')}/${value}` : value;
}

/** How «Запустить» starts the entry file of the project. */
export function challengeRunCommand(input: ChallengeCommandInput): ChallengeCommand {
    const platform = input.platform ?? process.platform;
    const venvPython = platform === 'win32' ? '.venv\\Scripts\\python.exe' : '.venv/bin/python';
    let command = 'python';
    let subArgs: string[] = [];
    if (input.hasPyproject) {
        command = 'uv';
        subArgs = ['run', 'python'];
    } else if (input.hasVenv) {
        command = venvPython;
    } else if ((input.pythonPath ?? '').trim()) {
        command = resolvePythonPath(input.pythonPath, input.workspaceFolders);
    }
    return { command, subArgs, display: [command, ...subArgs, input.entry].join(' ') };
}

/**
 * The line typed into the terminal. The entry is single-quoted because the
 * terminal may be PowerShell, cmd or bash; only the executable and its
 * sub-arguments are quoted per platform.
 */
export function challengeCommandLine(
    command: ChallengeCommand,
    entry: string,
    platform: NodeJS.Platform | string = process.platform
): string {
    const head = [command.command, ...command.subArgs].map((arg) => shellQuote(arg, platform)).join(' ');
    return `${head} '${entry.replace(/'/g, `''`)}'`;
}
