import { specialtyCatalog } from '@/research/specialties'

export interface ResearchDocument {
  id: string
  title: string
  path: string
  description: string
  updated: string
  workTitles: string[]
}

// These are navigation records for documents already tracked on GitHub.
// They do not import or republish document bodies or third-party media.
export const researchDocuments: ResearchDocument[] = [
  {
    id: 'songs-500',
    title: '中国儿童歌曲 500 首研究总目录',
    path: 'docs/CHINESE_CHILDRENS_SONGS_500_CATALOG.md',
    description: '音乐研究的总目录与各批次入口，候选登记不等于授权发布。',
    updated: '2026-11-21',
    workTitles: [],
  },
  {
    id: 'songs-history-02',
    title: '逐曲研究批次：历史作品与版本线索',
    path: 'docs/CHINESE_CHILDRENS_SONGS_RESEARCH_BATCH_2026-11-20.md',
    description: '记录创作、传播、早期录音与谱本线索，明确尚待核验的史料。',
    updated: '2026-11-20',
    workTitles: ['快乐的节日', '小燕子', '听妈妈讲那过去的事情', '每当我走过老师窗前', '小螺号'],
  },
  {
    id: 'songs-research-02',
    title: '逐曲研究档案 · 批次 02',
    path: 'docs/research/CHINESE_CHILDRENS_SONGS_BATCH_02.md',
    description: '以同期报刊、机构专题和书目交叉核验作品身份及传播历史。',
    updated: '2026-11-20',
    workTitles: ['快乐的节日', '听妈妈讲那过去的事情', '每当我走过老师窗前', '小燕子', '我们的田野'],
  },
  {
    id: 'songs-research-03',
    title: '逐曲研究档案 · 批次 03',
    path: 'docs/research/CHINESE_CHILDRENS_SONGS_BATCH_03.md',
    description: '分别记录创作、首播、唱片发行与后期传播，保留年代异说。',
    updated: '2026-11-20',
    workTitles: ['一分钱', '丢手绢', '上学歌', '小螺号'],
  },
  {
    id: 'songs-audio-verified-04',
    title: '音频入口与版本核验 · 批次 04',
    path: 'docs/research/CHINESE_CHILDRENS_SONGS_AUDIO_BATCH_04.md',
    description: '整理正规平台后期版本、音像出版物与谱本书目；不把试听当授权。',
    updated: '2026-11-21',
    workTitles: ['一分钱', '丢手绢', '听妈妈讲那过去的事情', '快乐的节日'],
  },
  {
    id: 'songs-audio-leads-04',
    title: '音频优先采集档案 · 批次 04',
    path: 'docs/research/CHINESE_CHILDRENS_SONGS_BATCH_04_AUDIO.md',
    description: '保存候选音频及谱面发现线索，标明聚合来源和待核风险。',
    updated: '2026-11-21',
    workTitles: ['一分钱', '快乐的节日', '听妈妈讲那过去的事情', '我们的田野', '丢手绢'],
  },
  {
    id: 'story-plan',
    title: '儿童故事馆建设方案',
    path: 'docs/STORY_LIBRARY_PLAN_V1.md',
    description: '故事馆目录结构、来源研究、权利审核与阅读层的建设原则。',
    updated: '持续维护',
    workTitles: [],
  },
]

export const governanceDocuments = [
  { title: '项目顶层原则', path: 'docs/PROJECT_PRINCIPLES.md', description: '研究资源库与儿童使用层如何分开。' },
  { title: '统一数据模型', path: 'docs/DATA_MODEL.md', description: '作品、版本、来源、媒体和权利如何关联。' },
  { title: '版权与内容审核政策', path: 'docs/COPYRIGHT_POLICY.md', description: '发现、内部研究与公开发布各自需要什么证据。' },
]

export function documentUrl(path: string): string {
  return `https://github.com/Tsuiwiki/childhood-library/blob/main/${path}`
}

export function documentsForWork(workId: string): ResearchDocument[] {
  const work = specialtyCatalog.find((item) => item.id === workId)
  if (!work) return []
  return researchDocuments.filter((document) => document.workTitles.includes(work.title))
}
