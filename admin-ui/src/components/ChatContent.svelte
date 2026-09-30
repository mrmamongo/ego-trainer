<script lang="ts">
  let { content }: { content: string } = $props();
  let copied = $state(-1);
  const blocks = $derived(content.split(/(```[\s\S]*?```)/g).filter(Boolean).map((part) => {
    if (!part.startsWith('```') || !part.endsWith('```')) return { code: false, text: part, language: '' };
    const inner = part.slice(3, -3); const match = inner.match(/^([\w+-]*)\n([\s\S]*)$/);
    return { code: true, text: match ? match[2] : inner, language: match ? match[1] : '' };
  }));
  async function copy(text: string, index: number) {
    try { await navigator.clipboard.writeText(text); copied = index; } catch { copied = -1; }
  }
</script>

<div class="chat-content">
  {#each blocks as block, i}
    {#if block.code}
      <div class="code-block"><div class="code-title"><span>{block.language || 'code'}</span><button type="button" onclick={() => copy(block.text, i)}>{copied === i ? 'Скопировано' : 'Копировать код'}</button></div><pre><code>{block.text}</code></pre></div>
    {:else}
      {#each block.text.split(/\n{2,}/).filter(Boolean) as paragraph}
        <p>{#each paragraph.split(/(\*\*[^*]+\*\*|`[^`]+`)/g) as part}{#if part.startsWith('**') && part.endsWith('**')}<strong>{part.slice(2, -2)}</strong>{:else if part.startsWith('`') && part.endsWith('`')}<code>{part.slice(1, -1)}</code>{:else}{part}{/if}{/each}</p>
      {/each}
    {/if}
  {/each}
</div>

<style>
  .chat-content { line-height: 1.7; overflow-wrap: anywhere; }
  p { white-space: pre-wrap; margin: 0 0 .8rem; } p:last-child { margin-bottom: 0; }
  code { font-family: 'Cascadia Code', Consolas, monospace; font-size: .9em; background: #252c34; padding: 2px 5px; border-radius: 4px; }
  .code-block { margin: 14px 0; border: 1px solid #39414c; border-radius: 8px; overflow: hidden; }
  .code-title { display: flex; justify-content: space-between; align-items: center; padding: 6px 10px; background: #252c34; color: #a5b2c2; font-size: 12px; }
  .code-title button { background: transparent; border: 0; padding: 3px 8px; color: inherit; }
  pre { margin: 0; padding: 14px; background: #15191e; overflow-x: auto; white-space: pre; }
  pre code { padding: 0; background: transparent; }
</style>
