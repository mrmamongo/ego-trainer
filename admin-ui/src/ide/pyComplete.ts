/**
 * Offline Python autocompletion data for the /ide Monaco editor.
 *
 * Plain data + a tiny completion-provider factory, no default exports.
 * Everything is hand-rolled (no language server): builtins, methods of the
 * most-used stdlib modules (dot-completion), snippets and words from the
 * current document. Node-testable without a browser.
 */

/** Builtin functions/types with short Russian hints. */
export const PY_BUILTINS = [
	['abs(x)', 'абсолютное значение'],
	['all(it)', 'True, если все элементы истинны'],
	['any(it)', 'True, если хотя бы один истинн'],
	['bin(n)', 'двоичная строка'],
	['bool(v)', 'приведение к bool'],
	['bytes(s)', 'строка байтов'],
	['callable(o)', 'вызываем ли объект'],
	['chr(n)', 'символ по коду'],
	['classmethod(f)', 'декоратор classmethod'],
	['dict(**kw)', 'словарь'],
	['divmod(a, b)', '(частное, остаток)'],
	['enumerate(it)', 'пары (индекс, элемент)'],
	['filter(f, it)', 'элементы, где f(x) истинно'],
	['float(x)', 'приведение к float'],
	['format(v, spec)', 'форматирование'],
	['frozenset(it)', 'неизменяемое множество'],
	['getattr(o, name)', 'значение атрибута'],
	['hasattr(o, name)', 'есть ли атрибут'],
	['hash(o)', 'хеш объекта'],
	['hex(n)', 'шестнадцатеричная строка'],
	['id(o)', 'идентификатор объекта'],
	['input(prompt)', 'чтение строки из ввода'],
	['int(s)', 'приведение к int'],
	['isinstance(o, cls)', 'проверка типа'],
	['issubclass(a, b)', 'проверка подкласса'],
	['iter(it)', 'итератор'],
	['len(s)', 'длина'],
	['list(it)', 'список'],
	['map(f, it)', 'f по каждому элементу'],
	['max(it)', 'максимум'],
	['min(it)', 'минимум'],
	['next(it)', 'следующий элемент итератора'],
	['oct(n)', 'восьмеричная строка'],
	['open(path)', 'открыть файл'],
	['ord(c)', 'код символа'],
	['pow(a, b)', 'возведение в степень'],
	['print(*values)', 'печать'],
	['range(n)', 'диапазон 0..n-1'],
	['repr(o)', 'строковое представление'],
	['reversed(it)', 'обратный порядок'],
	['round(x)', 'округление'],
	['set(it)', 'множество'],
	['setattr(o, name, v)', 'установить атрибут'],
	['sorted(it)', 'отсортированный список'],
	['staticmethod(f)', 'декоратор staticmethod'],
	['str(x)', 'строка'],
	['sum(it)', 'сумма'],
	['super()', 'родительский класс'],
	['tuple(it)', 'кортеж'],
	['type(o)', 'тип объекта'],
	['zip(a, b)', 'пары элементов'],
];

/** Keywords — snippet-ish completions. */
export const PY_KEYWORDS = [
	'and', 'as', 'assert', 'async', 'await', 'break', 'class', 'continue', 'def', 'del', 'elif',
	'else', 'except', 'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is', 'lambda',
	'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'try', 'while', 'with', 'yield',
];

