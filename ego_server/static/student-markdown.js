/* Small, safe markdown renderer for course content. No HTML is injected. */
(function (root) {
  'use strict';

  function appendInline(source, target) {
    const pattern = /(\[[^\]]+\]\((?:https?:\/\/|task:|lesson:)[^)]+\)|`[^`]+`|\*\*[^*]+\*\*|__[^_]+__|\*[^*]+\*)/g;
    let cursor = 0;
    for (const match of String(source).matchAll(pattern)) {
      target.append(document.createTextNode(String(source).slice(cursor, match.index)));
      const value = match[0];
      const link = value.match(/^\[([^\]]+)\]\(([^)]+)\)$/);
      if (link) {
        const destination = link[2].trim();
        const anchor = document.createElement('a');
        anchor.textContent = link[1];
        if (destination.startsWith('task:')) {
          const id = destination.slice(5);
          anchor.href = `/student/tasks/${encodeURIComponent(id)}`;
          anchor.dataset.taskLink = id;
        } else if (destination.startsWith('lesson:')) {
          const id = destination.slice(7);
          anchor.href = `/student?view=theory&lesson=${encodeURIComponent(id)}`;
          anchor.dataset.lessonLink = id;
        } else if (/^https?:\/\//i.test(destination)) {
          anchor.href = destination;
          anchor.target = '_blank';
          anchor.rel = 'noopener noreferrer';
        } else {
          target.append(document.createTextNode(value));
          cursor = match.index + value.length;
          continue;
        }
        target.append(anchor);
      } else if (value.startsWith('`')) {
        const code = document.createElement('code');
        code.textContent = value.slice(1, -1);
        target.append(code);
      } else if (value.startsWith('**') || value.startsWith('__')) {
        const strong = document.createElement('strong');
        appendInline(value.slice(2, -2), strong);
        target.append(strong);
      } else {
        const emphasis = document.createElement('em');
        appendInline(value.slice(1, -1), emphasis);
        target.append(emphasis);
      }
      cursor = match.index + value.length;
    }
    target.append(document.createTextNode(String(source).slice(cursor)));
  }

  function isSpecial(line) {
    return /^\s*```/.test(line) || /^\s{0,3}#{1,6}\s/.test(line) || /^\s*>/.test(line)
      || /^\s*[-*+]\s+/.test(line) || /^\s*\d+[.)]\s+/.test(line)
      || /^\s*<\/?details(?:\s[^>]*)?>/i.test(line) || /^\s*<summary>/i.test(line);
  }

  function tableCells(line) {
    const trimmed = line.trim().replace(/^\|/, '').replace(/\|$/, '');
    return trimmed.split('|').map((cell) => cell.trim());
  }

  function renderBlocks(lines, target, start = 0, stopAtDetails = false) {
    let i = start;
    while (i < lines.length) {
      const line = lines[i];
      if (!line.trim()) { i++; continue; }
      if (/^\s*<\/details>/i.test(line)) {
        if (stopAtDetails) return i + 1;
        i++;
        continue;
      }
      if (/^\s*<summary>/i.test(line)) {
        const match = line.match(/<summary>(.*?)<\/summary>/i);
        if (match) {
          const summary = document.createElement('summary');
          appendInline(match[1], summary);
          target.append(summary);
        }
        i++;
        continue;
      }
      const detailsMatch = line.match(/^\s*<details(?:\s[^>]*)?>/i);
      if (detailsMatch) {
        const details = document.createElement('details');
        const summaryMatch = line.match(/<summary>(.*?)<\/summary>/i);
        if (summaryMatch) {
          const summary = document.createElement('summary');
          appendInline(summaryMatch[1], summary);
          details.append(summary);
        }
        i = renderBlocks(lines, details, i + 1, true);
        target.append(details);
        continue;
      }
      if (/^\s*```/.test(line)) {
        const indent = (line.match(/^\s*/) || [''])[0].length;
        i++;
        const code = [];
        while (i < lines.length && !/^\s*```/.test(lines[i])) {
          const sourceLine = lines[i++];
          code.push(sourceLine.slice(Math.min(indent, (sourceLine.match(/^\s*/) || [''])[0].length)));
        }
        if (i < lines.length) i++;
        const pre = document.createElement('pre');
        const codeElement = document.createElement('code');
        codeElement.textContent = code.join('\n');
        pre.append(codeElement);
        target.append(pre);
        continue;
      }
      const heading = line.match(/^\s{0,3}(#{1,6})\s+(.+)$/);
      if (heading) {
        const element = document.createElement(`h${heading[1].length}`);
        appendInline(heading[2], element);
        target.append(element);
        i++;
        continue;
      }
      if (/^\s*>/.test(line)) {
        const quote = document.createElement('blockquote');
        const parts = [];
        while (i < lines.length && /^\s*>/.test(lines[i])) parts.push(lines[i++].replace(/^\s*>\s?/, ''));
        appendInline(parts.join(' '), quote);
        target.append(quote);
        continue;
      }
      if (i + 1 < lines.length && line.includes('|') && /^\s*\|?\s*:?-{3,}/.test(lines[i + 1])) {
        const wrap = document.createElement('div');
        wrap.className = 'table-wrap';
        const table = document.createElement('table');
        const head = document.createElement('thead');
        const headRow = document.createElement('tr');
        for (const cell of tableCells(line)) {
          const th = document.createElement('th');
          th.scope = 'col';
          appendInline(cell, th);
          headRow.append(th);
        }
        head.append(headRow);
        const body = document.createElement('tbody');
        i += 2;
        while (i < lines.length && lines[i].trim() && lines[i].includes('|')) {
          const row = document.createElement('tr');
          for (const cell of tableCells(lines[i++])) {
            const td = document.createElement('td');
            appendInline(cell, td);
            row.append(td);
          }
          body.append(row);
        }
        table.append(head, body);
        wrap.append(table);
        target.append(wrap);
        continue;
      }
      if (/^\s*[-*+]\s+/.test(line) || /^\s*\d+[.)]\s+/.test(line)) {
        const ordered = /^\s*\d+[.)]\s+/.test(line);
        const list = document.createElement(ordered ? 'ol' : 'ul');
        const pattern = ordered ? /^\s*\d+[.)]\s+/ : /^\s*[-*+]\s+/;
        while (i < lines.length && pattern.test(lines[i])) {
          const item = document.createElement('li');
          appendInline(lines[i++].replace(pattern, ''), item);
          list.append(item);
        }
        target.append(list);
        continue;
      }
      const paragraph = document.createElement('p');
      const parts = [];
      while (i < lines.length && lines[i].trim() && !isSpecial(lines[i])) {
        if (i + 1 < lines.length && lines[i].includes('|') && /^\s*\|?\s*:?-{3,}/.test(lines[i + 1])) break;
        parts.push(lines[i++].trim());
      }
      if (!parts.length) { i++; continue; }
      appendInline(parts.join(' '), paragraph);
      target.append(paragraph);
    }
    return i;
  }

  function render(source, target) {
    const fragment = document.createDocumentFragment();
    const container = document.createElement('div');
    const lines = String(source || '').replace(/\r/g, '').split('\n');
    renderBlocks(lines, container);
    while (container.firstChild) fragment.append(container.firstChild);
    target.replaceChildren(fragment);
    target.classList.add('markdown');
  }

  root.StudentMarkdown = { render, appendInline };
})(typeof globalThis !== 'undefined' ? globalThis : window);
