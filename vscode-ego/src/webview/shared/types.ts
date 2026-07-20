export interface TestResultDTO {
	description: string;
	passed: boolean;
	expected_repr: string;
	actual_repr: string | null;
	error: string | null;
}

export interface CheckResult {
	task_id: string;
	version: string;
	status: string; // passed | partial | failed | error | timeout | no_tests
	passed_tests: number;
	total_tests: number;
	solution_hash: string;
	results: TestResultDTO[];
	log: string;
}

export type EgoMode = 'server' | 'offline';

export type TaskStatusFilter = 'all' | 'passed' | 'partial' | 'new' | 'failed';

export interface DashboardRow {
	id: string;
	title: string;
	block: string;
	slug: string;
	version: string;
	status: string; // passed | partial | new | failed | error | ...
	passed_tests: number;
	total_tests: number;
	attempts: number;
	last_run_at: string | null;
	md_path?: string;
}

export interface DashboardSummary {
	passed: number;
	partial: number;
	new: number;
	failed: number;
	total: number;
}

export interface DashboardData {
	mode: EgoMode;
	summary: DashboardSummary;
	blocks: string[];
	rows: DashboardRow[];
	error?: string;
}

export interface TaskHint {
	level: number; // 1|2|3
	title: string;
	content: string;
}

export interface TaskViewData {
	id: string;
	title: string;
	status: string; // passed|partial|new|failed|...
	version: string;
	statement_html: string; // pre-rendered markdown HTML from host
	hints: TaskHint[];
	mode: EgoMode;
}
