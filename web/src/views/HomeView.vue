<script setup lang="ts">
import { computed } from 'vue'
import ClLibraryMap from '@/components/ClLibraryMap.vue'
import { useAudioPlayer } from '@/composables/useAudioPlayer'
import { audioSourceLinks } from '@/research/audioLinks'
import { catalogStats } from '@/research/catalog'
import { assetUrl, researchSamples, toPlayerTrack, type ResearchSample } from '@/research/samples'
import { hallRecords } from '@/research/library'
import { specialtyCatalog } from '@/research/specialties'

const { playTrack, selectedTrack } = useAudioPlayer()

const featuredIds = [
  'CN-C01', 'CN-C03', 'CN-C06', 'CN-C07',
  'CN-C10', 'CN-C11', 'CN-C14', 'CN-C20',
]
const featured = computed<ResearchSample[]>(() =>
  featuredIds
    .map((id) => researchSamples.find((sample) => sample.id === id))
    .filter((sample): sample is ResearchSample => Boolean(sample)),
)

const highlights = [
  { value: catalogStats.total, label: '首公开目录', to: '/music/catalog' },
  { value: researchSamples.length, label: '首可试听录音', to: '/works' },
  { value: audioSourceLinks.length, label: '条音源入口', to: '/music/sources' },
  { value: specialtyCatalog.length, label: '条作品档案', to: '/library' },
]

const halls = [
  { key: 'music', name: '儿童音乐馆', to: '/music', count: `${specialtyCatalog.length} 条作品目录`, note: `${researchSamples.length} 首可试听录音 · 8 个专题` },
  { key: 'story', name: '儿童故事馆', to: '/story', count: `${hallRecords('story').length} 条研究记录`, note: '神话、民间故事、童话与寓言' },
  { key: 'poetry', name: '古诗词馆', to: '/poetry', count: `${hallRecords('poetry').length} 条研究记录`, note: '唐诗、宋词与儿童诗词启蒙' },
] as const

function listen(sample: ResearchSample): void {
  playTrack(toPlayerTrack(sample, sample))
}

function isPlaying(sample: ResearchSample): boolean {
  return selectedTrack.value?.id === sample.id && selectedTrack.value?.source === `/audio/${sample.file}`
}
</script>

