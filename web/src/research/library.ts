import payload from '../../../design-demos/library-content.json'

export type ResearchHall = 'story' | 'poetry'

export interface ResearchGroup {
  id: string
  hall: ResearchHall
  no: string
  name: string
  target: number
  desc: string
  focus: string
  accent: string
  source: string[]
  isTopic?: boolean
  isAsset?: boolean
}

export interface ResearchRecord {
  id: string
  hall: ResearchHall
  group: string
  groupName: string
  title: string
  origin: string
  contributor: string
  ageBand: string
  note: string
  sourceName: string
  sourceUrl: string
  researchStatus: string
  rightsStatus: string
  qualityStatus: string
  accessMethod: string
  publicationStatus: string
  isTopic: boolean
  isAsset: boolean
  assetNote: string
}

export interface StatusModelRow {
  field: string
  values: string
  question: string
  note: string
}

interface LibraryContent {
  generatedOn: string
  statusModel: StatusModelRow[]
  statusLabels: Record<string, string>
  groups: ResearchGroup[]
  records: ResearchRecord[]
}

// The Vue halls read the existing checked-in research snapshot directly.
// No second copy of the 160 records is maintained in the frontend.
const content = payload as LibraryContent

export const statusModel = content.statusModel
export const statusLabels = content.statusLabels
export const generatedOn = content.generatedOn

export const hallContent: Record<ResearchHall, {
  title: string
  englishTitle: string
  description: string
  recordsLabel: string
  specialLabel: string
}> = {
  story: {
    title: '儿童故事馆 · 让好故事陪伴童年',
    englishTitle: 'STORY HALL',
    description: '以中国经典为根，以世界文学为窗，以优秀原创为未来的儿童文学图书馆。目前按《儿童故事馆建设方案》§2 / §9 建立研究目录。',
    recordsLabel: '作品 / 题材线索',
    specialLabel: '征集方向',
  },
  poetry: {
    title: '古诗词馆 · 把诗，读成声音与画面',
    englishTitle: 'POETRY HALL',
    description: '从启蒙篇目、自然四季到译注与朗诵，建立适合儿童的古诗词研究目录。作品、版本与媒体资产分别建档，不把资产线索当成新的文学作品。',
    recordsLabel: '作品线索',
    specialLabel: '版本 / 资产线索',
  },
}

export function hallGroups(hall: ResearchHall): ResearchGroup[] {
  return content.groups.filter((group) => group.hall === hall)
}

export function hallRecords(hall: ResearchHall): ResearchRecord[] {
  return content.records.filter((record) => record.hall === hall)
}

export function hallStats(hall: ResearchHall) {
  const records = hallRecords(hall)
  const special = records.filter((record) => record.isTopic || record.isAsset).length
  return {
    total: records.length,
    groups: hallGroups(hall).length,
    works: records.length - special,
    special,
  }
}

export function recordSearchText(record: ResearchRecord): string {
  return [
    record.id,
    record.title,
    record.contributor,
    record.origin,
    record.note,
    record.groupName,
  ].join(' ').normalize('NFKC').toLocaleLowerCase('zh-CN')
}

export function cleanResearchText(value: string): string {
  return value.replaceAll('**', '')
}
