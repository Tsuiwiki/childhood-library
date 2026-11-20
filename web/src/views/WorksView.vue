<script setup lang="ts">
import { ref } from 'vue'
import ClAudioPlayer, { type AudioPlayerTrack } from '@/components/ClAudioPlayer.vue'
import sampleRecords from '../../../design-demos/audio/samples.json'

interface ResearchSample {
  id: string
  file: string
  workTitle: string
  kind: string
  sampleType?: 'internal' | 'generated' | 'open'
  attribution: string
  license: string
}

// Reuse the checked-in research source directly; do not maintain a second copy
// in web/ and do not present these records as the empty production database.
const samples = sampleRecords as ResearchSample[]
const selectedTrack = ref<AudioPlayerTrack | null>(null)

function sourceLabel(sample: ResearchSample): string {
  if (sample.sampleType === 'internal') return '内部经典录音 · 权利待核验'
  if (sample.sampleType === 'generated') return '原创播放示范 · 非原曲'
  return '开放许可 / 原创示范'
}

function actionLabel(sample: ResearchSample): string {
  if (sample.sampleType === 'internal') return '播放经典原声'
  if (sample.sampleType === 'generated') return '播放原创示范'
  return '试听歌曲示例'
}

function playSample(sample: ResearchSample): void {
  selectedTrack.value = {
    id: sample.id,
    title: sample.workTitle,
    source: `/audio/${sample.file}`,
    kicker: `${sourceLabel(sample)} · ${sample.license}`,
    fileLabel: `${sample.kind} · ${sample.attribution}`,
    kind: 'sample',
  }
}
</script>

<template>
  <section class="shell works-page">
    <header class="works-header">
      <h1>曲目列表</h1>
      <p>
        内部研究试听，共 {{ samples.length }} 条主录音记录。本页直接读取既有
        <code>design-demos/audio/samples.json</code>，不是已发布曲库，也不代表数据库已经导入。
      </p>
      <p class="rights-note">权利待核验的录音仅限内部研究试听；开放许可仅对应各条目注明的具体录音。</p>
    </header>

    <div class="works-grid" aria-label="内部研究录音列表">
      <article v-for="sample in samples" :key="sample.id" class="work-card">
        <div class="card-top">
          <span class="id-tag">{{ sample.id }}</span>
          <span class="status-badge">{{ sample.license }}</span>
        </div>
        <h2>{{ sample.workTitle }}</h2>
        <p class="card-group">{{ sample.kind }}</p>
        <dl class="card-meta">
          <div><dt>录音</dt><dd>{{ sample.attribution }}</dd></div>
          <div><dt>来源</dt><dd>{{ sourceLabel(sample) }}</dd></div>
        </dl>
        <div class="card-footer">
          <button
            class="detail-button audio-action"
            type="button"
            data-audio-play="true"
            :data-work-id="sample.id"
            :aria-label="`${actionLabel(sample)}：${sample.workTitle}`"
            @click="playSample(sample)"
          >
            {{ actionLabel(sample) }}
          </button>
        </div>
      </article>
    </div>
  </section>

  <ClAudioPlayer :track="selectedTrack" @close="selectedTrack = null" />
</template>

<style scoped>
/* Card and button geometry copied from design-demos/works.html L299-L400. */
.works-page { padding-block: 42px 64px; }
.works-header { max-width: 850px; margin-bottom: 30px; }
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

@media (max-width: 1100px) {
  .works-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (max-width: 640px) {
  .works-grid { grid-template-columns: 1fr; gap: 20px; }
  .work-card { padding-right: 16px; }
  .detail-button { width: 100%; }
}
</style>
