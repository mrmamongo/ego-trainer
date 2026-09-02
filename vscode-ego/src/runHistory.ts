/** Pure helpers for validating and ordering local task run summaries. */

export interface TaskRunSummary {
    id: string;
    started_at: string;
    finished_at: string;
    status: string;
    passed_tests: number;
    total_tests: number;
}

function timestamp(value: unknown): string | undefined {
    if (typeof value !== 'string' || !value.trim() || Number.isNaN(Date.parse(value))) return undefined;
    return value;
}

function nonnegativeNumber(value: unknown, fallback: number): number | undefined {
    if (value === undefined || value === null) return fallback;
    if (typeof value !== 'number' || !Number.isFinite(value) || value < 0) return undefined;
    return value;
}

export function parseRunSummary(raw: unknown): TaskRunSummary | undefined {
    if (raw === null || typeof raw !== 'object') return undefined;
    const value = raw as Record<string, unknown>;
    if (typeof value.id !== 'string' || !value.id.trim()) return undefined;
    if (typeof value.status !== 'string' || !value.status.trim()) return undefined;
    const hasStarted = value.started_at !== undefined && value.started_at !== null;
    const hasFinished = value.finished_at !== undefined && value.finished_at !== null;
    const startedValue = hasStarted ? timestamp(value.started_at) : undefined;
    const finishedValue = hasFinished ? timestamp(value.finished_at) : undefined;
    if ((hasStarted && startedValue === undefined) || (hasFinished && finishedValue === undefined)) return undefined;
    const started = startedValue || finishedValue;
    const finished = finishedValue || startedValue;
    if (!started || !finished) return undefined;
    const passed = nonnegativeNumber(value.passed_tests, 0);
    const total = nonnegativeNumber(value.total_tests, 0);
    if (passed === undefined || total === undefined) return undefined;
    return {
        id: value.id,
        started_at: started,
        finished_at: finished,
        status: value.status,
        passed_tests: passed,
        total_tests: total,
    };
}

export function sortRecentRuns(runs: TaskRunSummary[], max = 20): TaskRunSummary[] {
    const limit = Number.isFinite(max) ? Math.max(0, Math.floor(max)) : 20;
    return [...runs]
        .sort((a, b) => {
            const time = Date.parse(b.finished_at || b.started_at) - Date.parse(a.finished_at || a.started_at);
            return time || a.id.localeCompare(b.id);
        })
        .slice(0, limit);
}
