<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import ClLibraryMap from '@/components/ClLibraryMap.vue'
import {
  audioLinkBatches,
  audioLinkKindLabel,
  audioLinkKinds,
  audioSourceLinks,
  sampleForAudioLink,
  type AudioLinkKind,
} from '@/research/audioLinks'
import { documentUrl } from '@/research/documents'

const query = ref('')
const kind = ref<'all' | AudioLinkKind>('all')
const page = ref(1)
const PAGE_SIZE = 12
const linkedRecordingCount = new Set(audioSourceLinks.map((link) => sampleForAudioLink(link)?.id).filter(Boolean)).size

const filteredLinks = computed(() => {
  const needle = query.value.normalize('NFKC').trim().toLocaleLowerCase()
  return audioSourceLinks.filter((link) => {
    if (kind.value !== 'all' && link.kind !== kind.value) return false
    if (!needle) return true
    return [link.title, link.version, link.platform, link.note, link.batch]
      .join(' ').normalize('NFKC').toLocaleLowerCase().includes(needle)
  })
})
const totalPages = computed(() => Math.max(1, Math.ceil(filteredLinks.value.length / PAGE_SIZE)))
const pageItems = computed(() => filteredLinks.value.slice((page.value - 1) * PAGE_SIZE, page.value * PAGE_SIZE))

watch([query, kind], () => { page.value = 1 })
watch(totalPages, (total) => { if (page.value > total) page.value = total })

onMounted(() => {
  query.value = new URLSearchParams(window.location.search).get('q') ?? ''
})

function clearFilters(): void {
  query.value = ''
  kind.value = 'all'
}
</script>

<template>
  <div class="sources-page">
    <section class="shell sources-hero" aria-labelledby="sources-title">
      <nav class="sources-context" aria-label="音乐资料导航">
        <RouterLink to="/music">← 儿童音乐馆</RouterLink>
        <RouterLink to="/music/catalog">百年儿歌目录</RouterLink>
        <RouterLink to="/works">已有研究录音</RouterLink>
        <RouterLink to="/library">资料总览</RouterLink>
      </nav>
      <h1 id="sources-title">儿歌音源链接</h1>
      <p>把 GitHub 研究档案里已登记的歌曲、专辑、视频和唱片目录入口集中到这里。共 {{ audioSourceLinks.length }} 条，其中 {{ linkedRecordingCount }} 首作品已有本地研究录音。</p>
      <details class="sources-boundary">
        <summary>关于外部链接的使用边界</summary>
        <p>外部链接用于人工试听、版本识别和目录核对；可播放不代表已下载或获得本站再发布授权。没有本地录音的条目只跳原站，不提供虚构播放按钮。</p>
      </details>
    </section>

    <section class="shell source-filter" aria-labelledby="source-filter-title">
      <h2 id="source-filter-title" class="visually-hidden">搜索和筛选音源链接</h2>
      <label class="source-search">
        <span>搜索歌曲、演唱者、平台或批次</span>
        <input v-model="query" type="search" placeholder="例如：小白船、小蓓蕾、Apple Music、12" autocomplete="off">
      </label>
      <div class="source-kinds" role="group" aria-label="按音源入口类型筛选">
        <button
          v-for="item in audioLinkKinds"
          :key="item.value"
          type="button"
          :aria-pressed="kind === item.value"
          @click="kind = item.value"
        >{{ item.label }}</button>
      </div>
      <p class="source-count" role="status" aria-live="polite">找到 {{ filteredLinks.length }} 条；当前第 {{ page }} / {{ totalPages }} 页。</p>
    </section>

    <section class="shell source-results" aria-label="GitHub 已登记音源链接">
      <article v-for="link in pageItems" :key="link.id" class="source-card" :data-source-id="link.id">
        <div class="source-card-top">
          <span>{{ audioLinkKindLabel(link.kind) }} · 批次 {{ link.batch }}</span>
          <span>{{ link.platform }}</span>
        </div>
        <h2>{{ link.title }}</h2>
        <p class="source-version">{{ link.version }}</p>
        <p class="source-note">{{ link.note }}</p>
        <div class="source-actions">
          <a class="source-primary" :href="link.url" target="_blank" rel="noopener noreferrer">打开原站入口 ↗</a>
          <RouterLink v-if="sampleForAudioLink(link)" :to="{ path: '/works', query: { work: sampleForAudioLink(link)!.id } }">查看已有研究录音 →</RouterLink>
          <span v-else>仅外部入口 · 未采集本地音频</span>
        </div>
        <a class="source-document" :href="documentUrl(audioLinkBatches[link.batch].path)" target="_blank" rel="noopener noreferrer">{{ audioLinkBatches[link.batch].title }} · GitHub 原文 ↗</a>
      </article>
      <div v-if="!pageItems.length" class="source-empty" role="status">
        <h2>没有匹配的音源链接</h2>
        <p>可以缩短关键词，或恢复全部入口类型。</p>
        <button type="button" @click="clearFilters">清空搜索与筛选</button>
      </div>
    </section>

    <nav v-if="filteredLinks.length > PAGE_SIZE" class="shell source-pagination" aria-label="音源链接分页">
      <button type="button" :disabled="page === 1" @click="page -= 1">上一页</button>
      <button
        v-for="number in totalPages"
        :key="number"
        type="button"
        :aria-current="page === number ? 'page' : undefined"
        :aria-label="`音源第 ${number} 页`"
        @click="page = number"
      >{{ number }}</button>
      <button type="button" :disabled="page === totalPages" @click="page += 1">下一页</button>
    </nav>

    <ClLibraryMap current="music" />
  </div>
