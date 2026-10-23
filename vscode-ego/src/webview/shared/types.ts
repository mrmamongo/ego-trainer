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
    understanding?: { submission_id: string; status: string } | null;
}

export type EgoMode = 'server' | 'offline';

export interface TaskRunSummary {
	id: string;
	started_at: string;
	finished_at: string;
	status: string;
	passed_tests: number;
	total_tests: number;
}

export type TaskStatusFilter = 'all' | 'passed' | 'partial' | 'new' | 'failed';

export interface DashboardRow {
	id: string;
	title: string;
	block: string;
	slug: string;
	version: string;
	stale: boolean;
	status: string; // passed | partial | new | failed | error | ...
	passed_tests: number;
	total_tests: number;
	attempts: number;
	last_run_at: string | null;
	md_path?: string;
	// Catalog fields (null/[] on older servers) — project → folder breakdown.
	project_id?: string | null;
	project_name?: string | null;
	project_order?: number;
	folder_id?: string | null;
	folder_name?: string | null;
	folder_order?: number;
	theory?: string[];
	/** Row state computed by the host (dashboardLogic.taskState). */
	state?: TaskState;
}

export type TaskState = 'passed' | 'defense' | 'started' | 'failed' | 'new';

/** Folder progress bar (project-level groups have no id). */
export interface FolderProgress {
	key: string;
	name: string;
	passed: number;
	total: number;
	percent: number;
}

export interface ProjectProgress extends FolderProgress {
	folders: FolderProgress[];
}

/** One row of GET /progress/me/understanding, ready to render. */
export interface UnderstandingEntry {
	task_id: string;
	task_title: string;
	status: string; // pending | confirmed | needs_review | active
	status_label: string;
	at: string | null;
}

/** Subset of GET /ai/me shown in the cabinet. */
export interface AiAccess {
	enabled: boolean;
	available: boolean;
	defense_required: boolean;
	reason: string;
	balance_usd: string;
	spent_usd: string;
}

export interface Cabinet {
	/** Per-project → per-folder passed/total progress. */
	projects: ProjectProgress[];
	/** First not-passed task in catalog order. */
	next_task_id: string | null;
	next_task_title: string | null;
	/** Understanding evidence, newest first (null = endpoint unavailable). */
	understanding: UnderstandingEntry[] | null;
	/** AI access/budget (null = endpoint unavailable or offline). */
	ai: AiAccess | null;
	/** Evidence rows that make a passed solution count as «Решена». */
	defense_required: boolean;
	/** Task id → state; absent keys are unknown (no progress data). */
	states: Record<string, TaskState>;
	/** AIAccount.reason already translated to Russian by the host. */
	ai_reason_label: string | null;
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
	/** Student cabinet sections; absent on data cached before the upgrade. */
	cabinet?: Cabinet;
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
	history: TaskRunSummary[];
	mode: EgoMode;
    ai_available?: boolean;
    loading?: boolean;
    /** 'lesson' = theory card (no check, read toggle). Default 'task'. */
    kind?: 'task' | 'lesson';
    /** Linked theory lessons (pre-rendered HTML), in the task's order. */
    theory?: TheoryItem[];
    lesson?: { id: string; content_hash: string; read: boolean };
}

export interface TheoryItem {
	id: string;
	title: string;
	html: string;
}
