(() => {
  // node_modules/esm-env/dev-fallback.js
  var node_env = globalThis.process?.env?.NODE_ENV;
  var dev_fallback_default = node_env && !node_env.toLowerCase().startsWith("prod");

  // node_modules/svelte/src/internal/shared/utils.js
  var is_array = Array.isArray;
  var index_of = Array.prototype.indexOf;
  var includes = Array.prototype.includes;
  var array_from = Array.from;
  var object_keys = Object.keys;
  var define_property = Object.defineProperty;
  var get_descriptor = Object.getOwnPropertyDescriptor;
  var get_descriptors = Object.getOwnPropertyDescriptors;
  var object_prototype = Object.prototype;
  var array_prototype = Array.prototype;
  var get_prototype_of = Object.getPrototypeOf;
  var is_extensible = Object.isExtensible;
  var noop = () => {
  };
  function run_all(arr) {
    for (var i = 0; i < arr.length; i++) {
      arr[i]();
    }
  }
  function deferred() {
    var resolve;
    var reject;
    var promise = new Promise((res, rej) => {
      resolve = res;
      reject = rej;
    });
    return { promise, resolve, reject };
  }
  function to_array(value, n) {
    if (Array.isArray(value)) {
      return value;
    }
    if (n === void 0 || !(Symbol.iterator in value)) {
      return Array.from(value);
    }
    const array = [];
    for (const element2 of value) {
      array.push(element2);
      if (array.length === n) break;
    }
    return array;
  }

  // node_modules/svelte/src/internal/client/constants.js
  var DERIVED = 1 << 1;
  var EFFECT = 1 << 2;
  var RENDER_EFFECT = 1 << 3;
  var MANAGED_EFFECT = 1 << 24;
  var BLOCK_EFFECT = 1 << 4;
  var BRANCH_EFFECT = 1 << 5;
  var ROOT_EFFECT = 1 << 6;
  var BOUNDARY_EFFECT = 1 << 7;
  var PAUSED = 1 << 8;
  var CONNECTED = 1 << 9;
  var CLEAN = 1 << 10;
  var DIRTY = 1 << 11;
  var MAYBE_DIRTY = 1 << 12;
  var INERT = 1 << 13;
  var DESTROYED = 1 << 14;
  var REACTION_RAN = 1 << 15;
  var DESTROYING = 1 << 25;
  var EFFECT_TRANSPARENT = 1 << 16;
  var EAGER_EFFECT = 1 << 17;
  var HEAD_EFFECT = 1 << 18;
  var EFFECT_PRESERVED = 1 << 19;
  var USER_EFFECT = 1 << 20;
  var EFFECT_OFFSCREEN = 1 << 25;
  var WAS_MARKED = 1 << 16;
  var REACTION_IS_UPDATING = 1 << 21;
  var ASYNC = 1 << 22;
  var ERROR_VALUE = 1 << 23;
  var STATE_SYMBOL = /* @__PURE__ */ Symbol("$state");
  var COMPONENT_SYMBOL = /* @__PURE__ */ Symbol("component");
  var LEGACY_PROPS = /* @__PURE__ */ Symbol("legacy props");
  var LOADING_ATTR_SYMBOL = /* @__PURE__ */ Symbol("");
  var PROXY_PATH_SYMBOL = /* @__PURE__ */ Symbol("proxy path");
  var ATTRIBUTES_CACHE = /* @__PURE__ */ Symbol("attributes");
  var CLASS_CACHE = /* @__PURE__ */ Symbol("class");
  var STYLE_CACHE = /* @__PURE__ */ Symbol("style");
  var TEXT_CACHE = /* @__PURE__ */ Symbol("text");
  var FORM_RESET_HANDLER = /* @__PURE__ */ Symbol("form reset");
  var HMR_ANCHOR = /* @__PURE__ */ Symbol("hmr anchor");
  var STALE_REACTION = new class StaleReactionError extends Error {
    name = "StaleReactionError";
    message = "The reaction that called `getAbortSignal()` was re-run or destroyed";
  }();
  var IS_XHTML = (
    // We gotta write it like this because after downleveling the pure comment may end up in the wrong location
    !!globalThis.document?.contentType && /* @__PURE__ */ globalThis.document.contentType.includes("xml")
  );
  var TEXT_NODE = 3;
  var COMMENT_NODE = 8;

  // node_modules/svelte/src/constants.js
  var EACH_ITEM_REACTIVE = 1;
  var EACH_INDEX_REACTIVE = 1 << 1;
  var EACH_IS_CONTROLLED = 1 << 2;
  var EACH_IS_ANIMATED = 1 << 3;
  var EACH_ITEM_IMMUTABLE = 1 << 4;
  var PROPS_IS_IMMUTABLE = 1;
  var PROPS_IS_RUNES = 1 << 1;
  var PROPS_IS_UPDATED = 1 << 2;
  var PROPS_IS_BINDABLE = 1 << 3;
  var PROPS_IS_LAZY_INITIAL = 1 << 4;
  var TRANSITION_OUT = 1 << 1;
  var TRANSITION_GLOBAL = 1 << 2;
  var TEMPLATE_FRAGMENT = 1;
  var TEMPLATE_USE_IMPORT_NODE = 1 << 1;
  var TEMPLATE_USE_SVG = 1 << 2;
  var TEMPLATE_USE_MATHML = 1 << 3;
  var HYDRATION_START = "[";
  var HYDRATION_START_ELSE = "[!";
  var HYDRATION_START_FAILED = "[?";
  var HYDRATION_END = "]";
  var HYDRATION_ERROR = {};
  var ELEMENT_PRESERVE_ATTRIBUTE_CASE = 1 << 1;
  var ELEMENT_IS_INPUT = 1 << 2;
  var UNINITIALIZED = /* @__PURE__ */ Symbol("uninitialized");
  var FILENAME = /* @__PURE__ */ Symbol("filename");
  var NAMESPACE_HTML = "http://www.w3.org/1999/xhtml";

  // node_modules/svelte/src/internal/client/warnings.js
  var bold = "font-weight: bold";
  var normal = "font-weight: normal";
  function await_reactivity_loss(name) {
    if (dev_fallback_default) {
      console.warn(`%c[svelte] await_reactivity_loss
%cDetected reactivity loss when reading \`${name}\`. This happens when state is read in an async function after an earlier \`await\`
https://svelte.dev/e/await_reactivity_loss`, bold, normal);
    } else {
      console.warn(`https://svelte.dev/e/await_reactivity_loss`);
    }
  }
  function await_waterfall(name, location2) {
    if (dev_fallback_default) {
      console.warn(`%c[svelte] await_waterfall
%cAn async derived, \`${name}\` (${location2}) was not read immediately after it resolved. This often indicates an unnecessary waterfall, which can slow down your app
https://svelte.dev/e/await_waterfall`, bold, normal);
    } else {
      console.warn(`https://svelte.dev/e/await_waterfall`);
    }
  }
  function derived_inert() {
    if (dev_fallback_default) {
      console.warn(`%c[svelte] derived_inert
%cReading a derived belonging to a now-destroyed effect may result in stale values
https://svelte.dev/e/derived_inert`, bold, normal);
    } else {
      console.warn(`https://svelte.dev/e/derived_inert`);
    }
  }
  function hydration_attribute_changed(attribute, html2, value) {
    if (dev_fallback_default) {
      console.warn(`%c[svelte] hydration_attribute_changed
%cThe \`${attribute}\` attribute on \`${html2}\` changed its value between server and client renders. The client value, \`${value}\`, will be ignored in favour of the server value
https://svelte.dev/e/hydration_attribute_changed`, bold, normal);
    } else {
      console.warn(`https://svelte.dev/e/hydration_attribute_changed`);
    }
  }
  function hydration_mismatch(location2) {
    if (dev_fallback_default) {
      console.warn(
        `%c[svelte] hydration_mismatch
%c${location2 ? `Hydration failed because the initial UI does not match what was rendered on the server. The error occurred near ${location2}` : "Hydration failed because the initial UI does not match what was rendered on the server"}
https://svelte.dev/e/hydration_mismatch`,
        bold,
        normal
      );
    } else {
      console.warn(`https://svelte.dev/e/hydration_mismatch`);
    }
  }
  function lifecycle_double_unmount() {
    if (dev_fallback_default) {
      console.warn(`%c[svelte] lifecycle_double_unmount
%cTried to unmount a component that was not mounted
https://svelte.dev/e/lifecycle_double_unmount`, bold, normal);
    } else {
      console.warn(`https://svelte.dev/e/lifecycle_double_unmount`);
    }
  }
  function select_multiple_invalid_value() {
    if (dev_fallback_default) {
      console.warn(`%c[svelte] select_multiple_invalid_value
%cThe \`value\` property of a \`<select multiple>\` element should be an array, but it received a non-array value. The selection will be kept as is.
https://svelte.dev/e/select_multiple_invalid_value`, bold, normal);
    } else {
      console.warn(`https://svelte.dev/e/select_multiple_invalid_value`);
    }
  }
  function state_proxy_equality_mismatch(operator) {
    if (dev_fallback_default) {
      console.warn(`%c[svelte] state_proxy_equality_mismatch
%cReactive \`$state(...)\` proxies and the values they proxy have different identities. Because of this, comparisons with \`${operator}\` will produce unexpected results
https://svelte.dev/e/state_proxy_equality_mismatch`, bold, normal);
    } else {
      console.warn(`https://svelte.dev/e/state_proxy_equality_mismatch`);
    }
  }
  function svelte_boundary_reset_noop() {
    if (dev_fallback_default) {
      console.warn(`%c[svelte] svelte_boundary_reset_noop
%cA \`<svelte:boundary>\` \`reset\` function only resets the boundary the first time it is called
https://svelte.dev/e/svelte_boundary_reset_noop`, bold, normal);
    } else {
      console.warn(`https://svelte.dev/e/svelte_boundary_reset_noop`);
    }
  }

  // node_modules/svelte/src/internal/client/dom/hydration.js
  var hydrating = false;
  function set_hydrating(value) {
    hydrating = value;
  }
  var hydrate_node;
  function set_hydrate_node(node) {
    if (node === null) {
      hydration_mismatch();
      throw HYDRATION_ERROR;
    }
    return hydrate_node = node;
  }
  function hydrate_next() {
    return set_hydrate_node(get_next_sibling(hydrate_node));
  }
  function reset(node) {
    if (!hydrating) return;
    if (get_next_sibling(hydrate_node) !== null) {
      hydration_mismatch();
      throw HYDRATION_ERROR;
    }
    hydrate_node = node;
  }
  function next(count = 1) {
    if (hydrating) {
      var i = count;
      var node = hydrate_node;
      while (i--) {
        node = /** @type {TemplateNode} */
        get_next_sibling(node);
      }
      hydrate_node = node;
    }
  }
  function skip_nodes(remove = true) {
    var depth = 0;
    var node = hydrate_node;
    while (true) {
      if (node.nodeType === COMMENT_NODE) {
        var data = (
          /** @type {Comment} */
          node.data
        );
        if (data === HYDRATION_END) {
          if (depth === 0) return node;
          depth -= 1;
        } else if (data === HYDRATION_START || data === HYDRATION_START_ELSE || // "[1", "[2", etc. for if blocks
        data[0] === "[" && !isNaN(Number(data.slice(1)))) {
          depth += 1;
        }
      }
      var next2 = (
        /** @type {TemplateNode} */
        get_next_sibling(node)
      );
      if (remove) node.remove();
      node = next2;
    }
  }
  function read_hydration_instruction(node) {
    if (!node || node.nodeType !== COMMENT_NODE) {
      hydration_mismatch();
      throw HYDRATION_ERROR;
    }
    return (
      /** @type {Comment} */
      node.data
    );
  }

  // node_modules/svelte/src/internal/client/reactivity/equality.js
  function equals(value) {
    return value === this.v;
  }
  function safe_not_equal(a, b) {
    return a != a ? b == b : a !== b || a !== null && typeof a === "object" || typeof a === "function";
  }
  function safe_equals(value) {
    return !safe_not_equal(value, this.v);
  }

  // node_modules/svelte/src/internal/shared/errors.js
  function invariant_violation(message) {
    if (dev_fallback_default) {
      const error = new Error(`invariant_violation
An invariant violation occurred, meaning Svelte's internal assumptions were flawed. This is a bug in Svelte, not your app \u2014 please open an issue at https://github.com/sveltejs/svelte, citing the following message: "${message}"
https://svelte.dev/e/invariant_violation`);
      error.name = "Svelte error";
      throw error;
    } else {
      throw new Error(`https://svelte.dev/e/invariant_violation`);
    }
  }
  function lifecycle_outside_component(name) {
    if (dev_fallback_default) {
      const error = new Error(`lifecycle_outside_component
\`${name}(...)\` can only be used during component initialisation
https://svelte.dev/e/lifecycle_outside_component`);
      error.name = "Svelte error";
      throw error;
    } else {
      throw new Error(`https://svelte.dev/e/lifecycle_outside_component`);
    }
  }

  // node_modules/svelte/src/internal/client/errors.js
  function async_derived_orphan() {
    if (dev_fallback_default) {
      const error = new Error(`async_derived_orphan
Cannot create a \`$derived(...)\` with an \`await\` expression outside of an effect tree
https://svelte.dev/e/async_derived_orphan`);
      error.name = "Svelte error";
      throw error;
    } else {
      throw new Error(`https://svelte.dev/e/async_derived_orphan`);
    }
  }
  function bind_invalid_checkbox_value() {
    if (dev_fallback_default) {
      const error = new Error(`bind_invalid_checkbox_value
Using \`bind:value\` together with a checkbox input is not allowed. Use \`bind:checked\` instead
https://svelte.dev/e/bind_invalid_checkbox_value`);
      error.name = "Svelte error";
      throw error;
    } else {
      throw new Error(`https://svelte.dev/e/bind_invalid_checkbox_value`);
    }
  }
  function derived_references_self() {
    if (dev_fallback_default) {
      const error = new Error(`derived_references_self
A derived value cannot reference itself recursively
https://svelte.dev/e/derived_references_self`);
      error.name = "Svelte error";
      throw error;
    } else {
      throw new Error(`https://svelte.dev/e/derived_references_self`);
    }
  }
  function each_key_duplicate(a, b, value) {
    if (dev_fallback_default) {
      const error = new Error(`each_key_duplicate
${value ? `Keyed each block has duplicate key \`${value}\` at indexes ${a} and ${b}` : `Keyed each block has duplicate key at indexes ${a} and ${b}`}
https://svelte.dev/e/each_key_duplicate`);
      error.name = "Svelte error";
      throw error;
    } else {
      throw new Error(`https://svelte.dev/e/each_key_duplicate`);
    }
  }
  function each_key_volatile(index2, a, b) {
    if (dev_fallback_default) {
      const error = new Error(`each_key_volatile
Keyed each block has key that is not idempotent \u2014 the key for item at index ${index2} was \`${a}\` but is now \`${b}\`. Keys must be the same each time for a given item
https://svelte.dev/e/each_key_volatile`);
      error.name = "Svelte error";
      throw error;
    } else {
      throw new Error(`https://svelte.dev/e/each_key_volatile`);
    }
  }
  function effect_in_teardown(rune) {
    if (dev_fallback_default) {
      const error = new Error(`effect_in_teardown
\`${rune}\` cannot be used inside an effect cleanup function
https://svelte.dev/e/effect_in_teardown`);
      error.name = "Svelte error";
      throw error;
    } else {
      throw new Error(`https://svelte.dev/e/effect_in_teardown`);
    }
  }
  function effect_in_unowned_derived() {
    if (dev_fallback_default) {
      const error = new Error(`effect_in_unowned_derived
Effect cannot be created inside a \`$derived\` value that was not itself created inside an effect
https://svelte.dev/e/effect_in_unowned_derived`);
      error.name = "Svelte error";
      throw error;
    } else {
      throw new Error(`https://svelte.dev/e/effect_in_unowned_derived`);
    }
  }
  function effect_orphan(rune) {
    if (dev_fallback_default) {
      const error = new Error(`effect_orphan
\`${rune}\` can only be used inside an effect (e.g. during component initialisation)
https://svelte.dev/e/effect_orphan`);
      error.name = "Svelte error";
      throw error;
    } else {
      throw new Error(`https://svelte.dev/e/effect_orphan`);
    }
  }
  function effect_update_depth_exceeded() {
    if (dev_fallback_default) {
      const error = new Error(`effect_update_depth_exceeded
Maximum update depth exceeded. This typically indicates that an effect reads and writes the same piece of state
https://svelte.dev/e/effect_update_depth_exceeded`);
      error.name = "Svelte error";
      throw error;
    } else {
      throw new Error(`https://svelte.dev/e/effect_update_depth_exceeded`);
    }
  }
  function hydration_failed() {
    if (dev_fallback_default) {
      const error = new Error(`hydration_failed
Failed to hydrate the application
https://svelte.dev/e/hydration_failed`);
      error.name = "Svelte error";
      throw error;
    } else {
      throw new Error(`https://svelte.dev/e/hydration_failed`);
    }
  }
  function props_invalid_value(key2) {
    if (dev_fallback_default) {
      const error = new Error(`props_invalid_value
Cannot do \`bind:${key2}={undefined}\` when \`${key2}\` has a fallback value
https://svelte.dev/e/props_invalid_value`);
      error.name = "Svelte error";
      throw error;
    } else {
      throw new Error(`https://svelte.dev/e/props_invalid_value`);
    }
  }
  function rune_outside_svelte(rune) {
    if (dev_fallback_default) {
      const error = new Error(`rune_outside_svelte
The \`${rune}\` rune is only available inside \`.svelte\` and \`.svelte.js/ts\` files
https://svelte.dev/e/rune_outside_svelte`);
      error.name = "Svelte error";
      throw error;
    } else {
      throw new Error(`https://svelte.dev/e/rune_outside_svelte`);
    }
  }
  function state_descriptors_fixed() {
    if (dev_fallback_default) {
      const error = new Error(`state_descriptors_fixed
Property descriptors defined on \`$state\` objects must contain \`value\` and always be \`enumerable\`, \`configurable\` and \`writable\`.
https://svelte.dev/e/state_descriptors_fixed`);
      error.name = "Svelte error";
      throw error;
    } else {
      throw new Error(`https://svelte.dev/e/state_descriptors_fixed`);
    }
  }
  function state_prototype_fixed() {
    if (dev_fallback_default) {
      const error = new Error(`state_prototype_fixed
Cannot set prototype of \`$state\` object
https://svelte.dev/e/state_prototype_fixed`);
      error.name = "Svelte error";
      throw error;
    } else {
      throw new Error(`https://svelte.dev/e/state_prototype_fixed`);
    }
  }
  function state_unsafe_mutation() {
    if (dev_fallback_default) {
      const error = new Error(`state_unsafe_mutation
Updating state inside \`$derived(...)\`, \`$inspect(...)\` or a template expression is forbidden. If the value should not be reactive, declare it without \`$state\`
https://svelte.dev/e/state_unsafe_mutation`);
      error.name = "Svelte error";
      throw error;
    } else {
      throw new Error(`https://svelte.dev/e/state_unsafe_mutation`);
    }
  }
  function svelte_boundary_reset_onerror() {
    if (dev_fallback_default) {
      const error = new Error(`svelte_boundary_reset_onerror
A \`<svelte:boundary>\` \`reset\` function cannot be called while an error is still being handled
https://svelte.dev/e/svelte_boundary_reset_onerror`);
      error.name = "Svelte error";
      throw error;
    } else {
      throw new Error(`https://svelte.dev/e/svelte_boundary_reset_onerror`);
    }
  }

  // node_modules/svelte/src/internal/flags/index.js
  var async_mode_flag = false;
  var legacy_mode_flag = false;
  var tracing_mode_flag = false;

  // node_modules/svelte/src/internal/client/dev/tracing.js
  var tracing_expressions = null;
  function tag(source2, label) {
    source2.label = label;
    tag_proxy(source2.v, label);
    return source2;
  }
  function tag_proxy(value, label) {
    value?.[PROXY_PATH_SYMBOL]?.(label);
    return value;
  }

  // node_modules/svelte/src/internal/shared/dev.js
  function get_error(label) {
    const error = new Error();
    const stack2 = get_stack();
    if (stack2.length === 0) {
      return null;
    }
    stack2.unshift("\n");
    define_property(error, "stack", {
      value: stack2.join("\n")
    });
    define_property(error, "name", {
      value: label
    });
    return (
      /** @type {Error & { stack: string }} */
      error
    );
  }
  function get_stack() {
    const limit = Error.stackTraceLimit;
    Error.stackTraceLimit = Infinity;
    const stack2 = new Error().stack;
    Error.stackTraceLimit = limit;
    if (!stack2) return [];
    const lines = stack2.split("\n");
    const new_lines = [];
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const posixified = line.replaceAll("\\", "/");
      if (line.trim() === "Error") {
        continue;
      }
      if (line.includes("validate_each_keys")) {
        return [];
      }
      if (posixified.includes("svelte/src/internal") || posixified.includes("node_modules/.vite")) {
        continue;
      }
      new_lines.push(line);
    }
    return new_lines;
  }
  function invariant(condition, message) {
    if (!dev_fallback_default) {
      throw new Error("invariant(...) was not guarded by if (DEV)");
    }
    if (!condition) invariant_violation(message);
  }

  // node_modules/svelte/src/internal/client/context.js
  var component_context = null;
  function set_component_context(context) {
    component_context = context;
  }
  var dev_stack = null;
  function set_dev_stack(stack2) {
    dev_stack = stack2;
  }
  var dev_current_component_function = null;
  function set_dev_current_component_function(fn) {
    dev_current_component_function = fn;
  }
  function push(props, runes = false, fn) {
    component_context = {
      p: component_context,
      i: false,
      c: null,
      e: null,
      s: props,
      x: null,
      r: (
        /** @type {Effect} */
        active_effect
      ),
      l: legacy_mode_flag && !runes ? { s: null, u: null, $: [] } : null
    };
    if (dev_fallback_default) {
      component_context.function = fn;
      dev_current_component_function = fn;
    }
  }
  function pop(component2) {
    var context = (
      /** @type {ComponentContext} */
      component_context
    );
    var effects = context.e;
    if (effects !== null) {
      context.e = null;
      for (var fn of effects) {
        create_user_effect(fn);
      }
    }
    if (component2 !== void 0) {
      context.x = component2;
    }
    context.i = true;
    component_context = context.p;
    if (dev_fallback_default) {
      dev_current_component_function = component_context?.function ?? null;
    }
    return mark_as_component(component2);
  }
  function mark_as_component(component2 = {}) {
    define_property(component2, COMPONENT_SYMBOL, { value: true });
    return component2;
  }
  function is_runes() {
    return !legacy_mode_flag || component_context !== null && component_context.l === null;
  }

  // node_modules/svelte/src/internal/client/dom/task.js
  var micro_tasks = [];
  function run_micro_tasks() {
    var tasks = micro_tasks;
    micro_tasks = [];
    run_all(tasks);
  }
  function queue_micro_task(fn) {
    if (micro_tasks.length === 0 && !is_flushing_sync) {
      var tasks = micro_tasks;
      queueMicrotask(() => {
        if (tasks === micro_tasks) run_micro_tasks();
      });
    }
    micro_tasks.push(fn);
  }
  function flush_tasks() {
    while (micro_tasks.length > 0) {
      run_micro_tasks();
    }
  }

  // node_modules/svelte/src/internal/client/reactivity/status.js
  var STATUS_MASK = ~(DIRTY | MAYBE_DIRTY | CLEAN);
  function set_signal_status(signal, status) {
    signal.f = signal.f & STATUS_MASK | status;
  }
  function update_derived_status(derived2) {
    if ((derived2.f & CONNECTED) !== 0 || derived2.deps === null) {
      set_signal_status(derived2, CLEAN);
    } else {
      set_signal_status(derived2, MAYBE_DIRTY);
    }
  }

  // node_modules/svelte/src/internal/client/reactivity/utils.js
  function clear_marked(deps) {
    if (deps === null) return;
    for (const dep of deps) {
      if ((dep.f & DERIVED) === 0 || (dep.f & WAS_MARKED) === 0) {
        continue;
      }
      dep.f ^= WAS_MARKED;
      clear_marked(
        /** @type {Derived} */
        dep.deps
      );
    }
  }
  function defer_effect(effect2, dirty_effects, maybe_dirty_effects) {
    if ((effect2.f & DIRTY) !== 0) {
      dirty_effects.add(effect2);
    } else if ((effect2.f & MAYBE_DIRTY) !== 0) {
      maybe_dirty_effects.add(effect2);
    }
    clear_marked(effect2.deps);
    set_signal_status(effect2, CLEAN);
  }

  // node_modules/svelte/src/internal/client/reactivity/store.js
  var legacy_is_updating_store = false;
  var is_store_binding = false;
  function capture_store_binding(fn) {
    var previous_is_store_binding = is_store_binding;
    try {
      is_store_binding = false;
      return [fn(), is_store_binding];
    } finally {
      is_store_binding = previous_is_store_binding;
    }
  }

  // node_modules/svelte/src/internal/client/dom/elements/misc.js
  function remove_textarea_child(dom) {
    if (hydrating && get_first_child(dom) !== null) {
      clear_text_content(dom);
    }
  }
  var listening_to_form_reset = false;
  function add_form_reset_listener() {
    if (!listening_to_form_reset) {
      listening_to_form_reset = true;
      document.addEventListener(
        "reset",
        (evt) => {
          Promise.resolve().then(() => {
            if (!evt.defaultPrevented) {
              for (
                const e of
                /**@type {HTMLFormElement} */
                evt.target.elements
              ) {
                e[FORM_RESET_HANDLER]?.();
              }
            }
          });
        },
        // In the capture phase to guarantee we get noticed of it (no possibility of stopPropagation)
        { capture: true }
      );
    }
  }

  // node_modules/svelte/src/internal/client/dom/elements/bindings/shared.js
  function without_reactive_context(fn) {
    var previous_reaction = active_reaction;
    var previous_effect = active_effect;
    set_active_reaction(null);
    set_active_effect(null);
    try {
      return fn();
    } finally {
      set_active_reaction(previous_reaction);
      set_active_effect(previous_effect);
    }
  }
  function listen_to_event_and_reset_event(element2, event2, handler, on_reset = handler) {
    element2.addEventListener(event2, () => without_reactive_context(handler));
    const prev = (
      /** @type {any} */
      element2[FORM_RESET_HANDLER]
    );
    if (prev) {
      element2[FORM_RESET_HANDLER] = () => {
        prev();
        on_reset(true);
      };
    } else {
      element2[FORM_RESET_HANDLER] = () => on_reset(true);
    }
    add_form_reset_listener();
  }

  // node_modules/svelte/src/internal/client/reactivity/async.js
  function flatten(blockers, sync, async2, fn) {
    const d = is_runes() ? derived : derived_safe_equal;
    var pending2 = blockers.filter((b) => !b.settled);
    var deriveds = sync.map(d);
    if (dev_fallback_default) {
      deriveds.forEach((d2, i) => {
        d2.label = sync[i].toString().replace("() => ", "").replaceAll("$.eager(() => ", "$state.eager(").replace(/\$\.get\((.+?)\)/g, (_, id) => id);
      });
    }
    if (async2.length === 0 && pending2.length === 0) {
      fn(deriveds);
      return;
    }
    var parent = (
      /** @type {Effect} */
      active_effect
    );
    var restore = capture();
    var blocker_promise = pending2.length === 1 ? pending2[0].promise : pending2.length > 1 ? Promise.all(pending2.map((b) => b.promise)) : null;
    function finish(async3) {
      if ((parent.f & DESTROYED) !== 0) {
        return;
      }
      restore();
      try {
        fn([...deriveds, ...async3]);
      } catch (error) {
        invoke_error_boundary(error, parent);
      }
      unset_context();
    }
    var decrement_pending = increment_pending();
    if (async2.length === 0) {
      blocker_promise.then(() => finish([])).finally(decrement_pending);
      return;
    }
    function run3() {
      Promise.all(async2.map((expression) => async_derived(expression))).then(finish).catch((error) => invoke_error_boundary(error, parent)).finally(decrement_pending);
    }
    if (blocker_promise) {
      blocker_promise.then(() => {
        restore();
        run3();
        unset_context();
      });
    } else {
      run3();
    }
  }
  function capture() {
    var previous_effect = (
      /** @type {Effect} */
      active_effect
    );
    var previous_reaction = active_reaction;
    var previous_component_context = component_context;
    var previous_batch2 = (
      /** @type {Batch} */
      current_batch
    );
    if (dev_fallback_default) {
      var previous_dev_stack = dev_stack;
    }
    return function restore(activate_batch = true) {
      set_active_effect(previous_effect);
      set_active_reaction(previous_reaction);
      set_component_context(previous_component_context);
      if (activate_batch && (previous_effect.f & DESTROYED) === 0) {
        previous_batch2?.activate();
        previous_batch2?.apply();
      }
      if (dev_fallback_default) {
        set_reactivity_loss_tracker(null);
        set_dev_stack(previous_dev_stack);
      }
    };
  }
  var restored = false;
  function unset_context(deactivate_batch = true) {
    restored = false;
    set_active_effect(null);
    set_active_reaction(null);
    set_component_context(null);
    if (deactivate_batch) current_batch?.deactivate();
    if (dev_fallback_default) {
      set_reactivity_loss_tracker(null);
      set_dev_stack(null);
    }
  }
  function increment_pending() {
    var effect2 = (
      /** @type {Effect} */
      active_effect
    );
    var boundary2 = effect2.b;
    var batch = (
      /** @type {Batch} */
      current_batch
    );
    var blocking = !!boundary2?.is_rendered();
    boundary2?.update_pending_count(1, batch);
    batch.increment(blocking, effect2);
    return () => {
      boundary2?.update_pending_count(-1, batch);
      batch.decrement(blocking, effect2);
    };
  }

  // node_modules/svelte/src/internal/client/reactivity/deriveds.js
  var reactivity_loss_tracker = null;
  function set_reactivity_loss_tracker(v) {
    reactivity_loss_tracker = v;
  }
  var recent_async_deriveds = /* @__PURE__ */ new Set();
  // @__NO_SIDE_EFFECTS__
  function derived(fn) {
    var flags2 = DERIVED | DIRTY;
    if (active_effect !== null) {
      active_effect.f |= EFFECT_PRESERVED;
    }
    const signal = {
      ctx: component_context,
      deps: null,
      effects: null,
      equals,
      f: flags2,
      fn,
      reactions: null,
      rv: 0,
      v: (
        /** @type {V} */
        UNINITIALIZED
      ),
      wv: 0,
      parent: active_effect,
      ac: null
    };
    if (dev_fallback_default && tracing_mode_flag) {
      signal.created = get_error("created at");
    }
    return signal;
  }
  var OBSOLETE = /* @__PURE__ */ Symbol("obsolete");
  // @__NO_SIDE_EFFECTS__
  function async_derived(fn, label, location2) {
    let parent = (
      /** @type {Effect | null} */
      active_effect
    );
    if (parent === null) {
      async_derived_orphan();
    }
    var promise = (
      /** @type {Promise<V>} */
      /** @type {unknown} */
      void 0
    );
    var signal = source(
      /** @type {V} */
      UNINITIALIZED
    );
    if (dev_fallback_default) signal.label = label ?? fn.toString();
    var should_suspend = !active_reaction;
    var deferreds = /* @__PURE__ */ new Set();
    async_effect(() => {
      var effect2 = (
        /** @type {Effect} */
        active_effect
      );
      if (dev_fallback_default) {
        reactivity_loss_tracker = { effect: effect2, effect_deps: /* @__PURE__ */ new Set(), warned: false };
      }
      var d = deferred();
      promise = d.promise;
      try {
        Promise.resolve(fn()).then(d.resolve, (e) => {
          if (e !== STALE_REACTION) d.reject(e);
        }).finally(unset_context);
      } catch (error) {
        d.reject(error);
        unset_context();
      }
      if (dev_fallback_default) {
        if (reactivity_loss_tracker) {
          if (effect2.deps !== null) {
            for (let i = 0; i < skipped_deps; i += 1) {
              reactivity_loss_tracker.effect_deps.add(effect2.deps[i]);
            }
          }
          if (new_deps !== null) {
            for (let i = 0; i < new_deps.length; i += 1) {
              reactivity_loss_tracker.effect_deps.add(new_deps[i]);
            }
          }
        }
        reactivity_loss_tracker = null;
      }
      var batch = (
        /** @type {Batch} */
        current_batch
      );
      if (should_suspend) {
        if ((effect2.f & REACTION_RAN) !== 0) {
          var decrement_pending = increment_pending();
        }
        if (
          // boundary can be null if the async derived is inside an $effect.root not connected to the component render tree
          parent.b?.is_rendered()
        ) {
          batch.async_deriveds.get(effect2)?.reject(OBSOLETE);
        } else {
          for (const d2 of deferreds.values()) {
            d2.reject(OBSOLETE);
          }
        }
        deferreds.add(d);
        batch.async_deriveds.set(effect2, d);
      }
      const handler = (value, error = void 0) => {
        if (dev_fallback_default) {
          reactivity_loss_tracker = null;
        }
        decrement_pending?.();
        deferreds.delete(d);
        if (error === OBSOLETE) return;
        batch.activate();
        if (error) {
          signal.f |= ERROR_VALUE;
          internal_set(signal, error);
        } else {
          if ((signal.f & ERROR_VALUE) !== 0) {
            signal.f ^= ERROR_VALUE;
          }
          if (dev_fallback_default && location2 !== void 0 && !signal.equals(value)) {
            recent_async_deriveds.add(signal);
            setTimeout(() => {
              if (recent_async_deriveds.has(signal) && (effect2.f & DESTROYED) === 0) {
                await_waterfall(
                  /** @type {string} */
                  signal.label,
                  location2
                );
                recent_async_deriveds.delete(signal);
              }
            });
          }
          internal_set(signal, value);
        }
        batch.deactivate();
      };
      d.promise.then(handler, (e) => handler(null, e || "unknown"));
    });
    teardown(() => {
      for (const d of deferreds) {
        d.reject(OBSOLETE);
      }
    });
    if (dev_fallback_default) {
      signal.f |= ASYNC;
    }
    return new Promise((fulfil) => {
      function next2(p) {
        function go() {
          if (p === promise) {
            fulfil(signal);
          } else {
            next2(promise);
          }
        }
        p.then(go, go);
      }
      next2(promise);
    });
  }
  // @__NO_SIDE_EFFECTS__
  function user_derived(fn) {
    const d = /* @__PURE__ */ derived(fn);
    if (!async_mode_flag) push_reaction_value(d);
    return d;
  }
  // @__NO_SIDE_EFFECTS__
  function derived_safe_equal(fn) {
    const signal = /* @__PURE__ */ derived(fn);
    signal.equals = safe_equals;
    return signal;
  }
  function destroy_derived_effects(derived2) {
    var effects = derived2.effects;
    if (effects !== null) {
      derived2.effects = null;
      for (var i = 0; i < effects.length; i += 1) {
        destroy_effect(
          /** @type {Effect} */
          effects[i]
        );
      }
    }
  }
  var stack = [];
  function execute_derived(derived2) {
    var value;
    var prev_active_effect = active_effect;
    var parent = derived2.parent;
    if (!is_destroying_effect && parent !== null && derived2.v !== UNINITIALIZED && // if it was never evaluated before, it's guaranteed to fail downstream, so we try to execute instead
    (parent.f & (DESTROYED | INERT)) !== 0) {
      derived_inert();
      return derived2.v;
    }
    set_active_effect(parent);
    if (dev_fallback_default) {
      let prev_eager_effects = eager_effects;
      set_eager_effects(/* @__PURE__ */ new Set());
      try {
        if (includes.call(stack, derived2)) {
          derived_references_self();
        }
        stack.push(derived2);
        derived2.f &= ~WAS_MARKED;
        destroy_derived_effects(derived2);
        value = update_reaction(derived2);
      } finally {
        set_active_effect(prev_active_effect);
        set_eager_effects(prev_eager_effects);
        stack.pop();
      }
    } else {
      try {
        derived2.f &= ~WAS_MARKED;
        destroy_derived_effects(derived2);
        value = update_reaction(derived2);
      } finally {
        set_active_effect(prev_active_effect);
      }
    }
    return value;
  }
  function update_derived(derived2) {
    var value = execute_derived(derived2);
    if (!derived2.equals(value)) {
      derived2.wv = increment_write_version();
      if (!current_batch?.is_fork || derived2.deps === null) {
        if (current_batch !== null) {
          current_batch.capture(derived2, value, true);
          previous_batch?.capture(derived2, value, true);
        } else {
          derived2.v = value;
        }
        if (derived2.deps === null) {
          set_signal_status(derived2, CLEAN);
          return;
        }
      }
    }
    if (is_destroying_effect) {
      return;
    }
    if (batch_values !== null) {
      if (effect_tracking() || current_batch?.is_fork) {
        batch_values.set(derived2, value);
      }
    } else {
      update_derived_status(derived2);
    }
  }
  function freeze_derived_effects(derived2) {
    if (derived2.effects === null) return;
    for (const e of derived2.effects) {
      if (e.teardown || e.ac) {
        e.teardown?.();
        if (e.ac !== null) {
          without_reactive_context(() => {
            e.ac.abort(STALE_REACTION);
            e.ac = null;
          });
        }
        if (e.fn !== null) e.teardown = noop;
        remove_reactions(e, 0);
        destroy_effect_children(e);
      }
    }
  }
  function unfreeze_derived_effects(derived2) {
    if (derived2.effects === null) return;
    for (const e of derived2.effects) {
      if (e.teardown && e.fn !== null) {
        update_effect(e);
      }
    }
  }

  // node_modules/svelte/src/internal/client/reactivity/batch.js
  var first_batch = null;
  var last_batch = null;
  var current_batch = null;
  var previous_batch = null;
  var batch_values = null;
  var last_scheduled_effect = null;
  var is_flushing_sync = false;
  var is_processing = false;
  var collected_effects = null;
  var legacy_updates = null;
  var flush_count = 0;
  var source_stacks = /* @__PURE__ */ new Set();
  var uid = 1;
  var Batch = class _Batch {
    id = uid++;
    /** True as soon as `#process` was called */
    #started = false;
    linked = true;
    /** @type {Batch | null} */
    #prev = null;
    /** @type {Batch | null} */
    #next = null;
    /** @type {Map<Effect, ReturnType<typeof deferred<any>>>} */
    async_deriveds = /* @__PURE__ */ new Map();
    /**
     * The current values of any signals that are updated in this batch.
     * Tuple format: [value, is_derived] (note: is_derived is false for deriveds, too, if they were overridden via assignment)
     * They keys of this map are identical to `this.#previous`
     * @type {Map<Value, [any, boolean]>}
     */
    current = /* @__PURE__ */ new Map();
    /**
     * The values of any signals (sources and deriveds) that are updated in this batch _before_ those updates took place.
     * They keys of this map are identical to `this.#current`
     * @type {Map<Value, any>}
     */
    previous = /* @__PURE__ */ new Map();
    /**
     * When the batch is committed (and the DOM is updated), we need to remove old branches
     * and append new ones by calling the functions added inside (if/each/key/etc) blocks
     * @type {Set<(batch: Batch) => void>}
     */
    #commit_callbacks = /* @__PURE__ */ new Set();
    /**
     * If a fork is discarded, we need to destroy any effects that are no longer needed
     * @type {Set<(batch: Batch) => void>}
     */
    #discard_callbacks = /* @__PURE__ */ new Set();
    /**
     * The number of async effects that are currently in flight
     */
    #pending = 0;
    /**
     * Async effects that are currently in flight, _not_ inside a pending boundary
     * @type {Map<Effect, number>}
     */
    #blocking_pending = /* @__PURE__ */ new Map();
    /**
     * A deferred that resolves when the batch is committed, used with `settled()`
     * TODO replace with Promise.withResolvers once supported widely enough
     * @type {{ promise: Promise<void>, resolve: (value?: any) => void, reject: (reason: unknown) => void } | null}
     */
    #deferred = null;
    /**
     * The root effects that need to be flushed
     * @type {Effect[]}
     */
    #roots = [];
    /**
     * Effects created while this batch was active.
     * @type {Effect[]}
     */
    #new_effects = [];
    /**
     * Deferred effects (which run after async work has completed) that are DIRTY
     * @type {Set<Effect>}
     */
    #dirty_effects = /* @__PURE__ */ new Set();
    /**
     * Deferred effects that are MAYBE_DIRTY
     * @type {Set<Effect>}
     */
    #maybe_dirty_effects = /* @__PURE__ */ new Set();
    /**
     * A map of branches that still exist, but will be destroyed when this batch
     * is committed — we skip over these during `process`.
     * The value contains child effects that were dirty/maybe_dirty before being reset,
     * so they can be rescheduled if the branch survives.
     * @type {Map<Effect, { d: Effect[], m: Effect[] }>}
     */
    #skipped_branches = /* @__PURE__ */ new Map();
    /**
     * Inverse of #skipped_branches which we need to tell prior batches to unskip them when committing
     * @type {Set<Effect>}
     */
    #unskipped_branches = /* @__PURE__ */ new Set();
    is_fork = false;
    #decrement_queued = false;
    constructor() {
      if (last_batch === null) {
        first_batch = last_batch = this;
      } else {
        last_batch.#next = this;
        this.#prev = last_batch;
      }
      last_batch = this;
    }
    #is_deferred() {
      if (this.is_fork) return true;
      for (const effect2 of this.#blocking_pending.keys()) {
        var e = effect2;
        var skipped = false;
        while (e.parent !== null) {
          if (this.#skipped_branches.has(e)) {
            skipped = true;
            break;
          }
          e = e.parent;
        }
        if (!skipped) {
          return true;
        }
      }
      return false;
    }
    /**
     * Add an effect to the #skipped_branches map and reset its children
     * @param {Effect} effect
     */
    skip_effect(effect2) {
      if (!this.#skipped_branches.has(effect2)) {
        this.#skipped_branches.set(effect2, { d: [], m: [] });
      }
      this.#unskipped_branches.delete(effect2);
    }
    /**
     * Remove an effect from the #skipped_branches map and reschedule
     * any tracked dirty/maybe_dirty child effects
     * @param {Effect} effect
     * @param {(e: Effect) => void} callback
     */
    unskip_effect(effect2, callback = (e) => this.schedule(e)) {
      var tracked = this.#skipped_branches.get(effect2);
      if (tracked) {
        this.#skipped_branches.delete(effect2);
        for (var e of tracked.d) {
          set_signal_status(e, DIRTY);
          callback(e);
        }
        for (e of tracked.m) {
          set_signal_status(e, MAYBE_DIRTY);
          callback(e);
        }
      }
      this.#unskipped_branches.add(effect2);
    }
    #process() {
      this.#started = true;
      if (flush_count++ > 1e3) {
        this.#unlink();
        infinite_loop_guard();
      }
      if (dev_fallback_default) {
        for (const value of this.current.keys()) {
          source_stacks.add(value);
        }
      }
      for (const e of this.#dirty_effects) {
        this.#maybe_dirty_effects.delete(e);
        set_signal_status(e, DIRTY);
        this.schedule(e);
      }
      for (const e of this.#maybe_dirty_effects) {
        set_signal_status(e, MAYBE_DIRTY);
        this.schedule(e);
      }
      const roots = this.#roots;
      this.#roots = [];
      this.apply();
      var effects = collected_effects = [];
      var render_effects = [];
      var updates = legacy_updates = [];
      for (const root11 of roots) {
        try {
          this.#traverse(root11, effects, render_effects);
        } catch (e) {
          reset_all(root11);
          if (!this.#is_deferred()) this.discard();
          throw e;
        }
      }
      current_batch = null;
      if (updates.length > 0) {
        var batch = _Batch.ensure();
        for (const e of updates) {
          batch.schedule(e);
        }
      }
      collected_effects = null;
      legacy_updates = null;
      if (this.#is_deferred()) {
        this.#defer_effects(render_effects);
        this.#defer_effects(effects);
        for (const [e, t] of this.#skipped_branches) {
          reset_branch(e, t);
        }
        if (updates.length > 0) {
          /** @type {unknown} */
          current_batch.#process();
        }
        return;
      }
      const earlier_batch = this.#find_earlier_batch();
      if (earlier_batch) {
        this.#defer_effects(render_effects);
        this.#defer_effects(effects);
        earlier_batch.#merge(this);
        return;
      }
      this.#dirty_effects.clear();
      this.#maybe_dirty_effects.clear();
      for (const fn of this.#commit_callbacks) fn(this);
      this.#commit_callbacks.clear();
      previous_batch = this;
      flush_queued_effects(render_effects);
      flush_queued_effects(effects);
      previous_batch = null;
      this.#deferred?.resolve();
      var next_batch = (
        /** @type {Batch | null} */
        /** @type {unknown} */
        current_batch
      );
      if (this.#pending === 0 && (this.#roots.length === 0 || next_batch !== null)) {
        this.#unlink();
        if (async_mode_flag) {
          this.#commit();
          current_batch = next_batch;
        }
      }
      if (this.#roots.length > 0) {
        if (next_batch !== null) {
          const batch2 = next_batch;
          batch2.#roots.push(...this.#roots.filter((r) => !batch2.#roots.includes(r)));
        } else {
          next_batch = this;
        }
      }
      if (next_batch !== null) {
        old_values.clear();
        next_batch.#process();
      }
    }
    /**
     * Traverse the effect tree, executing effects or stashing
     * them for later execution as appropriate
     * @param {Effect} root
     * @param {Effect[]} effects
     * @param {Effect[]} render_effects
     */
    #traverse(root11, effects, render_effects) {
      root11.f ^= CLEAN;
      var effect2 = root11.first;
      while (effect2 !== null) {
        var flags2 = effect2.f;
        var is_branch = (flags2 & (BRANCH_EFFECT | ROOT_EFFECT)) !== 0;
        var is_skippable_branch = is_branch && (flags2 & CLEAN) !== 0;
        var skip = is_skippable_branch || (flags2 & INERT) !== 0 || this.#skipped_branches.has(effect2);
        if (!skip && effect2.fn !== null) {
          if (is_branch) {
            effect2.f ^= CLEAN;
          } else if ((flags2 & EFFECT) !== 0) {
            effects.push(effect2);
          } else if (async_mode_flag && (flags2 & (RENDER_EFFECT | MANAGED_EFFECT)) !== 0) {
            render_effects.push(effect2);
          } else if (is_dirty(effect2)) {
            if ((flags2 & BLOCK_EFFECT) !== 0) this.#maybe_dirty_effects.add(effect2);
            update_effect(effect2);
          }
          var child2 = effect2.first;
          if (child2 !== null) {
            effect2 = child2;
            continue;
          }
        }
        while (effect2 !== null) {
          var next2 = effect2.next;
          if (next2 !== null) {
            effect2 = next2;
            break;
          }
          effect2 = effect2.parent;
        }
      }
    }
    #find_earlier_batch() {
      var batch = this.#prev;
      while (batch !== null) {
        if (!batch.is_fork) {
          for (const [value, [, is_derived]] of this.current) {
            if (batch.current.has(value) && !is_derived) {
              return batch;
            }
          }
        }
        batch = batch.#prev;
      }
      return null;
    }
    /**
     * @param {Batch} batch
     */
    #merge(batch) {
      for (const [source2, value] of batch.current) {
        if (!this.previous.has(source2) && batch.previous.has(source2)) {
          this.previous.set(source2, batch.previous.get(source2));
        }
        this.current.set(source2, value);
      }
      for (const [effect2, deferred2] of batch.async_deriveds) {
        const d = this.async_deriveds.get(effect2);
        if (d) deferred2.promise.then(d.resolve).catch(d.reject);
      }
      batch.async_deriveds.clear();
      this.transfer_effects(batch.#dirty_effects, batch.#maybe_dirty_effects);
      const mark = (value) => {
        var reactions = value.reactions;
        if (reactions === null) return;
        if ((value.f & DERIVED) !== 0 && (value.f & (DIRTY | MAYBE_DIRTY)) === 0) {
          return;
        }
        for (const reaction of reactions) {
          var flags2 = reaction.f;
          if ((flags2 & DERIVED) !== 0) {
            mark(
              /** @type {Derived} */
              reaction
            );
          } else {
            var effect2 = (
              /** @type {Effect} */
              reaction
            );
            if (flags2 & (ASYNC | BLOCK_EFFECT) && !this.async_deriveds.has(effect2)) {
              this.#maybe_dirty_effects.delete(effect2);
              set_signal_status(effect2, DIRTY);
              this.schedule(effect2);
            }
          }
        }
      };
      for (const source2 of this.current.keys()) {
        mark(source2);
      }
      this.oncommit(() => batch.discard());
      batch.#unlink();
      current_batch = this;
      this.#process();
    }
    /**
     * @param {Effect[]} effects
     */
    #defer_effects(effects) {
      for (var i = 0; i < effects.length; i += 1) {
        defer_effect(effects[i], this.#dirty_effects, this.#maybe_dirty_effects);
      }
    }
    /**
     * Associate a change to a given source with the current
     * batch, noting its previous and current values
     * @param {Value} source
     * @param {any} value
     * @param {boolean} [is_derived]
     */
    capture(source2, value, is_derived = false) {
      if (source2.v !== UNINITIALIZED && !this.previous.has(source2)) {
        this.previous.set(source2, source2.v);
      }
      if ((source2.f & ERROR_VALUE) === 0) {
        this.current.set(source2, [value, is_derived]);
        batch_values?.set(source2, value);
      }
      if (!this.is_fork) {
        source2.v = value;
      }
    }
    activate() {
      current_batch = this;
    }
    deactivate() {
      current_batch = null;
      batch_values = null;
    }
    flush() {
      try {
        if (dev_fallback_default) {
          source_stacks.clear();
        }
        is_processing = true;
        current_batch = this;
        this.#process();
      } finally {
        flush_count = 0;
        last_scheduled_effect = null;
        collected_effects = null;
        legacy_updates = null;
        is_processing = false;
        current_batch = null;
        batch_values = null;
        old_values.clear();
        if (dev_fallback_default) {
          for (const source2 of source_stacks) {
            source2.updated = null;
          }
        }
      }
    }
    discard() {
      for (const fn of this.#discard_callbacks) fn(this);
      this.#discard_callbacks.clear();
      for (const deferred2 of this.async_deriveds.values()) {
        deferred2.reject(OBSOLETE);
      }
      this.#unlink();
      this.#deferred?.resolve();
    }
    /**
     * @param {Effect} effect
     */
    register_created_effect(effect2) {
      this.#new_effects.push(effect2);
    }
    #commit() {
      for (let batch = first_batch; batch !== null; batch = batch.#next) {
        var is_earlier = batch.id < this.id;
        var sources = [];
        for (const [source3, [value, is_derived]] of this.current) {
          if (batch.current.has(source3)) {
            var batch_value = (
              /** @type {[any, boolean]} */
              batch.current.get(source3)[0]
            );
            if (is_earlier && value !== batch_value) {
              batch.current.set(source3, [value, is_derived]);
            } else {
              continue;
            }
          }
          sources.push(source3);
        }
        if (is_earlier) {
          for (const [effect2, deferred2] of this.async_deriveds) {
            const d = batch.async_deriveds.get(effect2);
            if (d) deferred2.promise.then(d.resolve).catch(d.reject);
          }
        }
        var current = [...batch.current.keys()].filter(
          (source3) => !/** @type {[any, boolean]} */
          batch.current.get(source3)[1]
        );
        if (!batch.#started || current.length === 0) continue;
        var others = current.filter((source3) => !this.current.has(source3));
        if (others.length === 0) {
          if (is_earlier) {
            batch.discard();
          }
        } else if (sources.length > 0) {
          if (dev_fallback_default && !batch.#decrement_queued) {
            invariant(batch.#roots.length === 0, "Batch has scheduled roots");
          }
          if (is_earlier) {
            for (const unskipped of this.#unskipped_branches) {
              batch.unskip_effect(unskipped, (e) => {
                if ((e.f & (BLOCK_EFFECT | ASYNC)) !== 0) {
                  batch.schedule(e);
                } else {
                  batch.#defer_effects([e]);
                }
              });
            }
          }
          batch.activate();
          var marked = /* @__PURE__ */ new Set();
          var checked = /* @__PURE__ */ new Map();
          for (var source2 of sources) {
            mark_effects(source2, others, marked, checked);
          }
          checked = /* @__PURE__ */ new Map();
          var current_unequal = [...batch.current].filter(([c, v1]) => {
            const v2 = this.current.get(c);
            if (!v2) return true;
            return v2[0] !== v1[0] || v2[1] !== v1[1];
          }).map(([c]) => c);
          if (current_unequal.length > 0) {
            for (const effect2 of this.#new_effects) {
              if ((effect2.f & (DESTROYED | INERT | EAGER_EFFECT)) === 0 && depends_on(effect2, current_unequal, checked)) {
                if ((effect2.f & (ASYNC | BLOCK_EFFECT)) !== 0) {
                  set_signal_status(effect2, DIRTY);
                  batch.schedule(effect2);
                } else {
                  batch.#dirty_effects.add(effect2);
                }
              }
            }
          }
          if (batch.#roots.length > 0 && !batch.#decrement_queued) {
            batch.apply();
            for (var root11 of batch.#roots) {
              batch.#traverse(root11, [], []);
            }
            batch.#roots = [];
          }
          batch.deactivate();
        }
      }
    }
    /**
     * @param {boolean} blocking
     * @param {Effect} effect
     */
    increment(blocking, effect2) {
      this.#pending += 1;
      if (blocking) {
        let blocking_pending_count = this.#blocking_pending.get(effect2) ?? 0;
        this.#blocking_pending.set(effect2, blocking_pending_count + 1);
      }
    }
    /**
     * @param {boolean} blocking
     * @param {Effect} effect
     */
    decrement(blocking, effect2) {
      this.#pending -= 1;
      if (blocking) {
        let blocking_pending_count = this.#blocking_pending.get(effect2) ?? 0;
        if (blocking_pending_count === 1) {
          this.#blocking_pending.delete(effect2);
        } else {
          this.#blocking_pending.set(effect2, blocking_pending_count - 1);
        }
      }
      if (this.#decrement_queued) return;
      this.#decrement_queued = true;
      queue_micro_task(() => {
        this.#decrement_queued = false;
        if (this.linked) {
          this.flush();
        }
      });
    }
    /**
     * @param {Set<Effect>} dirty_effects
     * @param {Set<Effect>} maybe_dirty_effects
     */
    transfer_effects(dirty_effects, maybe_dirty_effects) {
      for (const e of dirty_effects) {
        this.#dirty_effects.add(e);
      }
      for (const e of maybe_dirty_effects) {
        this.#maybe_dirty_effects.add(e);
      }
      dirty_effects.clear();
      maybe_dirty_effects.clear();
    }
    /** @param {(batch: Batch) => void} fn */
    oncommit(fn) {
      this.#commit_callbacks.add(fn);
    }
    /** @param {(batch: Batch) => void} fn */
    ondiscard(fn) {
      this.#discard_callbacks.add(fn);
    }
    settled() {
      return (this.#deferred ??= deferred()).promise;
    }
    static ensure() {
      if (current_batch === null) {
        const batch = current_batch = new _Batch();
        if (!is_processing && !is_flushing_sync) {
          queue_micro_task(() => {
            if (!batch.#started) {
              batch.flush();
            }
          });
        }
      }
      return current_batch;
    }
    apply() {
      if (!async_mode_flag || !this.is_fork && this.#prev === null && this.#next === null) {
        batch_values = null;
        return;
      }
      batch_values = /* @__PURE__ */ new Map();
      for (const [source2, [value]] of this.current) {
        batch_values.set(source2, value);
      }
      for (let batch = first_batch; batch !== null; batch = batch.#next) {
        if (batch === this || batch.is_fork) continue;
        var intersects = false;
        if (batch.id < this.id) {
          for (const [source2, [, is_derived]] of batch.current) {
            if (is_derived) continue;
            if (this.current.has(source2)) {
              intersects = true;
              break;
            }
          }
        }
        if (!intersects) {
          for (const [source2, previous] of batch.previous) {
            if (!batch_values.has(source2)) {
              batch_values.set(source2, previous);
            }
          }
        }
      }
    }
    /**
     *
     * @param {Effect} effect
     */
    schedule(effect2) {
      last_scheduled_effect = effect2;
      if (effect2.b?.is_pending && (effect2.f & (EFFECT | RENDER_EFFECT | MANAGED_EFFECT)) !== 0 && (effect2.f & REACTION_RAN) === 0) {
        effect2.b.defer_effect(effect2);
        return;
      }
      var e = effect2;
      while (e.parent !== null) {
        e = e.parent;
        var flags2 = e.f;
        if (collected_effects !== null && e === active_effect) {
          if (async_mode_flag) return;
          if ((active_reaction === null || (active_reaction.f & DERIVED) === 0) && !legacy_is_updating_store) {
            return;
          }
        }
        if ((flags2 & (ROOT_EFFECT | BRANCH_EFFECT)) !== 0) {
          if ((flags2 & CLEAN) === 0) {
            return;
          }
          e.f ^= CLEAN;
        }
      }
      this.#roots.push(e);
    }
    #unlink() {
      if (!this.linked) return;
      var prev = this.#prev;
      var next2 = this.#next;
      if (prev === null) {
        first_batch = next2;
      } else {
        prev.#next = next2;
      }
      if (next2 === null) {
        last_batch = prev;
      } else {
        next2.#prev = prev;
      }
      this.linked = false;
    }
  };
  function flushSync(fn) {
    var was_flushing_sync = is_flushing_sync;
    is_flushing_sync = true;
    try {
      var result;
      if (fn) {
        if (current_batch !== null && !current_batch.is_fork) {
          current_batch.flush();
        }
        result = fn();
      }
      while (true) {
        flush_tasks();
        if (current_batch === null) {
          return (
            /** @type {T} */
            result
          );
        }
        current_batch.flush();
      }
    } finally {
      is_flushing_sync = was_flushing_sync;
    }
  }
  function infinite_loop_guard() {
    if (dev_fallback_default) {
      var updates = /* @__PURE__ */ new Map();
      for (
        const source2 of
        /** @type {Batch} */
        current_batch.current.keys()
      ) {
        for (const [stack2, update2] of source2.updated ?? []) {
          var entry = updates.get(stack2);
          if (!entry) {
            entry = { error: update2.error, count: 0 };
            updates.set(stack2, entry);
          }
          entry.count += update2.count;
        }
      }
      for (const update2 of updates.values()) {
        if (update2.error) {
          console.error(update2.error);
        }
      }
    }
    try {
      effect_update_depth_exceeded();
    } catch (error) {
      if (dev_fallback_default) {
        define_property(error, "stack", { value: "" });
      }
      invoke_error_boundary(error, last_scheduled_effect);
    }
  }
  var eager_block_effects = null;
  function flush_queued_effects(effects) {
    var length = effects.length;
    if (length === 0) return;
    var i = 0;
    while (i < length) {
      var effect2 = effects[i++];
      if ((effect2.f & (DESTROYED | INERT)) === 0 && is_dirty(effect2)) {
        eager_block_effects = /* @__PURE__ */ new Set();
        update_effect(effect2);
        if (effect2.deps === null && effect2.first === null && effect2.nodes === null && effect2.teardown === null && effect2.ac === null) {
          unlink_effect(effect2);
        }
        if (eager_block_effects?.size > 0) {
          old_values.clear();
          for (const e of eager_block_effects) {
            if ((e.f & (DESTROYED | INERT)) !== 0) continue;
            const ordered_effects = [e];
            let ancestor = e.parent;
            while (ancestor !== null) {
              if (eager_block_effects.has(ancestor)) {
                eager_block_effects.delete(ancestor);
                ordered_effects.push(ancestor);
              }
              ancestor = ancestor.parent;
            }
            for (let j = ordered_effects.length - 1; j >= 0; j--) {
              const e2 = ordered_effects[j];
              if ((e2.f & (DESTROYED | INERT)) !== 0) continue;
              update_effect(e2);
            }
          }
          eager_block_effects.clear();
        }
      }
    }
    eager_block_effects = null;
  }
  function mark_effects(value, sources, marked, checked) {
    if (marked.has(value)) return;
    marked.add(value);
    if (value.reactions !== null) {
      for (const reaction of value.reactions) {
        const flags2 = reaction.f;
        if ((flags2 & DERIVED) !== 0) {
          mark_effects(
            /** @type {Derived} */
            reaction,
            sources,
            marked,
            checked
          );
        } else if ((flags2 & (ASYNC | BLOCK_EFFECT)) !== 0 && (flags2 & DIRTY) === 0 && depends_on(reaction, sources, checked)) {
          set_signal_status(reaction, DIRTY);
          schedule_effect(
            /** @type {Effect} */
            reaction
          );
        }
      }
    }
  }
  function depends_on(reaction, sources, checked) {
    const depends = checked.get(reaction);
    if (depends !== void 0) return depends;
    if (reaction.deps !== null) {
      for (const dep of reaction.deps) {
        if (includes.call(sources, dep)) {
          return true;
        }
        if ((dep.f & DERIVED) !== 0 && depends_on(
          /** @type {Derived} */
          dep,
          sources,
          checked
        )) {
          checked.set(
            /** @type {Derived} */
            dep,
            true
          );
          return true;
        }
      }
    }
    checked.set(reaction, false);
    return false;
  }
  function schedule_effect(effect2) {
    current_batch.schedule(effect2);
  }
  function reset_branch(effect2, tracked) {
    if ((effect2.f & BRANCH_EFFECT) !== 0 && (effect2.f & CLEAN) !== 0) {
      return;
    }
    if ((effect2.f & DIRTY) !== 0) {
      tracked.d.push(effect2);
    } else if ((effect2.f & MAYBE_DIRTY) !== 0) {
      tracked.m.push(effect2);
    }
    set_signal_status(effect2, CLEAN);
    var e = effect2.first;
    while (e !== null) {
      reset_branch(e, tracked);
      e = e.next;
    }
  }
  function reset_all(effect2) {
    set_signal_status(effect2, CLEAN);
    var e = effect2.first;
    while (e !== null) {
      reset_all(e);
      e = e.next;
    }
  }

  // node_modules/svelte/src/internal/client/reactivity/sources.js
  var eager_effects = /* @__PURE__ */ new Set();
  var old_values = /* @__PURE__ */ new Map();
  function set_eager_effects(v) {
    eager_effects = v;
  }
  var eager_effects_deferred = false;
  function set_eager_effects_deferred() {
    eager_effects_deferred = true;
  }
  function source(v, stack2) {
    var signal = {
      f: 0,
      // TODO ideally we could skip this altogether, but it causes type errors
      v,
      reactions: null,
      equals,
      rv: 0,
      wv: 0
    };
    if (dev_fallback_default && tracing_mode_flag) {
      signal.created = stack2 ?? get_error("created at");
      signal.updated = null;
      signal.set_during_effect = false;
      signal.trace = null;
    }
    return signal;
  }
  // @__NO_SIDE_EFFECTS__
  function state(v, stack2) {
    const s = source(v, stack2);
    push_reaction_value(s);
    return s;
  }
  // @__NO_SIDE_EFFECTS__
  function mutable_source(initial_value, immutable = false, trackable = true) {
    const s = source(initial_value);
    if (!immutable) {
      s.equals = safe_equals;
    }
    if (legacy_mode_flag && trackable && component_context !== null && component_context.l !== null) {
      (component_context.l.s ??= []).push(s);
    }
    return s;
  }
  function set(source2, value, should_proxy = false) {
    if (active_reaction !== null && // since we are untracking the function inside `$inspect.with` we need to add this check
    // to ensure we error if state is set inside an inspect effect
    (!untracking || (active_reaction.f & EAGER_EFFECT) !== 0) && is_runes() && (active_reaction.f & (DERIVED | BLOCK_EFFECT | ASYNC | EAGER_EFFECT)) !== 0 && (current_sources === null || !current_sources.has(source2))) {
      state_unsafe_mutation();
    }
    let new_value = should_proxy ? proxy(value) : value;
    if (dev_fallback_default) {
      tag_proxy(
        new_value,
        /** @type {string} */
        source2.label
      );
    }
    return internal_set(source2, new_value, legacy_updates);
  }
  function internal_set(source2, value, updated_during_traversal = null) {
    if (!source2.equals(value)) {
      if (is_destroying_effect) {
        old_values.set(source2, value);
      } else if (!old_values.has(source2)) {
        old_values.set(source2, source2.v);
      }
      var batch = Batch.ensure();
      batch.capture(source2, value);
      if (dev_fallback_default) {
        if (tracing_mode_flag || active_effect !== null) {
          source2.updated ??= /* @__PURE__ */ new Map();
          const count = (source2.updated.get("")?.count ?? 0) + 1;
          source2.updated.set("", { error: (
            /** @type {any} */
            null
          ), count });
          if (tracing_mode_flag || count > 5) {
            const error = get_error("updated at");
            if (error !== null) {
              let entry = source2.updated.get(error.stack);
              if (!entry) {
                entry = { error, count: 0 };
                source2.updated.set(error.stack, entry);
              }
              entry.count++;
            }
          }
        }
        if (active_effect !== null) {
          source2.set_during_effect = true;
        }
      }
      if ((source2.f & DERIVED) !== 0) {
        const derived2 = (
          /** @type {Derived} */
          source2
        );
        if ((source2.f & DIRTY) !== 0) {
          execute_derived(derived2);
        }
        if (batch_values === null) {
          update_derived_status(derived2);
        }
      }
      source2.wv = increment_write_version();
      mark_reactions(source2, DIRTY, updated_during_traversal);
      if (is_runes() && active_effect !== null && (active_effect.f & CLEAN) !== 0 && (active_effect.f & (BRANCH_EFFECT | ROOT_EFFECT)) === 0) {
        if (untracked_writes === null) {
          set_untracked_writes([source2]);
        } else {
          untracked_writes.push(source2);
        }
      }
      if (!batch.is_fork && eager_effects.size > 0 && !eager_effects_deferred) {
        flush_eager_effects();
      }
    }
    return value;
  }
  function flush_eager_effects() {
    eager_effects_deferred = false;
    for (const effect2 of eager_effects) {
      if ((effect2.f & CLEAN) !== 0) {
        set_signal_status(effect2, MAYBE_DIRTY);
      }
      let dirty;
      try {
        dirty = is_dirty(effect2);
      } catch {
        dirty = true;
      }
      if (dirty) {
        update_effect(effect2);
      }
    }
    eager_effects.clear();
  }
  function increment(source2) {
    set(source2, source2.v + 1);
  }
  function mark_reactions(signal, status, updated_during_traversal) {
    var reactions = signal.reactions;
    if (reactions === null) return;
    var runes = is_runes();
    var length = reactions.length;
    for (var i = 0; i < length; i++) {
      var reaction = reactions[i];
      var flags2 = reaction.f;
      if (!runes && reaction === active_effect) continue;
      var not_dirty = (flags2 & DIRTY) === 0;
      if (not_dirty) {
        set_signal_status(reaction, status);
      }
      if ((flags2 & EAGER_EFFECT) !== 0) {
        eager_effects.add(
          /** @type {Effect} */
          reaction
        );
      } else if ((flags2 & DERIVED) !== 0) {
        var derived2 = (
          /** @type {Derived} */
          reaction
        );
        batch_values?.delete(derived2);
        if ((flags2 & WAS_MARKED) === 0) {
          if (flags2 & CONNECTED && (active_effect === null || (active_effect.f & REACTION_IS_UPDATING) === 0)) {
            reaction.f |= WAS_MARKED;
          }
          mark_reactions(derived2, MAYBE_DIRTY, updated_during_traversal);
        }
      } else if (not_dirty) {
        var effect2 = (
          /** @type {Effect} */
          reaction
        );
        if ((flags2 & BLOCK_EFFECT) !== 0 && eager_block_effects !== null) {
          eager_block_effects.add(effect2);
        }
        if (updated_during_traversal !== null) {
          updated_during_traversal.push(effect2);
        } else {
          schedule_effect(effect2);
        }
      }
    }
  }

  // node_modules/svelte/src/internal/client/proxy.js
  var regex_is_valid_identifier = /^[a-zA-Z_$][a-zA-Z_$0-9]*$/;
  function proxy(value) {
    if (typeof value !== "object" || value === null || STATE_SYMBOL in value || COMPONENT_SYMBOL in value) {
      return value;
    }
    const prototype = get_prototype_of(value);
    if (prototype !== object_prototype && prototype !== array_prototype) {
      return value;
    }
    var sources = /* @__PURE__ */ new Map();
    var is_proxied_array = is_array(value);
    var version = state(0);
    var stack2 = dev_fallback_default && tracing_mode_flag ? get_error("created at") : null;
    var parent_version = update_version;
    var with_parent = (fn) => {
      if (update_version === parent_version) {
        return fn();
      }
      var reaction = active_reaction;
      var version2 = update_version;
      set_active_reaction(null);
      set_update_version(parent_version);
      var result = fn();
      set_active_reaction(reaction);
      set_update_version(version2);
      return result;
    };
    if (is_proxied_array) {
      sources.set("length", state(
        /** @type {any[]} */
        value.length,
        stack2
      ));
      if (dev_fallback_default) {
        value = /** @type {any} */
        inspectable_array(
          /** @type {any[]} */
          value
        );
      }
    }
    var path = "";
    let updating = false;
    function update_path(new_path) {
      if (updating) return;
      updating = true;
      path = new_path;
      tag(version, `${path} version`);
      for (const [prop2, source2] of sources) {
        tag(source2, get_label(path, prop2));
      }
      updating = false;
    }
    return new Proxy(
      /** @type {any} */
      value,
      {
        defineProperty(_, prop2, descriptor) {
          if (!("value" in descriptor) || descriptor.configurable === false || descriptor.enumerable === false || descriptor.writable === false) {
            state_descriptors_fixed();
          }
          var s = sources.get(prop2);
          if (s === void 0) {
            with_parent(() => {
              var s2 = state(descriptor.value, stack2);
              sources.set(prop2, s2);
              if (dev_fallback_default && typeof prop2 === "string") {
                tag(s2, get_label(path, prop2));
              }
              return s2;
            });
          } else {
            set(s, descriptor.value, true);
          }
          return true;
        },
        deleteProperty(target2, prop2) {
          var s = sources.get(prop2);
          if (s === void 0) {
            if (prop2 in target2) {
              const s2 = with_parent(() => state(UNINITIALIZED, stack2));
              sources.set(prop2, s2);
              increment(version);
              if (dev_fallback_default) {
                tag(s2, get_label(path, prop2));
              }
            }
          } else {
            set(s, UNINITIALIZED);
            increment(version);
          }
          return true;
        },
        get(target2, prop2, receiver) {
          if (prop2 === STATE_SYMBOL) {
            return value;
          }
          if (dev_fallback_default && prop2 === PROXY_PATH_SYMBOL) {
            return update_path;
          }
          var s = sources.get(prop2);
          var exists = prop2 in target2;
          if (s === void 0 && (!exists || get_descriptor(target2, prop2)?.writable)) {
            s = with_parent(() => {
              var p = proxy(exists ? target2[prop2] : UNINITIALIZED);
              var s2 = state(p, stack2);
              if (dev_fallback_default) {
                tag(s2, get_label(path, prop2));
              }
              return s2;
            });
            sources.set(prop2, s);
          }
          if (s !== void 0) {
            var v = get2(s);
            return v === UNINITIALIZED ? void 0 : v;
          }
          return Reflect.get(target2, prop2, receiver);
        },
        getOwnPropertyDescriptor(target2, prop2) {
          var descriptor = Reflect.getOwnPropertyDescriptor(target2, prop2);
          if (descriptor && "value" in descriptor) {
            var s = sources.get(prop2);
            if (s) descriptor.value = get2(s);
          } else if (descriptor === void 0) {
            var source2 = sources.get(prop2);
            var value2 = source2?.v;
            if (source2 !== void 0 && value2 !== UNINITIALIZED) {
              return {
                enumerable: true,
                configurable: true,
                value: value2,
                writable: true
              };
            }
          }
          return descriptor;
        },
        has(target2, prop2) {
          if (prop2 === STATE_SYMBOL) {
            return true;
          }
          var s = sources.get(prop2);
          var has = s !== void 0 && s.v !== UNINITIALIZED || Reflect.has(target2, prop2);
          if (s !== void 0 || active_effect !== null && (!has || get_descriptor(target2, prop2)?.writable)) {
            if (s === void 0) {
              s = with_parent(() => {
                var p = has ? proxy(target2[prop2]) : UNINITIALIZED;
                var s2 = state(p, stack2);
                if (dev_fallback_default) {
                  tag(s2, get_label(path, prop2));
                }
                return s2;
              });
              sources.set(prop2, s);
            }
            var value2 = get2(s);
            if (value2 === UNINITIALIZED) {
              return false;
            }
          }
          return has;
        },
        set(target2, prop2, value2, receiver) {
          var s = sources.get(prop2);
          var has = prop2 in target2;
          if (is_proxied_array && prop2 === "length") {
            for (var i = value2; i < /** @type {Source<number>} */
            s.v; i += 1) {
              var other_s = sources.get(i + "");
              if (other_s !== void 0) {
                set(other_s, UNINITIALIZED);
              } else if (i in target2) {
                other_s = with_parent(() => state(UNINITIALIZED, stack2));
                sources.set(i + "", other_s);
                if (dev_fallback_default) {
                  tag(other_s, get_label(path, i));
                }
              }
            }
          }
          if (s === void 0) {
            if (!has || get_descriptor(target2, prop2)?.writable) {
              s = with_parent(() => state(void 0, stack2));
              if (dev_fallback_default) {
                tag(s, get_label(path, prop2));
              }
              set(s, proxy(value2));
              sources.set(prop2, s);
            }
          } else {
            has = s.v !== UNINITIALIZED;
            var p = with_parent(() => proxy(value2));
            set(s, p);
          }
          var descriptor = Reflect.getOwnPropertyDescriptor(target2, prop2);
          if (descriptor?.set) {
            descriptor.set.call(receiver, value2);
          }
          if (!has) {
            if (is_proxied_array && typeof prop2 === "string") {
              var ls = (
                /** @type {Source<number>} */
                sources.get("length")
              );
              var n = Number(prop2);
              if (Number.isInteger(n) && n >= ls.v) {
                set(ls, n + 1);
              }
            }
            increment(version);
          }
          return true;
        },
        ownKeys(target2) {
          get2(version);
          var own_keys = Reflect.ownKeys(target2).filter((key3) => {
            var source3 = sources.get(key3);
            return source3 === void 0 || source3.v !== UNINITIALIZED;
          });
          for (var [key2, source2] of sources) {
            if (source2.v !== UNINITIALIZED && !(key2 in target2)) {
              own_keys.push(key2);
            }
          }
          return own_keys;
        },
        setPrototypeOf() {
          state_prototype_fixed();
        }
      }
    );
  }
  function get_label(path, prop2) {
    if (typeof prop2 === "symbol") return `${path}[Symbol(${prop2.description ?? ""})]`;
    if (regex_is_valid_identifier.test(prop2)) return `${path}.${prop2}`;
    return /^\d+$/.test(prop2) ? `${path}[${prop2}]` : `${path}['${prop2}']`;
  }
  function get_proxied_value(value) {
    try {
      if (value !== null && typeof value === "object" && STATE_SYMBOL in value) {
        return value[STATE_SYMBOL];
      }
    } catch {
    }
    return value;
  }
  function is(a, b) {
    return Object.is(get_proxied_value(a), get_proxied_value(b));
  }
  var ARRAY_MUTATING_METHODS = /* @__PURE__ */ new Set([
    "copyWithin",
    "fill",
    "pop",
    "push",
    "reverse",
    "shift",
    "sort",
    "splice",
    "unshift"
  ]);
  function inspectable_array(array) {
    return new Proxy(array, {
      get(target2, prop2, receiver) {
        var value = Reflect.get(target2, prop2, receiver);
        if (!ARRAY_MUTATING_METHODS.has(
          /** @type {string} */
          prop2
        )) {
          return value;
        }
        return function(...args) {
          set_eager_effects_deferred();
          var result = value.apply(this, args);
          flush_eager_effects();
          return result;
        };
      }
    });
  }

  // node_modules/svelte/src/internal/client/dev/equality.js
  function init_array_prototype_warnings() {
    const array_prototype2 = Array.prototype;
    const cleanup = Array.__svelte_cleanup;
    if (cleanup) {
      cleanup();
    }
    const { indexOf, lastIndexOf, includes: includes2 } = array_prototype2;
    array_prototype2.indexOf = function(item, from_index) {
      const index2 = indexOf.call(this, item, from_index);
      if (index2 === -1) {
        for (let i = from_index ?? 0; i < this.length; i += 1) {
          if (get_proxied_value(this[i]) === item) {
            state_proxy_equality_mismatch("array.indexOf(...)");
            break;
          }
        }
      }
      return index2;
    };
    array_prototype2.lastIndexOf = function(item, from_index) {
      const index2 = lastIndexOf.call(this, item, from_index ?? this.length - 1);
      if (index2 === -1) {
        for (let i = 0; i <= (from_index ?? this.length - 1); i += 1) {
          if (get_proxied_value(this[i]) === item) {
            state_proxy_equality_mismatch("array.lastIndexOf(...)");
            break;
          }
        }
      }
      return index2;
    };
    array_prototype2.includes = function(item, from_index) {
      const has = includes2.call(this, item, from_index);
      if (!has) {
        for (let i = 0; i < this.length; i += 1) {
          if (get_proxied_value(this[i]) === item) {
            state_proxy_equality_mismatch("array.includes(...)");
            break;
          }
        }
      }
      return has;
    };
    Array.__svelte_cleanup = () => {
      array_prototype2.indexOf = indexOf;
      array_prototype2.lastIndexOf = lastIndexOf;
      array_prototype2.includes = includes2;
    };
  }

  // node_modules/svelte/src/internal/client/dom/operations.js
  var $window;
  var $document;
  var is_firefox;
  var first_child_getter;
  var next_sibling_getter;
  function init_operations() {
    if ($window !== void 0) {
      return;
    }
    $window = window;
    $document = document;
    is_firefox = /Firefox/.test(navigator.userAgent);
    var element_prototype = Element.prototype;
    var node_prototype = Node.prototype;
    var text_prototype = Text.prototype;
    first_child_getter = get_descriptor(node_prototype, "firstChild").get;
    next_sibling_getter = get_descriptor(node_prototype, "nextSibling").get;
    if (is_extensible(element_prototype)) {
      element_prototype[CLASS_CACHE] = void 0;
      element_prototype[ATTRIBUTES_CACHE] = null;
      element_prototype[STYLE_CACHE] = void 0;
      element_prototype.__e = void 0;
    }
    if (is_extensible(text_prototype)) {
      text_prototype[TEXT_CACHE] = void 0;
    }
    if (dev_fallback_default) {
      element_prototype.__svelte_meta = null;
      init_array_prototype_warnings();
    }
  }
  function create_text(value = "") {
    return document.createTextNode(value);
  }
  // @__NO_SIDE_EFFECTS__
  function get_first_child(node) {
    return (
      /** @type {TemplateNode | null} */
      first_child_getter.call(node)
    );
  }
  // @__NO_SIDE_EFFECTS__
  function get_next_sibling(node) {
    return (
      /** @type {TemplateNode | null} */
      next_sibling_getter.call(node)
    );
  }
  function child(node, is_text) {
    if (!hydrating) {
      return /* @__PURE__ */ get_first_child(node);
    }
    var child2 = /* @__PURE__ */ get_first_child(hydrate_node);
    if (child2 === null) {
      child2 = hydrate_node.appendChild(create_text());
    } else if (is_text && child2.nodeType !== TEXT_NODE) {
      var text2 = create_text();
      child2?.before(text2);
      set_hydrate_node(text2);
      return text2;
    }
    if (is_text) {
      merge_text_nodes(
        /** @type {Text} */
        child2
      );
    }
    set_hydrate_node(child2);
    return child2;
  }
  function first_child(node, is_text = false) {
    if (!hydrating) {
      var first = /* @__PURE__ */ get_first_child(node);
      if (first instanceof Comment && first.data === "") return /* @__PURE__ */ get_next_sibling(first);
      return first;
    }
    if (is_text) {
      if (hydrate_node?.nodeType !== TEXT_NODE) {
        var text2 = create_text();
        hydrate_node?.before(text2);
        set_hydrate_node(text2);
        return text2;
      }
      merge_text_nodes(
        /** @type {Text} */
        hydrate_node
      );
    }
    return hydrate_node;
  }
  function only_child(node, is_text = false) {
    if (!hydrating) {
      return /* @__PURE__ */ get_first_child(node);
    }
    var first = child(node, is_text);
    reset(node);
    return first;
  }
  function sibling(node, count = 1, is_text = false) {
    let next_sibling = hydrating ? hydrate_node : node;
    var last_sibling;
    while (count--) {
      last_sibling = next_sibling;
      next_sibling = /** @type {TemplateNode} */
      /* @__PURE__ */ get_next_sibling(next_sibling);
    }
    if (!hydrating) {
      return next_sibling;
    }
    if (is_text) {
      if (next_sibling?.nodeType !== TEXT_NODE) {
        var text2 = create_text();
        if (next_sibling === null) {
          last_sibling?.after(text2);
        } else {
          next_sibling.before(text2);
        }
        set_hydrate_node(text2);
        return text2;
      }
      merge_text_nodes(
        /** @type {Text} */
        next_sibling
      );
    }
    set_hydrate_node(next_sibling);
    return next_sibling;
  }
  function clear_text_content(node) {
    node.textContent = "";
  }
  function should_defer_append() {
    if (!async_mode_flag) return false;
    if (eager_block_effects !== null) return false;
    var flags2 = (
      /** @type {Effect} */
      active_effect.f
    );
    return (flags2 & REACTION_RAN) !== 0;
  }
  function create_element(tag2, namespace, is2) {
    if (namespace == null || namespace === NAMESPACE_HTML) {
      return (
        /** @type {T extends keyof HTMLElementTagNameMap ? HTMLElementTagNameMap[T] : Element} */
        is2 ? document.createElement(tag2, { is: is2 }) : document.createElement(tag2)
      );
    }
    return (
      /** @type {T extends keyof HTMLElementTagNameMap ? HTMLElementTagNameMap[T] : Element} */
      is2 ? document.createElementNS(namespace, tag2, { is: is2 }) : document.createElementNS(namespace, tag2)
    );
  }
  function merge_text_nodes(text2) {
    if (
      /** @type {string} */
      text2.nodeValue.length < 65536
    ) {
      return;
    }
    let next2 = text2.nextSibling;
    while (next2 !== null && next2.nodeType === TEXT_NODE) {
      next2.remove();
      text2.nodeValue += /** @type {string} */
      next2.nodeValue;
      next2 = text2.nextSibling;
    }
  }

  // node_modules/svelte/src/internal/client/error-handling.js
  var adjustments = /* @__PURE__ */ new WeakMap();
  function handle_error(error) {
    var effect2 = active_effect;
    if (effect2 === null) {
      active_reaction.f |= ERROR_VALUE;
      return error;
    }
    if (dev_fallback_default && error instanceof Error && !adjustments.has(error)) {
      adjustments.set(error, get_adjustments(error, effect2));
    }
    if ((effect2.f & REACTION_RAN) === 0 && (effect2.f & EFFECT) === 0) {
      if (dev_fallback_default && !effect2.parent && error instanceof Error) {
        apply_adjustments(error);
      }
      throw error;
    }
    invoke_error_boundary(error, effect2);
  }
  function invoke_error_boundary(error, effect2) {
    if (effect2 !== null && (effect2.f & DESTROYED) !== 0) {
      return;
    }
    while (effect2 !== null) {
      if ((effect2.f & BOUNDARY_EFFECT) !== 0 && (effect2.f & (DESTROYED | DESTROYING)) === 0) {
        if ((effect2.f & REACTION_RAN) === 0) {
          throw error;
        }
        try {
          effect2.b.error(error);
          return;
        } catch (e) {
          error = e;
        }
      }
      effect2 = effect2.parent;
    }
    if (dev_fallback_default && error instanceof Error) {
      apply_adjustments(error);
    }
    throw error;
  }
  function get_adjustments(error, effect2) {
    const message_descriptor = get_descriptor(error, "message");
    if (message_descriptor && !message_descriptor.configurable) return;
    var indent = is_firefox ? "  " : "	";
    var component_stack = `
${indent}in ${effect2.fn?.name || "<unknown>"}`;
    var context = effect2.ctx;
    while (context !== null) {
      component_stack += `
${indent}in ${context.function?.[FILENAME].split("/").pop()}`;
      context = context.p;
    }
    return {
      message: error.message + `
${component_stack}
`,
      stack: error.stack?.split("\n").filter((line) => !line.includes("svelte/src/internal")).join("\n")
    };
  }
  function apply_adjustments(error) {
    const adjusted = adjustments.get(error);
    if (adjusted) {
      define_property(error, "message", {
        value: adjusted.message
      });
      define_property(error, "stack", {
        value: adjusted.stack
      });
    }
  }

  // node_modules/svelte/src/internal/client/reactivity/effects.js
  function validate_effect(rune) {
    if (active_effect === null) {
      if (active_reaction === null) {
        effect_orphan(rune);
      }
      effect_in_unowned_derived();
    }
    if (is_destroying_effect) {
      effect_in_teardown(rune);
    }
  }
  function push_effect(effect2, parent_effect) {
    var parent_last = parent_effect.last;
    if (parent_last === null) {
      parent_effect.last = parent_effect.first = effect2;
    } else {
      parent_last.next = effect2;
      effect2.prev = parent_last;
      parent_effect.last = effect2;
    }
  }
  function create_effect(type, fn) {
    var parent = active_effect;
    if (dev_fallback_default) {
      while (parent !== null && (parent.f & EAGER_EFFECT) !== 0) {
        parent = parent.parent;
      }
    }
    if (parent !== null && (parent.f & INERT) !== 0) {
      type |= INERT;
    }
    var effect2 = {
      ctx: component_context,
      deps: null,
      nodes: null,
      f: type | DIRTY | CONNECTED,
      first: null,
      fn,
      last: null,
      next: null,
      parent,
      b: parent && parent.b,
      prev: null,
      teardown: null,
      wv: 0,
      ac: null
    };
    if (dev_fallback_default) {
      effect2.component_function = dev_current_component_function;
    }
    current_batch?.register_created_effect(effect2);
    var e = effect2;
    if ((type & EFFECT) !== 0) {
      if (collected_effects !== null) {
        collected_effects.push(effect2);
      } else {
        Batch.ensure().schedule(effect2);
      }
    } else if (fn !== null) {
      try {
        update_effect(effect2);
      } catch (e2) {
        destroy_effect(effect2);
        throw e2;
      }
      if (e.deps === null && e.teardown === null && e.nodes === null && e.first === e.last && // either `null`, or a singular child
      (e.f & EFFECT_PRESERVED) === 0) {
        e = e.first;
        if ((type & BLOCK_EFFECT) !== 0 && (type & EFFECT_TRANSPARENT) !== 0 && e !== null) {
          e.f |= EFFECT_TRANSPARENT;
        }
      }
    }
    if (e !== null) {
      e.parent = parent;
      if (parent !== null) {
        push_effect(e, parent);
      }
      if (active_reaction !== null && (active_reaction.f & DERIVED) !== 0 && (type & ROOT_EFFECT) === 0) {
        var derived2 = (
          /** @type {Derived} */
          active_reaction
        );
        (derived2.effects ??= []).push(e);
      }
    }
    return effect2;
  }
  function effect_tracking() {
    return active_reaction !== null && !untracking;
  }
  function teardown(fn) {
    const effect2 = create_effect(RENDER_EFFECT, null);
    set_signal_status(effect2, CLEAN);
    effect2.teardown = fn;
    return effect2;
  }
  function user_effect(fn) {
    validate_effect("$effect");
    if (dev_fallback_default) {
      define_property(fn, "name", {
        value: "$effect"
      });
    }
    var flags2 = (
      /** @type {Effect} */
      active_effect.f
    );
    var defer = !active_reaction && (flags2 & BRANCH_EFFECT) !== 0 && component_context !== null && !component_context.i;
    if (defer) {
      var context = (
        /** @type {ComponentContext} */
        component_context
      );
      (context.e ??= []).push(fn);
    } else {
      return create_user_effect(fn);
    }
  }
  function create_user_effect(fn) {
    return create_effect(EFFECT | USER_EFFECT, fn);
  }
  function effect_root(fn) {
    Batch.ensure();
    const effect2 = create_effect(ROOT_EFFECT | EFFECT_PRESERVED, fn);
    return () => {
      destroy_effect(effect2);
    };
  }
  function component_root(fn) {
    Batch.ensure();
    const effect2 = create_effect(ROOT_EFFECT | EFFECT_PRESERVED, fn);
    return (options = {}) => {
      return new Promise((fulfil) => {
        if (options.outro) {
          pause_effect(effect2, () => {
            destroy_effect(effect2);
            fulfil(void 0);
          });
        } else {
          destroy_effect(effect2);
          fulfil(void 0);
        }
      });
    };
  }
  function effect(fn) {
    return create_effect(EFFECT, fn);
  }
  function async_effect(fn) {
    return create_effect(ASYNC | EFFECT_PRESERVED, fn);
  }
  function render_effect(fn, flags2 = 0) {
    return create_effect(RENDER_EFFECT | flags2, fn);
  }
  function template_effect(fn, sync = [], async2 = [], blockers = []) {
    flatten(blockers, sync, async2, (values) => {
      create_effect(RENDER_EFFECT, () => {
        fn(...values.map(get2));
      });
    });
  }
  function block(fn, flags2 = 0) {
    var effect2 = create_effect(BLOCK_EFFECT | flags2, fn);
    if (dev_fallback_default) {
      effect2.dev_stack = dev_stack;
    }
    return effect2;
  }
  function branch(fn) {
    return create_effect(BRANCH_EFFECT | EFFECT_PRESERVED, fn);
  }
  function execute_effect_teardown(effect2) {
    var teardown2 = effect2.teardown;
    if (teardown2 !== null) {
      const previously_destroying_effect = is_destroying_effect;
      const previous_reaction = active_reaction;
      set_is_destroying_effect(true);
      set_active_reaction(null);
      try {
        teardown2.call(null);
      } catch (error) {
        invoke_error_boundary(error, effect2.parent);
      } finally {
        set_is_destroying_effect(previously_destroying_effect);
        set_active_reaction(previous_reaction);
      }
    }
  }
  function destroy_effect_children(signal, remove_dom = false) {
    var effect2 = signal.first;
    signal.first = signal.last = null;
    while (effect2 !== null) {
      const controller = effect2.ac;
      if (controller !== null) {
        without_reactive_context(() => {
          controller.abort(STALE_REACTION);
        });
      }
      var next2 = effect2.next;
      if ((effect2.f & ROOT_EFFECT) !== 0) {
        effect2.parent = null;
      } else {
        destroy_effect(effect2, remove_dom);
      }
      effect2 = next2;
    }
  }
  function destroy_block_effect_children(signal) {
    var effect2 = signal.first;
    while (effect2 !== null) {
      var next2 = effect2.next;
      if ((effect2.f & BRANCH_EFFECT) === 0) {
        destroy_effect(effect2);
      }
      effect2 = next2;
    }
  }
  function destroy_effect(effect2, remove_dom = true) {
    var removed = false;
    if ((remove_dom || (effect2.f & HEAD_EFFECT) !== 0) && effect2.nodes !== null && effect2.nodes.end !== null) {
      remove_effect_dom(
        effect2.nodes.start,
        /** @type {TemplateNode} */
        effect2.nodes.end
      );
      removed = true;
    }
    effect2.f |= DESTROYING;
    destroy_effect_children(effect2, remove_dom && !removed);
    remove_reactions(effect2, 0);
    var transitions = effect2.nodes && effect2.nodes.t;
    if (transitions !== null) {
      for (const transition2 of transitions) {
        transition2.stop();
      }
    }
    execute_effect_teardown(effect2);
    effect2.f ^= DESTROYING;
    effect2.f |= DESTROYED;
    var parent = effect2.parent;
    if (parent !== null && parent.first !== null) {
      unlink_effect(effect2);
    }
    if (dev_fallback_default) {
      effect2.component_function = null;
    }
    effect2.next = effect2.prev = effect2.teardown = effect2.ctx = effect2.deps = effect2.fn = effect2.nodes = effect2.ac = effect2.b = null;
  }
  function remove_effect_dom(node, end) {
    while (node !== null) {
      var next2 = node === end ? null : get_next_sibling(node);
      node.remove();
      node = next2;
    }
  }
  function unlink_effect(effect2) {
    var parent = effect2.parent;
    var prev = effect2.prev;
    var next2 = effect2.next;
    if (prev !== null) prev.next = next2;
    if (next2 !== null) next2.prev = prev;
    if (parent !== null) {
      if (parent.first === effect2) parent.first = next2;
      if (parent.last === effect2) parent.last = prev;
    }
  }
  function pause_effect(effect2, callback, destroy = true) {
    var transitions = [];
    effect2.f |= PAUSED;
    pause_children(effect2, transitions, true);
    var fn = () => {
      if (destroy) destroy_effect(effect2);
      if (callback) callback();
    };
    var remaining = transitions.length;
    if (remaining > 0) {
      var check = () => --remaining || fn();
      for (var transition2 of transitions) {
        transition2.out(check);
      }
    } else {
      fn();
    }
  }
  function pause_children(effect2, transitions, local) {
    if ((effect2.f & INERT) !== 0) return;
    effect2.f ^= INERT;
    var t = effect2.nodes && effect2.nodes.t;
    if (t !== null) {
      for (const transition2 of t) {
        if (transition2.is_global || local) {
          transitions.push(transition2);
        }
      }
    }
    var child2 = effect2.first;
    while (child2 !== null) {
      var sibling2 = child2.next;
      if ((child2.f & ROOT_EFFECT) === 0) {
        var transparent = (child2.f & EFFECT_TRANSPARENT) !== 0 || // If this is a branch effect without a block effect parent,
        // it means the parent block effect was pruned. In that case,
        // transparency information was transferred to the branch effect.
        (child2.f & BRANCH_EFFECT) !== 0 && (effect2.f & BLOCK_EFFECT) !== 0;
        pause_children(child2, transitions, transparent ? local : false);
      }
      child2 = sibling2;
    }
  }
  function resume_effect(effect2) {
    effect2.f &= ~PAUSED;
    resume_children(effect2, true);
  }
  function resume_children(effect2, local) {
    if ((effect2.f & PAUSED) !== 0) return;
    if ((effect2.f & INERT) === 0) return;
    effect2.f ^= INERT;
    if ((effect2.f & CLEAN) === 0) {
      set_signal_status(effect2, DIRTY);
      Batch.ensure().schedule(effect2);
    }
    var child2 = effect2.first;
    while (child2 !== null) {
      var sibling2 = child2.next;
      var transparent = (child2.f & EFFECT_TRANSPARENT) !== 0 || (child2.f & BRANCH_EFFECT) !== 0;
      resume_children(child2, transparent ? local : false);
      child2 = sibling2;
    }
    var t = effect2.nodes && effect2.nodes.t;
    if (t !== null) {
      for (const transition2 of t) {
        if (transition2.is_global || local) {
          transition2.in();
        }
      }
    }
  }
  function move_effect(effect2, fragment) {
    if (!effect2.nodes) return;
    var node = effect2.nodes.start;
    var end = effect2.nodes.end;
    while (node !== null) {
      var next2 = node === end ? null : get_next_sibling(node);
      fragment.append(node);
      node = next2;
    }
  }

  // node_modules/svelte/src/internal/client/legacy.js
  var captured_signals = null;

  // node_modules/svelte/src/internal/client/runtime.js
  var is_updating_effect = false;
  var is_destroying_effect = false;
  function set_is_destroying_effect(value) {
    is_destroying_effect = value;
  }
  var active_reaction = null;
  var untracking = false;
  function set_active_reaction(reaction) {
    active_reaction = reaction;
  }
  var active_effect = null;
  function set_active_effect(effect2) {
    active_effect = effect2;
  }
  var current_sources = null;
  function push_reaction_value(value) {
    if (active_reaction !== null && (!async_mode_flag || (active_reaction.f & DERIVED) !== 0)) {
      (current_sources ??= /* @__PURE__ */ new Set()).add(value);
    }
  }
  var new_deps = null;
  var skipped_deps = 0;
  var untracked_writes = null;
  function set_untracked_writes(value) {
    untracked_writes = value;
  }
  var write_version = 1;
  var read_version = 0;
  var update_version = read_version;
  function set_update_version(value) {
    update_version = value;
  }
  function increment_write_version() {
    return ++write_version;
  }
  function is_dirty(reaction) {
    var flags2 = reaction.f;
    if ((flags2 & DIRTY) !== 0) {
      return true;
    }
    if (flags2 & DERIVED) {
      reaction.f &= ~WAS_MARKED;
    }
    if ((flags2 & MAYBE_DIRTY) !== 0) {
      var dependencies = (
        /** @type {Value[]} */
        reaction.deps
      );
      var length = dependencies.length;
      for (var i = 0; i < length; i++) {
        var dependency = dependencies[i];
        if (is_dirty(
          /** @type {Derived} */
          dependency
        )) {
          update_derived(
            /** @type {Derived} */
            dependency
          );
        }
        if (dependency.wv > reaction.wv) {
          return true;
        }
      }
      if ((flags2 & CONNECTED) !== 0 && // During time traveling we don't want to reset the status so that
      // traversal of the graph in the other batches still happens
      batch_values === null) {
        set_signal_status(reaction, CLEAN);
      }
    }
    return false;
  }
  function schedule_possible_effect_self_invalidation(signal, effect2, root11 = true) {
    var reactions = signal.reactions;
    if (reactions === null) return;
    if (!async_mode_flag && current_sources !== null && current_sources.has(signal)) {
      return;
    }
    for (var i = 0; i < reactions.length; i++) {
      var reaction = reactions[i];
      if ((reaction.f & DERIVED) !== 0) {
        schedule_possible_effect_self_invalidation(
          /** @type {Derived} */
          reaction,
          effect2,
          false
        );
      } else if (effect2 === reaction) {
        if (root11) {
          set_signal_status(reaction, DIRTY);
        } else if ((reaction.f & CLEAN) !== 0) {
          set_signal_status(reaction, MAYBE_DIRTY);
        }
        schedule_effect(
          /** @type {Effect} */
          reaction
        );
      }
    }
  }
  function update_reaction(reaction) {
    var previous_deps = new_deps;
    var previous_skipped_deps = skipped_deps;
    var previous_untracked_writes = untracked_writes;
    var previous_reaction = active_reaction;
    var previous_sources = current_sources;
    var previous_component_context = component_context;
    var previous_untracking = untracking;
    var previous_update_version = update_version;
    var flags2 = reaction.f;
    new_deps = /** @type {null | Value[]} */
    null;
    skipped_deps = 0;
    untracked_writes = null;
    active_reaction = (flags2 & (BRANCH_EFFECT | ROOT_EFFECT)) === 0 ? reaction : null;
    current_sources = null;
    set_component_context(reaction.ctx);
    untracking = false;
    update_version = ++read_version;
    if (reaction.ac !== null) {
      without_reactive_context(() => {
        reaction.ac.abort(STALE_REACTION);
      });
      reaction.ac = null;
    }
    try {
      reaction.f |= REACTION_IS_UPDATING;
      var fn = (
        /** @type {Function} */
        reaction.fn
      );
      var result = fn();
      reaction.f |= REACTION_RAN;
      var deps = update_dependencies(reaction);
      if (is_runes() && untracked_writes !== null && !untracking && deps !== null && (reaction.f & (DERIVED | MAYBE_DIRTY | DIRTY)) === 0) {
        for (var i = 0; i < /** @type {Source[]} */
        untracked_writes.length; i++) {
          schedule_possible_effect_self_invalidation(
            untracked_writes[i],
            /** @type {Effect} */
            reaction
          );
        }
      }
      if (previous_reaction !== null && previous_reaction !== reaction) {
        read_version++;
        if (previous_reaction.deps !== null) {
          for (let i2 = 0; i2 < previous_skipped_deps; i2 += 1) {
            previous_reaction.deps[i2].rv = read_version;
          }
        }
        if (previous_deps !== null) {
          for (const dep of previous_deps) {
            dep.rv = read_version;
          }
        }
        if (untracked_writes !== null) {
          if (previous_untracked_writes === null) {
            previous_untracked_writes = untracked_writes;
          } else {
            previous_untracked_writes.push(.../** @type {Source[]} */
            untracked_writes);
          }
        }
      }
      if ((reaction.f & ERROR_VALUE) !== 0) {
        reaction.f ^= ERROR_VALUE;
      }
      return result;
    } catch (error) {
      update_dependencies(reaction);
      return handle_error(error);
    } finally {
      reaction.f ^= REACTION_IS_UPDATING;
      new_deps = previous_deps;
      skipped_deps = previous_skipped_deps;
      untracked_writes = previous_untracked_writes;
      active_reaction = previous_reaction;
      current_sources = previous_sources;
      set_component_context(previous_component_context);
      untracking = previous_untracking;
      update_version = previous_update_version;
    }
  }
  function update_dependencies(reaction) {
    var deps = reaction.deps;
    var is_fork = current_batch?.is_fork;
    if (new_deps !== null) {
      var i;
      if (!is_fork) {
        remove_reactions(reaction, skipped_deps);
      }
      if (deps !== null && skipped_deps > 0) {
        deps.length = skipped_deps + new_deps.length;
        for (i = 0; i < new_deps.length; i++) {
          deps[skipped_deps + i] = new_deps[i];
        }
      } else {
        reaction.deps = deps = new_deps;
      }
      if (effect_tracking() && (reaction.f & CONNECTED) !== 0) {
        for (i = skipped_deps; i < deps.length; i++) {
          (deps[i].reactions ??= []).push(reaction);
        }
      }
    } else if (!is_fork && deps !== null && skipped_deps < deps.length) {
      remove_reactions(reaction, skipped_deps);
      deps.length = skipped_deps;
    }
    return deps;
  }
  function remove_reaction(signal, dependency) {
    let reactions = dependency.reactions;
    if (reactions !== null) {
      var index2 = index_of.call(reactions, signal);
      if (index2 !== -1) {
        var new_length = reactions.length - 1;
        if (new_length === 0) {
          reactions = dependency.reactions = null;
        } else {
          reactions[index2] = reactions[new_length];
          reactions.pop();
        }
      }
    }
    if (reactions === null && (dependency.f & DERIVED) !== 0 && // Destroying a child effect while updating a parent effect can cause a dependency to appear
    // to be unused, when in fact it is used by the currently-updating parent. Checking `new_deps`
    // allows us to skip the expensive work of disconnecting and immediately reconnecting it
    (new_deps === null || !includes.call(new_deps, dependency))) {
      var derived2 = (
        /** @type {Derived} */
        dependency
      );
      if ((derived2.f & CONNECTED) !== 0) {
        derived2.f ^= CONNECTED;
        derived2.f &= ~WAS_MARKED;
      }
      if (derived2.v !== UNINITIALIZED) {
        update_derived_status(derived2);
      }
      if (derived2.ac !== null) {
        without_reactive_context(() => {
          derived2.ac.abort(STALE_REACTION);
          derived2.ac = null;
          set_signal_status(derived2, DIRTY);
        });
      }
      freeze_derived_effects(derived2);
      remove_reactions(derived2, 0);
    }
  }
  function remove_reactions(signal, start_index) {
    var dependencies = signal.deps;
    if (dependencies === null) return;
    for (var i = start_index; i < dependencies.length; i++) {
      remove_reaction(signal, dependencies[i]);
    }
  }
  function update_effect(effect2) {
    var flags2 = effect2.f;
    if ((flags2 & DESTROYED) !== 0) {
      return;
    }
    set_signal_status(effect2, CLEAN);
    var previous_effect = active_effect;
    var was_updating_effect = is_updating_effect;
    active_effect = effect2;
    is_updating_effect = (flags2 & (BRANCH_EFFECT | ROOT_EFFECT)) === 0;
    if (dev_fallback_default) {
      var previous_component_fn = dev_current_component_function;
      set_dev_current_component_function(effect2.component_function);
      var previous_stack = (
        /** @type {any} */
        dev_stack
      );
      set_dev_stack(effect2.dev_stack ?? dev_stack);
    }
    try {
      if ((flags2 & (BLOCK_EFFECT | MANAGED_EFFECT)) !== 0) {
        destroy_block_effect_children(effect2);
      } else {
        destroy_effect_children(effect2);
      }
      execute_effect_teardown(effect2);
      var teardown2 = update_reaction(effect2);
      effect2.teardown = typeof teardown2 === "function" ? teardown2 : null;
      effect2.wv = write_version;
      if (dev_fallback_default && tracing_mode_flag && (effect2.f & DIRTY) !== 0 && effect2.deps !== null) {
        for (var dep of effect2.deps) {
          if (dep.set_during_effect) {
            dep.wv = increment_write_version();
            dep.set_during_effect = false;
          }
        }
      }
    } finally {
      is_updating_effect = was_updating_effect;
      active_effect = previous_effect;
      if (dev_fallback_default) {
        set_dev_current_component_function(previous_component_fn);
        set_dev_stack(previous_stack);
      }
    }
  }
  async function tick() {
    if (async_mode_flag) {
      return new Promise((f) => {
        requestAnimationFrame(() => f());
        setTimeout(() => f());
      });
    }
    await Promise.resolve();
    flushSync();
  }
  function get2(signal) {
    var flags2 = signal.f;
    var is_derived = (flags2 & DERIVED) !== 0;
    captured_signals?.add(signal);
    if (active_reaction !== null && !untracking) {
      var destroyed = active_effect !== null && (active_effect.f & DESTROYED) !== 0;
      if (!destroyed && (current_sources === null || !current_sources.has(signal))) {
        var deps = active_reaction.deps;
        if ((active_reaction.f & REACTION_IS_UPDATING) !== 0) {
          if (signal.rv < read_version) {
            signal.rv = read_version;
            if (new_deps === null && deps !== null && deps[skipped_deps] === signal) {
              skipped_deps++;
            } else if (new_deps === null) {
              new_deps = [signal];
            } else {
              new_deps.push(signal);
            }
          }
        } else {
          active_reaction.deps ??= [];
          if (!includes.call(active_reaction.deps, signal)) {
            active_reaction.deps.push(signal);
          }
          var reactions = signal.reactions;
          if (reactions === null) {
            signal.reactions = [active_reaction];
          } else if (!includes.call(reactions, active_reaction)) {
            reactions.push(active_reaction);
          }
        }
      }
    }
    if (dev_fallback_default) {
      if (!untracking && reactivity_loss_tracker && // By checking that current/previous batch are null we filter out false positives.
      // reactivity_loss_tracker is only reset after a microtask, so if a flush happens
      // before that, we get warnings for things we shouldn't warn on.
      current_batch === null && previous_batch === null && !reactivity_loss_tracker.warned && (reactivity_loss_tracker.effect.f & REACTION_IS_UPDATING) === 0 && !reactivity_loss_tracker.effect_deps.has(signal)) {
        reactivity_loss_tracker.warned = true;
        await_reactivity_loss(
          /** @type {string} */
          signal.label
        );
        var trace2 = get_error("traced at");
        if (trace2) console.warn(trace2);
      }
      recent_async_deriveds.delete(signal);
      if (tracing_mode_flag && !untracking && tracing_expressions !== null && active_reaction !== null && tracing_expressions.reaction === active_reaction) {
        if (signal.trace) {
          signal.trace();
        } else {
          trace2 = get_error("traced at");
          if (trace2) {
            var entry = tracing_expressions.entries.get(signal);
            if (entry === void 0) {
              entry = { traces: [] };
              tracing_expressions.entries.set(signal, entry);
            }
            var last = entry.traces[entry.traces.length - 1];
            if (trace2.stack !== last?.stack) {
              entry.traces.push(trace2);
            }
          }
        }
      }
    }
    if (is_destroying_effect && old_values.has(signal)) {
      return old_values.get(signal);
    }
    if (is_derived) {
      var derived2 = (
        /** @type {Derived} */
        signal
      );
      if (is_destroying_effect) {
        var value = derived2.v;
        if ((derived2.f & CLEAN) === 0 && derived2.reactions !== null || depends_on_old_values(derived2)) {
          value = execute_derived(derived2);
        }
        old_values.set(derived2, value);
        return value;
      }
      var should_connect = (derived2.f & CONNECTED) === 0 && !untracking && active_reaction !== null && (is_updating_effect || (active_reaction.f & CONNECTED) !== 0);
      var is_new = (derived2.f & REACTION_RAN) === 0;
      if (is_dirty(derived2)) {
        if (should_connect) {
          derived2.f |= CONNECTED;
        }
        update_derived(derived2);
      }
      if (should_connect && !is_new) {
        unfreeze_derived_effects(derived2);
        reconnect(derived2);
      }
    }
    if (batch_values?.has(signal)) {
      return batch_values.get(signal);
    }
    if ((signal.f & ERROR_VALUE) !== 0) {
      throw signal.v;
    }
    return signal.v;
  }
  function reconnect(derived2) {
    derived2.f |= CONNECTED;
    if (derived2.deps === null) return;
    for (const dep of derived2.deps) {
      (dep.reactions ??= []).push(derived2);
      if ((dep.f & DERIVED) !== 0 && (dep.f & CONNECTED) === 0) {
        unfreeze_derived_effects(
          /** @type {Derived} */
          dep
        );
        reconnect(
          /** @type {Derived} */
          dep
        );
      }
    }
  }
  function depends_on_old_values(derived2) {
    if (derived2.v === UNINITIALIZED) return true;
    if (derived2.deps === null) return false;
    for (const dep of derived2.deps) {
      if (old_values.has(dep)) {
        return true;
      }
      if ((dep.f & DERIVED) !== 0 && depends_on_old_values(
        /** @type {Derived} */
        dep
      )) {
        return true;
      }
    }
    return false;
  }
  function untrack(fn) {
    var previous_untracking = untracking;
    try {
      untracking = true;
      return fn();
    } finally {
      untracking = previous_untracking;
    }
  }

  // node_modules/svelte/src/utils.js
  var DOM_BOOLEAN_ATTRIBUTES = [
    "allowfullscreen",
    "async",
    "autofocus",
    "autoplay",
    "checked",
    "controls",
    "default",
    "disabled",
    "formnovalidate",
    "indeterminate",
    "inert",
    "ismap",
    "loop",
    "multiple",
    "muted",
    "nomodule",
    "novalidate",
    "open",
    "playsinline",
    "readonly",
    "required",
    "reversed",
    "seamless",
    "selected",
    "webkitdirectory",
    "defer",
    "disablepictureinpicture",
    "disableremoteplayback"
  ];
  var DOM_PROPERTIES = [
    ...DOM_BOOLEAN_ATTRIBUTES,
    "formNoValidate",
    "isMap",
    "noModule",
    "playsInline",
    "readOnly",
    "value",
    "volume",
    "defaultValue",
    "defaultChecked",
    "srcObject",
    "noValidate",
    "allowFullscreen",
    "disablePictureInPicture",
    "disableRemotePlayback"
  ];
  var PASSIVE_EVENTS = ["touchstart", "touchmove"];
  function is_passive_event(name) {
    return PASSIVE_EVENTS.includes(name);
  }
  var STATE_CREATION_RUNES = (
    /** @type {const} */
    [
      "$state",
      "$state.raw",
      "$derived",
      "$derived.by"
    ]
  );
  var RUNES = (
    /** @type {const} */
    [
      ...STATE_CREATION_RUNES,
      "$state.eager",
      "$state.snapshot",
      "$props",
      "$props.id",
      "$bindable",
      "$effect",
      "$effect.pre",
      "$effect.tracking",
      "$effect.root",
      "$effect.pending",
      "$inspect",
      "$inspect().with",
      "$inspect.trace",
      "$host"
    ]
  );

  // node_modules/svelte/src/internal/client/dev/css.js
  var all_styles = /* @__PURE__ */ new Map();
  function register_style(hash2, style) {
    var styles = all_styles.get(hash2);
    if (!styles) {
      styles = /* @__PURE__ */ new Set();
      all_styles.set(hash2, styles);
    }
    styles.add(style);
  }

  // node_modules/svelte/src/internal/client/dom/elements/events.js
  var event_symbol = /* @__PURE__ */ Symbol("events");
  var all_registered_events = /* @__PURE__ */ new Set();
  var root_event_handles = /* @__PURE__ */ new Set();
  function create_event(event_name, dom, handler, options = {}) {
    function target_handler(event2) {
      if (!options.capture) {
        handle_event_propagation.call(dom, event2);
      }
      if (!event2.cancelBubble) {
        return without_reactive_context(() => {
          return handler?.call(this, event2);
        });
      }
    }
    if (event_name.startsWith("pointer") || event_name.startsWith("touch") || event_name === "wheel") {
      queue_micro_task(() => {
        dom.addEventListener(event_name, target_handler, options);
      });
    } else {
      dom.addEventListener(event_name, target_handler, options);
    }
    return target_handler;
  }
  function event(event_name, dom, handler, capture2, passive2) {
    var options = { capture: capture2, passive: passive2 };
    var target_handler = create_event(event_name, dom, handler, options);
    if (dom === document.body || // @ts-ignore
    dom === window || // @ts-ignore
    dom === document || // Firefox has quirky behavior, it can happen that we still get "canplay" events when the element is already removed
    dom instanceof HTMLMediaElement) {
      teardown(() => {
        dom.removeEventListener(event_name, target_handler, options);
      });
    }
  }
  function delegated(event_name, element2, handler) {
    (element2[event_symbol] ??= {})[event_name] = handler;
  }
  function delegate(events) {
    for (var i = 0; i < events.length; i++) {
      all_registered_events.add(events[i]);
    }
    for (var fn of root_event_handles) {
      fn(events);
    }
  }
  var last_propagated_event = null;
  var last_propagated_event_clear_scheduled = false;
  function handle_event_propagation(event2) {
    var handler_element = this;
    var owner_document = (
      /** @type {Node} */
      handler_element.ownerDocument
    );
    var event_name = event2.type;
    var path = event2.composedPath?.() || [];
    var current_target = (
      /** @type {null | Element} */
      path[0] || event2.target
    );
    last_propagated_event = event2;
    if (!last_propagated_event_clear_scheduled) {
      last_propagated_event_clear_scheduled = true;
      setTimeout(() => {
        last_propagated_event_clear_scheduled = false;
        last_propagated_event = null;
      });
    }
    var path_idx = 0;
    var handled_at = last_propagated_event === event2 && event2[event_symbol];
    if (handled_at) {
      var at_idx = path.indexOf(handled_at);
      if (at_idx !== -1 && (handler_element === document || handler_element === /** @type {any} */
      window)) {
        event2[event_symbol] = handler_element;
        return;
      }
      var handler_idx = path.indexOf(handler_element);
      if (handler_idx === -1) {
        return;
      }
      if (at_idx <= handler_idx) {
        path_idx = at_idx;
      }
    }
    current_target = /** @type {Element} */
    path[path_idx] || event2.target;
    if (current_target === handler_element) return;
    define_property(event2, "currentTarget", {
      configurable: true,
      get() {
        return current_target || owner_document;
      }
    });
    var previous_reaction = active_reaction;
    var previous_effect = active_effect;
    set_active_reaction(null);
    set_active_effect(null);
    try {
      var throw_error;
      var other_errors = [];
      while (current_target !== null) {
        if (current_target === handler_element) break;
        try {
          var delegated2 = current_target[event_symbol]?.[event_name];
          if (delegated2 != null && (!/** @type {any} */
          current_target.disabled || // DOM could've been updated already by the time this is reached, so we check this as well
          // -> the target could not have been disabled because it emits the event in the first place
          event2.target === current_target)) {
            delegated2.call(current_target, event2);
          }
        } catch (error) {
          if (throw_error) {
            other_errors.push(error);
          } else {
            throw_error = error;
          }
        }
        if (event2.cancelBubble) break;
        path_idx++;
        current_target = path_idx < path.length ? (
          /** @type {Element} */
          path[path_idx]
        ) : null;
      }
      if (throw_error) {
        for (let error of other_errors) {
          queueMicrotask(() => {
            throw error;
          });
        }
        throw throw_error;
      }
    } finally {
      event2[event_symbol] = handler_element;
      delete event2.currentTarget;
      set_active_reaction(previous_reaction);
      set_active_effect(previous_effect);
    }
  }

  // node_modules/svelte/src/internal/client/dom/reconciler.js
  var policy = (
    // We gotta write it like this because after downleveling the pure comment may end up in the wrong location
    globalThis?.window?.trustedTypes && /* @__PURE__ */ globalThis.window.trustedTypes.createPolicy("svelte-trusted-html", {
      /** @param {string} html */
      createHTML: (html2) => {
        return html2;
      }
    })
  );
  function create_trusted_html(html2) {
    return (
      /** @type {string} */
      policy?.createHTML(html2) ?? html2
    );
  }
  function create_fragment_from_html(html2) {
    var elem = create_element("template");
    elem.innerHTML = create_trusted_html(html2.replaceAll("<!>", "<!---->"));
    return elem.content;
  }

  // node_modules/svelte/src/internal/client/dom/template.js
  function assign_nodes(start, end) {
    var effect2 = (
      /** @type {Effect} */
      active_effect
    );
    if (effect2.nodes === null) {
      effect2.nodes = { start, end, a: null, t: null };
    }
  }
  // @__NO_SIDE_EFFECTS__
  function from_html(content, flags2) {
    var is_fragment = (flags2 & TEMPLATE_FRAGMENT) !== 0;
    var use_import_node = (flags2 & TEMPLATE_USE_IMPORT_NODE) !== 0;
    var node;
    var has_start = !content.startsWith("<!>");
    return () => {
      if (hydrating) {
        assign_nodes(hydrate_node, null);
        return hydrate_node;
      }
      if (node === void 0) {
        node = create_fragment_from_html(has_start ? content : "<!>" + content);
        if (!is_fragment) node = /** @type {TemplateNode} */
        get_first_child(node);
      }
      var clone = (
        /** @type {TemplateNode} */
        use_import_node || is_firefox ? document.importNode(node, true) : node.cloneNode(true)
      );
      if (is_fragment) {
        var start = (
          /** @type {TemplateNode} */
          get_first_child(clone)
        );
        var end = (
          /** @type {TemplateNode} */
          clone.lastChild
        );
        assign_nodes(start, end);
      } else {
        assign_nodes(clone, clone);
      }
      return clone;
    };
  }
  function text(value = "") {
    if (!hydrating) {
      var t = create_text(value + "");
      assign_nodes(t, t);
      return t;
    }
    var node = hydrate_node;
    if (node.nodeType !== TEXT_NODE) {
      node.before(node = create_text());
      set_hydrate_node(node);
    } else {
      merge_text_nodes(
        /** @type {Text} */
        node
      );
    }
    assign_nodes(node, node);
    return node;
  }
  function comment() {
    if (hydrating) {
      assign_nodes(hydrate_node, null);
      return hydrate_node;
    }
    var frag = document.createDocumentFragment();
    var start = document.createComment("");
    var anchor = create_text();
    frag.append(start, anchor);
    assign_nodes(start, anchor);
    return frag;
  }
  function append(anchor, dom) {
    if (hydrating) {
      var effect2 = (
        /** @type {Effect & { nodes: EffectNodes }} */
        active_effect
      );
      if ((effect2.f & REACTION_RAN) === 0 || effect2.nodes.end === null) {
        effect2.nodes.end = hydrate_node;
      }
      hydrate_next();
      return;
    }
    if (anchor === null) {
      return;
    }
    anchor.before(
      /** @type {Node} */
      dom
    );
  }

  // node_modules/svelte/src/reactivity/create-subscriber.js
  function createSubscriber(start) {
    let subscribers = 0;
    let version = source(0);
    let stop;
    if (dev_fallback_default) {
      tag(version, "createSubscriber version");
    }
    return () => {
      if (effect_tracking()) {
        get2(version);
        render_effect(() => {
          if (subscribers === 0) {
            stop = untrack(() => start(() => increment(version)));
          }
          subscribers += 1;
          return () => {
            queue_micro_task(() => {
              subscribers -= 1;
              if (subscribers === 0) {
                stop?.();
                stop = void 0;
                increment(version);
              }
            });
          };
        });
      }
    };
  }

  // node_modules/svelte/src/internal/client/dom/blocks/boundary.js
  var flags = EFFECT_TRANSPARENT | EFFECT_PRESERVED;
  function boundary(node, props, children, transform_error) {
    new Boundary(node, props, children, transform_error);
  }
  var Boundary = class {
    /** @type {Boundary | null} */
    parent;
    is_pending = false;
    /**
     * API-level transformError transform function. Transforms errors before they reach the `failed` snippet.
     * Inherited from parent boundary, or defaults to identity.
     * @type {(error: unknown) => unknown}
     */
    transform_error;
    /** @type {TemplateNode} */
    #anchor;
    /** @type {TemplateNode | null} */
    #hydrate_open = hydrating ? hydrate_node : null;
    /** @type {BoundaryProps} */
    #props;
    /** @type {((anchor: Node) => void)} */
    #children;
    /** @type {Effect} */
    #effect;
    /** @type {Effect | null} */
    #main_effect = null;
    /** @type {Effect | null} */
    #pending_effect = null;
    /** @type {Effect | null} */
    #failed_effect = null;
    /** @type {DocumentFragment | null} */
    #offscreen_fragment = null;
    #local_pending_count = 0;
    #pending_count = 0;
    #pending_count_update_queued = false;
    /** @type {Set<Effect>} */
    #dirty_effects = /* @__PURE__ */ new Set();
    /** @type {Set<Effect>} */
    #maybe_dirty_effects = /* @__PURE__ */ new Set();
    /**
     * A source containing the number of pending async deriveds/expressions.
     * Only created if `$effect.pending()` is used inside the boundary,
     * otherwise updating the source results in needless `Batch.ensure()`
     * calls followed by no-op flushes
     * @type {Source<number> | null}
     */
    #effect_pending = null;
    #effect_pending_subscriber = createSubscriber(() => {
      this.#effect_pending = source(this.#local_pending_count);
      if (dev_fallback_default) {
        tag(this.#effect_pending, "$effect.pending()");
      }
      return () => {
        this.#effect_pending = null;
      };
    });
    /**
     * @param {TemplateNode} node
     * @param {BoundaryProps} props
     * @param {((anchor: Node) => void)} children
     * @param {((error: unknown) => unknown) | undefined} [transform_error]
     */
    constructor(node, props, children, transform_error) {
      this.#anchor = node;
      this.#props = props;
      this.#children = (anchor) => {
        var effect2 = (
          /** @type {Effect} */
          active_effect
        );
        effect2.b = this;
        effect2.f |= BOUNDARY_EFFECT;
        children(anchor);
      };
      this.parent = /** @type {Effect} */
      active_effect.b;
      this.transform_error = transform_error ?? this.parent?.transform_error ?? ((e) => e);
      this.#effect = block(() => {
        if (hydrating) {
          const comment2 = (
            /** @type {Comment} */
            this.#hydrate_open
          );
          hydrate_next();
          const server_rendered_pending = comment2.data === HYDRATION_START_ELSE;
          const server_rendered_failed = comment2.data.startsWith(HYDRATION_START_FAILED);
          if (server_rendered_failed) {
            const serialized_error = JSON.parse(comment2.data.slice(HYDRATION_START_FAILED.length));
            this.#hydrate_failed_content(serialized_error);
          } else if (server_rendered_pending) {
            this.#hydrate_pending_content();
          } else {
            this.#hydrate_resolved_content();
          }
        } else {
          this.#render();
        }
      }, flags);
      if (hydrating) {
        this.#anchor = hydrate_node;
      }
    }
    #hydrate_resolved_content() {
      try {
        this.#main_effect = branch(() => this.#children(this.#anchor));
      } catch (error) {
        this.error(error);
      }
    }
    /**
     * @param {unknown} error The deserialized error from the server's hydration comment
     */
    #hydrate_failed_content(error) {
      const failed = this.#props.failed;
      const { reset: reset2, invoke_onerror } = this.#create_reset(error);
      queue_micro_task(invoke_onerror);
      if (!failed) return;
      this.#failed_effect = branch(() => {
        failed(
          this.#anchor,
          () => error,
          () => reset2
        );
      });
    }
    /**
     * Creates the `reset` function for a failed boundary, along with a function
     * that invokes `onerror` with it (if provided)
     * @param {unknown} error
     * @returns {{ reset: () => void, invoke_onerror: () => void }}
     */
    #create_reset(error) {
      var did_reset = false;
      var calling_on_error = false;
      const reset2 = () => {
        if (did_reset) {
          svelte_boundary_reset_noop();
          return;
        }
        did_reset = true;
        if (calling_on_error) {
          svelte_boundary_reset_onerror();
        }
        if (this.#failed_effect !== null) {
          pause_effect(this.#failed_effect, () => {
            this.#failed_effect = null;
          });
        }
        this.#run(() => {
          this.#render();
        });
      };
      const invoke_onerror = () => {
        try {
          calling_on_error = true;
          this.#props.onerror?.(error, reset2);
          calling_on_error = false;
        } catch (err) {
          invoke_error_boundary(err, this.#effect && this.#effect.parent);
        }
      };
      return { reset: reset2, invoke_onerror };
    }
    #hydrate_pending_content() {
      const pending2 = this.#props.pending;
      if (!pending2) return;
      this.is_pending = true;
      this.#pending_effect = branch(() => pending2(this.#anchor));
      queue_micro_task(() => {
        var fragment = this.#offscreen_fragment = document.createDocumentFragment();
        var anchor = create_text();
        var handled = false;
        fragment.append(anchor);
        this.#main_effect = this.#run(() => {
          try {
            return branch(() => this.#children(anchor));
          } catch (error) {
            try {
              this.error(error);
              handled = true;
            } catch (error2) {
              invoke_error_boundary(error2, this.#effect.parent);
            }
            return null;
          }
        });
        if (this.#main_effect === null) {
          this.#offscreen_fragment = null;
          if (handled) this.#resolve(
            /** @type {Batch} */
            current_batch
          );
          return;
        }
        if (this.#pending_count === 0) {
          this.#anchor.before(fragment);
          this.#offscreen_fragment = null;
          pause_effect(
            /** @type {Effect} */
            this.#pending_effect,
            () => {
              this.#pending_effect = null;
            }
          );
          this.#resolve(
            /** @type {Batch} */
            current_batch
          );
        }
      });
    }
    #render() {
      try {
        this.is_pending = this.has_pending_snippet();
        this.#pending_count = 0;
        this.#local_pending_count = 0;
        this.#main_effect = branch(() => {
          this.#children(this.#anchor);
        });
        if (this.#pending_count > 0) {
          var fragment = this.#offscreen_fragment = document.createDocumentFragment();
          move_effect(this.#main_effect, fragment);
          const pending2 = (
            /** @type {(anchor: Node) => void} */
            this.#props.pending
          );
          this.#pending_effect = branch(() => pending2(this.#anchor));
        } else {
          this.#resolve(
            /** @type {Batch} */
            current_batch
          );
        }
      } catch (error) {
        this.error(error);
      }
    }
    /**
     * @param {Batch} batch
     */
    #resolve(batch) {
      this.is_pending = false;
      batch.transfer_effects(this.#dirty_effects, this.#maybe_dirty_effects);
    }
    /**
     * Defer an effect inside a pending boundary until the boundary resolves
     * @param {Effect} effect
     */
    defer_effect(effect2) {
      defer_effect(effect2, this.#dirty_effects, this.#maybe_dirty_effects);
    }
    /**
     * Returns `false` if the effect exists inside a boundary whose pending snippet is shown
     * @returns {boolean}
     */
    is_rendered() {
      return !this.is_pending && (!this.parent || this.parent.is_rendered());
    }
    has_pending_snippet() {
      return !!this.#props.pending;
    }
    /**
     * @template T
     * @param {() => T} fn
     */
    #run(fn) {
      var previous_effect = active_effect;
      var previous_reaction = active_reaction;
      var previous_ctx = component_context;
      set_active_effect(this.#effect);
      set_active_reaction(this.#effect);
      set_component_context(this.#effect.ctx);
      try {
        Batch.ensure();
        return fn();
      } finally {
        set_active_effect(previous_effect);
        set_active_reaction(previous_reaction);
        set_component_context(previous_ctx);
      }
    }
    /**
     * Updates the pending count associated with the currently visible pending snippet,
     * if any, such that we can replace the snippet with content once work is done
     * @param {1 | -1} d
     * @param {Batch} batch
     */
    #update_pending_count(d, batch) {
      if (!this.has_pending_snippet()) {
        if (this.parent) {
          this.parent.#update_pending_count(d, batch);
        }
        return;
      }
      this.#pending_count += d;
      if (this.#pending_count === 0) {
        this.#resolve(batch);
        if (this.#pending_effect) {
          pause_effect(this.#pending_effect, () => {
            this.#pending_effect = null;
          });
        }
        if (this.#offscreen_fragment) {
          this.#anchor.before(this.#offscreen_fragment);
          this.#offscreen_fragment = null;
        }
      }
    }
    /**
     * Update the source that powers `$effect.pending()` inside this boundary,
     * and controls when the current `pending` snippet (if any) is removed.
     * Do not call from inside the class
     * @param {1 | -1} d
     * @param {Batch} batch
     */
    update_pending_count(d, batch) {
      this.#update_pending_count(d, batch);
      this.#local_pending_count += d;
      if (!this.#effect_pending || this.#pending_count_update_queued) return;
      this.#pending_count_update_queued = true;
      queue_micro_task(() => {
        this.#pending_count_update_queued = false;
        if (this.#effect_pending) {
          internal_set(this.#effect_pending, this.#local_pending_count);
        }
      });
    }
    get_effect_pending() {
      this.#effect_pending_subscriber();
      return get2(
        /** @type {Source<number>} */
        this.#effect_pending
      );
    }
    /** @param {unknown} error */
    error(error) {
      if (!this.#props.onerror && !this.#props.failed) {
        throw error;
      }
      if (current_batch?.is_fork) {
        if (this.#main_effect) current_batch.skip_effect(this.#main_effect);
        if (this.#pending_effect) current_batch.skip_effect(this.#pending_effect);
        if (this.#failed_effect) current_batch.skip_effect(this.#failed_effect);
        current_batch.oncommit(() => {
          this.#handle_error(error);
        });
      } else {
        this.#handle_error(error);
      }
    }
    /**
     * @param {unknown} error
     */
    #handle_error(error) {
      if (this.#main_effect) {
        destroy_effect(this.#main_effect);
        this.#main_effect = null;
      }
      if (this.#pending_effect) {
        destroy_effect(this.#pending_effect);
        this.#pending_effect = null;
      }
      if (this.#failed_effect) {
        destroy_effect(this.#failed_effect);
        this.#failed_effect = null;
      }
      if (hydrating) {
        set_hydrate_node(
          /** @type {TemplateNode} */
          this.#hydrate_open
        );
        next();
        set_hydrate_node(skip_nodes());
      }
      let failed = this.#props.failed;
      const handle_error_result = (transformed_error) => {
        const { reset: reset2, invoke_onerror } = this.#create_reset(transformed_error);
        invoke_onerror();
        if (failed) {
          this.#failed_effect = this.#run(() => {
            try {
              return branch(() => {
                var effect2 = (
                  /** @type {Effect} */
                  active_effect
                );
                effect2.b = this;
                effect2.f |= BOUNDARY_EFFECT;
                failed(
                  this.#anchor,
                  () => transformed_error,
                  () => reset2
                );
              });
            } catch (error2) {
              invoke_error_boundary(
                error2,
                /** @type {Effect} */
                this.#effect.parent
              );
              return null;
            }
          });
        }
      };
      queue_micro_task(() => {
        var result;
        try {
          result = this.transform_error(error);
        } catch (e) {
          invoke_error_boundary(e, this.#effect && this.#effect.parent);
          return;
        }
        if (result !== null && typeof result === "object" && typeof /** @type {any} */
        result.then === "function") {
          result.then(
            handle_error_result,
            /** @param {unknown} e */
            (e) => invoke_error_boundary(e, this.#effect && this.#effect.parent)
          );
        } else {
          handle_error_result(result);
        }
      });
    }
  };

  // node_modules/svelte/src/internal/client/render.js
  var should_intro = true;
  function set_text(text2, value) {
    var str = value == null ? "" : typeof value === "object" ? `${value}` : value;
    if (str !== /** @type {any} */
    (text2[TEXT_CACHE] ??= text2.nodeValue)) {
      text2[TEXT_CACHE] = str;
      text2.nodeValue = `${str}`;
    }
  }
  function mount(component2, options) {
    return _mount(component2, options);
  }
  function hydrate(component2, options) {
    init_operations();
    options.intro = options.intro ?? false;
    const target2 = options.target;
    const was_hydrating = hydrating;
    const previous_hydrate_node = hydrate_node;
    try {
      var anchor = get_first_child(target2);
      while (anchor && (anchor.nodeType !== COMMENT_NODE || /** @type {Comment} */
      anchor.data !== HYDRATION_START)) {
        anchor = get_next_sibling(anchor);
      }
      if (!anchor) {
        throw HYDRATION_ERROR;
      }
      set_hydrating(true);
      set_hydrate_node(
        /** @type {Comment} */
        anchor
      );
      const instance = _mount(component2, { ...options, anchor });
      set_hydrating(false);
      return (
        /**  @type {Exports} */
        instance
      );
    } catch (error) {
      if (error instanceof Error && error.message.split("\n").some((line) => line.startsWith("https://svelte.dev/e/"))) {
        throw error;
      }
      if (error !== HYDRATION_ERROR) {
        console.warn("Failed to hydrate: ", error);
      }
      if (options.recover === false) {
        hydration_failed();
      }
      init_operations();
      clear_text_content(target2);
      set_hydrating(false);
      return mount(component2, options);
    } finally {
      set_hydrating(was_hydrating);
      set_hydrate_node(previous_hydrate_node);
    }
  }
  var listeners = /* @__PURE__ */ new Map();
  function _mount(Component, { target: target2, anchor, props = {}, events, context, intro = true, transformError }) {
    init_operations();
    var component2 = void 0;
    var unmount2 = component_root(() => {
      var anchor_node = anchor ?? target2.appendChild(create_text());
      boundary(
        /** @type {TemplateNode} */
        anchor_node,
        {
          pending: () => {
          }
        },
        (anchor_node2) => {
          push({});
          var ctx = (
            /** @type {ComponentContext} */
            component_context
          );
          if (context) ctx.c = context;
          if (events) {
            props.$$events = events;
          }
          if (hydrating) {
            assign_nodes(
              /** @type {TemplateNode} */
              anchor_node2,
              null
            );
          }
          should_intro = intro;
          component2 = Component(anchor_node2, props) || mark_as_component();
          should_intro = true;
          if (hydrating) {
            active_effect.nodes.end = hydrate_node;
            if (hydrate_node === null || hydrate_node.nodeType !== COMMENT_NODE || /** @type {Comment} */
            hydrate_node.data !== HYDRATION_END) {
              hydration_mismatch();
              throw HYDRATION_ERROR;
            }
          }
          pop();
        },
        transformError
      );
      var registered_events = /* @__PURE__ */ new Set();
      var event_handle = (events2) => {
        for (var i = 0; i < events2.length; i++) {
          var event_name = events2[i];
          if (registered_events.has(event_name)) continue;
          registered_events.add(event_name);
          var passive2 = is_passive_event(event_name);
          for (const node of [target2, document]) {
            var counts = listeners.get(node);
            if (counts === void 0) {
              counts = /* @__PURE__ */ new Map();
              listeners.set(node, counts);
            }
            var count = counts.get(event_name);
            if (count === void 0) {
              node.addEventListener(event_name, handle_event_propagation, { passive: passive2 });
              counts.set(event_name, 1);
            } else {
              counts.set(event_name, count + 1);
            }
          }
        }
      };
      event_handle(array_from(all_registered_events));
      root_event_handles.add(event_handle);
      return () => {
        for (var event_name of registered_events) {
          for (const node of [target2, document]) {
            var counts = (
              /** @type {Map<string, number>} */
              listeners.get(node)
            );
            var count = (
              /** @type {number} */
              counts.get(event_name)
            );
            if (--count == 0) {
              node.removeEventListener(event_name, handle_event_propagation);
              counts.delete(event_name);
              if (counts.size === 0) {
                listeners.delete(node);
              }
            } else {
              counts.set(event_name, count);
            }
          }
        }
        root_event_handles.delete(event_handle);
        if (anchor_node !== anchor) {
          anchor_node.parentNode?.removeChild(anchor_node);
        }
      };
    });
    mounted_components.set(component2, unmount2);
    return component2;
  }
  var mounted_components = /* @__PURE__ */ new WeakMap();
  function unmount(component2, options) {
    const fn = mounted_components.get(component2);
    if (fn) {
      mounted_components.delete(component2);
      return fn(options);
    }
    if (dev_fallback_default) {
      lifecycle_double_unmount();
    }
    return Promise.resolve();
  }

  // node_modules/svelte/src/internal/client/dom/blocks/branches.js
  var BranchManager = class {
    /** @type {TemplateNode} */
    anchor;
    /** @type {Map<Batch, Key>} */
    #batches = /* @__PURE__ */ new Map();
    /**
     * Map of keys to effects that are currently rendered in the DOM.
     * These effects are visible and actively part of the document tree.
     * Example:
     * ```
     * {#if condition}
     * 	foo
     * {:else}
     * 	bar
     * {/if}
     * ```
     * Can result in the entries `true->Effect` and `false->Effect`
     * @type {Map<Key, Effect>}
     */
    #onscreen = /* @__PURE__ */ new Map();
    /**
     * Similar to #onscreen with respect to the keys, but contains branches that are not yet
     * in the DOM, because their insertion is deferred.
     * @type {Map<Key, Branch>}
     */
    #offscreen = /* @__PURE__ */ new Map();
    /**
     * Keys of effects that are currently outroing
     * @type {Set<Key>}
     */
    #outroing = /* @__PURE__ */ new Set();
    /**
     * Whether to pause (i.e. outro) on change, or destroy immediately.
     * This is necessary for `<svelte:element>`
     */
    #transition = true;
    /**
     * @param {TemplateNode} anchor
     * @param {boolean} transition
     */
    constructor(anchor, transition2 = true) {
      this.anchor = anchor;
      this.#transition = transition2;
    }
    /**
     * @param {Batch} batch
     */
    #commit = (batch) => {
      if (!this.#batches.has(batch)) return;
      var key2 = (
        /** @type {Key} */
        this.#batches.get(batch)
      );
      var onscreen = this.#onscreen.get(key2);
      if (onscreen) {
        resume_effect(onscreen);
        this.#outroing.delete(key2);
      } else {
        var offscreen = this.#offscreen.get(key2);
        if (offscreen) {
          resume_effect(offscreen.effect);
          this.#onscreen.set(key2, offscreen.effect);
          this.#offscreen.delete(key2);
          if (dev_fallback_default) {
            offscreen.fragment.lastChild[HMR_ANCHOR] = this.anchor;
          }
          offscreen.fragment.lastChild.remove();
          this.anchor.before(offscreen.fragment);
          onscreen = offscreen.effect;
        }
      }
      for (const [b, k] of this.#batches) {
        this.#batches.delete(b);
        if (b === batch) {
          break;
        }
        const offscreen2 = this.#offscreen.get(k);
        if (offscreen2) {
          destroy_effect(offscreen2.effect);
          this.#offscreen.delete(k);
        }
      }
      for (const [k, effect2] of this.#onscreen) {
        if (k === key2 || this.#outroing.has(k)) continue;
        const on_destroy = () => {
          const keys = Array.from(this.#batches.values());
          if (keys.includes(k)) {
            var fragment = document.createDocumentFragment();
            move_effect(effect2, fragment);
            fragment.append(create_text());
            this.#offscreen.set(k, { effect: effect2, fragment });
          } else {
            destroy_effect(effect2);
          }
          this.#outroing.delete(k);
          this.#onscreen.delete(k);
        };
        if (this.#transition || !onscreen) {
          this.#outroing.add(k);
          pause_effect(effect2, on_destroy, false);
        } else {
          on_destroy();
        }
      }
    };
    /**
     * @param {Batch} batch
     */
    #discard = (batch) => {
      this.#batches.delete(batch);
      const keys = Array.from(this.#batches.values());
      for (const [k, branch2] of this.#offscreen) {
        if (!keys.includes(k)) {
          destroy_effect(branch2.effect);
          this.#offscreen.delete(k);
        }
      }
    };
    /**
     *
     * @param {any} key
     * @param {null | ((target: TemplateNode) => void)} fn
     */
    ensure(key2, fn) {
      var batch = (
        /** @type {Batch} */
        current_batch
      );
      var defer = should_defer_append();
      if (fn && !this.#onscreen.has(key2) && !this.#offscreen.has(key2)) {
        if (defer) {
          var fragment = document.createDocumentFragment();
          var target2 = create_text();
          fragment.append(target2);
          this.#offscreen.set(key2, {
            effect: branch(() => fn(target2)),
            fragment
          });
        } else {
          this.#onscreen.set(
            key2,
            branch(() => fn(this.anchor))
          );
        }
      }
      this.#batches.set(batch, key2);
      if (defer) {
        for (const [k, effect2] of this.#onscreen) {
          if (k === key2) {
            batch.unskip_effect(effect2);
          } else {
            batch.skip_effect(effect2);
          }
        }
        for (const [k, branch2] of this.#offscreen) {
          if (k === key2) {
            batch.unskip_effect(branch2.effect);
          } else {
            batch.skip_effect(branch2.effect);
          }
        }
        batch.oncommit(this.#commit);
        batch.ondiscard(this.#discard);
      } else {
        if (hydrating) {
          this.anchor = hydrate_node;
        }
        this.#commit(batch);
      }
    }
  };

  // node_modules/svelte/src/internal/client/dom/blocks/if.js
  function if_block(node, fn, elseif = false) {
    var marker;
    if (hydrating) {
      marker = hydrate_node;
      hydrate_next();
    }
    var branches = new BranchManager(node);
    var flags2 = elseif ? EFFECT_TRANSPARENT : 0;
    function update_branch(key2, fn2) {
      if (hydrating) {
        var data = read_hydration_instruction(
          /** @type {TemplateNode} */
          marker
        );
        if (key2 !== parseInt(data.substring(1))) {
          var anchor = skip_nodes();
          set_hydrate_node(anchor);
          branches.anchor = anchor;
          set_hydrating(false);
          branches.ensure(key2, fn2);
          set_hydrating(true);
          return;
        }
      }
      branches.ensure(key2, fn2);
    }
    block(() => {
      var has_branch = false;
      fn((fn2, key2 = 0) => {
        has_branch = true;
        update_branch(key2, fn2);
      });
      if (!has_branch) {
        update_branch(-1, null);
      }
    }, flags2);
  }

  // node_modules/svelte/src/internal/client/dom/blocks/each.js
  function index(_, i) {
    return i;
  }
  function pause_effects(state2, to_destroy, controlled_anchor) {
    var transitions = [];
    var length = to_destroy.length;
    var group;
    var remaining = to_destroy.length;
    for (var i = 0; i < length; i++) {
      let effect2 = to_destroy[i];
      pause_effect(
        effect2,
        () => {
          if (group) {
            group.pending.delete(effect2);
            group.done.add(effect2);
            if (group.pending.size === 0) {
              var groups = (
                /** @type {Set<EachOutroGroup>} */
                state2.outrogroups
              );
              destroy_effects(state2, array_from(group.done));
              groups.delete(group);
              if (groups.size === 0) {
                state2.outrogroups = null;
              }
            }
          } else {
            remaining -= 1;
          }
        },
        false
      );
    }
    if (remaining === 0) {
      var fast_path = transitions.length === 0 && controlled_anchor !== null && state2.pending.size === 0;
      if (fast_path) {
        var anchor = (
          /** @type {Element} */
          controlled_anchor
        );
        var parent_node = (
          /** @type {Element} */
          anchor.parentNode
        );
        clear_text_content(parent_node);
        parent_node.append(anchor);
        state2.items.clear();
      }
      destroy_effects(state2, to_destroy, !fast_path);
    } else {
      group = {
        pending: new Set(to_destroy),
        done: /* @__PURE__ */ new Set()
      };
      (state2.outrogroups ??= /* @__PURE__ */ new Set()).add(group);
    }
  }
  function destroy_effects(state2, to_destroy, remove_dom = true) {
    var preserved_effects;
    if (state2.pending.size > 0) {
      preserved_effects = /* @__PURE__ */ new Set();
      for (const keys of state2.pending.values()) {
        for (const key2 of keys) {
          preserved_effects.add(
            /** @type {EachItem} */
            state2.items.get(key2).e
          );
        }
      }
    }
    for (var i = 0; i < to_destroy.length; i++) {
      var e = to_destroy[i];
      if (preserved_effects?.has(e)) {
        e.f |= EFFECT_OFFSCREEN;
        const fragment = document.createDocumentFragment();
        move_effect(e, fragment);
      } else {
        destroy_effect(to_destroy[i], remove_dom);
      }
    }
  }
  var offscreen_anchor;
  function each(node, flags2, get_collection, get_key, render_fn, fallback_fn = null) {
    var anchor = node;
    var items = /* @__PURE__ */ new Map();
    var is_controlled = (flags2 & EACH_IS_CONTROLLED) !== 0;
    if (is_controlled) {
      var parent_node = (
        /** @type {Element} */
        node
      );
      anchor = hydrating ? set_hydrate_node(get_first_child(parent_node)) : parent_node.appendChild(create_text());
    }
    if (hydrating) {
      hydrate_next();
    }
    var fallback2 = null;
    var each_array = derived_safe_equal(() => {
      var collection = get_collection();
      return (
        /** @type {V[]} */
        is_array(collection) ? collection : collection == null ? [] : array_from(collection)
      );
    });
    if (dev_fallback_default) {
      tag(each_array, "{#each ...}");
    }
    var array;
    var pending2 = /* @__PURE__ */ new Map();
    var first_run = true;
    function commit(batch) {
      if ((state2.effect.f & DESTROYED) !== 0) {
        return;
      }
      state2.pending.delete(batch);
      state2.fallback = fallback2;
      reconcile(state2, array, anchor, flags2, get_key);
      if (fallback2 !== null) {
        if (array.length === 0) {
          if ((fallback2.f & EFFECT_OFFSCREEN) === 0) {
            resume_effect(fallback2);
          } else {
            fallback2.f ^= EFFECT_OFFSCREEN;
            move(fallback2, null, anchor);
          }
        } else {
          pause_effect(fallback2, () => {
            fallback2 = null;
          });
        }
      }
    }
    function discard(batch) {
      state2.pending.delete(batch);
    }
    var effect2 = block(() => {
      array = /** @type {V[]} */
      get2(each_array);
      var length = array.length;
      let mismatch = false;
      if (hydrating) {
        var is_else = read_hydration_instruction(anchor) === HYDRATION_START_ELSE;
        if (is_else !== (length === 0)) {
          anchor = skip_nodes();
          set_hydrate_node(anchor);
          set_hydrating(false);
          mismatch = true;
        }
      }
      var keys = /* @__PURE__ */ new Set();
      var batch = (
        /** @type {Batch} */
        current_batch
      );
      var defer = should_defer_append();
      for (var index2 = 0; index2 < length; index2 += 1) {
        if (hydrating && hydrate_node.nodeType === COMMENT_NODE && /** @type {Comment} */
        hydrate_node.data === HYDRATION_END) {
          anchor = /** @type {Comment} */
          hydrate_node;
          mismatch = true;
          set_hydrating(false);
        }
        var value = array[index2];
        var key2 = get_key(value, index2);
        if (dev_fallback_default) {
          var key_again = get_key(value, index2);
          if (key2 !== key_again) {
            each_key_volatile(String(index2), String(key2), String(key_again));
          }
        }
        var item = first_run ? null : items.get(key2);
        if (item) {
          if (item.v) internal_set(item.v, value);
          if (item.i) internal_set(item.i, index2);
          if (defer) {
            batch.unskip_effect(item.e);
          }
        } else {
          item = create_item(
            items,
            first_run ? anchor : offscreen_anchor ??= create_text(),
            value,
            key2,
            index2,
            render_fn,
            flags2,
            get_collection
          );
          if (!first_run) {
            item.e.f |= EFFECT_OFFSCREEN;
          }
          items.set(key2, item);
        }
        keys.add(key2);
      }
      if (length === 0 && fallback_fn && !fallback2) {
        if (first_run) {
          fallback2 = branch(() => fallback_fn(anchor));
        } else {
          fallback2 = branch(() => fallback_fn(offscreen_anchor ??= create_text()));
          fallback2.f |= EFFECT_OFFSCREEN;
        }
      }
      if (length > keys.size) {
        if (dev_fallback_default) {
          validate_each_keys(array, get_key);
        } else {
          each_key_duplicate("", "", "");
        }
      }
      if (hydrating && length > 0) {
        set_hydrate_node(skip_nodes());
      }
      if (!first_run) {
        pending2.set(batch, keys);
        if (defer) {
          for (const [key3, item2] of items) {
            if (!keys.has(key3)) {
              batch.skip_effect(item2.e);
            }
          }
          batch.oncommit(commit);
          batch.ondiscard(discard);
        } else {
          commit(batch);
        }
      }
      if (mismatch) {
        set_hydrating(true);
      }
      get2(each_array);
    });
    var state2 = { effect: effect2, flags: flags2, items, pending: pending2, outrogroups: null, fallback: fallback2 };
    first_run = false;
    if (hydrating) {
      anchor = hydrate_node;
    }
  }
  function skip_to_branch(effect2) {
    while (effect2 !== null && (effect2.f & BRANCH_EFFECT) === 0) {
      effect2 = effect2.next;
    }
    return effect2;
  }
  function reconcile(state2, array, anchor, flags2, get_key) {
    var is_animated = (flags2 & EACH_IS_ANIMATED) !== 0;
    var length = array.length;
    var items = state2.items;
    var current = skip_to_branch(state2.effect.first);
    var seen;
    var prev = null;
    var to_animate;
    var matched = [];
    var stashed = [];
    var value;
    var key2;
    var effect2;
    var i;
    if (is_animated) {
      for (i = 0; i < length; i += 1) {
        value = array[i];
        key2 = get_key(value, i);
        effect2 = /** @type {EachItem} */
        items.get(key2).e;
        if ((effect2.f & EFFECT_OFFSCREEN) === 0) {
          effect2.nodes?.a?.measure();
          (to_animate ??= /* @__PURE__ */ new Set()).add(effect2);
        }
      }
    }
    for (i = 0; i < length; i += 1) {
      value = array[i];
      key2 = get_key(value, i);
      effect2 = /** @type {EachItem} */
      items.get(key2).e;
      if (state2.outrogroups !== null) {
        for (const group of state2.outrogroups) {
          group.pending.delete(effect2);
          group.done.delete(effect2);
        }
      }
      if ((effect2.f & INERT) !== 0) {
        resume_effect(effect2);
        if (is_animated) {
          effect2.nodes?.a?.unfix();
          (to_animate ??= /* @__PURE__ */ new Set()).delete(effect2);
        }
      }
      if ((effect2.f & EFFECT_OFFSCREEN) !== 0) {
        effect2.f ^= EFFECT_OFFSCREEN;
        if (effect2 === current) {
          move(effect2, null, anchor);
        } else {
          var next2 = prev ? prev.next : current;
          if (effect2 === state2.effect.last) {
            state2.effect.last = effect2.prev;
          }
          if (effect2.prev) effect2.prev.next = effect2.next;
          if (effect2.next) effect2.next.prev = effect2.prev;
          link(state2, prev, effect2);
          link(state2, effect2, next2);
          move(effect2, next2, anchor);
          prev = effect2;
          matched = [];
          stashed = [];
          current = skip_to_branch(prev.next);
          continue;
        }
      }
      if (effect2 !== current) {
        if (seen !== void 0 && seen.has(effect2)) {
          if (matched.length < stashed.length) {
            var start = stashed[0];
            var j;
            prev = start.prev;
            var a = matched[0];
            var b = matched[matched.length - 1];
            for (j = 0; j < matched.length; j += 1) {
              move(matched[j], start, anchor);
            }
            for (j = 0; j < stashed.length; j += 1) {
              seen.delete(stashed[j]);
            }
            link(state2, a.prev, b.next);
            link(state2, prev, a);
            link(state2, b, start);
            current = start;
            prev = b;
            i -= 1;
            matched = [];
            stashed = [];
          } else {
            seen.delete(effect2);
            move(effect2, current, anchor);
            link(state2, effect2.prev, effect2.next);
            link(state2, effect2, prev === null ? state2.effect.first : prev.next);
            link(state2, prev, effect2);
            prev = effect2;
          }
          continue;
        }
        matched = [];
        stashed = [];
        while (current !== null && current !== effect2) {
          (seen ??= /* @__PURE__ */ new Set()).add(current);
          stashed.push(current);
          current = skip_to_branch(current.next);
        }
        if (current === null) {
          continue;
        }
      }
      if ((effect2.f & EFFECT_OFFSCREEN) === 0) {
        matched.push(effect2);
      }
      prev = effect2;
      current = skip_to_branch(effect2.next);
    }
    if (state2.outrogroups !== null) {
      for (const group of state2.outrogroups) {
        if (group.pending.size === 0) {
          destroy_effects(state2, array_from(group.done));
          state2.outrogroups?.delete(group);
        }
      }
      if (state2.outrogroups.size === 0) {
        state2.outrogroups = null;
      }
    }
    if (current !== null || seen !== void 0) {
      var to_destroy = [];
      if (seen !== void 0) {
        for (effect2 of seen) {
          if ((effect2.f & INERT) === 0) {
            to_destroy.push(effect2);
          }
        }
      }
      while (current !== null) {
        if ((current.f & INERT) === 0 && current !== state2.fallback) {
          to_destroy.push(current);
        }
        current = skip_to_branch(current.next);
      }
      var destroy_length = to_destroy.length;
      if (destroy_length > 0) {
        var controlled_anchor = (flags2 & EACH_IS_CONTROLLED) !== 0 && length === 0 ? anchor : null;
        if (is_animated) {
          for (i = 0; i < destroy_length; i += 1) {
            to_destroy[i].nodes?.a?.measure();
          }
          for (i = 0; i < destroy_length; i += 1) {
            to_destroy[i].nodes?.a?.fix();
          }
        }
        pause_effects(state2, to_destroy, controlled_anchor);
      }
    }
    if (is_animated) {
      queue_micro_task(() => {
        if (to_animate === void 0) return;
        for (effect2 of to_animate) {
          effect2.nodes?.a?.apply();
        }
      });
    }
  }
  function create_item(items, anchor, value, key2, index2, render_fn, flags2, get_collection) {
    var v = (flags2 & EACH_ITEM_REACTIVE) !== 0 ? (flags2 & EACH_ITEM_IMMUTABLE) === 0 ? mutable_source(value, false, false) : source(value) : null;
    var i = (flags2 & EACH_INDEX_REACTIVE) !== 0 ? source(index2) : null;
    if (dev_fallback_default && v) {
      v.trace = () => {
        get_collection()[i?.v ?? index2];
      };
    }
    return {
      v,
      i,
      e: branch(() => {
        render_fn(anchor, v ?? value, i ?? index2, get_collection);
        return () => {
          items.delete(key2);
        };
      })
    };
  }
  function move(effect2, next2, anchor) {
    if (!effect2.nodes) return;
    var node = effect2.nodes.start;
    var end = effect2.nodes.end;
    var dest = next2 && (next2.f & EFFECT_OFFSCREEN) === 0 ? (
      /** @type {EffectNodes} */
      next2.nodes.start
    ) : anchor;
    while (node !== null) {
      var next_node = (
        /** @type {TemplateNode} */
        get_next_sibling(node)
      );
      dest.before(node);
      if (node === end) {
        return;
      }
      node = next_node;
    }
  }
  function link(state2, prev, next2) {
    if (prev === null) {
      state2.effect.first = next2;
    } else {
      prev.next = next2;
    }
    if (next2 === null) {
      state2.effect.last = prev;
    } else {
      next2.prev = prev;
    }
  }
  function validate_each_keys(array, key_fn) {
    const keys = /* @__PURE__ */ new Map();
    const length = array.length;
    for (let i = 0; i < length; i++) {
      const key2 = key_fn(array[i], i);
      if (keys.has(key2)) {
        const a = String(keys.get(key2));
        const b = String(i);
        let k = String(key2);
        if (k.startsWith("[object ")) k = null;
        each_key_duplicate(a, b, k);
      }
      keys.set(key2, i);
    }
  }

  // node_modules/svelte/src/internal/client/dom/css.js
  function append_styles(anchor, css) {
    effect(() => {
      anchor = active_effect?.parent?.nodes?.start ?? anchor;
      var root11 = anchor.getRootNode();
      var target2 = (
        /** @type {ShadowRoot} */
        root11.host ? (
          /** @type {ShadowRoot} */
          root11
        ) : (
          /** @type {Document} */
          root11.head ?? /** @type {Document} */
          root11.ownerDocument.head
        )
      );
      if (!target2.querySelector("#" + css.hash)) {
        const style = create_element("style");
        style.id = css.hash;
        style.textContent = css.code;
        target2.appendChild(style);
        if (dev_fallback_default) {
          register_style(css.hash, style);
        }
      }
    });
  }

  // node_modules/svelte/src/internal/shared/attributes.js
  var whitespace = [..." 	\n\r\f\xA0\v\uFEFF"];
  function to_class(value, hash2, directives) {
    var classname = value == null ? "" : "" + value;
    if (hash2) {
      classname = classname ? classname + " " + hash2 : hash2;
    }
    if (directives) {
      for (var key2 of Object.keys(directives)) {
        if (directives[key2]) {
          classname = classname ? classname + " " + key2 : key2;
        } else if (classname.length) {
          var len = key2.length;
          var a = 0;
          while ((a = classname.indexOf(key2, a)) >= 0) {
            var b = a + len;
            if ((a === 0 || whitespace.includes(classname[a - 1])) && (b === classname.length || whitespace.includes(classname[b]))) {
              classname = (a === 0 ? "" : classname.substring(0, a)) + classname.substring(b + 1);
            } else {
              a = b;
            }
          }
        }
      }
    }
    return classname === "" ? null : classname;
  }

  // node_modules/svelte/src/internal/client/dom/elements/class.js
  function set_class(dom, is_html, value, hash2, prev_classes, next_classes) {
    var prev = (
      /** @type {any} */
      dom[CLASS_CACHE]
    );
    if (hydrating || prev !== value || prev === void 0) {
      var next_class_name = to_class(value, hash2, next_classes);
      if (!hydrating || next_class_name !== dom.getAttribute("class")) {
        if (next_class_name == null) {
          dom.removeAttribute("class");
        } else if (is_html) {
          dom.className = next_class_name;
        } else {
          dom.setAttribute("class", next_class_name);
        }
      }
      dom[CLASS_CACHE] = value;
    } else if (next_classes && prev_classes !== next_classes) {
      for (var key2 in next_classes) {
        var is_present = !!next_classes[key2];
        if (prev_classes == null || is_present !== !!prev_classes[key2]) {
          dom.classList.toggle(key2, is_present);
        }
      }
    }
    return next_classes;
  }

  // node_modules/svelte/src/internal/client/dom/elements/bindings/select.js
  function set_selected(option, selected) {
    if (selected) {
      if (!option.hasAttribute("selected")) option.setAttribute("selected", "");
    } else {
      option.removeAttribute("selected");
    }
  }
  function apply_default_select_value(select, preserve) {
    var value = select.__defaultValue;
    var multiple = select.multiple;
    var values = multiple ? value ?? [] : null;
    if (multiple && !is_array(values)) return;
    var index2 = select.selectedIndex;
    var selected = preserve && multiple ? new Set(select.selectedOptions) : null;
    for (var option of select.options) {
      var option_value = get_option_value(option);
      set_selected(
        option,
        multiple ? (
          /** @type {any[]} */
          values.includes(option_value)
        ) : is(option_value, value)
      );
    }
    if (!preserve) return;
    if (selected !== null) {
      for (option of select.options) {
        var was_selected = selected.has(option);
        if (option.selected !== was_selected) option.selected = was_selected;
      }
    } else if (select.selectedIndex !== index2) {
      select.selectedIndex = index2;
    }
  }
  function select_option(select, value, mounting = false) {
    if (select.multiple) {
      if (value == void 0) {
        return;
      }
      if (!is_array(value)) {
        return select_multiple_invalid_value();
      }
      for (var option of select.options) {
        option.selected = value.includes(get_option_value(option));
      }
      return;
    }
    for (option of select.options) {
      var option_value = get_option_value(option);
      if (is(option_value, value)) {
        option.selected = true;
        return;
      }
    }
    if (!mounting || value !== void 0) {
      select.selectedIndex = -1;
    }
  }
  function init_select(select) {
    var observer = new MutationObserver((entries) => {
      if (entries.every(is_selectedcontent_mutation)) return;
      if ("__defaultValue" in select) {
        apply_default_select_value(select, false);
      }
      if ("__value" in select) {
        select_option(select, select.__value);
      }
    });
    observer.observe(select, {
      // Listen to option element changes
      childList: true,
      subtree: true,
      // because of <optgroup>
      // Listen to option element value attribute changes
      // (doesn't get notified of select value changes,
      // because that property is not reflected as an attribute)
      attributes: true,
      attributeFilter: ["value"]
    });
    teardown(() => {
      observer.disconnect();
    });
  }
  function bind_select_value(select, get3, set2 = get3) {
    var batches = /* @__PURE__ */ new WeakSet();
    var mounting = true;
    listen_to_event_and_reset_event(select, "change", (is_reset) => {
      var query = is_reset ? "[selected]" : ":checked";
      var value;
      if (select.multiple) {
        value = [].map.call(select.querySelectorAll(query), get_option_value);
      } else {
        var selected_option = select.querySelector(query) ?? // will fall back to first non-disabled option if no option is selected
        select.querySelector("option:not([disabled])");
        value = selected_option && get_option_value(selected_option);
      }
      set2(value);
      select.__value = value;
      if (current_batch !== null) {
        batches.add(current_batch);
      }
    });
    effect(() => {
      var value = get3();
      if (select === document.activeElement) {
        var batch = (
          /** @type {Batch} */
          async_mode_flag ? previous_batch : current_batch
        );
        if (batches.has(batch)) {
          return;
        }
      }
      select_option(select, value, mounting);
      if (mounting && value === void 0) {
        var selected_option = select.querySelector(":checked");
        if (selected_option !== null) {
          value = get_option_value(selected_option);
          set2(value);
        }
      }
      select.__value = value;
      mounting = false;
    });
  }
  function get_option_value(option) {
    if ("__value" in option) {
      return option.__value;
    } else {
      return option.value;
    }
  }
  function is_selectedcontent_mutation(entry) {
    if (
      /** @type {Element} */
      entry.target.closest("selectedcontent") !== null
    ) {
      return true;
    }
    if (entry.type === "childList") {
      var nodes = [...entry.addedNodes, ...entry.removedNodes];
      return nodes.length > 0 && nodes.every((node) => node.nodeName === "SELECTEDCONTENT");
    }
    return false;
  }

  // node_modules/svelte/src/internal/client/dom/elements/attributes.js
  var IS_CUSTOM_ELEMENT = /* @__PURE__ */ Symbol("is custom element");
  var IS_HTML = /* @__PURE__ */ Symbol("is html");
  var LINK_TAG = IS_XHTML ? "link" : "LINK";
  var PROGRESS_TAG = IS_XHTML ? "progress" : "PROGRESS";
  function remove_input_defaults(input) {
    if (!hydrating) return;
    var already_removed = false;
    var remove_defaults = () => {
      if (already_removed) return;
      already_removed = true;
      if (input.hasAttribute("value")) {
        var value = input.value;
        set_attribute2(input, "value", null);
        input.value = value;
      }
      if (input.hasAttribute("checked")) {
        var checked = input.checked;
        set_attribute2(input, "checked", null);
        input.checked = checked;
      }
    };
    input[FORM_RESET_HANDLER] = remove_defaults;
    queue_micro_task(remove_defaults);
    add_form_reset_listener();
  }
  function set_value(element2, value) {
    var attributes = get_attributes(element2);
    if (attributes.value === (attributes.value = // treat null and undefined the same for the initial value
    value ?? void 0) || // @ts-expect-error
    // `progress` elements always need their value set when it's `0`
    element2.value === value && (value !== 0 || element2.nodeName !== PROGRESS_TAG)) {
      return;
    }
    element2.value = value ?? "";
  }
  function set_checked(element2, checked) {
    var attributes = get_attributes(element2);
    if (attributes.checked === (attributes.checked = // treat null and undefined the same for the initial value
    checked ?? void 0)) {
      return;
    }
    element2.checked = checked;
  }
  function set_attribute2(element2, attribute, value, skip_warning) {
    var attributes = get_attributes(element2);
    if (hydrating) {
      attributes[attribute] = element2.getAttribute(attribute);
      if (attribute === "src" || attribute === "srcset" || attribute === "href" && element2.nodeName === LINK_TAG) {
        if (!skip_warning) {
          check_src_in_dev_hydration(element2, attribute, value ?? "");
        }
        return;
      }
    }
    if (attributes[attribute] === (attributes[attribute] = value)) return;
    if (attribute === "loading") {
      element2[LOADING_ATTR_SYMBOL] = value;
    }
    if (value == null) {
      element2.removeAttribute(attribute);
    } else if (typeof value !== "string" && get_setters(element2).has(attribute)) {
      element2[attribute] = value;
    } else {
      element2.setAttribute(attribute, value);
    }
  }
  function get_attributes(element2) {
    return (
      /** @type {Record<string | symbol, unknown>} **/
      /** @type {any} */
      element2[ATTRIBUTES_CACHE] ??= {
        [IS_CUSTOM_ELEMENT]: element2.nodeName.includes("-"),
        [IS_HTML]: element2.namespaceURI === NAMESPACE_HTML
      }
    );
  }
  var setters_cache = /* @__PURE__ */ new Map();
  function get_setters(element2) {
    var cache_key = element2.getAttribute("is") || element2.nodeName;
    var setters = setters_cache.get(cache_key);
    if (setters) return setters;
    setters_cache.set(cache_key, setters = /* @__PURE__ */ new Set());
    var descriptors;
    var proto = element2;
    var element_proto = Element.prototype;
    while (element_proto !== proto) {
      descriptors = get_descriptors(proto);
      for (var key2 in descriptors) {
        if (descriptors[key2].set && // better safe than sorry, we don't want spread attributes to mess with HTML content
        key2 !== "innerHTML" && key2 !== "textContent" && key2 !== "innerText") {
          setters.add(key2);
        }
      }
      proto = get_prototype_of(proto);
    }
    return setters;
  }
  function check_src_in_dev_hydration(element2, attribute, value) {
    if (!dev_fallback_default) return;
    if (attribute === "srcset" && srcset_url_equal(element2, value)) return;
    if (src_url_equal(element2.getAttribute(attribute) ?? "", value)) return;
    hydration_attribute_changed(
      attribute,
      element2.outerHTML.replace(element2.innerHTML, element2.innerHTML && "..."),
      String(value)
    );
  }
  function src_url_equal(element_src, url) {
    if (element_src === url) return true;
    return new URL(element_src, document.baseURI).href === new URL(url, document.baseURI).href;
  }
  function split_srcset(srcset) {
    return srcset.split(",").map((src) => src.trim().split(" ").filter(Boolean));
  }
  function srcset_url_equal(element2, srcset) {
    var element_urls = split_srcset(element2.srcset);
    var urls = split_srcset(srcset);
    return urls.length === element_urls.length && urls.every(
      ([url, width], i) => width === element_urls[i][1] && // We need to test both ways because Vite will create an a full URL with
      // `new URL(asset, import.meta.url).href` for the client when `base: './'`, and the
      // relative URLs inside srcset are not automatically resolved to absolute URLs by
      // browsers (in contrast to img.src). This means both SSR and DOM code could
      // contain relative or absolute URLs.
      (src_url_equal(element_urls[i][0], url) || src_url_equal(url, element_urls[i][0]))
    );
  }

  // node_modules/svelte/src/internal/client/dom/elements/bindings/input.js
  function bind_value(input, get3, set2 = get3) {
    var batches = /* @__PURE__ */ new WeakSet();
    listen_to_event_and_reset_event(input, "input", async (is_reset) => {
      if (dev_fallback_default && input.type === "checkbox") {
        bind_invalid_checkbox_value();
      }
      var value = is_reset ? input.defaultValue : input.value;
      value = is_numberlike_input(input) ? to_number(value) : value;
      set2(value);
      if (current_batch !== null) {
        batches.add(current_batch);
      }
      await tick();
      if (value !== (value = get3())) {
        var start = input.selectionStart;
        var end = input.selectionEnd;
        var length = input.value.length;
        input.value = value ?? "";
        if (end !== null) {
          var new_length = input.value.length;
          if (start === end && end === length && new_length > length) {
            input.selectionStart = new_length;
            input.selectionEnd = new_length;
          } else {
            input.selectionStart = start;
            input.selectionEnd = Math.min(end, new_length);
          }
        }
      }
    });
    if (
      // If we are hydrating and the value has since changed,
      // then use the updated value from the input instead.
      hydrating && input.defaultValue !== input.value || // If defaultValue is set, then value == defaultValue
      // TODO Svelte 6: remove input.value check and set to empty string?
      untrack(get3) == null && input.value
    ) {
      set2(is_numberlike_input(input) ? to_number(input.value) : input.value);
      if (current_batch !== null) {
        batches.add(current_batch);
      }
    }
    render_effect(() => {
      if (dev_fallback_default && input.type === "checkbox") {
        bind_invalid_checkbox_value();
      }
      var value = get3();
      if (input === document.activeElement) {
        var batch = (
          /** @type {Batch} */
          async_mode_flag ? previous_batch : current_batch
        );
        if (batches.has(batch)) {
          return;
        }
      }
      if (is_numberlike_input(input) && value === to_number(input.value)) {
        return;
      }
      if (input.type === "date" && !value && !input.value) {
        return;
      }
      if (value !== input.value) {
        input.value = value ?? "";
      }
    });
  }
  function bind_checked(input, get3, set2 = get3) {
    listen_to_event_and_reset_event(input, "change", (is_reset) => {
      var value = is_reset ? input.defaultChecked : input.checked;
      set2(value);
    });
    if (
      // If we are hydrating and the value has since changed,
      // then use the update value from the input instead.
      hydrating && input.defaultChecked !== input.checked || // If defaultChecked is set, then checked == defaultChecked
      untrack(get3) == null
    ) {
      set2(input.checked);
    }
    render_effect(() => {
      var value = get3();
      input.checked = Boolean(value);
    });
  }
  function is_numberlike_input(input) {
    var type = input.type;
    return type === "number" || type === "range";
  }
  function to_number(value) {
    return value === "" ? null : +value;
  }

  // node_modules/svelte/src/internal/client/dom/elements/bindings/this.js
  function is_bound_this(bound_value, element_or_component) {
    return bound_value === element_or_component || bound_value?.[STATE_SYMBOL] === element_or_component;
  }
  function bind_this(element_or_component = mark_as_component(), update2, get_value, get_parts) {
    var component_effect = (
      /** @type {ComponentContext} */
      component_context.r
    );
    var parent = (
      /** @type {Effect} */
      active_effect
    );
    effect(() => {
      var old_parts;
      var parts;
      render_effect(() => {
        old_parts = parts;
        parts = get_parts?.() || [];
        untrack(() => {
          if (!is_bound_this(get_value(...parts), element_or_component)) {
            update2(element_or_component, ...parts);
            if (old_parts && is_bound_this(get_value(...old_parts), element_or_component)) {
              update2(null, ...old_parts);
            }
          }
        });
      });
      return () => {
        let p = parent;
        while (p !== component_effect && p.parent !== null && p.parent.f & DESTROYING) {
          p = p.parent;
        }
        const teardown2 = () => {
          if (parts && is_bound_this(get_value(...parts), element_or_component)) {
            update2(null, ...parts);
          }
        };
        const original_teardown = p.teardown;
        p.teardown = () => {
          teardown2();
          original_teardown?.();
        };
      };
    });
    return element_or_component;
  }

  // node_modules/svelte/src/internal/client/reactivity/props.js
  function prop(props, key2, flags2, fallback2) {
    var runes = !legacy_mode_flag || (flags2 & PROPS_IS_RUNES) !== 0;
    var bindable = (flags2 & PROPS_IS_BINDABLE) !== 0;
    var lazy = (flags2 & PROPS_IS_LAZY_INITIAL) !== 0;
    var fallback_value = (
      /** @type {V} */
      fallback2
    );
    var fallback_dirty = true;
    var fallback_signal = (
      /** @type {Derived<V> | undefined} */
      void 0
    );
    var get_fallback = () => {
      if (lazy && runes) {
        fallback_signal ??= derived(
          /** @type {() => V} */
          fallback2
        );
        return get2(fallback_signal);
      }
      if (fallback_dirty) {
        fallback_dirty = false;
        fallback_value = lazy ? untrack(
          /** @type {() => V} */
          fallback2
        ) : (
          /** @type {V} */
          fallback2
        );
      }
      return fallback_value;
    };
    let setter;
    if (bindable) {
      var is_entry_props = STATE_SYMBOL in props || LEGACY_PROPS in props;
      setter = get_descriptor(props, key2)?.set ?? (is_entry_props && key2 in props ? (v) => props[key2] = v : void 0);
    }
    var initial_value;
    var is_store_sub = false;
    if (bindable) {
      [initial_value, is_store_sub] = capture_store_binding(() => (
        /** @type {V} */
        props[key2]
      ));
    } else {
      initial_value = /** @type {V} */
      props[key2];
    }
    if (initial_value === void 0 && fallback2 !== void 0) {
      initial_value = get_fallback();
      if (setter) {
        if (runes) props_invalid_value(key2);
        setter(initial_value);
      }
    }
    var getter;
    if (runes) {
      getter = () => {
        var value = (
          /** @type {V} */
          props[key2]
        );
        if (value === void 0) return get_fallback();
        fallback_dirty = true;
        return value;
      };
    } else {
      getter = () => {
        var value = (
          /** @type {V} */
          props[key2]
        );
        if (value !== void 0) {
          fallback_value = /** @type {V} */
          void 0;
        }
        return value === void 0 ? fallback_value : value;
      };
    }
    if (runes && (flags2 & PROPS_IS_UPDATED) === 0) {
      return getter;
    }
    if (setter) {
      var legacy_parent = props.$$legacy;
      return (
        /** @type {() => V} */
        (function(value, mutation) {
          if (arguments.length > 0) {
            if (!runes || !mutation || legacy_parent || is_store_sub) {
              setter(mutation ? getter() : value);
            }
            return value;
          }
          return getter();
        })
      );
    }
    var overridden = false;
    var d = ((flags2 & PROPS_IS_IMMUTABLE) !== 0 ? derived : derived_safe_equal)(() => {
      overridden = false;
      return getter();
    });
    if (dev_fallback_default) {
      d.label = key2;
    }
    if (bindable) get2(d);
    var parent_effect = (
      /** @type {Effect} */
      active_effect
    );
    return (
      /** @type {() => V} */
      (function(value, mutation) {
        if (arguments.length > 0) {
          const new_value = mutation ? get2(d) : runes && bindable ? proxy(value) : value;
          set(d, new_value);
          overridden = true;
          if (fallback_value !== void 0) {
            fallback_value = new_value;
          }
          return value;
        }
        if (is_destroying_effect && overridden || (parent_effect.f & DESTROYED) !== 0) {
          return d.v;
        }
        return get2(d);
      })
    );
  }

  // node_modules/svelte/src/legacy/legacy-client.js
  function createClassComponent(options) {
    return new Svelte4Component(options);
  }
  var Svelte4Component = class {
    /** @type {any} */
    #events;
    /** @type {Record<string, any>} */
    #instance;
    /**
     * @param {ComponentConstructorOptions & {
     *  component: any;
     * }} options
     */
    constructor(options) {
      var sources = /* @__PURE__ */ new Map();
      var add_source = (key2, value) => {
        var s = mutable_source(value, false, false);
        sources.set(key2, s);
        return s;
      };
      const props = new Proxy(
        { ...options.props || {}, $$events: {} },
        {
          get(target2, prop2) {
            return get2(sources.get(prop2) ?? add_source(prop2, Reflect.get(target2, prop2)));
          },
          has(target2, prop2) {
            if (prop2 === LEGACY_PROPS) return true;
            get2(sources.get(prop2) ?? add_source(prop2, Reflect.get(target2, prop2)));
            return Reflect.has(target2, prop2);
          },
          set(target2, prop2, value) {
            set(sources.get(prop2) ?? add_source(prop2, value), value);
            return Reflect.set(target2, prop2, value);
          }
        }
      );
      this.#instance = (options.hydrate ? hydrate : mount)(options.component, {
        target: options.target,
        anchor: options.anchor,
        props,
        context: options.context,
        intro: options.intro ?? false,
        recover: options.recover,
        transformError: options.transformError
      });
      if (!async_mode_flag && (!options?.props?.$$host || options.sync === false)) {
        flushSync();
      }
      this.#events = props.$$events;
      for (const key2 of Object.keys(this.#instance)) {
        if (key2 === "$set" || key2 === "$destroy" || key2 === "$on") continue;
        define_property(this, key2, {
          get() {
            return this.#instance[key2];
          },
          /** @param {any} value */
          set(value) {
            this.#instance[key2] = value;
          },
          enumerable: true
        });
      }
      this.#instance.$set = /** @param {Record<string, any>} next */
      (next2) => {
        Object.assign(props, next2);
      };
      this.#instance.$destroy = () => {
        unmount(this.#instance);
      };
    }
    /** @param {Record<string, any>} props */
    $set(props) {
      this.#instance.$set(props);
    }
    /**
     * @param {string} event
     * @param {(...args: any[]) => any} callback
     * @returns {any}
     */
    $on(event2, callback) {
      this.#events[event2] = this.#events[event2] || [];
      const cb = (...args) => callback.call(this, ...args);
      this.#events[event2].push(cb);
      return () => {
        this.#events[event2] = this.#events[event2].filter(
          /** @param {any} fn */
          (fn) => fn !== cb
        );
      };
    }
    $destroy() {
      this.#instance.$destroy();
    }
  };

  // node_modules/svelte/src/internal/client/dom/elements/custom-element.js
  var SvelteElement;
  if (typeof HTMLElement === "function") {
    SvelteElement = class extends HTMLElement {
      /** The Svelte component constructor */
      $$ctor;
      /** Slots */
      $$s;
      /** @type {any} The Svelte component instance */
      $$c;
      /** Whether or not the custom element is connected */
      $$cn = false;
      /** @type {Record<string, any>} Component props data */
      $$d = {};
      /** `true` if currently in the process of reflecting component props back to attributes */
      $$r = false;
      /** @type {Record<string, CustomElementPropDefinition>} Props definition (name, reflected, type etc) */
      $$p_d = {};
      /** @type {Record<string, EventListenerOrEventListenerObject[]>} Event listeners */
      $$l = {};
      /** @type {Map<EventListenerOrEventListenerObject, Function>} Event listener unsubscribe functions */
      $$l_u = /* @__PURE__ */ new Map();
      /** @type {any} The managed render effect for reflecting attributes */
      $$me;
      /** @type {ShadowRoot | null} The ShadowRoot of the custom element */
      $$shadowRoot = null;
      /**
       * @param {*} $$componentCtor
       * @param {*} $$slots
       * @param {ShadowRootInit | undefined} shadow_root_init
       */
      constructor($$componentCtor, $$slots, shadow_root_init) {
        super();
        this.$$ctor = $$componentCtor;
        this.$$s = $$slots;
        if (shadow_root_init) {
          this.$$shadowRoot = this.attachShadow(shadow_root_init);
        }
      }
      /**
       * @param {string} type
       * @param {EventListenerOrEventListenerObject} listener
       * @param {boolean | AddEventListenerOptions} [options]
       */
      addEventListener(type, listener, options) {
        this.$$l[type] = this.$$l[type] || [];
        this.$$l[type].push(listener);
        if (this.$$c) {
          const unsub = this.$$c.$on(type, listener);
          this.$$l_u.set(listener, unsub);
        }
        super.addEventListener(type, listener, options);
      }
      /**
       * @param {string} type
       * @param {EventListenerOrEventListenerObject} listener
       * @param {boolean | AddEventListenerOptions} [options]
       */
      removeEventListener(type, listener, options) {
        super.removeEventListener(type, listener, options);
        if (this.$$c) {
          const unsub = this.$$l_u.get(listener);
          if (unsub) {
            unsub();
            this.$$l_u.delete(listener);
          }
        }
      }
      async connectedCallback() {
        this.$$cn = true;
        if (!this.$$c) {
          let create_slot = function(name) {
            return (anchor) => {
              const slot2 = create_element("slot");
              if (name !== "default") slot2.name = name;
              append(anchor, slot2);
            };
          };
          await Promise.resolve();
          if (!this.$$cn || this.$$c) {
            return;
          }
          const $$slots = {};
          const existing_slots = get_custom_elements_slots(this);
          for (const name of this.$$s) {
            if (name in existing_slots) {
              if (name === "default" && !this.$$d.children) {
                this.$$d.children = create_slot(name);
                $$slots.default = true;
              } else {
                $$slots[name] = create_slot(name);
              }
            }
          }
          for (const attribute of this.attributes) {
            const name = this.$$g_p(attribute.name);
            if (!(name in this.$$d)) {
              this.$$d[name] = get_custom_element_value(name, attribute.value, this.$$p_d, "toProp");
            }
          }
          for (const key2 in this.$$p_d) {
            if (!(key2 in this.$$d) && this[key2] !== void 0) {
              this.$$d[key2] = this[key2];
              delete this[key2];
            }
          }
          this.$$c = createClassComponent({
            component: this.$$ctor,
            target: this.$$shadowRoot || this,
            props: {
              ...this.$$d,
              $$slots,
              $$host: this
            }
          });
          this.$$me = effect_root(() => {
            render_effect(() => {
              this.$$r = true;
              for (const key2 of object_keys(this.$$c)) {
                if (!this.$$p_d[key2]?.reflect) continue;
                this.$$d[key2] = this.$$c[key2];
                const attribute_value = get_custom_element_value(
                  key2,
                  this.$$d[key2],
                  this.$$p_d,
                  "toAttribute"
                );
                if (attribute_value == null) {
                  this.removeAttribute(this.$$p_d[key2].attribute || key2);
                } else {
                  this.setAttribute(this.$$p_d[key2].attribute || key2, attribute_value);
                }
              }
              this.$$r = false;
            });
          });
          for (const type in this.$$l) {
            for (const listener of this.$$l[type]) {
              const unsub = this.$$c.$on(type, listener);
              this.$$l_u.set(listener, unsub);
            }
          }
          this.$$l = {};
        }
      }
      // We don't need this when working within Svelte code, but for compatibility of people using this outside of Svelte
      // and setting attributes through setAttribute etc, this is helpful
      /**
       * @param {string} attr
       * @param {string} _oldValue
       * @param {string} newValue
       */
      attributeChangedCallback(attr2, _oldValue, newValue) {
        if (this.$$r) return;
        attr2 = this.$$g_p(attr2);
        this.$$d[attr2] = get_custom_element_value(attr2, newValue, this.$$p_d, "toProp");
        this.$$c?.$set({ [attr2]: this.$$d[attr2] });
      }
      disconnectedCallback() {
        this.$$cn = false;
        Promise.resolve().then(() => {
          if (!this.$$cn && this.$$c) {
            this.$$c.$destroy();
            this.$$me();
            this.$$c = void 0;
          }
        });
      }
      /**
       * @param {string} attribute_name
       */
      $$g_p(attribute_name) {
        return object_keys(this.$$p_d).find(
          (key2) => this.$$p_d[key2].attribute === attribute_name || !this.$$p_d[key2].attribute && key2.toLowerCase() === attribute_name
        ) || attribute_name;
      }
    };
  }
  function get_custom_element_value(prop2, value, props_definition, transform) {
    const type = props_definition[prop2]?.type;
    value = type === "Boolean" && typeof value !== "boolean" ? value != null : value;
    if (!transform || !props_definition[prop2]) {
      return value;
    } else if (transform === "toAttribute") {
      switch (type) {
        case "Object":
        case "Array":
          return value == null ? null : JSON.stringify(value);
        case "Boolean":
          return value ? "" : null;
        case "Number":
          return value == null ? null : value;
        default:
          return value;
      }
    } else {
      switch (type) {
        case "Object":
        case "Array":
          return value && JSON.parse(value);
        case "Boolean":
          return value;
        // conversion already handled above
        case "Number":
          return value != null ? +value : value;
        default:
          return value;
      }
    }
  }
  function get_custom_elements_slots(element2) {
    const result = {};
    element2.childNodes.forEach((node) => {
      result[
        /** @type {Element} node */
        node.slot || "default"
      ] = true;
    });
    return result;
  }

  // node_modules/svelte/src/index-client.js
  if (dev_fallback_default) {
    let throw_rune_error = function(rune) {
      if (!(rune in globalThis)) {
        let value;
        Object.defineProperty(globalThis, rune, {
          configurable: true,
          // eslint-disable-next-line getter-return
          get: () => {
            if (value !== void 0) {
              return value;
            }
            rune_outside_svelte(rune);
          },
          set: (v) => {
            value = v;
          }
        });
      }
    };
    throw_rune_error("$state");
    throw_rune_error("$effect");
    throw_rune_error("$derived");
    throw_rune_error("$inspect");
    throw_rune_error("$props");
    throw_rune_error("$bindable");
  }
  function onMount(fn) {
    if (component_context === null) {
      lifecycle_outside_component("onMount");
    }
    if (legacy_mode_flag && component_context.l !== null) {
      init_update_callbacks(component_context).m.push(fn);
    } else {
      user_effect(() => {
        const cleanup = untrack(fn);
        if (typeof cleanup === "function") return (
          /** @type {() => void} */
          cleanup
        );
      });
    }
  }
  function onDestroy(fn) {
    if (component_context === null) {
      lifecycle_outside_component("onDestroy");
    }
    onMount(() => () => untrack(fn));
  }
  function init_update_callbacks(context) {
    var l = (
      /** @type {ComponentContextLegacy} */
      context.l
    );
    return l.u ??= { a: [], b: [], m: [] };
  }

  // node_modules/svelte/src/version.js
  var PUBLIC_VERSION = "5";

  // node_modules/svelte/src/internal/disclose-version.js
  if (typeof window !== "undefined") {
    ((window.__svelte ??= {}).v ??= /* @__PURE__ */ new Set()).add(PUBLIC_VERSION);
  }

  // src/api.ts
  var _token = null;
  function setToken(token) {
    _token = token;
    if (token) localStorage.setItem("ego_admin_token", token);
    else localStorage.removeItem("ego_admin_token");
  }
  function getToken() {
    return _token || localStorage.getItem("ego_admin_token");
  }
  function getBaseUrl() {
    return window.location.origin;
  }
  async function request(method, path, body) {
    const token = getToken();
    const headers = { "Content-Type": "application/json" };
    if (token) headers["Authorization"] = `Bearer ${token}`;
    const resp = await fetch(`${getBaseUrl()}${path}`, {
      method,
      headers,
      body: body ? JSON.stringify(body) : void 0
    });
    if (resp.status === 401) {
      setToken(null);
      window.dispatchEvent(new CustomEvent("ego:session-expired"));
      throw new Error("Session expired. Please log in again.");
    }
    if (!resp.ok) {
      const data2 = await resp.json().catch(() => ({}));
      const detail = typeof data2.detail === "string" ? data2.detail : Array.isArray(data2.detail) ? data2.detail.map((e) => e.msg || "Invalid field").join("; ") : `HTTP ${resp.status}`;
      throw new Error(detail);
    }
    if (resp.status === 204) {
      return void 0;
    }
    const data = await resp.json().catch(() => ({}));
    return data;
  }
  async function authProviders() {
    return request("GET", "/auth/providers");
  }
  async function startForgejo(code_challenge) {
    return request("POST", "/auth/forgejo/start", { code_challenge });
  }
  async function exchangeForgejo(state2, code_verifier, ticket) {
    return request("POST", "/auth/forgejo/exchange", { state: state2, code_verifier, ticket });
  }
  async function me() {
    return request("GET", "/auth/me");
  }
  async function login(username, password) {
    return request("POST", "/auth/login", { username, password });
  }
  async function listStudents() {
    return request("GET", "/admin/students");
  }
  async function getStudentProgress(studentId) {
    return request("GET", `/progress/${studentId}`);
  }
  async function createUser(username, password, role) {
    return request("POST", "/admin/users", { username, password, role });
  }
  async function updateRole(userId, role) {
    return request("PUT", `/admin/users/${userId}/role`, { role });
  }
  async function resetPassword(userId, password) {
    return request("PUT", `/admin/users/${userId}/password`, { password });
  }
  async function deleteUser(userId) {
    return request("DELETE", `/admin/users/${userId}`);
  }
  async function getOverview() {
    return request("GET", "/admin/overview");
  }
  async function getCatalog(q) {
    const needle = (q ?? "").trim();
    const path = needle ? `/admin/catalog?q=${encodeURIComponent(needle)}` : "/admin/catalog";
    return request("GET", path);
  }
  async function getTaskStudio(taskId) {
    return request("GET", `/admin/tasks/${encodeURIComponent(taskId)}/studio`);
  }
  async function validateTaskStudio(taskId, body) {
    return request(
      "POST",
      `/admin/tasks/${encodeURIComponent(taskId)}/studio/validate`,
      body
    );
  }
  async function saveTaskStudio(taskId, body) {
    return request(
      "PUT",
      `/admin/tasks/${encodeURIComponent(taskId)}/studio`,
      body
    );
  }

  // src/consoleApi.ts
  async function response(method, path, body, signal) {
    const token = getToken();
    const res = await fetch(getBaseUrl() + "/admin" + path, {
      method,
      signal,
      headers: { "Content-Type": "application/json", ...token ? { Authorization: `Bearer ${token}` } : {} },
      body: body === void 0 ? void 0 : JSON.stringify(body)
    });
    if (res.status === 401) {
      setToken(null);
      window.dispatchEvent(new CustomEvent("ego:session-expired"));
      throw new Error("\u0421\u0435\u0441\u0441\u0438\u044F \u0438\u0441\u0442\u0435\u043A\u043B\u0430. \u0412\u043E\u0439\u0434\u0438 \u0441\u043D\u043E\u0432\u0430, \u0447\u0442\u043E\u0431\u044B \u043F\u0440\u043E\u0434\u043E\u043B\u0436\u0438\u0442\u044C.");
    }
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      const detail = typeof data.detail === "string" ? data.detail : Array.isArray(data.detail) ? data.detail.map((e) => e.msg).join("; ") : `HTTP ${res.status}`;
      throw Object.assign(new Error(detail), { status: res.status });
    }
    return res;
  }
  async function json(method, path, body) {
    const res = await response(method, path, body);
    return res.status === 204 ? void 0 : await res.json();
  }
  var getSettings = () => json("GET", "/settings");
  var saveSettings = (draft, api_key, clear_api_key = false) => json("PUT", "/settings", { ...draft, changes: void 0, api_key, clear_api_key });
  var testAI = () => json("POST", "/settings/ai/test");
  var listModels = () => json("GET", "/settings/ai/models");
  var exportDeployment = async () => (await response("GET", "/settings/deployment")).text();
  var syncContent = (path) => json("POST", "/sync-tasks", { path, source: "manual" });
  var syncLog = () => json("GET", "/sync/log");
  var listChats = () => json("GET", "/assistant/sessions");
  var newChat = () => json("POST", "/assistant/sessions", { title: "\u041D\u043E\u0432\u044B\u0439 \u0447\u0430\u0442" });
  var readChat = (id) => json("GET", `/assistant/sessions/${encodeURIComponent(id)}`);
  var deleteChat = (id) => json("DELETE", `/assistant/sessions/${encodeURIComponent(id)}`);
  async function streamChat(id, content, task_id, signal, event2) {
    const res = await response("POST", `/assistant/sessions/${encodeURIComponent(id)}/messages`, { content, task_id }, signal);
    if (!res.body) throw new Error("\u0411\u0440\u0430\u0443\u0437\u0435\u0440 \u043D\u0435 \u043F\u043E\u0434\u0434\u0435\u0440\u0436\u0438\u0432\u0430\u0435\u0442 \u043F\u043E\u0442\u043E\u043A\u043E\u0432\u044B\u0435 \u043E\u0442\u0432\u0435\u0442\u044B.");
    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    try {
      while (true) {
        const { value, done } = await reader.read();
        buffer += decoder.decode(value, { stream: !done });
        let end;
        while ((end = buffer.indexOf("\n\n")) >= 0) {
          const frame = buffer.slice(0, end);
          buffer = buffer.slice(end + 2);
          const kind = frame.split("\n").find((line) => line.startsWith("event:"))?.slice(6).trim() || "message";
          const data = frame.split("\n").filter((line) => line.startsWith("data:")).map((line) => line.slice(5).trim()).join("\n");
          if (data) event2(kind, JSON.parse(data));
        }
        if (done) break;
      }
    } finally {
      reader.releaseLock();
    }
  }

  // src/components/Login.svelte
  var root = from_html(`<button type="button" class="svelte-h34f85">\u041E\u0442\u043C\u0435\u043D\u0438\u0442\u044C \u0432\u0445\u043E\u0434</button>`);
  var root_1 = from_html(`<button type="button" class="svelte-h34f85"> </button> <!>`, 1);
  var root_2 = from_html(`<form><input type="text" placeholder="\u0418\u043C\u044F \u043F\u043E\u043B\u044C\u0437\u043E\u0432\u0430\u0442\u0435\u043B\u044F" autocomplete="username" class="svelte-h34f85"/> <input type="password" placeholder="\u041F\u0430\u0440\u043E\u043B\u044C" autocomplete="current-password" class="svelte-h34f85"/> <button type="submit" class="svelte-h34f85"> </button></form>`);
  var root_3 = from_html(`<p>\u0412\u0445\u043E\u0434 \u043F\u043E\u043A\u0430 \u043D\u0435 \u043D\u0430\u0441\u0442\u0440\u043E\u0435\u043D. \u041E\u0431\u0440\u0430\u0442\u0438\u0441\u044C \u043A \u0430\u0434\u043C\u0438\u043D\u0438\u0441\u0442\u0440\u0430\u0442\u043E\u0440\u0443.</p>`);
  var root_4 = from_html(`<div class="error svelte-h34f85" role="alert"> </div>`);
  var root_5 = from_html(`<div class="login svelte-h34f85"><h1 class="svelte-h34f85">\u041F\u0430\u043D\u0435\u043B\u044C \u0443\u043F\u0440\u0430\u0432\u043B\u0435\u043D\u0438\u044F</h1> <p class="sub svelte-h34f85">\u0412\u0445\u043E\u0434 \u0434\u043B\u044F \u0430\u0434\u043C\u0438\u043D\u0438\u0441\u0442\u0440\u0430\u0442\u043E\u0440\u0430 \u0438\u043B\u0438 \u043D\u0430\u0441\u0442\u0430\u0432\u043D\u0438\u043A\u0430</p> <!> <!> <!> <!></div>`);
  var $$css = {
    hash: "svelte-h34f85",
    code: ".login.svelte-h34f85 {max-width:320px;margin:80px auto;}h1.svelte-h34f85 {font-size:1.2rem;font-weight:700;margin-bottom:4px;}.sub.svelte-h34f85 {color:#858585;font-size:0.8rem;margin-bottom:24px;}input.svelte-h34f85 {width:100%;padding:8px 12px;margin-bottom:12px;background:#2d2d2d;border:1px solid #3c3c3c;border-radius:4px;color:#d4d4d4;font-family:inherit;font-size:14px;}input.svelte-h34f85:focus {outline:none;border-color:#007acc;}button.svelte-h34f85 {width:100%;padding:8px;background:#007acc;color:#fff;border:none;border-radius:4px;font-family:inherit;font-size:14px;cursor:pointer;}button.svelte-h34f85:hover:not(:disabled) {opacity:0.9;}button.svelte-h34f85:disabled {opacity:0.5;cursor:not-allowed;}.error.svelte-h34f85 {color:#f87171;font-size:0.8rem;margin-top:8px;}"
  };
  function Login($$anchor, $$props) {
    push($$props, true);
    append_styles($$anchor, $$css);
    let username = state("");
    let password = state("");
    let error = state("");
    let loading = state(false);
    let providers = state(null);
    let attempt = 0;
    let popup = null;
    let channel = null;
    onMount(() => {
      void authProviders().then((value) => set(providers, value, true)).catch(() => set(error, "\u041D\u0435 \u0443\u0434\u0430\u043B\u043E\u0441\u044C \u043F\u043E\u043B\u0443\u0447\u0438\u0442\u044C \u0441\u043F\u043E\u0441\u043E\u0431\u044B \u0432\u0445\u043E\u0434\u0430. \u041E\u0431\u043D\u043E\u0432\u0438 \u0441\u0442\u0440\u0430\u043D\u0438\u0446\u0443."));
    });
    onDestroy(() => {
      attempt++;
      popup?.close();
      channel?.close();
    });
    function cancel() {
      attempt++;
      popup?.close();
      channel?.close();
      popup = null;
      set(loading, false);
    }
    async function forgejoLogin() {
      const current = ++attempt;
      set(error, "");
      set(loading, true);
      popup = window.open("about:blank", "_blank");
      if (!popup) {
        set(loading, false);
        set(error, "\u0420\u0430\u0437\u0440\u0435\u0448\u0438 \u043E\u0442\u043A\u0440\u044B\u0442\u0438\u0435 \u043D\u043E\u0432\u043E\u0439 \u0432\u043A\u043B\u0430\u0434\u043A\u0438 \u0434\u043B\u044F \u0432\u0445\u043E\u0434\u0430 \u0447\u0435\u0440\u0435\u0437 Forgejo.");
        return;
      }
      popup.opener = null;
      try {
        const bytes = crypto.getRandomValues(new Uint8Array(32));
        const encode = (data) => btoa(String.fromCharCode(...data)).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
        const verifier = encode(bytes);
        const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(verifier));
        const flow = await startForgejo(encode(new Uint8Array(digest)));
        if (current !== attempt) return;
        if (new URL(flow.authorization_url).origin !== location.origin) throw new Error("\u0410\u0434\u0440\u0435\u0441 \u0432\u0445\u043E\u0434\u0430 \u043D\u0435 \u0441\u043E\u0432\u043F\u0430\u0434\u0430\u0435\u0442 \u0441 \u0430\u0434\u0440\u0435\u0441\u043E\u043C \u0441\u0435\u0440\u0432\u0438\u0441\u0430. \u041F\u0440\u043E\u0432\u0435\u0440\u044C EGO_PUBLIC_URL.");
        let ticket = "";
        let failed = false;
        channel = new BroadcastChannel("ego-forgejo-" + flow.state);
        channel.onmessage = (event2) => {
          if (event2.data?.error === "login_failed") failed = true;
          if (typeof event2.data?.ticket === "string" && /^[A-Za-z0-9_-]{43}$/.test(event2.data.ticket)) ticket = event2.data.ticket;
        };
        popup.location.href = flow.authorization_url;
        const deadline = Date.now() + flow.expires_in * 1e3;
        while (current === attempt && Date.now() < deadline) {
          await new Promise((resolve) => setTimeout(resolve, 1500));
          if (current !== attempt) return;
          if (failed) throw new Error("\u0412\u0445\u043E\u0434 \u043D\u0435 \u0437\u0430\u0432\u0435\u0440\u0448\u0451\u043D \u0438\u043B\u0438 \u0440\u0435\u0433\u0438\u0441\u0442\u0440\u0430\u0446\u0438\u044F \u0437\u0430\u043A\u0440\u044B\u0442\u0430. \u041F\u043E\u043F\u0440\u043E\u0431\u0443\u0439 \u0441\u043D\u043E\u0432\u0430 \u0438\u043B\u0438 \u043E\u0431\u0440\u0430\u0442\u0438\u0441\u044C \u043A \u043D\u0430\u0441\u0442\u0430\u0432\u043D\u0438\u043A\u0443.");
          if (!ticket) continue;
          const result = await exchangeForgejo(flow.state, verifier, ticket);
          if (current !== attempt) return;
          if (!("pending" in result)) {
            popup?.close();
            popup = null;
            $$props.onLogin(result);
            return;
          }
        }
        if (current === attempt) throw new Error("\u0412\u0440\u0435\u043C\u044F \u0432\u0445\u043E\u0434\u0430 \u0438\u0441\u0442\u0435\u043A\u043B\u043E. \u041F\u043E\u043F\u0440\u043E\u0431\u0443\u0439 \u0435\u0449\u0451 \u0440\u0430\u0437.");
      } catch (e) {
        if (current === attempt) {
          set(error, e.message, true);
          popup?.close();
          popup = null;
        }
      } finally {
        if (current === attempt) {
          set(loading, false);
          channel?.close();
          channel = null;
        }
      }
    }
    async function submit() {
      if (!get2(username).trim() || !get2(password)) {
        set(error, "\u0412\u0432\u0435\u0434\u0438 \u0438\u043C\u044F \u043F\u043E\u043B\u044C\u0437\u043E\u0432\u0430\u0442\u0435\u043B\u044F \u0438 \u043F\u0430\u0440\u043E\u043B\u044C");
        return;
      }
      set(error, "");
      set(loading, true);
      try {
        const data = await login(get2(username).trim(), get2(password));
        $$props.onLogin(data);
      } catch (e) {
        set(error, e.message, true);
      } finally {
        set(loading, false);
      }
    }
    var div = root_5();
    var node = sibling(child(div), 4);
    {
      var consequent_1 = ($$anchor2) => {
        var fragment = root_1();
        var button = first_child(fragment);
        var text2 = only_child(button, true);
        var node_1 = sibling(button, 2);
        {
          var consequent = ($$anchor3) => {
            var button_1 = root();
            delegated("click", button_1, cancel);
            append($$anchor3, button_1);
          };
          if_block(node_1, ($$render) => {
            if (get2(loading)) $$render(consequent);
          });
        }
        template_effect(() => {
          button.disabled = get2(loading);
          set_text(text2, get2(loading) ? "\u041E\u0436\u0438\u0434\u0430\u044E \u0432\u0445\u043E\u0434 \u0432 Forgejo\u2026" : "\u0412\u043E\u0439\u0442\u0438 \u0447\u0435\u0440\u0435\u0437 Forgejo");
        });
        delegated("click", button, forgejoLogin);
        append($$anchor2, fragment);
      };
      if_block(node, ($$render) => {
        if (get2(providers)?.forgejo) $$render(consequent_1);
      });
    }
    var node_2 = sibling(node, 2);
    {
      var consequent_2 = ($$anchor2) => {
        var form = root_2();
        var input = child(form);
        remove_input_defaults(input);
        var input_1 = sibling(input, 2);
        remove_input_defaults(input_1);
        var button_2 = sibling(input_1, 2);
        var text_1 = only_child(button_2, true);
        reset(form);
        template_effect(() => {
          button_2.disabled = get2(loading);
          set_text(text_1, get2(loading) ? "\u0412\u0445\u043E\u0436\u0443\u2026" : "\u0412\u043E\u0439\u0442\u0438");
        });
        event("submit", form, (e) => {
          e.preventDefault();
          submit();
        });
        bind_value(input, () => get2(username), ($$value) => set(username, $$value));
        bind_value(input_1, () => get2(password), ($$value) => set(password, $$value));
        append($$anchor2, form);
      };
      if_block(node_2, ($$render) => {
        if (get2(providers)?.local) $$render(consequent_2);
      });
    }
    var node_3 = sibling(node_2, 2);
    {
      var consequent_3 = ($$anchor2) => {
        var p = root_3();
        append($$anchor2, p);
      };
      if_block(node_3, ($$render) => {
        if (get2(providers) && !get2(providers).forgejo && !get2(providers).local) $$render(consequent_3);
      });
    }
    var node_4 = sibling(node_3, 2);
    {
      var consequent_4 = ($$anchor2) => {
        var div_1 = root_4();
        var text_2 = only_child(div_1, true);
        template_effect(() => set_text(text_2, get2(error)));
        append($$anchor2, div_1);
      };
      if_block(node_4, ($$render) => {
        if (get2(error)) $$render(consequent_4);
      });
    }
    reset(div);
    append($$anchor, div);
    pop();
  }
  delegate(["click"]);

  // src/components/Overview.svelte
  var root2 = from_html(`<div class="loading svelte-op2jfd">Loading overview\u2026</div>`);
  var root_12 = from_html(`<div class="error svelte-op2jfd"> </div>`);
  var root_22 = from_html(`<div class="grid svelte-op2jfd"><div class="card svelte-op2jfd"><span class="card-label svelte-op2jfd">Server</span> <span> </span></div> <div class="card svelte-op2jfd"><span class="card-label svelte-op2jfd">Projects</span> <span class="card-value svelte-op2jfd"> </span></div> <div class="card svelte-op2jfd"><span class="card-label svelte-op2jfd">Folders</span> <span class="card-value svelte-op2jfd"> </span></div> <div class="card svelte-op2jfd"><span class="card-label svelte-op2jfd">Tasks</span> <span class="card-value svelte-op2jfd"> </span></div> <div class="card svelte-op2jfd"><span class="card-label svelte-op2jfd">Students</span> <span class="card-value svelte-op2jfd"> </span></div></div> <div class="sync-block svelte-op2jfd"><h3 class="svelte-op2jfd">Latest sync</h3> <dl class="svelte-op2jfd"><div class="svelte-op2jfd"><dt class="svelte-op2jfd">Status</dt><dd class="svelte-op2jfd"><span> </span></dd></div> <div class="svelte-op2jfd"><dt class="svelte-op2jfd">Source</dt><dd class="svelte-op2jfd"> </dd></div> <div class="svelte-op2jfd"><dt class="svelte-op2jfd">Repo</dt><dd class="svelte-op2jfd"> </dd></div> <div class="svelte-op2jfd"><dt class="svelte-op2jfd">Git SHA</dt><dd class="svelte-op2jfd"> </dd></div> <div class="svelte-op2jfd"><dt class="svelte-op2jfd">Started</dt><dd class="svelte-op2jfd"> </dd></div> <div class="svelte-op2jfd"><dt class="svelte-op2jfd">Finished</dt><dd class="svelte-op2jfd"> </dd></div> <div class="svelte-op2jfd"><dt class="svelte-op2jfd">Added</dt><dd class="svelte-op2jfd"> </dd></div> <div class="svelte-op2jfd"><dt class="svelte-op2jfd">Updated</dt><dd class="svelte-op2jfd"> </dd></div> <div class="svelte-op2jfd"><dt class="svelte-op2jfd">Skipped</dt><dd class="svelte-op2jfd"> </dd></div> <div class="svelte-op2jfd"><dt class="svelte-op2jfd">Errors</dt><dd class="svelte-op2jfd"> </dd></div> <div class="full svelte-op2jfd"><dt class="svelte-op2jfd">Error summary</dt><dd class="svelte-op2jfd"> </dd></div></dl></div>`, 1);
  var root_32 = from_html(`<div class="section"><div class="section-header svelte-op2jfd"><h2 class="svelte-op2jfd">Overview</h2> <button class="btn svelte-op2jfd" type="button" aria-label="Refresh overview"> </button></div> <!></div>`);
  var $$css2 = {
    hash: "svelte-op2jfd",
    code: ".section-header.svelte-op2jfd {display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;}h2.svelte-op2jfd {font-size:0.9rem;font-weight:600;}h3.svelte-op2jfd {font-size:0.8rem;font-weight:600;margin:20px 0 10px;color:#858585;text-transform:uppercase;letter-spacing:0.05em;}.btn.svelte-op2jfd {padding:4px 12px;background:transparent;border:1px solid #3c3c3c;border-radius:4px;color:#d4d4d4;font-family:inherit;font-size:0.8rem;cursor:pointer;}.btn.svelte-op2jfd:hover:not(:disabled) {border-color:#007acc;}.btn.svelte-op2jfd:disabled {opacity:0.5;cursor:not-allowed;}.grid.svelte-op2jfd {display:grid;grid-template-columns:repeat(auto-fit, minmax(140px, 1fr));gap:12px;}.card.svelte-op2jfd {display:flex;flex-direction:column;gap:4px;padding:14px 16px;background:#2d2d2d;border:1px solid #3c3c3c;border-radius:6px;}.card-label.svelte-op2jfd {font-size:0.7rem;text-transform:uppercase;letter-spacing:0.05em;color:#858585;}.card-value.svelte-op2jfd {font-size:1.4rem;font-weight:700;font-variant-numeric:tabular-nums;}.status-ok.svelte-op2jfd {color:#22c55e;}.status-err.svelte-op2jfd {color:#f87171;}.sync-block.svelte-op2jfd {margin-top:8px;}dl.svelte-op2jfd {display:grid;grid-template-columns:max-content 1fr;gap:6px 16px;margin:0;}dl.svelte-op2jfd div:where(.svelte-op2jfd) {display:contents;}dl.svelte-op2jfd .full:where(.svelte-op2jfd) {grid-column:1 / -1;}dt.svelte-op2jfd {color:#858585;font-size:0.75rem;}dd.svelte-op2jfd {margin:0;font-size:0.85rem;word-break:break-word;}.sync-pill.svelte-op2jfd {display:inline-block;padding:1px 8px;border-radius:10px;font-size:0.7rem;border:1px solid #3c3c3c;text-transform:capitalize;}.sync-pill.ok.svelte-op2jfd {color:#22c55e;border-color:#22c55e;}.sync-pill.running.svelte-op2jfd {color:#eab308;border-color:#eab308;}.sync-pill.err.svelte-op2jfd {color:#f87171;border-color:#f87171;}.sync-pill.none.svelte-op2jfd {color:#858585;}.loading.svelte-op2jfd, .error.svelte-op2jfd {padding:24px;text-align:center;color:#858585;}.error.svelte-op2jfd {color:#f87171;}\r\n\r\n	@media (max-width: 600px) {dl.svelte-op2jfd {grid-template-columns:1fr;}\r\n	}"
  };
  function Overview($$anchor, $$props) {
    push($$props, true);
    append_styles($$anchor, $$css2);
    let overview = state(null);
    let loading = state(true);
    let error = state("");
    async function load() {
      set(loading, true);
      set(error, "");
      try {
        set(overview, await getOverview(), true);
      } catch (e) {
        set(error, e.message, true);
      } finally {
        set(loading, false);
      }
    }
    function timeAgo(iso) {
      if (!iso) return "\u2014";
      const t = new Date(iso).getTime();
      if (Number.isNaN(t)) return iso;
      const s = Math.round((Date.now() - t) / 1e3);
      if (s < 0) return "just now";
      if (s < 60) return `${s}s ago`;
      if (s < 3600) return `${Math.round(s / 60)}m ago`;
      if (s < 86400) return `${Math.round(s / 3600)}h ago`;
      return `${Math.round(s / 86400)}d ago`;
    }
    function syncStatusClass(s) {
      if (!s) return "none";
      const st = (s.status || "").toLowerCase();
      if (st === "ok" || st === "success") return "ok";
      if (st === "running") return "running";
      return "err";
    }
    function syncLabel(s) {
      if (!s) return "never";
      return s.status || "\u2014";
    }
    function errorSummary(s) {
      if (!s) return "";
      if (s.errors <= 0 && !s.error_details) return "No errors.";
      const parts = [];
      parts.push(`${s.errors} error(s)`);
      if (s.error_details) parts.push(s.error_details);
      return parts.join(" \u2014 ");
    }
    onMount(() => {
      load();
    });
    var div = root_32();
    var div_1 = child(div);
    var button = sibling(child(div_1), 2);
    var text2 = only_child(button, true);
    reset(div_1);
    var node = sibling(div_1, 2);
    {
      var consequent = ($$anchor2) => {
        var div_2 = root2();
        append($$anchor2, div_2);
      };
      var consequent_1 = ($$anchor2) => {
        var div_3 = root_12();
        var text_1 = only_child(div_3, true);
        template_effect(() => set_text(text_1, get2(error)));
        append($$anchor2, div_3);
      };
      var consequent_2 = ($$anchor2) => {
        var fragment = root_22();
        var div_4 = first_child(fragment);
        var div_5 = child(div_4);
        var span = sibling(child(div_5), 2);
        var text_2 = only_child(span, true);
        reset(div_5);
        var div_6 = sibling(div_5, 2);
        var span_1 = sibling(child(div_6), 2);
        var text_3 = only_child(span_1, true);
        reset(div_6);
        var div_7 = sibling(div_6, 2);
        var span_2 = sibling(child(div_7), 2);
        var text_4 = only_child(span_2, true);
        reset(div_7);
        var div_8 = sibling(div_7, 2);
        var span_3 = sibling(child(div_8), 2);
        var text_5 = only_child(span_3, true);
        reset(div_8);
        var div_9 = sibling(div_8, 2);
        var span_4 = sibling(child(div_9), 2);
        var text_6 = only_child(span_4, true);
        reset(div_9);
        reset(div_4);
        var div_10 = sibling(div_4, 2);
        var dl = sibling(child(div_10), 2);
        var div_11 = child(dl);
        var dd = sibling(child(div_11));
        var span_5 = child(dd);
        var text_7 = only_child(span_5, true);
        reset(dd);
        reset(div_11);
        var div_12 = sibling(div_11, 2);
        var dd_1 = sibling(child(div_12));
        var text_8 = only_child(dd_1, true);
        reset(div_12);
        var div_13 = sibling(div_12, 2);
        var dd_2 = sibling(child(div_13));
        var text_9 = only_child(dd_2, true);
        reset(div_13);
        var div_14 = sibling(div_13, 2);
        var dd_3 = sibling(child(div_14));
        var text_10 = only_child(dd_3, true);
        reset(div_14);
        var div_15 = sibling(div_14, 2);
        var dd_4 = sibling(child(div_15));
        var text_11 = only_child(dd_4, true);
        reset(div_15);
        var div_16 = sibling(div_15, 2);
        var dd_5 = sibling(child(div_16));
        var text_12 = only_child(dd_5, true);
        reset(div_16);
        var div_17 = sibling(div_16, 2);
        var dd_6 = sibling(child(div_17));
        var text_13 = only_child(dd_6, true);
        reset(div_17);
        var div_18 = sibling(div_17, 2);
        var dd_7 = sibling(child(div_18));
        var text_14 = only_child(dd_7, true);
        reset(div_18);
        var div_19 = sibling(div_18, 2);
        var dd_8 = sibling(child(div_19));
        var text_15 = only_child(dd_8, true);
        reset(div_19);
        var div_20 = sibling(div_19, 2);
        var dd_9 = sibling(child(div_20));
        var text_16 = only_child(dd_9, true);
        reset(div_20);
        var div_21 = sibling(div_20, 2);
        var dd_10 = sibling(child(div_21));
        var text_17 = only_child(dd_10, true);
        reset(div_21);
        reset(dl);
        reset(div_10);
        template_effect(
          ($0, $1, $2, $3, $4) => {
            set_class(span, 1, `card-value status-${get2(overview).server === "ok" ? "ok" : "err"}`, "svelte-op2jfd");
            set_text(text_2, get2(overview).server);
            set_text(text_3, get2(overview).counts.projects);
            set_text(text_4, get2(overview).counts.folders);
            set_text(text_5, get2(overview).counts.tasks);
            set_text(text_6, get2(overview).counts.students);
            set_class(span_5, 1, `sync-pill ${$0 ?? ""}`, "svelte-op2jfd");
            set_text(text_7, $1);
            set_text(text_8, get2(overview).latest_sync?.source ?? "\u2014");
            set_text(text_9, get2(overview).latest_sync?.repo_url || "\u2014");
            set_text(text_10, get2(overview).latest_sync?.git_sha ?? "\u2014");
            set_text(text_11, $2);
            set_text(text_12, $3);
            set_text(text_13, get2(overview).latest_sync?.added ?? 0);
            set_text(text_14, get2(overview).latest_sync?.updated ?? 0);
            set_text(text_15, get2(overview).latest_sync?.skipped ?? 0);
            set_text(text_16, get2(overview).latest_sync?.errors ?? 0);
            set_text(text_17, $4);
          },
          [
            () => syncStatusClass(get2(overview).latest_sync),
            () => syncLabel(get2(overview).latest_sync),
            () => get2(overview).latest_sync ? timeAgo(get2(overview).latest_sync.started_at) : "\u2014",
            () => get2(overview).latest_sync ? timeAgo(get2(overview).latest_sync.finished_at) : "\u2014",
            () => errorSummary(get2(overview).latest_sync)
          ]
        );
        append($$anchor2, fragment);
      };
      if_block(node, ($$render) => {
        if (get2(loading) && !get2(overview)) $$render(consequent);
        else if (get2(error)) $$render(consequent_1, 1);
        else if (get2(overview)) $$render(consequent_2, 2);
      });
    }
    reset(div);
    template_effect(() => {
      button.disabled = get2(loading);
      set_text(text2, get2(loading) ? "Refreshing\u2026" : "Refresh");
    });
    delegated("click", button, load);
    append($$anchor, div);
    pop();
  }
  delegate(["click"]);

  // src/components/StudentList.svelte
  var root3 = from_html(`<button class="btn svelte-18vtxcr" type="button"> </button>`);
  var root_13 = from_html(`<p class="error svelte-18vtxcr" role="alert"> </p>`);
  var root_23 = from_html(`<form class="create-form svelte-18vtxcr"><input name="username" placeholder="Username" required="" class="svelte-18vtxcr"/> <input name="password" type="password" placeholder="Password" required="" class="svelte-18vtxcr"/> <select name="role" class="svelte-18vtxcr"><option>student</option><option>admin</option></select> <button type="submit" class="btn primary svelte-18vtxcr">Create</button></form>`);
  var root_33 = from_html(`<div class="loading svelte-18vtxcr">Loading students\u2026</div>`);
  var root_42 = from_html(`<div class="error svelte-18vtxcr" role="alert"> </div> <button class="btn svelte-18vtxcr" type="button">Retry</button>`, 1);
  var root_52 = from_html(`<div class="empty svelte-18vtxcr">No students yet</div>`);
  var root_6 = from_html(`<div class="empty svelte-18vtxcr"> </div>`);
  var root_7 = from_html(`<th class="svelte-18vtxcr"></th>`);
  var root_8 = from_html(`<select class="role-select svelte-18vtxcr"><option>student</option><option>admin</option></select>`);
  var root_9 = from_html(`<button type="button">\u041D\u0430\u0437\u043D\u0430\u0447\u0438\u0442\u044C \u043D\u0430\u0441\u0442\u0430\u0432\u043D\u0438\u043A\u043E\u043C</button>`);
  var root_10 = from_html(`<button title="Reset password" class="svelte-18vtxcr">pw</button>`);
  var root_11 = from_html(`<td class="actions svelte-18vtxcr"><!> <button title="Delete" class="danger svelte-18vtxcr">\xD7</button></td>`);
  var root_122 = from_html(`<tr class="student-row svelte-18vtxcr"><td class="svelte-18vtxcr"> </td><td class="svelte-18vtxcr"><!></td><td class="num svelte-18vtxcr"> </td><td class="num svelte-18vtxcr" style="color:#22c55e"> </td><td class="num svelte-18vtxcr" style="color:#eab308"> </td><td class="num svelte-18vtxcr" style="color:#f87171"> </td><td class="svelte-18vtxcr"> </td><!></tr>`);
  var root_132 = from_html(`<div class="pagination svelte-18vtxcr" aria-label="Student list pages"><button class="btn svelte-18vtxcr" type="button">Previous</button> <span> </span> <button class="btn svelte-18vtxcr" type="button">Next</button></div>`);
  var root_14 = from_html(`<table class="svelte-18vtxcr"><thead><tr><th class="svelte-18vtxcr">Student</th><th class="svelte-18vtxcr">Role</th><th class="num svelte-18vtxcr">Total</th><th class="num svelte-18vtxcr">Passed</th><th class="num svelte-18vtxcr">Partial</th><th class="num svelte-18vtxcr">Failed</th><th class="svelte-18vtxcr">Last activity</th><!></tr></thead><tbody></tbody></table> <!>`, 1);
  var root_15 = from_html(`<div class="list-toolbar svelte-18vtxcr"><label for="student-search">Search students</label> <input id="student-search" type="search" placeholder="Username or ID" class="svelte-18vtxcr"/> <span> </span></div> <!>`, 1);
  var root_16 = from_html(`<div class="section"><div class="section-header svelte-18vtxcr"><h2 class="svelte-18vtxcr">Students</h2> <div class="header-actions svelte-18vtxcr"><button class="btn svelte-18vtxcr" type="button"> </button> <!></div></div> <!> <!> <!></div>`);
  var $$css3 = {
    hash: "svelte-18vtxcr",
    code: ".section-header.svelte-18vtxcr {display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;}.header-actions.svelte-18vtxcr {display:flex;gap:8px;}h2.svelte-18vtxcr {font-size:0.9rem;font-weight:600;}.btn.svelte-18vtxcr {padding:4px 12px;background:transparent;border:1px solid #3c3c3c;border-radius:4px;color:#d4d4d4;font-family:inherit;font-size:0.8rem;cursor:pointer;}.btn.svelte-18vtxcr:hover {border-color:#007acc;}.btn.primary.svelte-18vtxcr {background:#007acc;color:#fff;border-color:transparent;}.btn.primary.svelte-18vtxcr:hover {opacity:0.9;}.create-form.svelte-18vtxcr {display:flex;gap:8px;margin-bottom:16px;}.create-form.svelte-18vtxcr input:where(.svelte-18vtxcr), .create-form.svelte-18vtxcr select:where(.svelte-18vtxcr) {padding:6px 10px;background:#2d2d2d;border:1px solid #3c3c3c;border-radius:4px;color:#d4d4d4;font-family:inherit;font-size:0.8rem;}.create-form.svelte-18vtxcr input:where(.svelte-18vtxcr) {flex:1;}.list-toolbar.svelte-18vtxcr {display:flex;align-items:center;gap:8px;margin-bottom:12px;color:#858585;font-size:0.75rem;}.list-toolbar.svelte-18vtxcr input:where(.svelte-18vtxcr) {flex:1;min-width:120px;padding:6px 10px;background:#2d2d2d;border:1px solid #3c3c3c;border-radius:4px;color:#d4d4d4;font:inherit;}.list-toolbar.svelte-18vtxcr input:where(.svelte-18vtxcr):focus {outline:none;border-color:#007acc;}table.svelte-18vtxcr {width:100%;border-collapse:collapse;}th.svelte-18vtxcr, td.svelte-18vtxcr {text-align:left;padding:6px 12px;border-bottom:1px solid #3c3c3c;}th.svelte-18vtxcr {font-size:0.7rem;font-weight:600;text-transform:uppercase;letter-spacing:0.05em;color:#858585;}tr.svelte-18vtxcr:hover td:where(.svelte-18vtxcr) {background:rgba(255,255,255,0.03);}.num.svelte-18vtxcr {text-align:right;font-variant-numeric:tabular-nums;}.student-row.svelte-18vtxcr {cursor:pointer;}.student-row.svelte-18vtxcr:hover td:where(.svelte-18vtxcr) {background:rgba(0,122,204,0.08);}.role-select.svelte-18vtxcr {background:#2d2d2d;border:1px solid #3c3c3c;border-radius:3px;color:#d4d4d4;font-family:inherit;font-size:0.75rem;padding:2px 6px;}.actions.svelte-18vtxcr {white-space:nowrap;}.actions.svelte-18vtxcr button:where(.svelte-18vtxcr) {padding:2px 8px;background:transparent;border:1px solid #3c3c3c;border-radius:3px;color:#858585;font-family:inherit;font-size:0.7rem;cursor:pointer;margin-left:4px;}.actions.svelte-18vtxcr button:where(.svelte-18vtxcr):hover {border-color:#007acc;color:#d4d4d4;}.actions.svelte-18vtxcr .danger:where(.svelte-18vtxcr):hover {border-color:#f87171;color:#f87171;}.pagination.svelte-18vtxcr {display:flex;justify-content:center;align-items:center;gap:12px;margin-top:12px;font-size:0.75rem;color:#858585;}.loading.svelte-18vtxcr, .empty.svelte-18vtxcr, .error.svelte-18vtxcr {padding:24px;text-align:center;color:#858585;}.error.svelte-18vtxcr {color:#f87171;}\r\n	@media (max-width: 600px) {.list-toolbar.svelte-18vtxcr {align-items:stretch;flex-direction:column;}.create-form.svelte-18vtxcr {flex-wrap:wrap;}table.svelte-18vtxcr {display:block;overflow-x:auto;white-space:nowrap;}\r\n	}"
  };
  function StudentList($$anchor, $$props) {
    push($$props, true);
    append_styles($$anchor, $$css3);
    let students = state(proxy([]));
    let loading = state(true);
    let error = state("");
    let actionError = state("");
    let showForm = state(false);
    let localAuthEnabled = state(false);
    let search = state("");
    let page = state(1);
    const pageSize = 25;
    let isAdmin = user_derived(() => $$props.userRole === "admin");
    let filteredStudents = user_derived(() => {
      const needle = get2(search).trim().toLocaleLowerCase();
      if (!needle) return get2(students);
      return get2(students).filter((student) => student.username.toLocaleLowerCase().includes(needle) || student.student_id.toLocaleLowerCase().includes(needle));
    });
    let pageCount = user_derived(() => Math.max(1, Math.ceil(get2(filteredStudents).length / pageSize)));
    let visibleStudents = user_derived(() => get2(filteredStudents).slice((get2(page) - 1) * pageSize, get2(page) * pageSize));
    async function load() {
      set(loading, true);
      set(error, "");
      set(actionError, "");
      try {
        set(students, await listStudents(), true);
        set(page, 1);
      } catch (e) {
        set(error, e.message, true);
      } finally {
        set(loading, false);
      }
    }
    async function handleDelete(student) {
      if (!confirm(`Delete ${student.username}? This removes their progress too.`)) return;
      try {
        await deleteUser(student.student_id);
        await load();
      } catch (e) {
        set(actionError, `Could not delete ${student.username}: ${e.message}`);
      }
    }
    async function handleRoleChange(student, newRole) {
      if (newRole === student.role) return;
      if (newRole === "mentor" && !confirm(`\u041D\u0430\u0437\u043D\u0430\u0447\u0438\u0442\u044C ${student.username} \u043D\u0430\u0441\u0442\u0430\u0432\u043D\u0438\u043A\u043E\u043C? \u041E\u043D \u0441\u043C\u043E\u0436\u0435\u0442 \u043D\u0430\u0437\u043D\u0430\u0447\u0430\u0442\u044C \u0434\u0440\u0443\u0433\u0438\u0445 \u043D\u0430\u0441\u0442\u0430\u0432\u043D\u0438\u043A\u043E\u0432.`)) return;
      try {
        await updateRole(student.student_id, newRole);
        await load();
      } catch (e) {
        set(actionError, `Could not update role: ${e.message}`);
      }
    }
    async function handleResetPassword(student) {
      const pw = prompt(`New password for ${student.username}:`);
      if (!pw) return;
      try {
        await resetPassword(student.student_id, pw);
        alert("Password updated.");
      } catch (e) {
        set(actionError, `Could not reset password: ${e.message}`);
      }
    }
    async function handleCreate(e) {
      e.preventDefault();
      const form = e.target;
      const fd = new FormData(form);
      const username = fd.get("username");
      const password = fd.get("password");
      const role = fd.get("role");
      if (!username || !password) return;
      try {
        await createUser(username, password, role);
        form.reset();
        set(showForm, false);
        await load();
      } catch (err) {
        set(actionError, `Could not create user: ${err.message}`);
      }
    }
    function statusColor(status) {
      const s = (status || "").toLowerCase();
      if (s === "passed") return "green";
      if (s === "partial") return "yellow";
      return "red";
    }
    function timeAgo(iso) {
      if (!iso) return "\u2014";
      const t = new Date(iso).getTime();
      const s = Math.round((Date.now() - t) / 1e3);
      if (s < 60) return `${s}s ago`;
      if (s < 3600) return `${Math.round(s / 60)}m ago`;
      if (s < 86400) return `${Math.round(s / 3600)}h ago`;
      return `${Math.round(s / 86400)}d ago`;
    }
    onMount(() => {
      void load();
      void authProviders().then((value) => set(localAuthEnabled, value.local, true)).catch(() => {
      });
    });
    var div = root_16();
    var div_1 = child(div);
    var div_2 = sibling(child(div_1), 2);
    var button = child(div_2);
    var text2 = only_child(button, true);
    var node = sibling(button, 2);
    {
      var consequent = ($$anchor2) => {
        var button_1 = root3();
        var text_1 = only_child(button_1, true);
        template_effect(() => set_text(text_1, get2(showForm) ? "Cancel" : "+ Add user"));
        delegated("click", button_1, () => {
          set(showForm, !get2(showForm));
        });
        append($$anchor2, button_1);
      };
      if_block(node, ($$render) => {
        if (get2(isAdmin) && get2(localAuthEnabled)) $$render(consequent);
      });
    }
    reset(div_2);
    reset(div_1);
    var node_1 = sibling(div_1, 2);
    {
      var consequent_1 = ($$anchor2) => {
        var p = root_13();
        var text_2 = only_child(p, true);
        template_effect(() => set_text(text_2, get2(actionError)));
        append($$anchor2, p);
      };
      if_block(node_1, ($$render) => {
        if (get2(actionError)) $$render(consequent_1);
      });
    }
    var node_2 = sibling(node_1, 2);
    {
      var consequent_2 = ($$anchor2) => {
        var form_1 = root_23();
        var select = sibling(child(form_1), 4);
        var option = child(select);
        option.value = option.__value = "student";
        var option_1 = sibling(option);
        option_1.value = option_1.__value = "admin";
        reset(select);
        next(2);
        reset(form_1);
        event("submit", form_1, handleCreate);
        append($$anchor2, form_1);
      };
      if_block(node_2, ($$render) => {
        if (get2(isAdmin) && get2(localAuthEnabled) && get2(showForm)) $$render(consequent_2);
      });
    }
    var node_3 = sibling(node_2, 2);
    {
      var consequent_3 = ($$anchor2) => {
        var div_3 = root_33();
        append($$anchor2, div_3);
      };
      var consequent_4 = ($$anchor2) => {
        var fragment = root_42();
        var div_4 = first_child(fragment);
        var text_3 = only_child(div_4, true);
        var button_2 = sibling(div_4, 2);
        template_effect(() => set_text(text_3, get2(error)));
        delegated("click", button_2, load);
        append($$anchor2, fragment);
      };
      var consequent_5 = ($$anchor2) => {
        var div_5 = root_52();
        append($$anchor2, div_5);
      };
      var alternate_2 = ($$anchor2) => {
        var fragment_1 = root_15();
        var div_6 = first_child(fragment_1);
        var input = sibling(child(div_6), 2);
        remove_input_defaults(input);
        var span = sibling(input, 2);
        var text_4 = only_child(span);
        reset(div_6);
        var node_4 = sibling(div_6, 2);
        {
          var consequent_6 = ($$anchor3) => {
            var div_7 = root_6();
            var text_5 = only_child(div_7);
            template_effect(() => set_text(text_5, `No students match \u201C${get2(search) ?? ""}\u201D.`));
            append($$anchor3, div_7);
          };
          var alternate_1 = ($$anchor3) => {
            var fragment_2 = root_14();
            var table = first_child(fragment_2);
            var thead = child(table);
            var tr = child(thead);
            var node_5 = sibling(child(tr), 7);
            {
              var consequent_7 = ($$anchor4) => {
                var th = root_7();
                append($$anchor4, th);
              };
              if_block(node_5, ($$render) => {
                if (get2(isAdmin)) $$render(consequent_7);
              });
            }
            reset(tr);
            reset(thead);
            var tbody = sibling(thead);
            each(tbody, 21, () => get2(visibleStudents), (s) => s.student_id, ($$anchor4, s) => {
              var tr_1 = root_122();
              var td = child(tr_1);
              var text_6 = only_child(td, true);
              var td_1 = sibling(td);
              var node_6 = child(td_1);
              {
                var consequent_8 = ($$anchor5) => {
                  var select_1 = root_8();
                  var option_2 = child(select_1);
                  option_2.value = option_2.__value = "student";
                  var option_3 = sibling(option_2);
                  option_3.value = option_3.__value = "admin";
                  reset(select_1);
                  var select_1_value;
                  init_select(select_1);
                  template_effect(() => {
                    if (select_1_value !== (select_1_value = get2(s).role)) {
                      select_1.value = (select_1.__value = select_1_value) ?? "", select_option(select_1, select_1_value);
                    }
                  });
                  delegated("change", select_1, (e) => handleRoleChange(get2(s), e.target.value));
                  delegated("click", select_1, (e) => e.stopPropagation());
                  append($$anchor5, select_1);
                };
                var consequent_9 = ($$anchor5) => {
                  var button_3 = root_9();
                  delegated("click", button_3, (e) => {
                    e.stopPropagation();
                    handleRoleChange(get2(s), "mentor");
                  });
                  append($$anchor5, button_3);
                };
                var alternate = ($$anchor5) => {
                  var text_7 = text();
                  template_effect(() => set_text(text_7, get2(s).role));
                  append($$anchor5, text_7);
                };
                if_block(node_6, ($$render) => {
                  if (get2(isAdmin)) $$render(consequent_8);
                  else if ($$props.userRole === "mentor") $$render(consequent_9, 1);
                  else $$render(alternate, -1);
                });
              }
              reset(td_1);
              var td_2 = sibling(td_1);
              var text_8 = only_child(td_2, true);
              var td_3 = sibling(td_2);
              var text_9 = only_child(td_3, true);
              var td_4 = sibling(td_3);
              var text_10 = only_child(td_4, true);
              var td_5 = sibling(td_4);
              var text_11 = only_child(td_5, true);
              var td_6 = sibling(td_5);
              var text_12 = only_child(td_6, true);
              var node_7 = sibling(td_6);
              {
                var consequent_11 = ($$anchor5) => {
                  var td_7 = root_11();
                  var node_8 = child(td_7);
                  {
                    var consequent_10 = ($$anchor6) => {
                      var button_4 = root_10();
                      delegated("click", button_4, (e) => {
                        e.stopPropagation();
                        handleResetPassword(get2(s));
                      });
                      append($$anchor6, button_4);
                    };
                    if_block(node_8, ($$render) => {
                      if (get2(localAuthEnabled)) $$render(consequent_10);
                    });
                  }
                  var button_5 = sibling(node_8, 2);
                  reset(td_7);
                  delegated("click", button_5, (e) => {
                    e.stopPropagation();
                    handleDelete(get2(s));
                  });
                  append($$anchor5, td_7);
                };
                if_block(node_7, ($$render) => {
                  if (get2(isAdmin)) $$render(consequent_11);
                });
              }
              reset(tr_1);
              template_effect(
                ($0) => {
                  set_text(text_6, get2(s).username);
                  set_text(text_8, get2(s).tasks_total);
                  set_text(text_9, get2(s).tasks_passed);
                  set_text(text_10, get2(s).tasks_partial);
                  set_text(text_11, get2(s).tasks_failed);
                  set_text(text_12, $0);
                },
                [() => timeAgo(get2(s).last_activity)]
              );
              delegated("click", tr_1, () => $$props.onSelect(get2(s).student_id, get2(s).username));
              append($$anchor4, tr_1);
            });
            reset(tbody);
            reset(table);
            var node_9 = sibling(table, 2);
            {
              var consequent_12 = ($$anchor4) => {
                var div_8 = root_132();
                var button_6 = child(div_8);
                var span_1 = sibling(button_6, 2);
                var text_13 = only_child(span_1);
                var button_7 = sibling(span_1, 2);
                reset(div_8);
                template_effect(() => {
                  button_6.disabled = get2(page) === 1;
                  set_text(text_13, `Page ${get2(page) ?? ""} of ${get2(pageCount) ?? ""}`);
                  button_7.disabled = get2(page) === get2(pageCount);
                });
                delegated("click", button_6, () => set(page, Math.max(1, get2(page) - 1), true));
                delegated("click", button_7, () => set(page, Math.min(get2(pageCount), get2(page) + 1), true));
                append($$anchor4, div_8);
              };
              if_block(node_9, ($$render) => {
                if (get2(pageCount) > 1) $$render(consequent_12);
              });
            }
            append($$anchor3, fragment_2);
          };
          if_block(node_4, ($$render) => {
            if (get2(filteredStudents).length === 0) $$render(consequent_6);
            else $$render(alternate_1, -1);
          });
        }
        template_effect(() => set_text(text_4, `${get2(filteredStudents).length ?? ""} of ${get2(students).length ?? ""}`));
        delegated("input", input, () => {
          set(page, 1);
        });
        bind_value(input, () => get2(search), ($$value) => set(search, $$value));
        append($$anchor2, fragment_1);
      };
      if_block(node_3, ($$render) => {
        if (get2(loading)) $$render(consequent_3);
        else if (get2(error)) $$render(consequent_4, 1);
        else if (get2(students).length === 0) $$render(consequent_5, 2);
        else $$render(alternate_2, -1);
      });
    }
    reset(div);
    template_effect(() => {
      button.disabled = get2(loading);
      set_text(text2, get2(loading) ? "Refreshing\u2026" : "Refresh");
    });
    delegated("click", button, load);
    append($$anchor, div);
    pop();
  }
  delegate(["click", "input", "change"]);

  // src/components/StudentDetail.svelte
  var root4 = from_html(`<div class="loading svelte-15k1m16">Loading progress\u2026</div>`);
  var root_17 = from_html(`<div class="error svelte-15k1m16" role="alert"> </div> <button class="refresh svelte-15k1m16" type="button">Retry</button>`, 1);
  var root_24 = from_html(`<div class="empty svelte-15k1m16">No progress yet</div>`);
  var root_34 = from_html(`<tr><td class="svelte-15k1m16"> </td><td class="svelte-15k1m16"><span></span> </td><td class="num svelte-15k1m16"> </td><td class="num svelte-15k1m16"> </td><td class="svelte-15k1m16"> </td></tr>`);
  var root_43 = from_html(`<table class="svelte-15k1m16"><thead><tr><th class="svelte-15k1m16">Task</th><th class="svelte-15k1m16">Status</th><th class="num svelte-15k1m16">Score</th><th class="num svelte-15k1m16">Attempts</th><th class="svelte-15k1m16">Last run</th></tr></thead><tbody></tbody></table>`);
  var root_53 = from_html(`<div class="detail"><div class="detail-header svelte-15k1m16"><button class="back svelte-15k1m16" type="button">&larr; Back to students</button> <h2 class="svelte-15k1m16"> </h2> <button class="refresh svelte-15k1m16" type="button"> </button></div> <!></div>`);
  var $$css4 = {
    hash: "svelte-15k1m16",
    code: ".back.svelte-15k1m16 {display:inline-block;margin-bottom:16px;color:#007acc;padding:0;border:0;background:transparent;cursor:pointer;font-family:inherit;font-size:0.8rem;text-decoration:none;}.back.svelte-15k1m16:hover {text-decoration:underline;}.detail-header.svelte-15k1m16 {display:flex;align-items:center;gap:12px;margin-bottom:12px;}h2.svelte-15k1m16 {flex:1;font-size:1rem;font-weight:600;margin:0;}.refresh.svelte-15k1m16 {padding:4px 10px;background:transparent;border:1px solid #3c3c3c;border-radius:4px;color:#d4d4d4;font-family:inherit;font-size:0.75rem;cursor:pointer;}.refresh.svelte-15k1m16:hover:not(:disabled) {border-color:#007acc;}.refresh.svelte-15k1m16:disabled {opacity:0.5;cursor:not-allowed;}table.svelte-15k1m16 {width:100%;border-collapse:collapse;}th.svelte-15k1m16, td.svelte-15k1m16 {text-align:left;padding:6px 12px;border-bottom:1px solid #3c3c3c;}th.svelte-15k1m16 {font-size:0.7rem;font-weight:600;text-transform:uppercase;letter-spacing:0.05em;color:#858585;}.num.svelte-15k1m16 {text-align:right;font-variant-numeric:tabular-nums;}.dot.svelte-15k1m16 {display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:6px;}.dot.green.svelte-15k1m16 {background:#22c55e;}.dot.yellow.svelte-15k1m16 {background:#eab308;}.dot.red.svelte-15k1m16 {background:#f87171;}.loading.svelte-15k1m16, .empty.svelte-15k1m16, .error.svelte-15k1m16 {padding:24px;text-align:center;color:#858585;}.error.svelte-15k1m16 {color:#f87171;}\r\n	@media (max-width: 600px) {.detail-header.svelte-15k1m16 {flex-wrap:wrap;}h2.svelte-15k1m16 {order:3;flex-basis:100%;}\r\n	}"
  };
  function StudentDetail($$anchor, $$props) {
    push($$props, true);
    append_styles($$anchor, $$css4);
    let progress = state(proxy([]));
    let loading = state(true);
    let error = state("");
    async function load() {
      set(loading, true);
      set(error, "");
      try {
        set(progress, await getStudentProgress($$props.studentId), true);
      } catch (e) {
        set(error, e.message, true);
      } finally {
        set(loading, false);
      }
    }
    function statusColor(status) {
      const s = (status || "").toLowerCase();
      if (s === "passed") return "green";
      if (s === "partial") return "yellow";
      return "red";
    }
    function statusLabel(status) {
      const s = (status || "").toLowerCase();
      if (s === "passed") return "PASS";
      if (s === "partial") return "PART";
      if (s === "failed") return "FAIL";
      return (status || "\u2014").toUpperCase();
    }
    function timeAgo(iso) {
      if (!iso) return "\u2014";
      const t = new Date(iso).getTime();
      const s = Math.round((Date.now() - t) / 1e3);
      if (s < 60) return `${s}s ago`;
      if (s < 3600) return `${Math.round(s / 60)}m ago`;
      if (s < 86400) return `${Math.round(s / 3600)}h ago`;
      return `${Math.round(s / 86400)}d ago`;
    }
    onMount(() => {
      load();
    });
    var div = root_53();
    var div_1 = child(div);
    var button = child(div_1);
    var h2 = sibling(button, 2);
    var text2 = only_child(h2);
    var button_1 = sibling(h2, 2);
    var text_1 = only_child(button_1, true);
    reset(div_1);
    var node = sibling(div_1, 2);
    {
      var consequent = ($$anchor2) => {
        var div_2 = root4();
        append($$anchor2, div_2);
      };
      var consequent_1 = ($$anchor2) => {
        var fragment = root_17();
        var div_3 = first_child(fragment);
        var text_2 = only_child(div_3, true);
        var button_2 = sibling(div_3, 2);
        template_effect(() => {
          set_text(text_2, get2(error));
          button_2.disabled = get2(loading);
        });
        delegated("click", button_2, load);
        append($$anchor2, fragment);
      };
      var consequent_2 = ($$anchor2) => {
        var div_4 = root_24();
        append($$anchor2, div_4);
      };
      var alternate = ($$anchor2) => {
        var table = root_43();
        var tbody = sibling(child(table));
        each(tbody, 21, () => get2(progress), (r) => r.task_id + r.version, ($$anchor3, r) => {
          var tr = root_34();
          var td = child(tr);
          var text_3 = only_child(td, true);
          var td_1 = sibling(td);
          var span = child(td_1);
          var text_4 = sibling(span);
          reset(td_1);
          var td_2 = sibling(td_1);
          var text_5 = only_child(td_2);
          var td_3 = sibling(td_2);
          var text_6 = only_child(td_3, true);
          var td_4 = sibling(td_3);
          var text_7 = only_child(td_4, true);
          reset(tr);
          template_effect(
            ($0, $1, $2) => {
              set_text(text_3, get2(r).task_id);
              set_class(span, 1, `dot ${$0 ?? ""}`, "svelte-15k1m16");
              set_text(text_4, ` ${$1 ?? ""}`);
              set_text(text_5, `${get2(r).passed_tests ?? ""}/${get2(r).total_tests ?? ""}`);
              set_text(text_6, get2(r).attempts);
              set_text(text_7, $2);
            },
            [
              () => statusColor(get2(r).status),
              () => statusLabel(get2(r).status),
              () => timeAgo(get2(r).last_run_at)
            ]
          );
          append($$anchor3, tr);
        });
        reset(tbody);
        reset(table);
        append($$anchor2, table);
      };
      if_block(node, ($$render) => {
        if (get2(loading)) $$render(consequent);
        else if (get2(error)) $$render(consequent_1, 1);
        else if (get2(progress).length === 0) $$render(consequent_2, 2);
        else $$render(alternate, -1);
      });
    }
    reset(div);
    template_effect(() => {
      set_text(text2, `Progress: ${$$props.username ?? ""}`);
      button_1.disabled = get2(loading);
      set_text(text_1, get2(loading) ? "Refreshing\u2026" : "Refresh");
    });
    delegated("click", button, function(...$$args) {
      $$props.onBack?.apply(this, $$args);
    });
    delegated("click", button_1, load);
    append($$anchor, div);
    pop();
  }
  delegate(["click"]);

  // src/components/Catalog.svelte
  var root5 = from_html(`<button class="btn svelte-qickb7" type="button" aria-label="Clear search">Clear</button>`);
  var root_18 = from_html(`<div class="loading svelte-qickb7">Loading catalog\u2026</div>`);
  var root_25 = from_html(`<div class="error svelte-qickb7"> </div>`);
  var root_35 = from_html(`<div class="empty svelte-qickb7"> </div>`);
  var root_44 = from_html(`<span class="filtered svelte-qickb7"> </span>`);
  var root_54 = from_html(`<span class="tag svelte-qickb7"> </span>`);
  var root_62 = from_html(`<span class="tag warn svelte-qickb7">breaking</span>`);
  var root_72 = from_html(`<li class="task"><button class="node task-node svelte-qickb7" type="button"><span class="task-id svelte-qickb7"> </span> <span class="task-title svelte-qickb7"> </span> <span class="task-tags svelte-qickb7"><!> <!> <!> <span class="tag svelte-qickb7"> </span></span></button></li>`);
  var root_82 = from_html(`<li class="folder svelte-qickb7"><div class="node folder-node svelte-qickb7"><span class="caret svelte-qickb7">\u25BE</span> <span class="name svelte-qickb7"> </span> <span class="meta svelte-qickb7"> </span> <span class="badge svelte-qickb7"> </span></div> <ul class="sub svelte-qickb7"></ul></li>`);
  var root_92 = from_html(`<li class="project svelte-qickb7"><div class="node project-node svelte-qickb7"><span class="caret svelte-qickb7">\u25BE</span> <span class="name svelte-qickb7"> </span> <span class="meta svelte-qickb7"> </span> <span class="badge svelte-qickb7"> </span></div> <ul class="sub svelte-qickb7"></ul></li>`);
  var root_102 = from_html(`<p class="count svelte-qickb7"> <!></p> <ul class="tree svelte-qickb7"></ul>`, 1);
  var root_112 = from_html(`<div class="section"><div class="section-header svelte-qickb7"><h2 class="svelte-qickb7">Catalog</h2> <button class="btn svelte-qickb7" type="button" aria-label="Refresh catalog"> </button></div> <div class="search svelte-qickb7"><input type="search" placeholder="Search projects, folders, tasks\u2026" aria-label="Search catalog" class="svelte-qickb7"/> <!></div> <!></div>`);
  var $$css5 = {
    hash: "svelte-qickb7",
    code: ".section-header.svelte-qickb7 {display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;}h2.svelte-qickb7 {font-size:0.9rem;font-weight:600;}.btn.svelte-qickb7 {padding:4px 12px;background:transparent;border:1px solid #3c3c3c;border-radius:4px;color:#d4d4d4;font-family:inherit;font-size:0.8rem;cursor:pointer;}.btn.svelte-qickb7:hover:not(:disabled) {border-color:#007acc;}.btn.svelte-qickb7:disabled {opacity:0.5;cursor:not-allowed;}.search.svelte-qickb7 {display:flex;gap:8px;margin-bottom:14px;}.search.svelte-qickb7 input:where(.svelte-qickb7) {flex:1;padding:6px 10px;background:#2d2d2d;border:1px solid #3c3c3c;border-radius:4px;color:#d4d4d4;font-family:inherit;font-size:0.8rem;}.search.svelte-qickb7 input:where(.svelte-qickb7):focus {outline:none;border-color:#007acc;}.count.svelte-qickb7 {font-size:0.75rem;color:#858585;margin:0 0 12px;}.filtered.svelte-qickb7 {color:#007acc;}.tree.svelte-qickb7, .sub.svelte-qickb7 {list-style:none;margin:0;padding:0;}.sub.svelte-qickb7 {padding-left:20px;border-left:1px solid #3c3c3c;margin-left:8px;}.project.svelte-qickb7 > .sub:where(.svelte-qickb7), .folder.svelte-qickb7 > .sub:where(.svelte-qickb7) {margin-top:2px;}.node.svelte-qickb7 {display:flex;align-items:center;gap:8px;padding:4px 8px;border-radius:4px;}.project-node.svelte-qickb7 {font-weight:600;}.folder-node.svelte-qickb7 {color:#d4d4d4;}.task-node.svelte-qickb7 {width:100%;text-align:left;background:transparent;border:1px solid transparent;color:#d4d4d4;font-family:inherit;font-size:0.8rem;cursor:pointer;}.task-node.svelte-qickb7:hover {background:rgba(0,122,204,0.08);border-color:#3c3c3c;}.caret.svelte-qickb7 {color:#858585;width:12px;font-size:0.7rem;}.name.svelte-qickb7 {flex:0 1 auto;}.meta.svelte-qickb7 {color:#858585;font-size:0.7rem;}.badge.svelte-qickb7 {margin-left:auto;padding:1px 8px;border:1px solid #3c3c3c;border-radius:10px;font-size:0.7rem;color:#858585;}.task-id.svelte-qickb7 {color:#007acc;font-family:inherit;flex:0 0 auto;}.task-title.svelte-qickb7 {flex:1 1 auto;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}.task-tags.svelte-qickb7 {display:inline-flex;gap:4px;flex:0 0 auto;}.tag.svelte-qickb7 {padding:0 6px;border:1px solid #3c3c3c;border-radius:3px;font-size:0.65rem;color:#858585;}.tag.warn.svelte-qickb7 {color:#eab308;border-color:#eab308;}.loading.svelte-qickb7, .empty.svelte-qickb7, .error.svelte-qickb7 {padding:24px;text-align:center;color:#858585;}.error.svelte-qickb7 {color:#f87171;}\r\n\r\n	@media (max-width: 600px) {.sub.svelte-qickb7 {padding-left:12px;}.task-title.svelte-qickb7 {white-space:normal;}\r\n	}"
  };
  function Catalog($$anchor, $$props) {
    push($$props, true);
    append_styles($$anchor, $$css5);
    let catalog = state(null);
    let loading = state(true);
    let error = state("");
    let query = state("");
    let activeQuery = state("");
    let debounce = null;
    let requestId = 0;
    function cancelDebounce() {
      if (debounce) clearTimeout(debounce);
      debounce = null;
    }
    async function load(q) {
      const currentRequest = ++requestId;
      set(loading, true);
      set(error, "");
      try {
        const result = await getCatalog(q);
        if (currentRequest !== requestId) return;
        set(catalog, result, true);
        set(activeQuery, q, true);
      } catch (e) {
        if (currentRequest === requestId) set(error, e.message, true);
      } finally {
        if (currentRequest === requestId) set(loading, false);
      }
    }
    function onInput(e) {
      set(query, e.target.value, true);
      requestId++;
      set(error, "");
      cancelDebounce();
      debounce = setTimeout(
        () => {
          debounce = null;
          void load(get2(query));
        },
        250
      );
    }
    function clearSearch() {
      cancelDebounce();
      set(query, "");
      void load("");
    }
    function taskCount(p) {
      return p.folders.reduce((n, f) => n + f.tasks.length, 0);
    }
    function totalTasks() {
      if (!get2(catalog)) return 0;
      return get2(catalog).projects.reduce((n, p) => n + taskCount(p), 0);
    }
    onMount(() => {
      void load("");
      return () => {
        cancelDebounce();
        requestId++;
      };
    });
    var div = root_112();
    var div_1 = child(div);
    var button = sibling(child(div_1), 2);
    var text2 = only_child(button, true);
    reset(div_1);
    var div_2 = sibling(div_1, 2);
    var input = child(div_2);
    remove_input_defaults(input);
    var node = sibling(input, 2);
    {
      var consequent = ($$anchor2) => {
        var button_1 = root5();
        delegated("click", button_1, clearSearch);
        append($$anchor2, button_1);
      };
      if_block(node, ($$render) => {
        if (get2(query)) $$render(consequent);
      });
    }
    reset(div_2);
    var node_1 = sibling(div_2, 2);
    {
      var consequent_1 = ($$anchor2) => {
        var div_3 = root_18();
        append($$anchor2, div_3);
      };
      var consequent_2 = ($$anchor2) => {
        var div_4 = root_25();
        var text_1 = only_child(div_4, true);
        template_effect(() => set_text(text_1, get2(error)));
        append($$anchor2, div_4);
      };
      var consequent_3 = ($$anchor2) => {
        var div_5 = root_35();
        var text_2 = only_child(div_5, true);
        template_effect(() => set_text(text_2, get2(activeQuery) ? `No matches for "${get2(activeQuery)}"` : "Catalog is empty \u2014 run a sync to populate."));
        append($$anchor2, div_5);
      };
      var consequent_8 = ($$anchor2) => {
        var fragment = root_102();
        var p_1 = first_child(fragment);
        var text_3 = child(p_1);
        var node_2 = sibling(text_3);
        {
          var consequent_4 = ($$anchor3) => {
            var span = root_44();
            var text_4 = only_child(span);
            template_effect(() => set_text(text_4, `\xB7 filtered by "${get2(activeQuery) ?? ""}"`));
            append($$anchor3, span);
          };
          if_block(node_2, ($$render) => {
            if (get2(activeQuery)) $$render(consequent_4);
          });
        }
        reset(p_1);
        var ul = sibling(p_1, 2);
        each(ul, 21, () => get2(catalog).projects, (p) => p.id, ($$anchor3, p) => {
          var li = root_92();
          var div_6 = child(li);
          var span_1 = sibling(child(div_6), 2);
          var text_5 = only_child(span_1, true);
          var span_2 = sibling(span_1, 2);
          var text_6 = only_child(span_2);
          var span_3 = sibling(span_2, 2);
          var text_7 = only_child(span_3);
          reset(div_6);
          var ul_1 = sibling(div_6, 2);
          each(ul_1, 21, () => get2(p).folders, (f) => f.id, ($$anchor4, f) => {
            var li_1 = root_82();
            var div_7 = child(li_1);
            var span_4 = sibling(child(div_7), 2);
            var text_8 = only_child(span_4, true);
            var span_5 = sibling(span_4, 2);
            var text_9 = only_child(span_5);
            var span_6 = sibling(span_5, 2);
            var text_10 = only_child(span_6, true);
            reset(div_7);
            var ul_2 = sibling(div_7, 2);
            each(ul_2, 21, () => get2(f).tasks, (t) => t.id, ($$anchor5, t) => {
              var li_2 = root_72();
              var button_2 = child(li_2);
              var span_7 = child(button_2);
              var text_11 = only_child(span_7, true);
              var span_8 = sibling(span_7, 2);
              var text_12 = only_child(span_8, true);
              var span_9 = sibling(span_8, 2);
              var node_3 = child(span_9);
              {
                var consequent_5 = ($$anchor6) => {
                  var span_10 = root_54();
                  var text_13 = only_child(span_10, true);
                  template_effect(() => set_text(text_13, get2(t).block));
                  append($$anchor6, span_10);
                };
                if_block(node_3, ($$render) => {
                  if (get2(t).block) $$render(consequent_5);
                });
              }
              var node_4 = sibling(node_3, 2);
              {
                var consequent_6 = ($$anchor6) => {
                  var span_11 = root_54();
                  var text_14 = only_child(span_11, true);
                  template_effect(() => set_text(text_14, get2(t).level));
                  append($$anchor6, span_11);
                };
                if_block(node_4, ($$render) => {
                  if (get2(t).level) $$render(consequent_6);
                });
              }
              var node_5 = sibling(node_4, 2);
              {
                var consequent_7 = ($$anchor6) => {
                  var span_12 = root_62();
                  append($$anchor6, span_12);
                };
                if_block(node_5, ($$render) => {
                  if (get2(t).breaking) $$render(consequent_7);
                });
              }
              var span_13 = sibling(node_5, 2);
              var text_15 = only_child(span_13);
              reset(span_9);
              reset(button_2);
              reset(li_2);
              template_effect(() => {
                set_attribute2(button_2, "aria-label", `Open task ${get2(t).task_id}: ${get2(t).title}`);
                set_text(text_11, get2(t).task_id);
                set_text(text_12, get2(t).title || get2(t).slug);
                set_text(text_15, `v${get2(t).version ?? ""}`);
              });
              delegated("click", button_2, () => $$props.onSelectTask(get2(t)));
              append($$anchor5, li_2);
            });
            reset(ul_2);
            reset(li_1);
            template_effect(() => {
              set_text(text_8, get2(f).name || get2(f).code);
              set_text(text_9, `${get2(f).code ?? ""}${get2(f).level ? ` \xB7 ${get2(f).level}` : ""}`);
              set_text(text_10, get2(f).tasks.length);
            });
            append($$anchor4, li_1);
          });
          reset(ul_1);
          reset(li);
          template_effect(
            ($0, $1) => {
              set_text(text_5, get2(p).name || get2(p).id);
              set_text(text_6, `${get2(p).id ?? ""} \xB7 v${get2(p).version ?? ""}`);
              set_text(text_7, `${$0 ?? ""} task${$1 ?? ""}`);
            },
            [
              () => taskCount(get2(p)),
              () => taskCount(get2(p)) === 1 ? "" : "s"
            ]
          );
          append($$anchor3, li);
        });
        reset(ul);
        template_effect(
          ($0, $1) => set_text(text_3, `${get2(catalog).projects.length ?? ""} project${get2(catalog).projects.length === 1 ? "" : "s"}
			\xB7 ${$0 ?? ""} task${$1 ?? ""} `),
          [() => totalTasks(), () => totalTasks() === 1 ? "" : "s"]
        );
        append($$anchor2, fragment);
      };
      if_block(node_1, ($$render) => {
        if (get2(loading) && !get2(catalog)) $$render(consequent_1);
        else if (get2(error)) $$render(consequent_2, 1);
        else if (get2(catalog) && get2(catalog).projects.length === 0) $$render(consequent_3, 2);
        else if (get2(catalog)) $$render(consequent_8, 3);
      });
    }
    reset(div);
    template_effect(() => {
      button.disabled = get2(loading);
      set_text(text2, get2(loading) ? "Refreshing\u2026" : "Refresh");
      set_value(input, get2(query));
    });
    delegated("click", button, () => {
      cancelDebounce();
      void load(get2(query));
    });
    delegated("input", input, onInput);
    append($$anchor, div);
    pop();
  }
  delegate(["click", "input"]);

  // src/components/TaskStudio.svelte
  var root6 = from_html(`<div class="loading svelte-1ci3929">Loading task studio\u2026</div>`);
  var root_19 = from_html(`<div class="error svelte-1ci3929"> </div> <button class="btn svelte-1ci3929" type="button" aria-label="Retry loading">Retry</button>`, 1);
  var root_26 = from_html(`<div class="error svelte-1ci3929" role="alert"> </div> <button class="btn svelte-1ci3929" type="button">Retry reload</button>`, 1);
  var root_36 = from_html(`<span class="dirty svelte-1ci3929" title="Unsaved changes">\u25CF dirty</span>`);
  var root_45 = from_html(`<div class="readonly-banner svelte-1ci3929" role="alert"> </div>`);
  var root_55 = from_html(`<div class="readonly-banner svelte-1ci3929" role="alert">Browse-only: mentors may view but not edit task content.</div>`);
  var root_63 = from_html(`<div class="readonly-banner svelte-1ci3929" role="alert"> <button class="btn svelte-1ci3929" type="button">Discard draft and use server version</button></div>`);
  var root_73 = from_html(`<p class="notice svelte-1ci3929" role="status" aria-live="polite"> </p>`);
  var root_83 = from_html(`<p class="error svelte-1ci3929" role="alert"> </p>`);
  var root_93 = from_html(`<p class="success svelte-1ci3929" role="status"> </p>`);
  var root_103 = from_html(`<button class="btn primary svelte-1ci3929" type="button" aria-label="Validate candidate"> </button> <button class="btn primary svelte-1ci3929" type="button" aria-label="Save candidate to canonical files"> </button> <button class="btn svelte-1ci3929" type="button" aria-label="Revert to server state">Revert</button>`, 1);
  var root_113 = from_html(`<span class="hint svelte-1ci3929">Mentor role: browse-only. No write actions available.</span>`);
  var root_123 = from_html(`<!> <dl class="meta svelte-1ci3929"><div class="svelte-1ci3929"><dt class="svelte-1ci3929">Task</dt><dd class="svelte-1ci3929"><strong> </strong></dd></div> <div class="svelte-1ci3929"><dt class="svelte-1ci3929">ID</dt><dd class="svelte-1ci3929"><code class="svelte-1ci3929"> </code></dd></div> <div class="svelte-1ci3929"><dt class="svelte-1ci3929">Version</dt><dd class="svelte-1ci3929"><code class="svelte-1ci3929"> </code><!></dd></div> <div class="svelte-1ci3929"><dt class="svelte-1ci3929">Version policy</dt><dd class="svelte-1ci3929"><code class="svelte-1ci3929"> </code></dd></div> <div class="svelte-1ci3929"><dt class="svelte-1ci3929">Canonical path</dt><dd class="svelte-1ci3929"><code class="svelte-1ci3929"> </code></dd></div></dl> <!> <!> <div class="tabs svelte-1ci3929" role="tablist" aria-label="Task content"><button role="tab" id="tab-statement" aria-controls="panel-statement" type="button">Statement Markdown</button> <button role="tab" id="tab-solution" aria-controls="panel-solution" type="button">Reference Solution</button> <button role="tab" id="tab-tests" aria-controls="panel-tests" type="button">Tests</button></div> <div id="panel-statement" role="tabpanel" aria-labelledby="tab-statement" class="svelte-1ci3929"><textarea class="editor svelte-1ci3929" spellcheck="false" wrap="off" aria-label="Statement markdown (full, including frontmatter)"></textarea></div> <div id="panel-solution" role="tabpanel" aria-labelledby="tab-solution" class="svelte-1ci3929"><textarea class="editor svelte-1ci3929" spellcheck="false" wrap="off" aria-label="Reference solution Python"></textarea></div> <div id="panel-tests" role="tabpanel" aria-labelledby="tab-tests" class="svelte-1ci3929"><textarea class="editor svelte-1ci3929" spellcheck="false" wrap="off" aria-label="Tests Python"></textarea></div> <!> <!> <!> <!> <!> <div class="actions svelte-1ci3929"><!></div>`, 1);
  var root_133 = from_html(`<div class="section"><div class="section-header svelte-1ci3929"><button class="btn back svelte-1ci3929" type="button" aria-label="Back to Catalog">\u2190 Catalog</button> <h2 class="svelte-1ci3929">Task Studio</h2> <button class="btn svelte-1ci3929" type="button" aria-label="Reload task studio"> </button></div> <!></div>`);
  var $$css6 = {
    hash: "svelte-1ci3929",
    code: `.section-header.svelte-1ci3929 {display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;gap:8px;}h2.svelte-1ci3929 {font-size:0.9rem;font-weight:600;}.btn.svelte-1ci3929 {padding:4px 12px;background:transparent;border:1px solid #3c3c3c;border-radius:4px;color:#d4d4d4;font-family:inherit;font-size:0.8rem;cursor:pointer;}.btn.svelte-1ci3929:hover:not(:disabled) {border-color:#007acc;}.btn.svelte-1ci3929:disabled {opacity:0.5;cursor:not-allowed;}.btn.primary.svelte-1ci3929 {border-color:#007acc;color:#007acc;}.btn.primary.svelte-1ci3929:hover:not(:disabled) {background:rgba(0,122,204,0.12);}.btn.back.svelte-1ci3929 {border-color:transparent;color:#858585;}.btn.back.svelte-1ci3929:hover:not(:disabled) {color:#d4d4d4;}.meta.svelte-1ci3929 {display:grid;grid-template-columns:repeat(auto-fit, minmax(200px, 1fr));gap:8px 16px;margin:0 0 12px;padding:12px;background:#2d2d2d;border:1px solid #3c3c3c;border-radius:6px;}.meta.svelte-1ci3929 div:where(.svelte-1ci3929) {display:flex;flex-direction:column;gap:2px;min-width:0;}.meta.svelte-1ci3929 dt:where(.svelte-1ci3929) {font-size:0.65rem;text-transform:uppercase;letter-spacing:0.05em;color:#858585;}.meta.svelte-1ci3929 dd:where(.svelte-1ci3929) {margin:0;font-size:0.8rem;word-break:break-all;}.meta.svelte-1ci3929 code:where(.svelte-1ci3929) {font-family:inherit;color:#d4d4d4;}.dirty.svelte-1ci3929 {color:#eab308;font-size:0.7rem;}.readonly-banner.svelte-1ci3929 {padding:8px 12px;margin-bottom:12px;background:rgba(234,179,8,0.08);border:1px solid #eab308;border-radius:4px;color:#eab308;font-size:0.8rem;}.tabs.svelte-1ci3929 {display:flex;gap:2px;border-bottom:1px solid #3c3c3c;margin-bottom:0;}.tabs.svelte-1ci3929 button:where(.svelte-1ci3929) {padding:6px 14px;background:transparent;border:1px solid transparent;border-bottom:none;border-radius:4px 4px 0 0;color:#858585;font-family:inherit;font-size:0.8rem;cursor:pointer;}.tabs.svelte-1ci3929 button:where(.svelte-1ci3929):hover {color:#d4d4d4;}.tabs.svelte-1ci3929 button.active:where(.svelte-1ci3929) {color:#d4d4d4;background:#2d2d2d;border-color:#3c3c3c;}.tabs.svelte-1ci3929 button[aria-selected="true"]:where(.svelte-1ci3929) {color:#d4d4d4;}div[role="tabpanel"].svelte-1ci3929 {margin:0;}.editor.svelte-1ci3929 {width:100%;min-height:420px;box-sizing:border-box;resize:vertical;padding:12px;background:#1e1e1e;border:1px solid #3c3c3c;border-radius:0 4px 4px 4px;color:#d4d4d4;font-family:'JetBrains Mono', 'Cascadia Code', 'Fira Code', 'Consolas', monospace;font-size:0.8rem;line-height:1.5;white-space:pre;overflow:auto;}.editor.svelte-1ci3929:focus {outline:none;border-color:#007acc;}.editor.svelte-1ci3929:disabled {opacity:0.85;cursor:not-allowed;background:#252525;}.actions.svelte-1ci3929 {display:flex;gap:8px;margin-top:12px;flex-wrap:wrap;align-items:center;}.hint.svelte-1ci3929 {color:#858585;font-size:0.75rem;}.notice.svelte-1ci3929 {color:#858585;font-size:0.75rem;margin:12px 0 0;}.success.svelte-1ci3929 {color:#4ade80;font-size:0.78rem;margin:12px 0 0;word-break:break-word;}.error.svelte-1ci3929 {color:#f87171;font-size:0.78rem;margin:12px 0 0;word-break:break-word;}.loading.svelte-1ci3929 {padding:24px;text-align:center;color:#858585;}\r
\r
	@media (max-width: 600px) {.meta.svelte-1ci3929 {grid-template-columns:1fr;}.tabs.svelte-1ci3929 button:where(.svelte-1ci3929) {padding:6px 10px;font-size:0.75rem;}.editor.svelte-1ci3929 {min-height:320px;}\r
	}`
  };
  function TaskStudio($$anchor, $$props) {
    push($$props, true);
    append_styles($$anchor, $$css6);
    let draft = prop($$props, "draft", 3, null);
    const canEdit = user_derived(() => $$props.role === "admin");
    let studio = state(null);
    let loading = state(true);
    let loadError = state("");
    let mdBuffer = state("");
    let solBuffer = state("");
    let testsBuffer = state("");
    let expectedVersion = state("");
    let expectedEtag = state("");
    let activeTab = state("statement");
    let validating = state(false);
    let validateError = state("");
    let validateResult = state(null);
    let saving = state(false);
    let saveError = state("");
    let saveResult = state(null);
    let notice = state(
      ""
      // generic transient status (e.g. reloaded)
    );
    let draftConflict = state(false);
    let draftConflictMessage = state("");
    let appliedDraft = null;
    let isBusy = user_derived(() => get2(loading) || get2(saving) || get2(validating));
    function isDirty() {
      if (get2(draftConflict)) return true;
      if (!get2(studio)) return false;
      return get2(mdBuffer) !== get2(studio).markdown || get2(solBuffer) !== get2(studio).solution_py || get2(testsBuffer) !== get2(studio).tests_py;
    }
    const editable = user_derived(() => !!get2(studio) && get2(studio).writable && get2(canEdit));
    user_effect(() => {
      const dirty = isDirty();
      $$props.onDirtyChange?.(dirty);
      if (!dirty) return;
      const warnBeforeUnload = (event2) => {
        event2.preventDefault();
        event2.returnValue = "";
      };
      window.addEventListener("beforeunload", warnBeforeUnload);
      return () => window.removeEventListener("beforeunload", warnBeforeUnload);
    });
    user_effect(() => {
      const busy = get2(saving) || get2(validating);
      $$props.onBusyChange?.(busy);
    });
    function confirmDiscard(action2) {
      return !isDirty() || confirm(`You have unsaved task changes. ${action2} and discard them?`);
    }
    async function load({ confirmDirty = true, allowBusy = false } = {}) {
      if (!allowBusy && (get2(saving) || get2(validating) || get2(loading) && !!get2(studio))) return;
      if (confirmDirty && !confirmDiscard("Reload")) return;
      set(loading, true);
      set(loadError, "");
      set(validateResult, null);
      set(validateError, "");
      set(saveResult, null);
      set(saveError, "");
      set(notice, "");
      set(draftConflict, false);
      set(draftConflictMessage, "");
      try {
        const data = await getTaskStudio($$props.taskId);
        set(studio, data, true);
        const incomingDraft = draft() && draft() !== appliedDraft ? draft() : null;
        if (incomingDraft) {
          appliedDraft = incomingDraft;
          const matchesServer = incomingDraft.expected_version === data.version && incomingDraft.expected_content_etag === data.content_etag;
          set(mdBuffer, incomingDraft.markdown, true);
          set(solBuffer, incomingDraft.solution_py, true);
          set(testsBuffer, incomingDraft.tests_py, true);
          set(expectedVersion, incomingDraft.expected_version, true);
          set(expectedEtag, incomingDraft.expected_content_etag, true);
          set(draftConflict, !matchesServer);
          if (!matchesServer) {
            set(draftConflictMessage, `Draft is based on v${incomingDraft.expected_version}; server is now v${data.version}. Draft text is preserved below. Copy it before discarding or reloading.`);
          }
        } else {
          set(mdBuffer, data.markdown, true);
          set(solBuffer, data.solution_py, true);
          set(testsBuffer, data.tests_py, true);
          set(expectedVersion, data.version, true);
          set(expectedEtag, data.content_etag, true);
        }
      } catch (e) {
        set(loadError, e.message, true);
      } finally {
        set(loading, false);
      }
    }
    function resetBuffers() {
      if (!get2(studio)) return;
      if (get2(isBusy) || !confirmDiscard("Revert to the latest server state")) return;
      appliedDraft = draft();
      set(mdBuffer, get2(studio).markdown, true);
      set(solBuffer, get2(studio).solution_py, true);
      set(testsBuffer, get2(studio).tests_py, true);
      set(expectedVersion, get2(studio).version, true);
      set(expectedEtag, get2(studio).content_etag, true);
      set(validateResult, null);
      set(validateError, "");
      set(saveResult, null);
      set(saveError, "");
      set(notice, "Reverted to server state");
      set(draftConflict, false);
      set(draftConflictMessage, "");
    }
    function handleBack() {
      if (get2(isBusy) || !confirmDiscard("Leave Task Studio")) return;
      $$props.onDirtyChange?.(false);
      $$props.onBack();
    }
    function selectTab(tab) {
      set(activeTab, tab, true);
    }
    async function doValidate() {
      if (!get2(editable) || !get2(studio) || get2(isBusy) || get2(draftConflict)) return;
      set(validating, true);
      set(validateError, "");
      set(validateResult, null);
      set(notice, "");
      try {
        const res = await validateTaskStudio($$props.taskId, {
          expected_version: get2(expectedVersion),
          expected_content_etag: get2(expectedEtag),
          markdown: get2(mdBuffer),
          solution_py: get2(solBuffer),
          tests_py: get2(testsBuffer)
        });
        set(validateResult, res, true);
      } catch (e) {
        set(validateError, e.message, true);
      } finally {
        set(validating, false);
      }
    }
    async function doSave() {
      if (!get2(editable) || !get2(studio) || get2(isBusy) || get2(draftConflict)) return;
      set(saving, true);
      set(saveError, "");
      set(saveResult, null);
      set(validateResult, null);
      set(validateError, "");
      set(notice, "");
      try {
        const res = await saveTaskStudio($$props.taskId, {
          expected_version: get2(expectedVersion),
          expected_content_etag: get2(expectedEtag),
          markdown: get2(mdBuffer),
          solution_py: get2(solBuffer),
          tests_py: get2(testsBuffer)
        });
        set(saveResult, res, true);
        await load({ confirmDirty: false, allowBusy: true });
        set(notice, `Saved (v${res.new_version}) \u2014 reloaded from server`);
      } catch (e) {
        set(saveError, e.message, true);
      } finally {
        set(saving, false);
      }
    }
    onMount(() => {
      void load({ confirmDirty: false });
    });
    onDestroy(() => {
      $$props.onDirtyChange?.(false);
      $$props.onBusyChange?.(false);
    });
    var div = root_133();
    var div_1 = child(div);
    var button = child(div_1);
    var button_1 = sibling(button, 4);
    var text2 = only_child(button_1, true);
    reset(div_1);
    var node = sibling(div_1, 2);
    {
      var consequent = ($$anchor2) => {
        var div_2 = root6();
        append($$anchor2, div_2);
      };
      var consequent_1 = ($$anchor2) => {
        var fragment = root_19();
        var div_3 = first_child(fragment);
        var text_1 = only_child(div_3, true);
        var button_2 = sibling(div_3, 2);
        template_effect(() => {
          set_text(text_1, get2(loadError));
          button_2.disabled = get2(isBusy);
        });
        delegated("click", button_2, () => load({ confirmDirty: false }));
        append($$anchor2, fragment);
      };
      var consequent_13 = ($$anchor2) => {
        var fragment_1 = root_123();
        var node_1 = first_child(fragment_1);
        {
          var consequent_2 = ($$anchor3) => {
            var fragment_2 = root_26();
            var div_4 = first_child(fragment_2);
            var text_2 = only_child(div_4);
            var button_3 = sibling(div_4, 2);
            template_effect(() => {
              set_text(text_2, `Could not refresh task: ${get2(loadError) ?? ""}`);
              button_3.disabled = get2(isBusy);
            });
            delegated("click", button_3, () => load({ confirmDirty: false }));
            append($$anchor3, fragment_2);
          };
          if_block(node_1, ($$render) => {
            if (get2(loadError)) $$render(consequent_2);
          });
        }
        var dl = sibling(node_1, 2);
        var div_5 = child(dl);
        var dd = sibling(child(div_5));
        var strong = child(dd);
        var text_3 = only_child(strong, true);
        reset(dd);
        reset(div_5);
        var div_6 = sibling(div_5, 2);
        var dd_1 = sibling(child(div_6));
        var code = child(dd_1);
        var text_4 = only_child(code, true);
        reset(dd_1);
        reset(div_6);
        var div_7 = sibling(div_6, 2);
        var dd_2 = sibling(child(div_7));
        var code_1 = child(dd_2);
        var text_5 = only_child(code_1);
        var node_2 = sibling(code_1);
        {
          var consequent_3 = ($$anchor3) => {
            var span = root_36();
            append($$anchor3, span);
          };
          var d = user_derived(() => isDirty());
          if_block(node_2, ($$render) => {
            if (get2(d)) $$render(consequent_3);
          });
        }
        reset(dd_2);
        reset(div_7);
        var div_8 = sibling(div_7, 2);
        var dd_3 = sibling(child(div_8));
        var code_2 = child(dd_3);
        var text_6 = only_child(code_2, true);
        reset(dd_3);
        reset(div_8);
        var div_9 = sibling(div_8, 2);
        var dd_4 = sibling(child(div_9));
        var code_3 = child(dd_4);
        var text_7 = only_child(code_3, true);
        reset(dd_4);
        reset(div_9);
        reset(dl);
        var node_3 = sibling(dl, 2);
        {
          var consequent_4 = ($$anchor3) => {
            var div_10 = root_45();
            var text_8 = only_child(div_10);
            template_effect(() => set_text(text_8, `Read-only: ${(get2(studio).read_only_reason || "content repo is not writable") ?? ""}. Editing is disabled; ask an admin to make the content repo writable (configure a local repo path with write access).`));
            append($$anchor3, div_10);
          };
          var consequent_5 = ($$anchor3) => {
            var div_11 = root_55();
            append($$anchor3, div_11);
          };
          if_block(node_3, ($$render) => {
            if (!get2(studio).writable) $$render(consequent_4);
            else if (!get2(canEdit)) $$render(consequent_5, 1);
          });
        }
        var node_4 = sibling(node_3, 2);
        {
          var consequent_6 = ($$anchor3) => {
            var div_12 = root_63();
            var text_9 = child(div_12);
            var button_4 = sibling(text_9);
            reset(div_12);
            template_effect(() => {
              set_text(text_9, `${get2(draftConflictMessage) ?? ""} Saving and validation are disabled until you discard this stale draft. `);
              button_4.disabled = get2(isBusy);
            });
            delegated("click", button_4, () => resetBuffers());
            append($$anchor3, div_12);
          };
          if_block(node_4, ($$render) => {
            if (get2(draftConflict)) $$render(consequent_6);
          });
        }
        var div_13 = sibling(node_4, 2);
        var button_5 = child(div_13);
        let classes;
        var button_6 = sibling(button_5, 2);
        let classes_1;
        var button_7 = sibling(button_6, 2);
        let classes_2;
        reset(div_13);
        var div_14 = sibling(div_13, 2);
        var textarea = child(div_14);
        remove_textarea_child(textarea);
        reset(div_14);
        var div_15 = sibling(div_14, 2);
        var textarea_1 = child(div_15);
        remove_textarea_child(textarea_1);
        reset(div_15);
        var div_16 = sibling(div_15, 2);
        var textarea_2 = child(div_16);
        remove_textarea_child(textarea_2);
        reset(div_16);
        var node_5 = sibling(div_16, 2);
        {
          var consequent_7 = ($$anchor3) => {
            var p = root_73();
            var text_10 = only_child(p, true);
            template_effect(() => set_text(text_10, get2(notice)));
            append($$anchor3, p);
          };
          if_block(node_5, ($$render) => {
            if (get2(notice)) $$render(consequent_7);
          });
        }
        var node_6 = sibling(node_5, 2);
        {
          var consequent_8 = ($$anchor3) => {
            var p_1 = root_83();
            var text_11 = only_child(p_1);
            template_effect(() => set_text(text_11, `Validate failed: ${get2(validateError) ?? ""}`));
            append($$anchor3, p_1);
          };
          if_block(node_6, ($$render) => {
            if (get2(validateError)) $$render(consequent_8);
          });
        }
        var node_7 = sibling(node_6, 2);
        {
          var consequent_9 = ($$anchor3) => {
            var p_2 = root_83();
            var text_12 = only_child(p_2);
            template_effect(() => set_text(text_12, `Save failed: ${get2(saveError) ?? ""}`));
            append($$anchor3, p_2);
          };
          if_block(node_7, ($$render) => {
            if (get2(saveError)) $$render(consequent_9);
          });
        }
        var node_8 = sibling(node_7, 2);
        {
          var consequent_10 = ($$anchor3) => {
            var p_3 = root_93();
            var text_13 = only_child(p_3);
            template_effect(() => set_text(text_13, `Valid \u2713 \u2014 task ${get2(validateResult).task_id ?? ""},
				current v${get2(validateResult).current_version ?? ""},
				candidate v${get2(validateResult).candidate_version ?? ""},
				${get2(validateResult).content_changed ? "content changed" : "no content change"},
				policy: ${get2(validateResult).version_policy ?? ""}`));
            append($$anchor3, p_3);
          };
          if_block(node_8, ($$render) => {
            if (get2(validateResult)) $$render(consequent_10);
          });
        }
        var node_9 = sibling(node_8, 2);
        {
          var consequent_11 = ($$anchor3) => {
            var p_4 = root_93();
            var text_14 = only_child(p_4);
            template_effect(() => set_text(text_14, `Saved \u2713 \u2014 task ${get2(saveResult).task_id ?? ""}, new version v${get2(saveResult).new_version ?? ""},
				sync: ${get2(saveResult).sync.status ?? ""}
				(+${get2(saveResult).sync.added ?? ""}/~${get2(saveResult).sync.updated ?? ""}/=${get2(saveResult).sync.skipped ?? ""},
				${get2(saveResult).sync.errors ?? ""} error${get2(saveResult).sync.errors === 1 ? "" : "s"})`));
            append($$anchor3, p_4);
          };
          if_block(node_9, ($$render) => {
            if (get2(saveResult)) $$render(consequent_11);
          });
        }
        var div_17 = sibling(node_9, 2);
        var node_10 = child(div_17);
        {
          var consequent_12 = ($$anchor3) => {
            var fragment_3 = root_103();
            var button_8 = first_child(fragment_3);
            var text_15 = only_child(button_8, true);
            var button_9 = sibling(button_8, 2);
            var text_16 = only_child(button_9, true);
            var button_10 = sibling(button_9, 2);
            template_effect(
              ($0, $1, $2) => {
                button_8.disabled = $0;
                set_text(text_15, get2(validating) ? "Validating\u2026" : "Validate");
                button_9.disabled = $1;
                set_text(text_16, get2(saving) ? "Saving\u2026" : "Save");
                button_10.disabled = $2;
              },
              [
                () => !get2(editable) || get2(validating) || get2(saving) || get2(loading) || get2(draftConflict) || !isDirty(),
                () => !get2(editable) || get2(saving) || get2(validating) || get2(loading) || get2(draftConflict) || !isDirty(),
                () => !get2(editable) || get2(saving) || get2(validating) || get2(loading) || !isDirty()
              ]
            );
            delegated("click", button_8, doValidate);
            delegated("click", button_9, doSave);
            delegated("click", button_10, resetBuffers);
            append($$anchor3, fragment_3);
          };
          var alternate = ($$anchor3) => {
            var span_1 = root_113();
            append($$anchor3, span_1);
          };
          if_block(node_10, ($$render) => {
            if (get2(canEdit)) $$render(consequent_12);
            else $$render(alternate, -1);
          });
        }
        reset(div_17);
        template_effect(() => {
          set_text(text_3, $$props.taskLabel || get2(studio).task_id);
          set_text(text_4, $$props.taskId);
          set_text(text_5, `v${get2(studio).version ?? ""}`);
          set_text(text_6, get2(studio).version_policy ?? "\u2014");
          set_text(text_7, get2(studio).md_path || "\u2014");
          set_attribute2(button_5, "aria-selected", get2(activeTab) === "statement");
          classes = set_class(button_5, 1, "svelte-1ci3929", null, classes, { active: get2(activeTab) === "statement" });
          set_attribute2(button_6, "aria-selected", get2(activeTab) === "solution");
          classes_1 = set_class(button_6, 1, "svelte-1ci3929", null, classes_1, { active: get2(activeTab) === "solution" });
          set_attribute2(button_7, "aria-selected", get2(activeTab) === "tests");
          classes_2 = set_class(button_7, 1, "svelte-1ci3929", null, classes_2, { active: get2(activeTab) === "tests" });
          set_attribute2(div_14, "hidden", get2(activeTab) !== "statement");
          set_value(textarea, get2(mdBuffer));
          textarea.disabled = !get2(editable) || get2(isBusy);
          set_attribute2(div_15, "hidden", get2(activeTab) !== "solution");
          set_value(textarea_1, get2(solBuffer));
          textarea_1.disabled = !get2(editable) || get2(isBusy);
          set_attribute2(div_16, "hidden", get2(activeTab) !== "tests");
          set_value(textarea_2, get2(testsBuffer));
          textarea_2.disabled = !get2(editable) || get2(isBusy);
        });
        delegated("click", button_5, () => selectTab("statement"));
        delegated("click", button_6, () => selectTab("solution"));
        delegated("click", button_7, () => selectTab("tests"));
        delegated("input", textarea, (e) => set(mdBuffer, e.target.value, true));
        delegated("input", textarea_1, (e) => set(solBuffer, e.target.value, true));
        delegated("input", textarea_2, (e) => set(testsBuffer, e.target.value, true));
        append($$anchor2, fragment_1);
      };
      if_block(node, ($$render) => {
        if (get2(loading) && !get2(studio)) $$render(consequent);
        else if (!get2(studio) && get2(loadError)) $$render(consequent_1, 1);
        else if (get2(studio)) $$render(consequent_13, 2);
      });
    }
    reset(div);
    template_effect(() => {
      button.disabled = get2(isBusy);
      button_1.disabled = get2(isBusy);
      set_text(text2, get2(loading) ? "Reloading\u2026" : "Reload");
    });
    delegated("click", button, handleBack);
    delegated("click", button_1, () => load());
    append($$anchor, div);
    pop();
  }
  delegate(["click", "input"]);

  // src/components/Settings.svelte
  var root7 = from_html(`<span class="revision svelte-1u3w06f"> </span>`);
  var root_110 = from_html(`<div class="state-card svelte-1u3w06f" role="status">\u0417\u0430\u0433\u0440\u0443\u0436\u0430\u044E \u043D\u0430\u0441\u0442\u0440\u043E\u0439\u043A\u0438 \u0441\u0435\u0440\u0432\u0438\u0441\u0430\u2026</div>`);
  var root_27 = from_html(`<div class="state-card error svelte-1u3w06f" role="alert"><p class="svelte-1u3w06f"> </p> <button type="button">\u041F\u043E\u0432\u0442\u043E\u0440\u0438\u0442\u044C \u0437\u0430\u0433\u0440\u0443\u0437\u043A\u0443</button></div>`);
  var root_37 = from_html(`<details class="svelte-1u3w06f"><summary class="svelte-1u3w06f">\u041F\u043E\u0441\u043C\u043E\u0442\u0440\u0435\u0442\u044C \u043F\u0440\u0435\u0434\u043B\u043E\u0436\u0435\u043D\u043D\u044B\u0435 \u0438\u0437\u043C\u0435\u043D\u0435\u043D\u0438\u044F</summary><pre class="svelte-1u3w06f"> </pre></details>`);
  var root_46 = from_html(`<details class="svelte-1u3w06f"><summary class="svelte-1u3w06f">\u041F\u043E\u0441\u043C\u043E\u0442\u0440\u0435\u0442\u044C \u043A\u043E\u043D\u0444\u0438\u0433\u0443\u0440\u0430\u0446\u0438\u044E \u0447\u0435\u0440\u043D\u043E\u0432\u0438\u043A\u0430</summary><pre class="svelte-1u3w06f"> </pre></details>`);
  var root_56 = from_html(`<div class="notice conflict svelte-1u3w06f" role="alert"><div><strong>\u0427\u0435\u0440\u043D\u043E\u0432\u0438\u043A \u043F\u043E\u043C\u043E\u0449\u043D\u0438\u043A\u0430 \u0442\u0440\u0435\u0431\u0443\u0435\u0442 \u0441\u0432\u0435\u0440\u043A\u0438</strong> <p class="svelte-1u3w06f"><!> \u041F\u0440\u0435\u0434\u043B\u043E\u0436\u0435\u043D\u0438\u0435 \u0441\u043E\u0445\u0440\u0430\u043D\u0435\u043D\u043E \u043E\u0442\u0434\u0435\u043B\u044C\u043D\u043E; \u0442\u0435\u043A\u0443\u0449\u0438\u0435 \u043F\u043E\u043B\u044F \u0444\u043E\u0440\u043C\u044B \u043D\u0435 \u0438\u0437\u043C\u0435\u043D\u0435\u043D\u044B.</p> <!></div> <div class="actions svelte-1u3w06f"><button type="button">\u041F\u0440\u0438\u043C\u0435\u043D\u0438\u0442\u044C \u0447\u0435\u0440\u043D\u043E\u0432\u0438\u043A</button> <button type="button">\u041E\u0442\u043A\u043B\u043E\u043D\u0438\u0442\u044C</button></div></div>`);
  var root_64 = from_html(`<div class="notice conflict svelte-1u3w06f" role="alert"><div><strong>\u041A\u043E\u043D\u0444\u043B\u0438\u043A\u0442 \u0441\u043E\u0445\u0440\u0430\u043D\u0435\u043D\u0438\u044F</strong><p class="svelte-1u3w06f"> </p></div> <button type="button">\u0417\u0430\u0433\u0440\u0443\u0437\u0438\u0442\u044C \u0430\u043A\u0442\u0443\u0430\u043B\u044C\u043D\u044B\u0435 \u043D\u0430\u0441\u0442\u0440\u043E\u0439\u043A\u0438</button></div>`);
  var root_74 = from_html(`<div class="notice error svelte-1u3w06f" role="alert"> </div>`);
  var root_84 = from_html(`<div class="dirty-bar svelte-1u3w06f"><span class="svelte-1u3w06f">\u0415\u0441\u0442\u044C \u043D\u0435\u0441\u043E\u0445\u0440\u0430\u043D\u0451\u043D\u043D\u044B\u0435 \u0438\u0437\u043C\u0435\u043D\u0435\u043D\u0438\u044F</span> <div class="actions svelte-1u3w06f"><button type="button">\u041E\u0442\u043C\u0435\u043D\u0438\u0442\u044C</button> <button type="button">\u041F\u0435\u0440\u0435\u0437\u0430\u0433\u0440\u0443\u0437\u0438\u0442\u044C</button> <button class="primary svelte-1u3w06f" type="button"> </button></div></div>`);
  var root_94 = from_html(`<small class="svelte-1u3w06f"> </small>`);
  var root_104 = from_html(`<p class="lock-note svelte-1u3w06f"> </p>`);
  var root_114 = from_html(`<div class="panel svelte-1u3w06f"><div class="section-title svelte-1u3w06f"><h3 class="svelte-1u3w06f">\u041E\u0431\u0449\u0438\u0435 \u043F\u0430\u0440\u0430\u043C\u0435\u0442\u0440\u044B</h3><p class="svelte-1u3w06f">\u041D\u0430\u0441\u0442\u0440\u043E\u0439\u043A\u0438 \u0440\u0435\u0433\u0438\u0441\u0442\u0440\u0430\u0446\u0438\u0438 \u0438 \u043E\u0433\u0440\u0430\u043D\u0438\u0447\u0435\u043D\u0438\u044F \u0432\u044B\u043F\u043E\u043B\u043D\u0435\u043D\u0438\u044F \u0437\u0430\u0434\u0430\u0447.</p></div> <label class="field svelte-1u3w06f"><span class="svelte-1u3w06f">\u041D\u0430\u0437\u0432\u0430\u043D\u0438\u0435 \u0441\u0435\u0440\u0432\u0438\u0441\u0430</span><input class="svelte-1u3w06f"/> <!></label> <label class="toggle svelte-1u3w06f"><input type="checkbox" class="svelte-1u3w06f"/><span class="svelte-1u3w06f"><strong>\u041E\u0442\u043A\u0440\u044B\u0442\u0430\u044F \u0440\u0435\u0433\u0438\u0441\u0442\u0440\u0430\u0446\u0438\u044F</strong><small class="svelte-1u3w06f">\u0420\u0430\u0437\u0440\u0435\u0448\u0438\u0442\u044C \u043D\u043E\u0432\u044B\u043C \u043F\u043E\u043B\u044C\u0437\u043E\u0432\u0430\u0442\u0435\u043B\u044F\u043C \u0441\u043E\u0437\u0434\u0430\u0432\u0430\u0442\u044C \u0430\u043A\u043A\u0430\u0443\u043D\u0442 \u0441\u0430\u043C\u043E\u0441\u0442\u043E\u044F\u0442\u0435\u043B\u044C\u043D\u043E.</small></span></label> <!> <div class="form-grid svelte-1u3w06f"><label class="field svelte-1u3w06f"><span class="svelte-1u3w06f">\u0414\u043B\u0438\u0442\u0435\u043B\u044C\u043D\u043E\u0441\u0442\u044C \u0441\u0435\u0441\u0441\u0438\u0438, \u043C\u0438\u043D\u0443\u0442</span><input type="number" min="15" max="43200" class="svelte-1u3w06f"/><!></label> <label class="field svelte-1u3w06f"><span class="svelte-1u3w06f">\u0422\u0430\u0439\u043C-\u0430\u0443\u0442 \u043F\u0440\u043E\u0432\u0435\u0440\u043A\u0438, \u0441\u0435\u043A\u0443\u043D\u0434</span><input type="number" min="1" max="30" step="0.5" class="svelte-1u3w06f"/><!></label> <label class="field svelte-1u3w06f"><span class="svelte-1u3w06f">\u041C\u0430\u043A\u0441\u0438\u043C\u0430\u043B\u044C\u043D\u044B\u0439 \u0440\u0430\u0437\u043C\u0435\u0440 \u043A\u043E\u0434\u0430, \u0441\u0438\u043C\u0432\u043E\u043B\u043E\u0432</span><input type="number" min="1000" max="500000" class="svelte-1u3w06f"/><!></label></div></div>`);
  var root_124 = from_html(`<small class="svelte-1u3w06f">\u0418\u0437\u043C\u0435\u043D\u0435\u043D\u0438\u0435 \u043F\u0443\u0442\u0438 \u0432\u0441\u0442\u0443\u043F\u0438\u0442 \u0432 \u0441\u0438\u043B\u0443 \u043F\u043E\u0441\u043B\u0435 \u0441\u043E\u0445\u0440\u0430\u043D\u0435\u043D\u0438\u044F.</small>`);
  var root_134 = from_html(`<p class="muted svelte-1u3w06f">\u0421\u043D\u0430\u0447\u0430\u043B\u0430 \u0441\u043E\u0445\u0440\u0430\u043D\u0438 \u0438\u0437\u043C\u0435\u043D\u0435\u043D\u0438\u044F, \u0447\u0442\u043E\u0431\u044B \u0441\u0438\u043D\u0445\u0440\u043E\u043D\u0438\u0437\u0430\u0446\u0438\u044F \u0438\u0441\u043F\u043E\u043B\u044C\u0437\u043E\u0432\u0430\u043B\u0430 \u043D\u043E\u0432\u044B\u0439 \u043F\u0443\u0442\u044C.</p>`);
  var root_142 = from_html(`<p class="inline-error svelte-1u3w06f" role="alert"> </p>`);
  var root_152 = from_html(`<div class="result-card svelte-1u3w06f" role="status"><strong>\u0421\u0438\u043D\u0445\u0440\u043E\u043D\u0438\u0437\u0430\u0446\u0438\u044F \u0437\u0430\u0432\u0435\u0440\u0448\u0435\u043D\u0430</strong><span class="svelte-1u3w06f"> </span></div>`);
  var root_162 = from_html(`<p class="muted svelte-1u3w06f">\u0417\u0430\u0433\u0440\u0443\u0436\u0430\u044E \u0436\u0443\u0440\u043D\u0430\u043B\u2026</p>`);
  var root_172 = from_html(`<p class="muted svelte-1u3w06f">\u0417\u0430\u043F\u0438\u0441\u0435\u0439 \u0441\u0438\u043D\u0445\u0440\u043E\u043D\u0438\u0437\u0430\u0446\u0438\u0438 \u043F\u043E\u043A\u0430 \u043D\u0435\u0442.</p>`);
  var root_182 = from_html(`<li class="svelte-1u3w06f"><strong> </strong><span class="svelte-1u3w06f"> </span><span class="svelte-1u3w06f"> </span><!></li>`);
  var root_192 = from_html(`<ul class="svelte-1u3w06f"></ul>`);
  var root_20 = from_html(`<div class="log-box svelte-1u3w06f"><!></div>`);
  var root_21 = from_html(`<div class="panel svelte-1u3w06f"><div class="section-title svelte-1u3w06f"><h3 class="svelte-1u3w06f">\u041A\u043E\u043D\u0442\u0435\u043D\u0442 \u0437\u0430\u0434\u0430\u0447</h3><p class="svelte-1u3w06f">\u041F\u0443\u0442\u044C \u043A \u0440\u0435\u043F\u043E\u0437\u0438\u0442\u043E\u0440\u0438\u044E \u0438 \u0440\u0443\u0447\u043D\u0430\u044F \u0441\u0438\u043D\u0445\u0440\u043E\u043D\u0438\u0437\u0430\u0446\u0438\u044F \u0435\u0433\u043E \u0441\u043E\u0434\u0435\u0440\u0436\u0438\u043C\u043E\u0433\u043E.</p></div> <label class="field svelte-1u3w06f"><span class="svelte-1u3w06f">\u041F\u0443\u0442\u044C \u043A \u043A\u043E\u043D\u0442\u0435\u043D\u0442\u0443</span><input class="svelte-1u3w06f"/> <!></label> <div class="subsection svelte-1u3w06f"><div class="svelte-1u3w06f"><h4 class="svelte-1u3w06f">\u0421\u0438\u043D\u0445\u0440\u043E\u043D\u0438\u0437\u0430\u0446\u0438\u044F</h4><p class="muted svelte-1u3w06f">\u0417\u0430\u043F\u0443\u0441\u043A\u0430\u0435\u0442\u0441\u044F \u043F\u043E \u0441\u043E\u0445\u0440\u0430\u043D\u0451\u043D\u043D\u043E\u043C\u0443 \u043F\u0443\u0442\u0438 \u0438 \u043D\u0435\u0434\u043E\u0441\u0442\u0443\u043F\u043D\u0430, \u043F\u043E\u043A\u0430 \u0444\u043E\u0440\u043C\u0430 \u0438\u0437\u043C\u0435\u043D\u0435\u043D\u0430.</p></div> <div class="actions svelte-1u3w06f"><button type="button"> </button> <button type="button"> </button></div></div> <!> <!> <!> <!></div>`);
  var root_222 = from_html(`<option></option>`);
  var root_232 = from_html(`<small class="inline-error svelte-1u3w06f"> </small>`);
  var root_242 = from_html(`<label class="field compact svelte-1u3w06f"><span class="svelte-1u3w06f">Temperature</span><input type="number" min="0" max="2" step="0.1" class="svelte-1u3w06f"/></label>`);
  var root_252 = from_html(`<p class="inline-error svelte-1u3w06f"> </p>`);
  var root_262 = from_html(`<label class="toggle danger-toggle svelte-1u3w06f"><input type="checkbox" class="svelte-1u3w06f"/><span class="svelte-1u3w06f"><strong class="svelte-1u3w06f">\u0423\u0434\u0430\u043B\u0438\u0442\u044C \u0441\u043E\u0445\u0440\u0430\u043D\u0451\u043D\u043D\u044B\u0439 \u043A\u043B\u044E\u0447</strong><small class="svelte-1u3w06f">\u0411\u0443\u0434\u0435\u0442 \u043F\u0440\u0438\u043C\u0435\u043D\u0435\u043D\u043E \u043F\u0440\u0438 \u0441\u043E\u0445\u0440\u0430\u043D\u0435\u043D\u0438\u0438; \u043F\u0443\u0441\u0442\u043E\u0435 \u043F\u043E\u043B\u0435 \u0441\u0430\u043C\u043E \u043F\u043E \u0441\u0435\u0431\u0435 \u043A\u043B\u044E\u0447 \u043D\u0435 \u043E\u0447\u0438\u0449\u0430\u0435\u0442.</small></span></label>`);
  var root_272 = from_html(`<span> </span>`);
  var root_28 = from_html(`<span class="inline-error svelte-1u3w06f" role="alert"> </span>`);
  var root_29 = from_html(`<div class="panel svelte-1u3w06f"><div class="section-title svelte-1u3w06f"><h3 class="svelte-1u3w06f">\u041F\u043E\u0434\u043A\u043B\u044E\u0447\u0435\u043D\u0438\u0435 AI</h3><p class="svelte-1u3w06f">\u041D\u0430\u0441\u0442\u0440\u043E\u0439 \u0441\u043E\u0432\u043C\u0435\u0441\u0442\u0438\u043C\u044B\u0439 API. \u041A\u043B\u044E\u0447 \u0445\u0440\u0430\u043D\u0438\u0442\u0441\u044F \u043E\u0442\u0434\u0435\u043B\u044C\u043D\u043E \u0438 \u043D\u0438\u043A\u043E\u0433\u0434\u0430 \u043D\u0435 \u0432\u043E\u0437\u0432\u0440\u0430\u0449\u0430\u0435\u0442\u0441\u044F \u0441\u0435\u0440\u0432\u0435\u0440\u043E\u043C.</p></div> <label class="toggle svelte-1u3w06f"><input type="checkbox" class="svelte-1u3w06f"/><span class="svelte-1u3w06f"><strong>\u0412\u043A\u043B\u044E\u0447\u0438\u0442\u044C AI-\u043F\u043E\u043C\u043E\u0449\u043D\u0438\u043A\u0430</strong><small class="svelte-1u3w06f">\u041F\u0440\u0438 \u043E\u0442\u043A\u043B\u044E\u0447\u0435\u043D\u0438\u0438 \u0437\u0430\u043F\u0440\u043E\u0441\u044B \u043A AI \u043D\u0435 \u0432\u044B\u043F\u043E\u043B\u043D\u044F\u044E\u0442\u0441\u044F.</small></span></label> <!> <div class="form-grid svelte-1u3w06f"><label class="field svelte-1u3w06f"><span class="svelte-1u3w06f">\u0421\u043E\u0432\u043C\u0435\u0441\u0442\u0438\u043C\u044B\u0439 API base URL</span><input type="url" placeholder="https://api.example.com/v1" class="svelte-1u3w06f"/><!></label> <label class="field svelte-1u3w06f"><span class="svelte-1u3w06f">\u041C\u043E\u0434\u0435\u043B\u044C</span><div class="input-action svelte-1u3w06f"><input list="ai-model-options" placeholder="\u041D\u0430\u043F\u0440\u0438\u043C\u0435\u0440, gpt-4.1-mini" class="svelte-1u3w06f"/><datalist id="ai-model-options"></datalist><button type="button"> </button></div><!><!></label> <label class="field svelte-1u3w06f"><span class="svelte-1u3w06f">\u0422\u0430\u0439\u043C-\u0430\u0443\u0442 AI, \u0441\u0435\u043A\u0443\u043D\u0434</span><input type="number" min="5" max="180" class="svelte-1u3w06f"/><!></label> <label class="field svelte-1u3w06f"><span class="svelte-1u3w06f">\u041B\u0438\u043C\u0438\u0442 \u0442\u043E\u043A\u0435\u043D\u043E\u0432 \u043E\u0442\u0432\u0435\u0442\u0430</span><input type="number" min="256" max="16384" class="svelte-1u3w06f"/><!></label></div> <label class="field svelte-1u3w06f"><span class="svelte-1u3w06f">\u0418\u043C\u044F \u043F\u0430\u0440\u0430\u043C\u0435\u0442\u0440\u0430 \u043B\u0438\u043C\u0438\u0442\u0430 \u0442\u043E\u043A\u0435\u043D\u043E\u0432</span><select class="svelte-1u3w06f"><option>max_tokens</option><option>max_completion_tokens</option></select><small class="svelte-1u3w06f">\u0412\u044B\u0431\u0435\u0440\u0438 \u0444\u043E\u0440\u043C\u0430\u0442, \u043A\u043E\u0442\u043E\u0440\u044B\u0439 \u043F\u0440\u0438\u043D\u0438\u043C\u0430\u0435\u0442 API-\u043F\u0440\u043E\u0432\u0430\u0439\u0434\u0435\u0440.</small></label> <!> <label class="toggle svelte-1u3w06f"><input type="checkbox" class="svelte-1u3w06f"/><span class="svelte-1u3w06f"><strong>\u0417\u0430\u0434\u0430\u0442\u044C temperature \u0432\u0440\u0443\u0447\u043D\u0443\u044E</strong><small class="svelte-1u3w06f">\u0415\u0441\u043B\u0438 \u0432\u044B\u043A\u043B\u044E\u0447\u0435\u043D\u043E, \u0438\u0441\u043F\u043E\u043B\u044C\u0437\u0443\u0435\u0442\u0441\u044F \u0437\u043D\u0430\u0447\u0435\u043D\u0438\u0435 \u043F\u0440\u043E\u0432\u0430\u0439\u0434\u0435\u0440\u0430 \u043F\u043E \u0443\u043C\u043E\u043B\u0447\u0430\u043D\u0438\u044E.</small></span></label> <!> <!> <label class="toggle svelte-1u3w06f"><input type="checkbox" class="svelte-1u3w06f"/><span class="svelte-1u3w06f"><strong>\u0420\u0430\u0437\u0440\u0435\u0448\u0438\u0442\u044C \u0438\u043D\u0441\u0442\u0440\u0443\u043C\u0435\u043D\u0442\u044B</strong><small class="svelte-1u3w06f">\u041F\u0435\u0440\u0435\u0434\u0430\u0432\u0430\u0442\u044C \u043F\u043E\u0434\u0434\u0435\u0440\u0436\u0438\u0432\u0430\u0435\u043C\u044B\u0435 tools/function calls AI-\u043F\u0440\u043E\u0432\u0430\u0439\u0434\u0435\u0440\u0443.</small></span></label> <!> <label class="field svelte-1u3w06f"><span class="svelte-1u3w06f">\u0421\u0438\u0441\u0442\u0435\u043C\u043D\u0430\u044F \u0438\u043D\u0441\u0442\u0440\u0443\u043A\u0446\u0438\u044F</span><textarea rows="7" class="svelte-1u3w06f"></textarea><!></label> <div class="key-panel svelte-1u3w06f"><div class="svelte-1u3w06f"><strong>API-\u043A\u043B\u044E\u0447</strong><p class="muted svelte-1u3w06f"> </p></div> <label class="field svelte-1u3w06f"><span class="svelte-1u3w06f"> </span><input type="password" autocomplete="new-password" class="svelte-1u3w06f"/></label> <!> <!> <!></div> <div class="actions footer-actions svelte-1u3w06f"><button class="primary svelte-1u3w06f" type="button"> </button> <!> <!></div></div>`);
  var root_30 = from_html(`<div class="svelte-1u3w06f"><small class="svelte-1u3w06f"> </small><strong class="svelte-1u3w06f"> </strong></div>`);
  var root_31 = from_html(`<button class="primary svelte-1u3w06f" type="button">\u0421\u043A\u0430\u0447\u0430\u0442\u044C .env.example</button>`);
  var root_322 = from_html(`<label class="field svelte-1u3w06f"><span class="svelte-1u3w06f">\u0422\u0435\u043A\u0441\u0442 \u0444\u0430\u0439\u043B\u0430 .env.example</span><textarea class="code svelte-1u3w06f" rows="14" spellcheck="false"></textarea></label>`);
  var root_332 = from_html(`<div class="panel svelte-1u3w06f"><div class="section-title svelte-1u3w06f"><h3 class="svelte-1u3w06f">\u0420\u0430\u0437\u0432\u0451\u0440\u0442\u044B\u0432\u0430\u043D\u0438\u0435</h3><p class="svelte-1u3w06f">\u041F\u0430\u0440\u0430\u043C\u0435\u0442\u0440\u044B \u0440\u0430\u0431\u043E\u0442\u0430\u044E\u0449\u0435\u0433\u043E \u043F\u0440\u043E\u0446\u0435\u0441\u0441\u0430 \u0434\u043E\u0441\u0442\u0443\u043F\u043D\u044B \u0442\u043E\u043B\u044C\u043A\u043E \u0434\u043B\u044F \u0447\u0442\u0435\u043D\u0438\u044F.</p></div> <div class="notice info svelte-1u3w06f"><div><strong>\u041F\u0440\u0438\u043C\u0435\u043D\u0435\u043D\u0438\u0435 \u0447\u0435\u0440\u0435\u0437 \u043E\u043A\u0440\u0443\u0436\u0435\u043D\u0438\u0435 \u0438 \u043F\u0435\u0440\u0435\u0437\u0430\u043F\u0443\u0441\u043A</strong><p class="svelte-1u3w06f">\u0418\u0437\u043C\u0435\u043D\u0435\u043D\u0438\u044F runtime-\u043F\u0430\u0440\u0430\u043C\u0435\u0442\u0440\u043E\u0432 \u0437\u0430\u0434\u0430\u044E\u0442\u0441\u044F \u043F\u0435\u0440\u0435\u043C\u0435\u043D\u043D\u044B\u043C\u0438 \u043E\u043A\u0440\u0443\u0436\u0435\u043D\u0438\u044F \u0438 \u0432\u0441\u0442\u0443\u043F\u0430\u044E\u0442 \u0432 \u0441\u0438\u043B\u0443 \u043F\u043E\u0441\u043B\u0435 \u043F\u0435\u0440\u0435\u0437\u0430\u043F\u0443\u0441\u043A\u0430 \u0441\u0435\u0440\u0432\u0438\u0441\u0430.</p></div></div> <div class="runtime-grid svelte-1u3w06f"></div> <div class="subsection deployment-export svelte-1u3w06f"><div class="svelte-1u3w06f"><h4 class="svelte-1u3w06f">\u0424\u0430\u0439\u043B \u043E\u043A\u0440\u0443\u0436\u0435\u043D\u0438\u044F</h4><p class="muted svelte-1u3w06f">\u0413\u0435\u043D\u0435\u0440\u0438\u0440\u0443\u0435\u0442\u0441\u044F \u0431\u0435\u0437 \u0441\u0435\u043A\u0440\u0435\u0442\u043E\u0432. \u041F\u0435\u0440\u0435\u0434 \u0441\u043A\u0430\u0447\u0438\u0432\u0430\u043D\u0438\u0435\u043C \u043C\u043E\u0436\u043D\u043E \u043E\u0442\u0440\u0435\u0434\u0430\u043A\u0442\u0438\u0440\u043E\u0432\u0430\u0442\u044C.</p></div> <div class="actions svelte-1u3w06f"><button type="button"> </button><!></div></div> <!> <!></div>`);
  var root_342 = from_html(`<fieldset class="settings-fields svelte-1u3w06f"><!> <!> <!> <nav class="tabs svelte-1u3w06f" aria-label="\u041A\u0430\u0442\u0435\u0433\u043E\u0440\u0438\u0438 \u043D\u0430\u0441\u0442\u0440\u043E\u0435\u043A"><button type="button">\u041E\u0431\u0449\u0438\u0435</button> <button type="button">\u041A\u043E\u043D\u0442\u0435\u043D\u0442</button> <button type="button">AI</button> <button type="button">\u0420\u0430\u0437\u0432\u0451\u0440\u0442\u044B\u0432\u0430\u043D\u0438\u0435</button></nav> <!></fieldset>`);
  var root_352 = from_html(`<div class="state-card svelte-1u3w06f">\u041D\u0430\u0441\u0442\u0440\u043E\u0439\u043A\u0438 \u0435\u0449\u0451 \u043D\u0435 \u0437\u0430\u0433\u0440\u0443\u0436\u0435\u043D\u044B.</div>`);
  var root_362 = from_html(`<section class="settings-page svelte-1u3w06f" aria-labelledby="settings-title"><div class="page-heading svelte-1u3w06f"><div><h2 id="settings-title" class="svelte-1u3w06f">\u041D\u0430\u0441\u0442\u0440\u043E\u0439\u043A\u0438 \u0441\u0435\u0440\u0432\u0438\u0441\u0430</h2> <p class="muted svelte-1u3w06f">\u041E\u0431\u0449\u0438\u0435 \u043F\u0430\u0440\u0430\u043C\u0435\u0442\u0440\u044B, \u043A\u043E\u043D\u0442\u0435\u043D\u0442, AI \u0438 \u043A\u043E\u043D\u0444\u0438\u0433\u0443\u0440\u0430\u0446\u0438\u044F \u0440\u0430\u0437\u0432\u0451\u0440\u0442\u044B\u0432\u0430\u043D\u0438\u044F.</p></div> <!></div> <!></section>`);
  var $$css7 = {
    hash: "svelte-1u3w06f",
    code: ".settings-fields.svelte-1u3w06f {border:0;margin:0;padding:0;min-width:0;display:grid;gap:16px;}.settings-page.svelte-1u3w06f {display:grid;gap:16px;min-width:0;}.page-heading.svelte-1u3w06f {display:flex;align-items:flex-start;justify-content:space-between;gap:12px;}h2.svelte-1u3w06f, h3.svelte-1u3w06f, h4.svelte-1u3w06f, p.svelte-1u3w06f {margin:0;}h2.svelte-1u3w06f {font-size:1.1rem;}h3.svelte-1u3w06f {font-size:0.95rem;}h4.svelte-1u3w06f {font-size:0.82rem;}.muted.svelte-1u3w06f, .section-title.svelte-1u3w06f p:where(.svelte-1u3w06f) {color:#858585;font-size:0.76rem;}.page-heading.svelte-1u3w06f .muted:where(.svelte-1u3w06f) {margin-top:4px;}.revision.svelte-1u3w06f {color:#858585;font-size:0.72rem;white-space:nowrap;}.tabs.svelte-1u3w06f {display:flex;gap:4px;border-bottom:1px solid #3c3c3c;overflow-x:auto;}.tabs.svelte-1u3w06f button:where(.svelte-1u3w06f) {padding:8px 12px;background:transparent;color:#858585;border:0;border-bottom:2px solid transparent;white-space:nowrap;}.tabs.svelte-1u3w06f button.active:where(.svelte-1u3w06f) {color:#d4d4d4;border-bottom-color:#007acc;}.panel.svelte-1u3w06f {display:grid;gap:16px;min-width:0;}.section-title.svelte-1u3w06f {display:grid;gap:3px;padding-bottom:4px;}.form-grid.svelte-1u3w06f {display:grid;grid-template-columns:repeat(2, minmax(0, 1fr));gap:14px;}.field.svelte-1u3w06f {display:grid;gap:5px;min-width:0;}.field.svelte-1u3w06f > span:where(.svelte-1u3w06f) {font-size:0.77rem;font-weight:600;}.field.svelte-1u3w06f small:where(.svelte-1u3w06f), .toggle.svelte-1u3w06f small:where(.svelte-1u3w06f) {color:#858585;font-size:0.7rem;line-height:1.4;}.field.svelte-1u3w06f input:where(.svelte-1u3w06f), .field.svelte-1u3w06f select:where(.svelte-1u3w06f), .field.svelte-1u3w06f textarea:where(.svelte-1u3w06f) {width:100%;box-sizing:border-box;min-width:0;}.field.svelte-1u3w06f textarea:where(.svelte-1u3w06f) {resize:vertical;}.field.svelte-1u3w06f input:where(.svelte-1u3w06f):disabled, .field.svelte-1u3w06f select:where(.svelte-1u3w06f):disabled, .field.svelte-1u3w06f textarea:where(.svelte-1u3w06f):disabled {opacity:0.62;cursor:not-allowed;}.compact.svelte-1u3w06f {max-width:260px;}.toggle.svelte-1u3w06f {display:flex;align-items:flex-start;gap:9px;}.toggle.svelte-1u3w06f input:where(.svelte-1u3w06f) {margin-top:3px;}.toggle.svelte-1u3w06f > span:where(.svelte-1u3w06f) {display:grid;gap:2px;}.lock-note.svelte-1u3w06f {color:#d0a85c;font-size:0.7rem;margin-top:-10px;}.notice.svelte-1u3w06f, .dirty-bar.svelte-1u3w06f, .result-card.svelte-1u3w06f, .state-card.svelte-1u3w06f {padding:12px 14px;border:1px solid #3c3c3c;border-radius:6px;background:#252526;}.notice.svelte-1u3w06f {display:flex;justify-content:space-between;align-items:flex-start;gap:12px;}.notice.svelte-1u3w06f p:where(.svelte-1u3w06f) {margin-top:3px;color:#a0a0a0;font-size:0.75rem;}.notice.conflict.svelte-1u3w06f {border-color:#9a6b2f;}.notice.info.svelte-1u3w06f {border-color:#36556a;}.notice.error.svelte-1u3w06f, .state-card.error.svelte-1u3w06f {color:#f87171;border-color:#704040;}.notice.svelte-1u3w06f details:where(.svelte-1u3w06f) {margin-top:8px;}.notice.svelte-1u3w06f summary:where(.svelte-1u3w06f) {font-size:0.72rem;cursor:pointer;}.notice.svelte-1u3w06f pre:where(.svelte-1u3w06f) {max-height:240px;overflow:auto;white-space:pre-wrap;font-size:0.7rem;color:#c6c6c6;}.actions.svelte-1u3w06f {display:flex;align-items:center;flex-wrap:wrap;gap:8px;}.dirty-bar.svelte-1u3w06f {display:flex;align-items:center;justify-content:space-between;gap:10px;border-color:#886828;}.dirty-bar.svelte-1u3w06f > span:where(.svelte-1u3w06f) {font-size:0.78rem;color:#e4c477;}.primary.svelte-1u3w06f {border-color:#007acc !important;color:#fff !important;background:#0e639c !important;}.subsection.svelte-1u3w06f {display:flex;justify-content:space-between;align-items:center;gap:14px;padding-top:12px;border-top:1px solid #333;}.subsection.svelte-1u3w06f > div:where(.svelte-1u3w06f):first-child {display:grid;gap:3px;}.result-card.svelte-1u3w06f {display:flex;flex-wrap:wrap;gap:8px 16px;font-size:0.76rem;}.result-card.svelte-1u3w06f span:where(.svelte-1u3w06f) {color:#a0a0a0;}.log-box.svelte-1u3w06f {border:1px solid #333;border-radius:5px;padding:10px;}.log-box.svelte-1u3w06f ul:where(.svelte-1u3w06f) {list-style:none;padding:0;margin:0;display:grid;gap:8px;}.log-box.svelte-1u3w06f li:where(.svelte-1u3w06f) {display:grid;grid-template-columns:auto 1fr auto;gap:8px;align-items:baseline;font-size:0.72rem;}.log-box.svelte-1u3w06f li:where(.svelte-1u3w06f) span:where(.svelte-1u3w06f) {color:#858585;}.log-box.svelte-1u3w06f li:where(.svelte-1u3w06f) small:where(.svelte-1u3w06f) {grid-column:1 / -1;color:#f87171;}.input-action.svelte-1u3w06f {display:flex;gap:6px;}.input-action.svelte-1u3w06f input:where(.svelte-1u3w06f) {flex:1;}.key-panel.svelte-1u3w06f {display:grid;gap:10px;padding:14px;border:1px solid #3c3c3c;border-radius:5px;}.key-panel.svelte-1u3w06f > div:where(.svelte-1u3w06f):first-child {display:grid;gap:3px;}.danger-toggle.svelte-1u3w06f strong:where(.svelte-1u3w06f) {color:#f0a0a0;}.footer-actions.svelte-1u3w06f {border-top:1px solid #333;padding-top:14px;}.test-status.svelte-1u3w06f {font-size:0.75rem;}.success.svelte-1u3w06f {color:#75c687;}.failure.svelte-1u3w06f, .inline-error.svelte-1u3w06f {color:#f87171;}.runtime-grid.svelte-1u3w06f {display:grid;grid-template-columns:repeat(3, minmax(0, 1fr));gap:8px;}.runtime-grid.svelte-1u3w06f > div:where(.svelte-1u3w06f) {min-width:0;padding:9px 10px;display:grid;gap:4px;border:1px solid #333;border-radius:4px;}.runtime-grid.svelte-1u3w06f small:where(.svelte-1u3w06f) {color:#858585;font-size:0.68rem;}.runtime-grid.svelte-1u3w06f strong:where(.svelte-1u3w06f) {overflow-wrap:anywhere;font-size:0.75rem;font-weight:500;}.deployment-export.svelte-1u3w06f {margin-top:4px;}.field.svelte-1u3w06f textarea.code:where(.svelte-1u3w06f) {font-family:'JetBrains Mono', 'Cascadia Code', 'Fira Code', 'Consolas', monospace;font-size:0.75rem;}.state-card.svelte-1u3w06f {color:#a0a0a0;text-align:center;}.state-card.svelte-1u3w06f p:where(.svelte-1u3w06f) {margin-bottom:10px;}\r\n\r\n	@media (max-width: 700px) {.form-grid.svelte-1u3w06f, .runtime-grid.svelte-1u3w06f {grid-template-columns:1fr;}.page-heading.svelte-1u3w06f, .dirty-bar.svelte-1u3w06f, .subsection.svelte-1u3w06f, .notice.svelte-1u3w06f {align-items:stretch;flex-direction:column;}.revision.svelte-1u3w06f {white-space:normal;}.log-box.svelte-1u3w06f li:where(.svelte-1u3w06f) {grid-template-columns:1fr;}\r\n	}"
  };
  function Settings($$anchor, $$props) {
    push($$props, true);
    append_styles($$anchor, $$css7);
    let draft = prop($$props, "draft", 3, null);
    let activeTab = state("general");
    let snapshot2 = state(null);
    let config = state(null);
    let loading = state(true);
    let loadError = state("");
    let saving = state(false);
    let actionError = state("");
    let apiKey = state("");
    let clearApiKey = state(false);
    let revisionConflict = state(false);
    let pendingProposal = state(null);
    let appliedDraft = null;
    let models = state(proxy([]));
    let modelsLoading = state(false);
    let modelsError = state("");
    let aiTest = state(null);
    let aiTestError = state("");
    let aiTesting = state(false);
    let syncBusy = state(false);
    let syncError = state("");
    let syncResult = state(null);
    let logsOpen = state(false);
    let logsLoading = state(false);
    let logsError = state("");
    let logs = state(null);
    let deploymentLoading = state(false);
    let deploymentError = state("");
    let deploymentText = state("");
    let deploymentReady = state(false);
    let dirty = user_derived(() => Boolean(get2(snapshot2) && get2(config) && (JSON.stringify(get2(config)) !== JSON.stringify(get2(snapshot2).config) || get2(apiKey).length > 0 || get2(clearApiKey))));
    function copyConfig(source2) {
      return { ...source2 };
    }
    function setBaseline(data) {
      set(snapshot2, data, true);
      set(config, copyConfig(data.config), true);
      set(apiKey, "");
      set(clearApiKey, false);
      set(revisionConflict, false);
      set(actionError, "");
      set(aiTest, null);
      set(aiTestError, "");
    }
    async function loadSettings(discardDirty = false) {
      if (get2(dirty) && !discardDirty && !window.confirm("\u0415\u0441\u0442\u044C \u043D\u0435\u0441\u043E\u0445\u0440\u0430\u043D\u0451\u043D\u043D\u044B\u0435 \u0438\u0437\u043C\u0435\u043D\u0435\u043D\u0438\u044F. \u041F\u0435\u0440\u0435\u0437\u0430\u0433\u0440\u0443\u0437\u0438\u0442\u044C \u043D\u0430\u0441\u0442\u0440\u043E\u0439\u043A\u0438 \u0438 \u043F\u043E\u0442\u0435\u0440\u044F\u0442\u044C \u0438\u0445?")) return;
      set(loading, true);
      set(loadError, "");
      try {
        const data = await getSettings();
        setBaseline(data);
        set(pendingProposal, null);
        appliedDraft = null;
      } catch (error) {
        set(loadError, error.message || "\u041D\u0435 \u0443\u0434\u0430\u043B\u043E\u0441\u044C \u0437\u0430\u0433\u0440\u0443\u0437\u0438\u0442\u044C \u043D\u0430\u0441\u0442\u0440\u043E\u0439\u043A\u0438.", true);
      } finally {
        set(loading, false);
      }
    }
    function isRevisionConflict(error) {
      const e = error;
      return e?.status === 409 || /\b409\b|revision|revision conflict|верси.{0,20}(измен|конфликт)|конфликт/i.test(e?.message || "");
    }
    function isLocked(field) {
      return Boolean(get2(snapshot2)?.locked_fields?.[field]);
    }
    function lockMessage(field) {
      const variable = get2(snapshot2)?.locked_fields?.[field];
      return variable ? `\u0417\u0430\u0434\u0430\u043D\u043E \u043F\u0435\u0440\u0435\u043C\u0435\u043D\u043D\u043E\u0439 \u043E\u043A\u0440\u0443\u0436\u0435\u043D\u0438\u044F ${variable}; \u0438\u0437\u043C\u0435\u043D\u0438\u0442\u044C \u0437\u0434\u0435\u0441\u044C \u043D\u0435\u043B\u044C\u0437\u044F.` : "";
    }
    function handleIncomingDraft(incoming) {
      if (!incoming || incoming === appliedDraft || !get2(snapshot2) || !get2(config)) return;
      if (get2(dirty)) {
        set(pendingProposal, incoming, true);
        return;
      }
      if (incoming.expected_revision !== get2(snapshot2).revision) {
        set(pendingProposal, incoming, true);
        return;
      }
      set(config, copyConfig(incoming.config), true);
      set(pendingProposal, null);
      appliedDraft = incoming;
    }
    user_effect(() => {
      handleIncomingDraft(draft());
    });
    user_effect(() => {
      $$props.onDirtyChange?.(get2(dirty));
    });
    function beforeUnload(event2) {
      if (!get2(dirty)) return;
      event2.preventDefault();
      event2.returnValue = "";
    }
    onMount(() => {
      void loadSettings(true);
      window.addEventListener("beforeunload", beforeUnload);
      return () => window.removeEventListener("beforeunload", beforeUnload);
    });
    async function save2(andTest = false) {
      if (!get2(snapshot2) || !get2(config) || get2(saving)) return;
      set(saving, true);
      set(actionError, "");
      if (andTest) {
        set(aiTest, null);
        set(aiTestError, "");
      }
      try {
        const saved = await saveSettings(
          {
            expected_revision: get2(snapshot2).revision,
            config: copyConfig(get2(config))
          },
          get2(apiKey) || void 0,
          get2(clearApiKey)
        );
        setBaseline(saved);
        set(pendingProposal, null);
        appliedDraft = null;
        $$props.onSaved?.(saved);
        if (andTest) {
          set(aiTesting, true);
          try {
            set(aiTest, await testAI(), true);
          } catch (error) {
            set(aiTestError, error.message || "\u041F\u0440\u043E\u0432\u0435\u0440\u043A\u0430 \u043F\u043E\u0434\u043A\u043B\u044E\u0447\u0435\u043D\u0438\u044F \u0437\u0430\u0432\u0435\u0440\u0448\u0438\u043B\u0430\u0441\u044C \u043E\u0448\u0438\u0431\u043A\u043E\u0439.", true);
          } finally {
            set(aiTesting, false);
          }
        }
      } catch (error) {
        if (isRevisionConflict(error)) {
          set(revisionConflict, true);
          set(actionError, "\u041D\u0430\u0441\u0442\u0440\u043E\u0439\u043A\u0438 \u043D\u0430 \u0441\u0435\u0440\u0432\u0435\u0440\u0435 \u0443\u0436\u0435 \u0438\u0437\u043C\u0435\u043D\u0438\u043B\u0438\u0441\u044C. \u0422\u0432\u043E\u0438 \u043F\u043E\u043B\u044F \u0441\u043E\u0445\u0440\u0430\u043D\u0435\u043D\u044B \u0432 \u0444\u043E\u0440\u043C\u0435; \u043E\u0431\u043D\u043E\u0432\u0438 \u0434\u0430\u043D\u043D\u044B\u0435 \u0438 \u043F\u0435\u0440\u0435\u043D\u0435\u0441\u0438 \u0438\u0437\u043C\u0435\u043D\u0435\u043D\u0438\u044F \u0432\u0440\u0443\u0447\u043D\u0443\u044E.");
        } else {
          set(actionError, error.message || "\u041D\u0435 \u0443\u0434\u0430\u043B\u043E\u0441\u044C \u0441\u043E\u0445\u0440\u0430\u043D\u0438\u0442\u044C \u043D\u0430\u0441\u0442\u0440\u043E\u0439\u043A\u0438.", true);
        }
      } finally {
        set(saving, false);
      }
    }
    function revert() {
      if (!get2(snapshot2) || !get2(dirty)) return;
      if (!window.confirm("\u041E\u0442\u043C\u0435\u043D\u0438\u0442\u044C \u0432\u0441\u0435 \u043D\u0435\u0441\u043E\u0445\u0440\u0430\u043D\u0451\u043D\u043D\u044B\u0435 \u0438\u0437\u043C\u0435\u043D\u0435\u043D\u0438\u044F?")) return;
      set(config, copyConfig(get2(snapshot2).config), true);
      set(apiKey, "");
      set(clearApiKey, false);
      set(actionError, "");
      set(revisionConflict, false);
      set(pendingProposal, null);
    }
    function acceptProposal() {
      if (!get2(pendingProposal) || !get2(snapshot2) || !get2(config)) return;
      if (get2(pendingProposal).expected_revision !== get2(snapshot2).revision) {
        set(revisionConflict, true);
        return;
      }
      if (get2(dirty) && !window.confirm("\u0417\u0430\u043C\u0435\u043D\u0438\u0442\u044C \u0442\u0435\u043A\u0443\u0449\u0438\u0435 \u043D\u0435\u0441\u043E\u0445\u0440\u0430\u043D\u0451\u043D\u043D\u044B\u0435 \u043F\u043E\u043B\u044F \u0447\u0435\u0440\u043D\u043E\u0432\u0438\u043A\u043E\u043C \u043F\u043E\u043C\u043E\u0449\u043D\u0438\u043A\u0430?")) return;
      set(config, copyConfig(get2(pendingProposal).config), true);
      appliedDraft = get2(pendingProposal);
      set(pendingProposal, null);
      set(revisionConflict, false);
    }
    async function loadModels() {
      set(modelsLoading, true);
      set(modelsError, "");
      try {
        set(models, await listModels(), true);
      } catch (error) {
        set(modelsError, error.message || "\u041D\u0435 \u0443\u0434\u0430\u043B\u043E\u0441\u044C \u0437\u0430\u0433\u0440\u0443\u0437\u0438\u0442\u044C \u043C\u043E\u0434\u0435\u043B\u0438.", true);
      } finally {
        set(modelsLoading, false);
      }
    }
    async function showLogs() {
      set(logsOpen, !get2(logsOpen));
      if (!get2(logsOpen) || get2(logs)) return;
      set(logsLoading, true);
      set(logsError, "");
      try {
        set(logs, await syncLog(), true);
      } catch (error) {
        set(logsError, error.message || "\u041D\u0435 \u0443\u0434\u0430\u043B\u043E\u0441\u044C \u0437\u0430\u0433\u0440\u0443\u0437\u0438\u0442\u044C \u0436\u0443\u0440\u043D\u0430\u043B \u0441\u0438\u043D\u0445\u0440\u043E\u043D\u0438\u0437\u0430\u0446\u0438\u0438.", true);
      } finally {
        set(logsLoading, false);
      }
    }
    async function runSync() {
      if (!get2(snapshot2) || get2(dirty) || get2(syncBusy)) return;
      set(syncBusy, true);
      set(syncError, "");
      set(syncResult, null);
      try {
        set(syncResult, await syncContent(get2(snapshot2).config.content_path), true);
        set(logs, null);
      } catch (error) {
        set(syncError, error.message || "\u041D\u0435 \u0443\u0434\u0430\u043B\u043E\u0441\u044C \u0441\u0438\u043D\u0445\u0440\u043E\u043D\u0438\u0437\u0438\u0440\u043E\u0432\u0430\u0442\u044C \u043A\u043E\u043D\u0442\u0435\u043D\u0442.", true);
      } finally {
        set(syncBusy, false);
      }
    }
    function redactSecrets(text2) {
      return text2.replace(/^([A-Z0-9_]*(?:API[_-]?KEY|TOKEN|SECRET|PASSWORD)[A-Z0-9_]*)\s*=.*$/gim, "$1=");
    }
    async function prepareDeployment() {
      set(deploymentLoading, true);
      set(deploymentError, "");
      try {
        set(deploymentText, redactSecrets(await exportDeployment()), true);
        set(deploymentReady, true);
      } catch (error) {
        set(deploymentError, error.message || "\u041D\u0435 \u0443\u0434\u0430\u043B\u043E\u0441\u044C \u043F\u043E\u0434\u0433\u043E\u0442\u043E\u0432\u0438\u0442\u044C \u0444\u0430\u0439\u043B \u043E\u043A\u0440\u0443\u0436\u0435\u043D\u0438\u044F.", true);
      } finally {
        set(deploymentLoading, false);
      }
    }
    function downloadDeployment() {
      const blob = new Blob([get2(deploymentText)], { type: "text/plain;charset=utf-8" });
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = ".env.example";
      anchor.click();
      URL.revokeObjectURL(url);
    }
    function setTemperatureEnabled(event2) {
      if (!get2(config)) return;
      const enabled = event2.currentTarget.checked;
      get2(config).ai_temperature = enabled ? 0.7 : null;
    }
    user_effect(() => {
      $$props.onBusyChange?.(get2(saving) || get2(syncBusy) || get2(aiTesting));
    });
    onDestroy(() => {
      $$props.onBusyChange?.(false);
    });
    var section = root_362();
    var div = child(section);
    var node = sibling(child(div), 2);
    {
      var consequent = ($$anchor2) => {
        var span = root7();
        var text_1 = only_child(span);
        template_effect(() => set_text(text_1, `\u0412\u0435\u0440\u0441\u0438\u044F \u043D\u0430\u0441\u0442\u0440\u043E\u0435\u043A \xB7 ${get2(snapshot2).revision ?? ""}`));
        append($$anchor2, span);
      };
      if_block(node, ($$render) => {
        if (get2(snapshot2)) $$render(consequent);
      });
    }
    reset(div);
    var node_1 = sibling(div, 2);
    {
      var consequent_1 = ($$anchor2) => {
        var div_1 = root_110();
        append($$anchor2, div_1);
      };
      var consequent_2 = ($$anchor2) => {
        var div_2 = root_27();
        var p = child(div_2);
        var text_2 = only_child(p, true);
        var button = sibling(p, 2);
        reset(div_2);
        template_effect(() => set_text(text_2, get2(loadError)));
        delegated("click", button, () => void loadSettings(true));
        append($$anchor2, div_2);
      };
      var consequent_46 = ($$anchor2) => {
        var fieldset = root_342();
        var node_2 = child(fieldset);
        {
          var consequent_5 = ($$anchor3) => {
            var div_3 = root_56();
            var div_4 = child(div_3);
            var p_1 = sibling(child(div_4), 2);
            var node_3 = child(p_1);
            {
              var consequent_3 = ($$anchor4) => {
                var text_3 = text();
                template_effect(() => set_text(text_3, `\u041E\u043D \u0441\u043E\u0437\u0434\u0430\u043D \u0434\u043B\u044F \u0432\u0435\u0440\u0441\u0438\u0438 ${get2(pendingProposal).expected_revision ?? ""}, \u0430 \u0437\u0430\u0433\u0440\u0443\u0436\u0435\u043D\u0430 \u0432\u0435\u0440\u0441\u0438\u044F ${get2(snapshot2).revision ?? ""}.`));
                append($$anchor4, text_3);
              };
              var alternate = ($$anchor4) => {
                var text_4 = text("\u0412 \u0444\u043E\u0440\u043C\u0435 \u0443\u0436\u0435 \u0435\u0441\u0442\u044C \u043D\u0435\u0441\u043E\u0445\u0440\u0430\u043D\u0451\u043D\u043D\u044B\u0435 \u0438\u0437\u043C\u0435\u043D\u0435\u043D\u0438\u044F.");
                append($$anchor4, text_4);
              };
              if_block(node_3, ($$render) => {
                if (get2(pendingProposal).expected_revision !== get2(snapshot2).revision) $$render(consequent_3);
                else $$render(alternate, -1);
              });
            }
            next();
            reset(p_1);
            var node_4 = sibling(p_1, 2);
            {
              var consequent_4 = ($$anchor4) => {
                var details = root_37();
                var pre = sibling(child(details));
                var text_5 = only_child(pre, true);
                reset(details);
                template_effect(($0) => set_text(text_5, $0), [
                  () => JSON.stringify(get2(pendingProposal).changes, null, 2)
                ]);
                append($$anchor4, details);
              };
              var alternate_1 = ($$anchor4) => {
                var details_1 = root_46();
                var pre_1 = sibling(child(details_1));
                var text_6 = only_child(pre_1, true);
                reset(details_1);
                template_effect(($0) => set_text(text_6, $0), [() => JSON.stringify(get2(pendingProposal).config, null, 2)]);
                append($$anchor4, details_1);
              };
              if_block(node_4, ($$render) => {
                if (get2(pendingProposal).changes) $$render(consequent_4);
                else $$render(alternate_1, -1);
              });
            }
            reset(div_4);
            var div_5 = sibling(div_4, 2);
            var button_1 = child(div_5);
            var button_2 = sibling(button_1, 2);
            reset(div_5);
            reset(div_3);
            template_effect(() => button_1.disabled = get2(pendingProposal).expected_revision !== get2(snapshot2).revision);
            delegated("click", button_1, acceptProposal);
            delegated("click", button_2, () => {
              set(pendingProposal, null);
            });
            append($$anchor3, div_3);
          };
          if_block(node_2, ($$render) => {
            if (get2(pendingProposal)) $$render(consequent_5);
          });
        }
        var node_5 = sibling(node_2, 2);
        {
          var consequent_6 = ($$anchor3) => {
            var div_6 = root_64();
            var div_7 = child(div_6);
            var p_2 = sibling(child(div_7));
            var text_7 = only_child(p_2, true);
            reset(div_7);
            var button_3 = sibling(div_7, 2);
            reset(div_6);
            template_effect(() => set_text(text_7, get2(actionError) || "\u0421\u0435\u0440\u0432\u0435\u0440 \u0441\u043E\u043E\u0431\u0449\u0438\u043B, \u0447\u0442\u043E revision \u0438\u0437\u043C\u0435\u043D\u0438\u043B\u0441\u044F. \u041B\u043E\u043A\u0430\u043B\u044C\u043D\u044B\u0435 \u043F\u043E\u043B\u044F \u0441\u043E\u0445\u0440\u0430\u043D\u0435\u043D\u044B."));
            delegated("click", button_3, () => void loadSettings());
            append($$anchor3, div_6);
          };
          var consequent_7 = ($$anchor3) => {
            var div_8 = root_74();
            var text_8 = only_child(div_8, true);
            template_effect(() => set_text(text_8, get2(actionError)));
            append($$anchor3, div_8);
          };
          if_block(node_5, ($$render) => {
            if (get2(revisionConflict)) $$render(consequent_6);
            else if (get2(actionError)) $$render(consequent_7, 1);
          });
        }
        var node_6 = sibling(node_5, 2);
        {
          var consequent_8 = ($$anchor3) => {
            var div_9 = root_84();
            var div_10 = sibling(child(div_9), 2);
            var button_4 = child(div_10);
            var button_5 = sibling(button_4, 2);
            var button_6 = sibling(button_5, 2);
            var text_9 = only_child(button_6, true);
            reset(div_10);
            reset(div_9);
            template_effect(() => {
              button_5.disabled = get2(loading);
              button_6.disabled = get2(saving);
              set_text(text_9, get2(saving) ? "\u0421\u043E\u0445\u0440\u0430\u043D\u044F\u044E\u2026" : "\u0421\u043E\u0445\u0440\u0430\u043D\u0438\u0442\u044C");
            });
            delegated("click", button_4, revert);
            delegated("click", button_5, () => void loadSettings());
            delegated("click", button_6, () => void save2());
            append($$anchor3, div_9);
          };
          if_block(node_6, ($$render) => {
            if (get2(dirty)) $$render(consequent_8);
          });
        }
        var nav = sibling(node_6, 2);
        var button_7 = child(nav);
        let classes;
        var button_8 = sibling(button_7, 2);
        let classes_1;
        var button_9 = sibling(button_8, 2);
        let classes_2;
        var button_10 = sibling(button_9, 2);
        let classes_3;
        reset(nav);
        var node_7 = sibling(nav, 2);
        {
          var consequent_14 = ($$anchor3) => {
            var div_11 = root_114();
            var label_1 = sibling(child(div_11), 2);
            var input = sibling(child(label_1));
            remove_input_defaults(input);
            var node_8 = sibling(input, 2);
            {
              var consequent_9 = ($$anchor4) => {
                var small = root_94();
                var text_10 = only_child(small, true);
                template_effect(($0) => set_text(text_10, $0), [() => lockMessage("service_name")]);
                append($$anchor4, small);
              };
              var d = user_derived(() => isLocked("service_name"));
              if_block(node_8, ($$render) => {
                if (get2(d)) $$render(consequent_9);
              });
            }
            reset(label_1);
            var label_2 = sibling(label_1, 2);
            var input_1 = child(label_2);
            remove_input_defaults(input_1);
            next();
            reset(label_2);
            var node_9 = sibling(label_2, 2);
            {
              var consequent_10 = ($$anchor4) => {
                var p_3 = root_104();
                var text_11 = only_child(p_3, true);
                template_effect(($0) => set_text(text_11, $0), [() => lockMessage("registration_enabled")]);
                append($$anchor4, p_3);
              };
              var d_1 = user_derived(() => isLocked("registration_enabled"));
              if_block(node_9, ($$render) => {
                if (get2(d_1)) $$render(consequent_10);
              });
            }
            var div_12 = sibling(node_9, 2);
            var label_3 = child(div_12);
            var input_2 = sibling(child(label_3));
            remove_input_defaults(input_2);
            var node_10 = sibling(input_2);
            {
              var consequent_11 = ($$anchor4) => {
                var small_1 = root_94();
                var text_12 = only_child(small_1, true);
                template_effect(($0) => set_text(text_12, $0), [() => lockMessage("session_minutes")]);
                append($$anchor4, small_1);
              };
              var d_2 = user_derived(() => isLocked("session_minutes"));
              if_block(node_10, ($$render) => {
                if (get2(d_2)) $$render(consequent_11);
              });
            }
            reset(label_3);
            var label_4 = sibling(label_3, 2);
            var input_3 = sibling(child(label_4));
            remove_input_defaults(input_3);
            var node_11 = sibling(input_3);
            {
              var consequent_12 = ($$anchor4) => {
                var small_2 = root_94();
                var text_13 = only_child(small_2, true);
                template_effect(($0) => set_text(text_13, $0), [() => lockMessage("check_timeout_seconds")]);
                append($$anchor4, small_2);
              };
              var d_3 = user_derived(() => isLocked("check_timeout_seconds"));
              if_block(node_11, ($$render) => {
                if (get2(d_3)) $$render(consequent_12);
              });
            }
            reset(label_4);
            var label_5 = sibling(label_4, 2);
            var input_4 = sibling(child(label_5));
            remove_input_defaults(input_4);
            var node_12 = sibling(input_4);
            {
              var consequent_13 = ($$anchor4) => {
                var small_3 = root_94();
                var text_14 = only_child(small_3, true);
                template_effect(($0) => set_text(text_14, $0), [() => lockMessage("max_code_chars")]);
                append($$anchor4, small_3);
              };
              var d_4 = user_derived(() => isLocked("max_code_chars"));
              if_block(node_12, ($$render) => {
                if (get2(d_4)) $$render(consequent_13);
              });
            }
            reset(label_5);
            reset(div_12);
            reset(div_11);
            template_effect(
              ($0, $1, $2, $3, $4) => {
                input.disabled = $0;
                input_1.disabled = $1;
                input_2.disabled = $2;
                input_3.disabled = $3;
                input_4.disabled = $4;
              },
              [
                () => isLocked("service_name"),
                () => isLocked("registration_enabled"),
                () => isLocked("session_minutes"),
                () => isLocked("check_timeout_seconds"),
                () => isLocked("max_code_chars")
              ]
            );
            bind_value(input, () => get2(config).service_name, ($$value) => get2(config).service_name = $$value);
            bind_checked(input_1, () => get2(config).registration_enabled, ($$value) => get2(config).registration_enabled = $$value);
            bind_value(input_2, () => get2(config).session_minutes, ($$value) => get2(config).session_minutes = $$value);
            bind_value(input_3, () => get2(config).check_timeout_seconds, ($$value) => get2(config).check_timeout_seconds = $$value);
            bind_value(input_4, () => get2(config).max_code_chars, ($$value) => get2(config).max_code_chars = $$value);
            append($$anchor3, div_11);
          };
          var consequent_25 = ($$anchor3) => {
            var div_13 = root_21();
            var label_6 = sibling(child(div_13), 2);
            var input_5 = sibling(child(label_6));
            remove_input_defaults(input_5);
            var node_13 = sibling(input_5, 2);
            {
              var consequent_15 = ($$anchor4) => {
                var small_4 = root_94();
                var text_15 = only_child(small_4, true);
                template_effect(($0) => set_text(text_15, $0), [() => lockMessage("content_path")]);
                append($$anchor4, small_4);
              };
              var d_5 = user_derived(() => isLocked("content_path"));
              var alternate_2 = ($$anchor4) => {
                var small_5 = root_124();
                append($$anchor4, small_5);
              };
              if_block(node_13, ($$render) => {
                if (get2(d_5)) $$render(consequent_15);
                else $$render(alternate_2, -1);
              });
            }
            reset(label_6);
            var div_14 = sibling(label_6, 2);
            var div_15 = sibling(child(div_14), 2);
            var button_11 = child(div_15);
            var text_16 = only_child(button_11, true);
            var button_12 = sibling(button_11, 2);
            var text_17 = only_child(button_12, true);
            reset(div_15);
            reset(div_14);
            var node_14 = sibling(div_14, 2);
            {
              var consequent_16 = ($$anchor4) => {
                var p_4 = root_134();
                append($$anchor4, p_4);
              };
              if_block(node_14, ($$render) => {
                if (get2(dirty)) $$render(consequent_16);
              });
            }
            var node_15 = sibling(node_14, 2);
            {
              var consequent_17 = ($$anchor4) => {
                var p_5 = root_142();
                var text_18 = only_child(p_5, true);
                template_effect(() => set_text(text_18, get2(syncError)));
                append($$anchor4, p_5);
              };
              if_block(node_15, ($$render) => {
                if (get2(syncError)) $$render(consequent_17);
              });
            }
            var node_16 = sibling(node_15, 2);
            {
              var consequent_18 = ($$anchor4) => {
                var div_16 = root_152();
                var span_1 = sibling(child(div_16));
                var text_19 = only_child(span_1);
                reset(div_16);
                template_effect(() => set_text(text_19, `\u0414\u043E\u0431\u0430\u0432\u043B\u0435\u043D\u043E: ${get2(syncResult).added ?? ""} \xB7 \u043E\u0431\u043D\u043E\u0432\u043B\u0435\u043D\u043E: ${get2(syncResult).updated ?? ""} \xB7 \u043F\u0440\u043E\u043F\u0443\u0449\u0435\u043D\u043E: ${get2(syncResult).skipped ?? ""} \xB7 \u043E\u0448\u0438\u0431\u043E\u043A: ${get2(syncResult).errors ?? ""}`));
                append($$anchor4, div_16);
              };
              if_block(node_16, ($$render) => {
                if (get2(syncResult)) $$render(consequent_18);
              });
            }
            var node_17 = sibling(node_16, 2);
            {
              var consequent_24 = ($$anchor4) => {
                var div_17 = root_20();
                var node_18 = child(div_17);
                {
                  var consequent_19 = ($$anchor5) => {
                    var p_6 = root_162();
                    append($$anchor5, p_6);
                  };
                  var consequent_20 = ($$anchor5) => {
                    var p_7 = root_142();
                    var text_20 = only_child(p_7, true);
                    template_effect(() => set_text(text_20, get2(logsError)));
                    append($$anchor5, p_7);
                  };
                  var consequent_21 = ($$anchor5) => {
                    var p_8 = root_172();
                    append($$anchor5, p_8);
                  };
                  var consequent_23 = ($$anchor5) => {
                    var ul = root_192();
                    each(ul, 21, () => get2(logs), (item) => item.id, ($$anchor6, item) => {
                      var li = root_182();
                      var strong = child(li);
                      var text_21 = only_child(strong, true);
                      var span_2 = sibling(strong);
                      var text_22 = only_child(span_2, true);
                      var span_3 = sibling(span_2);
                      var text_23 = only_child(span_3);
                      var node_19 = sibling(span_3);
                      {
                        var consequent_22 = ($$anchor7) => {
                          var small_6 = root_94();
                          var text_24 = only_child(small_6, true);
                          template_effect(() => set_text(text_24, get2(item).error_details));
                          append($$anchor7, small_6);
                        };
                        if_block(node_19, ($$render) => {
                          if (get2(item).error_details) $$render(consequent_22);
                        });
                      }
                      reset(li);
                      template_effect(() => {
                        set_text(text_21, get2(item).status);
                        set_text(text_22, get2(item).finished_at || "\u0412\u0440\u0435\u043C\u044F \u043D\u0435 \u0443\u043A\u0430\u0437\u0430\u043D\u043E");
                        set_text(text_23, `\u041E\u0448\u0438\u0431\u043E\u043A: ${get2(item).errors ?? ""}`);
                      });
                      append($$anchor6, li);
                    });
                    reset(ul);
                    append($$anchor5, ul);
                  };
                  if_block(node_18, ($$render) => {
                    if (get2(logsLoading)) $$render(consequent_19);
                    else if (get2(logsError)) $$render(consequent_20, 1);
                    else if (get2(logs) && get2(logs).length === 0) $$render(consequent_21, 2);
                    else if (get2(logs)) $$render(consequent_23, 3);
                  });
                }
                reset(div_17);
                append($$anchor4, div_17);
              };
              if_block(node_17, ($$render) => {
                if (get2(logsOpen)) $$render(consequent_24);
              });
            }
            reset(div_13);
            template_effect(
              ($0) => {
                input_5.disabled = $0;
                button_11.disabled = get2(dirty) || get2(syncBusy) || !get2(snapshot2).config.content_path;
                set_text(text_16, get2(syncBusy) ? "\u0421\u0438\u043D\u0445\u0440\u043E\u043D\u0438\u0437\u0438\u0440\u0443\u044E\u2026" : "\u0421\u0438\u043D\u0445\u0440\u043E\u043D\u0438\u0437\u0438\u0440\u043E\u0432\u0430\u0442\u044C \u0441\u0435\u0439\u0447\u0430\u0441");
                set_text(text_17, get2(logsOpen) ? "\u0421\u043A\u0440\u044B\u0442\u044C \u0436\u0443\u0440\u043D\u0430\u043B" : "\u0416\u0443\u0440\u043D\u0430\u043B \u0441\u0438\u043D\u0445\u0440\u043E\u043D\u0438\u0437\u0430\u0446\u0438\u0438");
              },
              [() => isLocked("content_path")]
            );
            bind_value(input_5, () => get2(config).content_path, ($$value) => get2(config).content_path = $$value);
            delegated("click", button_11, () => void runSync());
            delegated("click", button_12, () => void showLogs());
            append($$anchor3, div_13);
          };
          var consequent_42 = ($$anchor3) => {
            var div_18 = root_29();
            var label_7 = sibling(child(div_18), 2);
            var input_6 = child(label_7);
            remove_input_defaults(input_6);
            next();
            reset(label_7);
            var node_20 = sibling(label_7, 2);
            {
              var consequent_26 = ($$anchor4) => {
                var p_9 = root_104();
                var text_25 = only_child(p_9, true);
                template_effect(($0) => set_text(text_25, $0), [() => lockMessage("ai_enabled")]);
                append($$anchor4, p_9);
              };
              var d_6 = user_derived(() => isLocked("ai_enabled"));
              if_block(node_20, ($$render) => {
                if (get2(d_6)) $$render(consequent_26);
              });
            }
            var div_19 = sibling(node_20, 2);
            var label_8 = child(div_19);
            var input_7 = sibling(child(label_8));
            remove_input_defaults(input_7);
            var node_21 = sibling(input_7);
            {
              var consequent_27 = ($$anchor4) => {
                var small_7 = root_94();
                var text_26 = only_child(small_7, true);
                template_effect(($0) => set_text(text_26, $0), [() => lockMessage("ai_base_url")]);
                append($$anchor4, small_7);
              };
              var d_7 = user_derived(() => isLocked("ai_base_url"));
              if_block(node_21, ($$render) => {
                if (get2(d_7)) $$render(consequent_27);
              });
            }
            reset(label_8);
            var label_9 = sibling(label_8, 2);
            var div_20 = sibling(child(label_9));
            var input_8 = child(div_20);
            remove_input_defaults(input_8);
            var datalist = sibling(input_8);
            each(datalist, 21, () => get2(models), index, ($$anchor4, model) => {
              var option = root_222();
              var option_value = {};
              template_effect(() => {
                if (option_value !== (option_value = get2(model))) {
                  option.value = (option.__value = option_value) ?? "";
                }
              });
              append($$anchor4, option);
            });
            reset(datalist);
            var button_13 = sibling(datalist);
            var text_27 = only_child(button_13, true);
            reset(div_20);
            var node_22 = sibling(div_20);
            {
              var consequent_28 = ($$anchor4) => {
                var small_8 = root_94();
                var text_28 = only_child(small_8, true);
                template_effect(($0) => set_text(text_28, $0), [() => lockMessage("ai_model")]);
                append($$anchor4, small_8);
              };
              var d_8 = user_derived(() => isLocked("ai_model"));
              if_block(node_22, ($$render) => {
                if (get2(d_8)) $$render(consequent_28);
              });
            }
            var node_23 = sibling(node_22);
            {
              var consequent_29 = ($$anchor4) => {
                var small_9 = root_232();
                var text_29 = only_child(small_9, true);
                template_effect(() => set_text(text_29, get2(modelsError)));
                append($$anchor4, small_9);
              };
              if_block(node_23, ($$render) => {
                if (get2(modelsError)) $$render(consequent_29);
              });
            }
            reset(label_9);
            var label_10 = sibling(label_9, 2);
            var input_9 = sibling(child(label_10));
            remove_input_defaults(input_9);
            var node_24 = sibling(input_9);
            {
              var consequent_30 = ($$anchor4) => {
                var small_10 = root_94();
                var text_30 = only_child(small_10, true);
                template_effect(($0) => set_text(text_30, $0), [() => lockMessage("ai_timeout_seconds")]);
                append($$anchor4, small_10);
              };
              var d_9 = user_derived(() => isLocked("ai_timeout_seconds"));
              if_block(node_24, ($$render) => {
                if (get2(d_9)) $$render(consequent_30);
              });
            }
            reset(label_10);
            var label_11 = sibling(label_10, 2);
            var input_10 = sibling(child(label_11));
            remove_input_defaults(input_10);
            var node_25 = sibling(input_10);
            {
              var consequent_31 = ($$anchor4) => {
                var small_11 = root_94();
                var text_31 = only_child(small_11, true);
                template_effect(($0) => set_text(text_31, $0), [() => lockMessage("ai_max_tokens")]);
                append($$anchor4, small_11);
              };
              var d_10 = user_derived(() => isLocked("ai_max_tokens"));
              if_block(node_25, ($$render) => {
                if (get2(d_10)) $$render(consequent_31);
              });
            }
            reset(label_11);
            reset(div_19);
            var label_12 = sibling(div_19, 2);
            var select = sibling(child(label_12));
            var option_1 = child(select);
            option_1.value = option_1.__value = "max_tokens";
            var option_2 = sibling(option_1);
            option_2.value = option_2.__value = "max_completion_tokens";
            reset(select);
            init_select(select);
            next();
            reset(label_12);
            var node_26 = sibling(label_12, 2);
            {
              var consequent_32 = ($$anchor4) => {
                var p_10 = root_104();
                var text_32 = only_child(p_10, true);
                template_effect(($0) => set_text(text_32, $0), [() => lockMessage("ai_token_limit_parameter")]);
                append($$anchor4, p_10);
              };
              var d_11 = user_derived(() => isLocked("ai_token_limit_parameter"));
              if_block(node_26, ($$render) => {
                if (get2(d_11)) $$render(consequent_32);
              });
            }
            var label_13 = sibling(node_26, 2);
            var input_11 = child(label_13);
            remove_input_defaults(input_11);
            next();
            reset(label_13);
            var node_27 = sibling(label_13, 2);
            {
              var consequent_33 = ($$anchor4) => {
                var label_14 = root_242();
                var input_12 = sibling(child(label_14));
                remove_input_defaults(input_12);
                reset(label_14);
                template_effect(($0) => input_12.disabled = $0, [() => isLocked("ai_temperature")]);
                bind_value(input_12, () => get2(config).ai_temperature, ($$value) => get2(config).ai_temperature = $$value);
                append($$anchor4, label_14);
              };
              if_block(node_27, ($$render) => {
                if (get2(config).ai_temperature !== null) $$render(consequent_33);
              });
            }
            var node_28 = sibling(node_27, 2);
            {
              var consequent_34 = ($$anchor4) => {
                var p_11 = root_104();
                var text_33 = only_child(p_11, true);
                template_effect(($0) => set_text(text_33, $0), [() => lockMessage("ai_temperature")]);
                append($$anchor4, p_11);
              };
              var d_12 = user_derived(() => isLocked("ai_temperature"));
              if_block(node_28, ($$render) => {
                if (get2(d_12)) $$render(consequent_34);
              });
            }
            var label_15 = sibling(node_28, 2);
            var input_13 = child(label_15);
            remove_input_defaults(input_13);
            next();
            reset(label_15);
            var node_29 = sibling(label_15, 2);
            {
              var consequent_35 = ($$anchor4) => {
                var p_12 = root_104();
                var text_34 = only_child(p_12, true);
                template_effect(($0) => set_text(text_34, $0), [() => lockMessage("ai_tools_enabled")]);
                append($$anchor4, p_12);
              };
              var d_13 = user_derived(() => isLocked("ai_tools_enabled"));
              if_block(node_29, ($$render) => {
                if (get2(d_13)) $$render(consequent_35);
              });
            }
            var label_16 = sibling(node_29, 2);
            var textarea = sibling(child(label_16));
            remove_textarea_child(textarea);
            var node_30 = sibling(textarea);
            {
              var consequent_36 = ($$anchor4) => {
                var small_12 = root_94();
                var text_35 = only_child(small_12, true);
                template_effect(($0) => set_text(text_35, $0), [() => lockMessage("ai_system_prompt")]);
                append($$anchor4, small_12);
              };
              var d_14 = user_derived(() => isLocked("ai_system_prompt"));
              if_block(node_30, ($$render) => {
                if (get2(d_14)) $$render(consequent_36);
              });
            }
            reset(label_16);
            var div_21 = sibling(label_16, 2);
            var div_22 = child(div_21);
            var p_13 = sibling(child(div_22));
            var text_36 = only_child(p_13);
            reset(div_22);
            var label_17 = sibling(div_22, 2);
            var span_4 = child(label_17);
            var text_37 = only_child(span_4, true);
            var input_14 = sibling(span_4);
            remove_input_defaults(input_14);
            reset(label_17);
            var node_31 = sibling(label_17, 2);
            {
              var consequent_37 = ($$anchor4) => {
                var p_14 = root_104();
                var text_38 = only_child(p_14, true);
                template_effect(($0) => set_text(text_38, $0), [() => lockMessage("api_key")]);
                append($$anchor4, p_14);
              };
              var d_15 = user_derived(() => isLocked("api_key"));
              if_block(node_31, ($$render) => {
                if (get2(d_15)) $$render(consequent_37);
              });
            }
            var node_32 = sibling(node_31, 2);
            {
              var consequent_38 = ($$anchor4) => {
                var p_15 = root_252();
                var text_39 = only_child(p_15);
                template_effect(() => set_text(text_39, `\u041E\u0448\u0438\u0431\u043A\u0430 \u043A\u043B\u044E\u0447\u0430: ${get2(snapshot2).api_key_error ?? ""}`));
                append($$anchor4, p_15);
              };
              if_block(node_32, ($$render) => {
                if (get2(snapshot2).api_key_error) $$render(consequent_38);
              });
            }
            var node_33 = sibling(node_32, 2);
            {
              var consequent_39 = ($$anchor4) => {
                var label_18 = root_262();
                var input_15 = child(label_18);
                remove_input_defaults(input_15);
                next();
                reset(label_18);
                template_effect(($0) => input_15.disabled = $0, [() => isLocked("api_key")]);
                bind_checked(input_15, () => get2(clearApiKey), ($$value) => set(clearApiKey, $$value));
                append($$anchor4, label_18);
              };
              if_block(node_33, ($$render) => {
                if (get2(snapshot2).api_key_configured) $$render(consequent_39);
              });
            }
            reset(div_21);
            var div_23 = sibling(div_21, 2);
            var button_14 = child(div_23);
            var text_40 = only_child(button_14, true);
            var node_34 = sibling(button_14, 2);
            {
              var consequent_40 = ($$anchor4) => {
                var span_5 = root_272();
                let classes_4;
                var text_41 = only_child(span_5);
                template_effect(() => {
                  classes_4 = set_class(span_5, 1, "test-status svelte-1u3w06f", null, classes_4, { success: get2(aiTest).ok, failure: !get2(aiTest).ok });
                  set_text(text_41, `${get2(aiTest).ok ? "\u041F\u043E\u0434\u043A\u043B\u044E\u0447\u0435\u043D\u0438\u0435 \u0443\u0441\u043F\u0435\u0448\u043D\u043E" : "\u041F\u0440\u043E\u0432\u0430\u0439\u0434\u0435\u0440 \u0432\u0435\u0440\u043D\u0443\u043B \u043E\u0448\u0438\u0431\u043A\u0443"} \xB7 ${get2(aiTest).latency_ms ?? ""} \u043C\u0441 \xB7 ${get2(aiTest).model ?? ""}`);
                });
                append($$anchor4, span_5);
              };
              if_block(node_34, ($$render) => {
                if (get2(aiTest)) $$render(consequent_40);
              });
            }
            var node_35 = sibling(node_34, 2);
            {
              var consequent_41 = ($$anchor4) => {
                var span_6 = root_28();
                var text_42 = only_child(span_6, true);
                template_effect(() => set_text(text_42, get2(aiTestError)));
                append($$anchor4, span_6);
              };
              if_block(node_35, ($$render) => {
                if (get2(aiTestError)) $$render(consequent_41);
              });
            }
            reset(div_23);
            reset(div_18);
            template_effect(
              ($0, $1, $2, $3, $4, $5, $6, $7, $8, $9) => {
                input_6.disabled = $0;
                input_7.disabled = $1;
                input_8.disabled = $2;
                button_13.disabled = get2(modelsLoading);
                set_text(text_27, get2(modelsLoading) ? "\u0417\u0430\u0433\u0440\u0443\u0437\u043A\u0430\u2026" : "\u0417\u0430\u0433\u0440\u0443\u0437\u0438\u0442\u044C \u043C\u043E\u0434\u0435\u043B\u0438");
                input_9.disabled = $3;
                input_10.disabled = $4;
                select.disabled = $5;
                set_checked(input_11, get2(config).ai_temperature !== null);
                input_11.disabled = $6;
                input_13.disabled = $7;
                textarea.disabled = $8;
                set_text(text_36, `${get2(snapshot2).api_key_configured ? "\u041A\u043B\u044E\u0447 \u043D\u0430\u0441\u0442\u0440\u043E\u0435\u043D. \u041F\u043E\u043B\u0435 \u043F\u0443\u0441\u0442\u043E\u0435 \u2014 \u043E\u0441\u0442\u0430\u0432\u0438\u0442\u044C \u0442\u0435\u043A\u0443\u0449\u0438\u0439 \u043A\u043B\u044E\u0447." : "\u041A\u043B\u044E\u0447 \u0435\u0449\u0451 \u043D\u0435 \u0437\u0430\u0434\u0430\u043D."} \u0412\u0432\u0435\u0434\u0451\u043D\u043D\u043E\u0435 \u0437\u043D\u0430\u0447\u0435\u043D\u0438\u0435 \u0441\u0435\u0440\u0432\u0435\u0440 \u043D\u0435 \u043F\u043E\u043A\u0430\u0436\u0435\u0442 \u043F\u043E\u0432\u0442\u043E\u0440\u043D\u043E.`);
                set_text(text_37, get2(snapshot2).api_key_configured ? "\u041D\u043E\u0432\u044B\u0439 \u043A\u043B\u044E\u0447 (\u043D\u0435\u043E\u0431\u044F\u0437\u0430\u0442\u0435\u043B\u044C\u043D\u043E)" : "\u041A\u043B\u044E\u0447");
                set_attribute2(input_14, "placeholder", get2(snapshot2).api_key_configured ? "\u041E\u0441\u0442\u0430\u0432\u044C \u043F\u0443\u0441\u0442\u044B\u043C, \u0447\u0442\u043E\u0431\u044B \u0441\u043E\u0445\u0440\u0430\u043D\u0438\u0442\u044C \u0442\u0435\u043A\u0443\u0449\u0438\u0439" : "\u0412\u0432\u0435\u0434\u0438 API-\u043A\u043B\u044E\u0447");
                input_14.disabled = $9;
                button_14.disabled = get2(saving) || get2(aiTesting);
                set_text(text_40, get2(saving) ? "\u0421\u043E\u0445\u0440\u0430\u043D\u044F\u044E\u2026" : get2(aiTesting) ? "\u041F\u0440\u043E\u0432\u0435\u0440\u044F\u044E\u2026" : "\u0421\u043E\u0445\u0440\u0430\u043D\u0438\u0442\u044C \u0438 \u043F\u0440\u043E\u0432\u0435\u0440\u0438\u0442\u044C AI");
              },
              [
                () => isLocked("ai_enabled"),
                () => isLocked("ai_base_url"),
                () => isLocked("ai_model"),
                () => isLocked("ai_timeout_seconds"),
                () => isLocked("ai_max_tokens"),
                () => isLocked("ai_token_limit_parameter"),
                () => isLocked("ai_temperature"),
                () => isLocked("ai_tools_enabled"),
                () => isLocked("ai_system_prompt"),
                () => isLocked("api_key")
              ]
            );
            bind_checked(input_6, () => get2(config).ai_enabled, ($$value) => get2(config).ai_enabled = $$value);
            bind_value(input_7, () => get2(config).ai_base_url, ($$value) => get2(config).ai_base_url = $$value);
            bind_value(input_8, () => get2(config).ai_model, ($$value) => get2(config).ai_model = $$value);
            delegated("click", button_13, () => void loadModels());
            bind_value(input_9, () => get2(config).ai_timeout_seconds, ($$value) => get2(config).ai_timeout_seconds = $$value);
            bind_value(input_10, () => get2(config).ai_max_tokens, ($$value) => get2(config).ai_max_tokens = $$value);
            bind_select_value(select, () => get2(config).ai_token_limit_parameter, ($$value) => get2(config).ai_token_limit_parameter = $$value);
            delegated("change", input_11, setTemperatureEnabled);
            bind_checked(input_13, () => get2(config).ai_tools_enabled, ($$value) => get2(config).ai_tools_enabled = $$value);
            bind_value(textarea, () => get2(config).ai_system_prompt, ($$value) => get2(config).ai_system_prompt = $$value);
            bind_value(input_14, () => get2(apiKey), ($$value) => set(apiKey, $$value));
            delegated("click", button_14, () => void save2(true));
            append($$anchor3, div_18);
          };
          var alternate_3 = ($$anchor3) => {
            var div_24 = root_332();
            var div_25 = sibling(child(div_24), 4);
            each(
              div_25,
              21,
              () => Object.entries({
                \u0412\u0435\u0440\u0441\u0438\u044F: get2(snapshot2).runtime.version,
                \u041E\u043A\u0440\u0443\u0436\u0435\u043D\u0438\u0435: get2(snapshot2).runtime.environment,
                "\u041F\u0443\u0442\u044C \u043A \u0411\u0414": get2(snapshot2).runtime.db_path,
                "\u0410\u0434\u0440\u0435\u0441 \u043F\u0440\u0438\u0432\u044F\u0437\u043A\u0438": get2(snapshot2).runtime.bind_host,
                \u041F\u043E\u0440\u0442: get2(snapshot2).runtime.bind_port,
                \u0412\u043E\u0440\u043A\u0435\u0440\u044B: get2(snapshot2).runtime.workers,
                "JWT secret \u0437\u0430\u0434\u0430\u043D": get2(snapshot2).runtime.jwt_secret_configured ? "\u0414\u0430" : "\u041D\u0435\u0442",
                "Allowed hosts": get2(snapshot2).runtime.allowed_hosts.join(", ") || "\u2014",
                "CORS origins": get2(snapshot2).runtime.cors_origins.join(", ") || "\u2014"
              }),
              index,
              ($$anchor4, $$item) => {
                var $$array = user_derived(() => to_array(get2($$item), 2));
                let label = () => get2($$array)[0];
                let value = () => get2($$array)[1];
                var div_26 = root_30();
                var small_13 = child(div_26);
                var text_43 = only_child(small_13, true);
                var strong_1 = sibling(small_13);
                var text_44 = only_child(strong_1, true);
                reset(div_26);
                template_effect(() => {
                  set_text(text_43, label());
                  set_text(text_44, value());
                });
                append($$anchor4, div_26);
              }
            );
            reset(div_25);
            var div_27 = sibling(div_25, 2);
            var div_28 = sibling(child(div_27), 2);
            var button_15 = child(div_28);
            var text_45 = only_child(button_15, true);
            var node_36 = sibling(button_15);
            {
              var consequent_43 = ($$anchor4) => {
                var button_16 = root_31();
                delegated("click", button_16, downloadDeployment);
                append($$anchor4, button_16);
              };
              if_block(node_36, ($$render) => {
                if (get2(deploymentReady)) $$render(consequent_43);
              });
            }
            reset(div_28);
            reset(div_27);
            var node_37 = sibling(div_27, 2);
            {
              var consequent_44 = ($$anchor4) => {
                var p_16 = root_142();
                var text_46 = only_child(p_16, true);
                template_effect(() => set_text(text_46, get2(deploymentError)));
                append($$anchor4, p_16);
              };
              if_block(node_37, ($$render) => {
                if (get2(deploymentError)) $$render(consequent_44);
              });
            }
            var node_38 = sibling(node_37, 2);
            {
              var consequent_45 = ($$anchor4) => {
                var label_19 = root_322();
                var textarea_1 = sibling(child(label_19));
                remove_textarea_child(textarea_1);
                reset(label_19);
                bind_value(textarea_1, () => get2(deploymentText), ($$value) => set(deploymentText, $$value));
                append($$anchor4, label_19);
              };
              if_block(node_38, ($$render) => {
                if (get2(deploymentReady)) $$render(consequent_45);
              });
            }
            reset(div_24);
            template_effect(() => {
              button_15.disabled = get2(deploymentLoading);
              set_text(text_45, get2(deploymentLoading) ? "\u0413\u043E\u0442\u043E\u0432\u043B\u044E\u2026" : "\u041F\u043E\u0434\u0433\u043E\u0442\u043E\u0432\u0438\u0442\u044C .env.example");
            });
            delegated("click", button_15, () => void prepareDeployment());
            append($$anchor3, div_24);
          };
          if_block(node_7, ($$render) => {
            if (get2(activeTab) === "general") $$render(consequent_14);
            else if (get2(activeTab) === "content") $$render(consequent_25, 1);
            else if (get2(activeTab) === "ai") $$render(consequent_42, 2);
            else $$render(alternate_3, -1);
          });
        }
        reset(fieldset);
        template_effect(() => {
          fieldset.disabled = get2(saving) || get2(syncBusy) || get2(aiTesting);
          classes = set_class(button_7, 1, "svelte-1u3w06f", null, classes, { active: get2(activeTab) === "general" });
          classes_1 = set_class(button_8, 1, "svelte-1u3w06f", null, classes_1, { active: get2(activeTab) === "content" });
          classes_2 = set_class(button_9, 1, "svelte-1u3w06f", null, classes_2, { active: get2(activeTab) === "ai" });
          classes_3 = set_class(button_10, 1, "svelte-1u3w06f", null, classes_3, { active: get2(activeTab) === "deployment" });
        });
        delegated("click", button_7, () => set(activeTab, "general"));
        delegated("click", button_8, () => set(activeTab, "content"));
        delegated("click", button_9, () => set(activeTab, "ai"));
        delegated("click", button_10, () => set(activeTab, "deployment"));
        append($$anchor2, fieldset);
      };
      var alternate_4 = ($$anchor2) => {
        var div_29 = root_352();
        append($$anchor2, div_29);
      };
      if_block(node_1, ($$render) => {
        if (get2(loading) && !get2(snapshot2)) $$render(consequent_1);
        else if (get2(loadError) && !get2(snapshot2)) $$render(consequent_2, 1);
        else if (get2(snapshot2) && get2(config)) $$render(consequent_46, 2);
        else $$render(alternate_4, -1);
      });
    }
    reset(section);
    append($$anchor, section);
    pop();
  }
  delegate(["click", "change"]);

  // src/components/ChatContent.svelte
  var root8 = from_html(`<div class="code-block svelte-1qmz6rz"><div class="code-title svelte-1qmz6rz"><span> </span><button type="button" class="svelte-1qmz6rz"> </button></div><pre class="svelte-1qmz6rz"><code class="svelte-1qmz6rz"> </code></pre></div>`);
  var root_111 = from_html(`<strong> </strong>`);
  var root_210 = from_html(`<code class="svelte-1qmz6rz"> </code>`);
  var root_38 = from_html(`<p class="svelte-1qmz6rz"></p>`);
  var root_47 = from_html(`<div class="chat-content svelte-1qmz6rz"></div>`);
  var $$css8 = {
    hash: "svelte-1qmz6rz",
    code: ".chat-content.svelte-1qmz6rz {line-height:1.7;overflow-wrap:anywhere;}p.svelte-1qmz6rz {white-space:pre-wrap;margin:0 0 .8rem;}p.svelte-1qmz6rz:last-child {margin-bottom:0;}code.svelte-1qmz6rz {font-family:'Cascadia Code', Consolas, monospace;font-size:.9em;background:#252c34;padding:2px 5px;border-radius:4px;}.code-block.svelte-1qmz6rz {margin:14px 0;border:1px solid #39414c;border-radius:8px;overflow:hidden;}.code-title.svelte-1qmz6rz {display:flex;justify-content:space-between;align-items:center;padding:6px 10px;background:#252c34;color:#a5b2c2;font-size:12px;}.code-title.svelte-1qmz6rz button:where(.svelte-1qmz6rz) {background:transparent;border:0;padding:3px 8px;color:inherit;}pre.svelte-1qmz6rz {margin:0;padding:14px;background:#15191e;overflow-x:auto;white-space:pre;}pre.svelte-1qmz6rz code:where(.svelte-1qmz6rz) {padding:0;background:transparent;}"
  };
  function ChatContent($$anchor, $$props) {
    push($$props, true);
    append_styles($$anchor, $$css8);
    let copied = state(-1);
    const blocks = user_derived(() => $$props.content.split(/(```[\s\S]*?```)/g).filter(Boolean).map((part) => {
      if (!part.startsWith("```") || !part.endsWith("```")) return { code: false, text: part, language: "" };
      const inner = part.slice(3, -3);
      const match = inner.match(/^([\w+-]*)\n([\s\S]*)$/);
      return {
        code: true,
        text: match ? match[2] : inner,
        language: match ? match[1] : ""
      };
    }));
    async function copy(text2, index2) {
      try {
        await navigator.clipboard.writeText(text2);
        set(copied, index2, true);
      } catch {
        set(copied, -1);
      }
    }
    var div = root_47();
    each(div, 21, () => get2(blocks), index, ($$anchor2, block2, i) => {
      var fragment = comment();
      var node = first_child(fragment);
      {
        var consequent = ($$anchor3) => {
          var div_1 = root8();
          var div_2 = child(div_1);
          var span = child(div_2);
          var text_1 = only_child(span, true);
          var button = sibling(span);
          var text_2 = only_child(button, true);
          reset(div_2);
          var pre = sibling(div_2);
          var code = child(pre);
          var text_3 = only_child(code, true);
          reset(pre);
          reset(div_1);
          template_effect(() => {
            set_text(text_1, get2(block2).language || "code");
            set_text(text_2, get2(copied) === i ? "\u0421\u043A\u043E\u043F\u0438\u0440\u043E\u0432\u0430\u043D\u043E" : "\u041A\u043E\u043F\u0438\u0440\u043E\u0432\u0430\u0442\u044C \u043A\u043E\u0434");
            set_text(text_3, get2(block2).text);
          });
          delegated("click", button, () => copy(get2(block2).text, i));
          append($$anchor3, div_1);
        };
        var alternate_1 = ($$anchor3) => {
          var fragment_1 = comment();
          var node_1 = first_child(fragment_1);
          each(node_1, 17, () => get2(block2).text.split(/\n{2,}/).filter(Boolean), index, ($$anchor4, paragraph) => {
            var p = root_38();
            each(p, 21, () => get2(paragraph).split(/(\*\*[^*]+\*\*|`[^`]+`)/g), index, ($$anchor5, part) => {
              var fragment_2 = comment();
              var node_2 = first_child(fragment_2);
              {
                var consequent_1 = ($$anchor6) => {
                  var strong = root_111();
                  var text_4 = only_child(strong, true);
                  template_effect(($0) => set_text(text_4, $0), [() => get2(part).slice(2, -2)]);
                  append($$anchor6, strong);
                };
                var d = user_derived(() => get2(part).startsWith("**") && get2(part).endsWith("**"));
                var consequent_2 = ($$anchor6) => {
                  var code_1 = root_210();
                  var text_5 = only_child(code_1, true);
                  template_effect(($0) => set_text(text_5, $0), [() => get2(part).slice(1, -1)]);
                  append($$anchor6, code_1);
                };
                var d_1 = user_derived(() => get2(part).startsWith("`") && get2(part).endsWith("`"));
                var alternate = ($$anchor6) => {
                  var text_6 = text();
                  template_effect(() => set_text(text_6, get2(part)));
                  append($$anchor6, text_6);
                };
                if_block(node_2, ($$render) => {
                  if (get2(d)) $$render(consequent_1);
                  else if (get2(d_1)) $$render(consequent_2, 1);
                  else $$render(alternate, -1);
                });
              }
              append($$anchor5, fragment_2);
            });
            reset(p);
            append($$anchor4, p);
          });
          append($$anchor3, fragment_1);
        };
        if_block(node, ($$render) => {
          if (get2(block2).code) $$render(consequent);
          else $$render(alternate_1, -1);
        });
      }
      append($$anchor2, fragment);
    });
    reset(div);
    append($$anchor, div);
    pop();
  }
  delegate(["click"]);

  // src/components/Assistant.svelte
  var root9 = from_html(`<div><button class="chat-title svelte-1tlx730"> <small class="svelte-1tlx730"> </small></button> <button class="delete svelte-1tlx730">\xD7</button></div>`);
  var root_115 = from_html(`<p class="muted svelte-1tlx730">\u0414\u0438\u0430\u043B\u043E\u0433\u0438 \u043F\u043E\u044F\u0432\u044F\u0442\u0441\u044F \u0437\u0434\u0435\u0441\u044C \u043F\u043E\u0441\u043B\u0435 \u043F\u0435\u0440\u0432\u043E\u0433\u043E \u0441\u043E\u043E\u0431\u0449\u0435\u043D\u0438\u044F.</p>`);
  var root_211 = from_html(`<p class="muted svelte-1tlx730">\u0417\u0430\u0433\u0440\u0443\u0436\u0430\u044E \u0434\u0438\u0430\u043B\u043E\u0433\u2026</p>`);
  var root_39 = from_html(`<div class="empty-state svelte-1tlx730"><h2 class="svelte-1tlx730">\u041F\u043E\u0434\u043A\u043B\u044E\u0447\u0438 \u0441\u0432\u043E\u0435\u0433\u043E AI-\u043F\u0440\u043E\u0432\u0430\u0439\u0434\u0435\u0440\u0430</h2><p>\u0423\u043A\u0430\u0436\u0438 URL API, \u043C\u043E\u0434\u0435\u043B\u044C \u0438 \u043A\u043B\u044E\u0447 \u0432 \u043D\u0430\u0441\u0442\u0440\u043E\u0439\u043A\u0430\u0445. \u0414\u0438\u0430\u043B\u043E\u0433\u0438 \u0438 \u0447\u0435\u0440\u043D\u043E\u0432\u0438\u043A\u0438 \u0431\u0443\u0434\u0443\u0442 \u0445\u0440\u0430\u043D\u0438\u0442\u044C\u0441\u044F \u043D\u0430 \u0441\u0435\u0440\u0432\u0435\u0440\u0435.</p><button class="primary">\u041E\u0442\u043A\u0440\u044B\u0442\u044C \u043D\u0430\u0441\u0442\u0440\u043E\u0439\u043A\u0438</button></div>`);
  var root_48 = from_html(`<button class="svelte-1tlx730"> </button>`);
  var root_57 = from_html(`<div class="empty-state svelte-1tlx730"><span class="assistant-mark svelte-1tlx730">\u2726</span><h2 class="svelte-1tlx730">\u0427\u0442\u043E \u0440\u0430\u0437\u0431\u0435\u0440\u0451\u043C \u0432 \u0441\u0435\u0440\u0432\u0438\u0441\u0435?</h2><p>\u041C\u043E\u0433\u0443 \u043F\u0440\u043E\u0432\u0435\u0440\u0438\u0442\u044C \u0441\u043E\u0441\u0442\u043E\u044F\u043D\u0438\u0435, \u043D\u0430\u0439\u0442\u0438 \u0437\u0430\u0434\u0430\u0447\u0443, \u043F\u043E\u0434\u0433\u043E\u0442\u043E\u0432\u0438\u0442\u044C \u043D\u0430\u0441\u0442\u0440\u043E\u0439\u043A\u0438 \u0438 \u043F\u0440\u0435\u0434\u043B\u043E\u0436\u0438\u0442\u044C \u043F\u0440\u0430\u0432\u043A\u0443 \u0442\u0435\u043A\u0441\u0442\u0430 \u0438\u043B\u0438 \u0442\u0435\u0441\u0442\u043E\u0432.</p><div class="suggestions svelte-1tlx730"></div></div>`);
  var root_65 = from_html(`<div class="proposal svelte-1tlx730"><div class="svelte-1tlx730"><small class="svelte-1tlx730">\u0427\u0435\u0440\u043D\u043E\u0432\u0438\u043A \xB7 \u0442\u0440\u0435\u0431\u0443\u0435\u0442\u0441\u044F \u043F\u0440\u043E\u0432\u0435\u0440\u043A\u0430</small><strong> </strong><span class="svelte-1tlx730"> </span></div><button class="primary">\u041F\u0440\u043E\u0432\u0435\u0440\u0438\u0442\u044C \u0438\u0437\u043C\u0435\u043D\u0435\u043D\u0438\u044F \u2192</button></div>`);
  var root_75 = from_html(`<article><div class="message-heading svelte-1tlx730"><strong class="svelte-1tlx730"> </strong><span> </span><!></div> <!> <!></article>`);
  var root_85 = from_html(`<div class="inline-error svelte-1tlx730" role="alert"> </div>`);
  var root_95 = from_html(`<option> </option>`);
  var root_105 = from_html(`<button>\u25A0 \u041E\u0441\u0442\u0430\u043D\u043E\u0432\u0438\u0442\u044C</button>`);
  var root_116 = from_html(`<button class="primary">\u041E\u0442\u043F\u0440\u0430\u0432\u0438\u0442\u044C \u2191</button>`);
  var root_125 = from_html(`<div class="assistant-layout svelte-1tlx730"><aside class="history svelte-1tlx730" aria-label="\u0418\u0441\u0442\u043E\u0440\u0438\u044F AI-\u0434\u0438\u0430\u043B\u043E\u0433\u043E\u0432"><button class="primary">\uFF0B \u041D\u043E\u0432\u044B\u0439 \u0434\u0438\u0430\u043B\u043E\u0433</button> <p class="eyebrow svelte-1tlx730">\u0418\u0441\u0442\u043E\u0440\u0438\u044F</p> <!> <!> <div class="history-footer svelte-1tlx730"><span class="model svelte-1tlx730"> </span><button>\u041D\u0430\u0441\u0442\u0440\u043E\u0439\u043A\u0438 AI \u2192</button></div></aside> <section class="conversation svelte-1tlx730" aria-label="\u0427\u0430\u0442 \u0441 AI-\u043F\u043E\u043C\u043E\u0449\u043D\u0438\u043A\u043E\u043C"><div class="context svelte-1tlx730"><span class="context-dot svelte-1tlx730"></span> \u041A\u043E\u043D\u0442\u0435\u043A\u0441\u0442: \u0441\u0435\u0440\u0432\u0438\u0441, \u043D\u0430\u0441\u0442\u0440\u043E\u0439\u043A\u0438 \u0438 \u043A\u0430\u0442\u0430\u043B\u043E\u0433 <span class="muted svelte-1tlx730">\xB7 \u0438\u0437\u043C\u0435\u043D\u0435\u043D\u0438\u044F \u0447\u0435\u0440\u0435\u0437 \u043F\u0440\u043E\u0432\u0435\u0440\u044F\u0435\u043C\u044B\u0435 \u0447\u0435\u0440\u043D\u043E\u0432\u0438\u043A\u0438</span></div> <div class="messages svelte-1tlx730" aria-live="polite"><!> <!> <!></div> <div class="composer svelte-1tlx730"><!> <label class="attachment svelte-1tlx730">\u0417\u0430\u0434\u0430\u0447\u0430 \u0432 \u043A\u043E\u043D\u0442\u0435\u043A\u0441\u0442\u0435 <select class="svelte-1tlx730"><option>\u041E\u0431\u0449\u0438\u0439 \u043A\u043E\u043D\u0442\u0435\u043A\u0441\u0442 \u0441\u0435\u0440\u0432\u0438\u0441\u0430</option><!></select></label> <div class="input-box svelte-1tlx730"><textarea placeholder="\u041D\u0430\u043F\u0438\u0448\u0438, \u0447\u0442\u043E \u043D\u0443\u0436\u043D\u043E \u043F\u0440\u043E\u0432\u0435\u0440\u0438\u0442\u044C \u0438\u043B\u0438 \u043F\u043E\u0434\u0433\u043E\u0442\u043E\u0432\u0438\u0442\u044C\u2026" aria-label="\u0421\u043E\u043E\u0431\u0449\u0435\u043D\u0438\u0435 \u043F\u043E\u043C\u043E\u0449\u043D\u0438\u043A\u0443" maxlength="8000" class="svelte-1tlx730"></textarea><div class="composer-actions svelte-1tlx730"><small class="svelte-1tlx730"> </small><!></div></div></div></section></div>`);
  var $$css9 = {
    hash: "svelte-1tlx730",
    code: ".assistant-layout.svelte-1tlx730 {display:grid;grid-template-columns:230px minmax(0, 1fr);height:calc(100vh - 140px);min-height:550px;border:1px solid #343a44;border-radius:12px;overflow:hidden;background:#1b2026;}.history.svelte-1tlx730 {padding:16px;border-right:1px solid #343a44;display:flex;flex-direction:column;gap:6px;overflow:auto;background:#191d23;}.eyebrow.svelte-1tlx730 {color:#8e9aaa;font-size:11px;text-transform:uppercase;letter-spacing:.1em;margin:18px 4px 8px;}.chat-row.svelte-1tlx730 {display:flex;border-radius:7px;}.chat-row.active.svelte-1tlx730 {background:#2c3848;}.chat-title.svelte-1tlx730 {border:0;background:transparent;text-align:left;flex:1;min-width:0;padding:10px;text-overflow:ellipsis;overflow:hidden;white-space:nowrap;}.chat-title.svelte-1tlx730 small:where(.svelte-1tlx730) {display:block;color:#8e9aaa;font-size:11px;margin-top:4px;}.delete.svelte-1tlx730 {background:transparent;border:0;color:#8e9aaa;padding:8px;}.history-footer.svelte-1tlx730 {margin-top:auto;padding-top:22px;display:grid;gap:8px;}.model.svelte-1tlx730 {overflow:hidden;text-overflow:ellipsis;color:#a5b2c2;font-size:12px;}.conversation.svelte-1tlx730 {display:flex;flex-direction:column;min-height:0;}.context.svelte-1tlx730 {padding:13px 20px;border-bottom:1px solid #343a44;font-size:12px;color:#a5b2c2;}.context-dot.svelte-1tlx730 {display:inline-block;width:6px;height:6px;border-radius:100%;background:#76c4aa;margin-right:6px;}.messages.svelte-1tlx730 {flex:1;overflow:auto;padding:24px 30px;}.empty-state.svelte-1tlx730 {max-width:550px;margin:45px auto;text-align:center;color:#a5b2c2;}h2.svelte-1tlx730 {color:#ecf0f6;font-size:24px;letter-spacing:-.03em;}.assistant-mark.svelte-1tlx730 {font-size:34px;color:#a9c9ff;}.suggestions.svelte-1tlx730 {display:grid;gap:9px;margin-top:24px;text-align:left;}.suggestions.svelte-1tlx730 button:where(.svelte-1tlx730) {text-align:left;background:#242b34;}.message.svelte-1tlx730 {padding:18px 0 24px;border-bottom:1px solid #30363f;}.message.user.svelte-1tlx730 {background:#252d38;border:0;border-radius:9px;padding:16px 20px;margin:12px 0;}.message.failed.svelte-1tlx730 {border-left:2px solid #dc8188;padding-left:14px;}.message-heading.svelte-1tlx730 {display:flex;gap:14px;align-items:center;color:#b9c5d6;font-size:12px;margin-bottom:12px;}.message-heading.svelte-1tlx730 strong:where(.svelte-1tlx730) {color:#e8edf5;}.message-heading.svelte-1tlx730 button:where(.svelte-1tlx730) {margin-left:auto;border:0;background:transparent;padding:3px;color:#8e9aaa;font-size:11px;}.proposal.svelte-1tlx730 {display:flex;gap:16px;align-items:center;justify-content:space-between;background:#263546;border:1px solid #405d7c;border-radius:8px;padding:14px;margin-top:16px;}.proposal.svelte-1tlx730 div:where(.svelte-1tlx730) {display:grid;gap:5px;}.proposal.svelte-1tlx730 small:where(.svelte-1tlx730), .proposal.svelte-1tlx730 span:where(.svelte-1tlx730) {font-size:11px;color:#afc0d7;}.composer.svelte-1tlx730 {padding:14px 22px 18px;border-top:1px solid #343a44;background:#1b2026;}.attachment.svelte-1tlx730 {display:flex;gap:12px;align-items:center;font-size:11px;color:#a5b2c2;margin-bottom:10px;}.attachment.svelte-1tlx730 select:where(.svelte-1tlx730) {padding:5px 8px;max-width:400px;font-size:12px;}.input-box.svelte-1tlx730 {border:1px solid #475262;background:#242b34;border-radius:10px;padding:10px 12px;}textarea.svelte-1tlx730 {resize:vertical;min-height:65px;max-height:200px;padding:6px;width:100%;box-sizing:border-box;border:0;background:transparent;font-family:inherit;color:inherit;font-size:14px;}textarea.svelte-1tlx730:focus {outline:none;}.composer-actions.svelte-1tlx730 {display:flex;align-items:center;justify-content:space-between;gap:10px;}.composer-actions.svelte-1tlx730 small:where(.svelte-1tlx730) {color:#8e9aaa;font-size:11px;}.muted.svelte-1tlx730 {color:#8e9aaa;}.inline-error.svelte-1tlx730 {padding:10px;color:#ffb4bb;background:#41262c;border-radius:6px;margin-bottom:10px;}\r\n  @media (max-width: 1000px) {.assistant-layout.svelte-1tlx730 {grid-template-columns:180px minmax(0, 1fr);}.messages.svelte-1tlx730 {padding:16px;}.context.svelte-1tlx730 .muted:where(.svelte-1tlx730) {display:none;} }\r\n  @media (max-width: 700px) {.assistant-layout.svelte-1tlx730 {grid-template-columns:1fr;height:calc(100vh - 180px);min-height:600px;}.history.svelte-1tlx730 {max-height:150px;border-right:0;border-bottom:1px solid #343a44;}.history-footer.svelte-1tlx730, .history.svelte-1tlx730 .eyebrow:where(.svelte-1tlx730) {display:none;}.conversation.svelte-1tlx730 {min-height:480px;}.attachment.svelte-1tlx730 select:where(.svelte-1tlx730) {max-width:100%;}.composer.svelte-1tlx730 {padding:10px;}.proposal.svelte-1tlx730 {flex-direction:column;align-items:flex-start;}.attachment.svelte-1tlx730 {flex-wrap:wrap;}.composer-actions.svelte-1tlx730 small:where(.svelte-1tlx730) {max-width:55%;} }"
  };
  function Assistant($$anchor, $$props) {
    push($$props, true);
    append_styles($$anchor, $$css9);
    let chats = state(proxy([]));
    let messages = state(proxy([]));
    let activeId = state("");
    let input = state("");
    let error = state("");
    let loading = state(true);
    let busy = state(false);
    let ready = state(false);
    let model = state("");
    let taskId = state("");
    let tasks = state(proxy([]));
    let status = state("");
    let copied = state("");
    let scroll;
    let follow = true;
    let controller = null;
    let generation = 0;
    const suggestions = [
      "\u0427\u0442\u043E \u0441\u0435\u0439\u0447\u0430\u0441 \u0441\u043E \u0437\u0434\u043E\u0440\u043E\u0432\u044C\u0435\u043C \u0441\u0435\u0440\u0432\u0438\u0441\u0430?",
      "\u041F\u043E\u043C\u043E\u0433\u0438 \u043D\u0430\u0441\u0442\u0440\u043E\u0438\u0442\u044C \u0441\u0435\u0440\u0432\u0438\u0441 \u0434\u043B\u044F \u0437\u0430\u043A\u0440\u044B\u0442\u043E\u0433\u043E \u043F\u0438\u043B\u043E\u0442\u0430.",
      "\u041D\u0430\u0439\u0434\u0438 \u0437\u0430\u0434\u0430\u0447\u0443 \u0438 \u043F\u0440\u0435\u0434\u043B\u043E\u0436\u0438 \u0443\u043B\u0443\u0447\u0448\u0435\u043D\u0438\u044F \u0435\u0451 \u0442\u0435\u0441\u0442\u043E\u0432."
    ];
    async function init2() {
      set(loading, true);
      set(error, "");
      const results = await Promise.allSettled([getSettings(), listChats(), getCatalog()]);
      const config = results[0];
      const history2 = results[1];
      const catalog = results[2];
      if (config.status === "fulfilled") {
        set(ready, config.value.config.ai_enabled && !!config.value.config.ai_base_url && !!config.value.config.ai_model, true);
        set(model, config.value.config.ai_model, true);
      } else set(
        error,
        config.reason instanceof Error ? config.reason.message : "\u041D\u0435 \u0443\u0434\u0430\u043B\u043E\u0441\u044C \u0437\u0430\u0433\u0440\u0443\u0437\u0438\u0442\u044C \u043D\u0430\u0441\u0442\u0440\u043E\u0439\u043A\u0438 AI.",
        true
      );
      if (history2.status === "fulfilled") set(chats, history2.value, true);
      else set(
        error,
        history2.reason instanceof Error ? history2.reason.message : "\u041D\u0435 \u0443\u0434\u0430\u043B\u043E\u0441\u044C \u0437\u0430\u0433\u0440\u0443\u0437\u0438\u0442\u044C \u0434\u0438\u0430\u043B\u043E\u0433\u0438.",
        true
      );
      if (catalog.status === "fulfilled") set(tasks, catalog.value.projects.flatMap((p) => p.folders.flatMap((f) => f.tasks)), true);
      set(loading, false);
      if (get2(chats).length && !get2(activeId)) await select(get2(chats)[0].id);
    }
    async function select(id) {
      if (get2(busy)) return;
      const request2 = ++generation;
      set(error, "");
      set(loading, true);
      try {
        const data = await readChat(id);
        if (request2 !== generation) return;
        set(activeId, id, true);
        set(messages, data.messages, true);
        follow = true;
      } catch (e) {
        if (request2 === generation) set(error, e.message, true);
      } finally {
        if (request2 === generation) set(loading, false);
      }
    }
    async function create() {
      if (get2(busy) || get2(loading)) return;
      set(error, "");
      set(loading, true);
      try {
        const chat = await newChat();
        set(chats, [chat, ...get2(chats)], true);
        set(activeId, chat.id, true);
        set(messages, [], true);
        set(input, "");
        set(taskId, "");
        follow = true;
      } catch (e) {
        set(error, e.message, true);
      } finally {
        set(loading, false);
      }
    }
    async function remove(chat) {
      if (get2(busy) || !confirm(`\u0423\u0434\u0430\u043B\u0438\u0442\u044C \u0434\u0438\u0430\u043B\u043E\u0433 \xAB${chat.title}\xBB?`)) return;
      try {
        await deleteChat(chat.id);
        set(chats, get2(chats).filter((c) => c.id !== chat.id), true);
        if (get2(activeId) === chat.id) {
          set(activeId, "");
          set(messages, [], true);
          if (get2(chats).length) await select(get2(chats)[0].id);
        }
      } catch (e) {
        set(error, e.message, true);
      }
    }
    async function send(text2 = get2(input)) {
      if (get2(busy) || !get2(ready) || !text2.trim()) return;
      if (!get2(activeId)) {
        await create();
        if (!get2(activeId)) return;
      }
      const id = get2(activeId);
      const content = text2.trim();
      set(busy, true);
      set(status, "\u041F\u043E\u0434\u043A\u043B\u044E\u0447\u0430\u044E\u0441\u044C\u2026");
      set(error, "");
      follow = true;
      controller = new AbortController();
      const user = {
        id: `local-user-${Date.now()}`,
        role: "user",
        content,
        status: "complete",
        created_at: (/* @__PURE__ */ new Date()).toISOString(),
        proposals: []
      };
      let assistant = {
        id: "pending",
        role: "assistant",
        content: "",
        status: "streaming",
        created_at: (/* @__PURE__ */ new Date()).toISOString(),
        proposals: []
      };
      set(messages, [...get2(messages), user, assistant], true);
      set(input, "");
      try {
        await streamChat(id, content, get2(taskId) || void 0, controller.signal, (kind, data) => {
          if (kind === "start") {
            assistant = { ...assistant, id: String(data.message_id) };
            set(status, "\u041F\u0438\u0448\u0435\u0442 \u043E\u0442\u0432\u0435\u0442\u2026");
          }
          if (kind === "delta") assistant = {
            ...assistant,
            content: assistant.content + String(data.text || "")
          };
          if (kind === "tool") set(status, `\u0427\u0438\u0442\u0430\u0435\u0442 \u0434\u0430\u043D\u043D\u044B\u0435: ${String(data.name)}`);
          if (kind === "proposal") assistant = { ...assistant, proposals: [...assistant.proposals, data] };
          if (kind === "done") assistant = { ...assistant, status: String(data.status) };
          if (kind === "error") {
            set(error, String(data.message), true);
            assistant = { ...assistant, status: "error" };
          }
          set(messages, [...get2(messages).slice(0, -1), assistant], true);
        });
      } catch (e) {
        if (e.name === "AbortError") set(status, "\u041E\u0442\u0432\u0435\u0442 \u043E\u0441\u0442\u0430\u043D\u043E\u0432\u043B\u0435\u043D");
        else {
          set(error, e.message, true);
          set(input, content, true);
        }
      } finally {
        controller = null;
        try {
          for (let attempt = 0; attempt < 15; attempt++) {
            const data = await readChat(id);
            if (get2(activeId) === id) set(messages, data.messages, true);
            if (!data.messages.some((message) => message.status === "streaming")) break;
            await new Promise((resolve) => setTimeout(resolve, 100));
          }
          set(chats, await listChats(), true);
        } catch (e) {
          if (!get2(error)) set(error, e.message, true);
        }
        if (!get2(status).includes("\u043E\u0441\u0442\u0430\u043D\u043E\u0432\u043B\u0435\u043D")) set(status, "");
        set(busy, false);
      }
    }
    function stop() {
      controller?.abort();
    }
    function keydown(e) {
      if (e.key === "Enter" && !e.shiftKey && !e.isComposing) {
        e.preventDefault();
        void send();
      }
    }
    function review(proposal) {
      if (proposal.kind === "settings") $$props.onReviewSettings(proposal.payload);
      else $$props.onReviewTask(proposal.payload);
    }
    async function copy(message) {
      try {
        await navigator.clipboard.writeText(message.content);
        set(copied, message.id, true);
      } catch {
        set(error, "\u041D\u0435 \u0443\u0434\u0430\u043B\u043E\u0441\u044C \u0441\u043A\u043E\u043F\u0438\u0440\u043E\u0432\u0430\u0442\u044C \u043E\u0442\u0432\u0435\u0442.");
      }
    }
    user_effect(() => {
      get2(messages).map((m) => m.content.length + m.proposals.length).join(",");
      if (follow) void tick().then(() => {
        if (scroll) scroll.scrollTop = scroll.scrollHeight;
      });
    });
    onMount(() => {
      void init2();
    });
    onDestroy(() => {
      generation++;
      controller?.abort();
    });
    var div = root_125();
    var aside = child(div);
    var button = child(aside);
    var node = sibling(button, 4);
    each(node, 17, () => get2(chats), (chat) => chat.id, ($$anchor2, chat) => {
      var div_1 = root9();
      let classes;
      var button_1 = child(div_1);
      var text_1 = child(button_1, true);
      var small = sibling(text_1);
      var text_2 = only_child(small, true);
      reset(button_1);
      var button_2 = sibling(button_1, 2);
      reset(div_1);
      template_effect(
        ($0) => {
          classes = set_class(div_1, 1, "chat-row svelte-1tlx730", null, classes, { active: get2(chat).id === get2(activeId) });
          button_1.disabled = get2(busy) || get2(loading);
          set_attribute2(button_1, "title", get2(chat).title);
          set_text(text_1, get2(chat).title);
          set_text(text_2, $0);
          button_2.disabled = get2(busy) || get2(loading);
          set_attribute2(button_2, "aria-label", `\u0423\u0434\u0430\u043B\u0438\u0442\u044C ${get2(chat).title}`);
        },
        [
          () => new Date(get2(chat).updated_at).toLocaleDateString("ru")
        ]
      );
      delegated("click", button_1, () => select(get2(chat).id));
      delegated("click", button_2, () => remove(get2(chat)));
      append($$anchor2, div_1);
    });
    var node_1 = sibling(node, 2);
    {
      var consequent = ($$anchor2) => {
        var p_1 = root_115();
        append($$anchor2, p_1);
      };
      if_block(node_1, ($$render) => {
        if (!get2(chats).length && !get2(loading)) $$render(consequent);
      });
    }
    var div_2 = sibling(node_1, 2);
    var span = child(div_2);
    var text_3 = only_child(span, true);
    var button_3 = sibling(span);
    reset(div_2);
    reset(aside);
    var section = sibling(aside, 2);
    var div_3 = sibling(child(section), 2);
    var node_2 = child(div_3);
    {
      var consequent_1 = ($$anchor2) => {
        var p_2 = root_211();
        append($$anchor2, p_2);
      };
      if_block(node_2, ($$render) => {
        if (get2(loading)) $$render(consequent_1);
      });
    }
    var node_3 = sibling(node_2, 2);
    {
      var consequent_2 = ($$anchor2) => {
        var div_4 = root_39();
        var button_4 = sibling(child(div_4), 2);
        reset(div_4);
        delegated("click", button_4, function(...$$args) {
          $$props.onSettings?.apply(this, $$args);
        });
        append($$anchor2, div_4);
      };
      var consequent_3 = ($$anchor2) => {
        var div_5 = root_57();
        var div_6 = sibling(child(div_5), 3);
        each(div_6, 21, () => suggestions, index, ($$anchor3, suggestion) => {
          var button_5 = root_48();
          var text_4 = only_child(button_5, true);
          template_effect(() => set_text(text_4, get2(suggestion)));
          delegated("click", button_5, () => send(get2(suggestion)));
          append($$anchor3, button_5);
        });
        reset(div_6);
        reset(div_5);
        append($$anchor2, div_5);
      };
      if_block(node_3, ($$render) => {
        if (!get2(ready) && !get2(loading)) $$render(consequent_2);
        else if (!get2(messages).length && !get2(loading)) $$render(consequent_3, 1);
      });
    }
    var node_4 = sibling(node_3, 2);
    each(node_4, 17, () => get2(messages), (message) => message.id, ($$anchor2, message) => {
      var article = root_75();
      let classes_1;
      var div_7 = child(article);
      var strong = child(div_7);
      var text_5 = only_child(strong, true);
      var span_1 = sibling(strong);
      var text_6 = only_child(span_1, true);
      var node_5 = sibling(span_1);
      {
        var consequent_4 = ($$anchor3) => {
          var button_6 = root_48();
          var text_7 = only_child(button_6, true);
          template_effect(() => set_text(text_7, get2(copied) === get2(message).id ? "\u0421\u043A\u043E\u043F\u0438\u0440\u043E\u0432\u0430\u043D\u043E" : "\u041A\u043E\u043F\u0438\u0440\u043E\u0432\u0430\u0442\u044C"));
          delegated("click", button_6, () => copy(get2(message)));
          append($$anchor3, button_6);
        };
        if_block(node_5, ($$render) => {
          if (get2(message).content) $$render(consequent_4);
        });
      }
      reset(div_7);
      var node_6 = sibling(div_7, 2);
      {
        let $0 = user_derived(() => get2(message).content || (get2(busy) ? "\u2026" : "\u041E\u0442\u0432\u0435\u0442 \u043D\u0435 \u0437\u0430\u0432\u0435\u0440\u0448\u0451\u043D. \u041C\u043E\u0436\u043D\u043E \u043F\u043E\u0432\u0442\u043E\u0440\u0438\u0442\u044C \u0437\u0430\u043F\u0440\u043E\u0441."));
        ChatContent(node_6, {
          get content() {
            return get2($0);
          }
        });
      }
      var node_7 = sibling(node_6, 2);
      each(node_7, 17, () => get2(message).proposals, (proposal) => proposal.id, ($$anchor3, proposal) => {
        var div_8 = root_65();
        var div_9 = child(div_8);
        var strong_1 = sibling(child(div_9));
        var text_8 = only_child(strong_1, true);
        var span_2 = sibling(strong_1);
        var text_9 = only_child(span_2, true);
        reset(div_9);
        var button_7 = sibling(div_9);
        reset(div_8);
        template_effect(() => {
          set_text(text_8, get2(proposal).title);
          set_text(text_9, get2(proposal).kind === "settings" ? "\u041D\u0430\u0441\u0442\u0440\u043E\u0439\u043A\u0438 \u0441\u0435\u0440\u0432\u0438\u0441\u0430" : "\u0421\u043E\u0434\u0435\u0440\u0436\u0438\u043C\u043E\u0435 \u0437\u0430\u0434\u0430\u0447\u0438");
          button_7.disabled = get2(busy) || get2(loading);
        });
        delegated("click", button_7, () => review(get2(proposal)));
        append($$anchor3, div_8);
      });
      reset(article);
      template_effect(() => {
        classes_1 = set_class(article, 1, "message svelte-1tlx730", null, classes_1, {
          user: get2(message).role === "user",
          failed: get2(message).status === "error"
        });
        set_text(text_5, get2(message).role === "user" ? "\u0422\u044B" : "\u041F\u043E\u043C\u043E\u0449\u043D\u0438\u043A");
        set_text(text_6, get2(message).role === "assistant" && get2(message).status !== "complete" ? {
          streaming: "\u041E\u0442\u0432\u0435\u0447\u0430\u0435\u0442\u2026",
          interrupted: "\u041E\u0442\u0432\u0435\u0442 \u043E\u0441\u0442\u0430\u043D\u043E\u0432\u043B\u0435\u043D",
          truncated: "\u0414\u043E\u0441\u0442\u0438\u0433\u043D\u0443\u0442 \u043B\u0438\u043C\u0438\u0442 \u043E\u0442\u0432\u0435\u0442\u0430",
          error: "\u041E\u0448\u0438\u0431\u043A\u0430"
        }[get2(message).status] || get2(message).status : "");
      });
      append($$anchor2, article);
    });
    reset(div_3);
    bind_this(div_3, ($$value) => scroll = $$value, () => scroll);
    var div_10 = sibling(div_3, 2);
    var node_8 = child(div_10);
    {
      var consequent_5 = ($$anchor2) => {
        var div_11 = root_85();
        var text_10 = only_child(div_11, true);
        template_effect(() => set_text(text_10, get2(error)));
        append($$anchor2, div_11);
      };
      if_block(node_8, ($$render) => {
        if (get2(error)) $$render(consequent_5);
      });
    }
    var label = sibling(node_8, 2);
    var select_1 = sibling(child(label));
    var option = child(select_1);
    option.value = option.__value = "";
    var node_9 = sibling(option);
    each(node_9, 17, () => get2(tasks), (task) => task.id, ($$anchor2, task) => {
      var option_1 = root_95();
      var text_11 = only_child(option_1);
      var option_1_value = {};
      template_effect(() => {
        set_text(text_11, `${get2(task).task_id ?? ""} \xB7 ${get2(task).title ?? ""}`);
        if (option_1_value !== (option_1_value = get2(task).id)) {
          option_1.value = (option_1.__value = option_1_value) ?? "";
        }
      });
      append($$anchor2, option_1);
    });
    reset(select_1);
    init_select(select_1);
    reset(label);
    var div_12 = sibling(label, 2);
    var textarea = child(div_12);
    remove_textarea_child(textarea);
    var div_13 = sibling(textarea);
    var small_1 = child(div_13);
    var text_12 = only_child(small_1, true);
    var node_10 = sibling(small_1);
    {
      var consequent_6 = ($$anchor2) => {
        var button_8 = root_105();
        delegated("click", button_8, stop);
        append($$anchor2, button_8);
      };
      var alternate = ($$anchor2) => {
        var button_9 = root_116();
        template_effect(($0) => button_9.disabled = $0, [
          () => !get2(ready) || get2(loading) || !get2(input).trim()
        ]);
        delegated("click", button_9, () => send());
        append($$anchor2, button_9);
      };
      if_block(node_10, ($$render) => {
        if (get2(busy)) $$render(consequent_6);
        else $$render(alternate, -1);
      });
    }
    reset(div_13);
    reset(div_12);
    reset(div_10);
    reset(section);
    reset(div);
    template_effect(() => {
      button.disabled = get2(busy) || get2(loading);
      set_attribute2(span, "title", get2(model));
      set_text(text_3, get2(model) || "AI \u043D\u0435 \u043F\u043E\u0434\u043A\u043B\u044E\u0447\u0451\u043D");
      select_1.disabled = get2(busy) || get2(loading);
      textarea.disabled = !get2(ready) || get2(loading);
      set_text(text_12, get2(busy) ? get2(status) : "Enter \u2014 \u043E\u0442\u043F\u0440\u0430\u0432\u0438\u0442\u044C \xB7 Shift+Enter \u2014 \u043D\u043E\u0432\u0430\u044F \u0441\u0442\u0440\u043E\u043A\u0430");
    });
    delegated("click", button, create);
    delegated("click", button_3, function(...$$args) {
      $$props.onSettings?.apply(this, $$args);
    });
    event("scroll", div_3, () => {
      if (scroll) follow = scroll.scrollHeight - scroll.scrollTop - scroll.clientHeight < 100;
    });
    bind_select_value(select_1, () => get2(taskId), ($$value) => set(taskId, $$value));
    delegated("keydown", textarea, keydown);
    bind_value(textarea, () => get2(input), ($$value) => set(input, $$value));
    append($$anchor, div);
    pop();
  }
  delegate(["click", "keydown"]);

  // src/App.svelte
  var root10 = from_html(`<div class="boot svelte-1n46o8q">\u041F\u0440\u043E\u0432\u0435\u0440\u044F\u044E \u0441\u0435\u0441\u0441\u0438\u044E\u2026</div>`);
  var root_117 = from_html(`<p class="auth-error svelte-1n46o8q" role="alert"> </p>`);
  var root_212 = from_html(`<!><!>`, 1);
  var root_310 = from_html(`<p class="nav-caption svelte-1n46o8q">\u0410\u0434\u043C\u0438\u043D\u0438\u0441\u0442\u0440\u0438\u0440\u043E\u0432\u0430\u043D\u0438\u0435</p><button><span class="svelte-1n46o8q">\u2726</span> AI-\u043F\u043E\u043C\u043E\u0449\u043D\u0438\u043A</button><button><span class="svelte-1n46o8q">\u2699</span> \u041D\u0430\u0441\u0442\u0440\u043E\u0439\u043A\u0438</button>`, 1);
  var root_49 = from_html(`<span class="unsaved svelte-1n46o8q">\u25CF \u041D\u0435\u0441\u043E\u0445\u0440\u0430\u043D\u0451\u043D\u043D\u044B\u0435 \u0438\u0437\u043C\u0435\u043D\u0435\u043D\u0438\u044F</span>`);
  var root_58 = from_html(`<span class="online svelte-1n46o8q">\u25CF</span> \u0421\u0435\u0440\u0432\u0438\u0441 \u0434\u043E\u0441\u0442\u0443\u043F\u0435\u043D`, 1);
  var root_66 = from_html(`<main class="shell svelte-1n46o8q"><aside class="sidebar svelte-1n46o8q"><div class="brand svelte-1n46o8q"><span class="logo svelte-1n46o8q">e</span><div><strong class="svelte-1n46o8q"> </strong><small class="svelte-1n46o8q">\u041F\u0430\u043D\u0435\u043B\u044C \u0443\u043F\u0440\u0430\u0432\u043B\u0435\u043D\u0438\u044F</small></div></div> <p class="nav-caption svelte-1n46o8q">\u0420\u0430\u0431\u043E\u0447\u0435\u0435 \u043F\u0440\u043E\u0441\u0442\u0440\u0430\u043D\u0441\u0442\u0432\u043E</p><nav aria-label="\u041D\u0430\u0432\u0438\u0433\u0430\u0446\u0438\u044F \u0430\u0434\u043C\u0438\u043D\u043A\u0438" class="svelte-1n46o8q"><button><span class="svelte-1n46o8q">\u25EB</span> \u041E\u0431\u0437\u043E\u0440</button> <button><span class="svelte-1n46o8q">\u2659</span> \u041F\u043E\u043B\u044C\u0437\u043E\u0432\u0430\u0442\u0435\u043B\u0438</button> <button><span class="svelte-1n46o8q">\u25A4</span> \u041A\u0430\u0442\u0430\u043B\u043E\u0433 \u0437\u0430\u0434\u0430\u0447</button> <!></nav> <div class="account svelte-1n46o8q"><strong> </strong><small class="svelte-1n46o8q"> </small><button class="svelte-1n46o8q">\u0412\u044B\u0439\u0442\u0438 \u0438\u0437 \u0430\u043A\u043A\u0430\u0443\u043D\u0442\u0430</button></div></aside> <section class="workspace svelte-1n46o8q"><header class="page-header svelte-1n46o8q"><div><p class="eyebrow svelte-1n46o8q"> </p><h1 class="svelte-1n46o8q"> </h1></div><div class="header-status svelte-1n46o8q"><!></div></header> <div class="page-body svelte-1n46o8q"><!></div></section></main>`);
  var root_76 = from_html(`<!> <!>`, 1);
  var $$css10 = {
    hash: "svelte-1n46o8q",
    code: "html, body {margin:0;min-height:100%;background:#171b21;color:#dce3ed;font:14px/1.5 'Segoe UI', system-ui, sans-serif;}* {box-sizing:border-box;}button, input, select, textarea {font:inherit;}button {padding:8px 12px;border:1px solid #3b4654;border-radius:6px;background:#252d38;color:#dce3ed;cursor:pointer;}button:hover:not(:disabled) {border-color:#8cbaff;background:#2d394b;}button:disabled {opacity:.5;cursor:not-allowed;}button.primary {background:#aac9fb;color:#13223b;border-color:#aac9fb;font-weight:600;}button.primary:hover:not(:disabled) {background:#c1d8ff;}input, select, textarea {background:#202731;color:#e7edf6;border:1px solid #3b4654;border-radius:6px;padding:10px 12px;}input:focus, select:focus, textarea:focus {outline:2px solid #8cbaff;outline-offset:1px;}.shell.svelte-1n46o8q {display:grid;grid-template-columns:224px minmax(0, 1fr);min-height:100vh;}.shell[hidden].svelte-1n46o8q {display:none;}.sidebar.svelte-1n46o8q {position:sticky;top:0;height:100vh;background:#191e26;border-right:1px solid #303946;display:flex;flex-direction:column;padding:26px 16px 18px;}.brand.svelte-1n46o8q {display:flex;gap:10px;align-items:center;padding:0 8px 30px;}.brand.svelte-1n46o8q strong:where(.svelte-1n46o8q) {font-size:15px;letter-spacing:-.02em;display:block;}.brand.svelte-1n46o8q small:where(.svelte-1n46o8q) {color:#8e9aaa;font-size:11px;}.logo.svelte-1n46o8q {font-size:24px;line-height:36px;width:36px;text-align:center;color:#18283f;background:#aac9fb;font-weight:700;border-radius:10px;}.nav-caption.svelte-1n46o8q {font-size:10px;text-transform:uppercase;letter-spacing:.1em;color:#7f8a9c;padding:0 10px;margin:8px 0 12px;}nav.svelte-1n46o8q {display:grid;gap:5px;}nav.svelte-1n46o8q button:where(.svelte-1n46o8q) {display:flex;gap:11px;align-items:center;background:transparent;border-color:transparent;text-align:left;padding:11px 12px;color:#a6b3c7;}nav.svelte-1n46o8q button:where(.svelte-1n46o8q) span:where(.svelte-1n46o8q) {width:18px;font-size:17px;}nav.svelte-1n46o8q button.active:where(.svelte-1n46o8q) {background:#2c3b52;color:#d4e5ff;border-color:#405677;}nav.svelte-1n46o8q .nav-caption:where(.svelte-1n46o8q) {margin-top:25px;}.account.svelte-1n46o8q {margin-top:auto;display:grid;gap:7px;padding:18px 8px 0;border-top:1px solid #303946;}.account.svelte-1n46o8q small:where(.svelte-1n46o8q) {color:#8e9aaa;}.account.svelte-1n46o8q button:where(.svelte-1n46o8q) {margin-top:6px;font-size:11px;}.workspace.svelte-1n46o8q {min-width:0;}.page-header.svelte-1n46o8q {display:flex;justify-content:space-between;align-items:center;gap:20px;padding:22px 32px;border-bottom:1px solid #303946;}.eyebrow.svelte-1n46o8q {color:#8e9aaa;font-size:11px;margin:0 0 5px;}h1.svelte-1n46o8q {font-size:22px;letter-spacing:-.025em;margin:0;font-weight:600;}.page-body.svelte-1n46o8q {padding:26px 32px;max-width:1600px;margin:0 auto;}.header-status.svelte-1n46o8q {font-size:11px;color:#8e9aaa;white-space:nowrap;}.online.svelte-1n46o8q {color:#76c4aa;padding-right:6px;}.unsaved.svelte-1n46o8q {color:#e8b86e;}.boot.svelte-1n46o8q {text-align:center;padding:20vh 20px;color:#a6b3c7;}.auth-error.svelte-1n46o8q {color:#ffb4bb;text-align:center;margin:25px 20px 0;}\r\n  @media (max-width: 1000px) {.shell.svelte-1n46o8q {grid-template-columns:190px minmax(0, 1fr);}.page-body.svelte-1n46o8q, .page-header.svelte-1n46o8q {padding:20px;}.header-status.svelte-1n46o8q {display:none;} }\r\n  @media (max-width: 700px) {.shell.svelte-1n46o8q {display:block;}.sidebar.svelte-1n46o8q {height:auto;position:static;padding:14px;border-right:0;border-bottom:1px solid #303946;}.brand.svelte-1n46o8q {padding-bottom:12px;}nav.svelte-1n46o8q {display:flex;flex-wrap:wrap;gap:4px;}nav.svelte-1n46o8q button:where(.svelte-1n46o8q) {padding:8px;font-size:12px;}.nav-caption.svelte-1n46o8q, nav.svelte-1n46o8q .nav-caption:where(.svelte-1n46o8q), .account.svelte-1n46o8q small:where(.svelte-1n46o8q) {display:none;}.account.svelte-1n46o8q {margin-top:10px;display:flex;justify-content:space-between;align-items:center;padding-top:10px;}.account.svelte-1n46o8q button:where(.svelte-1n46o8q) {margin-top:0;}.page-header.svelte-1n46o8q {padding:18px 14px;}.page-body.svelte-1n46o8q {padding:14px;}h1.svelte-1n46o8q {font-size:20px;} }"
  };
  function App($$anchor, $$props) {
    push($$props, true);
    append_styles($$anchor, $$css10);
    const titles = {
      overview: "\u041E\u0431\u0437\u043E\u0440 \u0441\u0435\u0440\u0432\u0438\u0441\u0430",
      students: "\u041F\u043E\u043B\u044C\u0437\u043E\u0432\u0430\u0442\u0435\u043B\u0438",
      catalog: "\u041A\u0430\u0442\u0430\u043B\u043E\u0433 \u0437\u0430\u0434\u0430\u0447",
      settings: "\u041D\u0430\u0441\u0442\u0440\u043E\u0439\u043A\u0438 \u0441\u0435\u0440\u0432\u0438\u0441\u0430",
      assistant: "AI-\u043F\u043E\u043C\u043E\u0449\u043D\u0438\u043A"
    };
    let view = state(proxy(Object.keys(titles).includes(location.hash.slice(1)) ? location.hash.slice(1) : "overview"));
    let loggedIn = state(false);
    let sessionSeen = state(false);
    let checking = state(true);
    let userRole = state("");
    let username = state("");
    let userId = state("");
    let authError = state("");
    let serviceName = state("Ego Trainer");
    let version = state("");
    let dirty = state(false);
    let workBusy = state(false);
    let selectedStudent = state(null);
    let selectedTask = state(null);
    let settingsDraft = state(null);
    let taskDraft = state(null);
    const isAdmin = user_derived(() => get2(userRole) === "admin");
    async function brand() {
      if (get2(userRole) !== "admin") return;
      try {
        const data = await getSettings();
        saved(data);
      } catch {
      }
    }
    function saved(data) {
      set(serviceName, data.config.service_name, true);
      set(version, data.runtime.version, true);
    }
    function accept(data) {
      if (data.role === "student") {
        setToken(null);
        set(authError, "\u0410\u0434\u043C\u0438\u043D\u043A\u0430 \u0434\u043E\u0441\u0442\u0443\u043F\u043D\u0430 \u043D\u0430\u0441\u0442\u0430\u0432\u043D\u0438\u043A\u0430\u043C \u0438 \u0430\u0434\u043C\u0438\u043D\u0438\u0441\u0442\u0440\u0430\u0442\u043E\u0440\u0430\u043C.");
        return;
      }
      if (get2(userId) && get2(userId) !== data.user_id) {
        set(selectedTask, null);
        set(selectedStudent, null);
        set(taskDraft, null);
        set(settingsDraft, null);
        set(dirty, false);
        set(view, "overview");
      }
      set(userId, data.user_id, true);
      set(username, data.username, true);
      set(userRole, data.role, true);
      set(authError, "");
      set(loggedIn, true);
      set(sessionSeen, true);
      if (get2(userRole) !== "admin" && (get2(view) === "settings" || get2(view) === "assistant")) set(view, "overview");
      void brand();
    }
    async function restoreSession() {
      try {
        if (getToken()) accept(await me());
      } catch {
        setToken(null);
      } finally {
        set(checking, false);
      }
    }
    function handleLogin(data) {
      if (data.role !== "student") setToken(data.access_token);
      accept(data);
    }
    function navTo(next2) {
      if (get2(workBusy)) return false;
      if (get2(dirty) && !confirm("\u0415\u0441\u0442\u044C \u043D\u0435\u0441\u043E\u0445\u0440\u0430\u043D\u0451\u043D\u043D\u044B\u0435 \u0438\u0437\u043C\u0435\u043D\u0435\u043D\u0438\u044F. \u041F\u0435\u0440\u0435\u0439\u0442\u0438 \u0438 \u043E\u0442\u0431\u0440\u043E\u0441\u0438\u0442\u044C \u0438\u0445?")) return false;
      set(dirty, false);
      set(view, next2, true);
      set(selectedStudent, null);
      set(selectedTask, null);
      set(settingsDraft, null);
      set(taskDraft, null);
      history.replaceState(null, "", "#" + next2);
      return true;
    }
    function logout() {
      if (!navTo("overview")) return;
      setToken(null);
      set(loggedIn, false);
      set(sessionSeen, false);
      set(userRole, "");
      set(username, "");
      set(userId, "");
    }
    function reviewSettings(draft) {
      if (navTo("settings")) set(settingsDraft, draft, true);
    }
    function reviewTask(draft) {
      if (navTo("catalog")) {
        set(selectedTask, { id: draft.task_id, task_id: draft.task_id }, true);
        set(taskDraft, draft, true);
      }
    }
    function sessionExpired() {
      if (get2(loggedIn)) {
        set(loggedIn, false);
        set(authError, "\u0421\u0435\u0441\u0441\u0438\u044F \u0438\u0441\u0442\u0435\u043A\u043B\u0430. \u0412\u043E\u0439\u0434\u0438 \u0441\u043D\u043E\u0432\u0430 \u2014 \u043E\u0442\u043A\u0440\u044B\u0442\u044B\u0439 \u0447\u0435\u0440\u043D\u043E\u0432\u0438\u043A \u0441\u043E\u0445\u0440\u0430\u043D\u0451\u043D \u0432 \u044D\u0442\u043E\u0439 \u0432\u043A\u043B\u0430\u0434\u043A\u0435.");
      }
    }
    onMount(() => {
      void restoreSession();
      const beforeUnload = (e) => {
        if (get2(dirty)) {
          e.preventDefault();
          e.returnValue = "";
        }
      };
      const hashChange = () => {
        const next2 = location.hash.slice(1);
        if (next2 in titles && !navTo(next2)) history.replaceState(null, "", "#" + get2(view));
      };
      window.addEventListener("ego:session-expired", sessionExpired);
      window.addEventListener("beforeunload", beforeUnload);
      window.addEventListener("hashchange", hashChange);
      return () => {
        window.removeEventListener("ego:session-expired", sessionExpired);
        window.removeEventListener("beforeunload", beforeUnload);
        window.removeEventListener("hashchange", hashChange);
      };
    });
    var fragment = root_76();
    var node = first_child(fragment);
    {
      var consequent = ($$anchor2) => {
        var div = root10();
        append($$anchor2, div);
      };
      var consequent_2 = ($$anchor2) => {
        var fragment_1 = root_212();
        var node_1 = first_child(fragment_1);
        {
          var consequent_1 = ($$anchor3) => {
            var p = root_117();
            var text2 = only_child(p, true);
            template_effect(() => set_text(text2, get2(authError)));
            append($$anchor3, p);
          };
          if_block(node_1, ($$render) => {
            if (get2(authError)) $$render(consequent_1);
          });
        }
        var node_2 = sibling(node_1);
        Login(node_2, { onLogin: handleLogin });
        append($$anchor2, fragment_1);
      };
      if_block(node, ($$render) => {
        if (get2(checking)) $$render(consequent);
        else if (!get2(loggedIn)) $$render(consequent_2, 1);
      });
    }
    var node_3 = sibling(node, 2);
    {
      var consequent_12 = ($$anchor2) => {
        var main = root_66();
        var aside = child(main);
        var div_1 = child(aside);
        var div_2 = sibling(child(div_1));
        var strong = child(div_2);
        var text_1 = only_child(strong, true);
        next();
        reset(div_2);
        reset(div_1);
        var nav = sibling(div_1, 3);
        var button = child(nav);
        let classes;
        var button_1 = sibling(button, 2);
        let classes_1;
        var button_2 = sibling(button_1, 2);
        let classes_2;
        var node_4 = sibling(button_2, 2);
        {
          var consequent_3 = ($$anchor3) => {
            var fragment_2 = root_310();
            var button_3 = sibling(first_child(fragment_2));
            let classes_3;
            var button_4 = sibling(button_3);
            let classes_4;
            template_effect(() => {
              button_3.disabled = get2(workBusy);
              set_attribute2(button_3, "aria-current", get2(view) === "assistant" ? "page" : void 0);
              classes_3 = set_class(button_3, 1, "svelte-1n46o8q", null, classes_3, { active: get2(view) === "assistant" });
              button_4.disabled = get2(workBusy);
              set_attribute2(button_4, "aria-current", get2(view) === "settings" ? "page" : void 0);
              classes_4 = set_class(button_4, 1, "svelte-1n46o8q", null, classes_4, { active: get2(view) === "settings" });
            });
            delegated("click", button_3, () => navTo("assistant"));
            delegated("click", button_4, () => navTo("settings"));
            append($$anchor3, fragment_2);
          };
          if_block(node_4, ($$render) => {
            if (get2(isAdmin)) $$render(consequent_3);
          });
        }
        reset(nav);
        var div_3 = sibling(nav, 2);
        var strong_1 = child(div_3);
        var text_2 = only_child(strong_1, true);
        var small = sibling(strong_1);
        var text_3 = only_child(small);
        var button_5 = sibling(small);
        reset(div_3);
        reset(aside);
        var section = sibling(aside, 2);
        var header = child(section);
        var div_4 = child(header);
        var p_1 = child(div_4);
        var text_4 = only_child(p_1, true);
        var h1 = sibling(p_1);
        var text_5 = only_child(h1, true);
        reset(div_4);
        var div_5 = sibling(div_4);
        var node_5 = child(div_5);
        {
          var consequent_4 = ($$anchor3) => {
            var span = root_49();
            append($$anchor3, span);
          };
          var alternate = ($$anchor3) => {
            var fragment_3 = root_58();
            next();
            append($$anchor3, fragment_3);
          };
          if_block(node_5, ($$render) => {
            if (get2(dirty)) $$render(consequent_4);
            else $$render(alternate, -1);
          });
        }
        reset(div_5);
        reset(header);
        var div_6 = sibling(header, 2);
        var node_6 = child(div_6);
        {
          var consequent_5 = ($$anchor3) => {
            Overview($$anchor3, {});
          };
          var consequent_7 = ($$anchor3) => {
            var fragment_5 = comment();
            var node_7 = first_child(fragment_5);
            {
              var consequent_6 = ($$anchor4) => {
                StudentDetail($$anchor4, {
                  get studentId() {
                    return get2(selectedStudent).id;
                  },
                  get username() {
                    return get2(selectedStudent).username;
                  },
                  onBack: () => {
                    set(selectedStudent, null);
                  }
                });
              };
              var alternate_1 = ($$anchor4) => {
                StudentList($$anchor4, {
                  get userRole() {
                    return get2(userRole);
                  },
                  onSelect: (id, name) => {
                    set(selectedStudent, { id, username: name }, true);
                  }
                });
              };
              if_block(node_7, ($$render) => {
                if (get2(selectedStudent)) $$render(consequent_6);
                else $$render(alternate_1, -1);
              });
            }
            append($$anchor3, fragment_5);
          };
          var consequent_9 = ($$anchor3) => {
            var fragment_8 = comment();
            var node_8 = first_child(fragment_8);
            {
              var consequent_8 = ($$anchor4) => {
                TaskStudio($$anchor4, {
                  get taskId() {
                    return get2(selectedTask).id;
                  },
                  get taskLabel() {
                    return get2(selectedTask).task_id;
                  },
                  get role() {
                    return get2(userRole);
                  },
                  get draft() {
                    return get2(taskDraft);
                  },
                  onBusyChange: (value) => {
                    set(workBusy, value, true);
                  },
                  onDirtyChange: (value) => {
                    set(dirty, value, true);
                  },
                  onBack: () => {
                    set(dirty, false);
                    set(selectedTask, null);
                    set(taskDraft, null);
                  }
                });
              };
              var alternate_2 = ($$anchor4) => {
                Catalog($$anchor4, {
                  onSelectTask: (task) => {
                    set(selectedTask, task, true);
                  }
                });
              };
              if_block(node_8, ($$render) => {
                if (get2(selectedTask)) $$render(consequent_8);
                else $$render(alternate_2, -1);
              });
            }
            append($$anchor3, fragment_8);
          };
          var consequent_10 = ($$anchor3) => {
            Settings($$anchor3, {
              get draft() {
                return get2(settingsDraft);
              },
              onBusyChange: (value) => {
                set(workBusy, value, true);
              },
              onDirtyChange: (value) => {
                set(dirty, value, true);
              },
              onSaved: saved
            });
          };
          var consequent_11 = ($$anchor3) => {
            Assistant($$anchor3, {
              onSettings: () => navTo("settings"),
              onReviewSettings: reviewSettings,
              onReviewTask: reviewTask
            });
          };
          if_block(node_6, ($$render) => {
            if (get2(view) === "overview") $$render(consequent_5);
            else if (get2(view) === "students") $$render(consequent_7, 1);
            else if (get2(view) === "catalog") $$render(consequent_9, 2);
            else if (get2(view) === "settings" && get2(isAdmin)) $$render(consequent_10, 3);
            else if (get2(view) === "assistant" && get2(isAdmin)) $$render(consequent_11, 4);
          });
        }
        reset(div_6);
        reset(section);
        reset(main);
        template_effect(() => {
          set_attribute2(main, "hidden", !get2(loggedIn));
          set_text(text_1, get2(serviceName));
          button.disabled = get2(workBusy);
          set_attribute2(button, "aria-current", get2(view) === "overview" ? "page" : void 0);
          classes = set_class(button, 1, "svelte-1n46o8q", null, classes, { active: get2(view) === "overview" });
          button_1.disabled = get2(workBusy);
          set_attribute2(button_1, "aria-current", get2(view) === "students" ? "page" : void 0);
          classes_1 = set_class(button_1, 1, "svelte-1n46o8q", null, classes_1, { active: get2(view) === "students" });
          button_2.disabled = get2(workBusy);
          set_attribute2(button_2, "aria-current", get2(view) === "catalog" ? "page" : void 0);
          classes_2 = set_class(button_2, 1, "svelte-1n46o8q", null, classes_2, { active: get2(view) === "catalog" });
          set_text(text_2, get2(username));
          set_text(text_3, `${get2(isAdmin) ? "\u0410\u0434\u043C\u0438\u043D\u0438\u0441\u0442\u0440\u0430\u0442\u043E\u0440" : "\u041D\u0430\u0441\u0442\u0430\u0432\u043D\u0438\u043A"}${get2(version) ? ` \xB7 v${get2(version)}` : ""}`);
          button_5.disabled = get2(workBusy);
          set_text(text_4, get2(serviceName));
          set_text(text_5, get2(selectedTask) ? "\u0420\u0435\u0434\u0430\u043A\u0442\u043E\u0440 \u0437\u0430\u0434\u0430\u0447\u0438" : get2(selectedStudent) ? `\u041F\u0440\u043E\u0433\u0440\u0435\u0441\u0441: ${get2(selectedStudent).username}` : titles[get2(view)]);
        });
        delegated("click", button, () => navTo("overview"));
        delegated("click", button_1, () => navTo("students"));
        delegated("click", button_2, () => navTo("catalog"));
        delegated("click", button_5, logout);
        append($$anchor2, main);
      };
      if_block(node_3, ($$render) => {
        if (get2(sessionSeen)) $$render(consequent_12);
      });
    }
    append($$anchor, fragment);
    pop();
  }
  delegate(["click"]);

  // src/main.ts
  var target = document.getElementById("app");
  if (!target) throw new Error("#app not found");
  mount(App, { target });
})();
