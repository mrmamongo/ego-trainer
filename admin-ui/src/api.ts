/** API client for ego-server admin endpoints. */

export interface StudentSummary {
	student_id: string;
	username: string;
	role: string;
	tasks_total: number;
	tasks_passed: number;
	tasks_partial: number;
	tasks_failed: number;
	last_activity: string | null;
}

export interface ProgressRow {
	student_id: string;
	task_id: string;
	version: string;
	status: string;
	attempts: number;
	passed_tests: number;
	total_tests: number;
	last_run_at: string;
}

export interface AuthResponse {
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

// === Overview / Catalog (GET /admin/overview, GET /admin/catalog) ===

export interface SyncLogRow {
	id: number;
	started_at: string;
	finished_at: string | null;
	source: string;
	repo_url: string;
	git_sha: string | null;
	status: string;
	added: number;
	updated: number;
	skipped: number;
	errors: number;
	error_details: string;
}

export interface OverviewCounts {
	projects: number;
	folders: number;
	tasks: number;
	students: number;
}

export interface OverviewDTO {
	server: string;
	counts: OverviewCounts;
	latest_sync: SyncLogRow | null;
}

export interface CatalogTaskDTO {
	id: string;
	task_id: string;
	title: string;
	block: string;
	slug: string;
	level: string;
	version: string;
	breaking: boolean;
	md_path: string;
	folder_id: string | null;
	project_id: string | null;
}

export interface CatalogFolderDTO {
	id: string;
	project_id: string;
	code: string;
	name: string;
	order: number;
	level: string | null;
	tasks: CatalogTaskDTO[];
}

export interface CatalogProjectDTO {
	id: string;
	name: string;
	order: number;
	version: string;
	folders: CatalogFolderDTO[];
}

export interface CatalogDTO {
	projects: CatalogProjectDTO[];
}

let _token: string | null = null;

export function setToken(token: string | null): void {
	_token = token;
	if (token) localStorage.setItem('ego_admin_token', token);
	else localStorage.removeItem('ego_admin_token');
}

export function getToken(): string | null {
	return _token || localStorage.getItem('ego_admin_token');
}

export function getBaseUrl(): string {
	return window.location.origin;
}

async function request<T>(method: string, path: string, body?: unknown): Promise<T> {
	const token = getToken();
	const headers: Record<string, string> = { 'Content-Type': 'application/json' };
	if (token) headers['Authorization'] = `Bearer ${token}`;

	const resp = await fetch(`${getBaseUrl()}${path}`, {
		method,
		headers,
		body: body ? JSON.stringify(body) : undefined,
	});

	if (resp.status === 401) {
		setToken(null);
		window.dispatchEvent(new CustomEvent('ego:session-expired'));
		throw new Error('Session expired. Please log in again.');
	}
	if (!resp.ok) {
		const data = await resp.json().catch(() => ({}));
		const detail = typeof data.detail === 'string' ? data.detail
			: Array.isArray(data.detail) ? data.detail.map((e: { msg?: string }) => e.msg || 'Invalid field').join('; ')
			: `HTTP ${resp.status}`;
		throw new Error(detail);
	}
	if (resp.status === 204) {
		return undefined as T;
	}
	const data = await resp.json().catch(() => ({}));
	return data as T;
}

// === Auth ===

export interface AuthProviders { forgejo: boolean; local: boolean }
export interface ForgejoFlow { state: string; authorization_url: string; expires_in: number }

export async function authProviders(): Promise<AuthProviders> {
	return request<AuthProviders>('GET', '/auth/providers');
}

export async function startForgejo(code_challenge: string): Promise<ForgejoFlow> {
	return request<ForgejoFlow>('POST', '/auth/forgejo/start', { code_challenge });
}

export async function exchangeForgejo(state: string, code_verifier: string, ticket: string): Promise<AuthResponse | { pending: true }> {
	return request('POST', '/auth/forgejo/exchange', { state, code_verifier, ticket });
}

export async function me(): Promise<MeResponse> {
	return request<MeResponse>('GET', '/auth/me');
}

export async function login(username: string, password: string): Promise<AuthResponse> {
	return request<AuthResponse>('POST', '/auth/login', { username, password });
}

// === Students ===

export async function listStudents(): Promise<StudentSummary[]> {
	return request<StudentSummary[]>('GET', '/admin/students');
}

export async function getStudentProgress(studentId: string): Promise<ProgressRow[]> {
	return request<ProgressRow[]>('GET', `/progress/${studentId}`);
}

export async function createUser(username: string, password: string, role: string): Promise<unknown> {
	return request<unknown>('POST', '/admin/users', { username, password, role });
}

export async function updateRole(userId: string, role: string): Promise<unknown> {
	return request<unknown>('PUT', `/admin/users/${userId}/role`, { role });
}

export async function resetPassword(userId: string, password: string): Promise<unknown> {
	return request<unknown>('PUT', `/admin/users/${userId}/password`, { password });
}

export async function deleteUser(userId: string): Promise<void> {
	return request<void>('DELETE', `/admin/users/${userId}`);
}

// === Overview & Catalog ===

export async function getOverview(): Promise<OverviewDTO> {
	return request<OverviewDTO>('GET', '/admin/overview');
}

export async function getCatalog(q?: string): Promise<CatalogDTO> {
	const needle = (q ?? '').trim();
	const path = needle ? `/admin/catalog?q=${encodeURIComponent(needle)}` : '/admin/catalog';
	return request<CatalogDTO>('GET', path);
}

// === Task Studio (GET / PUT / POST /admin/tasks/{id}/studio) ===

export interface SyncResultDTO {
	log_id: number;
	status: string; // success | partial | failed
	added: number;
	updated: number;
	skipped: number;
	errors: number;
	error_details: string;
	started_at: string;
	finished_at: string;
	git_sha: string | null;
	repo_url: string;
}

export interface TaskStudioDTO {
	task_id: string;
	version: string;
	md_path: string;
	markdown: string;
	solution_py: string;
	tests_py: string;
	content_etag: string;
	version_policy: string | null;
	writable: boolean;
	read_only_reason: string;
}

export interface StudioCandidateBody {
	expected_version: string;
	expected_content_etag: string;
	markdown: string; // full .md including YAML frontmatter
	solution_py: string;
	tests_py: string;
}

export interface StudioValidateResponse {
	valid: boolean;
	task_id: string;
	current_version: string;
	candidate_version: string;
	content_changed: boolean;
	version_policy: string;
}

export interface StudioSaveResponse {
	task_id: string;
	new_version: string;
	content_etag: string;
	sync: SyncResultDTO;
}

export async function getTaskStudio(taskId: string): Promise<TaskStudioDTO> {
	return request<TaskStudioDTO>('GET', `/admin/tasks/${encodeURIComponent(taskId)}/studio`);
}

export async function validateTaskStudio(
	taskId: string,
	body: StudioCandidateBody,
): Promise<StudioValidateResponse> {
	return request<StudioValidateResponse>(
		'POST',
		`/admin/tasks/${encodeURIComponent(taskId)}/studio/validate`,
		body,
	);
}

export async function saveTaskStudio(
	taskId: string,
	body: StudioCandidateBody,
): Promise<StudioSaveResponse> {
	return request<StudioSaveResponse>(
		'PUT',
		`/admin/tasks/${encodeURIComponent(taskId)}/studio`,
		body,
	);
}

export interface AIAccount {
    enabled: boolean; defense_required: boolean; available: boolean; reason: string;
    balance_usd: string; reserved_usd: string; spent_usd: string;
}
export interface AIUsage {
    id: number; purpose: string; model: string; input_tokens: number; output_tokens: number;
    estimated: boolean; cost_usd: string; outcome: string;
}
export interface AISubmission {
    id: string; task_id: string; version: string; understanding: string;
    evidence: { stage: string; quote: string }[];
}
export interface AIModelConfig {
    base_url: string; model: string; api_key_set?: boolean; api_key?: string;
    input_usd_per_million: number | string; output_usd_per_million: number | string;
    max_output_tokens: number; json_mode: boolean;
}
export interface AIConfig {
    enabled: boolean; main: AIModelConfig; guard: AIModelConfig;
    timeout_seconds: number; max_context_bytes: number; max_reply_bytes: number; max_turns: number;
}
export function getAISettings(): Promise<AIConfig> { return request('GET', '/admin/ai/settings'); }
export function saveAISettings(config: AIConfig): Promise<AIConfig> { return request('PUT', '/admin/ai/settings', config); }
export function getAIAccount(id: string): Promise<AIAccount> { return request('GET', `/admin/ai/students/${encodeURIComponent(id)}`); }
export function updateAIAccess(id: string, enabled: boolean, defense_required: boolean): Promise<AIAccount> {
    return request('PUT', `/admin/ai/students/${encodeURIComponent(id)}`, { enabled, defense_required });
}
export function creditAIAccount(id: string, amount_usd: number, request_id: string): Promise<AIAccount> {
    return request('POST', `/admin/ai/students/${encodeURIComponent(id)}/credits`, { amount_usd, request_id });
}
export function getAIUsage(id: string): Promise<AIUsage[]> { return request('GET', `/admin/ai/students/${encodeURIComponent(id)}/usage`); }
export function getAISubmissions(id: string): Promise<AISubmission[]> { return request('GET', `/admin/ai/students/${encodeURIComponent(id)}/submissions`); }
