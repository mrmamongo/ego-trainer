<script lang="ts">
	import { postToHost } from './shared/api';

	function connect() {
		postToHost({ type: 'welcome.connect' });
	}

	function offline() {
		postToHost({ type: 'welcome.offline' });
	}

	function skip() {
		postToHost({ type: 'welcome.skip' });
	}
</script>

<main class="welcome">
	<div class="atmosphere" aria-hidden="true"></div>

	<section class="compose">
		<h1 class="brand">Ego Trainer</h1>
		<p class="lede">
			Practice coding tasks with auto-checking — connect to a server or work offline.
		</p>

		<div class="actions">
			<button type="button" class="btn primary" onclick={connect}>Connect to Server</button>
			<button type="button" class="btn primary" onclick={offline}>Use Offline</button>
			<button type="button" class="btn quiet" onclick={skip}>Skip for now</button>
		</div>
	</section>
</main>

<style>
	:global(html),
	:global(body) {
		margin: 0;
		height: 100%;
		font-family: var(--vscode-font-family, 'Segoe UI', sans-serif);
		color: var(--vscode-foreground);
		background: var(--vscode-editor-background);
	}

	:global(#app) {
		height: 100%;
	}

	.welcome {
		position: relative;
		isolation: isolate;
		display: flex;
		align-items: center;
		justify-content: center;
		min-height: 100%;
		box-sizing: border-box;
		padding: 2.5rem 1.5rem;
		overflow: hidden;
	}

	.atmosphere {
		position: absolute;
		inset: 0;
		z-index: -1;
		pointer-events: none;
		background:
			radial-gradient(
				ellipse 80% 55% at 50% 0%,
				color-mix(in srgb, var(--vscode-button-background) 18%, transparent),
				transparent 70%
			),
			radial-gradient(
				ellipse 55% 45% at 15% 90%,
				color-mix(in srgb, var(--vscode-focusBorder, var(--vscode-button-background)) 12%, transparent),
				transparent 65%
			),
			radial-gradient(
				ellipse 50% 40% at 90% 75%,
				color-mix(in srgb, var(--vscode-editor-selectionBackground, var(--vscode-button-background)) 14%, transparent),
				transparent 60%
			),
			linear-gradient(
				165deg,
				var(--vscode-editor-background) 0%,
				color-mix(in srgb, var(--vscode-sideBar-background, var(--vscode-editor-background)) 70%, var(--vscode-editor-background)) 100%
			);
		animation: atmosphere-drift 14s ease-in-out infinite alternate;
	}

	.compose {
		width: min(28rem, 100%);
		text-align: center;
		animation: compose-in 0.55s ease-out both;
	}

	.brand {
		margin: 0;
		font-size: clamp(2.25rem, 6vw, 3rem);
		font-weight: 700;
		letter-spacing: -0.03em;
		line-height: 1.1;
		color: var(--vscode-foreground);
		animation: brand-rise 0.7s ease-out both;
	}

	.lede {
		margin: 1rem 0 0;
		font-size: 0.95rem;
		line-height: 1.5;
		opacity: 0.82;
		animation: brand-rise 0.7s ease-out 0.08s both;
	}

	.actions {
		display: flex;
		flex-direction: column;
		gap: 0.65rem;
		margin-top: 2rem;
		animation: brand-rise 0.7s ease-out 0.16s both;
	}

	.btn {
		appearance: none;
		border: 1px solid transparent;
		border-radius: 2px;
		padding: 0.65rem 1rem;
		font: inherit;
		font-size: 0.9rem;
		cursor: pointer;
		transition:
			background-color 0.12s ease,
			border-color 0.12s ease,
			opacity 0.12s ease;
	}

	.btn:focus-visible {
		outline: 1px solid var(--vscode-focusBorder, var(--vscode-button-background));
		outline-offset: 2px;
	}

	.btn.primary {
		background: var(--vscode-button-background);
		color: var(--vscode-button-foreground);
	}

	.btn.primary:hover {
		background: var(--vscode-button-hoverBackground, var(--vscode-button-background));
	}

	.btn.quiet {
		background: transparent;
		color: var(--vscode-descriptionForeground, var(--vscode-foreground));
		border-color: color-mix(in srgb, var(--vscode-foreground) 18%, transparent);
		opacity: 0.85;
	}

	.btn.quiet:hover {
		background: var(--vscode-button-secondaryBackground, color-mix(in srgb, var(--vscode-foreground) 8%, transparent));
		color: var(--vscode-button-secondaryForeground, var(--vscode-foreground));
		opacity: 1;
	}

	@keyframes compose-in {
		from {
			opacity: 0;
		}
		to {
			opacity: 1;
		}
	}

	@keyframes brand-rise {
		from {
			opacity: 0;
			transform: translateY(0.4rem);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}

	@keyframes atmosphere-drift {
		from {
			transform: scale(1);
		}
		to {
			transform: scale(1.04);
		}
	}

	@media (prefers-reduced-motion: reduce) {
		.atmosphere,
		.compose,
		.brand,
		.lede,
		.actions {
			animation: none;
		}
	}
</style>
