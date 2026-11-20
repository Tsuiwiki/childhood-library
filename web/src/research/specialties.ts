import payload from '../../../design-demos/specialties.json'
import { researchSamples } from '@/research/samples'

export type SpecialtyId =
  | 'childhood'
  | 'nature'
  | 'play'
  | 'lullaby'
  | 'classical'
  | 'world'
  | 'forgotten'
  | 'original'

export interface SpecialtyDefinition {
  id: SpecialtyId
  no: string
  name: string
  shortDescription: string
  description: string
  scope: string
  focus: string
  tone: 'red' | 'green' | 'yellow' | 'blue' | 'brown'
}

export interface SpecialtyWork {
  id: string
  title: string
  type: string
  note: string
  region: string
  specialties: SpecialtyId[]
}

export const specialtyDefinitions: SpecialtyDefinition[] = [
  { id: 'childhood', no: '01', name: '童年的歌', shortDescription: '中国经典儿童歌曲、校园歌曲与童年记忆。', description: '中国经典儿童歌曲、校园歌曲与童年记忆，是几代人共同的听觉底色。这里收录旋律舒展、歌词有画面的创作儿歌与校园歌。', scope: '中国经典儿童歌曲、校园歌曲、童年记忆', focus: '区分儿童歌曲、校园歌曲与成人怀旧作品', tone: 'red' },
  { id: 'nature', no: '02', name: '大自然的歌', shortDescription: '春夏秋冬、花草树木、鸟兽、河流海洋。', description: '春夏秋冬、花草树木、鸟兽虫鱼与河流海洋。自然观察与画面感，是这类作品最珍贵的部分。', scope: '春夏秋冬、花草树木、鸟兽、河流海洋', focus: '自然观察、画面感与旋律舒展度', tone: 'green' },
  { id: 'play', no: '03', name: '游戏与伙伴', shortDescription: '游戏歌、拍手歌、数数歌、问答歌。', description: '游戏歌、拍手歌、数数歌、问答歌。在语言与身体的互动里，藏着最自然的童趣。', scope: '游戏歌、拍手歌、数数歌、问答歌', focus: '互动性、语言趣味与传统玩法', tone: 'yellow' },
  { id: 'lullaby', no: '04', name: '月亮与摇篮曲', shortDescription: '中国及世界各地的摇篮曲与安睡音乐。', description: '中国及世界各地的摇篮曲与安睡音乐。温柔、克制，适合陪伴，不承诺任何助眠效果。', scope: '中国及世界各地摇篮曲、安睡音乐', focus: '温柔、克制、适合陪伴，不承诺助眠效果', tone: 'blue' },
  { id: 'classical', no: '05', name: '古典音乐的童年', shortDescription: '儿童古典作品、适龄器乐小品、音乐故事。', description: '儿童古典作品、适龄器乐小品与音乐故事。引导聆听，而非把作品简化成训练工具。', scope: '儿童古典作品、适龄器乐小品、音乐故事', focus: '引导聆听，不把作品简化成训练工具', tone: 'brown' },
  { id: 'world', no: '06', name: '世界的童谣', shortDescription: '多语言童谣、地方儿童歌曲、民族音乐。', description: '多语言童谣、地方儿童歌曲与民族音乐。保留原语言与文化背景，听见不同地域的童年。', scope: '多语言童谣、地方儿童歌曲、民族音乐', focus: '保留原语言、文化背景和地域版本', tone: 'blue' },
  { id: 'forgotten', no: '07', name: '被遗忘的童谣', shortDescription: '地方方言、口传童谣、历史采录。', description: '地方方言、口传童谣与历史采录。记录传承人、采录地点、异文与语境，留住正在远去的声音。', scope: '地方方言、口传童谣、历史采录', focus: '记录传承人、采录地点、异文和语境', tone: 'brown' },
  { id: 'original', no: '08', name: '新芽原创', shortDescription: '当代原创儿童音乐，尊重儿童视角与明确授权。', description: '当代原创儿童音乐。尊重儿童视角、创作质量与明确授权，给真正的新作品留出空间。', scope: '当代原创儿童音乐', focus: '尊重儿童视角、创作质量与明确授权', tone: 'green' },
]

export const specialtyCatalog = payload.works as SpecialtyWork[]
const audioWorkIds = new Set(researchSamples.map((sample) => sample.id))

export function isSpecialtyId(value: string): value is SpecialtyId {
  return specialtyDefinitions.some((specialty) => specialty.id === value)
}

export function getSpecialty(id: string): SpecialtyDefinition | undefined {
  return specialtyDefinitions.find((specialty) => specialty.id === id)
}

export function specialtyWorks(id: SpecialtyId): SpecialtyWork[] {
  return specialtyCatalog
    .filter((work) => work.specialties.includes(id))
    .sort((a, b) => a.id.localeCompare(b.id))
}

export function specialtyCount(id: SpecialtyId): number {
  return specialtyWorks(id).length
}

export function hasResearchAudio(workId: string): boolean {
  return audioWorkIds.has(workId)
}

export function workSpecialties(workId: string): SpecialtyDefinition[] {
  const work = specialtyCatalog.find((item) => item.id === workId)
  if (!work) return []
  return work.specialties
    .map((id) => getSpecialty(id))
    .filter((item): item is SpecialtyDefinition => Boolean(item))
}
