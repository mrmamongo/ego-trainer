export interface AIAccount {
    student_id: string;
    enabled: boolean;
    defense_required: boolean;
    available: boolean;
    reason: string;
    balance_usd: string;
    reserved_usd: string;
    spent_usd: string;
}

export interface AISubmission {
    id: string;
    task_id: string;
    version: string;
    solution_hash: string;
    understanding: string;
    evidence: { stage: string; quote: string }[];
}

export interface AISession {
    id: string;
    task_id: string;
    mode: 'hint' | 'explain' | 'defend';
    status: string;
    stage: string;
    submission_id: string | null;
    messages: { role: string; content: string }[];
    account: AIAccount;
}

export interface AssistantData {
    taskId: string;
    account: AIAccount | null;
    session: AISession | null;
    submissionId?: string;
    busy: boolean;
    error: string;
}
