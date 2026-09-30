import { get } from 'svelte/store';
import { mount } from 'svelte';
import TaskView from './taskView.svelte';
import { taskViewData, checkResult } from './shared/store';
import { onHostMessage, postToHost } from './shared/api';

const target = document.getElementById('app');
if (!target) throw new Error('Ego webview: #app not found');
mount(TaskView, { target });

onHostMessage((msg) => {
	if (msg.type === 'taskView.setData') {
		const previousId = get(taskViewData)?.id;
		taskViewData.set(msg.payload);
		// Preserve the latest result when refreshing the same task.
		if (previousId !== msg.payload.id) checkResult.set(null);
	}
	if (msg.type === 'taskView.setResult' || msg.type === 'setResult') {
		checkResult.set(msg.payload);
		// Keep header status badge in sync with latest check.
		taskViewData.update((data) =>
			data && msg.payload?.task_id === data.id
				? { ...data, status: msg.payload.status }
				: data
		);
	}
});

postToHost({ type: 'ready' });
