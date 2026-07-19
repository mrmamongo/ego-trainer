/** Markdown → HTML for Task View (host-side, trusted task content). */

import { marked } from 'marked';

marked.setOptions({
    gfm: true,
    breaks: false,
});

/** Render task statement markdown to HTML. Strips reference-solution <details>. */
export function renderStatementHtml(md: string): string {
    const cleaned = stripSolutionDetails(md);
    return marked.parse(cleaned, { async: false }) as string;
}

/** Remove <details>…</details> blocks (etalon solution etc.). */
export function stripSolutionDetails(md: string): string {
    return md.replace(/<details\b[\s\S]*?<\/details>/gi, '').trim();
}

export function extractSection(md: string, sectionName: string): string {
    const lines = md.split('\n');
    let capturing = false;
    const result: string[] = [];
    for (const line of lines) {
        if (line.trim().startsWith('## ') && line.includes(sectionName)) {
            capturing = true;
            continue;
        }
        if (capturing && line.trim().startsWith('## ')) break;
        if (capturing) result.push(line);
    }
    return result.join('\n').trim();
}

export function extractSignature(stubPy: string): string {
    for (const line of stubPy.split('\n')) {
        if (line.trim().startsWith('def task_')) {
            return line.trim().replace(/:$/, '');
        }
    }
    return '';
}
