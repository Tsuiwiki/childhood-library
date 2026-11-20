<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import {
  actionLabel,
  assetUrl,
  externalUrl,
  formatBytes,
  rightsNote,
  sourceLabel,
  type ResearchSample,
  type ResearchVersion,
} from '@/research/samples'

const props = defineProps<{ sample: ResearchSample | null }>()
const emit = defineEmits<{
  (e: 'close'): void
  (e: 'play', version: ResearchVersion): void
  (e: 'version-change', version: ResearchVersion): void
}>()

const dialog = ref<HTMLDialogElement | null>(null)
const selectedIndex = ref(0)
const versions = computed<ResearchVersion[]>(() => props.sample ? [props.sample, ...(props.sample.variants ?? [])] : [])
const selectedVersion = computed(() => versions.value[selectedIndex.value] ?? null)
const rightsText = computed(() => selectedVersion.value ? rightsNote(selectedVersion.value) : '')
const sourcePage = computed(() => externalUrl(selectedVersion.value?.sourcePage))
const licensePage = computed(() => externalUrl(selectedVersion.value?.licenseUrl))
const downloadedFile = computed(() => externalUrl(selectedVersion.value?.downloadedFile))

function sync(open: boolean): void {
  if (!open) document.body.classList.remove('dialog-open')
  const el = dialog.value
  if (!el) return
  if (open) {
    if (el.open) return
    // jsdom does not implement showModal(); keep the component testable.
    if (typeof el.showModal === 'function') el.showModal()
    else el.setAttribute('open', '')
    document.body.classList.add('dialog-open')
  } else {
    if (typeof el.close === 'function' && el.open) el.close()
    else el.removeAttribute('open')
    document.body.classList.remove('dialog-open')
  }
}

function onCancel(event: Event): void {
  event.preventDefault()
  emit('close')
}

function onClose(): void {
  document.body.classList.remove('dialog-open')
  if (props.sample) emit('close')
}

function onVersionChange(): void {
  if (selectedVersion.value) emit('version-change', selectedVersion.value)
}

function onDialogClick(event: MouseEvent): void {
  const el = dialog.value
  if (!el || event.target !== el) return
  const rect = el.getBoundingClientRect()
  const inside = event.clientX >= rect.left && event.clientX <= rect.right
    && event.clientY >= rect.top && event.clientY <= rect.bottom
  if (!inside) emit('close')
}

watch(() => props.sample, (sample) => {
  selectedIndex.value = 0
  sync(Boolean(sample))
}, { flush: 'post' })

onMounted(() => sync(Boolean(props.sample)))
onBeforeUnmount(() => document.body.classList.remove('dialog-open'))
</script>

