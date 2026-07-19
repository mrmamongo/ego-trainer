import { writable } from 'svelte/store';
import type { CheckResult, DashboardData } from './types';

export const checkResult = writable<CheckResult | null>(null);
export const dashboardData = writable<DashboardData | null>(null);
