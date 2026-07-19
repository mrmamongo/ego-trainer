/** TreeDataProvider for Ego Tasks sidebar.
 *
 * Shows blocks → tasks with status icons. Clicking a task opens it.
 */

import * as vscode from 'vscode';
import { EgoApi, TaskMeta, ProgressRow } from './api';

export class TaskItem extends vscode.TreeItem {
    constructor(
        public readonly task: TaskMeta,
        public readonly progress: ProgressRow | undefined,
        collapsibleState: vscode.TreeItemCollapsibleState
    ) {
        super(task.task_id, collapsibleState);
        this.tooltip = `${task.title} (v${task.version})`;
        this.description = this._statusLabel();
        this.contextValue = 'task';
        this.iconPath = this._icon();
        this.command = {
            command: 'ego.openTask',
            title: 'Open Task',
            arguments: [task],
        };
    }

    private _statusLabel(): string {
        if (!this.progress) {
            return 'new';
        }
        const icon = this._statusIcon(this.progress.status);
        return `${icon} ${this.progress.passed_tests}/${this.progress.total_tests}`;
    }

    private _statusIcon(status: string): string {
        switch (status) {
            case 'passed': return '✓';
            case 'partial': return '◐';
            case 'failed': return '✗';
            case 'error': return '⚠';
            default: return '○';
        }
    }

    private _icon(): vscode.ThemeIcon {
        if (!this.progress) {
            return new vscode.ThemeIcon('circle-outline');
        }
        switch (this.progress.status) {
            case 'passed':
                return new vscode.ThemeIcon('check', new vscode.ThemeColor('testing.iconPassed'));
            case 'partial':
                return new vscode.ThemeIcon('circle-filled', new vscode.ThemeColor('testing.iconQueued'));
            case 'failed':
            case 'error':
                return new vscode.ThemeIcon('x', new vscode.ThemeColor('testing.iconFailed'));
            default:
                return new vscode.ThemeIcon('circle-outline');
        }
    }
}

export class BlockItem extends vscode.TreeItem {
    constructor(
        public readonly block: string,
        public readonly taskCount: number,
        collapsibleState: vscode.TreeItemCollapsibleState
    ) {
        super(`Block ${block}`, collapsibleState);
        this.description = `${taskCount} tasks`;
        this.contextValue = 'block';
        this.iconPath = new vscode.ThemeIcon('folder');
    }
}

export class EgoTaskTreeProvider implements vscode.TreeDataProvider<BlockItem | TaskItem> {
    private _onDidChange = new vscode.EventEmitter<void>();
    readonly onDidChangeTreeData = this._onDidChange.event;

    private api: EgoApi;
    private progressMap: Map<string, ProgressRow> = new Map();

    constructor(api: EgoApi) {
        this.api = api;
    }

    updateApi(newApi: EgoApi): void {
        this.api = newApi;
        this.progressMap.clear();
        this.refresh();
    }

    refresh(): void {
        this._onDidChange.fire();
    }

    getTreeItem(element: BlockItem | TaskItem): vscode.TreeItem {
        return element;
    }

    async getChildren(element?: BlockItem | TaskItem): Promise<(BlockItem | TaskItem)[]> {
        if (!element) {
            // Root: return blocks.
            try {
                const tasks = await this.api.listTasks();
                // Also load progress for status icons.
                try {
                    const me = await this.api.me();
                    const progress = await this.api.getProgress(me.user_id);
                    this.progressMap = new Map(progress.map(p => [p.task_id, p]));
                } catch {
                    // Progress loading failed — show without status.
                }
                // Group by block.
                const blocks = new Map<string, TaskMeta[]>();
                for (const t of tasks) {
                    if (!blocks.has(t.block)) {
                        blocks.set(t.block, []);
                    }
                    blocks.get(t.block)!.push(t);
                }
                return Array.from(blocks.entries())
                    .sort((a, b) => a[0].localeCompare(b[0]))
                    .map(([block, tasks]) =>
                        new BlockItem(block, tasks.length, vscode.TreeItemCollapsibleState.Collapsed)
                    );
            } catch (e) {
                return [new BlockItem('Error', 0, vscode.TreeItemCollapsibleState.None)];
            }
        }

        if (element instanceof BlockItem) {
            // Block: return its tasks.
            try {
                const tasks = await this.api.listTasks(element.block);
                return tasks
                    .sort((a, b) => a.task_id.localeCompare(b.task_id))
                    .map(t =>
                        new TaskItem(
                            t,
                            this.progressMap.get(t.task_id),
                            vscode.TreeItemCollapsibleState.None
                        )
                    );
            } catch {
                return [];
            }
        }

        return [];
    }
}
