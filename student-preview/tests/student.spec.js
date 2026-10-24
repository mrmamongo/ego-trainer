import { test, expect } from '@playwright/test';

const tasks = [
  { id: 'V01', task_id: 'V01', title: 'Первая переменная', block: 'variables', slug: 'v01', level: 'start', version: '1.0.0', project_id: 'python', project_name: 'Python с нуля', project_order: 0, folder_id: 'variables', folder_name: 'Переменные', folder_order: 0, theory: ['v-assignment'] },
  { id: 'V02', task_id: 'V02', title: 'Переменные и типы', block: 'variables', slug: 'v02', level: 'start', version: '1.0.0', project_id: 'python', project_name: 'Python с нуля', project_order: 0, folder_id: 'variables', folder_name: 'Переменные', folder_order: 0, theory: ['v-assignment'] },
  { id: 'V03', task_id: 'V03', title: 'Изменяем значение', block: 'variables', slug: 'v03', level: 'start', version: '1.0.0', project_id: 'python', project_name: 'Python с нуля', project_order: 0, folder_id: 'variables', folder_name: 'Переменные', folder_order: 0, theory: [] },
  { id: 'F2', task_id: 'F2', title: 'Аргументы функции', block: 'functions', slug: 'f2', level: 'base', version: '1.0.0', project_id: 'python', project_name: 'Python с нуля', project_order: 0, folder_id: 'functions', folder_name: 'Функции', folder_order: 1, theory: [] },
  { id: 'F10', task_id: 'F10', title: 'Возвращаем результат', block: 'functions', slug: 'f10', level: 'base', version: '1.0.0', project_id: 'python', project_name: 'Python с нуля', project_order: 0, folder_id: 'functions', folder_name: 'Функции', folder_order: 1, theory: [] },
  { id: 'XL-A02', task_id: 'XL-A02', title: 'Сообщения в пределах бюджета', block: 'xl_a', slug: 'xl-a02', level: 'project', version: '1.0.0', project_id: 'xl', project_name: 'XL-A', project_order: 1, folder_id: 'xl_a', folder_name: 'Продуктовые задачи', folder_order: 0, theory: [] },
];
const lesson = { id: 'v-assignment', title: 'Знак = — это команда записи', block: 'variables', project_id: 'python', folder_id: 'variables', order: 1, version: '1.0.0', content_hash: 'hash' };
const lessonBody = `# Знак = — это команда записи\n\n**Переменная** — это имя для значения.\n\n| Строка | x |\n|---|---|\n| 1 | 5 |\n\n## Проверь себя\n\nЧто будет после \`x = 7\`?\n\n<details><summary>Ответ</summary>\n\nВ переменной останется \`7\`. Перейди к [следующей задаче](task:V03).\n\n</details>`;
const egorProgress = [
  { task_id: 'V01', version: '1.0.0', status: 'passed', solution_hash: 'h1', attempts: 1, passed_tests: 3, total_tests: 3, last_run_at: '2026-10-23T10:00:00Z' },
  { task_id: 'V02', version: '1.0.0', status: 'passed', solution_hash: 'h2', attempts: 2, passed_tests: 3, total_tests: 3, last_run_at: '2026-10-24T07:00:00Z' },
  { task_id: 'V03', version: '1.0.0', status: 'failed', solution_hash: 'h3', attempts: 1, passed_tests: 1, total_tests: 3, last_run_at: '2026-10-24T07:10:00Z' },
  { task_id: 'F2', version: '1.0.0', status: 'partial', solution_hash: 'h4', attempts: 1, passed_tests: 2, total_tests: 4, last_run_at: '2026-10-24T07:20:00Z' },
];

async function mockApi(page, { username = 'Егор', progress = egorProgress } = {}) {
  const errors = [];
  page.on('pageerror', (error) => errors.push(error.message));
  await page.route('**/*', async (route) => {
    const request = route.request();
    const url = new URL(request.url());
    if (url.origin !== 'http://127.0.0.1:7100') return route.continue();
    const path = url.pathname;
    const json = (body, status = 200) => route.fulfill({ status, contentType: 'application/json', body: JSON.stringify(body) });
    if (path === '/auth/providers') return json({ local: true, registration: true, forgejo: true });
    if (path === '/auth/login' && request.method() === 'POST') return json({ access_token: 'test-token' });
    if (path === '/auth/me') return json({ id: 'egor', username, role: 'student' });
    if (path === '/tasks') return json(tasks);
    const taskMatch = path.match(/^\/tasks\/([^/]+)$/);
    if (taskMatch) {
      const id = decodeURIComponent(taskMatch[1]);
      const task = tasks.find((item) => item.id === id);
      return task ? json({ ...task, statement_md: `# ${task.title}\n\nНапиши функцию и проверь пример.\n\n\`\`\`python\nx = 5\nx = 7\n\`\`\``, stub_py: 'def solution():\n    pass', solution_py: '' }) : json({ detail: 'Not found' }, 404);
    }
    const hintsMatch = path.match(/^\/tasks\/([^/]+)\/hints$/);
    if (hintsMatch) return json({ hints: [{ level: 1, title: 'Начни с примера', content: 'Посмотри, **как меняется значение**.' }, { level: 2, title: 'Проверь порядок', content: 'Строки выполняются сверху вниз.' }] });
    if (path === '/progress/me') return json(progress);
    if (path === '/progress/me/understanding') return json([{ task_id: 'V01', version: '1.0.0', solution_hash: 'h1', understanding: 'confirmed', created_at: '2026-10-23T10:10:00Z' }]);
    if (path === '/ai/me') return json({ enabled: true, defense_required: true, available: true, reason: 'available', balance_usd: '5' });
    if (path === '/lessons') return json([lesson]);
    if (path === '/lessons/v-assignment') return json({ ...lesson, body_md: lessonBody });
    if (path === '/extension/latest') return json({ version: '0.2.1', download_url: '/extension/download' });
    return route.continue();
  });
  return errors;
}

