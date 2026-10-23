import { writable } from 'svelte/store';
import type { CheckResult, DashboardData, TaskViewData, TrainerState } from './types';

export const checkResult = writable<CheckResult | null>(null);
export const dashboardData = writable<DashboardData | null>(null);
export const taskViewData = writable<TaskViewData | null>(null);
/** Latest trainer state from `trainer.state` (null until loaded / unsupported). */
export const trainerState = writable<TrainerState | null>(null);
