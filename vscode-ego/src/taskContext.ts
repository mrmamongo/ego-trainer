/** Match only task file basenames; directory names cannot select a task. */
export function taskIdFromFilePath(path: string): string | undefined {
    const filename = path.replace(/\\/g, '/').split('/').pop() || '';
    return filename.match(/^task_([a-z0-9_]+)\.py$/i)?.[1].replace(/_/g, '.').toUpperCase();
}
