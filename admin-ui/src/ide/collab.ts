/**
 * Collaborative editing client for the /ide app (ADR-0017, P1).
 *
 * Server contract (ego_server/collab.py): WS endpoint
 * `${ws|wss}://<host>/collab/ws/<room>?token=<JWT>` where room is
 * `scenario:taskId:fileKey`; the IDE always uses `pair:<taskId>:<fileId>`
 * (taskId = task binding of the workspace file, fileId = workspace file uuid).
 * Transport is standard y-websocket (yjs sync protocol + awareness), so late
 * joiners receive the persisted snapshot through the regular sync step —
 * no REST snapshot call is needed in the client.
 *
 * The pure helpers (collabRoomFor, parseCollabRoom, buildPeers, mapStatus,
 * peerColorFor, collabServerUrl) are exported separately and unit-tested in
 * Node without any network (collab.test.mjs imports this very module — Node 22
 * strips TS types natively). To keep this file importable from Node, Monaco
 * appears only as `import type`, and y-monaco is loaded lazily inside
 * attachEditor: its static import would drag the whole Monaco tree (including
 * CSS) into the Node test run.
 */

import type * as monaco from 'monaco-editor/esm/vs/editor/editor.api';
import * as Y from 'yjs';
import { WebsocketProvider } from 'y-websocket';

// === Типы ===

export type CollabStatus = 'off' | 'connecting' | 'syncing' | 'live' | 'error';

export type Peer = {
	clientID: number;
	name: string;
	role: string;
	color: string;
	cursor: { line: number; column: number } | null;
};

/** Сценарии совместной работы из серверного контракта. */
export const COLLAB_SCENARIOS = ['studio', 'defense', 'pair'] as const;

export type CollabScenario = (typeof COLLAB_SCENARIOS)[number];

/** Сколько неудачных подключений подряд считаем истёкшей сессией. */
export const COLLAB_MAX_RETRIES = 3;

/** Код закрытия WS, которым сервер сообщает о невалидном/истёкшем токене. */
export const COLLAB_TOKEN_CLOSE_CODE = 1008;

/** Дебаунс доставки изменений текста (своих и удалённых) в onTextChange. */
export const COLLAB_TEXT_DEBOUNCE_MS = 400;

/** Палитра аватаров участников; цвет выбирается по хэшу имени. */
export const PEER_COLORS = [
	'#60a5fa',
	'#f472b6',
	'#34d399',
	'#fbbf24',
	'#a78bfa',
	'#fb7185',
	'#4ade80',
	'#38bdf8',
	'#f97316',
	'#2dd4bf',
] as const;

// === Чистые помощники (тестируются в Node без сети) ===

/** Детерминированный хэш строки (djb2-подобный, для выбора цвета). */
export function hashString(value: string): number {
	let hash = 0;
	for (let i = 0; i < value.length; i++) {
		hash = (hash * 31 + value.charCodeAt(i)) | 0;
	}
	return Math.abs(hash);
}

/** Цвет участника: стабилен для одного и того же имени. */
export function peerColorFor(name: string): string {
	return PEER_COLORS[hashString(name) % PEER_COLORS.length];
}

/** Имя комнаты парного редактирования файла, привязанного к задаче. */
export function collabRoomFor(taskId: string, fileId: string): string {
	return `pair:${taskId}:${fileId}`;
}

export type CollabRoom = { scenario: CollabScenario; taskId: string; fileKey: string };

/** Разбирает и валидирует имя комнаты по списку известных сценариев. */
export function parseCollabRoom(room: string): CollabRoom | null {
	const parts = room.split(':');
	if (parts.length !== 3) return null;
	const [scenario, taskId, fileKey] = parts;
	if (!(COLLAB_SCENARIOS as readonly string[]).includes(scenario)) return null;
	if (!taskId || !fileKey) return null;
	return { scenario: scenario as CollabScenario, taskId, fileKey };
}

/** Видимое имя для участника без корректного поля user в awareness. */
export function fallbackPeerName(clientID: number): string {
	return `Гость ${clientID}`;
}

/**
 * Базовый WS-адрес коллаба, выведенный из происхождения страницы
 * (https→wss, иначе ws). Провайдер сам добавит `/<room>?token=...`.
 */
export function collabServerUrl(locationLike?: { protocol: string; host: string }): string {
	const loc = locationLike ?? (typeof window !== 'undefined' ? window.location : undefined);
	if (!loc) return 'ws://localhost';
	return (loc.protocol === 'https:' ? 'wss' : 'ws') + '://' + loc.host;
}

/**
 * Собирает список участников из awareness-состояний, исключая себя.
 * Записи без поля user (например, успевшие положить только выделение от
 * y-monaco) получают запасное имя «Гость <id>» и цвет по хэшу имени.
 * Курсор в P1 не парсится: y-monaco кладёт относительные позиции в поле
 * selection, так что cursor всегда null.
 */
