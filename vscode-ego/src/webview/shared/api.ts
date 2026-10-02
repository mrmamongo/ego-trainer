/** postMessage wrapper for VSCode webview <-> extension host */
export type ExtMessage =
	| { type: 'assistant.refresh' }
	| { type: 'assistant.start'; mode: 'hint' | 'explain' | 'defend'; taskId: string }
	| { type: 'assistant.send'; text: string; taskId: string }
	| { type: 'assistant.tasks' }
	| { type: 'assistant.login' }
	| { type: 'assistant.connect' }
	| { type: 'taskView.assistant'; taskId: string }
	| { type: 'setResult'; payload: import('./types').CheckResult }
	| { type: 'ready' }
	| { type: 'welcome.connect' }
	| { type: 'welcome.offline' }
	| { type: 'welcome.skip' }
	| { type: 'dashboard.refresh' }
	| { type: 'dashboard.open'; taskId: string }
	| { type: 'dashboard.check'; taskId: string }
	| { type: 'dashboard.hints'; taskId: string }
	| { type: 'dashboard.pullAll' }
	| { type: 'dashboard.push' }
	| { type: 'taskView.check'; taskId: string }
	| { type: 'taskView.openPy'; taskId: string }
	| { type: 'taskView.refresh' };

export type HostMessage =
	| { type: 'assistant.data'; payload: import('../../aiTypes').AssistantData }
	| { type: 'setResult'; payload: import('./types').CheckResult }
	| { type: 'dashboard.setData'; payload: import('./types').DashboardData }
	| { type: 'taskView.setData'; payload: import('./types').TaskViewData }
	| { type: 'taskView.setResult'; payload: import('./types').CheckResult }
	| { type: 'noop' };

declare function acquireVsCodeApi(): {
	postMessage(msg: ExtMessage): void;
	getState(): unknown;
	setState(state: unknown): void;
};

const vscode = acquireVsCodeApi();

export function postToHost(msg: ExtMessage): void {
	vscode.postMessage(msg);
}

export function onHostMessage(handler: (msg: HostMessage) => void): () => void {
	const listener = (event: MessageEvent<HostMessage>) => {
		if (event.data && typeof event.data === 'object' && 'type' in event.data) {
			handler(event.data);
		}
	};
	window.addEventListener('message', listener);
	return () => window.removeEventListener('message', listener);
}

export function getVsCodeApi() {
	return vscode;
}
