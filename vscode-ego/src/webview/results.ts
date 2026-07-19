import { mount } from 'svelte';
import Results from './results.svelte';
import { checkResult } from './shared/store';
import { onHostMessage, postToHost } from './shared/api';

const target = document.getElementById('app');
if (!target) {
	throw new Error('Ego webview: #app not found');
}

mount(Results, { target });

onHostMessage((msg) => {
	if (msg.type === 'setResult') {
		checkResult.set(msg.payload);
	}
});

postToHost({ type: 'ready' });
