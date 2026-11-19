<script setup lang="ts">
import { onMounted, ref } from 'vue'
import ClCard from '@/components/ClCard.vue'
import ClFilterBar from '@/components/ClFilterBar.vue'
import ClDetailDialog from '@/components/ClDetailDialog.vue'
import { ApiClientError } from '@/api/client'
import { getHealth, getMediaCapabilities } from '@/api/endpoints'
import type { HealthData, MediaCapabilitiesData } from '@/api/types'

const health = ref<HealthData | null>(null)
const capabilities = ref<MediaCapabilitiesData | null>(null)
const statusError = ref('')

const query = ref('')
const activeFilter = ref('all')
const dialogOpen = ref(false)

const filters = [
  { value: 'all', label: '全部' },
  { value: 'music', label: '音乐馆' },
  { value: 'story', label: '故事馆' },
  { value: 'poetry', label: '古诗词馆' },
]

onMounted(async () => {
  try {
    const [h, c] = await Promise.all([getHealth(), getMediaCapabilities()])
    health.value = h.data
    capabilities.value = c.data
  } catch (error) {
    statusError.value = error instanceof ApiClientError ? error.message : '接口状态读取失败'
  }
})
</script>

<template>
  <section class="hero">
    <div class="shell">
      <span class="eyebrow">T-08 · 工程骨架</span>
      <h1>童年书房 <span style="color: var(--red)">前端工程</span></h1>
      <p class="hero-desc">
        Vue 3 + TypeScript + Vite 已就位，沿用静态原型的纸感配色与硬描边卡片。
        本页只展示工程与接口状态，<strong>不加载任何曲目、录音或权利数据</strong>。
      </p>
      <div class="hero-actions">
        <RouterLink class="button button-primary" to="/catalog">查看领域占位页</RouterLink>
        <button type="button" class="button" @click="dialogOpen = true">查看设计边界</button>
      </div>
    </div>
  </section>

  <section class="shell section-block">
    <div class="section-heading">
      <h2>三馆结构</h2>
      <p>沿用既有产品结构，仅作导航说明；正式前台内容属 T-10。</p>
    </div>
    <div class="card-grid">
      <ClCard kicker="01" title="音乐馆" tone="red" badge="规划中">
        中国经典儿歌、世界经典与原创作品的研究、采集与使用分层。
      </ClCard>
      <ClCard kicker="02" title="故事馆" tone="blue" badge="规划中">
        神话、民间故事、童话、寓言与儿童文学经典的版本溯源。
      </ClCard>
      <ClCard kicker="03" title="古诗词馆" tone="green" badge="规划中">
        唐诗、宋词、元曲与儿童诗词启蒙的注释与出处核验。
      </ClCard>
    </div>
  </section>

  <section class="shell section-block">
    <div class="section-heading">
      <h2>共享组件交互</h2>
      <p>筛选栏与详情弹窗从原型交互抽出；此处仅演示组件行为，未绑定业务数据。</p>
    </div>
    <ClFilterBar
      v-model="query"
      :filters="filters"
      :active="activeFilter"
      @update:active="activeFilter = $event"
    />
    <p class="hint">当前筛选词：{{ query || '（空）' }} ｜ 当前分类：{{ activeFilter }}</p>
  </section>

  <section class="shell section-block">
    <div class="section-heading">
      <h2>API 状态</h2>
      <p>实时读取 /healthz 与 /api/v1/media/capabilities；未连接时如实显示，不伪造数据。</p>
    </div>
    <p v-if="statusError" class="status-line status-line--error">{{ statusError }}</p>
    <div v-else-if="health" class="card-grid">
      <ClCard kicker="HEALTHZ" :title="health.service" tone="green">
        环境 {{ health.environment }} ｜ 版本 {{ health.version }} ｜
        database_sql: {{ health.checks.database_sql }}
      </ClCard>
      <ClCard kicker="T-07 MEDIA" :title="capabilities?.provider ?? 'media'" tone="brown">
        <template v-if="capabilities">
          本地对象 {{ capabilities.flat_object_count }} 个 ｜
          只读 {{ capabilities.read_only }} ｜
          签发公开 URL {{ capabilities.public_url_issued }}
        </template>
        <template v-else>能力信息尚未返回。</template>
      </ClCard>
    </div>
    <p v-else class="status-line">正在读取接口状态…</p>
  </section>

  <ClDetailDialog :open="dialogOpen" title="T-08 设计边界" @close="dialogOpen = false">
    <ul>
      <li>静态原型 <code>design-demos/*.html</code> 保持只读，仍可独立打开。</li>
      <li>七个业务域清单端点仍返回 <code>501 NOT_IMPLEMENTED</code>。</li>
      <li>不导入原型 JSON、不生成示例曲目或权利结论。</li>
      <li>不启动 nginx / Compose web 服务。</li>
    </ul>
  </ClDetailDialog>
</template>

<style scoped>
.hero { padding-block: 60px 40px; }
.hero h1 { font-family: var(--serif); font-size: clamp(38px, 5vw, 60px); font-weight: 900; line-height: 1.14; }
.hero-desc { max-width: 660px; margin-bottom: 26px; font-size: 17px; line-height: 1.9; }
.hero-actions { display: flex; flex-wrap: wrap; gap: 16px; }
.section-block { padding-block: 24px 36px; }
.card-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 18px; }
.hint { margin-top: 16px; font-size: 14px; color: var(--ink-soft); }
.status-line { padding: 14px 16px; border: 2px solid var(--ink); background: var(--paper-light); font-size: 14px; }
.status-line--error { border-color: var(--red); }
code { padding: 1px 5px; background: rgba(25, 25, 23, 0.08); }
</style>
