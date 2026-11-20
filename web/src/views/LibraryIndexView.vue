<script setup lang="ts">
import { computed, ref } from 'vue'
import ClLibraryMap from '@/components/ClLibraryMap.vue'
import { documentUrl, documentsForWork, governanceDocuments, researchDocuments } from '@/research/documents'
import { hallContent, hallRecords, recordSearchText, type ResearchHall } from '@/research/library'
import { researchSamples } from '@/research/samples'
import { hasResearchAudio, specialtyCatalog, workSpecialties } from '@/research/specialties'

type ResultKind = 'music' | ResearchHall | 'document'
interface LibraryResult {
  id: string
  kind: ResultKind
  title: string
  meta: string
  description: string
  to?: string
  href?: string
  action: string
  search: string
}

const query = ref('')
const kind = ref<'all' | ResultKind>('all')
const filters = [
  { value: 'all', label: '全部资料' },
  { value: 'music', label: '音乐作品' },
  { value: 'story', label: '故事' },
  { value: 'poetry', label: '古诗词' },
  { value: 'document', label: '研究文档' },
] as const
const hallCards = [
  { id: 'music', title: '儿童音乐馆', to: '/music', count: `${specialtyCatalog.length} 条作品目录`, note: `${researchSamples.length} 条主录音记录 · 8 个专题`, tone: 'music' },
  { id: 'story', title: '儿童故事馆', to: '/story', count: `${hallRecords('story').length} 条研究记录`, note: '9 个目录组 · 来源与五维状态', tone: 'story' },
  { id: 'poetry', title: '古诗词馆', to: '/poetry', count: `${hallRecords('poetry').length} 条研究记录`, note: '10 个专题 · 版本与资产线索', tone: 'poetry' },
] as const

const allResults = computed<LibraryResult[]>(() => [
  ...specialtyCatalog.map((work): LibraryResult => {
    const specialties = workSpecialties(work.id)
    const documents = documentsForWork(work.id)
    return {
      id: work.id,
      kind: 'music',
      title: work.title,
      meta: `${work.id} · ${specialties.map((item) => item.name).join(' / ')}`,
      description: `${work.type} · ${work.region}${work.note ? ` · ${work.note}` : ''}`,
      to: hasResearchAudio(work.id) ? `/works?work=${work.id}` : `/music/specialties/${specialties[0]?.id ?? 'childhood'}`,
      action: hasResearchAudio(work.id) ? '查看录音与资料' : '进入所属专题',
      search: [work.id, work.title, work.type, work.region, work.note, ...specialties.map((item) => item.name), ...documents.map((item) => item.title)].join(' '),
    }
  }),
  ...(['story', 'poetry'] as const).flatMap((hall) => hallRecords(hall).map((record): LibraryResult => ({
    id: record.id,
    kind: hall,
    title: record.title,
    meta: `${record.id} · ${hallContent[hall].title.split(' · ')[0]} · ${record.groupName}`,
    description: `${record.contributor || record.origin} · ${record.note}`,
    to: `/${hall}?q=${encodeURIComponent(record.id)}`,
    action: '查看研究记录',
    search: recordSearchText(record),
  }))),
  ...researchDocuments.map((document): LibraryResult => ({
    id: document.id,
    kind: 'document',
    title: document.title,
    meta: `研究文档 · ${document.updated}`,
    description: document.description,
    href: documentUrl(document.path),
    action: '阅读 GitHub 原文',
    search: [document.title, document.description, ...document.workTitles].join(' '),
  })),
])

const normalizedQuery = computed(() => query.value.trim().normalize('NFKC').toLocaleLowerCase('zh-CN'))
const filteredResults = computed(() => allResults.value.filter((result) => {
  const inKind = kind.value === 'all' || result.kind === kind.value
  return inKind && (!normalizedQuery.value || result.search.normalize('NFKC').toLocaleLowerCase('zh-CN').includes(normalizedQuery.value))
}))
const browsing = computed(() => Boolean(normalizedQuery.value || kind.value !== 'all'))
const visibleResults = computed(() => filteredResults.value.slice(0, 30))
const kindNames: Record<ResultKind, string> = { music: '音乐', story: '故事', poetry: '诗词', document: '档案' }

function searchFor(value: string): void {
  kind.value = 'all'
  query.value = value
}

function reset(): void {
  query.value = ''
  kind.value = 'all'
}
</script>