<template>
  <dialog
    v-if="sample && selectedVersion"
    ref="dialog"
    class="track-dialog"
    aria-labelledby="dialog-title"
    aria-describedby="dialog-rights"
    @cancel="onCancel"
    @close="onClose"
    @click="onDialogClick"
  >
    <div class="dialog-header">
      <p class="dialog-kicker">录音资料卡 · 完整字段</p><!-- taste-skill-ignore: 保留原型资料卡标识。 -->
      <button class="dialog-close" type="button" aria-label="关闭作品详情" autofocus @click="emit('close')">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true"><path d="m5 5 14 14M19 5 5 19" /></svg>
      </button>
    </div>

    <div class="dialog-body">
      <h2 id="dialog-title">{{ sample.workTitle }}</h2>
      <dl class="dialog-meta">
        <div><dt>目录编号</dt><dd>{{ sample.id }}</dd></div>
        <div><dt>录音类型</dt><dd>{{ selectedVersion.kind }}</dd></div>
        <div><dt>时长</dt><dd>{{ selectedVersion.durationLabel || '待核验' }}</dd></div>
        <div><dt>演唱 / 作者</dt><dd>{{ selectedVersion.author || selectedVersion.attribution }}</dd></div>
        <div><dt>版本</dt><dd>{{ selectedVersion.versionLabel || '主录音版本' }}</dd></div>
        <div><dt>来源名称</dt><dd>{{ selectedVersion.sourceTitle || '来源名称待补充' }}</dd></div>
        <div><dt>许可状态</dt><dd>{{ selectedVersion.license }}</dd></div>
        <div><dt>采集日期</dt><dd>{{ selectedVersion.retrievedOn || '待核验' }}</dd></div>
        <div><dt>音频文件</dt><dd>{{ selectedVersion.file }} · {{ formatBytes(selectedVersion.bytes) }}</dd></div>
        <div><dt>SHA-256</dt><dd class="hash-value">{{ selectedVersion.sha256 || '待核验' }}</dd></div>
      </dl>

      <section class="sample-audio-panel" :class="`is-${selectedVersion.sampleType || 'open'}`" aria-labelledby="sample-audio-title">
        <h3 id="sample-audio-title">{{ sourceLabel(selectedVersion) }}</h3>
        <div v-if="versions.length > 1" class="sample-version-field">
          <label for="sample-version">录音版本（共 {{ versions.length }} 个）</label>
          <select id="sample-version" v-model.number="selectedIndex" @change="onVersionChange">
            <option v-for="(version, index) in versions" :key="version.file" :value="index">
              {{ version.versionLabel || version.kind }}
            </option>
          </select>
        </div>
        <p>{{ selectedVersion.deliveryNote || '录音说明待补充。' }}</p>
        <p v-if="selectedVersion.versionNote" class="version-note">{{ selectedVersion.versionNote }}</p>
        <p class="sample-audio-meta">署名：{{ selectedVersion.attribution }} · {{ selectedVersion.license }}</p>
        <p v-if="selectedVersion.changes" class="sample-audio-meta">本地处理：{{ selectedVersion.changes }}</p>
        <button class="button button-primary" type="button" @click="emit('play', selectedVersion)">
          {{ actionLabel(selectedVersion) }}
        </button>
        <div class="sample-links">
          <a v-if="sourcePage" :href="sourcePage" target="_blank" rel="noopener noreferrer">录音 / 资料来源 ↗</a>
          <a v-if="licensePage" :href="licensePage" target="_blank" rel="noopener noreferrer">许可全文 ↗</a>
          <a v-if="downloadedFile" :href="downloadedFile" target="_blank" rel="noopener noreferrer">原始音频附件 ↗</a>
        </div>
      </section>

      <section class="song-materials" aria-labelledby="song-materials-title">
        <h3 id="song-materials-title">{{ sample.materials.score ? '封面、歌词与五线谱' : '封面、歌词与资料卡' }}</h3>
        <div class="song-material-grid">
          <figure class="song-cover">
            <img :src="assetUrl(sample.materials.cover)" :alt="sample.materials.coverAlt" width="800" height="600">
            <figcaption>童年书房原创剪贴簿封面 · <a class="material-link" :href="assetUrl(sample.materials.cover)" download>下载封面 SVG</a></figcaption>
          </figure>
          <section class="lyrics-sheet" aria-labelledby="lyrics-title">
            <h4 id="lyrics-title">{{ sample.materials.lyricsTitle || '歌词核验状态' }}</h4>
            <div v-if="sample.materials.lyrics?.length" class="lyrics-lines">
              <p v-for="line in sample.materials.lyrics" :key="line">{{ line }}</p>
            </div>
            <p v-else class="lyrics-lines">歌词尚未逐条核验，本页不以虚构内容补齐。</p>
            <p v-if="sample.materials.lyricsNote" class="lyrics-note">{{ sample.materials.lyricsNote }}</p>
          </section>
        </div>

        <section v-if="sample.materials.score" class="score-sheet" aria-labelledby="score-title">
          <div class="score-heading">
            <h4 id="score-title">{{ sample.materials.scoreTitle }}</h4>
            <div class="score-downloads" aria-label="五线谱下载">
              <a class="material-link" :href="assetUrl(sample.materials.score)" download>五线谱 SVG</a>
              <a v-if="sample.materials.scoreSource" class="material-link" :href="assetUrl(sample.materials.scoreSource)" download>MusicXML 源文件</a>
            </div>
          </div>
          <p class="score-note">{{ sample.materials.scoreNote }} 窄屏可横向滚动。</p>
          <div class="score-scroll" tabindex="0" role="region" :aria-label="`《${sample.workTitle}》五线谱，窄屏可横向滚动`">
            <img :src="assetUrl(sample.materials.score)" :alt="`《${sample.workTitle}》${sample.materials.scoreTitle}五线谱`" width="1200" height="500">
          </div>
          <ul v-if="sample.materials.scoreReferences?.length" class="score-references">
            <li v-for="reference in sample.materials.scoreReferences" :key="reference.url">
              <a v-if="externalUrl(reference.url)" :href="reference.url" target="_blank" rel="noopener noreferrer">{{ reference.title }} ↗</a>
              <span v-if="reference.note">：{{ reference.note }}</span>
            </li>
          </ul>
        </section>
      </section>

      <section class="material-sources" aria-labelledby="material-sources-title">
        <h4 id="material-sources-title">来源、权利与采集状态</h4>
        <dl>
          <dt>权利说明</dt><dd>{{ selectedVersion.licenseNote || selectedVersion.license }}</dd>
          <template v-if="selectedVersion.sourceUsageStatement">
            <dt>来源平台说明</dt><dd>{{ selectedVersion.sourceUsageStatement }}</dd>
            <dt>说明核对日期</dt><dd>{{ selectedVersion.sourceUsageStatementCheckedOn || '待核验' }}</dd>
          </template>
          <dt>原始格式</dt><dd>{{ selectedVersion.downloadedFormat || '按现有音频文件记录' }}</dd>
          <dt>研究边界</dt><dd>研究收录不等于公开播放、下载或分发授权；公开发布前仍须逐条复核。</dd>
        </dl>
      </section>

      <p id="dialog-rights" class="dialog-rights">{{ rightsText }}</p>
    </div>
  </dialog>
