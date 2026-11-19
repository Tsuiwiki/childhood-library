<script setup lang="ts">
import { computed, useId } from 'vue'

interface FilterOption {
  value: string
  label: string
}

const props = defineProps<{
  modelValue: string
  filters?: ReadonlyArray<FilterOption>
  active?: string
  placeholder?: string
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
  (e: 'update:active', value: string): void
  (e: 'reset'): void
}>()

const inputId = useId()
const hasFilters = computed(() => (props.filters?.length ?? 0) > 0)
const current = computed(() => props.active ?? 'all')

function onInput(event: Event) {
  emit('update:modelValue', (event.target as HTMLInputElement).value)
}

function resetAll() {
  emit('update:modelValue', '')
  emit('update:active', 'all')
  emit('reset')
}
</script>

<template>
  <div class="cl-filter">
    <label class="visually-hidden" :for="inputId">筛选关键词</label>
    <input
      :id="inputId"
      class="cl-filter__input"
      type="search"
      :value="modelValue"
      :placeholder="placeholder ?? '输入关键词筛选'"
      @input="onInput"
    />
    <div v-if="hasFilters" class="cl-filter__chips">
      <button
        v-for="option in filters"
        :key="option.value"
        type="button"
        class="cl-filter__chip"
        :class="{ 'is-active': current === option.value }"
        :aria-pressed="current === option.value"
        @click="emit('update:active', option.value)"
      >{{ option.label }}</button>
    </div>
    <button type="button" class="cl-filter__reset" @click="resetAll">重置</button>
  </div>
</template>

<style scoped>
/* Interaction shape from design-demos/works.html filter bar; no data bound. */
.cl-filter { display: flex; flex-wrap: wrap; align-items: center; gap: 12px; }
.cl-filter__input {
  min-height: 44px; flex: 1 1 220px;
  padding: 8px 12px; border: 2px solid var(--ink);
  background: var(--paper-light); font-size: 15px;
}
.cl-filter__chips { display: flex; flex-wrap: wrap; gap: 8px; }
.cl-filter__chip {
  min-height: 40px; padding: 6px 14px;
  border: 2px solid var(--ink); background: var(--paper-light);
  font-size: 13px; font-weight: 800;
}
.cl-filter__chip.is-active { background: var(--yellow); box-shadow: 3px 3px 0 var(--ink); }
.cl-filter__reset {
  min-height: 40px; padding: 6px 14px;
  border: 2px solid var(--ink); background: var(--paper-light);
  font-size: 13px; font-weight: 800;
}
</style>
