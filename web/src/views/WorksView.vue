<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import ClTrackDetailDialog from '@/components/ClTrackDetailDialog.vue'
import { useAudioPlayer } from '@/composables/useAudioPlayer'
import { getSpecialty, isSpecialtyId, workSpecialties, type SpecialtyId } from '@/research/specialties'
import {
  assetUrl,
  researchSamples,
  sampleCategory,
  toPlayerTrack,
  type ResearchSample,
  type ResearchVersion,
} from '@/research/samples'

const samples = researchSamples
const { playTrack, playPlaylist, stopVersion } = useAudioPlayer()
const detailSample = ref<ResearchSample | null>(null)
const query = ref('')
const category = ref('all')
const topicId = ref<SpecialtyId | null>(null)
const page = ref(1)
const PAGE_SIZE = 9
const categoryFilters = [
  { value: 'all', label: '全部录音' },
  { value: 'internal', label: '经典原声' },
  { value: 'generated', label: '原创示范 · 非原曲' },
  { value: 'open', label: '开放许可' },
]

const activeTopic = computed(() => topicId.value ? getSpecialty(topicId.value) : undefined)
const filteredSamples = computed(() => {
  const needle = query.value.normalize('NFKC').trim().toLocaleLowerCase()
  return samples.filter((sample) => {
    if (category.value !== 'all' && sampleCategory(sample) !== category.value) return false
    if (topicId.value && !workSpecialties(sample.id).some((item) => item.id === topicId.value)) return false
    if (!needle) return true
    return [sample.id, sample.workTitle, sample.kind, sample.author, sample.attribution, sample.sourceTitle, sample.license]
      .filter(Boolean).join(' ').normalize('NFKC').toLocaleLowerCase().includes(needle)
  })
})
const totalPages = computed(() => Math.max(1, Math.ceil(filteredSamples.value.length / PAGE_SIZE)))
const pageItems = computed(() => filteredSamples.value.slice((page.value - 1) * PAGE_SIZE, page.value * PAGE_SIZE))

watch([query, category, topicId], () => { page.value = 1 })
watch(totalPages, (total) => { if (page.value > total) page.value = total })

onMounted(() => {
  const params = new URLSearchParams(window.location.search)
  const requestedTopic = params.get('topic')
  if (requestedTopic && isSpecialtyId(requestedTopic)) topicId.value = requestedTopic
  const workId = params.get('work')
  if (!workId) return
  const sample = samples.find((item) => item.id === workId)
  if (sample) detailSample.value = sample
})

function clearFilters(): void {
  query.value = ''
  category.value = 'all'
  topicId.value = null
}

function playFilteredSamples(): void {
  playPlaylist(filteredSamples.value.map((sample) => toPlayerTrack(sample, sample)))
}

function playSample(version: ResearchVersion, work: ResearchSample): void {
  playTrack(toPlayerTrack(version, work))
}

function playFromDetail(version: ResearchVersion): void {
  if (detailSample.value) playSample(version, detailSample.value)
}

function onVersionChange(version: ResearchVersion): void {
  const work = detailSample.value
  if (work) stopVersion(work.id, `/audio/${version.file}`)
}
</script>

