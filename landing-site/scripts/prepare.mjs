import { copyFileSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const staticDir = join(root, '..', 'ego_server', 'static');
const brand = JSON.parse(readFileSync(join(staticDir, 'branding', 'brand.json'), 'utf8'));
const forgejoUrl = 'https://git.born-in-july.ru';
let html = readFileSync(join(staticDir, 'landing.html'), 'utf8');
const values = {
  BRAND_NAME: brand.name,
  BRAND_DESCRIPTION: brand.description,
  BRAND_MARK: brand.mark,
  BRAND_LOGO_URL: brand.logo_url,
  FORGEJO_URL: forgejoUrl,
};
for (const [key, value] of Object.entries(values)) {
  html = html.replaceAll(`{{${key}}}`, value);
}
writeFileSync(join(root, 'index.html'), html);
mkdirSync(join(root, 'public', 'static', 'branding'), { recursive: true });
for (const file of ['favicon.ico', 'cogito-mark.png', 'cogito-logo.png']) {
  copyFileSync(join(staticDir, 'branding', file), join(root, 'public', 'static', 'branding', file));
}
