import type { AudioPlayerTrack } from '@/components/ClAudioPlayer.vue'
import sampleRecords from '../../../design-demos/audio/samples.json'

export interface ScoreReference {
  title: string
  url: string
  note?: string
}

export interface ResearchMaterials {
  cover: string
  coverAlt: string
  lyrics?: string[]
  lyricsTitle?: string
  lyricsNote?: string
  score?: string
  scoreSource?: string
  scoreTitle?: string
  scoreNote?: string
  scoreReferences?: ScoreReference[]
}

export interface ResearchVersion {
  file: string
  workTitle: string
  kind: string
  sampleType?: 'internal' | 'generated' | 'open'
  attribution: string
  license: string
  author?: string
  sourceTitle?: string
  sourcePage?: string
  sourceDate?: string
  downloadedFile?: string
  downloadedFormat?: string
  deliveryNote?: string
  licenseUrl?: string
  licenseNote?: string
  sourceUsageStatement?: string
  sourceUsageStatementCheckedOn?: string
  retrievedOn?: string
  bytes?: number
  sha256?: string
  changes?: string
  durationLabel?: string
  versionLabel?: string
  versionNote?: string
}

export interface ResearchSample extends ResearchVersion {
  id: string
  materials: ResearchMaterials
  variants?: ResearchVersion[]
}

// One checked-in research source; no copied JSON and no invented detail fields.
export const researchSamples = sampleRecords as ResearchSample[]

export function sampleCategory(sample: ResearchVersion): 'internal' | 'generated' | 'open' {
  return sample.sampleType ?? 'open'
}

export function sourceLabel(sample: ResearchVersion): string {
  const category = sampleCategory(sample)
  if (category === 'internal') return '内部经典录音 · 权利待核验'
  if (category === 'generated') return '原创播放示范 · 非原曲'
  return '开放许可 / 原创示范'
}

export function actionLabel(sample: ResearchVersion): string {
  const category = sampleCategory(sample)
  if (category === 'internal') return '播放经典原声'
  if (category === 'generated') return '播放原创示范'
  return '试听歌曲示例'
}

export function rightsNote(sample: ResearchVersion): string {
  const category = sampleCategory(sample)
  if (category === 'internal') {
    return '本条目提供经典人声录音供内部研究与原型试听；歌词、谱面按资料卡实际状态展示。词曲、表演及具体录音 / 片段权利待核验，不属于开放许可素材，不得据此公开发布。'
  }
  if (category === 'generated') {
    return '此音频是项目程序合成的原创播放示范，不是本曲旋律或歌曲录音；CC0 许可仅覆盖该新音频，不改变词曲、歌词和其他录音的权利状态。'
  }
  return '本示例仅覆盖上述具体音频和原创素材，不改变作品目录状态；传统歌词按所标地域版本与来源整理，公开发布前仍须复核。'
}

export function toPlayerTrack(version: ResearchVersion, work: ResearchSample): AudioPlayerTrack {
  return {
    id: work.id,
    title: work.workTitle,
    source: `/audio/${version.file}`,
    kicker: `${sourceLabel(version)} · ${version.license}`,
    fileLabel: `${version.kind} · ${version.attribution}`,
    kind: 'sample',
  }
}

export function assetUrl(path: string): string {
  return `/${path.replace(/^\/+/, '')}`
}

export function externalUrl(value?: string): string | null {
  if (!value) return null
  try {
    const parsed = new URL(value)
    return parsed.protocol === 'http:' || parsed.protocol === 'https:' ? parsed.href : null
  } catch {
    return null
  }
}

export function formatBytes(value?: number): string {
  if (value === undefined) return '文件大小待核验'
  if (value < 1024) return `${value} B`
  if (value < 1024 * 1024) return `${(value / 1024).toFixed(1)} KB`
  return `${(value / (1024 * 1024)).toFixed(2)} MB`
}
