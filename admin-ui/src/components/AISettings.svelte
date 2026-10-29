<script lang="ts">
    import { onMount, onDestroy } from 'svelte';
    import { getAISettings, saveAISettings, type AIConfig } from '../api';
    import Button from '../lib/components/ui/button/Button.svelte';
    import Card from '../lib/components/ui/card/Card.svelte';
    import Icon from '../lib/Icon.svelte';
    let { onBusyChange = (_value: boolean) => {}, onDirtyChange = (_value: boolean) => {} } = $props();
    onDestroy(() => { onBusyChange(false); onDirtyChange(false); });
    let config = $state<AIConfig | null>(null);
    let error = $state('');
    let saved = $state(false);
    let busy = $state(false);
    let dirty = $state(false);
    let mainKey = $state('');
    let guardKey = $state('');
    async function load() { error = ''; try { config = await getAISettings(); } catch (failure) { error = (failure as Error).message; } }
    onMount(() => { void load(); });
    function changed() { saved = false; dirty = true; onDirtyChange(true); }
    async function save(event: SubmitEvent) {
        event.preventDefault();
        if (!config) return;
        busy = true; onBusyChange(true); error = ''; saved = false;
        try {
            config = await saveAISettings({ ...config,
                main: { ...config.main, ...(mainKey ? { api_key: mainKey } : {}) },
                guard: { ...config.guard, ...(guardKey ? { api_key: guardKey } : {}) },
            });
            mainKey = ''; guardKey = ''; saved = true; dirty = false; onDirtyChange(false);
        } catch (e) { error = (e as Error).message; }
        finally { busy = false; onBusyChange(false); }
    }
</script>

<section class="admin-stack">
  <div class="admin-section-head"><div><h2>Помощь и проверка понимания</h2><p class="admin-subtitle">Основная модель ведёт диалог. Проверяющая оценивает каждый ответ перед показом ученику.</p></div><span class="admin-badge" class:success={!!config?.enabled}>{config?.enabled ? 'Включён' : 'Выключен'}</span></div>
  {#if error}<div class="admin-notice error" role="alert">{error}</div>{/if}
  {#if saved}<div class="admin-notice success" role="status">Настройки сохранены. Они применятся к следующим запросам.</div>{/if}
  {#if config}
    <form class="admin-stack" onsubmit={save} oninput={changed}>
      <fieldset disabled={busy} class="ai-fields admin-stack">
        <div class="admin-panel"><label class="admin-toggle"><input type="checkbox" bind:checked={config.enabled} /><span><strong>Включить учебного ассистента</strong><small>Доступ и бюджет для каждого ученика настраиваются в его профиле.</small></span></label></div>
        <div class="models-grid">
          {#each ['main', 'guard'] as name}
            {@const model = name === 'main' ? config.main : config.guard}
            <Card class="gap-6 p-6">
              <div class="model-heading"><span class="model-icon"><Icon name={name === 'main' ? 'ai' : 'shield'} size={20} /></span><div><h3>{name === 'main' ? 'Основная модель' : 'Проверяющая модель'}</h3><p>{name === 'main' ? 'Подсказки, объяснения и диалог о решении' : 'Проверка ответа перед выдачей ученику'}</p></div></div>
              <label class="admin-field">Адрес API<input type="url" bind:value={model.base_url} placeholder="https://gateway.example/v1" /><small>Укажи базовый адрес, включая /v1, если его требует провайдер.</small></label>
              <label class="admin-field">Идентификатор модели<input bind:value={model.model} placeholder="Точное название у провайдера" /></label>
              <label class="admin-field"><span class="key-label">API-ключ<span class="admin-badge">{model.api_key_set ? 'Сохранён' : 'Не задан'}</span></span>
                {#if name === 'main'}<input type="password" bind:value={mainKey} autocomplete="new-password" placeholder={model.api_key_set ? 'Оставь пустым, чтобы сохранить ключ' : 'Ключ доступа провайдера'} />
                {:else}<input type="password" bind:value={guardKey} autocomplete="new-password" placeholder={model.api_key_set ? 'Оставь пустым, чтобы сохранить ключ' : 'Ключ доступа провайдера'} />{/if}
                <small>Пустое поле сохраняет текущий ключ.</small>
              </label>
              <div class="pricing"><h4>Стоимость за миллион токенов</h4><div class="price-fields"><label class="admin-field">Вход, USD<input type="number" min="0" step="any" bind:value={model.input_usd_per_million} required /></label><label class="admin-field">Выход, USD<input type="number" min="0" step="any" bind:value={model.output_usd_per_million} required /></label></div></div>
              <details class="model-options"><summary>Параметры ответа</summary><div><label class="admin-field">Максимум выходных токенов<input type="number" min="128" max="4096" bind:value={model.max_output_tokens} required /></label><label class="admin-toggle"><input type="checkbox" bind:checked={model.json_mode} /><span>API поддерживает JSON mode</span></label></div></details>
            </Card>
          {/each}
        </div>
      </fieldset>
      <div class="admin-save-bar"><p>{dirty ? 'Есть несохранённые изменения' : 'Настройки моделей применяются к новым запросам'}</p><Button disabled={busy || !dirty} type="submit">{busy ? 'Сохраняю…' : 'Сохранить настройки'}</Button></div>
    </form>
  {:else if error}<div><Button variant="outline" onclick={load}>Повторить загрузку</Button></div>
  {:else}<div class="admin-state" role="status">Загружаю настройки ассистента…</div>{/if}
</section>

<style>
  .ai-fields { min-width: 0; margin: 0; padding: 0; border: 0; }
  .models-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 20px; }
  .model-heading { display: flex; align-items: flex-start; gap: 12px; }
  .model-icon { width: 40px; height: 40px; flex-shrink: 0; display: grid; place-items: center; border: 1px solid var(--border); border-radius: 10px; background: var(--secondary); color: var(--muted-foreground); }
  h3 { margin: 0; font-size: 16px; font-weight: 600; letter-spacing: -.02em; }
  .model-heading p { margin: 4px 0 0; color: var(--muted-foreground); font-size: 12px; line-height: 1.6; }
  .key-label { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
  .key-label .admin-badge { font-size: 10px; padding: 2px 7px; }
  .pricing { padding-top: 20px; border-top: 1px solid var(--border); }
  h4 { margin: 0 0 14px; font-size: 12px; font-weight: 500; color: var(--muted-foreground); }
  .price-fields { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; }
  .model-options { padding-top: 20px; border-top: 1px solid var(--border); }
  summary { font-size: 13px; cursor: pointer; }
  .model-options > div { display: grid; gap: 18px; margin-top: 20px; }
  @media (max-width: 1000px) { .models-grid { grid-template-columns: 1fr; } }
</style>
