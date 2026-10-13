import { test } from 'node:test';
import assert from 'node:assert/strict';

import {
	buildWorkspaceZip,
	crc32,
	languageForName,
	parseWorkspaceZip,
} from './wsZip.ts';

const encoder = new TextEncoder();

test('round-trip: build → parse preserves name/language/content', () => {
	const longContent = [
		'# Мой блокнот',
		'',
		'Строка 1: кириллица и пробелы',
		'Строка 2: табы\tи "кавычки"',
		'',
		'Финальная строка с эмодзи 🐍',
		' и переводом строки внутри',
	].join('\n');

	const files = [
		{
			name: 'моё решение.py',
			language: 'python',
			content: 'def answer():\n    return 42\n',
		},
		{
			name: 'notes with spaces.md',
			language: 'markdown',
			content: longContent,
		},
		{
			name: 'scratch.txt',
			language: 'plaintext',
			content: '',
		},
	];

	const zipBytes = buildWorkspaceZip(files);
	const parsed = parseWorkspaceZip(zipBytes);

	assert.deepEqual(
		parsed.map(({ name, language, content }) => ({ name, language, content })),
		files,
	);
});

test('parse rejects garbage bytes with "Не zip-архив"', () => {
	const garbage = encoder.encode('this is not a zip archive at all');
	assert.throws(() => parseWorkspaceZip(garbage), /Не zip-архив/);
});

test('languageForName maps extensions case-insensitively', () => {
	assert.equal(languageForName('solution.py'), 'python');
	assert.equal(languageForName('NOTES.MD'), 'markdown');
	assert.equal(languageForName('data.txt'), 'plaintext');
});

test('crc32 known vector: crc32("123456789") === 0xCBF43926', () => {
	assert.equal(crc32(encoder.encode('123456789')), 0xcbf43926);
});
