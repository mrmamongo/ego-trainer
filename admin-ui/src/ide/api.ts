/** Typed IDE API client for ego-server (student console). */

import {
	createIdeApi as createIdeApiCore,
	IDE_TOKEN_KEY,
	IDE_SESSION_EXPIRED_EVENT,
} from './apiCore.js';

// === DTOs (mirror ego_server/models.py) ===

export interface TaskMeta {
	id: string;
	block: string;
	slug: string;
	task_id: string;
	title: string;
	level: string;
	tags: string[];
	version: string;
	content_hash: string;
	breaking: boolean;
	md_path: string;
}

export interface TaskFull extends TaskMeta {
	statement_md: string;
	stub_py: string;
	solution_py: string;
}

export interface TestResult {
	description: string;
	passed: boolean;
	expected_repr: string;
	actual_repr: string | null;
	error: string | null;
}

export interface CheckResponse {
	task_id: string;
	version: string;
	status: string;
	passed_tests: number;
	total_tests: number;
	solution_hash: string;
	results: TestResult[];
	log: string;
	understanding: Record<string, unknown> | null;
}

export interface LoginResponse {
	access_token: string;
	token_type: string;
	role: string;
	username: string;
	user_id: string;
}

export interface MeResponse {
	user_id: string;
	username: string;
	role: string;
}

export interface AuthProviders {
	forgejo: boolean;
	local: boolean;
	registration: boolean;
}

export interface ForgejoFlow {
	state: string;
	authorization_url: string;
	expires_in: number;
}

export interface ForgejoExchangeResult extends Partial<LoginResponse> {
	pending?: boolean;
}

export interface ShareRoom {
	room_id: string;
	task_id: string;
	title: string;
	created_by: string;
	active: boolean;
}

// === Client ===

/** Typed view of the client returned by createIdeApi (runtime lives in apiCore.js). */
export interface IdeApi {
	setToken(token: string | null): void;
	getToken(): string | null;
	clearToken(): void;
	request<T>(method: string, path: string, body?: unknown): Promise<T>;
	authProviders(): Promise<AuthProviders>;
	login(username: string, password: string): Promise<LoginResponse>;
	startForgejo(codeChallenge: string): Promise<ForgejoFlow>;
	exchangeForgejo(state: string, codeVerifier: string, ticket: string): Promise<ForgejoExchangeResult>;
	me(): Promise<MeResponse>;
	listTasks(): Promise<TaskMeta[]>;
	getTask(taskId: string): Promise<TaskFull>;
	check(taskId: string, studentCode: string): Promise<CheckResponse>;
}

/**
 * Factory for the IDE API client. Every environment dependency is injectable,
 * so the network logic is unit-testable without a browser (see api.test.mjs);
 * runtime lives in apiCore.js, this is only the typed facade.
 */
export function createIdeApi(
	baseUrl: string,
	storage: Storage,
	fetchFn: typeof fetch,
	eventTarget?: { dispatchEvent(event: Event): unknown } | null,
): IdeApi {
	return createIdeApiCore(baseUrl, storage, fetchFn, eventTarget ?? null) as IdeApi;
}

let _browserApi: IdeApi | null = null;

/** Singleton bound to window/localStorage/fetch (lazily, for non-browser imports). */
function browserApi(): IdeApi {
	if (!_browserApi) {
		_browserApi = createIdeApiCore(
			window.location.origin,
			window.localStorage,
			fetch,
			window,
		) as IdeApi;
	}
	return _browserApi;
}

export { IDE_TOKEN_KEY, IDE_SESSION_EXPIRED_EVENT };

/** Store/clear the IDE JWT (persisted under `ego_ide_token`, separate from admin). */
export function setIdeToken(token: string | null): void {
	browserApi().setToken(token);
}

/** Read the IDE JWT from memory or localStorage. */
export function getIdeToken(): string | null {
	return browserApi().getToken();
}

/** Drop the IDE JWT from memory and localStorage. */
export function clearIdeToken(): void {
	browserApi().clearToken();
}

async function request<T>(method: string, path: string, body?: unknown): Promise<T> {
	return browserApi().request<T>(method, path, body);
}

// === Endpoints ===

/** GET /auth/providers — which login methods the server offers. */
export async function authProviders(): Promise<AuthProviders> {
	return request<AuthProviders>('GET', '/auth/providers');
}

/** POST /auth/login — also stores the returned access token for later calls. */
export async function ideLogin(username: string, password: string): Promise<LoginResponse> {
	return browserApi().login(username, password);
}

/** POST /auth/forgejo/start {client:'browser', code_challenge} — begin PKCE flow. */
export async function startForgejo(codeChallenge: string): Promise<ForgejoFlow> {
	return browserApi().startForgejo(codeChallenge);
}

/**
 * POST /auth/forgejo/exchange — finish the PKCE flow; stores the token on
 * success. A `{pending: true}` result means approval is still required.
 */
export async function exchangeForgejo(
	state: string,
	codeVerifier: string,
	ticket: string,
): Promise<ForgejoExchangeResult> {
	return browserApi().exchangeForgejo(state, codeVerifier, ticket);
}

/** GET /auth/me */
export async function ideMe(): Promise<MeResponse> {
	return request<MeResponse>('GET', '/auth/me');
}

/** GET /tasks */
export async function listTasks(): Promise<TaskMeta[]> {
	return request<TaskMeta[]>('GET', '/tasks');
}

/** GET /tasks/{task_id} */
export async function getTask(taskId: string): Promise<TaskFull> {
	return request<TaskFull>('GET', `/tasks/${encodeURIComponent(taskId)}`);
}

/** POST /check {task_id, student_code} */
export async function runCheck(taskId: string, studentCode: string): Promise<CheckResponse> {
	return request<CheckResponse>('POST', '/check', {
		task_id: taskId,
		student_code: studentCode,
	});
}

// === Collab share rooms (link-capability rooms) ===

/** POST /collab/share {task_id, title} — mentor/admin creates a share room. */
export async function createShareRoom(
	taskId: string,
	title = '',
): Promise<ShareRoom> {
	return request<ShareRoom>('POST', '/collab/share', { task_id: taskId, title });
}

/** GET /collab/share/{room_id} — check a deep-linked share room. */
export async function getShareRoom(roomId: string): Promise<ShareRoom> {
	return request<ShareRoom>('GET', `/collab/share/${encodeURIComponent(roomId)}`);
}

/** POST /collab/share/{room_id}/close — creator or admin closes the room. */
export async function closeShareRoom(roomId: string): Promise<{ ok: boolean }> {
	return request<{ ok: boolean }>(
		'POST',
		`/collab/share/${encodeURIComponent(roomId)}/close`,
	);
}
