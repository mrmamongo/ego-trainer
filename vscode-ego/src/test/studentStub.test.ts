import { test } from 'node:test';
import assert from 'node:assert/strict';
import { studentStubFromSolution } from '../studentStub';

test('simple function keeps imports and signature while replacing body', () => {
    const source = `import math
from pathlib import Path

CONSTANT = "hidden constant"
def add(a: int, b: int) -> int:
    """hidden docstring"""
    return a + b`;

    assert.equal(
        studentStubFromSolution(source),
        'import math\nfrom pathlib import Path\ndef add(a: int, b: int) -> int:\n    pass\n'
    );
});

test('multiline async function keeps its complete typed signature', () => {
    const source = `from collections.abc import Iterable

async def fetch_items(
    values: Iterable[str],
    limit: int = 3,
) -> list[str]:
    return [value for value in values][:limit]`;

    assert.equal(
        studentStubFromSolution(source),
        'from collections.abc import Iterable\nasync def fetch_items(\n    values: Iterable[str],\n    limit: int = 3,\n) -> list[str]:\n    pass\n'
    );
});

test('keeps two top-level functions', () => {
    const source = `def first(value: int) -> int:
    return value + 1


def second(value: str) -> str:
    return value.upper()`;

    assert.equal(
        studentStubFromSolution(source),
        'def first(value: int) -> int:\n    pass\ndef second(value: str) -> str:\n    pass\n'
    );
});

test('excludes secrets, constants, docstrings, returns, and nested definitions', () => {
    const source = `"""module documentation secret"""
SECRET_TOKEN = "do-not-copy"
class HiddenClass:
    pass

def visible(value: str) -> str:
    """function documentation secret"""
    nested_secret = "nested secret"
    def nested() -> str:
        return "nested return secret"
    class NestedClass:
        pass
    return "return secret"`;

    const stub = studentStubFromSolution(source);
    assert.equal(stub, 'def visible(value: str) -> str:\n    pass\n');
    for (const excluded of [
        'module documentation secret',
        'SECRET_TOKEN',
        'do-not-copy',
        'HiddenClass',
        'function documentation secret',
        'nested_secret',
        'nested secret',
        'nested',
        'nested return secret',
        'NestedClass',
        'return secret',
    ]) {
        assert.equal(stub.includes(excluded), false, `unexpected output: ${excluded}`);
    }
});

test('throws when there is no top-level function definition', () => {
    assert.throws(
        () => studentStubFromSolution('import os\nVALUE = 1\nclass Example:\n    pass\n'),
        /No top-level def found/
    );
});

test('throws on an unterminated top-level function signature', () => {
    assert.throws(
        () => studentStubFromSolution('def broken(\n    value: int\n'),
        /Unterminated top-level function signature/
    );
});
