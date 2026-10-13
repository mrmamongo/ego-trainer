import assert from 'node:assert/strict';
import { describe, it } from 'node:test';
import { buildPaletteItems } from './paletteItems.ts';

const base = {
	files: [
		{ id: 'f1', name: 'main.py' },
		{ id: 'f2', name: 'README.md' },
		{ id: 'f3', name: 'задача_про_списки.py' },
	],
	tasks: [
		{ task_id: 't1', title: 'Сумма чисел', block: 'Блок F' },
		{ task_id: 't2', title: 'Работа со строками', block: 'Блок H' },
		{ task_id: 't3' },
	],
	commands: [
		{ id: 'save', label: 'Сохранить файл' },
		{ id: 'check', label: 'Запустить проверку' },
	],
};

describe('buildPaletteItems', () => {
	it('empty query returns all, commands first, then files, then tasks', () => {
		const items = buildPaletteItems({ query: '   ', ...base });
		assert.equal(items.length, 8);
		assert.deepEqual(
			items.map((item) => item.kind),
			['command', 'command', 'file', 'file', 'file', 'task', 'task', 'task'],
		);
		assert.deepEqual(items[0], {
			id: 'cmd:check',
			kind: 'command',
			label: 'Запустить проверку',
			hint: 'команда',
		});
	});

	it('maps items with russian hints and prefixed ids', () => {
		const items = buildPaletteItems({ query: '', ...base });
		assert.ok(items.some((item) => item.id === 'file:f1' && item.label === 'main.py' && item.hint === 'файл'));
		assert.ok(
			items.some(
				(item) => item.id === 'task:t1' && item.label === 'Блок F · Сумма чисел' && item.hint === 'задача',
			),
		);
		assert.ok(items.some((item) => item.id === 'task:t3' && item.label === 't3'));
	});

	it('multi-term matching is order-independent', () => {
		const byNameThenBlock = buildPaletteItems({ query: 'строками Блок', ...base });
		assert.ok(byNameThenBlock.some((item) => item.id === 'task:t2'));
		const byBlockThenName = buildPaletteItems({ query: 'Блок строками', ...base });
		assert.deepEqual(
			byNameThenBlock.map((item) => item.id),
			byBlockThenName.map((item) => item.id),
		);
		// Каждый терм должен совпасть: «Блок» + «чисел» оставляют только t1.
		const narrowed = buildPaletteItems({ query: 'Блок чисел', ...base });
		assert.deepEqual(
			narrowed.map((item) => item.id),
			['task:t1'],
		);
	});

	it('matching is case-insensitive across label, hint and id', () => {
		const byLabel = buildPaletteItems({ query: 'MAIN', ...base });
		assert.deepEqual(
			byLabel.map((item) => item.id),
			['file:f1'],
		);
		// Подстрока ищется по label/hint/id: «задача» есть и в hint задач,
		// и в имени файла «задача_про_списки.py».
		const byHint = buildPaletteItems({ query: 'ЗАДАЧА', ...base });
		assert.equal(byHint.length, 4);
		assert.deepEqual(
			byHint.filter((item) => item.kind === 'task').length,
			3,
		);
		const byId = buildPaletteItems({ query: 't2', ...base });
		assert.deepEqual(
			byId.map((item) => item.id),
			['task:t2'],
		);
	});

	it('grouping order holds inside filtered results', () => {
		const items = buildPaletteItems({ query: 'ф', ...base });
		const kinds = items.map((item) => item.kind);
		assert.deepEqual(kinds, [...kinds].sort((a, b) => ({ command: 0, file: 1, task: 2 })[a] - ({ command: 0, file: 1, task: 2 })[b]));
		assert.equal(items[0].kind, 'command');
	});

	it('cyrillic terms match cyrillic labels', () => {
		const items = buildPaletteItems({ query: 'проверку', ...base });
		assert.deepEqual(
			items.map((item) => item.id),
			['cmd:check'],
		);
		const tasks = buildPaletteItems({ query: 'списки', ...base });
		assert.deepEqual(
			tasks.map((item) => item.id),
			['file:f3'],
		);
	});

	it('result is capped at 50 items', () => {
		const many = {
			query: '',
			files: Array.from({ length: 30 }, (_, i) => ({ id: `f${i}`, name: `file_${String(i).padStart(2, '0')}.py` })),
			tasks: Array.from({ length: 30 }, (_, i) => ({ task_id: `t${i}`, title: `Задача ${String(i).padStart(2, '0')}` })),
			commands: Array.from({ length: 30 }, (_, i) => ({ id: `c${i}`, label: `Команда ${String(i).padStart(2, '0')}` })),
		};
		const items = buildPaletteItems(many);
		assert.equal(items.length, 50);
		// Кап режет с конца: команды и файлы целиком, задачи частично.
		assert.ok(items.every((item) => item.kind !== 'task' || item.id.startsWith('task:t')));
	});
});
