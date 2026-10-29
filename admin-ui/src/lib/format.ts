export function relativeTime(value: string | null): string {
  if (!value) return 'Пока нет';
  const timestamp = new Date(value).getTime();
  if (!Number.isFinite(timestamp)) return 'Дата не указана';
  const seconds = Math.round((timestamp - Date.now()) / 1000);
  if (Math.abs(seconds) < 60) return 'Только что';
  const formatter = new Intl.RelativeTimeFormat('ru', { numeric: 'auto' });
  for (const [size, unit] of [[86400, 'day'], [3600, 'hour'], [60, 'minute']] as const) {
    if (Math.abs(seconds) >= size) return formatter.format(Math.round(seconds / size), unit);
  }
  return 'Только что';
}

export function dateTime(value: string | null): string {
  if (!value) return 'Дата не указана';
  const date = new Date(value);
  return Number.isFinite(date.getTime())
    ? new Intl.DateTimeFormat('ru', { dateStyle: 'medium', timeStyle: 'short' }).format(date)
    : 'Дата не указана';
}

export function roleLabel(role: string): string {
  return ({ admin: 'Администратор', mentor: 'Наставник', student: 'Ученик' } as Record<string, string>)[role] || role;
}

export function dollars(value: number | string): string {
  return new Intl.NumberFormat('ru', { style: 'currency', currency: 'USD', minimumFractionDigits: 2, maximumFractionDigits: 6 }).format(Number(value));
}
