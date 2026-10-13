// Чистые хелперы для палитры быстрого открытия (Ctrl+P). Без DOM, без импортов.

export type PaletteItem = {
	id: string;
	kind: 'file' | 'task' | 'command';
	label: string;
	hint?: string;
};

export type PaletteInputFile = { id: string; name: string };
export type PaletteInputTask = { task_id: string; title?: string; block?: string };
export type PaletteInputCommand = { id: string; label: string };

export type PaletteInput = {
	query: string;
	files: PaletteInputFile[];
	tasks: PaletteInputTask[];
	commands: PaletteInputCommand[];
};

const CAP = 50;

// Каждый терм запроса должен встречаться (подстрока, без учёта регистра)
// хотя бы в одном из полей: label, hint, id. Порядок термов не важен.
function matchesEveryTerm(item: PaletteItem, terms: string[]): boolean {
	const haystack = `${item.label}\n${item.hint ?? ''}\n${item.id}`.toLowerCase();
	return terms.every((term) => haystack.includes(term.toLowerCase()));
}

function byLabel(a: PaletteItem, b: PaletteItem): number {
	return a.label.localeCompare(b.label, 'ru');
}

export function buildPaletteItems(input: PaletteInput): PaletteItem[] {
	const terms = input.query.split(/\s+/).filter((term) => term.length > 0);

	const commands: PaletteItem[] = input.commands
		.map((command) => ({
			id: `cmd:${command.id}`,
			kind: 'command',
			label: command.label,
			hint: 'команда',
		}))
		.filter((item) => matchesEveryTerm(item, terms))
		.sort(byLabel);

	const files: PaletteItem[] = input.files
		.map((file) => ({
			id: `file:${file.id}`,
			kind: 'file',
			label: file.name,
			hint: 'файл',
		}))
		.filter((item) => matchesEveryTerm(item, terms))
		.sort(byLabel);

	const tasks: PaletteItem[] = input.tasks
		.map((task) => ({
			id: `task:${task.task_id}`,
			kind: 'task',
			label: `${task.block ? task.block + ' · ' : ''}${task.title ?? task.task_id}`,
			hint: 'задача',
		}))
		.filter((item) => matchesEveryTerm(item, terms))
		.sort(byLabel);

	return [...commands, ...files, ...tasks].slice(0, CAP);
}
