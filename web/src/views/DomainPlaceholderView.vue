<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { ApiClientError, isNotImplemented } from '@/api/client'
import { listDomain } from '@/api/endpoints'
import type { DomainName } from '@/api/types'

const props = defineProps<{ domain: DomainName }>()

type LoadState = 'loading' | 'not-implemented' | 'error' | 'unexpected'

const state = ref<LoadState>('loading')
const message = ref('')
const plannedFrom = ref('')

async function load(): Promise<void> {
  state.value = 'loading'
  try {
    await listDomain(props.domain)
    // No fabricated rows: a non-501 answer is surfaced as unexpected, not data.
    state.value = 'unexpected'
    message.value = '接口返回了非预期结果，未渲染任何内容'
  } catch (error) {
    if (isNotImplemented(error) && error instanceof ApiClientError) {
      state.value = 'not-implemented'
      message.value = error.message
      const details = error.data as { planned_from?: string } | null
      plannedFrom.value = details?.planned_from ?? ''
    } else {
      state.value = 'error'
      message.value = error instanceof ApiClientError ? error.message : '接口状态读取失败'
    }
  }
}

onMounted(load)
watch(() => props.domain, load)
</script>

<template>
  <section class="shell placeholder">
    <span class="eyebrow">领域占位</span>
    <h1>/{{ domain }}</h1>
    <p class="lead">
      该领域的数据模型已由 T-06 建表，但业务实现尚未接入。页面只呈现服务端的真实响应，不加载任何本地示例数据。
    </p>

    <div v-if="state === 'loading'" class="notice">正在读取接口状态…</div>
    <div v-else-if="state === 'not-implemented'" class="notice notice--warn">
      <strong>501 NOT_IMPLEMENTED</strong>
      <p>{{ message }}</p>
      <p v-if="plannedFrom">planned_from: {{ plannedFrom }}</p>
    </div>
    <div v-else class="notice notice--error">
      <strong>{{ state === 'unexpected' ? '非预期响应' : '接口不可用' }}</strong>
      <p>{{ message }}</p>
    </div>

    <RouterLink class="button" to="/">返回骨架首页</RouterLink>
  </section>
</template>

<style scoped>
.placeholder { padding-block: 64px; }
.placeholder h1 { font-family: var(--serif); font-size: clamp(34px, 5vw, 54px); font-weight: 900; }
.lead { max-width: 640px; font-size: 17px; line-height: 1.9; }
.notice { margin-bottom: 24px; padding: 18px 20px; border: var(--line); background: var(--paper-light); box-shadow: 5px 5px 0 var(--ink); }
.notice--warn { border-color: var(--red); }
.notice--error { border-color: var(--blue); }
.notice p { margin: 8px 0 0; font-size: 14px; }
</style>
