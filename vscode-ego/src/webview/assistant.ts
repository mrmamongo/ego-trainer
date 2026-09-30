import { mount } from 'svelte';
import Assistant from './assistant.svelte';

const target = document.getElementById('app');
if (!target) throw new Error('Ego assistant: #app not found');
mount(Assistant, { target });
