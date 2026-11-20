<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import ClLibraryMap from '@/components/ClLibraryMap.vue'
import {
  getSpecialty,
  hasResearchAudio,
  isSpecialtyId,
  specialtyDefinitions,
  specialtyWorks,
} from '@/research/specialties'

const route = useRoute()
const specialty = computed(() => {
  const id = String(route.params.id ?? '')
  return isSpecialtyId(id) ? getSpecialty(id) : undefined
})
const works = computed(() => specialty.value ? specialtyWorks(specialty.value.id) : [])
const currentIndex = computed(() => specialty.value ? specialtyDefinitions.findIndex((item) => item.id === specialty.value?.id) : -1)
const previous = computed(() => currentIndex.value >= 0 ? specialtyDefinitions[(currentIndex.value + specialtyDefinitions.length - 1) % specialtyDefinitions.length] : undefined)
const next = computed(() => currentIndex.value >= 0 ? specialtyDefinitions[(currentIndex.value + 1) % specialtyDefinitions.length] : undefined)
</script>

<template>
  <div v-if="specialty" class="specialty-page" :style="{ '--accent': `var(--${specialty.tone})` }">
    <nav class="shell crumb" aria-label="面包屑导航">
      <RouterLink to="/music">儿童音乐馆</RouterLink><span class="sep">/</span><span>{{ specialty.name }}</span>
    </nav>

    <section class="shell hero" aria-labelledby="page-title">
      <div class="hero-head">
        <span class="hero-num">{{ specialty.no }}</span>
        <div><h1 id="page-title">{{ specialty.name }}</h1><p class="hero-sub">{{ specialty.name }} · MUSIC SPECIALTY</p></div>
      </div>
      <p class="hero-desc">{{ specialty.description }}</p>
      <div class="hero-scope"><b>内容范围：</b>{{ specialty.scope }}　<b>编辑关注：</b>{{ specialty.focus }}</div>
    </section>

    <section class="shell works" aria-labelledby="works-title">
      <div class="works-head"><h2 id="works-title">候选作品</h2><span class="count">{{ works.length }} 首</span></div>
      <div class="works-grid">
        <component
          :is="hasResearchAudio(work.id) ? 'RouterLink' : 'article'"
          v-for="work in works"
          :key="work.id"
          class="work-card"
          :to="hasResearchAudio(work.id) ? { path: '/works', query: { work: work.id } } : undefined"
        >
          <span class="id">{{ work.id }}</span>
          <h3>{{ work.title }}</h3>
          <span class="type">{{ work.type }} · {{ work.region }}</span>
          <p v-if="work.note" class="note">{{ work.note }}</p>
          <span class="status">{{ hasResearchAudio(work.id) ? '查看研究录音 →' : '候选 · 待核验' }}</span>
        </component>
        <div v-if="works.length === 0" class="empty">
          <h3>当前暂无已登记曲目</h3>
          <p>本专题面向当代原创儿童音乐。候选作品须通过编辑评审与可追溯授权后逐首入库。</p>
        </div>
      </div>
    </section>

    <nav class="shell lib-peers" aria-label="八个专题横向导航">
      <div class="lib-peers-inner">
        <strong>音乐馆 · 八个专题串联</strong>
        <div class="lib-peer-list">
          <RouterLink v-for="item in specialtyDefinitions" :key="item.id" :to="`/music/specialties/${item.id}`" :aria-current="item.id === specialty.id ? 'page' : undefined">{{ item.no }} {{ item.name }}</RouterLink>
        </div>
        <div class="lib-peer-ends">
          <RouterLink v-if="previous" :to="`/music/specialties/${previous.id}`">← 上一专题：{{ previous.no }} {{ previous.name }}</RouterLink>
          <span class="spacer"></span>
          <RouterLink v-if="next" :to="`/music/specialties/${next.id}`">下一专题：{{ next.no }} {{ next.name }} →</RouterLink>
        </div>
      </div>
    </nav>

    <div class="shell back-band"><RouterLink class="button" to="/music">← 回到音乐馆</RouterLink></div>
    <section class="shell footnote" aria-label="专题边界"><h2 class="visually-hidden">专题边界</h2><p>本页面为儿童音乐馆专题策展页。候选作品仅为目录发现层，不构成法律意见，也不授予任何第三方内容的使用权。有研究录音的作品可进入内部曲目页查看来源与版本。</p></section>
    <ClLibraryMap current="music" />
  </div>
  <section v-else class="shell missing" aria-labelledby="missing-title">
    <h1 id="missing-title">没有找到这个音乐专题</h1>
    <p>专题地址可能不正确，请返回音乐馆重新选择。</p>
    <RouterLink class="button button-primary" to="/music">返回音乐馆</RouterLink>
  </section>