<template>
  <section class="shell works-page">
    <header class="works-header">
      <nav class="works-context" aria-label="资料导航"><RouterLink to="/library">← 资料总览</RouterLink><RouterLink to="/music">儿童音乐馆与专题</RouterLink><RouterLink to="/music/sources">已采集音源链接</RouterLink></nav>
      <div v-if="activeTopic" class="topic-context" aria-label="当前专题筛选">
        <span>来自音乐专题</span>
        <strong>{{ activeTopic.name }}</strong>
        <RouterLink :to="`/music/specialties/${activeTopic.id}`">返回专题档案</RouterLink>
        <button type="button" @click="topicId = null">查看全部录音</button>
      </div>
      <h1>{{ activeTopic ? `${activeTopic.name} · 已有录音` : '曲目列表' }}</h1>
      <p>共 {{ samples.length }} 条主录音记录。挑一首直接听，或点开看版本与详情。</p>
      <details class="rights-note">
        <summary>内部试听与权利边界</summary>
        <p>权利待核验的录音仅限内部研究试听；开放许可仅对应各条目注明的具体录音。本页不是已发布曲库，也不代表数据库已经导入。</p>
      </details>
    </header>

    <section class="filter-card" aria-labelledby="filter-title">
      <h2 id="filter-title" class="visually-hidden">搜索和筛选录音</h2>
      <label class="search-field">
        <span>搜索曲目、演唱者、来源或许可</span>
        <input v-model="query" type="search" placeholder="例如：小燕子、CC0、中央乐团" autocomplete="off">
      </label>
      <div class="category-filters" role="group" aria-label="按录音类型筛选">
        <button
          v-for="filter in categoryFilters"
          :key="filter.value"
          type="button"
          :aria-pressed="category === filter.value"
          @click="category = filter.value"
        >{{ filter.label }}</button>
      </div>
      <div class="playlist-launch">
        <button
          class="detail-button playlist-start"
          type="button"
          data-playlist-start
          :disabled="!filteredSamples.length"
          @click="playFilteredSamples"
        >循环播放当前 {{ filteredSamples.length }} 首</button>
        <p>包含全部筛选结果和后续分页；启动后保留这份播放列表。</p>
      </div>
      <p class="results-status" role="status" aria-live="polite">
        找到 {{ filteredSamples.length }} 条；当前显示第 {{ page }} / {{ totalPages }} 页。
      </p>
    </section>

    <div v-if="pageItems.length" class="works-grid" aria-label="已有录音列表">
      <article v-for="sample in pageItems" :key="sample.id" class="work-card" :data-work="sample.id">
        <button
          class="work-cover"
          type="button"
          :aria-label="`查看《${sample.workTitle}》详情`"
          @click="detailSample = sample"
        >
          <img :src="assetUrl(sample.materials.cover)" :alt="sample.materials.coverAlt" loading="lazy">
        </button>
        <div class="work-body">
          <h2>{{ sample.workTitle }}</h2>
          <p class="work-credit">{{ sample.author || sample.kind }}</p>
          <p class="work-meta">{{ sample.durationLabel ?? '时长待核' }}</p>
          <div class="work-actions">
            <button
              class="play-button"
              type="button"
              data-audio-play="true"
              :data-work-id="sample.id"
              :data-play="sample.id"
              :aria-label="`试听《${sample.workTitle}》`"
              @click="playSample(sample, sample)"
            >试听 <span aria-hidden="true">▶</span></button>
            <button
              class="detail-link"
              type="button"
              :data-work-detail="sample.id"
              @click="detailSample = sample"
            >看详情 →</button>
          </div>
        </div>
      </article>
    </div>

    <div v-else class="no-results" role="status">
      <h2>没有匹配的录音</h2>
      <p>可以缩短关键词，或切换为“全部录音”。</p>
      <button class="detail-button" type="button" @click="clearFilters">清空搜索与筛选</button>
    </div>

    <nav v-if="filteredSamples.length > PAGE_SIZE" class="pagination" aria-label="录音列表分页">
      <button class="detail-button" type="button" :disabled="page === 1" @click="page -= 1">上一页</button>
      <button
        v-for="number in totalPages"
        :key="number"
        class="detail-button page-button"
        type="button"
        :aria-current="page === number ? 'page' : undefined"
        :aria-label="`第 ${number} 页`"
        @click="page = number"
      >{{ number }}</button>
      <button class="detail-button" type="button" :disabled="page === totalPages" @click="page += 1">下一页</button>
    </nav>
  </section>

  <ClTrackDetailDialog
    :sample="detailSample"
    @close="detailSample = null"
    @play="playFromDetail"
    @version-change="onVersionChange"
  />
</template>

<style scoped>
/* Card and button geometry copied from design-demos/works.html L299-L400. */
.works-page { padding-block: 42px 64px; }
.works-header { max-width: 850px; margin-bottom: 30px; }
.works-context { display: flex; flex-wrap: wrap; gap: 10px 22px; margin-bottom: 18px; font-size: 14px; font-weight: 900; }
.works-context a { text-underline-offset: 4px; }
.topic-context { display: flex; flex-wrap: wrap; align-items: center; gap: 8px 16px; margin-bottom: 18px; padding: 12px 14px; border: var(--line); background: var(--yellow); box-shadow: 4px 4px 0 var(--ink); /* taste-skill-ignore: 保留原型筛选提示硬阴影。 */ }
.topic-context strong { font-family: var(--serif); font-size: 20px; }
.topic-context a { font-weight: 900; text-underline-offset: 4px; }
.topic-context button { min-height: 44px; margin-left: auto; padding: 7px 11px; border: 2px solid var(--ink); background: var(--paper-light); font-size: 13px; font-weight: 900; }
.works-header h1 { margin-bottom: 12px; font-family: var(--serif); font-size: clamp(38px, 5vw, 58px); font-weight: 900; line-height: 1.2; }
.works-header p { margin-bottom: 12px; font-size: 17px; }
.works-header code { padding: 1px 5px; background: rgba(25, 25, 23, .08); overflow-wrap: anywhere; }
.rights-note { margin-top: 4px; font-size: 14px; }
.rights-note summary { padding: 8px 0; font-weight: 900; cursor: pointer; }
.rights-note p { margin: 0; padding: 6px 0 0; color: var(--ink-soft); line-height: 1.8; }
.works-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 22px; }
/* Same content-card language as HomeView: cover first, listening first.
   Version / source / rights detail stays in the detail dialog and the
   collapsed boundary note instead of being stamped on every card. */