<template>
  <div class="home-page">
    <section class="shell hero" aria-labelledby="home-title">
      <span class="eyebrow"><!-- taste-skill-ignore: 保留原型旋转眉题。 -->童年书房 · CHILDHOOD LIBRARY</span>
      <h1 id="home-title">把值得一听再听的儿歌，<br><span class="accent">一首一首收进来。</span></h1>
      <p class="hero-desc">从《让我们荡起双桨》到《小燕子》，这里收着真实录音、公开目录与可追溯的版本线索。挑一首，先听听着。</p>
      <div class="hero-actions">
        <RouterLink class="button button-primary" to="/works">开始听歌 <span aria-hidden="true">→</span></RouterLink>
        <RouterLink class="button" to="/music/catalog">翻百年儿歌目录</RouterLink>
      </div>
    </section>

    <section class="shell highlight-strip" aria-label="书房内容概览">
      <RouterLink v-for="item in highlights" :key="item.label" class="highlight" :to="item.to">
        <strong>{{ item.value }}</strong><span>{{ item.label }}</span>
      </RouterLink>
    </section>

    <section class="shell section-block featured" aria-labelledby="featured-title">
      <div class="section-heading">
        <h2 id="featured-title">现在可以听</h2>
        <p>八首已有研究录音的经典儿歌。点封面看详情，或直接试听。</p>
      </div>
      <div class="work-grid">
        <article v-for="sample in featured" :key="sample.id" class="work-card" :data-work="sample.id">
          <RouterLink class="work-cover" :to="{ path: '/works', query: { work: sample.id } }" :aria-label="`查看《${sample.workTitle}》详情`">
            <img :src="assetUrl(sample.materials.cover)" :alt="sample.materials.coverAlt" loading="lazy">
          </RouterLink>
          <div class="work-body">
            <h3>{{ sample.workTitle }}</h3>
            <p class="work-credit">{{ sample.author || sample.kind }}</p>
            <p class="work-meta">{{ sample.durationLabel ?? '时长待核' }}</p>
            <div class="work-actions">
              <button
                type="button"
                class="play-button"
                :data-play="sample.id"
                :aria-label="`试听《${sample.workTitle}》`"
                :aria-pressed="isPlaying(sample)"
                @click="listen(sample)"
              >{{ isPlaying(sample) ? '正在播放' : '试听' }} <span aria-hidden="true">▶</span></button>
              <RouterLink :to="{ path: '/works', query: { work: sample.id } }">看详情 →</RouterLink>
            </div>
          </div>
        </article>
      </div>
    </section>

    <section class="shell section-block halls" aria-labelledby="halls-title">
      <div class="section-heading">
        <h2 id="halls-title">三座馆</h2>
        <p>音乐、故事与诗词，各自有目录，也共用一套作品脉络。</p>
      </div>
      <div class="hall-grid">
        <RouterLink v-for="hall in halls" :key="hall.key" class="hall-card" :class="`is-${hall.key}`" :to="hall.to">
          <span class="hall-name">{{ hall.name }}</span>
          <strong>{{ hall.count }}</strong>
          <p>{{ hall.note }}</p>
          <span class="hall-go">进入场馆 <span aria-hidden="true">→</span></span>
        </RouterLink>
      </div>
    </section>

    <section class="shell section-block explore" aria-labelledby="explore-title">
      <div class="explore-band">
        <div>
          <h2 id="explore-title">还想找更多？</h2>
          <p>《中国儿童歌曲百年经典》已核对 {{ catalogStats.total }} 首公开目录，另有 {{ audioSourceLinks.length }} 条外部音源入口。没有录音的作品如实标为待采集，不摆空播放按钮。</p>
        </div>
        <div class="explore-actions">
          <RouterLink class="button" to="/music/catalog">百年儿歌目录</RouterLink>
          <RouterLink class="button" to="/music/sources">音源链接</RouterLink>
          <RouterLink class="button" to="/library">跨馆检索</RouterLink>
        </div>
      </div>
    </section>

    <section class="shell section-block boundary" aria-label="来源与使用说明">
      <details>
        <summary>关于来源、版本与权利</summary>
        <p>本页录音用于内部研究试听；外部音源只跳原站，不提供下载或再分发。每条目录记录保留其公开目录行号，可在 GitHub 独立复核。原设计稿仍可<a href="/dir-3.html">单独打开</a>。</p>
      </details>
    </section>

    <ClLibraryMap />
  </div>
</template>