/** Methods of the most common stdlib modules, `module.` completion. */
export const PY_MODULES = {
	str: [
		'capitalize', 'casefold', 'center', 'count', 'encode', 'endswith', 'expandtabs', 'find',
		'format', 'format_map', 'index', 'isalnum', 'isalpha', 'isascii', 'isdecimal', 'isdigit',
		'isidentifier', 'islower', 'isnumeric', 'isprintable', 'isspace', 'istitle', 'isupper',
		'join', 'ljust', 'lower', 'lstrip', 'partition', 'removeprefix', 'removesuffix', 'replace',
		'rfind', 'rindex', 'rjust', 'rpartition', 'rsplit', 'rstrip', 'split', 'splitlines',
		'startswith', 'strip', 'swapcase', 'title', 'upper', 'zfill',
	],
	list: [
		'append', 'clear', 'copy', 'count', 'extend', 'index', 'insert', 'pop', 'remove',
		'reverse', 'sort',
	],
	dict: ['clear', 'copy', 'fromkeys', 'get', 'items', 'keys', 'pop', 'popitem', 'setdefault', 'update', 'values'],
	set: ['add', 'clear', 'copy', 'difference', 'discard', 'intersection', 'isdisjoint', 'issubset', 'issuperset', 'pop', 'remove', 'symmetric_difference', 'union', 'update'],
	tuple: ['count', 'index'],
	math: [
		'acos', 'acosh', 'asin', 'asinh', 'atan', 'atan2', 'atanh', 'ceil', 'comb', 'copysign',
		'cos', 'cosh', 'degrees', 'dist', 'erf', 'exp', 'expm1', 'fabs', 'factorial', 'floor',
		'fmod', 'gcd', 'hypot', 'inf', 'isclose', 'isfinite', 'isinf', 'isnan', 'lcm', 'ldexp',
		'log', 'log10', 'log2', 'modf', 'nan', 'perm', 'pi', 'pow', 'prod', 'radians', 'remainder',
		'sin', 'sinh', 'sqrt', 'tan', 'tanh', 'tau', 'trunc',
	],
	random: ['betavariate', 'choice', 'choices', 'expovariate', 'gammavariate', 'gauss', 'randint', 'random', 'randrange', 'sample', 'seed', 'shuffle', 'uniform'],
	collections: ['Counter', 'OrderedDict', 'defaultdict', 'deque', 'namedtuple'],
	itertools: [
		'accumulate', 'chain', 'combinations', 'combinations_with_replacement', 'compress',
		'count', 'cycle', 'dropwhile', 'filterfalse', 'groupby', 'islice', 'permutations',
		'product', 'repeat', 'starmap', 'takewhile', 'tee', 'zip_longest',
	],
	datetime: ['date', 'datetime', 'time', 'timedelta', 'timezone', 'MAXYEAR', 'MINYEAR'],
	re: [
		'compile', 'escape', 'findall', 'finditer', 'fullmatch', 'match', 'search', 'split',
		'sub', 'subn', 'I', 'M', 'S', 'X',
	],
	json: ['dump', 'dumps', 'load', 'loads', 'JSONDecodeError'],
	os: [
		'getcwd', 'listdir', 'makedirs', 'mkdir', 'name', 'path', 'remove', 'rename',
		'rmdir', 'sep', 'stat', 'walk',
	],
	sys: ['argv', 'exit', 'maxsize', 'path', 'platform', 'stderr', 'stdin', 'stdout', 'version'],
};

/** Insert-mode snippets: [label, insert, detail]. */
export const PY_SNIPPETS = [
	['main', 'def main():\n    ${1:pass}\n\n\nif __name__ == "__main__":\n    main()\n$0', 'точка входа'],
	['ifmain', 'if __name__ == "__main__":\n    ${1:main()}\n$0', 'запуск как скрипта'],
	['def', 'def ${1:name}(${2:}):\n    ${3:pass}\n$0', 'функция'],
	['class', 'class ${1:Name}:\n    def __init__(self${2:}):\n        ${3:pass}\n$0', 'класс с конструктором'],
	['dataclass', '@dataclass\nclass ${1:Name}:\n    ${2:x: int}\n$0', 'dataclass (нужен import dataclasses)'],
	['tryexcept', 'try:\n    ${1:pass}\nexcept ${2:Exception} as e:\n    ${3:pass}\n$0', 'try/except'],
	['tryfinally', 'try:\n    ${1:pass}\nfinally:\n    ${2:pass}\n$0', 'try/finally'],
	['forr', 'for ${1:i} in range(${2:n}):\n    ${3:pass}\n$0', 'for по range'],
	['fore', 'for ${1:item} in ${2:items}:\n    ${3:pass}\n$0', 'for по коллекции'],
	['foren', 'for ${1:i}, ${2:v} in enumerate(${3:items}):\n    ${4:pass}\n$0', 'for с индексом'],
	['while', 'while ${1:cond}:\n    ${2:pass}\n$0', 'цикл while'],
	['with', 'with ${1:open(path)} as ${2:f}:\n    ${3:pass}\n$0', 'менеджер контекста'],
	['lcomp', '[${1:x} for ${1:x} in ${2:items}]$0', 'списковое включение'],
	['dcomp', '{${1:k}: ${2:v} for ${1:k}, ${2:v} in ${3:items}}$0', 'dict comprehension'],
	['imp', 'import ${1:module}$0', 'import'],
	['fromimp', 'from ${1:module} import ${2:name}$0', 'from ... import'],
	['lambda', 'lambda ${1:x}: ${2:x}$0', 'лямбда'],
	['pr', 'print(${1:})$0', 'print'],
	['pdb', 'import pdb; pdb.set_trace()', 'точка останова'],
];

/**
 * The last dotted segment of an identifier prefix, lowercase — the module
 * name when the user typed `someth.`.
 */
export function moduleBeforeDot(word: string): string | null {
	const m = /([A-Za-z_][A-Za-z0-9_]*)\s*\.\s*$/.exec(word);
	return m ? m[1].toLowerCase() : null;
}

/** Unique identifiers (len >= 3) present in the document. */
export function wordsFromDocument(text: string): string[] {
	const seen = new Set<string>();
	const out: string[] = [];
	for (const m of text.matchAll(/[A-Za-z_][A-Za-z0-9_]{2,}/g)) {
		const w = m[0];
		if (!seen.has(w)) {
			seen.add(w);
			out.push(w);
		}
	}
	return out;
}