export function buildPeers(statesMap: Map<number, unknown>, selfId: number): Peer[] {
	const peers: Peer[] = [];
	statesMap.forEach((raw, clientID) => {
		if (clientID === selfId) return;
		const state = (raw ?? {}) as { user?: { name?: unknown; role?: unknown; color?: unknown } };
		const user = state.user;
		const name = typeof user?.name === 'string' && user.name.trim() ? user.name : fallbackPeerName(clientID);
		const role = typeof user?.role === 'string' ? user.role : '';
		const color = typeof user?.color === 'string' && user.color ? user.color : peerColorFor(name);
		peers.push({ clientID, name, role, color, cursor: null });
	});
	return peers.sort((a, b) => a.clientID - b.clientID);
}

/** Переводит статус y-websocket + флаг синхронизации в статус UI. */
export function mapStatus(wsStatus: string, synced: boolean): CollabStatus {
	if (wsStatus === 'connecting') return 'connecting';
	if (wsStatus === 'connected') return synced ? 'live' : 'syncing';
	if (wsStatus === 'disconnected') return 'error';
	return 'off';
}

// === Сессия ===

export type CollabSessionOpts = {
	room: string;
	getToken(): string | null;
	userName: string;
	userRole: string;
	onStatus(status: CollabStatus, detail?: string): void;
	onPeers(peers: Peer[]): void;
};

type PendingAttach = {
	editor: monaco.editor.IStandaloneCodeEditor;
	model: monaco.editor.ITextModel;
	initialText: string;
};

/**
 * Одна коллаб-сессия = одна комната = один файл задачи.
 * Провайдер пересоздаётся на каждый start(), потому что JWT мог обновиться.
 */
export class IdeCollabSession {
	readonly room: string;

	#opts: CollabSessionOpts;
	#doc: Y.Doc | null = null;
	#ytext: Y.Text | null = null;
	#provider: WebsocketProvider | null = null;
	#binding: { destroy(): void } | null = null;
	#attachedModel: monaco.editor.ITextModel | null = null;
	#pendingAttach: PendingAttach | null = null;
	#modelDispose: monaco.IDisposable | null = null;
	#bindingRequested = false;
	#synced = false;
	#stopped = false;
	#attachSeq = 0;
	#textTimer: ReturnType<typeof setTimeout> | undefined;
	#textListener: ((text: string) => void) | null = null;

	constructor(opts: CollabSessionOpts) {
		this.#opts = opts;
		this.room = opts.room;
	}

