<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import ClTrackDetailDialog from '@/components/ClTrackDetailDialog.vue'
import { useAudioPlayer } from '@/composables/useAudioPlayer'
import { getSpecialty, isSpecialtyId, workSpecialties, type SpecialtyId } from '@/research/specialties'
import {
  actionLabel,
  assetUrl,
  researchSamples,
  sampleCategory,
  sourceLabel,
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
  { value: 'internal', label: '经典原声 · 权利待核验' },
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
      <nav class="works-context" aria-label="资料导航"><RouterLink to="/library">← 资料总览</RouterLink><RouterLink to="/music">儿童音乐馆与专题</RouterLink></nav>
      <div v-if="activeTopic" class="topic-context" aria-label="当前专题筛选">
        <span>来自音乐专题</span>
        <strong>{{ activeTopic.name }}</strong>
        <RouterLink :to="`/music/specialties/${activeTopic.id}`">返回专题档案</RouterLink>
        <button type="button" @click="topicId = null">查看全部录音</button>
      </div>
      <h1>{{ activeTopic ? `${activeTopic.name} · 已有录音` : '曲目列表' }}</h1>
      <p>
        内部研究试听，共 {{ samples.length }} 条主录音记录。查看封面、歌词谱面、录音版本、来源与权利状态；
        本页不是已发布曲库，也不代表数据库已经导入。
      </p>
      <p class="rights-note">权利待核验的录音仅限内部研究试听；开放许可仅对应各条目注明的具体录音。</p>
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

    <div v-if="pageItems.length" class="works-grid" aria-label="内部研究录音列表">
      <article v-for="sample in pageItems" :key="sample.id" class="work-card">
        <div class="card-top">
          <span class="id-tag">{{ sample.id }}</span>
          <span class="status-badge">{{ sample.license }}</span>
        </div>
        <div class="sample-card-intro">
          <img
            class="sample-card-cover"
            :src="assetUrl(sample.materials.cover)"
            :alt="sample.materials.coverAlt"
            width="800"
            height="600"
            loading="lazy"
          >
          <div class="sample-card-copy">
            <h2>{{ sample.workTitle }}</h2>
            <p class="card-group">{{ sample.kind }}</p>
          </div>
        </div>
        <dl class="card-meta">
          <div><dt>录音</dt><dd>{{ sample.attribution }}</dd></div>
          <div><dt>来源</dt><dd>{{ sourceLabel(sample) }}</dd></div>
          <div><dt>素材</dt><dd>{{ sample.materials.lyrics?.length ? '歌词与谱面已收录' : '封面已收录 · 歌词待核验' }}</dd></div>
        </dl>
        <div class="card-footer">
          <button class="detail-button" type="button" :data-work-detail="sample.id" @click="detailSample = sample">查看详情</button>
          <button
            class="detail-button audio-action"
            type="button"
            data-audio-play="true"
            :data-work-id="sample.id"
            :aria-label="`${actionLabel(sample)}：${sample.workTitle}`"
            @click="playSample(sample, sample)"
          >
            {{ actionLabel(sample) }}
          </button>
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
.rights-note { padding: 12px 14px; border-left: 5px solid var(--red); background: var(--paper-light); font-weight: 800; }
.works-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 22px; }
.work-card {
  position: relative;
  min-width: 0;
  display: flex;
  flex-direction: column;
  padding: 18px 18px 16px 29px;
  border: var(--line);
  background: var(--paper-light);
  box-shadow: 5px 5px 0 var(--ink); /* taste-skill-ignore: 保留原型卡片硬阴影。 */
}
.work-card::before {
  content: "";
  position: absolute;
  inset: 0 auto 0 0;
  width: 11px;
  border-right: 3px solid var(--ink);
  background: var(--red);
}
.card-top { display: flex; flex-wrap: wrap; align-items: center; gap: 8px 10px; margin-bottom: 12px; }
.id-tag { display: inline-flex; align-items: center; min-height: 30px; padding: 3px 9px; border: 2px solid var(--ink); background: var(--yellow); font-size: 13px; font-weight: 900; font-variant-numeric: tabular-nums; }
.status-badge { display: inline-flex; align-items: center; min-height: 30px; max-width: 100%; padding: 4px 9px; border: 2px solid currentColor; color: #7a2017; background: #f9ddd7; font-size: 12px; font-weight: 900; line-height: 1.4; overflow-wrap: anywhere; }
.work-card h2 { margin: 0 0 7px; font-family: var(--serif); font-size: 25px; font-weight: 900; line-height: 1.3; overflow-wrap: anywhere; }
.card-group { margin-bottom: 13px; font-size: 14px; font-weight: 800; line-height: 1.5; }
.card-meta { display: grid; gap: 7px; margin: 0 0 13px; }
.card-meta div { display: grid; grid-template-columns: 46px minmax(0, 1fr); gap: 8px; }
.card-meta dt { font-size: 13px; font-weight: 800; }
.card-meta dd { margin: 0; font-size: 16px; line-height: 1.5; overflow-wrap: anywhere; }
.card-footer { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 10px; margin-top: auto; padding-top: 13px; border-top: 2px solid var(--ink); }
.detail-button { min-height: 44px; flex: 0 0 auto; padding: 8px 12px; border: 2px solid var(--ink); border-radius: 0; background: var(--paper-light); box-shadow: 3px 3px 0 var(--ink); /* taste-skill-ignore: 保留原型按钮硬阴影。 */ font-size: 14px; font-weight: 900; }
.audio-action { background: var(--yellow); }
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
.sample-card-intro { display: grid; grid-template-columns: 104px minmax(0, 1fr); align-items: start; gap: 14px; margin-bottom: 13px; }
.sample-card-copy { min-width: 0; }
.sample-card-cover { width: 104px; height: auto; aspect-ratio: 4 / 3; display: block; object-fit: cover; border: 2px solid var(--ink); background: var(--paper); transform: rotate(-1.5deg); }
.sample-card-intro .card-group { margin-bottom: 0; }
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
  .work-card { padding-right: 16px; }
  .detail-button { width: 100%; }
}
</style>
