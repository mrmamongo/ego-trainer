/** Decide whether `ego.login` may reuse the current stored session.
 *
 * The check runs GET /auth/me before the browser flow: a valid token keeps
 * the user signed in, an expired one is dropped, and an unreachable server
 * must never open a login window or forget the token.
 */

export type AuthMeResult = 'ok' | 'unauthorized' | 'unreachable';
export type AuthStart = 'already' | 'login' | 'unreachable';

export interface AuthStartInput {
    hasToken: boolean;
    meResult: AuthMeResult;
}

/** Map the stored token and the /auth/me outcome to the next login step. */
export function decideAuthStart({ hasToken, meResult }: AuthStartInput): AuthStart {
    if (!hasToken || meResult === 'unauthorized') return 'login';
    return meResult === 'ok' ? 'already' : 'unreachable';
}

/** Classify an /auth/me failure: HTTP 401/403 means the token is dead. */
export function classifyAuthStatus(status: number): AuthMeResult {
    return status === 401 || status === 403 ? 'unauthorized' : 'unreachable';
}
