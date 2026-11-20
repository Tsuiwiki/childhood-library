<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import ClLibraryMap from '@/components/ClLibraryMap.vue'
import ClResearchRecordCard from '@/components/ClResearchRecordCard.vue'
import {
  cleanResearchText,
  generatedOn,
  hallContent,
  hallGroups,
  hallRecords,
  hallStats,
  recordSearchText,
  statusModel,
  type ResearchHall,
} from '@/research/library'

const props = defineProps<{ hall: ResearchHall }>()
const query = ref('')
const group = ref('all')

const content = computed(() => hallContent[props.hall])
const groups = computed(() => hallGroups(props.hall))
const records = computed(() => hallRecords(props.hall))
const stats = computed(() => hallStats(props.hall))
const titleParts = computed(() => content.value.title.split(' · '))

const filteredRecords = computed(() => {
  const needle = query.value.trim().normalize('NFKC').toLocaleLowerCase('zh-CN')
  return records.value.filter((record) => {
    const inGroup = group.value === 'all' || record.group === group.value
    return inGroup && (!needle || recordSearchText(record).includes(needle))
  })
})

const visibleGroups = computed(() => groups.value
  .map((item) => ({
    ...item,
    records: filteredRecords.value.filter((record) => record.group === item.id),
  }))
  .filter((item) => item.records.length > 0))

function resetFilters() {
  query.value = ''
  group.value = 'all'
}

watch(() => props.hall, resetFilters)
</script>

<template>
  <div class="research-hall">
    <section class="shell hero" aria-labelledby="page-title">
      <span class="eyebrow"><!-- taste-skill-ignore: 保留原型旋转眉题。 -->{{ content.englishTitle }} · 研究目录</span>
      <h1 id="page-title">{{ titleParts[0] }} · <span class="accent">{{ titleParts[1] }}</span></h1>
      <p class="hero-desc">{{ content.description }}共 {{ stats.groups }} 个目录组、{{ stats.total }} 条研究记录。</p>
      <div class="hero-actions">
        <a class="button button-primary" href="/research.html">看研究资源库与五维状态 <span aria-hidden="true">→</span></a>
        <a class="button" href="#groups">按专题浏览</a>
      </div>
      <div class="stat-strip" aria-label="目录统计">
        <div class="stat-cell"><b>{{ stats.total }}</b><span>研究记录总数</span></div>
        <div class="stat-cell"><b>{{ stats.groups }}</b><span>目录组</span></div>
        <div class="stat-cell"><b>{{ stats.works }}</b><span>{{ content.recordsLabel }}</span></div>
        <div class="stat-cell"><b>{{ stats.special }}</b><span>{{ content.specialLabel }}</span></div>
      </div>
      <div class="notice"><b>这一页是研究资源库视图，不是儿童阅读页。</b>这里登记作品身份、文化来源、来源线索与待核验事项。所有记录当前均为研究草稿、质量未审；页面不展示正文、译文、插画或音视频。研究完成不等于获得公开传播许可。</div>
    </section>

    <section class="shell toolbar" id="groups" aria-label="目录筛选">
      <div class="toolbar-inner">
        <label :for="`${hall}-search`">检索目录</label>
        <input :id="`${hall}-search`" v-model="query" type="search" placeholder="输入作品、作者或编号" autocomplete="off">
        <label :for="`${hall}-group`">专题</label>
        <select :id="`${hall}-group`" v-model="group">
          <option value="all">全部专题</option>
          <option v-for="item in groups" :key="item.id" :value="item.id">{{ item.no }} {{ item.name }}</option>
        </select>
        <button v-if="query || group !== 'all'" class="reset" type="button" @click="resetFilters">清除筛选</button>
        <span class="result-count" role="status" aria-live="polite">显示 {{ filteredRecords.length }} / {{ stats.total }} 条</span>
      </div>
      <nav class="group-nav" aria-label="专题快捷导航">
        <a v-for="item in groups" :key="item.id" :href="`#group-${item.id}`">{{ item.no }} {{ item.name }}</a>
      </nav>
    </section>

    <section
      v-for="item in visibleGroups"
      :id="`group-${item.id}`"
      :key="item.id"
      class="shell group-section"
      :data-group-section="item.id"
    >
      <div class="group-head">
        <span class="no" :style="{ color: item.accent }">{{ item.no }} · {{ content.englishTitle }} · 研究目录</span>
        <h2>{{ item.name }}<small>{{ item.records.length }} 条线索 / 规划目标 {{ item.target }} 条</small></h2>
        <p>{{ cleanResearchText(item.desc) }}</p>
        <p class="focus">编辑关注：{{ item.focus }}</p>
      </div>
      <div class="rec-grid">
        <ClResearchRecordCard v-for="record in item.records" :key="record.id" :record="record" />
      </div>
    </section>

    <section v-if="filteredRecords.length === 0" class="shell empty" aria-labelledby="empty-title">
      <h2 id="empty-title">没有匹配的研究记录</h2>
      <p>可以更换关键词，或清除专题筛选后重新浏览。</p>
      <button class="button button-primary" type="button" @click="resetFilters">查看全部记录</button>
    </section>

    <section class="shell model-band" aria-labelledby="model-title">
      <div class="model-box">
        <h2 id="model-title">统一状态模型 · 五个维度互不替代</h2>
        <p>研究完成不等于版权已确认；版权确认不等于质量审核通过；内容适合儿童也不等于获得公开传播许可。依据《项目顶层设计原则》§6 与《数据模型设计》§4。</p>
        <div class="model-table-wrap">
          <table class="model-table">
            <thead><tr><th>字段</th><th>建议状态</th><th>回答的问题</th></tr></thead>
            <tbody><tr v-for="row in statusModel" :key="row.field"><td><code>{{ row.field }}</code></td><td>{{ row.values }}</td><td>{{ row.question }}</td></tr></tbody>
          </table>
        </div>
        <a class="button" href="/research.html#dashboard">查看研究状态看板</a>
      </div>
    </section>

    <ClLibraryMap :current="hall" />

    <footer class="research-footer">
      <div class="shell">
        <p>{{ content.title }}研究目录 · 依据项目顶层原则与统一数据模型建立，{{ generatedOn }} 生成。</p>
        <p>本页为内部研究与原型展示视图。候选目录不构成法律意见，也不授予任何第三方内容的使用权；具体公开、复制、翻译、改编、插画和音频使用，按目标发布地域、具体版本和实际许可逐项核实。</p>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.hero { padding-block: 48px 26px; }
