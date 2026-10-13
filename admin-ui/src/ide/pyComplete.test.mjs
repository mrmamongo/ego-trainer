import assert from 'node:assert/strict';
import test from 'node:test';

import {
	PY_BUILTINS,
	PY_KEYWORDS,
	PY_MODULES,
	PY_SNIPPETS,
	moduleBeforeDot,
	wordsFromDocument,
} from './pyComplete.ts';

test('builtins/keywords/modules/snippets are non-empty and sane', () => {
	assert.ok(PY_BUILTINS.length >= 40);
	assert.ok(PY_KEYWORDS.includes('def'));
	assert.ok(PY_MODULES.str.includes('split'));
	assert.ok(PY_MODULES.dict.includes('items'));
	assert.ok(PY_SNIPPETS.some(([label]) => label === 'main'));
	// Snippet inserts use monaco placeholder syntax.
	for (const [, insert] of PY_SNIPPETS) {
		assert.ok(!insert.includes('\\n'), 'raw escapes');
	}
});

test('moduleBeforeDot extracts the segment before the trailing dot', () => {
	assert.equal(moduleBeforeDot('str.'), 'str');
	assert.equal(moduleBeforeDot('os.pa'), null); // incomplete suffix, not a bare dot
	assert.equal(moduleBeforeDot('MyList . '), 'mylist');
	assert.equal(moduleBeforeDot('nodot'), null);
	assert.equal(moduleBeforeDot('a.b.'), 'b');
});

test('wordsFromDocument returns unique identifiers of length >= 3', () => {
	const words = wordsFromDocument('def solve(items):\n    return solve(items) + total\n');
	assert.deepEqual(words, ['def', 'solve', 'items', 'return', 'total']);
	assert.ok(!words.includes('a'));
});