</template>

<style scoped>
/* Structure and styling follow design-demos/works.html L947-L1050 and L433-L548. */
:global(body.dialog-open) { overflow: hidden; }
.track-dialog { width: min(980px, calc(100% - 32px)); max-height: calc(100dvh - 40px); padding: 0; overflow: auto; border: var(--line); border-radius: 0; color: var(--ink); background-color: var(--paper); background-image: radial-gradient(circle, rgba(25, 25, 23, .17) .8px, transparent .9px); background-size: 9px 9px; box-shadow: 9px 9px 0 var(--ink); /* taste-skill-ignore: 原型模态框硬阴影。 */ }
.track-dialog::backdrop { background: rgba(25, 25, 23, .72); }
.dialog-header { display: flex; align-items: center; justify-content: space-between; gap: 18px; padding: 16px 20px; border-bottom: var(--line); background: var(--yellow); }
.dialog-kicker { margin: 0; font-size: 14px; font-weight: 900; }
.dialog-close { min-width: 48px; min-height: 48px; display: inline-flex; align-items: center; justify-content: center; flex: 0 0 auto; padding: 9px; border: 2px solid var(--ink); background: var(--paper-light); box-shadow: 3px 3px 0 var(--ink); /* taste-skill-ignore: 原型关闭按钮硬阴影。 */ }
.dialog-close svg { width: 22px; height: 22px; }
.dialog-body { padding: 26px; }
.dialog-body h2 { margin: 0 0 20px; font-family: var(--serif); font-size: clamp(28px, 5vw, 40px); line-height: 1.3; overflow-wrap: anywhere; }
.dialog-meta { display: grid; gap: 0; margin: 0 0 22px; border: 2px solid var(--ink); background: var(--paper-light); }
.dialog-meta div { display: grid; grid-template-columns: 118px minmax(0, 1fr); gap: 14px; padding: 10px 14px; }
.dialog-meta div + div { border-top: 2px dashed var(--ink); }
.dialog-meta dt { font-size: 14px; font-weight: 900; }
.dialog-meta dd { margin: 0; font-size: 16px; overflow-wrap: anywhere; }
.hash-value { font-family: ui-monospace, monospace; font-size: 13px !important; overflow-wrap: anywhere; } /* taste-skill-ignore: SHA-256 是逐字核对的校验值。 */
.sample-audio-panel { margin-bottom: 22px; padding: 18px; border: var(--line); background: #e2edcf; box-shadow: 5px 5px 0 var(--green); /* taste-skill-ignore: 原型录音面板硬阴影。 */ }
.sample-audio-panel.is-internal { background: #f9ddd7; box-shadow: 5px 5px 0 var(--red); /* taste-skill-ignore: 原型权利待核验面板。 */ }
.sample-audio-panel.is-generated { background: #dfe8fb; box-shadow: 5px 5px 0 var(--blue); /* taste-skill-ignore: 原型原创示范面板。 */ }
.sample-audio-panel h3 { margin: 0 0 12px; font-family: var(--serif); font-size: 25px; line-height: 1.35; }
.sample-audio-panel p { line-height: 1.65; }
.sample-version-field { margin: 16px 0; }
.sample-version-field label { display: block; margin-bottom: 6px; font-weight: 900; }
.sample-version-field select { width: 100%; min-height: 48px; padding: 10px 12px; border: 2px solid var(--ink); border-radius: 0; background: var(--paper-light); color: var(--ink); font: inherit; font-weight: 800; }
.sample-audio-meta { font-weight: 800; overflow-wrap: anywhere; }
.version-note { font-weight: 700; }
.sample-links { display: flex; flex-wrap: wrap; gap: 8px 20px; margin-top: 12px; }
.sample-links a, .material-link { display: inline-flex; align-items: center; min-height: 44px; font-weight: 900; text-decoration-thickness: 2px; text-underline-offset: 4px; }
.song-materials { min-width: 0; margin: 0 0 22px; padding-top: 24px; border-top: var(--line); }
.song-materials > h3 { margin: 0 0 18px; font-family: var(--serif); font-size: 29px; line-height: 1.3; }
.song-material-grid { display: grid; grid-template-columns: minmax(220px, .85fr) minmax(0, 1.15fr); align-items: stretch; gap: 20px; }
.song-cover { min-width: 0; margin: 0; }
.song-cover img { display: block; width: 100%; height: auto; aspect-ratio: 4 / 3; object-fit: cover; border: var(--line); background: var(--paper-light); box-shadow: 5px 5px 0 var(--red); /* taste-skill-ignore: 原型封面硬阴影。 */ }
.song-cover figcaption { margin-top: 12px; font-size: 14px; font-weight: 800; }
.lyrics-sheet { min-width: 0; padding: 18px; border: var(--line); background: var(--paper-light); box-shadow: 5px 5px 0 var(--blue); /* taste-skill-ignore: 原型歌词卡硬阴影。 */ }
.lyrics-sheet h4, .score-sheet h4 { margin: 0 0 10px; font-family: var(--serif); font-size: 22px; line-height: 1.35; }
.lyrics-lines { display: grid; gap: 7px; margin: 16px 0; }
.lyrics-lines p { margin: 0; font-family: var(--serif); font-size: 18px; font-weight: 700; line-height: 1.55; overflow-wrap: anywhere; }
.lyrics-note, .score-note { margin: 0; font-size: 14px; font-weight: 700; line-height: 1.65; }
.score-sheet { min-width: 0; margin-top: 22px; }
.score-heading { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 8px 18px; margin-bottom: 8px; }
.score-downloads { display: flex; flex-wrap: wrap; gap: 4px 16px; }
.score-note { margin-bottom: 12px; }
.score-scroll { max-width: 100%; overflow: auto; border: var(--line); background: var(--paper-light); overscroll-behavior: contain; }
.score-scroll img { display: block; width: 100%; min-width: 960px; height: auto; }
.score-references { padding-left: 22px; font-size: 14px; line-height: 1.7; }
.score-references a { font-weight: 900; }
.material-sources { min-width: 0; margin: 22px 0; padding: 18px 20px; border: var(--line); background: var(--paper-light); box-shadow: 5px 5px 0 var(--green); /* taste-skill-ignore: 原型来源卡硬阴影。 */ }
.material-sources h4 { margin: 0 0 12px; font-family: var(--serif); font-size: 22px; }
.material-sources dl { display: grid; grid-template-columns: 110px minmax(0, 1fr); gap: 10px 16px; margin: 0; }
.material-sources dt { font-size: 14px; font-weight: 900; }
.material-sources dd { min-width: 0; margin: 0; font-size: 14px; font-weight: 700; line-height: 1.7; overflow-wrap: anywhere; }
.dialog-rights { margin: 0; padding: 15px; border: 2px dashed var(--ink); font-size: 16px; font-weight: 800; }

@media (max-width: 640px) {
  .dialog-header { padding: 13px 14px; }
  .dialog-body { padding: 22px 18px; }
  .dialog-meta div { grid-template-columns: 100px minmax(0, 1fr); gap: 10px; padding-inline: 12px; }
  .song-material-grid { grid-template-columns: 1fr; }
  .song-cover { max-width: 420px; }
  .material-sources dl { grid-template-columns: 1fr; gap: 4px; }
  .material-sources dd { margin-bottom: 10px; }
}
@media (max-width: 400px) {
  .dialog-meta div { grid-template-columns: 1fr; gap: 3px; }
  .lyrics-sheet, .sample-audio-panel { padding: 14px; }
}
</style>