.hero h1 { font-family: var(--serif); font-size: clamp(40px, 5vw, 62px); font-weight: 900; line-height: 1.16; letter-spacing: -.04em; margin-bottom: 16px; }
.accent { color: var(--red); }
.hero-desc { max-width: 760px; font-size: 17px; line-height: 1.9; margin-bottom: 22px; }
.hero-actions { display: flex; flex-wrap: wrap; gap: 14px; }
.stat-strip { display: grid; grid-template-columns: repeat(4, 1fr); border: var(--line); background: var(--paper-light); box-shadow: 5px 5px 0 var(--blue); /* taste-skill-ignore: 保留原型统计条硬阴影。 */ margin-top: 30px; }
.stat-cell { padding: 16px 18px; border-right: 2px solid var(--ink); }
.stat-cell:last-child { border-right: 0; }
.stat-cell b { display: block; font-family: var(--serif); font-size: 27px; font-weight: 900; line-height: 1.2; }
.stat-cell span { font-size: 12px; color: var(--ink-soft); }
.notice { margin-top: 24px; padding: 14px 18px; border: 2px solid var(--ink); background: #dde5f6; box-shadow: 4px 4px 0 var(--ink); /* taste-skill-ignore: 保留原型研究面板硬阴影。 */ font-size: 14px; line-height: 1.75; }
.notice b { color: var(--blue); }
.toolbar { padding-block: 26px 8px; scroll-margin-top: 104px; }
.toolbar-inner { display: flex; flex-wrap: wrap; gap: 12px; align-items: center; padding: 14px 16px; border: var(--line); background: var(--paper-light); box-shadow: 4px 4px 0 var(--ink); /* taste-skill-ignore: 保留原型研究面板硬阴影。 */ }
.toolbar label { font-size: 13px; font-weight: 800; }
.toolbar input, .toolbar select { min-height: 42px; padding: 8px 12px; border: 2px solid var(--ink); background: var(--paper-light); font-size: 14px; }
.toolbar input { flex: 1 1 240px; min-width: 0; }
.result-count { margin-left: auto; font-size: 13px; font-weight: 800; }
.reset { min-height: 42px; padding: 6px 12px; border: 2px solid var(--ink); background: var(--yellow); font-size: 13px; font-weight: 800; }
.group-nav { padding-block: 16px 4px; display: flex; flex-wrap: wrap; gap: 8px; }
.group-nav a { padding: 5px 11px; border: 2px solid var(--ink); background: var(--paper-light); box-shadow: 2px 2px 0 var(--ink); /* taste-skill-ignore: 保留原型专题快捷链接硬阴影。 */ font-size: 12px; font-weight: 800; text-decoration: none; }
.group-nav a:hover { background: var(--yellow); }
.group-section { padding-block: 26px 12px; scroll-margin-top: 104px; }
.group-head { border-bottom: 2px dashed var(--ink); padding-bottom: 12px; margin-bottom: 20px; }
.no { font-size: 12px; font-weight: 900; letter-spacing: .12em; }
.group-head h2 { font-family: var(--serif); font-size: clamp(25px, 3vw, 32px); font-weight: 900; margin: 4px 0 6px; }
.group-head h2 small { font-family: var(--sans); font-size: 14px; font-weight: 800; margin-left: 10px; color: var(--ink-soft); }
.group-head p { margin: 0; font-size: 14px; color: var(--ink-soft); max-width: 900px; }
.group-head .focus { margin-top: 6px; font-size: 13px; font-weight: 800; }
.rec-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; align-items: start; }
.empty { margin-block: 32px; padding: 32px; border: var(--line); background: var(--paper-light); box-shadow: var(--shadow); /* taste-skill-ignore: 保留原型空结果与状态模型硬阴影。 */ }
.empty h2 { font-family: var(--serif); }
.model-band { padding-block: 30px 20px; }
.model-box { border: var(--line); background: var(--paper-light); box-shadow: var(--shadow); /* taste-skill-ignore: 保留原型空结果与状态模型硬阴影。 */ padding: 24px 24px 18px; }
.model-box h2 { font-family: var(--serif); font-size: 27px; font-weight: 900; margin-bottom: 6px; }
.model-box > p { font-size: 14px; color: var(--ink-soft); margin-bottom: 16px; }
.model-table-wrap { overflow-x: auto; }
.model-table { width: 100%; min-width: 650px; border-collapse: collapse; font-size: 13px; }
.model-table th, .model-table td { border: 2px solid var(--ink); padding: 8px 10px; text-align: left; vertical-align: top; }
.model-table th { background: var(--yellow); font-weight: 900; }
.model-table code { font-family: monospace; font-weight: 800; }
.model-box .button { margin-top: 18px; }
.research-footer { margin-top: 34px; padding-block: 30px 40px; border-top: var(--line); background: var(--ink); color: var(--paper-light); }
.research-footer p { margin: 0; font-size: 13px; }
@media (max-width: 1000px) { .rec-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 640px) { .stat-strip { grid-template-columns: repeat(2, 1fr); } .stat-cell:nth-child(2) { border-right: 0; } .stat-cell:nth-child(-n+2) { border-bottom: 2px solid var(--ink); } .rec-grid { grid-template-columns: 1fr; } .hero { padding-block: 34px 20px; } .hero h1 { font-size: clamp(34px, 10vw, 48px); } .model-box { padding: 18px 14px 14px; } .result-count { margin-left: 0; width: 100%; } }
</style>
