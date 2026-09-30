import { getBaseUrl, getToken, setToken, type StudioCandidateBody } from './api';

export interface ConsoleConfig {
  service_name: string; registration_enabled: boolean; session_minutes: number;
  check_timeout_seconds: number; max_code_chars: number; content_path: string;
  ai_enabled: boolean; ai_base_url: string; ai_model: string; ai_temperature: number | null;
  ai_max_tokens: number; ai_timeout_seconds: number; ai_tools_enabled: boolean;
  ai_token_limit_parameter: 'max_tokens' | 'max_completion_tokens'; ai_system_prompt: string;
}
export interface SettingsSnapshot {
  revision: number; config: ConsoleConfig; api_key_configured: boolean; api_key_error: string;
  locked_fields: Record<string, string>; updated_at: string | null;
  runtime: { version: string; environment: string; db_path: string; bind_host: string;
    bind_port: number; workers: number; allowed_hosts: string[]; cors_origins: string[];
    jwt_secret_configured: boolean; };
}
export interface SettingsDraft { expected_revision: number; config: ConsoleConfig; changes?: Record<string, unknown>; }
export interface TaskDraft extends StudioCandidateBody { task_id: string; }
export interface ChatSession { id: string; title: string; created_at: string; updated_at: string; }
export interface ChatProposal { id: string; title: string; kind: 'settings' | 'task'; payload: SettingsDraft | TaskDraft; }
export interface ChatMessage { id: string; role: 'user' | 'assistant'; content: string; status: string;
  created_at: string; proposals: ChatProposal[]; }
export interface ChatData { session: ChatSession; messages: ChatMessage[]; }

async function response(method: string, path: string, body?: unknown, signal?: AbortSignal) {
  const token = getToken();
  const res = await fetch(getBaseUrl() + '/admin' + path, {
    method, signal, headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}) },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  if (res.status === 401) {
    setToken(null); window.dispatchEvent(new CustomEvent('ego:session-expired'));
    throw new Error('Сессия истекла. Войди снова, чтобы продолжить.');
  }
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    const detail = typeof data.detail === 'string' ? data.detail : Array.isArray(data.detail)
      ? data.detail.map((e: { msg: string }) => e.msg).join('; ') : `HTTP ${res.status}`;
    throw Object.assign(new Error(detail), { status: res.status });
  }
  return res;
}
async function json<T>(method: string, path: string, body?: unknown): Promise<T> {
  const res = await response(method, path, body);
  return res.status === 204 ? undefined as T : await res.json() as T;
}
export const getSettings = () => json<SettingsSnapshot>('GET', '/settings');
export const saveSettings = (draft: SettingsDraft, api_key?: string, clear_api_key = false) =>
  json<SettingsSnapshot>('PUT', '/settings', { ...draft, changes: undefined, api_key, clear_api_key });
export const testAI = () => json<{ ok: boolean; model: string; latency_ms: number; answer: string }>('POST', '/settings/ai/test');
export const listModels = () => json<string[]>('GET', '/settings/ai/models');
export const exportDeployment = async () => (await response('GET', '/settings/deployment')).text();
export const syncContent = (path: string) => json<{ added: number; updated: number; skipped: number; errors: number; status: string }>('POST', '/sync-tasks', { path, source: 'manual' });
export const syncLog = () => json<Array<{ id: number; status: string; finished_at: string; errors: number; error_details: string }>>('GET', '/sync/log');
export const listChats = () => json<ChatSession[]>('GET', '/assistant/sessions');
export const newChat = () => json<ChatSession>('POST', '/assistant/sessions', { title: 'Новый чат' });
export const readChat = (id: string) => json<ChatData>('GET', `/assistant/sessions/${encodeURIComponent(id)}`);
export const deleteChat = (id: string) => json<void>('DELETE', `/assistant/sessions/${encodeURIComponent(id)}`);

export async function streamChat(id: string, content: string, task_id: string | undefined,
  signal: AbortSignal, event: (kind: string, data: Record<string, unknown>) => void): Promise<void> {
  const res = await response('POST', `/assistant/sessions/${encodeURIComponent(id)}/messages`, { content, task_id }, signal);
  if (!res.body) throw new Error('Браузер не поддерживает потоковые ответы.');
  const reader = res.body.getReader(); const decoder = new TextDecoder(); let buffer = '';
  try {
    while (true) {
      const { value, done } = await reader.read();
      buffer += decoder.decode(value, { stream: !done });
      let end: number;
      while ((end = buffer.indexOf('\n\n')) >= 0) {
        const frame = buffer.slice(0, end); buffer = buffer.slice(end + 2);
        const kind = frame.split('\n').find((line) => line.startsWith('event:'))?.slice(6).trim() || 'message';
        const data = frame.split('\n').filter((line) => line.startsWith('data:')).map((line) => line.slice(5).trim()).join('\n');
        if (data) event(kind, JSON.parse(data));
      }
      if (done) break;
    }
  } finally { reader.releaseLock(); }
}
