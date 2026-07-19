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
