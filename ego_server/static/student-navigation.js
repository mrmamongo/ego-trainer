export const taskTabs = ['statement', 'code', 'help', 'defense'];
const statuses = ['new', 'started', 'passed', 'defense'];

export function readStudentRoute({ pathname, search = '' }) {
  const params = new URLSearchParams(search);
  const prefix = '/student/tasks/';
  let taskId = null;
  if (pathname.startsWith(prefix)) {
    try { taskId = decodeURIComponent(pathname.slice(prefix.length)); }
    catch { taskId = ''; }
  }
  return {
    taskId,
    tab: taskTabs.includes(params.get('tab')) ? params.get('tab') : 'statement',
    filters: {
      q: params.get('q') || '', block: params.get('block') || '',
      status: statuses.includes(params.get('status')) ? params.get('status') : ''
    }
  };
}

export function studentTaskUrl(id, tab = 'statement') {
  const path = `/student/tasks/${encodeURIComponent(id)}`;
  return taskTabs.includes(tab) && tab !== 'statement' ? `${path}?tab=${tab}` : path;
}

export function studentCatalogUrl(filters = {}) {
  const params = new URLSearchParams();
  for (const key of ['q', 'block', 'status']) {
    if (typeof filters[key] === 'string' && filters[key]) params.set(key, filters[key]);
  }
  return '/student' + (params.size ? `?${params}` : '');
}

export function isPlainNavigation(event) {
  return event.button === 0 && !event.ctrlKey && !event.metaKey && !event.shiftKey && !event.altKey;
}
