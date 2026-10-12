import assert from 'node:assert/strict';
import test from 'node:test';

import {
  IDE_ROOM_PATH_PREFIX,
  IDE_TASK_PATH_PREFIX,
  readIdeRoute,
  ideRoomUrl,
  ideTaskUrl,
  findIdeFileForTask,
  findIdeTaskForId,
} from './route.js';

// --- readIdeRoute / ideRoomUrl -------------------------------------------------

test('room links round-trip opaque capability ids', () => {
  for (const id of ['abcdefghijklmnop', 'room_XYz012-9AbCdEfG', 'x']) {
    assert.equal(readIdeRoute({ pathname: ideRoomUrl(id) }).roomId, id);
  }
  assert.equal(IDE_ROOM_PATH_PREFIX, '/ide/room/');
});

test('room link yields roomId and no taskId', () => {
  const route = readIdeRoute({ pathname: '/ide/room/abcdefghijklmnop' });
  assert.equal(route.roomId, 'abcdefghijklmnop');
  assert.equal(route.taskId, null);
});

test('room link: trailing slash stripped, bare prefix null, malformed null', () => {
  assert.equal(readIdeRoute({ pathname: '/ide/room/abcdefghijklmnop/' }).roomId, 'abcdefghijklmnop');
  assert.equal(readIdeRoute({ pathname: '/ide/room/' }).roomId, null);
  assert.equal(readIdeRoute({ pathname: '/ide/room/%E0%A4%A' }).roomId, null);
});

// --- readIdeRoute / ideTaskUrl ------------------------------------------------

test('task links round-trip identifiers with spaces, unicode and query chars', () => {
  for (const id of ['F2', '1.5', 'course/task one', 'Ветка #1?']) {
    assert.equal(readIdeRoute({ pathname: ideTaskUrl(id) }).taskId, id);
  }
  assert.equal(IDE_TASK_PATH_PREFIX, '/ide/task/');
});

test('readIdeRoute accepts a real URL and ignores an unknown search', () => {
  const url = new URL(ideTaskUrl('F2') + '?tab=statement', 'https://cogito.test');
  assert.equal(readIdeRoute(url).taskId, 'F2');
});

test('paths outside the prefix yield no task id', () => {
  for (const pathname of ['/ide', '/ide/', '/student/tasks/F2', '/ide/tasks/F2', '/ide/task']) {
    assert.equal(readIdeRoute({ pathname }).taskId, null, pathname);
  }
});

test('trailing slash is stripped and a bare prefix yields null', () => {
  assert.equal(readIdeRoute({ pathname: '/ide/task/F2/' }).taskId, 'F2');
  assert.equal(readIdeRoute({ pathname: '/ide/task/' }).taskId, null);
  assert.equal(readIdeRoute({ pathname: '/ide/task' }).taskId, null);
});

test('malformed percent-encoding never throws', () => {
  assert.equal(readIdeRoute({ pathname: '/ide/task/%E0%A4%A' }).taskId, null);
  assert.equal(readIdeRoute({ pathname: '/ide/task/%' }).taskId, null);
});

// --- findIdeFileForTask -------------------------------------------------------

test('findIdeFileForTask returns the first bound file or null', () => {
  const files = [
    { id: 'f1', name: 'notes.py', task_id: null },
    { id: 'f2', name: 'F2_sum.py', task_id: 'F2' },
    { id: 'f3', name: 'F2_copy.py', task_id: 'F2' },
  ];
  assert.equal(findIdeFileForTask(files, 'F2'), files[1]);
  assert.equal(findIdeFileForTask(files, 'F9'), null);
  assert.equal(findIdeFileForTask([], 'F2'), null);
  assert.equal(findIdeFileForTask(undefined, 'F2'), null);
});

// --- findIdeTaskForId ---------------------------------------------------------

test('findIdeTaskForId matches task_id and falls back to the id field', () => {
  const tasks = [
    { id: 1, task_id: 'F1', title: 'Сумма' },
    { id: 2, task_id: 'F2', title: 'Ветка' },
  ];
  assert.equal(findIdeTaskForId(tasks, 'F2'), tasks[1]);
  // task_id missing → numeric id still resolvable from a deep link.
  assert.deepEqual(findIdeTaskForId([{ id: 7 }], '7'), { id: 7 });
  assert.equal(findIdeTaskForId([{ id: 'X1', task_id: 'other' }], 'X1').id, 'X1');
  assert.equal(findIdeTaskForId(tasks, 'nope'), null);
  assert.equal(findIdeTaskForId(null, 'F1'), null);
});
