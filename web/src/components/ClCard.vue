<script setup lang="ts">
export type CardTone = 'red' | 'yellow' | 'blue' | 'green' | 'brown'

withDefaults(
  defineProps<{
    title: string
    kicker?: string
    tone?: CardTone
    badge?: string
  }>(),
  { kicker: '', tone: 'blue', badge: '' },
)
</script>

<template>
  <article class="cl-card" :class="`cl-card--${tone}`">
    <span v-if="kicker" class="cl-card__kicker">{{ kicker }}</span>
    <h3 class="cl-card__title">{{ title }}</h3>
    <span v-if="badge" class="cl-card__badge">{{ badge }}</span>
    <div class="cl-card__body"><slot /></div>
    <div v-if="$slots.footer" class="cl-card__footer"><slot name="footer" /></div>
  </article>
</template>

<style scoped>
/* Lifted from design-demos/music.html L63-L75 (.spec-card) */
.cl-card {
  --tone: var(--blue);
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 18px 16px;
  border: var(--line);
  background: var(--paper-light);
  box-shadow: 5px 5px 0 var(--ink);
  text-align: left;
}
.cl-card--red { --tone: var(--red); }
.cl-card--yellow { --tone: var(--yellow); }
.cl-card--blue { --tone: var(--blue); }
.cl-card--green { --tone: var(--green); }
.cl-card--brown { --tone: var(--brown); }
.cl-card__kicker { font-size: 12px; font-weight: 900; letter-spacing: 0.1em; color: var(--tone); }
.cl-card__title { margin: 0; font-family: var(--serif); font-size: 20px; font-weight: 900; }
.cl-card__body { font-size: 14px; line-height: 1.6; color: var(--ink-soft); }
.cl-card__badge {
  position: absolute; top: -11px; right: 12px;
  padding: 1px 8px; border: 2px solid var(--ink);
  background: var(--yellow); font-size: 11px; font-weight: 800;
  transform: rotate(2deg);
}
.cl-card__footer { margin-top: auto; padding-top: 6px; font-size: 13px; font-weight: 800; }
</style>
