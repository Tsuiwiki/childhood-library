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
    id: 'songs-audio-links-05',
    title: '音频链接采集 · 批次 05',
    path: 'docs/research/CHINESE_CHILDRENS_SONGS_BATCH_05_AUDIO_LINKS.md',
    description: '汇集正规平台、唱片与机构页面的人工试听入口，逐版本保留来源。',
    updated: '2026-11-21',
    workTitles: ['一分钱', '快乐的节日', '丢手绢', '听妈妈讲那过去的事情', '我们的田野', '红星歌', '小螺号', '采蘑菇的小姑娘', '种太阳', '歌声与微笑', '让我们荡起双桨'],
  },
  {
    id: 'songs-audio-links-06',
    title: '音频链接采集 · 批次 06',
    path: 'docs/research/CHINESE_CHILDRENS_SONGS_BATCH_06_AUDIO_LINKS.md',
    description: '补充 12 首作品、21 条正规平台与公开演绎入口，逐版本保留来源。',
    updated: '2026-11-21',
    workTitles: ['小白船', '小兔子乖乖', '春天在哪里', '两只老虎', '歌唱二小放牛郎', '卖报歌', '拔萝卜', '劳动最光荣', '小星星', '泥娃娃', '读书郎', '外婆的澎湖湾'],
  },
  {
    id: 'songs-audio-links-07',
    title: '节目与专辑目录 · 批次 07',
    path: 'docs/research/CHINESE_CHILDRENS_SONGS_BATCH_07_AUDIO_LINKS.md',
    description: '记录央视节目、具体演唱片段与专辑级目录，区分逐曲和专辑入口。',
    updated: '2026-11-21',
    workTitles: ['共产儿童团歌', '小燕子', '中国儿童之歌'],
  },
  {
    id: 'songs-audio-quality-08',
    title: '正规专辑与音源质量 · 批次 08',
    path: 'docs/research/CHINESE_CHILDRENS_SONGS_BATCH_08_AUDIO_QUALITY.md',
    description: '汇总正规专辑、规格与传播线索；不把平台规格当作实际听音评价。',
    updated: '2026-11-21',
    workTitles: ['一分钱', '拔萝卜', '让我们荡起双桨', '快乐的节日'],
  },
  {
    id: 'songs-audio-catalog-10',
    title: '系列专辑扩展采集 · 批次 10',
    path: 'docs/research/CHINESE_CHILDRENS_SONGS_BATCH_10_AUDIO_CATALOG.md',
    description: '整理五张系列专辑与逐曲目录，保留平台曲目数量差异。',
    updated: '2026-11-21',
    workTitles: ['小燕子', '让我们荡起双桨', '我们的田野', '读书郎', '卖报歌', '快乐的节日', '采蘑菇的小姑娘'],
  },
  {
    id: 'songs-broadcast-choirs-11',
    title: '广播合唱团与机构录音 · 批次 11',
    path: 'docs/research/CHINESE_CHILDRENS_SONGS_BATCH_11_BROADCAST_CHOIRS.md',
    description: '追溯广播合唱团、唱片发行和机构档案，区分发行年与录音年。',
    updated: '2026-11-21',
    workTitles: ['让我们荡起双桨', '共产儿童团歌', '只怕不抵抗', '歌唱二小放牛郎', '采蘑菇的小姑娘'],
  },
  {
    id: 'songs-china-records-12',
    title: '中国唱片与广播历史档案 · 批次 12',
    path: 'docs/research/CHINESE_CHILDRENS_SONGS_BATCH_12_CHINA_RECORDS_ARCHIVES.md',
    description: '整理唱片编号、历史磁带与出版社产品目录，不把目录页写成音频文件。',
    updated: '2026-11-21',
    workTitles: ['我们的田野', '卖报歌', '红星歌', '我们多么幸福', '嘀哩，嘀哩'],
  },
  {
    id: 'songs-china-records-13',
    title: '中国唱片历史发行 · 批次 13',
    path: 'docs/research/CHINESE_CHILDRENS_SONGS_BATCH_13_CHINA_RECORDS_CLASSICS.md',
    description: '央广少年广播合唱团 1970/1979 年唱片与电影歌曲合辑的曲目及试听入口。',
    updated: '2026-11-21',
    workTitles: ['让我们荡起双桨', '共产儿童团歌'],
  },
  // 批次 14–23：按 docs/research/ 原文逐条登记，仅作 GitHub 档案导航。
  {
    id: 'songs-research-14',
    title: '逐曲研究档案 · 批次 14',
    path: 'docs/research/CHINESE_CHILDRENS_SONGS_BATCH_14_RADIO_CHOIR_ARCHIVES.md',
    description: '1970 年代历史唱片与《金色年华》逐曲入口；仅登记来源线索，不代表公开授权。',
    updated: '2026-11-21',
    workTitles: ['让我们荡起双桨', '我们的田野'],
  },
  {
    id: 'songs-research-15',
    title: '逐曲研究档案 · 批次 15',
    path: 'docs/research/CHINESE_CHILDRENS_SONGS_BATCH_15_AUDIO_SCORE_SOURCES.md',
    description: '图书馆逐曲音频与曲谱入口；仅登记来源线索，不代表公开授权。',
    updated: '2026-11-24',
    workTitles: ['卖报歌', '让我们荡起双桨', '我们的田野', '快乐的节日', '一分钱', '我爱北京天安门', '小小螺丝帽', '采蘑菇的小姑娘', '歌声与微笑'],
  },
  {
    id: 'songs-research-16',
    title: '逐曲研究档案 · 批次 16',
    path: 'docs/research/CHINESE_CHILDRENS_SONGS_BATCH_16_LIBRARY_AUDIO_SCORE_CATALOGS.md',
    description: '清华馆藏童声唱片与正规曲谱目录；仅登记来源线索，不代表公开授权。',
    updated: '2026-11-24',
    workTitles: ['歌声与微笑', '快乐的节日', '我们的田野', '让我们荡起双桨', '小老鼠上灯台', '春天在哪里', '听妈妈讲那过去的事情', '采蘑菇的小姑娘'],
  },
  {
    id: 'songs-research-17',
    title: '逐曲研究档案 · 批次 17',
    path: 'docs/research/CHINESE_CHILDRENS_SONGS_BATCH_17_PUBLISHED_SCORE_CATALOGS.md',
    description: '出版曲集目录扩展与示范音频线索；仅登记来源线索，不代表公开授权。',
    updated: '2026-11-24',
    workTitles: ['小鸭子', '我爱北京天安门', '丢手绢', '虫儿飞', '童年', '小燕子', '数蛤蟆'],
  },
  {
    id: 'songs-research-18',
    title: '逐曲研究档案 · 批次 18',
    path: 'docs/research/CHINESE_CHILDRENS_SONGS_BATCH_18_AUDIO_CATALOGS.md',
    description: '清华图书馆馆藏目录逐曲核验；仅登记来源线索，不代表公开授权。',
    updated: '2026-11-24',
    workTitles: ['歌声与微笑', '快乐的节日', '我们的田野', '让我们荡起双桨', '采蘑菇的小姑娘'],
  },
  {
    id: 'songs-research-19',
    title: '逐曲研究档案 · 批次 19',
    path: 'docs/research/CHINESE_CHILDRENS_SONGS_BATCH_19_SCORE_LYRICS_METADATA.md',
    description: '曲谱目录交叉匹配与作品史料核验；仅登记来源线索，不代表公开授权。',
    updated: '2026-11-24',
    workTitles: ['采蘑菇的小姑娘', '春天在哪里', '快乐的节日', '歌声与微笑', '我爱北京天安门', '让我们荡起双桨', '听妈妈讲那过去的事情', '我们的田野', '小燕子', '卖报歌'],
  },
  {
    id: 'songs-research-20',
    title: '逐曲研究档案 · 批次 20',
    path: 'docs/research/CHINESE_CHILDRENS_SONGS_BATCH_20_AUDIO_SCORE_LYRICS.md',
    description: '音频、曲谱与歌词出处（2026-11-24）；仅登记来源线索，不代表公开授权。',
    updated: '2026-11-24',
    workTitles: ['听妈妈讲那过去的事情', '小燕子', '快乐的节日', '让我们荡起双桨', '我们的田野', '卖报歌'],
  },
  {
    id: 'songs-research-21',
    title: '逐曲研究档案 · 批次 21',
    path: 'docs/research/CHINESE_CHILDRENS_SONGS_BATCH_21_EARLY_RECORDINGS_HISTORY.md',
    description: '早期演唱者、历史传播与曲谱线索（2026-11-24）；仅登记来源线索，不代表公开授权。',
    updated: '2026-11-24',
    workTitles: ['听妈妈讲那过去的事情', '小燕子', '快乐的节日', '让我们荡起双桨', '我们的田野', '卖报歌'],
  },
  {
    id: 'songs-research-22',
    title: '逐曲研究档案 · 批次 22',
    path: 'docs/research/CHINESE_CHILDRENS_SONGS_BATCH_22_ARCHIVAL_AUDIO_SCORES.md',
    description: '儿童歌曲音频、曲谱与馆藏线索补充·批次22；仅登记来源线索，不代表公开授权。',
    updated: '2026-11-24',
    workTitles: ['听妈妈讲那过去的事情', '小燕子', '我们的田野', '让我们荡起双桨'],
  },
  {
    id: 'songs-research-23',
    title: '逐曲研究档案 · 批次 23',
    path: 'docs/research/CHINESE_CHILDRENS_SONGS_BATCH_23_SCORE_HISTORY.md',
    description: '儿童歌曲曲谱版本与创作出处补充·批次23；仅登记来源线索，不代表公开授权。',
    updated: '2026-11-24',
    workTitles: ['听妈妈讲那过去的事情', '快乐的节日', '卖报歌'],
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