<style scoped>
.home-page { --page-width: 1240px; }
.home-page > .shell { width: min(calc(100% - 48px), var(--page-width)); }
.hero { padding-block: 58px 34px; }
.eyebrow { display: inline-block; font-size: 12px; font-weight: 900; letter-spacing: .14em; }
.hero h1 { margin: 14px 0 16px; font-family: var(--serif); font-size: clamp(38px, 5.4vw, 66px); font-weight: 900; line-height: 1.18; letter-spacing: -.03em; }
.accent { color: var(--red); }
.hero-desc { max-width: 640px; margin-bottom: 26px; font-size: 18px; line-height: 1.9; }
.hero-actions { display: flex; flex-wrap: wrap; gap: 16px; }
.highlight-strip { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 14px; margin-bottom: 12px; }
.highlight { display: flex; flex-direction: column; gap: 2px; padding: 16px 18px; border: var(--line); background: var(--paper-light); box-shadow: 4px 4px 0 var(--ink); /* taste-skill-ignore: 沿用原型硬阴影。 */ text-decoration: none; }
.highlight:hover { background: var(--yellow); }
.highlight strong { font-family: var(--serif); font-size: 32px; line-height: 1.15; }
.highlight span { font-size: 13px; font-weight: 800; color: var(--ink-soft); }
.section-block { padding-block: 30px 20px; }
.section-heading { margin-bottom: 22px; }
.section-heading h2 { margin-bottom: 6px; font-family: var(--serif); font-size: clamp(26px, 3vw, 34px); font-weight: 900; }
.section-heading p { margin: 0; color: var(--ink-soft); font-size: 15px; }
.work-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 18px; }
.work-card { min-width: 0; display: flex; flex-direction: column; border: var(--line); background: var(--paper-light); box-shadow: 5px 5px 0 var(--ink); /* taste-skill-ignore: 沿用原型作品卡硬阴影。 */ }
.work-cover { display: block; aspect-ratio: 4 / 3; overflow: hidden; border-bottom: var(--line); background: var(--paper); }
.work-cover img { display: block; width: 100%; height: 100%; object-fit: cover; }
.work-body { display: flex; flex: 1; flex-direction: column; padding: 14px 14px 16px; }
.work-body h3 { margin: 0 0 6px; font-family: var(--serif); font-size: 21px; font-weight: 900; line-height: 1.35; overflow-wrap: anywhere; }
.work-credit { margin: 0 0 4px; font-size: 13px; font-weight: 800; line-height: 1.55; }
.work-meta { margin: 0 0 14px; font-size: 12px; color: var(--ink-soft); }
.work-actions { display: flex; flex-wrap: wrap; align-items: center; gap: 8px 14px; margin-top: auto; padding-top: 12px; border-top: 2px dashed var(--ink); font-size: 13px; font-weight: 800; }
.play-button { min-height: 42px; padding: 7px 12px; border: 2px solid var(--ink); border-radius: 0; background: var(--yellow); font-size: 13px; font-weight: 900; }
.play-button[aria-pressed="true"] { background: var(--green); color: var(--paper-light); }
.work-actions a { min-height: 42px; display: inline-flex; align-items: center; text-underline-offset: 4px; }
.hall-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 18px; }
.hall-card { min-width: 0; display: flex; flex-direction: column; gap: 6px; padding: 20px 18px; border: var(--line); box-shadow: 5px 5px 0 var(--ink); /* taste-skill-ignore: 沿用原型场馆卡硬阴影。 */ text-decoration: none; }
.hall-card:hover { translate: -2px -2px; }
.is-music { background: #fdf1c9; }
.is-story { background: #fbe3dd; }
.is-poetry { background: #e2ebd7; }
.hall-name { font-family: var(--serif); font-size: 22px; font-weight: 900; }
.hall-card strong { font-size: 14px; }
.hall-card p { margin: 0; font-size: 13px; color: var(--ink-soft); }
.hall-go { margin-top: auto; padding-top: 14px; font-size: 13px; font-weight: 900; }
.explore-band { display: flex; flex-wrap: wrap; align-items: center; gap: 22px 32px; padding: 28px; border: var(--line); background: var(--blue); box-shadow: var(--shadow); /* taste-skill-ignore: 沿用原型横幅硬阴影。 */ color: var(--paper-light); }
.explore-band > div:first-child { flex: 1 1 420px; }
.explore-band h2 { margin-bottom: 8px; font-family: var(--serif); font-size: 26px; font-weight: 900; }
.explore-band p { margin: 0; font-size: 15px; line-height: 1.8; }
.explore-actions { display: flex; flex-wrap: wrap; gap: 12px; }
.explore-actions .button { background: var(--yellow); color: var(--ink); }
.boundary { padding-bottom: 20px; }
.boundary details { max-width: 860px; font-size: 14px; }
.boundary summary { padding: 8px 0; font-weight: 900; cursor: pointer; }
.boundary p { margin: 0; padding: 4px 0 0; color: var(--ink-soft); line-height: 1.8; }
@media (max-width: 1000px) { .work-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } .hall-grid { grid-template-columns: 1fr; } }
@media (max-width: 640px) {
  .home-page > .shell { width: min(calc(100% - 32px), var(--page-width)); }
  .hero { padding-block: 36px 26px; }
  .hero-desc { font-size: 16px; }
  .highlight-strip { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .work-grid { grid-template-columns: 1fr; }
  .explore-band { padding: 22px 18px; }
}
</style>
