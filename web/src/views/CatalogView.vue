<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import ClLibraryMap from '@/components/ClLibraryMap.vue'
import {
  catalogAudioLinks,
  catalogAvailability,
  catalogDocumentTitle,
  catalogDocumentUrl,
  catalogEntries,
  catalogLineUrl,
  catalogRecordings,
  catalogSpecialtyWork,
  catalogStats,
  catalogVolumeInfo,
  type CatalogAvailability,
  type CatalogVolume,
} from '@/research/catalog'

const query = ref('')
const volume = ref<'all' | CatalogVolume>('all')
const availability = ref<'all' | CatalogAvailability>('all')
const page = ref(1)
const PAGE_SIZE = 12

const volumeFilters = [
  { value: 'all', label: `全部 ${catalogStats.total} 首` },
  { value: 'V1', label: `第一卷 ${catalogStats.v1} 首` },
  { value: 'V4', label: `第四卷 ${catalogStats.v4} 首` },
] as const

const availabilityFilters = [
  { value: 'all', label: '全部状态' },
  { value: 'recording', label: `已有录音 ${catalogStats.withRecording}` },
  { value: 'source', label: `有音源线索 ${catalogStats.withSource}` },
  { value: 'bibliography', label: `仅目录 ${catalogStats.bibliographyOnly}` },
] as const

const filteredEntries = computed(() => {
  const needle = query.value.normalize('NFKC').trim().toLocaleLowerCase('zh-CN')
  return catalogEntries.filter((entry) => {
    if (volume.value !== 'all' && entry.volume !== volume.value) return false
    if (availability.value !== 'all' && catalogAvailability(entry) !== availability.value) return false
    if (!needle) return true
    return [entry.id, entry.title, entry.volume, entry.era]
      .join(' ').normalize('NFKC').toLocaleLowerCase('zh-CN').includes(needle)
  })
})
const totalPages = computed(() => Math.max(1, Math.ceil(filteredEntries.value.length / PAGE_SIZE)))
const pageItems = computed(() => filteredEntries.value.slice((page.value - 1) * PAGE_SIZE, page.value * PAGE_SIZE))

watch([query, volume, availability], () => { page.value = 1 })
watch(totalPages, (total) => { if (page.value > total) page.value = total })

onMounted(() => {
  const params = new URLSearchParams(window.location.search)
  query.value = params.get('q') ?? ''
  const requestedVolume = params.get('volume')
  if (requestedVolume === 'V1' || requestedVolume === 'V4') volume.value = requestedVolume
})

function clearFilters(): void {
  query.value = ''
  volume.value = 'all'
  availability.value = 'all'
}
</script>

