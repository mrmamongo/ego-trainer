/** Soft course recommendations: readiness formatting (pure, no vscode/DOM).
 *
 * A project may declare `recommended_after` (project.yaml → GET /projects):
 * a prerequisite project, a number of passed tasks and, optionally, a
 * minimum per kind tag (bug / modify / new). It is advisory only — nothing
 * here may block opening or checking a task. Unit-tested from
 * src/test/recommendations.test.ts.
 */

import type { Breakdown, ProjectInfo, RecommendedAfter, Readiness } from './api';

/** Kind tags of the exam breakdown, in display order. */
export const KIND_TAGS = ['bug', 'modify', 'new'] as const;

export const KIND_LABELS: Record<string, string> = {
    bug: 'Баги',
    modify: 'Доработки',
    new: 'Новое',
};

function countOf(value: unknown): number {
    const n = Number(value);
    return Number.isFinite(n) && n > 0 ? Math.floor(n) : 0;
}

/** Project id → row, tolerant to a missing/odd response. */
export function indexProjects(list: readonly ProjectInfo[] | null | undefined): Map<string, ProjectInfo> {
    const map = new Map<string, ProjectInfo>();
    if (!Array.isArray(list)) return map;
    for (const item of list) {
        if (item && typeof item.id === 'string' && item.id) map.set(item.id, item);
    }
    return map;
}

/** Projects whose recommendation is declared and not met, in catalog order. */
export function unmetRecommendations(
    list: readonly ProjectInfo[] | null | undefined
): ProjectInfo[] {
    if (!Array.isArray(list)) return [];
    return list
        .filter((p) => p && p.recommended_after && p.readiness && p.readiness.met === false)
        .slice()
        .sort((a, b) => (a.order ?? 0) - (b.order ?? 0) || String(a.id).localeCompare(String(b.id)));
}

/**
 * The tree description for an unmet recommendation, e.g.
 * `рекомендуем после XL-A: 14/21`. Null when there is nothing to show
 * (no recommendation or already met). A count the server did not send
 * (old server: readiness without numbers) renders as `?`; the per-kind
 * part is shown only when the server counted the kinds.
 */
export function readinessLine(
    project: Pick<ProjectInfo, 'recommended_after' | 'readiness'> | null | undefined,
    nameOf?: (id: string) => string | undefined
): string | null {
    const rec = project?.recommended_after;
    const readiness = project?.readiness;
    if (!rec || !readiness || readiness.met) return null;
    const name = (nameOf && nameOf(rec.project)) || rec.project;
    let line = `рекомендуем после ${name}: ${formatCount(readiness.passed)}/${formatCount(readiness.required)}`;
    if (rec.min_per_kind !== null && rec.min_per_kind !== undefined && hasPerKind(readiness.per_kind)) {
        const need = countOf(rec.min_per_kind);
        const parts = KIND_TAGS.map((kind) => {
            const passed = countOf(readiness.per_kind?.[kind]);
            return `${passed}/${need} ${(KIND_LABELS[kind] || kind).toLocaleLowerCase('ru')}`;
        });
        line += ` · ${parts.join(', ')}`;
    }
    return line;
}

function hasPerKind(perKind: Record<string, number> | null | undefined): boolean {
    return Boolean(perKind) && KIND_TAGS.some((kind) => Object.prototype.hasOwnProperty.call(perKind, kind));
}

function formatCount(value: unknown): number | '?' {
    return Number.isFinite(Number(value)) ? countOf(value) : '?';
}

/**
 * Tooltip for a project with an unmet recommendation: the note (when the
 * content author wrote one) plus the exact numbers. Null when met/absent.
 */
export function recommendationTooltip(
    project: Pick<ProjectInfo, 'recommended_after' | 'readiness'> | null | undefined,
    nameOf?: (id: string) => string | undefined
): string | null {
    const rec: RecommendedAfter | null | undefined = project?.recommended_after;
    const readiness: Readiness | null | undefined = project?.readiness;
    if (!rec || !readiness || readiness.met) return null;
    const prerequisite = (nameOf && nameOf(rec.project)) || rec.project;
    const details: string[] = [
        `Пройдено задач «${prerequisite}»: ${formatCount(readiness.passed)} из ${formatCount(readiness.required)}.`,
    ];
    if (rec.min_per_kind !== null && rec.min_per_kind !== undefined && hasPerKind(readiness.per_kind)) {
        const need = countOf(rec.min_per_kind);
        const kinds = KIND_TAGS.map(
            (kind) => `${(KIND_LABELS[kind] || kind).toLocaleLowerCase('ru')} ${countOf(readiness.per_kind?.[kind])}/${need}`
        ).join(', ');
        details.push(`По видам: ${kinds}.`);
    }
    details.push('Это рекомендация — можно начинать в любой момент.');
    return [rec.note.trim(), ...details].filter(Boolean).join('\n');
}

export interface BreakdownRow {
    key: string;
    label: string;
    passed: number;
    total: number;
    percent: number;
}

/** Rows of the exam breakdown card (bug / modify / new). */
export function breakdownRows(breakdown: Breakdown | null | undefined): BreakdownRow[] {
    const kinds = breakdown?.kinds ?? {};
    return KIND_TAGS.map((kind) => {
        const bucket = kinds[kind] ?? { passed: 0, total: 0 };
        const passed = countOf(bucket.passed);
        const total = Math.max(countOf(bucket.total), passed);
        const percent = total > 0 ? Math.round((Math.min(passed, total) / total) * 100) : 0;
        return { key: kind, label: KIND_LABELS[kind] || kind, passed, total, percent };
    });
}

/** True when the breakdown has at least one kind task (the card is worth showing). */
export function hasBreakdown(breakdown: Breakdown | null | undefined): boolean {
    return breakdownRows(breakdown).some((row) => row.total > 0);
}
