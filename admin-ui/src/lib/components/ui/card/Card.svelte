<!-- Adapted from shadcn-svelte (MIT): https://www.shadcn-svelte.com/docs/components/card -->
<script lang="ts">
  import { cn, type WithElementRef } from '../../../utils';
  import type { HTMLAttributes } from 'svelte/elements';
  let { ref = $bindable(null), class: className, children, ...rest }:
    WithElementRef<HTMLAttributes<HTMLDivElement>, HTMLDivElement> = $props();
</script>
<div bind:this={ref} data-slot="card" class={cn('flex flex-col gap-6 rounded-xl border border-border bg-card text-card-foreground shadow-sm', className)} {...rest}>
  {@render children?.()}
</div>
