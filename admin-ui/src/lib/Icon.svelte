<script lang="ts">
  let { name, size = 20 }: { name: string; size?: number } = $props();
  const paths: Record<string, string[]> = {
    overview: ['M3 3h7v7H3z M14 3h7v7h-7z M3 14h7v7H3z M14 14h7v7h-7z'],
    users: ['M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2 M20 8a4 4 0 0 1 0 8 M22 21v-2a4 4 0 0 0-3-3.87', 'M13 7a4 4 0 1 1-8 0 4 4 0 0 1 8 0'],
    catalog: ['M3 7V5a2 2 0 0 1 2-2h5l2 3h7a2 2 0 0 1 2 2v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7z', 'M7 11h10 M7 15h7'],
    ai: ['m12 3 2.7 6.3L21 12l-6.3 2.7L12 21l-2.7-6.3L3 12l6.3-2.7L12 3z'],
    settings: ['M4 6h5 M13 6h7 M4 12h9 M17 12h3 M4 18h2 M10 18h10', 'M9 3v6 M17 9v6 M6 15v6'],
    logout: ['M9 4H5a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h4 M13 8l4 4-4 4 M8 12h13'],
    arrow: ['M5 12h14 M13 6l6 6-6 6'],
    back: ['M19 12H5 M11 6l-6 6 6 6'],
    refresh: ['M20 7v5h-5 M4 17v-5h5', 'M6 7a7 7 0 0 1 11-2l3 3 M18 17a7 7 0 0 1-11 2l-3-3'],
    check: ['m5 12 4 4L19 6'],
    plus: ['M12 5v14 M5 12h14'],
    book: ['M4 3h12a3 3 0 0 1 3 3v15H7a3 3 0 0 1-3-3V3z M4 17h15 M8 7h7 M8 11h5'],
    shield: ['M12 3 3 7v5c0 5 9 9 9 9s9-4 9-9V7l-9-4z', 'm8 12 3 3 5-6'],
  };
</script>

<svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">
  {#each paths[name] || paths.overview as path}<path d={path} />{/each}
</svg>
