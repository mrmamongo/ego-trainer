import assert from 'node:assert/strict';
import test from 'node:test';
import { readStudentRoute, studentTaskUrl, studentCatalogUrl, isPlainNavigation } from '../../ego_server/static/student-navigation.js';

test('task links round-trip catalog identifiers and selected tabs', () => {
  for (const id of ['F2', 'course/task one', 'Ветка #1?', 'percent%2F']) {
    const route = readStudentRoute(new URL(studentTaskUrl(id, 'help'), 'https://cogito.test'));
    assert.equal(route.taskId, id);
    assert.equal(route.tab, 'help');
  }
});

test('malformed identifiers cannot become a catalog route', () => {
  const route = readStudentRoute({ pathname: '/student/tasks/%E0%A4%A', search: '?tab=unknown' });
  assert.equal(route.taskId, '');
  assert.equal(route.tab, 'statement');
});

test('catalog filters survive a link round-trip without task tab parameters', () => {
  const filters = { q: 'список & словарь', block: 'XL-A', status: 'defense' };
  const route = readStudentRoute(new URL(studentCatalogUrl(filters), 'https://cogito.test'));
  assert.equal(route.taskId, null);
  assert.deepEqual(route.filters, filters);
  assert.equal(studentCatalogUrl(), '/student');
  assert.equal(readStudentRoute({ pathname: '/student', search: '?status=unknown' }).filters.status, '');
});

test('modified clicks retain native new-tab and browser navigation', () => {
  assert.equal(isPlainNavigation({ button: 0 }), true);
  for (const event of [{ button: 1 }, { button: 0, ctrlKey: true }, { button: 0, metaKey: true }, { button: 0, shiftKey: true }, { button: 0, altKey: true }]) {
    assert.equal(isPlainNavigation(event), false);
  }
});
