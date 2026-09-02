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