</template>

<style scoped>
.specialty-page { --accent: var(--red); }
.crumb { padding: 20px 0 0; }
.crumb a { text-decoration: none; font-weight: 700; font-size: 14px; }
.crumb a:hover { text-decoration: underline; }
.sep { margin: 0 8px; color: var(--ink-soft); }
.hero { padding-block: 30px 24px; }
.hero-head { display: flex; align-items: flex-end; gap: 20px; flex-wrap: wrap; }
.hero-num { font-family: var(--serif); font-size: 72px; font-weight: 900; line-height: 1; color: var(--accent); }
h1 { font-family: var(--serif); font-size: clamp(34px, 4vw, 48px); font-weight: 900; letter-spacing: -.02em; margin: 0; }
.hero-sub { margin: 6px 0 0; font-size: 15px; color: var(--ink-soft); letter-spacing: .06em; }
.hero-desc { max-width: 760px; margin-top: 18px; font-size: 17px; line-height: 1.9; }
.hero-scope { margin-top: 16px; padding: 14px 18px; border: 2px solid var(--ink); background: var(--paper-light); box-shadow: 4px 4px 0 var(--ink); /* taste-skill-ignore: 保留原型专题说明硬阴影。 */ font-size: 14px; }
.hero-scope b { color: var(--accent); }
.works { padding-block: 12px 48px; }
.works-head { display: flex; align-items: baseline; gap: 14px; margin-bottom: 20px; }
.works-head h2 { font-family: var(--serif); font-size: 26px; font-weight: 900; margin: 0; }
.count { font-weight: 800; color: var(--accent); }
.works-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; align-items: stretch; }
.work-card { display: flex; flex-direction: column; gap: 8px; text-align: left; border: var(--line); background: var(--paper-light); box-shadow: 5px 5px 0 var(--ink); /* taste-skill-ignore: 保留原型候选作品卡硬阴影。 */ padding: 16px 16px 14px; text-decoration: none; transition: translate .15s ease, box-shadow .15s ease; }
a.work-card:hover { translate: -2px -2px; box-shadow: 7px 7px 0 var(--ink); /* taste-skill-ignore: 保留原型候选卡悬停硬阴影。 */ }
.id { font-size: 11px; font-weight: 900; color: var(--blue); letter-spacing: .08em; }
.work-card h3 { margin: 0; font-family: var(--serif); font-size: 19px; font-weight: 900; line-height: 1.35; }
.type { font-size: 13px; color: var(--ink-soft); }
.note { font-size: 13px; color: var(--ink-soft); line-height: 1.55; margin: 0; }
.status { margin-top: auto; display: inline-flex; align-self: flex-start; padding: 2px 8px; border: 2px solid var(--ink); background: var(--yellow); font-size: 11px; font-weight: 800; }
.empty { grid-column: 1 / -1; padding: 40px; border: var(--line); background: var(--paper-light); text-align: center; }
.empty h3 { font-family: var(--serif); }
.empty p { margin: 0; font-size: 15px; color: var(--ink-soft); }
.lib-peers { padding-block: 6px 26px; }
.lib-peers-inner { border: var(--line); background: var(--paper-light); box-shadow: 4px 4px 0 var(--ink); /* taste-skill-ignore: 保留原型专题说明硬阴影。 */ padding: 16px 18px; }
.lib-peers-inner > strong { display: block; font-size: 13px; margin-bottom: 10px; }
.lib-peer-list { display: flex; flex-wrap: wrap; gap: 8px; }
.lib-peer-list a { padding: 5px 10px; border: 2px solid var(--ink); background: var(--paper-light); font-size: 12px; font-weight: 800; text-decoration: none; }
.lib-peer-list a:hover, .lib-peer-list a[aria-current='page'] { background: var(--yellow); }
.lib-peer-ends { display: flex; justify-content: space-between; gap: 12px; margin-top: 14px; font-size: 13px; font-weight: 800; }
.lib-peer-ends a { text-decoration: none; border-bottom: 2px solid var(--ink); }
.spacer { flex: 1; }
.back-band { padding-block: 12px 56px; }
.back-band .button { background: var(--accent); }
.footnote { padding-block: 4px 48px; }
.footnote p { max-width: 760px; font-size: 13px; color: var(--ink-soft); }
.missing { padding-block: 80px; }
.missing h1 { margin-bottom: 18px; }
@media (max-width: 900px) { .works-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 640px) { .works-grid { grid-template-columns: 1fr; } .hero-num { font-size: 56px; } .lib-peer-ends { flex-direction: column; } .spacer { display: none; } }
</style>
