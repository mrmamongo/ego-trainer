export function assertSafeCatalogSegment(value: string, label: string): void {
    const deviceName = /^(?:con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\.|$)/i;
    if (
        !value ||
        value === '.' ||
        value === '..' ||
        !/^[A-Za-z0-9_.-]+$/.test(value) ||
        value.startsWith('.') ||
        value.endsWith('.') ||
        value.startsWith(' ') ||
        value.endsWith(' ') ||
        deviceName.test(value)
    ) {
        throw new Error(`Unsafe ${label}: ${value}`);
    }
}

export type FileDecision = 'create' | 'unchanged' | 'conflict';

export function decideTextFile(
    existing: string | undefined,
    incoming: string
): FileDecision {
    if (existing === undefined) return 'create';

    const normalizeNewlines = (text: string): string => text.replace(/\r\n/g, '\n');
    return normalizeNewlines(existing) === normalizeNewlines(incoming)
        ? 'unchanged'
        : 'conflict';
}

export type ManifestTaskEntry = {
    id: string;
    block: string;
    slug: string;
    version: string;
    content_hash: string;
    pulled_at: string;
    md_path: string;
    md_modified?: boolean;
    stub_modified?: boolean;
};

export function mergeManifestEntries(
    existing: ManifestTaskEntry[],
    incoming: ManifestTaskEntry[]
): ManifestTaskEntry[] {
    const merged = new Map<string, ManifestTaskEntry>();

    for (const entry of existing) {
        merged.set(entry.id.toLowerCase(), { ...entry });
    }

    for (const entry of incoming) {
        const key = entry.id.toLowerCase();
        const previous = merged.get(key);
        const next: ManifestTaskEntry = { ...entry };

        if (typeof entry.md_modified !== 'boolean') {
            if (typeof previous?.md_modified === 'boolean') {
                next.md_modified = previous.md_modified;
            } else {
                delete next.md_modified;
            }
        }
        if (typeof entry.stub_modified !== 'boolean') {
            if (typeof previous?.stub_modified === 'boolean') {
                next.stub_modified = previous.stub_modified;
            } else {
                delete next.stub_modified;
            }
        }

        merged.set(key, next);
    }

    return Array.from(merged.values()).sort((a, b) =>
        a.id.localeCompare(b.id)
    );
}

/** Server task fields the planner needs (`TaskMeta` is a superset). */
export type PullTaskMeta = {
    id: string;
    version: string;
    content_hash: string;
};

export type PullPlan<T extends PullTaskMeta> = {
    /** New or changed tasks — download via GET /tasks/{id}. */
    fetch: T[];
    /** Manifest matches server and local .md/.py exist — leave untouched. */
    upToDate: T[];
};

/**
 * Decide which server tasks need a download. A task is up to date when the
 * manifest has an entry with the same id (case-insensitive), the same
 * `version` and `content_hash`, and its `.md` and `.py` files still exist.
 * Everything else (new, changed, missing files, no manifest entry) is fetched.
 *
 * `localFilesExist` receives the manifest entry (for its `md_path`) and the
 * server task; it returns whether both task files are on disk.
 */
export function planPull<T extends PullTaskMeta>(
    serverTasks: readonly T[],
    manifestEntries: readonly ManifestTaskEntry[],
    localFilesExist: (entry: ManifestTaskEntry, task: T) => boolean
): PullPlan<T> {
    const byId = new Map<string, ManifestTaskEntry>();
    for (const entry of manifestEntries) {
        byId.set(entry.id.toLowerCase(), entry);
    }

    const plan: PullPlan<T> = { fetch: [], upToDate: [] };
    for (const task of serverTasks) {
        const entry = byId.get(task.id.toLowerCase());
        const current =
            entry !== undefined &&
            entry.version === task.version &&
            entry.content_hash === task.content_hash &&
            localFilesExist(entry, task);
        (current ? plan.upToDate : plan.fetch).push(task);
    }
    return plan;
}
