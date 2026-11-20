<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'

export type AudioPlayerKind = 'local' | 'sample'

export interface AudioPlayerTrack {
  id: string
  title: string
  source: string | Blob
  kicker: string
  fileLabel: string
  kind: AudioPlayerKind
}

const props = defineProps<{ track: AudioPlayerTrack | null }>()
const emit = defineEmits<{ (e: 'close'): void }>()

const audioElement = ref<HTMLAudioElement | null>(null)
const current = ref<AudioPlayerTrack | null>(null)
const playerError = ref('')

let mounted = false
let objectUrl: string | null = null
let requestSerial = 0
let returnFocus: HTMLElement | null = null

function clearAudioSource() {
  const audio = audioElement.value
  if (!audio) return

  requestSerial += 1
  audio.pause()
  if (objectUrl) URL.revokeObjectURL(objectUrl)
  objectUrl = null
  audio.removeAttribute('src')
  audio.load()
}

function restoreTriggerFocus(previousId: string | undefined, focusTarget: HTMLElement | null) {
  if (focusTarget?.isConnected && focusTarget.getClientRects().length) {
    focusTarget.focus()
    return
  }
  if (!previousId) return

  const cardButton = Array.from(document.querySelectorAll<HTMLElement>('[data-audio-play]'))
    .find((button) => button.dataset.workId === previousId)
  cardButton?.focus()
}

function closeAudioPlayer(restoreFocus = true) {
  const previousId = current.value?.id
  const focusTarget = returnFocus
  clearAudioSource()
  current.value = null
  playerError.value = ''
  document.body.classList.remove('audio-player-open')
  returnFocus = null
  if (restoreFocus) restoreTriggerFocus(previousId, focusTarget)
}

function isSameSource(track: AudioPlayerTrack) {
  return current.value?.id === track.id
    && current.value.kind === track.kind
    && current.value.source === track.source
    && Boolean(audioElement.value?.getAttribute('src'))
}

async function playAudio(track: AudioPlayerTrack | null) {
  const audio = audioElement.value
  if (!audio) return
  if (!track) {
    closeAudioPlayer(false)
    return
  }

  if (!current.value && document.activeElement instanceof HTMLElement) {
    returnFocus = document.activeElement
  }

  if (!isSameSource(track)) {
    clearAudioSource()
    current.value = track
    if (track.source instanceof Blob) {
      objectUrl = URL.createObjectURL(track.source)
      audio.src = objectUrl
    } else {
      audio.src = track.source
    }
  } else {
    current.value = track
  }

  document.body.classList.add('audio-player-open')
  playerError.value = ''
  const serial = ++requestSerial
  try {
    await audio.play()
  } catch {
    if (serial !== requestSerial || current.value?.id !== track.id) return
    playerError.value = track.kind === 'local'
      ? '无法播放此本地文件。请确认浏览器支持其编码，或替换为其他音频文件。'
      : '无法播放歌曲录音。请保持 audio 文件夹与 works.html 的相对位置，并确认浏览器支持 MP3、WAV、M4A、MP4 音轨或 FLAC。'
  }
}

function onClose() {
  closeAudioPlayer()
  emit('close')
}

function onAudioError() {
  const audio = audioElement.value
  if (!audio?.getAttribute('src') || !current.value) return
  playerError.value = current.value.kind === 'sample'
    ? '浏览器无法读取开放示例，请确认 audio 文件夹完整且与 works.html 放在一起。'
    : '浏览器无法解码此本地文件，请替换为支持的音频格式或编码。'
}

watch(() => props.track, (track) => {
  if (mounted) void playAudio(track)
})

onMounted(() => {
  mounted = true
  if (props.track) void playAudio(props.track)
})

onBeforeUnmount(() => {
  mounted = false
  closeAudioPlayer(false)
})
</script>

<template>
  <aside class="audio-player" aria-label="内部本地试听播放器" :hidden="!current">
    <div class="player-inner">
      <div class="player-copy">
        <span class="player-kicker">{{ current?.kicker || '内部本地试听 · 不上传、不发布' }}</span><!-- taste-skill-ignore: 保留原型的权利与来源说明，不是新增标题装饰。 -->
        <strong class="player-title">{{ current?.title }}</strong>
        <span class="player-file">{{ current?.fileLabel }}</span>
      </div>
      <audio
        ref="audioElement"
        class="player-audio"
        controls
        preload="metadata"
        aria-label="当前作品的本地音频"
        @error="onAudioError"
      ></audio>
      <button
        class="dialog-close player-close"
        type="button"
        aria-label="关闭内部本地试听播放器"
        @click="onClose"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true"><path d="m5 5 14 14M19 5 5 19" /></svg>
      </button>
      <p class="player-error" role="status" aria-live="polite" :hidden="!playerError">{{ playerError }}</p>
    </div>
  </aside>
</template>

<style scoped>
/* Visual and interaction baseline: design-demos/works.html L522-L548, L683-L689. */
:global(body.audio-player-open) { padding-bottom: 152px; }
.audio-player {
  position: fixed;
  z-index: 40;
  right: 0;
  bottom: 0;
  left: 0;
  border-top: var(--line);
  background: var(--yellow);
  box-shadow: 0 -5px 0 rgba(25, 25, 23, .18); /* taste-skill-ignore: 固定底栏沿用原型顶部硬阴影。 */
}
.player-inner {
  width: min(calc(100% - 48px), 1240px);
  min-width: 0;
  display: grid;
  grid-template-columns: minmax(180px, 1fr) minmax(300px, 2fr) 48px;
  align-items: center;
  gap: 16px;
  margin-inline: auto;
  padding-block: 12px;
}
.player-copy { min-width: 0; }
.player-kicker { display: block; margin-bottom: 2px; font-size: 12px; font-weight: 900; }
.player-title { display: block; font-family: var(--serif); font-size: 20px; font-weight: 900; line-height: 1.35; overflow-wrap: anywhere; }
.player-file { display: block; font-size: 12px; font-weight: 700; overflow-wrap: anywhere; }
.player-audio { display: block; width: 100%; min-width: 0; min-height: 48px; }
.dialog-close {
  min-width: 48px;
  min-height: 48px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 auto;
  padding: 9px;
  border: 2px solid var(--ink);
  background: var(--paper-light);
  box-shadow: 3px 3px 0 var(--ink); /* taste-skill-ignore: 关闭按钮沿用原型硬阴影。 */
}
.dialog-close svg { width: 22px; height: 22px; }
.player-close { align-self: center; }
.player-error { grid-column: 1 / -1; margin: -4px 0 0; color: #791b14; font-size: 16px; font-weight: 900; }

@media (max-width: 640px) {
  :global(body.audio-player-open) { padding-bottom: 292px; }
  .player-inner { width: calc(100% - 32px); grid-template-columns: minmax(0, 1fr) 48px; gap: 10px 12px; padding-block: 10px; }
  .player-copy { padding-right: 2px; }
  .player-title { font-size: 18px; }
  .player-audio { grid-column: 1 / -1; grid-row: 2; }
  .player-close { grid-column: 2; grid-row: 1; }
  .player-error { grid-row: 3; }
}
</style>
