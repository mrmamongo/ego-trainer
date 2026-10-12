import { mount } from 'svelte';
import IdeApp from './IdeApp.svelte';

const target = document.getElementById('app');
if (!target) throw new Error('#app not found');
mount(IdeApp, { target });
