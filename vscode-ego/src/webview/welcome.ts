import { mount } from 'svelte';
import Welcome from './welcome.svelte';
import { postToHost } from './shared/api';

const target = document.getElementById('app');
if (!target) throw new Error('Ego webview: #app not found');
mount(Welcome, { target });
postToHost({ type: 'ready' });
