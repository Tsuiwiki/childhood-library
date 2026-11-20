<script setup lang="ts">
import type { ResearchRecord } from '@/research/library'
import { statusLabels, statusModel } from '@/research/library'

defineProps<{ record: ResearchRecord }>()

const statusKeys = ['researchStatus', 'rightsStatus', 'qualityStatus', 'accessMethod', 'publicationStatus'] as const

function isExternal(url: string): boolean {
  return /^https?:\/\//.test(url)
}

function localSource(url: string): string {
  if (url === 'specialty-classical.html') return '/music/specialties/classical'
  if (url.endsWith('DATA_MODEL.md')) return 'https://github.com/Tsuiwiki/childhood-library/blob/main/docs/DATA_MODEL.md'
  return url
}
</script>

<template>
  <article class="rec-card" :data-record-id="record.id" :data-group="record.group">
    <span class="rid">{{ record.id }} · {{ record.isTopic ? '征集方向' : record.isAsset ? '版本 / 资产线索' : '作品线索' }}</span>
    <h3>{{ record.title }}</h3>
    <span class="meta">{{ record.origin }} · {{ record.contributor }}</span>
    <span class="meta">适读 {{ record.ageBand }} 岁 · {{ record.groupName }}</span>
    <div class="rec-tags" aria-label="研究状态">
      <span
        v-for="key in statusKeys"
        :key="key"
        :class="{ warn: (key === 'rightsStatus' || key === 'publicationStatus') }"
        :title="key"
      >{{ statusLabels[record[key]] ?? record[key] }}</span>
    </div>
    <details>
      <summary>研究备注与来源线索</summary>
      <p><b>待核验事项：</b>{{ record.note }}</p>
      <p>
        <b>来源线索：</b>
        <a
          :href="isExternal(record.sourceUrl) ? record.sourceUrl : localSource(record.sourceUrl)"
          :target="isExternal(record.sourceUrl) || localSource(record.sourceUrl).startsWith('http') ? '_blank' : undefined"
          :rel="isExternal(record.sourceUrl) || localSource(record.sourceUrl).startsWith('http') ? 'noopener noreferrer' : undefined"
        >{{ record.sourceName }} ↗</a>
        <template v-if="!record.isTopic && !record.isAsset">（机构/栏目入口，具体作品页面待逐条考证）</template>
      </p>
      <p><b>资产边界：</b>{{ record.assetNote }}</p>
      <dl class="status-list">
        <template v-for="(row, index) in statusModel" :key="row.field">
          <dt>{{ row.field }}</dt>
          <dd>{{ record[statusKeys[index]!] }} · {{ statusLabels[record[statusKeys[index]!]] }}</dd>
        </template>
      </dl>
    </details>
  </article>
</template>

<style scoped>
.rec-card { border: var(--line); background: var(--paper-light); box-shadow: 4px 4px 0 var(--ink); /* taste-skill-ignore: 保留原型研究卡硬阴影。 */ padding: 14px 15px 12px; display: flex; flex-direction: column; gap: 6px; }
.rid { font-size: 11px; font-weight: 900; color: var(--blue); letter-spacing: .08em; }
h3 { font-family: var(--serif); font-size: 19px; font-weight: 900; line-height: 1.4; margin: 0; }
.meta { font-size: 12px; color: var(--ink-soft); }
.rec-tags { display: flex; flex-wrap: wrap; gap: 5px; margin-top: 2px; }
.rec-tags span { padding: 1px 7px; border: 2px solid var(--ink); background: var(--yellow); font-size: 10px; font-weight: 800; }
.rec-tags span.warn { background: #dde5f6; }
details { margin-top: 6px; border-top: 2px dashed var(--ink); padding-top: 8px; font-size: 13px; }
summary { font-weight: 800; cursor: pointer; }
details p { margin: 8px 0 0; line-height: 1.65; color: #33322e; }
details a { text-decoration: underline 2px var(--blue); text-underline-offset: 3px; font-weight: 800; overflow-wrap: anywhere; }
.status-list { display: grid; grid-template-columns: auto 1fr; gap: 3px 10px; margin: 8px 0 0; font-size: 12px; }
.status-list dt { font-weight: 800; font-family: monospace; /* taste-skill-ignore: 五维状态字段名按原型使用等宽字体。 */ overflow-wrap: anywhere; }
.status-list dd { margin: 0; }
</style>