async function signIn(page) {
  await page.addInitScript(() => localStorage.setItem('ego_student_token', 'test-token'));
}

async function expectNoOverflow(page) {
  const dimensions = await page.evaluate(() => ({ width: window.innerWidth, scroll: document.documentElement.scrollWidth }));
  expect(dimensions.scroll).toBeLessThanOrEqual(dimensions.width);
}

test('guest sees friendly login on desktop and mobile and can sign in', async ({ page }) => {
  const errors = await mockApi(page);
  await page.goto('/student');
  await expect(page.getByRole('heading', { name: 'Рад тебя видеть!' })).toBeVisible();
  await page.screenshot({ path: 'test-results/guest-desktop.png', fullPage: true });
  await page.setViewportSize({ width: 375, height: 812 });
  await expectNoOverflow(page);
  await page.screenshot({ path: 'test-results/guest-mobile.png', fullPage: true });
  await page.getByLabel('Логин').fill('egor');
  await page.getByLabel('Пароль').fill('password');
  await page.getByRole('button', { name: 'Войти →' }).click();
  await expect(page).toHaveURL(/\/student\/tasks\/V02$/);
  await expect(page.locator('.reader-page')).toBeVisible();
  expect(errors).toEqual([]);
});

test('empty progress opens the first task and fits a phone', async ({ page }) => {
  const errors = await mockApi(page, { progress: [] });
  await signIn(page);
  await page.goto('/student');
  await expect(page).toHaveURL(/\/student\/tasks\/V01$/);
  await expect(page.getByRole('heading', { name: 'Первая переменная', exact: true })).toBeVisible();
  await expect(page.locator('.sidebar-progress-head')).toContainText('0 из 6');
  await page.setViewportSize({ width: 375, height: 812 });
  await expectNoOverflow(page);
  await page.screenshot({ path: 'test-results/empty-mobile.png', fullPage: true });
  expect(errors).toEqual([]);
});

test('desktop sidebar selects, searches and opens a clean task page', async ({ page }) => {
  const errors = await mockApi(page);
  await signIn(page);
  await page.goto('/student');
  await expect(page).toHaveURL(/\/student\/tasks\/V02$/);
  await expect(page.locator('#course-sidebar')).toBeVisible();
  await expect(page.locator('[data-task-link="V02"]')).toHaveAttribute('aria-current', 'page');
  const contentBox = await page.locator('#view-content').boundingBox();
  const sidebarBox = await page.locator('#course-sidebar').boundingBox();
  expect(contentBox.x + contentBox.width).toBeLessThan(sidebarBox.x);
  await expect(page.locator('.reader-vscode')).toHaveAttribute('href', 'vscode://ego-trainer.ego-trainer/open?task=V02');
  await expect(page.locator('.reader-statement')).toContainText('Напиши функцию и проверь пример.');
  await expect(page.locator('.task-theory, .attempt-card, .hint-item, .next-card')).toHaveCount(0);
  await page.locator('#sidebar-toggle').click();
  await expect(page.locator('#course-sidebar')).toBeHidden();
  await expect(page.locator('#dashboard')).toHaveClass(/sidebar-collapsed/);
  const expandedBox = await page.locator('#view-content').boundingBox();
  expect(expandedBox.width).toBeGreaterThan(contentBox.width + sidebarBox.width);
  await page.screenshot({ path: 'test-results/task-expanded-desktop.png', fullPage: true });
  await page.locator('#sidebar-toggle').click();
  await expect(page.locator('#course-sidebar')).toBeVisible();
  const folder = page.locator('.sidebar-folder').filter({ hasText: 'Функции' });
  const transition = await folder.evaluate((node) => getComputedStyle(node, '::details-content').transitionProperty);
  expect(transition).toContain('height');
  await folder.locator('summary').click();
  await expect(folder).toHaveAttribute('open', '');
  await folder.locator('summary').click();
  await expect(folder).not.toHaveAttribute('open', '');
  await page.screenshot({ path: 'test-results/task-desktop.png', fullPage: true });
  await page.getByRole('searchbox', { name: 'Поиск по задачам и теории' }).fill('F10');
  await expect(page.locator('#sidebar-catalog .task-link')).toHaveCount(1);
  await expect(page.locator('#sidebar-catalog .task-link .item-title')).toContainText('F10');
  await page.locator('[data-task-link="F10"]').click();
  await expect(page).toHaveURL(/\/student\/tasks\/F10$/);
  await expect(page.getByRole('heading', { name: 'Возвращаем результат', exact: true })).toBeVisible();
  await expect(page.locator('.reader-statement')).toContainText('Напиши функцию и проверь пример.');
  expect(errors).toEqual([]);
});

