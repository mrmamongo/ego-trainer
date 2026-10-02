import { test } from 'node:test';
import assert from 'node:assert/strict';
import { taskIdFromFilePath } from '../taskContext';

test('active task context follows Python task basenames on Windows and remote paths', () => {
    assert.equal(taskIdFromFilePath('C:\\course\\tasks\\block_g\\task_g1.py'), 'G1');
    assert.equal(taskIdFromFilePath('/workspace/tasks/xl/task_xl_a1.py'), 'XL.A1');
    assert.equal(taskIdFromFilePath('/workspace/task_G3.PY'), 'G3');
    for (const path of ['/workspace/task_g1.py/settings.json', '/workspace/task_g1.md',
        '/workspace/backup_task_g1.py', '/workspace/student.py', '/workspace/task_.py']) {
        assert.equal(taskIdFromFilePath(path), undefined);
    }
});
