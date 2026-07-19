/** Markdown → HTML for Task View (host-side, trusted task content). */

import { marked, type Tokens } from 'marked';

marked.setOptions({
    gfm: true,
    breaks: false,
});

const PY_KEYWORDS =
    /\b(and|as|assert|async|await|break|class|continue|def|del|elif|else|except|False|finally|for|from|global|if|import|in|is|lambda|None|nonlocal|not|or|pass|raise|return|True|try|while|with|yield)\b/g;

/** Lightweight Python highlighter for statement/hint code blocks. */
function highlightPython(code: string): string {
    const escaped = escapeHtml(code);
    return escaped
        .replace(/(#.*)$/gm, '<span class="tok-comment">$1</span>')
        .replace(
            /("(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|"""[\s\S]*?"""|'''[\s\S]*?''')/g,
            '<span class="tok-string">$1</span>'
        )
        .replace(PY_KEYWORDS, '<span class="tok-kw">$1</span>')
        .replace(/\b(\d+(?:\.\d+)?)\b/g, '<span class="tok-num">$1</span>');
}

function escapeHtml(s: string): string {
    return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

marked.use({
    renderer: {
        code({ text, lang }: Tokens.Code): string {
            const language = (lang || '').trim().toLowerCase();
            const body =
                language === 'python' || language === 'py'
                    ? highlightPython(text)
                    : escapeHtml(text);
            const cls = language ? `language-${language}` : '';
            return `<pre><code class="${cls}">${body}</code></pre>\n`;
        },
    },
});

/** Render arbitrary trusted markdown (hints, snippets) to HTML. */
export function renderMarkdownHtml(md: string): string {
    return marked.parse(md ?? '', { async: false }) as string;
}

/** Render task statement markdown to HTML. Strips reference-solution <details>. */
export function renderStatementHtml(md: string): string {
    const cleaned = stripSolutionDetails(md);
    return renderMarkdownHtml(cleaned);
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
