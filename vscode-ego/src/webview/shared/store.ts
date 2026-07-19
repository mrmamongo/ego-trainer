import { writable } from 'svelte/store';
import type { CheckResult, DashboardData, TaskViewData } from './types';

export const checkResult = writable<CheckResult | null>(null);
export const dashboardData = writable<DashboardData | null>(null);
export const taskViewData = writable<TaskViewData | null>(null);