.work-card { min-width: 0; display: flex; flex-direction: column; border: var(--line); background: var(--paper-light); box-shadow: 5px 5px 0 var(--ink); /* taste-skill-ignore: 沿用首页作品卡硬阴影。 */ }
.work-cover { display: block; width: 100%; aspect-ratio: 4 / 3; padding: 0; overflow: hidden; border: 0; border-bottom: var(--line); border-radius: 0; background: var(--paper); cursor: pointer; }
.work-cover img { display: block; width: 100%; height: 100%; object-fit: cover; }
.work-body { display: flex; flex: 1; flex-direction: column; padding: 14px 16px 16px; }
.work-body h2 { margin: 0 0 6px; font-family: var(--serif); font-size: 22px; font-weight: 900; line-height: 1.35; overflow-wrap: anywhere; }
.work-credit { margin: 0 0 4px; font-size: 13px; font-weight: 800; line-height: 1.55; }
.work-meta { margin: 0 0 14px; font-size: 12px; color: var(--ink-soft); }
.work-actions { display: flex; flex-wrap: wrap; align-items: center; gap: 8px 14px; margin-top: auto; padding-top: 12px; border-top: 2px dashed var(--ink); font-size: 13px; font-weight: 800; }
.play-button { min-height: 42px; padding: 7px 12px; border: 2px solid var(--ink); border-radius: 0; background: var(--yellow); font-size: 13px; font-weight: 900; cursor: pointer; }
.detail-link { min-height: 42px; padding: 7px 2px; border: 0; background: transparent; color: var(--ink); font-size: 13px; font-weight: 900; text-underline-offset: 4px; cursor: pointer; }
.detail-link:hover { text-decoration: underline; }
/* Still used by the filter, pagination and topic-context controls. */
.detail-button { min-height: 44px; flex: 0 0 auto; padding: 8px 12px; border: 2px solid var(--ink); border-radius: 0; background: var(--paper-light); box-shadow: 3px 3px 0 var(--ink); /* taste-skill-ignore: 保留原型按钮硬阴影。 */ font-size: 14px; font-weight: 900; }
.filter-card { margin-bottom: 30px; padding: 20px; border: var(--line); background: var(--paper-light); box-shadow: 5px 5px 0 var(--ink); /* taste-skill-ignore: 保留原型筛选卡硬阴影。 */ }
.search-field { display: grid; gap: 7px; font-weight: 900; }
.search-field input { width: 100%; min-height: 52px; padding: 10px 14px; border: 2px solid var(--ink); border-radius: 0; background: #fff; color: var(--ink); font: inherit; }
.category-filters { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 16px; }
.category-filters button { min-height: 44px; padding: 8px 13px; border: 2px solid var(--ink); border-radius: 0; background: var(--paper); font-size: 14px; font-weight: 800; }
.category-filters button[aria-pressed="true"] { background: var(--blue); color: var(--paper-light); }
.playlist-launch { display: flex; flex-wrap: wrap; align-items: center; gap: 10px 16px; margin-top: 16px; }
.playlist-launch p { margin: 0; font-size: 13px; font-weight: 700; }
.playlist-start { background: var(--yellow); }
.results-status { margin: 14px 0 0; font-weight: 800; }
.no-results { padding: 30px 22px; border: var(--line); background: var(--yellow); text-align: center; }
.no-results h2 { font-family: var(--serif); font-size: 28px; }
.pagination { display: flex; flex-wrap: wrap; justify-content: center; gap: 9px; margin-top: 30px; }
.page-button[aria-current="page"] { background: var(--yellow); }
.detail-button:disabled { cursor: not-allowed; opacity: .55; }

@media (max-width: 1100px) {
  .works-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (max-width: 640px) {
  .works-grid { grid-template-columns: 1fr; gap: 20px; }
  .detail-button { width: 100%; }
}
</style>