	start(): void {
		if (this.#stopped || this.#provider) return;
		const token = this.#opts.getToken();
		const doc = new Y.Doc();
		// connect: false — сначала подписки и awareness, потом само соединение.
		const provider = new WebsocketProvider(collabServerUrl(), this.room, doc, {
			connect: false,
			params: token ? { token } : {},
		});
		this.#doc = doc;
		this.#ytext = doc.getText('content');
		this.#provider = provider;
		provider.on('status', this.#onStatusEvent);
		// 'sync' — типизированная пара события 'synced' из y-websocket.
		provider.on('sync', this.#onSyncEvent);
		provider.on('connection-close', this.#onConnectionClose);
		provider.on('closed', this.#onClosed);
		provider.awareness.on('change', this.#onAwarenessChange);
		this.#ytext.observe(this.#onTextEvent);
		provider.awareness.setLocalStateField('user', {
			name: this.#opts.userName,
			role: this.#opts.userRole,
			color: peerColorFor(this.#opts.userName),
		});
		this.#emitStatus('connecting');
		provider.connect();
	}

	stop(): void {
		if (this.#stopped) return;
		this.#stopped = true;
		if (this.#textTimer) {
			clearTimeout(this.#textTimer);
			this.#textTimer = undefined;
		}
		this.#textListener = null;
		this.detachEditor();
		const provider = this.#provider;
		const doc = this.#doc;
		this.#provider = null;
		this.#doc = null;
		this.#ytext = null;
		// destroy() документа заодно останавливает таймеры awareness.
		if (provider) provider.destroy();
		if (doc) doc.destroy();
	}

	/**
	 * Привязывает Monaco-модель к общему тексту. Пока первая синхронизация
	 * не прошла, привязка откладывается: иначе сеяние локального текста в
	 * пустой Y.Doc склеилось бы с содержимым комнаты при синке. После синка:
	 * комната пуста → сеем текст модели; нет → комната главнее (late join).
	 */
	attachEditor(editor: monaco.editor.IStandaloneCodeEditor, model: monaco.editor.ITextModel, initialText: string): void {
		if (this.#stopped || !this.#provider || !this.#ytext || !this.#doc) return;
		if (this.#binding && this.#attachedModel === model) return; // уже привязан
		this.detachEditor();
		this.#pendingAttach = { editor, model, initialText };
		this.#modelDispose = model.onWillDispose(() => this.detachEditor());
		if (this.#synced) this.#bindPending();
	}

	detachEditor(): void {
		this.#attachSeq++; // отменяем отложенную привязку, если она в полёте
		this.#bindingRequested = false;
		this.#pendingAttach = null;
		if (this.#modelDispose) {
			this.#modelDispose.dispose();
			this.#modelDispose = null;
		}
		if (this.#binding) {
			this.#binding.destroy();
			this.#binding = null;
		}
		this.#attachedModel = null;
	}

	/** Привязан ли MonacoBinding: тогда источник истины по тексту — Y.Doc. */
	isAttached(): boolean {
		return !this.#stopped && this.#binding !== null;
	}

	getDocText(): string {
		return this.#ytext?.toString() ?? '';
	}

	/**
	 * Стартовый текст: вставляем только если Y.Doc пуст, а текст непуст.
	 * Если комната уже жива, её содержимое главнее — опоздавшие получают
	 * его обычным yjs-синком, и перезаписывать его нельзя.
	 */
	setDocText(text: string): void {
		const ytext = this.#ytext;
		const doc = this.#doc;
		if (!ytext || !doc) return;
		if (ytext.length === 0 && text.length > 0) {
			doc.transact(() => {
				ytext.insert(0, text);
			});
		}
	}

	/** Подписка на изменения текста (свои и удалённые), с дебаунсом 400 мс. */
	onTextChange(cb: (text: string) => void): void {
		this.#textListener = cb;
	}

	// --- внутреннее ---

	#emitStatus = (status: CollabStatus, detail?: string): void => {
		if (this.#stopped) return;
		this.#opts.onStatus(status, detail);
	};

	#onStatusEvent = (event: { status: string }): void => {
		if (this.#stopped) return;
		if (event.status === 'disconnected') this.#synced = false;
		const status = mapStatus(event.status, this.#synced);
		if (status === 'off') return;
		this.#emitStatus(status, status === 'error' ? 'Соединение потеряно' : undefined);
	};

	#onSyncEvent = (state: boolean): void => {
		if (this.#stopped || !state) return;
		this.#synced = true;
		this.#emitStatus('live');
		if (this.#pendingAttach && !this.#binding) this.#bindPending();
	};

	#onConnectionClose = (event: CloseEvent | null): void => {
		// event === null — соединение закрыли мы сами (stop/watchdog).
		if (this.#stopped || !event || !this.#provider) return;
		if (event.code === COLLAB_TOKEN_CLOSE_CODE) {
			this.#expire();
			return;
		}
		// wsUnsuccessfulReconnects сбрасывается сам при успешной синхронизации.
		if (this.#provider.wsUnsuccessfulReconnects >= COLLAB_MAX_RETRIES) this.#expire();
	};

	/** Сервер закрыл соединение «насовсем» (диапазон 4400-4499). */
	#onClosed = (): void => {
		if (this.#stopped) return;
		this.#expire();
	};

	#expire(): void {
		this.#emitStatus('error', 'Сессия истекла');
		this.stop();
	}

	#bindPending(): void {
		const pending = this.#pendingAttach;
		if (!pending || this.#bindingRequested || this.#binding || this.#stopped) return;
		if (!this.#ytext || !this.#provider) return;
		if (pending.model.isDisposed()) {
			this.detachEditor();
			return;
		}
		if (this.#ytext.length === 0) {
			// Модель могла уже получить правки пользователя до синка — сеем её
			// текущее содержимое; initialText — запасной вариант.
			const seed = pending.model.getValue() || pending.initialText;
			if (seed) this.setDocText(seed);
		}
		this.#bindingRequested = true;
		const seq = ++this.#attachSeq;
		const ytext = this.#ytext;
		const awareness = this.#provider.awareness;
		// Ленивый импорт: статический тянет Monaco и ломает Node-тесты.
		void import('y-monaco')
			.then(({ MonacoBinding }): void => {
				this.#bindingRequested = false;
				if (this.#stopped || seq !== this.#attachSeq || this.#ytext !== ytext) return;
				if (pending.model.isDisposed()) return;
				this.#binding = new MonacoBinding(ytext, pending.model, new Set([pending.editor]), awareness);
				this.#attachedModel = pending.model;
			})
			.catch((): void => {
				this.#bindingRequested = false;
				if (this.#stopped) return;
				this.#emitStatus('error', 'Не удалось подключить редактор');
				this.stop();
			});
	}

	#onAwarenessChange = (): void => {
		if (this.#stopped) return;
		const provider = this.#provider;
		if (!provider) return;
		this.#opts.onPeers(buildPeers(provider.awareness.getStates(), provider.doc.clientID));
	};

	#onTextEvent = (): void => {
		if (this.#textTimer) clearTimeout(this.#textTimer);
		this.#textTimer = setTimeout(() => {
			this.#textTimer = undefined;
			if (this.#stopped || !this.#ytext || !this.#textListener) return;
			this.#textListener(this.#ytext.toString());
		}, COLLAB_TEXT_DEBOUNCE_MS);
	};
}
