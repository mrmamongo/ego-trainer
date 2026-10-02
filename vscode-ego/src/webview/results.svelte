<script lang="ts">
	import { checkResult } from './shared/store';
	import ResultsBody from './ResultsBody.svelte';
</script>

<ResultsBody result={$checkResult} emptyMessage="Waiting for results…" />

<style>
	:global(body) {
		font-family: 'JetBrains Mono', 'Cascadia Code', 'Fira Code', 'Consolas', 'Courier New', monospace;
		padding: 16px;
		margin: 0;
		color: var(--vscode-foreground, #333);
		background: var(--vscode-editor-background, #fff);
	}
</style>
