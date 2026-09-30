<script lang="ts">
    import { onMount, onDestroy } from 'svelte';
    import { getAISettings, saveAISettings, type AIConfig } from '../api';
    let { onBusyChange = (_value: boolean) => {}, onDirtyChange = (_value: boolean) => {} } = $props();
    onDestroy(() => { onBusyChange(false); onDirtyChange(false); });
    let config = $state<AIConfig | null>(null);
    let error = $state('');
    let saved = $state(false);
    let busy = $state(false);
    let mainKey = $state('');
    let guardKey = $state('');
    onMount(() => { getAISettings().then((value) => config = value).catch((e) => error = e.message); });
    async function save(event: SubmitEvent) {
        event.preventDefault();
        if (!config) return;
        busy = true; onBusyChange(true); error = ''; saved = false;
        try {
            config = await saveAISettings({ ...config,
                main: { ...config.main, ...(mainKey ? { api_key: mainKey } : {}) },
                guard: { ...config.guard, ...(guardKey ? { api_key: guardKey } : {}) },
            });
            mainKey = ''; guardKey = ''; saved = true; onDirtyChange(false);
        } catch (e) { error = (e as Error).message; }
        finally { busy = false; onBusyChange(false); }
    }
</script>

<section>
    <h2>Настройки студенческого ассистента</h2>
    <p>Проверяющая модель проверяет каждый ответ до показа студенту. Изменения применяются к следующим запросам.</p>
    {#if error}<p class="error" role="alert">{error}</p>{/if}
    {#if saved}<p class="ok" role="status">Настройки сохранены</p>{/if}
    {#if config}
        <form onsubmit={save} oninput={() => { saved = false; onDirtyChange(true); }}>
            <label><input type="checkbox" bind:checked={config.enabled} /> Включить ассистента на сервере</label>
            {#each ['main', 'guard'] as name}
                {@const model = name === 'main' ? config.main : config.guard}
                <fieldset>
                    <legend>{name === 'main' ? 'Основная модель' : 'Проверяющая модель'}</legend>
                    <label>Адрес API (включая /v1)<input type="url" bind:value={model.base_url} placeholder="https://gateway.example/v1" /></label>
                    <label>Model ID<input bind:value={model.model} /></label>
                    <label>API-ключ {model.api_key_set ? '(сохранён)' : '(не задан)'}
                        {#if name === 'main'}<input type="password" bind:value={mainKey} autocomplete="new-password" />
                        {:else}<input type="password" bind:value={guardKey} autocomplete="new-password" />{/if}
                    </label>
                    <small>Пустое поле сохраняет текущий ключ.</small>
                    <label>USD за миллион входных токенов<input type="number" min="0" step="any" bind:value={model.input_usd_per_million} required /></label>
                    <label>USD за миллион выходных токенов<input type="number" min="0" step="any" bind:value={model.output_usd_per_million} required /></label>
                    <label>Максимум выходных токенов<input type="number" min="128" max="4096" bind:value={model.max_output_tokens} required /></label>
                    <label><input type="checkbox" bind:checked={model.json_mode} /> API поддерживает JSON mode</label>
                </fieldset>
            {/each}
            <button disabled={busy} type="submit">{busy ? 'Сохраняю…' : 'Сохранить'}</button>
        </form>
    {:else}<p>Загружаю настройки…</p>{/if}
</section>

<style>
    section { margin: 24px 0; } fieldset { border: 1px solid #3c3c3c; margin: 20px 0; padding: 16px; }
    label { display: block; margin: 12px 0; } input:not([type=checkbox]) { box-sizing: border-box; display: block; width: 100%; margin-top: 6px; padding: 8px; background: #252526; color: #d4d4d4; border: 1px solid #555; border-radius: 4px; }
    button { padding: 8px 16px; background: #007acc; color: white; border: 0; border-radius: 4px; cursor: pointer; } button:disabled { opacity: .5; } .error { color: #f87171; } .ok { color: #22c55e; } small { color: #aaa; }
</style>
