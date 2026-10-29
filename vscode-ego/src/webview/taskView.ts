import { get } from 'svelte/store';
import { mount } from 'svelte';
import TaskView from './taskView.svelte';
import { taskViewData, checkResult, trainerState } from './shared/store';
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
	if (msg.type === 'trainer.state') trainerState.set(msg.payload.state);
	if (msg.type === 'taskView.setLessonRead') {
		taskViewData.update((data) =>
			data?.lesson && data.id === msg.taskId
				? { ...data, lesson: { ...data.lesson, read: msg.read } }
				: data
		);
	}
	if (msg.type === 'challenge.stageData') {
		// The stage list is already loaded; only the stage on screen changes.
		taskViewData.update((data) =>
			data?.challenge && data.challenge.challenge_id === msg.payload.challenge_id
				? { ...data, challenge: { ...data.challenge, stage: msg.payload.stage } }
				: data
		);
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
