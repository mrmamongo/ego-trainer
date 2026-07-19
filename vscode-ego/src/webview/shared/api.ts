/** postMessage wrapper for VSCode webview <-> extension host */
export type ExtMessage =
	| { type: 'setResult'; payload: import('./types').CheckResult }
	| { type: 'ready' }
	| { type: 'welcome.connect' }
	| { type: 'welcome.offline' }
	| { type: 'welcome.skip' };

export type HostMessage =
	| { type: 'setResult'; payload: import('./types').CheckResult }
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