<template>
  <div class="library-index">
    <section class="shell hero" aria-labelledby="page-title">
      <p class="hero-label">童年书房 · 资料总览</p>
      <h1 id="page-title">从一份资料，<br>走进整座书房。</h1>
      <p class="hero-desc">把作品、专题、录音、谱面、来源与研究档案放在一起查找。这里连接的是现有研究资料，不把线索包装成已公开发布的内容。</p>
      <div class="hero-actions">
        <a class="button button-primary" href="#search">开始检索 <span aria-hidden="true">↓</span></a>
        <a class="button" href="/research.html">打开研究状态看板</a>
      </div>
    </section>

    <section class="shell halls" aria-labelledby="halls-title">
      <div class="section-heading"><h2 id="halls-title">三座馆，共用一套资料脉络</h2><p>先按内容进入场馆，也可以直接搜索作品名、作者、编号或研究批次。</p></div>
      <div class="hall-grid">
        <RouterLink v-for="hall in hallCards" :key="hall.id" class="hall-card" :class="`is-${hall.tone}`" :to="hall.to">
          <h3>{{ hall.title }}</h3><strong>{{ hall.count }}</strong><p>{{ hall.note }}</p><span>进入场馆 →</span>
        </RouterLink>
      </div>
    </section>

    <section class="shell search-section" id="search" aria-labelledby="search-title">
      <div class="search-box">
        <h2 id="search-title">跨馆查找</h2>
        <label for="library-query">作品、作者、目录编号或研究文档</label>
        <div class="search-line">
          <input id="library-query" v-model="query" type="search" placeholder="例如：小燕子、女娲补天、批次 04" autocomplete="off">
          <button v-if="browsing" class="button" type="button" @click="reset">清除</button>
        </div>
        <div class="filters" role="group" aria-label="资料类型筛选">
          <button v-for="filter in filters" :key="filter.value" type="button" :aria-pressed="kind === filter.value" @click="kind = filter.value">{{ filter.label }}</button>
        </div>
        <div v-if="!browsing" class="quick-search"><span>试着查找：</span><button type="button" @click="searchFor('小燕子')">小燕子</button><button type="button" @click="searchFor('女娲补天')">女娲补天</button><button type="button" @click="searchFor('批次 04')">批次 04</button></div>
      </div>

      <div v-if="browsing" class="results" aria-live="polite">
        <div class="results-head"><h3>检索结果</h3><p>共 {{ filteredResults.length }} 条{{ filteredResults.length > 30 ? '，当前显示前 30 条；请继续缩小范围' : '' }}</p></div>
        <div v-if="visibleResults.length" class="result-list">
          <article v-for="result in visibleResults" :key="`${result.kind}-${result.id}`" class="result-card" :class="`is-${result.kind}`">
            <div class="result-copy"><span class="result-kind">{{ kindNames[result.kind] }}</span><h4>{{ result.title }}</h4><p class="result-meta">{{ result.meta }}</p><p>{{ result.description }}</p></div>
            <RouterLink v-if="result.to" :to="result.to">{{ result.action }} →</RouterLink>
            <a v-else :href="result.href" target="_blank" rel="noopener noreferrer">{{ result.action }} ↗</a>
          </article>
        </div>
        <div v-else class="empty"><h3>没有找到匹配资料</h3><p>换一个作品名或目录编号，或回到全部资料重新查找。</p><button class="button button-primary" type="button" @click="reset">重新浏览</button></div>
      </div>
    </section>

    <section v-if="!browsing" class="shell documents" aria-labelledby="documents-title">
      <div class="section-heading"><h2 id="documents-title">最新研究档案</h2><p>文档原文保存在 GitHub；页面只建立入口和作品关系，不复制档案正文。</p></div>
      <div class="document-grid">
        <a v-for="document in researchDocuments.filter((document) => document.id.startsWith('songs-') && document.id !== 'songs-500')" :key="document.id" class="document-card" :href="documentUrl(document.path)" target="_blank" rel="noopener noreferrer">
          <span>{{ document.updated }}</span><h3>{{ document.title }}</h3><p>{{ document.description }}</p><template v-if="document.workTitles.length"><b>关联作品</b><p>{{ document.workTitles.join(' · ') }}</p></template><strong>阅读研究原文 ↗</strong>
        </a>
      </div>
    </section>

    <section class="shell governance" aria-labelledby="governance-title">
      <div><h2 id="governance-title">资料为什么这样串联</h2><p>作品身份、具体版本、媒体文件和使用许可不是同一件事。每个入口都保留来源与研究边界，便于继续核验。</p></div>
      <nav aria-label="项目治理文档"><a v-for="document in governanceDocuments" :key="document.path" :href="documentUrl(document.path)" target="_blank" rel="noopener noreferrer"><b>{{ document.title }} ↗</b><span>{{ document.description }}</span></a></nav>
    </section>

    <ClLibraryMap />
  </div>
</template>

