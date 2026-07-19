import { mount } from 'svelte';
import TaskView from './taskView.svelte';
import { taskViewData, checkResult } from './shared/store';
import { onHostMessage, postToHost } from './shared/api';

const target = document.getElementById('app');
if (!target) throw new Error('Ego webview: #app not found');
mount(TaskView, { target });

onHostMessage((msg) => {
	if (msg.type === 'taskView.setData') {
		taskViewData.set(msg.payload);
		// reset results when switching task
		checkResult.set(null);
	}
	if (msg.type === 'taskView.setResult' || msg.type === 'setResult') {
		checkResult.set(msg.payload);
	}
});

postToHost({ type: 'ready' });