test('theory opens separately and keeps self-check answers and VS Code guide', async ({ page }) => {
  const errors = await mockApi(page);
  await signIn(page);
  await page.goto('/student/tasks/V02');
  await page.locator('[data-lesson-link="v-assignment"]').click();
  await expect(page).toHaveURL(/\/student\?view=theory&lesson=v-assignment$/);
  await expect(page.getByRole('heading', { name: 'Знак = — это команда записи', exact: true })).toBeVisible();
  await expect(page.locator('[data-lesson-link="v-assignment"]')).toHaveAttribute('aria-current', 'page');
  await expect(page.locator('.reader-statement table')).toHaveCount(1);
  const answer = page.locator('.reader-statement details');
  await answer.locator('summary').click();
  await expect(answer).toHaveAttribute('open', '');
  await expect(answer.getByText(/В переменной останется/)).toBeVisible();
  await page.screenshot({ path: 'test-results/theory-desktop.png', fullPage: true });
  await page.locator('.sidebar-setup').click();
  await expect(page.getByText('Версия 0.2.1')).toBeVisible();
  await expect(page.getByRole('link', { name: 'Скачать расширение ↓' })).toHaveAttribute('href', '/extension/download');
  expect(errors).toEqual([]);
});

test('dark theme persists and keeps the reader usable', async ({ page }) => {
  const errors = await mockApi(page);
  await signIn(page);
  await page.goto('/student/tasks/V02');
  await expect(page.getByRole('heading', { name: 'Переменные и типы', exact: true })).toBeVisible();
  const lightBackground = await page.locator('body').evaluate((node) => getComputedStyle(node).backgroundColor);
  await page.locator('#theme-toggle').click();
  await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark');
  const darkBackground = await page.locator('body').evaluate((node) => getComputedStyle(node).backgroundColor);
  expect(darkBackground).not.toBe(lightBackground);
  await page.screenshot({ path: 'test-results/task-dark-desktop.png', fullPage: true });
  await page.reload();
  await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark');
  await expect(page.getByRole('heading', { name: 'Переменные и типы', exact: true })).toBeVisible();
  await page.setViewportSize({ width: 375, height: 812 });
  await expectNoOverflow(page);
  await page.screenshot({ path: 'test-results/task-dark-mobile.png', fullPage: true, animations: 'disabled' });
  await page.locator('#theme-toggle').click();
  await expect(page.locator('html')).toHaveAttribute('data-theme', 'light');
  expect(errors).toEqual([]);
});

test('mobile drawer closes after task selection and supports Escape', async ({ page }) => {
  const errors = await mockApi(page);
  await signIn(page);
  await page.setViewportSize({ width: 375, height: 812 });
  await page.goto('/student/tasks/V02');
  await expect(page.getByRole('heading', { name: 'Переменные и типы', exact: true })).toBeVisible();
  await expectNoOverflow(page);
  await page.screenshot({ path: 'test-results/task-mobile.png', fullPage: true });
  await page.locator('#sidebar-toggle').click();
  await expect(page.locator('body')).toHaveClass(/sidebar-open/);
  await expect(page.locator('#course-sidebar')).toHaveCSS('transform', 'matrix(1, 0, 0, 1, 0, 0)');
  const drawerBox = await page.locator('#course-sidebar').boundingBox();
  expect(drawerBox.x).toBeGreaterThan(0);
  expect(drawerBox.x + drawerBox.width).toBe(375);
  await page.screenshot({ path: 'test-results/sidebar-mobile.png', fullPage: true, animations: 'disabled' });
  await page.getByRole('searchbox', { name: 'Поиск по задачам и теории' }).fill('F10');
  await page.locator('[data-task-link="F10"]').click();
  await expect(page).toHaveURL(/\/student\/tasks\/F10$/);
  await expect(page.locator('body')).not.toHaveClass(/sidebar-open/);
  await expect(page.getByRole('heading', { name: 'Возвращаем результат', exact: true })).toBeVisible();
  await page.locator('#sidebar-toggle').click();
  await page.keyboard.press('Escape');
  await expect(page.locator('body')).not.toHaveClass(/sidebar-open/);
  await expectNoOverflow(page);
  expect(errors).toEqual([]);
});
