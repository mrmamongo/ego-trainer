import { defineConfig } from 'vite';
import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.dirname(fileURLToPath(import.meta.url));
const staticRoot = path.resolve(root, '../ego_server/static');
const contentTypes = {
  '.css': 'text/css; charset=utf-8', '.js': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8', '.png': 'image/png',
  '.svg': 'image/svg+xml', '.ico': 'image/x-icon',
};

function studentShell() {
  return {
    name: 'cogito-student-shell',
    configureServer(server) {
      server.middlewares.use(async (request, response, next) => {
        if (request.method !== 'GET' && request.method !== 'HEAD') return next();
        const pathname = decodeURIComponent(new URL(request.url, 'http://localhost').pathname);
        try {
          if (pathname.startsWith('/static/')) {
            const file = path.resolve(staticRoot, pathname.slice('/static/'.length));
            if (!file.startsWith(staticRoot + path.sep)) return next();
            const body = await readFile(file);
            response.setHeader('Content-Type', contentTypes[path.extname(file)] || 'application/octet-stream');
            response.setHeader('Cache-Control', 'no-cache');
            response.end(request.method === 'HEAD' ? undefined : body);
            return;
          }
          if (pathname === '/' || pathname === '/student' || pathname === '/student/' || pathname.startsWith('/student/tasks/')) {
            const body = await readFile(path.join(staticRoot, 'student.html'), 'utf8');
            response.setHeader('Content-Type', 'text/html; charset=utf-8');
            response.setHeader('Cache-Control', 'no-store');
            response.end(body);
            return;
          }
        } catch {
          response.statusCode = 404;
          response.end('Not found');
          return;
        }
        next();
      });
    },
  };
}

const proxy = Object.fromEntries(['/auth', '/tasks', '/progress', '/ai', '/lessons', '/extension'].map((prefix) => [prefix, {
  target: 'https://cogito.born-in-july.ru', changeOrigin: true, secure: true,
}]));

export default defineConfig({
  plugins: [studentShell()],
  server: { host: '0.0.0.0', port: 7100, proxy },
});