<template>
  <div class="catalog-page">
    <section class="shell catalog-hero" aria-labelledby="catalog-title">
      <nav class="catalog-context" aria-label="音乐资料导航">
        <RouterLink to="/music">← 儿童音乐馆</RouterLink>
        <RouterLink to="/works">已有研究录音</RouterLink>
        <RouterLink to="/music/sources">音源链接</RouterLink>
      </nav>
      <h1 id="catalog-title">百年儿歌目录</h1>
      <p class="catalog-lead">《中国儿童歌曲百年经典》公开目录已核对 <strong>{{ catalogStats.total }}</strong> 首：第一卷 {{ catalogStats.v1 }} 首、第四卷 {{ catalogStats.v4 }} 首。每首作品按实际采集进度展示可听录音、外部音源线索或待采集状态。</p>
      <div class="catalog-numbers" aria-label="目录采集进度">
        <div><strong>{{ catalogStats.total }}</strong><span>已登记作品</span></div>
        <div><strong>{{ catalogStats.withRecording }}</strong><span>已有研究录音</span></div>
        <div><strong>{{ catalogStats.withSource }}</strong><span>已有音源线索</span></div>
        <div><strong>{{ catalogStats.bibliographyOnly }}</strong><span>待采集</span></div>
      </div>
      <details class="catalog-details">
        <summary>目录来源与边界</summary>
        <p>条目依 {{ catalogDocumentTitle }} 的公开目录次序登记，状态保持原文的「目录核对 / 待评审」。第二、三卷尚未取得可逐首核验的公开目录，不推测标题补齐 500 首。目录登记不等于已取得录音、曲谱或再发布授权。</p>
        <a :href="catalogDocumentUrl" target="_blank" rel="noopener noreferrer">在 GitHub 查看原始目录 ↗</a>
      </details>
    </section>

    <section class="shell catalog-filter" aria-labelledby="catalog-filter-title">
      <h2 id="catalog-filter-title" class="visually-hidden">搜索和筛选目录</h2>
      <label class="catalog-search">
        <span>搜索作品名或目录编号</span>
        <input v-model="query" type="search" placeholder="例如：小老鼠上灯台、V1-001、送别" autocomplete="off">
      </label>
      <div class="catalog-filter-row">
        <div class="catalog-kinds" role="group" aria-label="按卷筛选">
          <button
            v-for="item in volumeFilters"
            :key="item.value"
            type="button"
            :aria-pressed="volume === item.value"
            @click="volume = item.value"
          >{{ item.label }}</button>
        </div>
        <div class="catalog-kinds catalog-states" role="group" aria-label="按采集状态筛选">
          <button
            v-for="item in availabilityFilters"
            :key="item.value"
            type="button"
            :aria-pressed="availability === item.value"
            @click="availability = item.value"
          >{{ item.label }}</button>
        </div>
      </div>
      <p class="catalog-count" role="status" aria-live="polite">找到 {{ filteredEntries.length }} 首；当前第 {{ page }} / {{ totalPages }} 页。</p>
    </section>

    <section class="shell catalog-results" aria-label="公开目录作品">
      <article
        v-for="entry in pageItems"
        :key="entry.id"
        class="catalog-card"
        :class="`is-${catalogAvailability(entry)}`"
        :data-catalog-id="entry.id"
      >
        <div class="catalog-card-top">
          <span>{{ entry.id }}</span>
          <span>{{ catalogVolumeInfo[entry.volume].label }} · {{ entry.era }}</span>
        </div>
        <h2>{{ entry.title }}</h2>
        <p class="catalog-status" :data-availability="catalogAvailability(entry)">
          <template v-if="catalogAvailability(entry) === 'recording'">已有 {{ catalogRecordings(entry).length }} 条研究录音</template>
          <template v-else-if="catalogAvailability(entry) === 'source'">{{ catalogAudioLinks(entry).length }} 条外部音源线索</template>
          <template v-else>仅目录登记 · 待采集</template>
        </p>
        <div class="catalog-actions">
          <RouterLink
            v-if="catalogRecordings(entry).length"
            class="catalog-primary"
            :to="{ path: '/works', query: { work: catalogRecordings(entry)[0]!.id } }"
          >试听已有录音 →</RouterLink>
          <RouterLink
            v-else-if="catalogAudioLinks(entry).length"
            class="catalog-primary"
            :to="{ path: '/music/sources', query: { q: entry.title } }"
          >查看音源线索 →</RouterLink>
          <span v-else class="catalog-pending">暂无可听版本</span>
          <RouterLink
            v-if="catalogSpecialtyWork(entry)"
            :to="`/music/specialties/${catalogSpecialtyWork(entry)!.specialties[0] ?? 'childhood'}`"
          >所属专题 →</RouterLink>
        </div>
        <a class="catalog-source" :href="catalogLineUrl(entry)" target="_blank" rel="noopener noreferrer">目录原文 L{{ entry.sourceLine }} ↗</a>
      </article>
      <div v-if="!pageItems.length" class="catalog-empty" role="status">
        <h2>没有匹配的作品</h2>
        <p>可以缩短关键词，或恢复全部卷与状态。</p>
        <button type="button" @click="clearFilters">清空搜索与筛选</button>
      </div>
    </section>

    <nav v-if="filteredEntries.length > PAGE_SIZE" class="shell catalog-pagination" aria-label="目录分页">
      <button type="button" :disabled="page === 1" @click="page -= 1">上一页</button>
      <button
        v-for="number in totalPages"
        :key="number"
        type="button"
        :aria-current="page === number ? 'page' : undefined"
        :aria-label="`目录第 ${number} 页`"
        @click="page = number"
      >{{ number }}</button>
      <button type="button" :disabled="page === totalPages" @click="page += 1">下一页</button>
    </nav>

    <ClLibraryMap current="music" />
  </div>
</template>

