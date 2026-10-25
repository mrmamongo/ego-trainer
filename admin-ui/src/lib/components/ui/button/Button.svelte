<!-- Adapted from shadcn-svelte (MIT): https://www.shadcn-svelte.com/docs/components/button -->
<script lang="ts" module>
  import { tv, type VariantProps } from 'tailwind-variants';
  import { cn, type WithElementRef } from '../../../utils';
  import type { HTMLAnchorAttributes, HTMLButtonAttributes } from 'svelte/elements';

  export const buttonVariants = tv({
    base: 'inline-flex shrink-0 items-center justify-center gap-2 whitespace-nowrap rounded-md border border-transparent text-sm font-medium transition-colors outline-none focus-visible:border-ring focus-visible:ring-2 focus-visible:ring-ring/50 disabled:pointer-events-none disabled:opacity-50',
    variants: {
      variant: {
        default: 'bg-primary text-primary-foreground hover:bg-primary/90',
        outline: 'border-border bg-background text-foreground hover:bg-muted',
        secondary: 'bg-secondary text-secondary-foreground hover:bg-secondary/80',
        ghost: 'text-muted-foreground hover:bg-muted hover:text-foreground',
        destructive: 'bg-destructive/10 text-destructive hover:bg-destructive/20',
        link: 'text-primary underline-offset-4 hover:underline'
      },
      size: { default: 'h-9 px-4 py-2', sm: 'h-8 px-3 text-xs', icon: 'size-9' }
    },
    defaultVariants: { variant: 'default', size: 'default' }
  });
  export type ButtonProps = WithElementRef<HTMLButtonAttributes & HTMLAnchorAttributes> & {
    variant?: VariantProps<typeof buttonVariants>['variant'];
    size?: VariantProps<typeof buttonVariants>['size'];
  };
</script>
<script lang="ts">
  let { class: className, variant = 'default', size = 'default', ref = $bindable(null),
    href, type = 'button', disabled, children, ...rest }: ButtonProps = $props();
</script>
{#if href}
  <a bind:this={ref} data-slot="button" class={cn(buttonVariants({ variant, size }), className)}
    href={disabled ? undefined : href} aria-disabled={disabled} tabindex={disabled ? -1 : undefined} {...rest}>
    {@render children?.()}
  </a>
{:else}
  <button bind:this={ref} data-slot="button" class={cn(buttonVariants({ variant, size }), className)} {type} {disabled} {...rest}>
    {@render children?.()}
  </button>
{/if}