</template>

<style scoped>
.sources-hero { max-width: 900px; padding-block: 40px 28px; }
.sources-context { display: flex; flex-wrap: wrap; gap: 10px 22px; margin-bottom: 20px; font-size: 14px; font-weight: 900; }
.sources-context a { text-underline-offset: 4px; }
.sources-hero h1 { margin-bottom: 14px; font-family: var(--serif); font-size: clamp(40px, 6vw, 62px); line-height: 1.15; }
.sources-hero > p { font-size: 17px; line-height: 1.8; }
.sources-boundary { margin-top: 6px; font-size: 14px; }
.sources-boundary summary { padding: 8px 0; font-weight: 900; cursor: pointer; }
.sources-boundary p { margin: 0; padding: 8px 0 0; color: var(--ink-soft); line-height: 1.8; }
.source-filter { margin-bottom: 26px; padding: 20px; border: var(--line); background: var(--paper-light); box-shadow: 5px 5px 0 var(--ink); /* taste-skill-ignore: 沿用录音页筛选卡硬阴影。 */ }
.source-search { display: grid; gap: 7px; font-weight: 900; }
.source-search input { width: 100%; min-height: 52px; padding: 10px 14px; border: 2px solid var(--ink); border-radius: 0; background: #fff; color: var(--ink); font: inherit; }
.source-kinds { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 16px; }
.source-kinds button, .source-pagination button, .source-empty button { min-height: 44px; padding: 8px 13px; border: 2px solid var(--ink); border-radius: 0; background: var(--paper); font-size: 14px; font-weight: 800; }
.source-kinds button[aria-pressed="true"], .source-pagination button[aria-current="page"] { background: var(--blue); color: var(--paper-light); }
.source-count { margin: 14px 0 0; font-weight: 800; }
.source-results { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 20px; }
.source-card { min-width: 0; display: flex; flex-direction: column; padding: 18px; border: var(--line); background: var(--paper-light); box-shadow: 5px 5px 0 var(--ink); /* taste-skill-ignore: 沿用研究资料卡硬阴影。 */ }
.source-card-top { display: flex; flex-wrap: wrap; justify-content: space-between; gap: 7px 12px; margin-bottom: 12px; font-size: 12px; font-weight: 900; }
.source-card h2 { margin: 0 0 8px; font-family: var(--serif); font-size: 24px; line-height: 1.35; overflow-wrap: anywhere; }
.source-version { margin: 0 0 12px; font-size: 15px; font-weight: 900; line-height: 1.55; }
.source-note { margin: 0 0 16px; color: var(--ink-soft); font-size: 14px; line-height: 1.7; }
.source-actions { display: flex; flex-wrap: wrap; align-items: center; gap: 9px 16px; margin-top: auto; padding-top: 14px; border-top: 2px dashed var(--ink); font-size: 13px; font-weight: 800; }
.source-actions a { min-height: 44px; display: inline-flex; align-items: center; text-underline-offset: 4px; }
.source-actions .source-primary { padding-inline: 12px; border: 2px solid var(--ink); background: var(--yellow); text-decoration: none; }
.source-document { margin-top: 10px; font-size: 12px; font-weight: 800; line-height: 1.6; text-underline-offset: 3px; }
.source-empty { grid-column: 1 / -1; padding: 30px; border: var(--line); background: var(--yellow); text-align: center; }
.source-empty h2 { font-family: var(--serif); }
.source-pagination { display: flex; flex-wrap: wrap; justify-content: center; gap: 9px; padding-block: 30px 44px; }
.source-pagination button:disabled { cursor: not-allowed; opacity: .55; }
@media (max-width: 1050px) { .source-results { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 640px) { .source-results { grid-template-columns: 1fr; } .sources-hero { padding-block: 30px 22px; } .source-card { padding: 16px; } }
</style>