<style scoped>
.hero { padding-block: 60px 48px; }
.hero-label { color: var(--red); font-size: 15px; font-weight: 900; }
.hero h1 { max-width: 900px; margin: 10px 0 20px; font-family: var(--serif); font-size: clamp(44px, 6vw, 76px); line-height: 1.12; letter-spacing: -.04em; }
.hero-desc { max-width: 780px; font-size: 18px; line-height: 1.9; }
.hero-actions { display: flex; flex-wrap: wrap; gap: 14px; margin-top: 26px; }
.section-heading { margin-bottom: 24px; }
.section-heading h2, .search-box h2, .governance h2 { font-family: var(--serif); font-size: clamp(28px, 4vw, 38px); margin-bottom: 8px; }
.section-heading p { color: var(--ink-soft); }
.halls { padding-block: 16px 40px; }
.hall-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 20px; }
.hall-card { display: flex; flex-direction: column; min-height: 230px; padding: 24px; border: var(--line); box-shadow: 5px 5px 0 var(--ink); /* taste-skill-ignore: 保留原型场馆卡硬阴影。 */ text-decoration: none; transition: translate .15s ease; }
.hall-card:hover { translate: -2px -2px; }
.hall-card.is-music { background: #fdf1c9; }
.hall-card.is-story { background: #fbe3dd; }
.hall-card.is-poetry { background: #e2ebd7; }
.hall-card h3 { font-family: var(--serif); font-size: 27px; }
.hall-card strong { margin-block: 12px 5px; font-size: 20px; }
.hall-card p { color: var(--ink-soft); }
.hall-card > span { margin-top: auto; font-weight: 900; }
.search-section { padding-block: 24px 42px; scroll-margin-top: 100px; }
.search-box { padding: 26px; border: var(--line); background: var(--yellow); box-shadow: var(--shadow); /* taste-skill-ignore: 保留原型检索面板硬阴影。 */ }
.search-box label { display: block; margin: 18px 0 8px; font-weight: 900; }
.search-line { display: flex; gap: 12px; }
.search-line input { flex: 1; min-width: 0; min-height: 54px; padding: 10px 14px; border: 2px solid var(--ink); background: var(--paper-light); font: inherit; }
.filters { display: flex; flex-wrap: wrap; gap: 9px; margin-top: 16px; }
.filters button, .quick-search button { min-height: 44px; padding: 7px 12px; border: 2px solid var(--ink); background: var(--paper-light); font-weight: 800; }
.filters button[aria-pressed='true'] { background: var(--blue); color: var(--paper-light); }
.quick-search { display: flex; flex-wrap: wrap; align-items: center; gap: 9px; margin-top: 18px; font-size: 14px; }
.quick-search button { min-height: 38px; background: transparent; }
.results { margin-top: 28px; }
.results-head { display: flex; flex-wrap: wrap; align-items: baseline; justify-content: space-between; gap: 6px 20px; margin-bottom: 14px; }
.results-head h3 { font-family: var(--serif); font-size: 27px; }
.results-head p { color: var(--ink-soft); }
.result-list { display: grid; gap: 12px; }
.result-card { display: flex; align-items: center; gap: 20px; padding: 18px 20px; border: var(--line); border-left: 10px solid var(--blue); background: var(--paper-light); }
.result-card.is-music { border-left-color: var(--red); }
.result-card.is-story { border-left-color: var(--brown); }
.result-card.is-poetry { border-left-color: var(--green); }
.result-copy { flex: 1; min-width: 0; }
.result-kind { color: var(--blue); font-size: 13px; font-weight: 900; }
.result-card h4 { margin: 3px 0; font-family: var(--serif); font-size: 23px; }
.result-card p { margin: 3px 0; font-size: 14px; line-height: 1.65; }
.result-card .result-meta { font-weight: 800; }
.result-card > a { flex: 0 0 auto; font-weight: 900; text-underline-offset: 4px; }
.empty { padding: 28px; border: var(--line); background: var(--paper-light); text-align: center; }
.empty h3 { font-family: var(--serif); font-size: 26px; }
.documents { padding-block: 20px 42px; }
.document-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 18px; }
.document-card { display: flex; flex-direction: column; padding: 22px; border: var(--line); background: var(--paper-light); box-shadow: 4px 4px 0 var(--ink); /* taste-skill-ignore: 保留原型档案卡硬阴影。 */ text-decoration: none; }
.document-card > span { color: var(--red); font-size: 13px; font-weight: 900; }
.document-card h3 { font-family: var(--serif); font-size: 23px; margin-block: 8px; }
.document-card p { color: var(--ink-soft); font-size: 14px; line-height: 1.7; }
.document-card b { margin-top: 8px; }
.document-card strong { margin-top: auto; padding-top: 14px; }
.governance { display: grid; grid-template-columns: minmax(240px, .8fr) minmax(0, 1.2fr); gap: 40px; padding-block: 36px; }
.governance > div > p { line-height: 1.8; }
.governance nav { display: grid; gap: 10px; }
.governance a { display: grid; gap: 4px; padding: 14px 18px; background: #dde5f6; border: 2px solid var(--ink); text-decoration: none; }
.governance a span { font-size: 14px; }
@media (max-width: 850px) { .hall-grid { grid-template-columns: 1fr; } .hall-card { min-height: 190px; } .governance { grid-template-columns: 1fr; gap: 12px; } }
@media (max-width: 640px) { .hero { padding-block: 38px 30px; } .hero h1 { font-size: 43px; } .search-box { padding: 20px 16px; } .search-line { flex-direction: column; } .document-grid { grid-template-columns: 1fr; } .result-card { align-items: flex-start; flex-direction: column; gap: 8px; } }
</style>
