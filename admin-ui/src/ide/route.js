/**
 * Deep-link route helpers for the /ide app (no DOM access).
 *
 * Two deep-link kinds:
 * - `/ide/room/<room_id>` — shared collab room (capability link): room_id is
 *   the opaque id from `collab_share_rooms` (see ego_server/collab.py).
 * - `/ide/task/<task_id>` — task deep link: opens/imports the task file.
 *
 * The server serves the same ide.html shell for all of them, so the client
 * parses `location` itself. Parsing is dependency-free and injectable
 * (`readIdeRoute({ pathname })`), mirroring the pure-helper style of
 * `ego_server/static/student-navigation.js`.
 *
 * @module ide/route
 */

/** Path prefix under which a shared-room deep link lives. */
export const IDE_ROOM_PATH_PREFIX = '/ide/room/';

/** Path prefix under which a task deep link lives. */
export const IDE_TASK_PATH_PREFIX = '/ide/task/';

/**
 * Extract the deep-link intent from a location-like object.
 *
 * Malformed percent-encoding never throws — the offending id becomes null.
 * A room link wins when both prefixes would match (they cannot overlap).
 *
 * @param {{pathname: string, search?: string}} locationLike
 * @returns {{roomId: string | null, taskId: string | null}}
 */
export function readIdeRoute(locationLike) {
  if (!locationLike || typeof locationLike.pathname !== 'string') {
    return { roomId: null, taskId: null };
  }
  const parse = (prefix) => {
    if (!locationLike.pathname.startsWith(prefix)) return null;
    let rest = locationLike.pathname.slice(prefix.length);
    if (rest.endsWith('/')) rest = rest.slice(0, -1);
    if (!rest) return null;
    try {
      return decodeURIComponent(rest);
    } catch {
      return null;
    }
  };
  const roomId = parse(IDE_ROOM_PATH_PREFIX);
  if (roomId) return { roomId, taskId: null };
  const taskId = parse(IDE_TASK_PATH_PREFIX);
  return { roomId: null, taskId };
}

/**
 * Build the deep-link path for a shared room id. Inverse of the room part:
 * `readIdeRoute({ pathname: ideRoomUrl(id) }).roomId === id`.
 *
 * @param {string} roomId
 * @returns {string}
 */
export function ideRoomUrl(roomId) {
  return IDE_ROOM_PATH_PREFIX + encodeURIComponent(roomId);
}

/**
 * Build the deep-link path for a task id. Inverse of the task part:
 * `readIdeRoute({ pathname: ideTaskUrl(id) }).taskId === id`.
 *
 * @param {string} taskId
 * @returns {string}
 */
export function ideTaskUrl(taskId) {
  return IDE_TASK_PATH_PREFIX + encodeURIComponent(taskId);
}

/**
 * First workspace file already bound to the task, else `null`.
 *
 * @param {Array<{id: string, name: string, task_id?: string | null}> | null | undefined} files
 * @param {string} taskId
 * @returns {{id: string, name: string, task_id?: string | null} | null}
 */
export function findIdeFileForTask(files, taskId) {
  if (!Array.isArray(files)) return null;
  return files.find((file) => file && file.task_id === taskId) ?? null;
}

/**
 * First catalog task matching the id (`task_id` field first, numeric/string
 * `id` field as fallback), else `null`.
 *
 * @param {Array<{id?: number | string, task_id?: string}> | null | undefined} tasks
 * @param {string} taskId
 * @returns {{id?: number | string, task_id?: string} | null}
 */
export function findIdeTaskForId(tasks, taskId) {
  if (!Array.isArray(tasks)) return null;
  return tasks.find((task) => task && task.task_id === taskId)
    ?? tasks.find((task) => task && task.id !== undefined && String(task.id) === taskId)
    ?? null;
}
