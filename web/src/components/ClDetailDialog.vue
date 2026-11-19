<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useId } from 'vue'

const props = defineProps<{ open: boolean; title: string }>()
const emit = defineEmits<{ (e: 'close'): void }>()

const dialog = ref<HTMLDialogElement | null>(null)
const titleId = useId()

function sync(open: boolean) {
  const el = dialog.value
  if (!el) return
  if (open) {
    // jsdom does not implement showModal(); keep the component testable.
    if (typeof el.showModal === 'function') el.showModal()
    else el.setAttribute('open', '')
  } else if (typeof el.close === 'function' && el.open) {
    el.close()
  } else {
    el.removeAttribute('open')
  }
}

watch(() => props.open, sync)
onMounted(() => sync(props.open))

function onCancel(event: Event) {
  // Escape must close the dialog, matching the prototype regression script.
  event.preventDefault()
  emit('close')
}

function onClose() {
  if (props.open) emit('close')
}
</script>

<template>
  <dialog
    ref="dialog"
    class="cl-dialog"
    :aria-labelledby="titleId"
    @cancel="onCancel"
    @close="onClose"
  >
    <h2 :id="titleId" class="cl-dialog__title">{{ title }}</h2>
    <div class="cl-dialog__body"><slot /></div>
    <button type="button" class="button" @click="emit('close')">关闭</button>
  </dialog>
</template>

<style scoped>
.cl-dialog {
  width: min(calc(100% - 32px), 560px);
  padding: 24px;
  border: var(--line);
  background: var(--paper-light);
  box-shadow: var(--shadow);
  color: var(--ink);
}
.cl-dialog::backdrop { background: rgba(25, 25, 23, 0.45); }
.cl-dialog__title { font-family: var(--serif); font-size: 24px; font-weight: 900; }
.cl-dialog__body { margin-bottom: 20px; font-size: 15px; line-height: 1.7; }
</style>