<style scoped>
.catalog-page { --page-width: 1240px; }
.catalog-page > .shell { width: min(calc(100% - 48px), var(--page-width)); }
.catalog-hero { padding-block: 40px 30px; }
.catalog-context { display: flex; flex-wrap: wrap; gap: 10px 22px; margin-bottom: 20px; font-size: 14px; font-weight: 900; }
.catalog-context a { text-underline-offset: 4px; }
.catalog-hero h1 { margin-bottom: 12px; font-family: var(--serif); font-size: clamp(40px, 6vw, 62px); line-height: 1.15; }
.catalog-lead { max-width: 780px; margin-bottom: 24px; font-size: 17px; line-height: 1.85; }
.catalog-numbers { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 14px; margin-bottom: 22px; }
.catalog-numbers div { display: flex; flex-direction: column; gap: 2px; padding: 14px 16px; border: var(--line); background: var(--paper-light); box-shadow: 4px 4px 0 var(--ink); /* taste-skill-ignore: 沿用研究资料卡硬阴影。 */ }
.catalog-numbers strong { font-family: var(--serif); font-size: 30px; line-height: 1.2; }
.catalog-numbers span { font-size: 13px; font-weight: 800; color: var(--ink-soft); }
.catalog-details { max-width: 780px; padding: 0; border-left: 5px solid var(--blue); background: var(--paper-light); }
.catalog-details summary { padding: 10px 14px; font-size: 14px; font-weight: 900; cursor: pointer; }
.catalog-details p { margin: 0; padding: 0 14px 10px; font-size: 13px; line-height: 1.8; color: var(--ink-soft); }
.catalog-details a { display: inline-block; padding: 0 14px 12px; font-size: 13px; font-weight: 800; }
.catalog-filter { margin-bottom: 26px; padding: 20px; border: var(--line); background: var(--paper-light); box-shadow: 5px 5px 0 var(--ink); /* taste-skill-ignore: 沿用录音页筛选卡硬阴影。 */ }
.catalog-search { display: grid; gap: 7px; font-weight: 900; }
.catalog-search input { width: 100%; min-height: 52px; padding: 10px 14px; border: 2px solid var(--ink); border-radius: 0; background: #fff; color: var(--ink); font: inherit; }
.catalog-filter-row { display: flex; flex-wrap: wrap; gap: 12px 24px; margin-top: 16px; }
.catalog-kinds { display: flex; flex-wrap: wrap; gap: 10px; }
.catalog-kinds button, .catalog-pagination button, .catalog-empty button { min-height: 44px; padding: 8px 13px; border: 2px solid var(--ink); border-radius: 0; background: var(--paper); font-size: 14px; font-weight: 800; }
.catalog-kinds button[aria-pressed="true"], .catalog-pagination button[aria-current="page"] { background: var(--blue); color: var(--paper-light); }
.catalog-states button { font-size: 13px; }
.catalog-count { margin: 14px 0 0; font-weight: 800; }
.catalog-results { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 20px; }
.catalog-card { min-width: 0; display: flex; flex-direction: column; padding: 18px; border: var(--line); background: var(--paper-light); box-shadow: 5px 5px 0 var(--ink); /* taste-skill-ignore: 沿用研究资料卡硬阴影。 */ }
.catalog-card.is-recording { background: #fdf1c9; }
.catalog-card.is-source { background: #e2ebd7; }
.catalog-card-top { display: flex; flex-wrap: wrap; justify-content: space-between; gap: 7px 12px; margin-bottom: 12px; font-size: 12px; font-weight: 900; }
.catalog-card h2 { margin: 0 0 10px; font-family: var(--serif); font-size: 24px; line-height: 1.35; overflow-wrap: anywhere; }
.catalog-status { margin: 0 0 16px; font-size: 14px; font-weight: 900; line-height: 1.6; }
.catalog-status[data-availability="recording"] { color: #8a640b; }
.catalog-status[data-availability="source"] { color: var(--green); }
.catalog-status[data-availability="bibliography"] { color: var(--ink-soft); }
.catalog-actions { display: flex; flex-wrap: wrap; align-items: center; gap: 9px 16px; margin-top: auto; padding-top: 14px; border-top: 2px dashed var(--ink); font-size: 13px; font-weight: 800; }
.catalog-actions a { min-height: 44px; display: inline-flex; align-items: center; text-underline-offset: 4px; }
.catalog-actions .catalog-primary { padding-inline: 12px; border: 2px solid var(--ink); background: var(--yellow); text-decoration: none; }
.catalog-pending { color: var(--ink-soft); }
.catalog-source { margin-top: 10px; font-size: 12px; font-weight: 800; line-height: 1.6; text-underline-offset: 3px; }
.catalog-empty { grid-column: 1 / -1; padding: 30px; border: var(--line); background: var(--yellow); text-align: center; }
.catalog-empty h2 { font-family: var(--serif); }
.catalog-pagination { display: flex; flex-wrap: wrap; justify-content: center; gap: 9px; padding-block: 30px 44px; }
.catalog-pagination button:disabled { cursor: not-allowed; opacity: .55; }
@media (max-width: 1050px) { .catalog-results { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 640px) {
  .catalog-page > .shell { width: min(calc(100% - 32px), var(--page-width)); }
  .catalog-results { grid-template-columns: 1fr; }
  .catalog-hero { padding-block: 30px 22px; }
  .catalog-numbers { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .catalog-card { padding: 16px; }
}
</style>
