import { mount } from 'svelte';
import Dashboard from './dashboard.svelte';
import { dashboardData } from './shared/store';
import { onHostMessage, postToHost } from './shared/api';

const target = document.getElementById('app');
if (!target) throw new Error('Ego webview: #app not found');
mount(Dashboard, { target });

onHostMessage((msg) => {
	if (msg.type === 'dashboard.setData') {
		dashboardData.set(msg.payload);
	}
});

postToHost({ type: 'ready' });
