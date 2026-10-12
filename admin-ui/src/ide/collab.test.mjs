import assert from 'node:assert/strict';
import test from 'node:test';

// Pure parts of the collab client only — no network, no websocket, no Monaco.
import {
	buildPeers,
	collabRoomFor,
	COLLAB_MAX_RETRIES,
	COLLAB_SCENARIOS,
	COLLAB_TEXT_DEBOUNCE_MS,
	COLLAB_TOKEN_CLOSE_CODE,
	collabServerUrl,
	fallbackPeerName,
	hashString,
	mapStatus,
	parseCollabRoom,
	peerColorFor,
	PEER_COLORS,
} from './collab.ts';

// --- collabRoomFor / parseCollabRoom ----------------------------------------

test('collabRoomFor formats the pair room for a task-bound file', () => {
	assert.equal(collabRoomFor('F1.fib', 'abc123'), 'pair:F1.fib:abc123');
	assert.equal(collabRoomFor('block-f2/task', 'f_1-x'), 'pair:block-f2/task:f_1-x');
});

test('collabRoomFor keeps scenario, task and file parts separable', () => {
	const room = collabRoomFor('task:with:colons', 'file1');
	// Colons in a taskId make the room ambiguous — parse must reject it.
	assert.equal(parseCollabRoom(room), null);
	assert.deepEqual(parseCollabRoom(collabRoomFor('F1', 'file1')), {
		scenario: 'pair',
		taskId: 'F1',
		fileKey: 'file1',
	});
});

test('parseCollabRoom validates the scenario against COLLAB_SCENARIOS', () => {
	for (const scenario of COLLAB_SCENARIOS) {
		assert.deepEqual(parseCollabRoom(`${scenario}:task:file`), {
			scenario,
			taskId: 'task',
			fileKey: 'file',
		});
	}
	assert.equal(parseCollabRoom('random:task:file'), null);
	assert.equal(parseCollabRoom('pair:task'), null);
	assert.equal(parseCollabRoom('pair:task:file:extra'), null);
	assert.equal(parseCollabRoom(''), null);
});

test('parseCollabRoom rejects empty task or file parts', () => {
	assert.equal(parseCollabRoom('pair::file'), null);
	assert.equal(parseCollabRoom('pair:task:'), null);
});

test('COLLAB_SCENARIOS lists studio, defense and pair', () => {
	assert.deepEqual([...COLLAB_SCENARIOS], ['studio', 'defense', 'pair']);
});

// --- buildPeers ---------------------------------------------------------------

test('buildPeers maps awareness states to peers with fallbacks', () => {
	const states = new Map([
		[7, { user: { name: 'Ольга', role: 'mentor', color: '#ffffff' } }],
		[8, { user: { name: '', role: 'student', color: '' } }],
		[9, { user: { role: 'student' } }],
		[10, {}],
		[11, { user: 'not-an-object' }],
		[12, { user: { name: 'Anna', role: 'student' } }],
	]);
	const peers = buildPeers(states, 1);
	assert.equal(peers.length, 6);
	assert.deepEqual(peers[0], {
		clientID: 7,
		name: 'Ольга',
		role: 'mentor',
		color: '#ffffff',
		cursor: null,
	});
	assert.equal(peers[1].name, 'Гость 8');
	assert.equal(peers[1].color, peerColorFor('Гость 8'));
	assert.equal(peers[2].name, 'Гость 9');
	assert.equal(peers[2].role, 'student');
	assert.equal(peers[3].name, 'Гость 10');
	assert.equal(peers[3].role, '');
	// «user», не являющийся объектом, приравнивается к отсутствию user.
	assert.equal(peers[4].name, 'Гость 11');
	assert.equal(peers[5].name, 'Anna');
	assert.equal(peers[5].color, peerColorFor('Anna'));
	assert.ok(peers.every((peer) => peer.cursor === null));
});

test('buildPeers excludes the local client and survives null states', () => {
	const states = new Map([
		[1, { user: { name: 'self', role: 'student' } }],
		[2, {}],
		[3, null],
		[4, { user: { name: 'Anna', role: 'student' } }],
	]);
	const peers = buildPeers(states, 1);
	assert.equal(peers.length, 3);
	assert.ok(peers.every((peer) => peer.clientID !== 1));
	assert.deepEqual(buildPeers(new Map(), 42), []);
});

// --- color assignment ---------------------------------------------------------

test('peerColorFor is deterministic and stays inside the palette', () => {
	const first = peerColorFor('anna');
	assert.ok(PEER_COLORS.includes(first));
	assert.equal(peerColorFor('anna'), first);
	assert.equal(peerColorFor('Иван Петров'), peerColorFor('Иван Петров'));
	for (const name of ['', 'a', 'bb', 'ccc', 'Иван', 'mentor-1']) {
		assert.ok(PEER_COLORS.includes(peerColorFor(name)));
	}
});

test('hashString is stable and matches the djb2-like rule', () => {
	assert.equal(hashString(''), 0);
	assert.equal(hashString('ab'), (97 * 31 + 98) | 0 >= 0 ? (97 * 31 + 98) : -(97 * 31 + 98));
	// Разные имена в основном дают разные цвета.
	const colors = new Set(['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'].map((n) => peerColorFor(n)));
	assert.ok(colors.size > 1, `expected variety, got ${colors.size}`);
});

test('fallbackPeerName renders the guest placeholder in Russian', () => {
	assert.equal(fallbackPeerName(12), 'Гость 12');
});

// --- mapStatus ----------------------------------------------------------------

test('mapStatus covers the full ws-status matrix', () => {
	assert.equal(mapStatus('connecting', false), 'connecting');
	assert.equal(mapStatus('connecting', true), 'connecting');
	assert.equal(mapStatus('connected', false), 'syncing');
	assert.equal(mapStatus('connected', true), 'live');
	assert.equal(mapStatus('disconnected', false), 'error');
	assert.equal(mapStatus('disconnected', true), 'error');
});

test('mapStatus maps unknown statuses to off', () => {
	assert.equal(mapStatus('weird', false), 'off');
	assert.equal(mapStatus('', true), 'off');
});

// --- constants ----------------------------------------------------------------

test('session constants: retries, token close code and debounce', () => {
	assert.equal(COLLAB_MAX_RETRIES, 3);
	assert.equal(COLLAB_TOKEN_CLOSE_CODE, 1008);
	assert.equal(COLLAB_TEXT_DEBOUNCE_MS, 400);
});

// --- collabServerUrl ----------------------------------------------------------

test('collabServerUrl derives ws/wss from the page origin', () => {
	assert.equal(collabServerUrl({ protocol: 'https:', host: 'cogito.example' }), 'wss://cogito.example/collab/ws');
	assert.equal(collabServerUrl({ protocol: 'http:', host: 'localhost:8000' }), 'ws://localhost:8000/collab/ws');
	assert.equal(collabServerUrl({ protocol: 'file:', host: 'x' }), 'ws://x/collab/ws');
});
