/** Status bar helper — ADR-0015 / 8bv.9.8.
 *
 * Format: `Ego: [Server|Offline] | <task_id> ✓ n/m`
 * Click → Ego: Dashboard.
 */

import * as vscode from 'vscode';
import type { EgoMode } from './egoWorkspace';

export interface StatusBarState {
    mode: EgoMode;
    taskId?: string;
    status?: string;
    passed?: number;
    total?: number;
    checking?: boolean;
    error?: boolean;
}

const STATUS_ICONS: Record<string, string> = {
    passed: '✓',
    partial: '◐',
    failed: '✗',
    error: '⚠',
    timeout: '⏱',
    no_tests: '○',
    new: '○',
};

export class EgoStatusBar {
    private item: vscode.StatusBarItem;
    private state: StatusBarState = { mode: 'server' };

    constructor(command = 'ego.dashboard') {
        this.item = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
        this.item.command = command;
        this.item.tooltip = 'Ego: Dashboard';
        this.render();
        this.item.show();
    }

    get disposable(): vscode.Disposable {
        return this.item;
    }

    getMode(): EgoMode {
        return this.state.mode;
    }

    setMode(mode: EgoMode): void {
        this.state.mode = mode;
        this.state.checking = false;
        this.state.error = false;
        this.render();
    }

    setTask(taskId: string, status?: string, passed?: number, total?: number): void {
        this.state.taskId = taskId;
        if (status !== undefined) this.state.status = status;
        if (passed !== undefined) this.state.passed = passed;
        if (total !== undefined) this.state.total = total;
        this.state.checking = false;
        this.state.error = false;
        this.render();
    }

    setChecking(): void {
        this.state.checking = true;
        this.state.error = false;
        this.render();
    }

    setCheckResult(
        taskId: string,
        status: string,
        passed: number,
        total: number
    ): void {
        this.state.taskId = taskId;
        this.state.status = status;
        this.state.passed = passed;
        this.state.total = total;
        this.state.checking = false;
        this.state.error = false;
        this.render();
    }

    setError(message?: string): void {
        this.state.checking = false;
        this.state.error = true;
        this.item.tooltip = message ? `Ego: ${message}` : 'Ego: check failed';
        this.render();
    }

    clearTask(): void {
        this.state.taskId = undefined;
        this.state.status = undefined;
        this.state.passed = undefined;
        this.state.total = undefined;
        this.state.checking = false;
        this.state.error = false;
        this.render();
    }

    private render(): void {
        const modeLabel = this.state.mode === 'offline' ? 'Offline' : 'Server';
        if (this.state.checking) {
            this.item.text = `$(loading~spin) Ego: ${modeLabel} | checking…`;
            this.item.tooltip = 'Ego: running check…';
            return;
        }
        if (this.state.error) {
            this.item.text = `$(error) Ego: ${modeLabel}`;
            return;
        }
        if (this.state.taskId) {
            const icon = STATUS_ICONS[this.state.status || ''] || '○';
            const scores =
                this.state.passed !== undefined && this.state.total !== undefined
                    ? ` ${this.state.passed}/${this.state.total}`
                    : '';
            this.item.text = `Ego: ${modeLabel} | ${this.state.taskId} ${icon}${scores}`;
            this.item.tooltip = `Ego Dashboard — ${this.state.taskId} (${this.state.status || 'new'})`;
            return;
        }
        this.item.text = `Ego: ${modeLabel}`;
        this.item.tooltip = 'Ego: Dashboard';
    }
}
