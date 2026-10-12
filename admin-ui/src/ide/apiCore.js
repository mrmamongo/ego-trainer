/**
 * Plain-JS core of the IDE API client for ego-server.
 *
 * No TypeScript and no DOM assumptions: every environment dependency
 * (base URL, token storage, fetch, event target) is injected through
 * `createIdeApi`, so the full network contract is unit-testable in Node.
 * `api.ts` re-exports this factory behind typed signatures for app code.
 */

/** localStorage key for the IDE JWT (separate from the admin token). */
export const IDE_TOKEN_KEY = 'ego_ide_token';

/** Window event dispatched when a request comes back with 401. */
export const IDE_SESSION_EXPIRED_EVENT = 'ego:ide-session-expired';

/**
 * Build an IDE API client bound to the given environment.
 *
 * @param {string} baseUrl server origin, e.g. window.location.origin
 * @param {Storage} storage token storage, e.g. window.localStorage
 * @param {typeof fetch} fetchFn fetch implementation to use for requests
 * @param {{ dispatchEvent?: (event: Event) => unknown } | null} [eventTarget]
 *   target for the session-expired event, e.g. window (null skips dispatch)
 * @returns {object} { setToken, getToken, clearToken, request, login, me,
 *   listTasks, getTask, check }
 */
export function createIdeApi(baseUrl, storage, fetchFn, eventTarget = null) {
  let currentToken = null;

  function setToken(token) {
    currentToken = token || null;
    if (token) storage.setItem(IDE_TOKEN_KEY, token);
    else storage.removeItem(IDE_TOKEN_KEY);
  }

  function getToken() {
    return currentToken || storage.getItem(IDE_TOKEN_KEY);
  }

  function clearToken() {
    setToken(null);
  }

  async function extractDetail(resp) {
    const data = await resp.json().catch(() => ({}));
    if (typeof data.detail === 'string') return data.detail;
    if (Array.isArray(data.detail)) {
      return data.detail.map((e) => e?.msg || 'Invalid field').join('; ');
    }
    return null;
  }

  async function request(method, path, body) {
    const token = getToken();
    const headers = { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const resp = await fetchFn(`${baseUrl}${path}`, {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined,
    });

    if (resp.status === 401) {
      clearToken();
      if (eventTarget) {
        eventTarget.dispatchEvent(new CustomEvent(IDE_SESSION_EXPIRED_EVENT));
      }
      const detail = await extractDetail(resp);
      throw new Error(detail || 'Session expired. Please log in again.');
    }
    if (!resp.ok) {
      const detail = await extractDetail(resp);
      throw new Error(detail || `HTTP ${resp.status}`);
    }
    if (resp.status === 204) return undefined;
    return await resp.json().catch(() => ({}));
  }

  return {
    setToken,
    getToken,
    clearToken,
    request,

    /** GET /auth/providers — which login methods the server offers. */
    authProviders() {
      return request('GET', '/auth/providers');
    },

    /** POST /auth/login {username, password} — stores the access token. */
    async login(username, password) {
      const res = await request('POST', '/auth/login', { username, password });
      if (res && res.access_token) setToken(res.access_token);
      return res;
    },

    /** POST /auth/forgejo/start {client, code_challenge} — begin PKCE flow. */
    startForgejo(codeChallenge) {
      return request('POST', '/auth/forgejo/start', {
        client: 'browser',
        code_challenge: codeChallenge,
      });
    },

    /**
     * POST /auth/forgejo/exchange {state, code_verifier, ticket} — finish the
     * PKCE flow; a `pending: true` result means registration approval is
     * still required, keep polling with the same triplet.
     */
    async exchangeForgejo(state, codeVerifier, ticket) {
      const res = await request('POST', '/auth/forgejo/exchange', {
        state,
        code_verifier: codeVerifier,
        ticket,
      });
      if (res && res.access_token) setToken(res.access_token);
      return res;
    },

    /** GET /auth/me */
    me() {
      return request('GET', '/auth/me');
    },

    /** GET /tasks */
    listTasks() {
      return request('GET', '/tasks');
    },

    /** GET /tasks/{task_id} */
    getTask(taskId) {
      return request('GET', `/tasks/${encodeURIComponent(taskId)}`);
    },

    /** POST /check {task_id, student_code} */
    check(taskId, studentCode) {
      return request('POST', '/check', { task_id: taskId, student_code: studentCode });
    },
  };
}
