import { writable } from 'svelte/store';
import type { CheckResult } from './types';

export const checkResult = writable<CheckResult | null>(null);
