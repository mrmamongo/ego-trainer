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
	/** Soft recommendation cards (labels pre-rendered by the host; [] = none). */
	recommendation_cards?: RecommendationCard[];
	/** Exam breakdown card (bug / modify / new), null = hidden. */
	breakdown?: BreakdownCard | null;
}

/** One project card: readiness against its `recommended_after` (soft, never blocking). */
export interface RecommendationCard {
	id: string;
	name: string;
	/** True when a recommendation is declared but not met yet. */
	unmet: boolean;
	/** «рекомендуем после XL-A: 14/21» or null. */
	readiness_label: string | null;
	/** The author's note (may be empty). */
	note: string;
	/** Per-kind progress («баги 3/6, доработки 2/6, новое 0/6») or null. */
	per_kind_label: string | null;
	/** Project progress line, e.g. «12/27 решено». */
	progress_label: string;
}

/** XL-A style breakdown card: one bar per kind tag. */
export interface BreakdownRow {
	key: string;
	label: string;
	passed: number;
	total: number;
	percent: number;
}

export interface BreakdownCard {
	project_id: string;
	project_name: string;
	rows: BreakdownRow[];
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
    /** Interactive trainer for tasks tagged `trace` / `parsons` (see ../../trainer). */
    trainer?: TrainerKind;
}

export interface TheoryItem {
	id: string;
	title: string;
	html: string;
}

// === Trainers (mirror of src/trainer.ts; that module must not be imported by the webview) ===

export type TrainerKind = 'trace' | 'parsons';

export interface TraceLine {
	label: string; // "1", "A2"
	code: string; // code with its Python indentation
}

export interface TraceAnswer {
	name: string;
	label: string; // «a после строки 3», «x в конце»
	value: string; // prefilled literal, '' when None
	line: string | null; // referenced trace line for highlighting
}

export interface TraceState {
	kind: 'trace';
	supported: true;
	intro: string;
	lines: TraceLine[];
	answers: TraceAnswer[];
}

export interface ParsonsLine {
	id: number;
	text: string;
	level: number;
}

export interface ParsonsState {
	kind: 'parsons';
	supported: true;
	defLine: string;
	intro: string;
	lines: ParsonsLine[];
	assembled: boolean;
}

export type TrainerState =
	| TraceState
	| ParsonsState
	| { kind: TrainerKind | null; supported: false; reason: string };
