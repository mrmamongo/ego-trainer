/* Browser port of vscode-ego/src/dashboardLogic.ts. Keep behavior in sync. */
(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.StudentLogic = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  const FALLBACK_PROJECT_NAME = 'Без проекта';
  const FALLBACK_FOLDER_NAME = 'Без папки';

  function normalizeStatus(status) {
    return (status ?? '').trim().toLowerCase();
  }

  function isPassedStatus(status) {
    return normalizeStatus(status) === 'passed';
  }

  function isFailedStatus(status) {
    const s = normalizeStatus(status);
    return s === 'failed' || s === 'error' || s === 'timeout';
  }

  function isStartedStatus(status) {
    const s = normalizeStatus(status);
    if (s === '' || s === 'new') return false;
    if (isPassedStatus(s) || isFailedStatus(s)) return false;
    return true;
  }

  function evidenceMatches(evidence, progress, task) {
    if (!evidence || !progress) return false;
    if (evidence.task_id !== task.id) return false;
    if (evidence.version !== progress.version || progress.version !== task.version) return false;
    if (!progress.solution_hash) return true;
    return evidence.solution_hash === progress.solution_hash;
  }

  function taskState(task, progress, evidence, defenseRequired) {
    if (!progress) return 'new';
    if (isPassedStatus(progress.status)) {
      if (!defenseRequired) return 'passed';
      return evidenceMatches(evidence, progress, task) && normalizeStatus(evidence?.understanding) === 'confirmed'
        ? 'passed'
        : 'defense';
    }
    if (isFailedStatus(progress.status)) return 'failed';
    if (isStartedStatus(progress.status)) return 'started';
    return 'new';
  }

  function newestEvidenceByTask(rows) {
    const byTask = new Map();
    for (const row of rows) {
      if (!row || typeof row.task_id !== 'string') continue;
      const seen = byTask.get(row.task_id);
      if (!seen || (row.created_at || '') > (seen.created_at || '')) byTask.set(row.task_id, row);
    }
    return byTask;
  }

  function effectiveDefenseRequired(accountDefenseRequired, evidenceAvailable) {
    return evidenceAvailable && accountDefenseRequired === true ? true : null;
  }

  function isOpenState(state) {
    return state !== 'passed';
  }

  function taskStateLabel(state) {
    switch (state) {
      case 'passed': return 'Решена';
      case 'defense': return 'Ждёт защиты понимания';
      case 'started': return 'В работе';
      case 'failed': return 'Есть ошибки';
      default: return 'Не начата';
    }
  }

  function understandingStatusLabel(status) {
    switch (normalizeStatus(status)) {
      case 'confirmed': return 'Понимание подтверждено';
      case 'pending':
      case 'active': return 'Защита идёт';
      case 'needs_review': return 'Нужна проверка наставника';
      default: return 'Ждёт защиты понимания';
    }
  }

  function aiAccessReasonLabel(reason) {
    const text = (reason ?? '').trim();
    switch (text.toLowerCase()) {
      case '':
      case 'available': return 'доступен';
      case 'disabled':
      case 'not_granted': return 'доступ не выдан — обратись к наставнику';
      case 'low_balance':
      case 'insufficient_funds':
      case 'no_funds':
      case 'budget_exhausted': return 'бюджет исчерпан';
      case 'not_configured': return 'не настроен на сервере';
      default: return text;
    }
  }

  function naturalCompare(a, b) {
    const ax = a.match(/(\d+|\D+)/g) ?? [];
    const bx = b.match(/(\d+|\D+)/g) ?? [];
    const n = Math.min(ax.length, bx.length);
    for (let i = 0; i < n; i++) {
      const pa = ax[i];
      const pb = bx[i];
      const numA = /^\d/.test(pa);
      const numB = /^\d/.test(pb);
      if (numA && numB) {
        const diff = Number(pa) - Number(pb);
        if (diff !== 0) return diff;
        if (pa.length !== pb.length) return pa.length - pb.length;
        continue;
      }
      if (numA !== numB) return numA ? -1 : 1;
      const cmp = pa.toLowerCase().localeCompare(pb.toLowerCase());
      if (cmp !== 0) return cmp;
      if (pa !== pb) return pa < pb ? -1 : 1;
    }
    if (ax.length !== bx.length) return ax.length - bx.length;
    return a === b ? 0 : a < b ? -1 : 1;
  }

  function orderOf(value) {
    const n = typeof value === 'string' && value.trim() !== '' ? Number(value) : value;
    return typeof n === 'number' && Number.isFinite(n) ? n : 0;
  }

  function compareCatalogOrder(a, b) {
    const byFolder = orderOf(a.folder_order) - orderOf(b.folder_order);
    if (byFolder !== 0) return byFolder;
    return naturalCompare(a.id, b.id);
  }

  function compareProjectOrder(a, b) {
    const byOrder = orderOf(a.project_order) - orderOf(b.project_order);
    if (byOrder !== 0) return byOrder;
    const byId = naturalCompare(a.project_id || a.block || '', b.project_id || b.block || '');
    if (byId !== 0) return byId;
    return compareCatalogOrder(a, b);
  }

  function pickNextTask(tasks, stateOf) {
    const ordered = [...tasks].sort((a, b) => compareProjectOrder(a, b) || compareCatalogOrder(a, b));
    return ordered.find((task) => isOpenState(stateOf(task)));
  }

  function catalogValue(value) {
    return typeof value === 'string' && value !== '' ? value : '';
  }

  function groupCatalog(tasks, visit) {
    const hasProjects = tasks.some((t) => catalogValue(t.project_id) !== '');
    const projects = [];
    const projectByKey = new Map();
    const folderByKey = new Map();

    for (const task of tasks) {
      const projectId = catalogValue(task.project_id);
      const projectKey = projectId ? `p:${projectId}` : hasProjects ? 'p:' : `b:${catalogValue(task.block)}`;
      let project = projectByKey.get(projectKey);
      if (!project) {
        const name = projectId
          ? catalogValue(task.project_name) || projectId
          : catalogValue(task.block) ? `Блок ${task.block}` : FALLBACK_PROJECT_NAME;
        project = { key: projectKey, id: projectId || null, name, order: orderOf(task.project_order), tasks: [], folders: [], passed: 0, total: 0 };
        projectByKey.set(projectKey, project);
        projects.push(project);
      }

      const folderId = catalogValue(task.folder_id);
      const folderKey = `${projectKey}|${folderId ? `f:${folderId}` : `b:${catalogValue(task.block)}`}`;
      let folder = folderByKey.get(folderKey);
      if (!folder) {
        const name = folderId
          ? catalogValue(task.folder_name) || folderId
          : catalogValue(task.block) ? `Блок ${task.block}` : FALLBACK_FOLDER_NAME;
        folder = { key: folderKey, id: folderId || null, name, order: orderOf(task.folder_order), tasks: [], passed: 0, total: 0 };
        folderByKey.set(folderKey, folder);
        project.folders.push(folder);
      }

      folder.tasks.push(task);
      folder.total++;
      project.tasks.push(task);
      project.total++;
    }

    for (const project of projects) {
      project.folders.sort(compareGroups);
      for (const folder of project.folders) {
        folder.tasks.sort(compareCatalogOrder);
        if (visit) for (const task of folder.tasks) visit(project, folder, task);
      }
      project.tasks.sort(compareCatalogOrder);
    }
    projects.sort(compareGroups);
    return { projects, hasProjects };
  }

  function compareGroups(a, b) {
    if (a.order !== b.order) return a.order - b.order;
    return naturalCompare(a.name, b.name);
  }

  function percent(passed, total) {
    if (!Number.isFinite(total) || total <= 0) return 0;
    return Math.round((Math.min(passed, total) / total) * 100);
  }

  // === Soft recommendations (GET /projects) ===

  // Exam-kind tags of the breakdown card (same order as the server).
  const KIND_TAGS = ['bug', 'modify', 'new'];
  const KIND_LABELS = { bug: 'Баги', modify: 'Доработки', new: 'Новое' };

  function countOf(value) {
    const n = Number(value);
    return Number.isFinite(n) && n > 0 ? Math.floor(n) : 0;
  }

  /** Project id → project row from GET /projects (tolerates a missing list). */
  function indexProjects(list) {
    const map = new Map();
    if (!Array.isArray(list)) return map;
    for (const item of list) {
      if (item && typeof item.id === 'string' && item.id) map.set(item.id, item);
    }
    return map;
  }

  /**
   * Projects whose recommendation is declared and not met yet, in catalog order.
   * `projects` is the raw GET /projects list; each row carries `name`.
   */
  function unmetRecommendations(projects) {
    if (!Array.isArray(projects)) return [];
    return projects
      .filter((p) => p && p.recommended_after && p.readiness && p.readiness.met === false)
      .sort((a, b) => orderOf(a.order) - orderOf(b.order) || naturalCompare(String(a.id), String(b.id)));
  }

  /**
   * Readiness line under a project heading, e.g. «рекомендуем после XL-A: 14/21».
   * Null when the project has no recommendation or it is already met.
   * A missing count renders as «?» (old server: no readiness in GET /projects);
   * the optional per-kind part is shown only when the server counted the kinds.
   */
  function readinessLine(project, nameOf) {
    const rec = project && project.recommended_after;
    const readiness = project && project.readiness;
    if (!rec || !readiness || readiness.met) return null;
    const name = (typeof nameOf === 'function' && nameOf(rec.project)) || rec.project;
    const passed = Number.isFinite(Number(readiness.passed)) ? countOf(readiness.passed) : '?';
    const required = Number.isFinite(Number(readiness.required)) ? countOf(readiness.required) : '?';
    let line = `рекомендуем после ${name}: ${passed}/${required}`;
    if (rec.min_per_kind !== null && rec.min_per_kind !== undefined && hasPerKind(readiness.per_kind)) {
      const need = countOf(rec.min_per_kind);
      const parts = KIND_TAGS.map((kind) => {
        const got = countOf(readiness.per_kind[kind]);
        return `${got}/${need} ${(KIND_LABELS[kind] || kind).toLocaleLowerCase('ru')}`;
      });
      line += ` · ${parts.join(', ')}`;
    }
    return line;
  }

  function hasPerKind(perKind) {
    return Boolean(perKind) && KIND_TAGS.some((kind) => Object.prototype.hasOwnProperty.call(perKind, kind));
  }

  /** Rows of the XL-A style breakdown card: [{key, label, passed, total, percent}]. */
  function breakdownRows(breakdown) {
    const kinds = (breakdown && breakdown.kinds) || {};
    return KIND_TAGS.map((kind) => {
      const bucket = kinds[kind] || {};
      const passed = countOf(bucket.passed);
      const total = Math.max(countOf(bucket.total), passed);
      return { key: kind, label: KIND_LABELS[kind] || kind, passed, total, percent: percent(passed, total) };
    });
  }

  /** True when a breakdown response has at least one kind task. */
  function hasBreakdown(breakdown) {
    return breakdownRows(breakdown).some((row) => row.total > 0);
  }

  /**
   * Tooltip of a task link: the recommendation of the task's project, when
   * declared. Met → just the note; unmet → the readiness line plus the note.
   * Null when the project has no recommendation (or a note-less met one).
   */
  function recommendationHint(projectId, projects, readinessOf) {
    if (!projectId || !Array.isArray(projects)) return null;
    const row = projects.find((item) => item && item.id === projectId);
    const rec = row && row.recommended_after;
    if (!rec) return null;
    const note = (rec.note || '').trim();
    const line = typeof readinessOf === 'function' ? readinessOf(row) : null;
    if (!line) return note ? `Открыть задачу. Рекомендация «${note}».` : null;
    const quoted = note ? (/([.!?…])$/.test(note) ? ` ${note}` : ` ${note}.`) : '';
    return `Открыть задачу. Рекомендация: ${line}.${quoted} Это совет, а не ограничение.`;
  }

  return {
    normalizeStatus, isPassedStatus, taskState, newestEvidenceByTask,
    effectiveDefenseRequired, isOpenState, taskStateLabel, understandingStatusLabel,
    aiAccessReasonLabel, naturalCompare, compareCatalogOrder, compareProjectOrder,
    pickNextTask, groupCatalog, percent, KIND_TAGS, indexProjects,
    unmetRecommendations, readinessLine, breakdownRows, hasBreakdown, recommendationHint,
  };
});
