/** Pure helpers for offlineCheck.ts (8bv.9.9 Windows/offline slice).
 *
 * No `vscode` import, no `child_process`, no filesystem access — every
 * function is deterministic and unit-testable with Node's built-in test
 * runner. The runtime entry point (`offlineCheck.ts`) composes these with
 * `spawn` and the VSCode API.
 */

/** Default platform used when a caller does not pass one explicitly. */
const DEFAULT_PLATFORM: string =
    typeof process !== 'undefined' && process.platform ? process.platform : '';

/**
 * Normalize a working directory into a stable cache key.
 *
 * - Backslashes are converted to forward slashes so the same directory
 *   written with either separator collides in the cache.
 * - Repeated separators are collapsed and a trailing separator is stripped
 *   (except for the POSIX root `/`).
 * - On Windows (case-insensitive FS) the result is lower-cased so that
 *   `C:\Foo` and `c:\foo` share a cache entry.
 *
 * The return value is **a key**, not a path: it must not be passed to
 * `spawn` as `cwd`. Use the original OS-native `cwd` for that.
 */
export function normalizeCwd(
    cwd: string,
    platform: string = DEFAULT_PLATFORM
): string {
    if (!cwd || typeof cwd !== 'string') return '';
    let p = cwd.trim();
    if (!p) return '';
    // Normalize separators to '/' for a stable cross-platform key.
    p = p.replace(/\\/g, '/');
    // Collapse repeated separators.
    p = p.replace(/\/+/g, '/');
    // Strip trailing slash, but keep the POSIX root '/'.
    if (p.length > 1 && p.endsWith('/')) p = p.slice(0, -1);
    // win32 filesystems are case-insensitive — lowercase for a stable key.
    if (platform === 'win32') p = p.toLowerCase();
    return p;
}

/** Cache key for the python/ego detection result. Alias of `normalizeCwd`. */
export function cwdCacheKey(
    cwd: string,
    platform: string = DEFAULT_PLATFORM
): string {
    return normalizeCwd(cwd, platform);
}

/**
 * Decide whether `spawn` should request a shell.
 *
 * On Windows the `ego` / `uv` console scripts are `.cmd` shims that Node
 * cannot launch directly without a shell. On POSIX we skip the shell to
 * keep argv handling exact and avoid quoting pitfalls.
 */
export function shouldUseShell(platform: string = DEFAULT_PLATFORM): boolean {
    return platform === 'win32';
}

/**
 * Build the child process environment.
 *
 * Preserves the caller-supplied env (defaults to `process.env` at call
 * time) and forces UTF-8 on stdout/stderr and the interpreter itself so
 * captured output decodes deterministically across locales.
 */
export function childEnv(
    env: NodeJS.ProcessEnv = typeof process !== 'undefined' ? process.env : {}
): NodeJS.ProcessEnv {
    return {
        ...env,
        PYTHONIOENCODING: 'utf-8',
        PYTHONUTF8: '1',
    };
}

export type TaskIdValidation =
    | { ok: true }
    | { ok: false; error: string };

/**
 * Validate a catalog task id before it can reach a shell.
 *
 * Accepted ids are made of ASCII letters, digits, and the separators
 * `.` `_` `-` (e.g. `block_f.task-1_2`). Anything else is rejected with an
 * actionable message. This is a defensive check: even when `shell:true` is
 * used on win32, a rejected id never becomes part of a command line.
 */
export function validateTaskId(taskId: string): TaskIdValidation {
    if (!taskId || typeof taskId !== 'string') {
        return { ok: false, error: 'Task id is required.' };
    }
    if (!/^[A-Za-z0-9._-]+$/.test(taskId)) {
        const preview = taskId.length > 40 ? taskId.slice(0, 40) + '…' : taskId;
        return {
            ok: false,
            error:
                `Invalid task id "${preview}". ` +
                'Expected only ASCII letters, digits, ".", "_", or "-" ' +
                '(e.g. block_f.task-1_2).',
        };
    }
    return { ok: true };
}
