import { researchSamples, type ResearchSample } from '@/research/samples'
import { specialtyCatalog } from '@/research/specialties'

export type AudioLinkKind = 'recording' | 'video' | 'album' | 'archive'

export interface AudioLinkRecord {
  id: string
  title: string
  version: string
  platform: string
  url: string
  note: string
  kind: AudioLinkKind
  batch: string
}

export const audioLinkKinds: { value: 'all' | AudioLinkKind; label: string }[] = [
  { value: 'all', label: '全部入口' },
  { value: 'recording', label: '单曲 / 录音' },
  { value: 'video', label: '视频演绎' },
  { value: 'album', label: '专辑目录' },
  { value: 'archive', label: '历史档案' },
]

export const audioLinkBatches: Record<string, { title: string; path: string }> = {
  '04': { title: '批次 04 · 音频入口与版本核验', path: 'docs/research/CHINESE_CHILDRENS_SONGS_AUDIO_BATCH_04.md' },
  '04A': { title: '批次 04 · 音频优先采集', path: 'docs/research/CHINESE_CHILDRENS_SONGS_BATCH_04_AUDIO.md' },
  '05': { title: '批次 05 · 音频链接', path: 'docs/research/CHINESE_CHILDRENS_SONGS_BATCH_05_AUDIO_LINKS.md' },
  '06': { title: '批次 06 · 新增作品', path: 'docs/research/CHINESE_CHILDRENS_SONGS_BATCH_06_AUDIO_LINKS.md' },
  '07': { title: '批次 07 · 节目与专辑', path: 'docs/research/CHINESE_CHILDRENS_SONGS_BATCH_07_AUDIO_LINKS.md' },
  '08': { title: '批次 08 · 正规专辑', path: 'docs/research/CHINESE_CHILDRENS_SONGS_BATCH_08_AUDIO_QUALITY.md' },
  '10': { title: '批次 10 · 系列专辑', path: 'docs/research/CHINESE_CHILDRENS_SONGS_BATCH_10_AUDIO_CATALOG.md' },
  '11': { title: '批次 11 · 广播合唱团', path: 'docs/research/CHINESE_CHILDRENS_SONGS_BATCH_11_BROADCAST_CHOIRS.md' },
  '12': { title: '批次 12 · 唱片档案', path: 'docs/research/CHINESE_CHILDRENS_SONGS_BATCH_12_CHINA_RECORDS_ARCHIVES.md' },
  '13': { title: '批次 13 · 中国唱片历史发行', path: 'docs/research/CHINESE_CHILDRENS_SONGS_BATCH_13_CHINA_RECORDS_CLASSICS.md' },
  '14': { title: '批次 14 · 1970 年代历史唱片与《金色年', path: 'docs/research/CHINESE_CHILDRENS_SONGS_BATCH_14_RADIO_CHOIR_ARCHIVES.md' },
  '15': { title: '批次 15 · 图书馆逐曲音频与曲谱入口', path: 'docs/research/CHINESE_CHILDRENS_SONGS_BATCH_15_AUDIO_SCORE_SOURCES.md' },
  '16': { title: '批次 16 · 清华馆藏童声唱片与正规曲谱目录', path: 'docs/research/CHINESE_CHILDRENS_SONGS_BATCH_16_LIBRARY_AUDIO_SCORE_CATALOGS.md' },
  '17': { title: '批次 17 · 出版曲集目录扩展与示范音频线索', path: 'docs/research/CHINESE_CHILDRENS_SONGS_BATCH_17_PUBLISHED_SCORE_CATALOGS.md' },
  '18': { title: '批次 18 · 清华图书馆馆藏目录逐曲核验', path: 'docs/research/CHINESE_CHILDRENS_SONGS_BATCH_18_AUDIO_CATALOGS.md' },
  '19': { title: '批次 19 · 曲谱目录交叉匹配与作品史料核验', path: 'docs/research/CHINESE_CHILDRENS_SONGS_BATCH_19_SCORE_LYRICS_METADATA.md' },
  '20': { title: '批次 20 · 音频、曲谱与歌词出处（2026-', path: 'docs/research/CHINESE_CHILDRENS_SONGS_BATCH_20_AUDIO_SCORE_LYRICS.md' },
  '21': { title: '批次 21 · 早期演唱者、历史传播与曲谱线索（', path: 'docs/research/CHINESE_CHILDRENS_SONGS_BATCH_21_EARLY_RECORDINGS_HISTORY.md' },
  '22': { title: '批次 22 · 儿童歌曲音频、曲谱与馆藏线索补充', path: 'docs/research/CHINESE_CHILDRENS_SONGS_BATCH_22_ARCHIVAL_AUDIO_SCORES.md' },
  '23': { title: '批次 23 · 儿童歌曲曲谱版本与创作出处补充·', path: 'docs/research/CHINESE_CHILDRENS_SONGS_BATCH_23_SCORE_HISTORY.md' },
}

// Curated metadata from the tracked GitHub research documents. These are external
// navigation records, not claims that a local audio file or redistribution right exists.
export const audioSourceLinks: AudioLinkRecord[] = [
  { id: '05-01', title: '一分钱', version: '小蓓蕾组合', platform: 'Apple Music', url: 'https://music.apple.com/us/album/潘振声儿童歌曲集锦/1641845621', note: '《潘振声儿童歌曲集锦》曲目，约 1:31，页面标注 2000 年发行。', kind: 'recording', batch: '05' },
  { id: '05-02', title: '快乐的节日', version: '儿歌点点', platform: 'Apple Music', url: 'https://music.apple.com/us/song/1713057031', note: '2023 年发行的后期演绎版本。', kind: 'recording', batch: '05' },
  { id: '05-03', title: '丢手绢', version: '小蓓蕾组合', platform: 'Apple Music', url: 'https://music.apple.com/us/song/1609582246', note: '《童歌经典02》，页面标注 2000 年发行。', kind: 'recording', batch: '05' },
  { id: '05-04', title: '听妈妈讲那过去的事情', version: '小蓓蕾组合', platform: 'Apple Music', url: 'https://music.apple.com/us/song/1609599826', note: '《童歌经典08》，页面标注 2000 年发行。', kind: 'recording', batch: '05' },
  { id: '05-05', title: '听妈妈讲那过去的事情', version: '中国武警男声合唱团', platform: 'Apple Music', url: 'https://music.apple.com/us/song/1790113293', note: '《辉煌之声II 听妈妈讲那过去的事情》，2008 年发行。', kind: 'recording', batch: '05' },
  { id: '05-06', title: '我们的田野', version: '上海人民广播电台少年儿童广播合唱团、叶红', platform: 'Apple Music', url: 'https://music.apple.com/us/album/我们的田野/6793372676?i=6793372683', note: '《可爱的小白杨》曲目，3:24；中国唱片发行信息待核录音年代。', kind: 'recording', batch: '05' },
  { id: '05-07', title: '我们的田野', version: '北京市少年宫合唱团', platform: 'Apple Music', url: 'https://music.apple.com/us/song/1681475279', note: '《爱国歌曲大家唱》，2009 年发行。', kind: 'recording', batch: '05' },
  { id: '05-08', title: '红星歌', version: '中央广播少年儿童合唱团', platform: 'Apple Music', url: 'https://music.apple.com/us/album/中国电影百年歌曲精萃-五/1888430784', note: '《中国电影百年歌曲精萃（五）》曲目，1:33，中国唱片发行线索。', kind: 'recording', batch: '05' },
  { id: '05-09', title: '红星歌', version: '中央人民广播电台少年广播合唱团', platform: '文艺作品库', url: 'https://ku.artnchina.com/page/opus/music/music.html?fileName=%E7%BA%A2%E6%98%9F%E6%AD%8C+%E7%AE%80%E8%B0%B1.jpg&id=ccaad27035fa42d0a0b198d0ef6e4642&path=clfac%2Fupload%2F32c478753f65a1230306b27a44071abb.jpg&type=audio', note: '作品页列出音频文件名和曲谱图，发行信息不完整。', kind: 'recording', batch: '05' },
  { id: '05-10', title: '小螺号', version: '程琳', platform: 'Apple Music', url: 'https://music.apple.com/us/song/1619505686', note: '《童年的小摇车》，页面标注 1982-05-21，词曲署名付林。', kind: 'recording', batch: '05' },
  { id: '05-11', title: '采蘑菇的小姑娘', version: '青燕子演唱组、广州交响乐团', platform: 'Apple Music', url: 'https://music.apple.com/us/album/采蘑菇的小姑娘/1634086039?i=1634086435', note: '《草原牧歌（少女与弦乐四重奏）》曲目，3:23，2000 年发行。', kind: 'recording', batch: '05' },
  { id: '05-12', title: '种太阳', version: '小蓓蕾组合', platform: 'Apple Music', url: 'https://music.apple.com/us/song/1609599822', note: '《童歌经典08》，页面标注 2000 年发行。', kind: 'recording', batch: '05' },
  { id: '05-13', title: '种太阳', version: '会声花儿组合', platform: 'Apple Music', url: 'https://music.apple.com/us/song/1645485406', note: '《儿童歌曲1》，2002 年发行。', kind: 'recording', batch: '05' },
  { id: '05-14', title: '歌声与微笑', version: '上海小荧星儿童合唱团', platform: '江西理工大学', url: 'https://hsjd.jxust.edu.cn/content.jsp?urltype=news.NewsContentUrl&wbnewsid=1448&wbtreeid=1060', note: '机构页面附 MP3 入口；现有本地研究录音已另行登记。', kind: 'recording', batch: '05' },
  { id: '05-15', title: '歌声与微笑', version: '上海小荧星艺术团合唱团等', platform: 'bilibili', url: 'https://www.bilibili.com/video/BV1LM4m1R7WY/', note: '标注 1986 年上海电视节片段；上传者声明未经授权禁止转载。', kind: 'video', batch: '05' },
  { id: '05-16', title: '让我们荡起双桨', version: '中央人民广播电台少年儿童合唱团', platform: 'YouTube', url: 'https://www.youtube.com/watch?v=0HD7QrrDQkc', note: 'Release-Topic，《中国电影百年歌曲精萃（三）II》，中国唱片集团发行线索。', kind: 'video', batch: '05' },
  { id: '05-17', title: '让我们荡起双桨', version: '贺斌演唱', platform: 'YouTube', url: 'https://www.youtube.com/watch?v=1ThcRM56bjE', note: 'CCTV 少儿歌曲专题播放页，介绍电影《祖国的花朵》主题曲。', kind: 'video', batch: '05' },
  { id: '05-18', title: '让我们荡起双桨', version: '机构嵌入视频', platform: '腾讯视频', url: 'https://v.qq.com/txp/iframe/player.html?vid=e32563ovuaf', note: '南方医科大学页面嵌入的腾讯视频入口。', kind: 'video', batch: '05' },

  { id: '06-01', title: '小白船', version: '北京蓝天艺术合唱小组', platform: 'Apple Music', url: 'https://music.apple.com/us/song/1648937746', note: '《中外儿童金曲（2）》，2015 年发行。', kind: 'recording', batch: '06' },
  { id: '06-02', title: '小白船', version: '上海·黄浦春天少年合唱团', platform: 'YouTube', url: 'https://www.youtube.com/watch?v=oSV1-zVXVyI', note: '合唱团公开频道 2021 年演绎，陈明茹编配。', kind: 'video', batch: '06' },
  { id: '06-03', title: '小兔子乖乖', version: '小蓓蕾组合', platform: 'Apple Music', url: 'https://music.apple.com/us/song/1642289570', note: '《亲子儿童歌曲02》，2000 年发行。', kind: 'recording', batch: '06' },
  { id: '06-04', title: '小兔子乖乖', version: '儿歌点点', platform: 'Apple Music', url: 'https://music.apple.com/us/song/1713056666', note: '《点点儿歌》，2023 年发行。', kind: 'recording', batch: '06' },
  { id: '06-05', title: '春天在哪里', version: '新时代小星星组合', platform: 'Apple Music', url: 'https://music.apple.com/us/song/1841836890', note: '《儿童歌谣（第一辑）》，页面标注 1990 年。', kind: 'recording', batch: '06' },
  { id: '06-06', title: '春天在哪里', version: '儿歌点点', platform: 'Apple Music', url: 'https://music.apple.com/us/song/1713056788', note: '《点点儿歌》，2023 年发行。', kind: 'recording', batch: '06' },
  { id: '06-07', title: '两只老虎', version: '小蓓蕾组合', platform: 'Apple Music', url: 'https://music.apple.com/us/song/1642289580', note: '《亲子儿童歌曲02》，2000 年发行。', kind: 'recording', batch: '06' },
  { id: '06-08', title: '两只老虎', version: '小星星儿童合唱团', platform: 'Apple Music', url: 'https://music.apple.com/us/song/1848273408', note: '《儿歌 爸爸妈妈我好爱你（下）》，页面标注 1991 年。', kind: 'recording', batch: '06' },
  { id: '06-09', title: '歌唱二小放牛郎', version: '小海燕少年合唱团', platform: 'Apple Music', url: 'https://music.apple.com/us/song/1620329482', note: '《爱国歌曲大家唱100首发烧童声合唱3》，2010 年发行。', kind: 'recording', batch: '06' },
  { id: '06-10', title: '歌唱二小放牛郎', version: '小蓓蕾组合', platform: 'Apple Music', url: 'https://music.apple.com/us/song/1607021497', note: '《少年广播合唱集锦》，2000 年发行。', kind: 'recording', batch: '06' },
  { id: '06-11', title: '卖报歌', version: '儿歌多多、小呱呱乐队', platform: 'Apple Music', url: 'https://music.apple.com/us/song/1779248166', note: '2022 年后期演绎，不标记为历史首录。', kind: 'recording', batch: '06' },
  { id: '06-12', title: '拔萝卜', version: '小蓓蕾组合', platform: 'Apple Music', url: 'https://music.apple.com/us/song/1609599760', note: '《童歌经典04》，2000 年发行。', kind: 'recording', batch: '06' },
  { id: '06-13', title: '拔萝卜', version: '小星星儿童合唱团', platform: 'Apple Music', url: 'https://music.apple.com/us/song/1848269234', note: '《儿歌 爸爸妈妈我好爱你（上）》，页面标注 1991 年。', kind: 'recording', batch: '06' },
  { id: '06-14', title: '劳动最光荣', version: '中央人民广播电台少年广播合唱团', platform: 'Apple Music', url: 'https://music.apple.com/us/song/1842717534', note: '唱片目录入口；发行年份不能直接当作录音年份。', kind: 'recording', batch: '06' },
  { id: '06-15', title: '劳动最光荣', version: '小蓓蕾组合', platform: 'Apple Music', url: 'https://music.apple.com/us/song/1610055182', note: '《童歌经典07》，2000 年发行。', kind: 'recording', batch: '06' },
  { id: '06-16', title: '小星星', version: '新和儿童乐队合唱团', platform: 'Apple Music', url: 'https://music.apple.com/us/song/977656761', note: '《儿童歌曲第二集 恐龙救生队·我爱中华》，页面标注 1979 年。', kind: 'recording', batch: '06' },
  { id: '06-17', title: '泥娃娃', version: '新和儿童乐队合唱团', platform: 'Apple Music', url: 'https://music.apple.com/us/song/978032129', note: '《儿童歌曲第三集 小甜甜·上学》，页面标注 1979 年。', kind: 'recording', batch: '06' },
  { id: '06-18', title: '泥娃娃', version: '小蓓蕾组合', platform: 'Apple Music', url: 'https://music.apple.com/us/song/1650865532', note: '《快乐学唱歌（03）》，2000 年发行的逐句教学版本。', kind: 'recording', batch: '06' },
  { id: '06-19', title: '读书郎', version: '小蓓蕾组合', platform: 'Apple Music', url: 'https://music.apple.com/us/song/1609599081', note: '《童歌经典04》，2000 年发行。', kind: 'recording', batch: '06' },
  { id: '06-20', title: '读书郎', version: '会声花儿组合', platform: 'Apple Music', url: 'https://music.apple.com/us/song/1645567949', note: '《儿童歌曲4》，2003 年发行。', kind: 'recording', batch: '06' },
  { id: '06-21', title: '外婆的澎湖湾', version: 'Cute Princess、Bei Bei', platform: 'Apple Music', url: 'https://music.apple.com/us/song/637354755', note: '《那些年我们一起唱的童谣》，2012 年发行。', kind: 'recording', batch: '06' },

  { id: '07-01', title: '共产儿童团歌', version: 'CCTV 少儿 2018 年六一晚会', platform: 'YouTube', url: 'https://www.youtube.com/watch?v=G2vfI926hqo', note: '官方频道节目片段，属于晚会演出版。', kind: 'video', batch: '07' },
  { id: '07-02', title: '小燕子', version: '门子轩、何语涵', platform: 'YouTube', url: 'https://www.youtube.com/watch?v=CTuNYWly_WU', note: 'CCTV 少儿《音乐快递》节目约 15:22 处。', kind: 'video', batch: '07' },
  { id: '07-03', title: '中国儿童之歌', version: '小蓓蕾组合', platform: 'Apple Music', url: 'https://music.apple.com/cn/song/1641845868', note: '《潘振声儿童歌曲集锦》，页面标注 2000 年。', kind: 'recording', batch: '07' },
  { id: '07-04', title: '潘振声儿童歌曲集锦', version: '小蓓蕾组合', platform: 'Apple Music', url: 'https://music.apple.com/us/album/潘振声儿童歌曲集锦/1641845621', note: '专辑级目录；逐曲身份和版本需分别核对。', kind: 'album', batch: '07' },
  { id: '07-05', title: '童歌经典01', version: '小蓓蕾组合', platform: 'Apple Music', url: 'https://music.apple.com/us/album/童歌经典01/1609581347', note: '专辑页显示 17 首；未核对曲目不冒充新增作品。', kind: 'album', batch: '07' },
  { id: '07-06', title: '童声合唱歌曲', version: '小蓓蕾组合、广州小云雀合唱团等', platform: 'Apple Music', url: 'https://music.apple.com/us/album/童声合唱歌曲/1642775126', note: '21 首、约 61 分钟，作为合唱版本目录入口。', kind: 'album', batch: '07' },

  { id: '08-01', title: '潘振声儿童歌曲集锦', version: '小蓓蕾组合 · 颂今音乐', platform: 'Qobuz', url: 'https://www.qobuz.com/us-en/album/-/udwl0ezrhkuqb', note: '标注 16-bit/44.1kHz；规格信息不等于已试听或获得下载授权。', kind: 'album', batch: '08' },
  { id: '08-02', title: '童声合唱歌曲精选01（齐唱版）', version: '小蓓蕾组合 · 颂今音乐', platform: 'Qobuz', url: 'https://www.qobuz.com/dk-en/album/01/u9mio7mp78o8b', note: '正规专辑与高品质规格线索，录音质量仍需逐曲人工复核。', kind: 'album', batch: '08' },
  { id: '08-03', title: '童歌经典01', version: '小蓓蕾组合 · 颂今音乐', platform: 'Amazon Music', url: 'https://music.amazon.es/albums/B09SDML4D5', note: '列出 17 首曲目及时长；当前未确认无损规格。', kind: 'album', batch: '08' },
  { id: '08-04', title: '童声合唱歌曲', version: '小蓓蕾组合、广州小云雀合唱团等', platform: 'Amazon Music', url: 'https://music.amazon.com/albums/B0BCM5Q3KJ', note: '用于多合唱团曲目和版本交叉核对。', kind: 'album', batch: '08' },

  { id: '10-01', title: '童歌经典03', version: '小蓓蕾组合', platform: 'Apple Music', url: 'https://music.apple.com/us/album/童歌经典03/1609612603', note: '平台显示 16 首；辅助目录列出 18 个标题，数量差异待核。', kind: 'album', batch: '10' },
  { id: '10-02', title: '童歌经典04', version: '小蓓蕾组合', platform: 'Amazon Music', url: 'https://music.amazon.ca/albums/B09S9XDJ2X', note: '15 首、约 39 分钟，含《读书郎》《卖报歌》《采蘑菇的小姑娘》等。', kind: 'album', batch: '10' },
  { id: '10-03', title: '童歌经典06', version: '小蓓蕾组合', platform: 'Amazon Music', url: 'https://music.amazon.com/albums/B09SKMY1KQ', note: '14 首、约 37 分钟，含《兰花草》《蜗牛与黄鹂鸟》《捉泥鳅》等。', kind: 'album', batch: '10' },
  { id: '10-04', title: '童歌经典07', version: '小蓓蕾组合', platform: 'Amazon Music', url: 'https://music.amazon.es/albums/B09SHWZS5Y', note: '16 首、约 37 分钟，含《小燕子》《小小少年》《劳动最光荣》等。', kind: 'album', batch: '10' },
  { id: '10-05', title: '童声合唱歌曲精选07', version: '小蓓蕾组合等', platform: 'Amazon Music', url: 'https://music.amazon.com/albums/B09RV9SPK2', note: '15 首、约 54 分钟；横跨民歌、儿童合唱与英文合唱作品。', kind: 'album', batch: '10' },

  { id: '11-01', title: '中国电影百年歌曲精萃（三）', version: '中央人民广播电台少年儿童合唱团等', platform: 'Apple Music', url: 'https://music.apple.com/us/album/%E7%BA%A2%E5%86%9B%E6%A1%A5/1888431701?i=1888432145', note: '含《让我们荡起双桨》《共产儿童团歌》；发行信息不直接证明录音日期。', kind: 'album', batch: '11' },
  { id: '11-02', title: '正义之声—100首优秀抗战歌曲集', version: '中央人民广播电台少年广播合唱团等', platform: 'Apple Music', url: 'https://music.apple.com/us/album/%E6%AD%A3%E4%B9%89%E4%B9%8B%E5%A3%B0-100%E9%A6%96%E4%BC%98%E7%A7%80%E6%8A%97%E6%88%98%E6%AD%8C%E6%9B%B2%E9%9B%86/1842732073', note: '含《只怕不抵抗》《酸枣刺》《红缨枪》《歌唱二小放牛郎》等版本线索。', kind: 'album', batch: '11' },
  { id: '11-03', title: '歌唱二小放牛郎', version: '中央人民广播电台少年广播合唱团', platform: 'Apple Music', url: 'https://music.apple.com/us/album/%E6%AD%8C%E5%94%B1%E4%BA%8C%E5%B0%8F%E6%94%BE%E7%89%9B%E9%83%8E/1842732073?i=1842733960', note: '可定位具体曲目与演唱团体，6:20；录音年代仍待核。', kind: 'recording', batch: '11' },
  { id: '11-04', title: '我们是抗战的孩子', version: '上海人民广播电台少年儿童广播合唱团', platform: 'Apple Music', url: 'https://music.apple.com/us/album/%E6%88%91%E4%BB%AC%E6%98%AF%E6%8A%97%E6%88%98%E7%9A%84%E5%AD%A9%E5%AD%90/1842732073?i=1842733846', note: '目前核实到该团的一首具体发行曲目，1:10。', kind: 'recording', batch: '11' },
  { id: '11-05', title: '云雀之声', version: '广州小云雀合唱团', platform: 'Apple Music', url: 'https://music.apple.com/us/album/%E4%BA%91%E9%9B%80%E4%B9%8B%E5%A3%B0/1801509613', note: '2008 年正规厂牌发行目录，15 首、56 分钟。', kind: 'album', batch: '11' },
  { id: '11-06', title: '云雀之声4', version: '广州小云雀合唱团', platform: 'Amazon Music', url: 'https://music.amazon.com/albums/B09Z76RBDY', note: '13 首、约 61 分钟；偏合唱艺术与儿童文化拓展。', kind: 'album', batch: '11' },
  { id: '11-07', title: '中国经典古诗100首歌曲精选2', version: '广州小云雀合唱团小童星', platform: 'Amazon Music', url: 'https://music.amazon.in/albums/B0C4TVD462', note: '20 首古诗歌曲目录，可连接诗词馆继续核验词曲和编曲。', kind: 'album', batch: '11' },

  { id: '12-01', title: '我们的歌：杨鸿年和他的孩子们唱响经典童声合唱120首', version: '杨鸿年、杨力、王天阳等', platform: '豆瓣音乐', url: 'https://music.douban.com/subject/25733448/', note: '中国唱片总公司 8CD 目录，条形码 9787799922690；不是逐曲播放页。', kind: 'archive', batch: '12' },
  { id: '12-02', title: '金色年华 HL-152', version: '中央人民广播电台少年广播合唱团', platform: 'Discogs Fandom', url: 'https://discogs.fandom.com/zh/wiki/中国唱片/HL', note: '1983 年磁带目录线索，需以实物、封套或权威馆藏复核。', kind: 'archive', batch: '12' },
  { id: '12-03', title: '中央人民广播电台少年儿童合唱团', version: '团体与《金色年华》资料', platform: '百度百科', url: 'https://bkso.baidu.com/item/中央人民广播电台少年儿童合唱团/10562223?fromModule=lemma_inlink', note: '记录团体与专辑曲目线索，不是音频文件入口。', kind: 'archive', batch: '12' },
  { id: '12-04', title: '中华儿歌珍藏集 CCD-2838/2843', version: '中唱上海 6CD', platform: '我爱ABC', url: 'https://www.oiabc.net/1497.html', note: '第三方目录提供逐曲演唱者、指挥、伴奏与时长，需再由唱片资料复核。', kind: 'archive', batch: '12' },
  { id: '12-05', title: '中央人民广播电台少年儿童合唱团歌曲列表', version: '广播合唱团曲目索引', platform: 'RapZH', url: 'https://rapzh.com/artists/384677/songs', note: '第三方聚合目录，仅用于发现曲目和专辑关系。', kind: 'archive', batch: '12' },
  { id: '12-06', title: '中国广播少年合唱团歌曲列表', version: '广播合唱团曲目索引', platform: 'RapZH', url: 'https://rapzh.com/artists/355783/songs', note: '含《丢手绢》《酸枣刺》《只怕不抵抗》等目录线索。', kind: 'archive', batch: '12' },
  { id: '12-07', title: '宝宝听唱学儿歌（季节篇）', version: '上海音乐出版社', platform: '出版社产品目录', url: 'https://www.smph.cn/NewsDetails.aspx?id=538', note: '30 首，官方说明配示范、伴奏和电子歌谱；页面本身不是逐曲音频。', kind: 'archive', batch: '12' },
  { id: '12-08', title: '宝宝听唱学儿歌——幸福的童年', version: '上海音乐出版社', platform: '出版社产品目录', url: 'https://www.smph.cn/NewsDetails.aspx?id=545', note: '18 首，全新编曲制作，可沿官方数字产品继续核验。', kind: 'archive', batch: '12' },
  { id: '12-09', title: '宝宝听唱学儿歌——我爱我的大中国', version: '上海音乐出版社', platform: '出版社产品目录', url: 'https://www.smph.cn/NewsDetails.aspx?id=542', note: '含《大中国》《少年强》《少年，少年，祖国的春天》等配套资源线索。', kind: 'archive', batch: '12' },
  { id: '12-10', title: '最好的未来', version: '上海音乐出版社', platform: '出版社产品目录', url: 'https://www.smph.cn/NewsDetails.aspx?id=543', note: '同系列 14 首产品目录；没有把产品介绍页写成直接音频。', kind: 'archive', batch: '12' },

  // Batch 04 (audio entrance/version verification): later recorded versions only.
  { id: '04-01', title: '丢手绢', version: '刘玉兰', platform: 'Apple Music', url: 'https://music.apple.com/us/song/1588856638', note: '《汇悦经典儿歌大全（一）》，2020 年后期演唱版本。', kind: 'recording', batch: '04' },
  { id: '04-02', title: '丢手绢', version: '乔柯', platform: 'Apple Music', url: 'https://music.apple.com/us/album/丢手绢/1874234675?i=1874234676', note: '《宝宝听唱学儿歌——记忆中的童声》，上海音乐出版社相关发行，页面标注 2025 年。', kind: 'recording', batch: '04' },
  { id: '04-03', title: '听妈妈讲那过去的事情', version: '陈心蕊', platform: 'Apple Music', url: 'https://music.apple.com/us/song/1800154363', note: 'EP，2017 年后期演唱版本。', kind: 'recording', batch: '04' },
  { id: '04-04', title: '听妈妈讲那过去的事情', version: '国家大剧院合唱团现场版', platform: 'Apple Music Classical', url: 'https://classical.music.apple.com/cn/album/1781199453', note: '《永恒的旋律》国家大剧院合唱团经典作品音乐会，2024 年现场版。', kind: 'recording', batch: '04' },
  { id: '04-05', title: '听妈妈讲那过去的事情', version: '中国爱乐乐团音乐会版本', platform: 'Apple Music Classical', url: 'https://classical.music.apple.com/cn/album/1544206133', note: '2014 年中国爱乐乐团交响音乐会合辑，平台页面列出该曲。', kind: 'recording', batch: '04' },

  // Batch 04 audio-first: the one traceable release-metadata entrance, not the
  // unlicensed download aggregator pages explicitly excluded by that document.
  { id: '04A-01', title: '丢手绢', version: '小蓓蕾组合 Topic', platform: 'YouTube', url: 'https://www.youtube.com/watch?v=bIaUuDm067k', note: '颂今音乐提供的自动生成 Topic，《童歌经典02》标注 2000 年发行；发行元数据入口，不是 1940 年代原始录音。', kind: 'video', batch: '04A' },

  { id: '08-05', title: '童声合唱歌曲精选01（齐唱版）', version: '小蓓蕾组合 · 颂今音乐', platform: 'TIDAL', url: 'https://tidal.com/album/214215436', note: '17 首曲目可与 Qobuz 交叉核对；页面不是下载入口。', kind: 'album', batch: '08' },
  { id: '08-06', title: '小蓓蕾组合', version: '平台 Top Songs 目录', platform: 'Apple Music', url: 'https://music.apple.com/us/artist/小蓓蕾组合/1029540804', note: '平台推荐曲目总览；页面无公开播放量，不作传播度结论。', kind: 'archive', batch: '08' },
  { id: '10-06', title: '童歌经典07', version: '小蓓蕾组合', platform: 'Apple Music', url: 'https://music.apple.com/us/album/童歌经典07/1610054690', note: '与 Amazon Music 页面交叉确认专辑身份，含《小燕子》《让我们荡起双桨》等版本线索。', kind: 'album', batch: '10' },

  // Batch 13: China Records historical releases. Four album/artist entrances plus
  // ten work-level clues, all marked as in-album listening rather than standalone
  // single pages (batch 13 L104). Doc L88 says the ten clues are not ten new works.
  { id: '13-01', title: '藏族小朋友歌唱毛主席（Single）', version: '周义瑛、中央人民广播电台少年广播合唱团 · 1970', platform: 'Apple Music', url: 'https://music.apple.com/us/album/藏族小朋友歌唱毛主席-single/6793380087', note: '1970 年 ℗ 中国唱片，3 首曲目与试听入口；发行年份不必然等于录音年份。', kind: 'album', batch: '13' },
  { id: '13-02', title: '营火熊熊（EP）', version: '中央人民广播电台少年广播合唱团 · 1979', platform: 'Apple Music', url: 'https://music.apple.com/us/album/营火熊熊-ep/6793393064', note: '1979 年 ℗ 中国唱片，5 首少年生活与夏令营题材曲目。', kind: 'album', batch: '13' },
  { id: '13-03', title: '中国电影百年歌曲精萃（三）· 1971', version: '中央人民广播电台少年儿童合唱团', platform: 'Apple Music', url: 'https://music.apple.com/us/album/中国电影百年歌曲精萃/1888431701', note: '1971 年 ℗ 中国唱片，页面列出《让我们荡起双桨》《共产儿童团歌》。', kind: 'album', batch: '13' },
  { id: '13-04', title: '中央人民广播电台少年广播合唱团', version: '历史发行艺术家目录', platform: 'Apple Music', url: 'https://music.apple.com/us/artist/中央人民广播电台少年广播合唱团/1778148500', note: '列出《金色年华》《泉水》《祖国颂歌》等发行；目录入口不代表逐曲已核验。', kind: 'archive', batch: '13' },
  { id: '13-05', title: '荔枝大又多', version: '中央人民广播电台少年广播合唱团 · 1970', platform: 'Apple Music', url: 'https://music.apple.com/us/album/藏族小朋友歌唱毛主席-single/6793380087', note: '专辑内逐曲试听，1:21；非独立单曲页，词曲作者与母带待核。', kind: 'album', batch: '13' },
  { id: '13-06', title: '藏族小朋友歌唱毛主席', version: '中国唱片 · 1970', platform: 'Apple Music', url: 'https://music.apple.com/us/album/藏族小朋友歌唱毛主席-single/6793380087', note: '专辑内逐曲试听，1:24；音质待试听。', kind: 'album', batch: '13' },
  { id: '13-07', title: '在一起', version: '中央人民广播电台少年广播合唱团 · 1970', platform: 'Apple Music', url: 'https://music.apple.com/us/album/藏族小朋友歌唱毛主席-single/6793380087', note: '专辑内逐曲试听，1:38；非独立单曲页。', kind: 'album', batch: '13' },
  { id: '13-08', title: '蓝天向我们召唤', version: '中央人民广播电台少年广播合唱团 · 1979', platform: 'Apple Music', url: 'https://music.apple.com/us/album/营火熊熊-ep/6793393064', note: 'EP 内逐曲试听，1:55；实体唱片编号与词曲作者待核。', kind: 'album', batch: '13' },
  { id: '13-09', title: '营火熊熊', version: '中央人民广播电台少年广播合唱团 · 1979', platform: 'Apple Music', url: 'https://music.apple.com/us/album/营火熊熊-ep/6793393064', note: 'EP 内逐曲试听，2:21；音质待试听。', kind: 'album', batch: '13' },
  { id: '13-10', title: '航海夏令营营歌', version: '中央人民广播电台少年广播合唱团 · 1979', platform: 'Apple Music', url: 'https://music.apple.com/us/album/营火熊熊-ep/6793393064', note: 'EP 内逐曲试听，2:50；非独立单曲页。', kind: 'album', batch: '13' },
  { id: '13-11', title: '走在上学的路上', version: '中央人民广播电台少年广播合唱团 · 1979', platform: 'Apple Music', url: 'https://music.apple.com/us/album/营火熊熊-ep/6793393064', note: 'EP 内逐曲试听，1:29；录音日期待核。', kind: 'album', batch: '13' },
  { id: '13-12', title: '营火晚会', version: '中央人民广播电台少年广播合唱团 · 1979', platform: 'Apple Music', url: 'https://music.apple.com/us/album/营火熊熊-ep/6793393064', note: 'EP 内逐曲试听，1:07；非独立单曲页。', kind: 'album', batch: '13' },
  { id: '13-13', title: '让我们荡起双桨', version: '中央人民广播电台少年儿童合唱团 · 1971', platform: 'Apple Music', url: 'https://music.apple.com/us/album/中国电影百年歌曲精萃/1888431701', note: '电影《祖国的花朵》插曲，合辑内逐曲试听 2:22；与电影原声是否同版本待核。', kind: 'album', batch: '13' },
  { id: '13-14', title: '共产儿童团歌', version: '中央人民广播电台少年儿童合唱团 · 1971', platform: 'Apple Music', url: 'https://music.apple.com/us/album/中国电影百年歌曲精萃/1888431701', note: '合辑内逐曲试听 1:52；发行年不能直接当作首次录音时间。', kind: 'album', batch: '13' },
  // 批次 15：按 docs/research/ 原文登记的外部来源线索；档案/曲谱/史料类不是可播放音频。
  { id: '15-01', title: '让我们荡起双桨', version: '版本见原档案', platform: '中国曲谱网', url: 'https://www.qupu123.com/shaoer/qizi/p53613.html', note: '标注词：乔羽；曲：刘炽；格式：简谱；页面说明为合唱版本。（批次 15 · L76）', kind: 'archive', batch: '15' },
  { id: '15-02', title: '让我们荡起双桨', version: '版本见原档案', platform: '人人钢琴网', url: 'https://www.everyonepiano.cn/Music-65.html', note: '属于平台编配/整理谱页，需核对谱面完整性及版本适配。（批次 15 · L79）', kind: 'archive', batch: '15' },
  { id: '15-03', title: '让我们荡起双桨', version: '版本见原档案', platform: 'books.google.com', url: 'https://books.google.com/books/about/让我们荡起双桨.html?id=d3OkzQEACAAJ', note: '《让我们荡起双桨：女声合唱五线谱与简谱》，人民音乐出版社，2014，陈一新；可作为正规出版曲谱线索。（批次 15 · L82）', kind: 'archive', batch: '15' },
  { id: '15-04', title: '让我们荡起双桨', version: '版本见原档案', platform: 'www.cangqiang.com.cn', url: 'https://www.cangqiang.com.cn/bofang/141370.html', note: '页面标注刘炽作曲、乔羽作词、降E调、2/4拍；属于在线制谱/视唱页面。（批次 15 · L85）', kind: 'archive', batch: '15' },
  { id: '15-05', title: '卖报歌', version: '版本见原档案', platform: '中国曲谱网', url: 'https://www.qupu123.com/Mobile-view-id-13163.html', note: '页面标注作曲聂耳；版本来源包括其他曲谱站和出版物选编，需按具体版本复核。（批次 15 · L90）另见批次 20 交叉引用。', kind: 'archive', batch: '15' },

  // 批次 19：按 docs/research/ 原文登记的外部来源线索；档案/曲谱/史料类不是可播放音频。
  { id: '19-01', title: '小燕子', version: '版本见原档案', platform: '政府/机构站', url: 'https://www.hbda.gov.cn/info/1940', note: '见批次 19 原档案登记的来源线索。（批次 19 · L68）另见批次 20、21 交叉引用。', kind: 'archive', batch: '19' },
  { id: '19-02', title: '快乐的节日', version: '版本见原档案', platform: 'YouTube', url: 'https://www.youtube.com/watch?v=KNra3AseQJw', note: '文化和旅游部少年儿童合唱艺术歌曲名单：<（批次 19 · L85）另见批次 20、21 交叉引用。', kind: 'video', batch: '19' },
  { id: '19-03', title: '快乐的节日', version: '版本见原档案', platform: '政府/机构站', url: 'https://zwgk.mct.gov.cn/zfxxgkml/wysy/202012/t20201206_917741.html', note: 'CCTV少儿视频页面：<（批次 19 · L86）另见批次 20 交叉引用。', kind: 'archive', batch: '19' },

  // 批次 20：按 docs/research/ 原文登记的外部来源线索；档案/曲谱/史料类不是可播放音频。
  { id: '20-03', title: '快乐的节日', version: '版本见原档案', platform: '中国曲谱网', url: 'https://www.qupu123.com/Mobile-view-id-728.html', note: '页面列出管桦词、李群曲，并提供多个谱本版本；其中一个版本注明选自中国人民保卫儿童全国委员会编著《一九五四年得奖儿童歌曲》。（批次 20 · L34）另见批次 21、23 交叉引用。', kind: 'archive', batch: '20' },
  { id: '20-04', title: '让我们荡起双桨', version: '版本见原档案', platform: 'v.sjs.com.cn', url: 'https://v.sjs.com.cn/ebooks/58E2823C.pdf', note: '搜索结果可见该教材 PDF 中有歌曲简谱、歌词和刘炽（1921—1998）介绍，并说明歌曲为电影《祖国的花朵》插曲。（批次 20 · L41）另见批次 21 交叉引用。', kind: 'archive', batch: '20' },
  { id: '20-06', title: '听妈妈讲那过去的事情', version: '版本见原档案', platform: '人人钢琴网', url: 'https://www.everyonepiano.cn/Music-558.html', note: '页面提供五线谱、双手简谱及PDF入口，并标注作者瞿希贤。该页面是具体谱本入口，但上传者/版本信息仍需进一步核实，正式收藏优先采用出版社或图书馆版本。（批次 20 · L55）另见批次 23 交叉引用。', kind: 'archive', batch: '20' },
  { id: '20-07', title: '听妈妈讲那过去的事情', version: '版本见原档案', platform: '豆瓣', url: 'https://music.douban.com/subject/26377102/', note: '该专辑是后期合唱改编版本，可作为合唱编配参考，不是原始首唱版本。（批次 20 · L60）', kind: 'archive', batch: '20' },
  { id: '20-08', title: '我们的田野', version: '版本见原档案', platform: '中国作家网', url: 'https://www.chinawriter.com.cn/n1/2023/1023/c404018-40100992.html', note: '文章明确称歌曲创作于1953年，管桦作词、张文纲作曲，并从作者个人经历回忆其在小学音乐课中的传播。（批次 20 · L66）', kind: 'archive', batch: '20' },
  { id: '20-09', title: '我们的田野', version: '版本见原档案', platform: 'www.yuntaigo.com', url: 'https://www.yuntaigo.com/book.action?recordid=ZmZ6a21rZmM5Nzg3ODg4ODA2Nzcx', note: '该专辑目录可用来定位正式发行实体CD（条码9787888806771）；目录信息显示出版者为上海文艺音像电子出版社。实际音质与具体录音年份仍需试听/查看唱片内页。（批次 20 · L75）', kind: 'archive', batch: '20' },
  { id: '20-10', title: '卖报歌', version: '版本见原档案', platform: 'YouTube', url: 'https://www.youtube.com/watch?v=kPJa8VJMHhM', note: '重要限制：录音日期和人员信息目前来自上传者描述，尚未找到唱片标签、档案目录或机构资料独立确认。暂列“历史录音候选”，不可标为已确证原始录音。（批次 20 · L88）', kind: 'video', batch: '20' },

  // 批次 21：按 docs/research/ 原文登记的外部来源线索；档案/曲谱/史料类不是可播放音频。
  { id: '21-02', title: '小燕子', version: '版本见原档案', platform: 'www.thepaper.cn', url: 'https://www.thepaper.cn/newsDetail_forward_1869618', note: '王丹凤在访谈中回忆，《护士日记》中哄小孩睡觉的场景原本考虑请女高音演唱，她认为由自己以护士角色的本色嗓音演唱更合适，最终亲自演唱。（批次 21 · L20）', kind: 'archive', batch: '21' },
  { id: '21-03', title: '小燕子', version: '版本见原档案', platform: '新华网', url: 'https://www.xinhuanet.com/politics/2018-05/07/c_129866298.htm', note: '新华社报道确认《小燕子》是王丹凤在电影《护士日记》中唱红的歌曲，并记载上海电影博物馆追思活动放映影片时重现了该演唱。（批次 21 · L22）', kind: 'archive', batch: '21' },
  { id: '21-04', title: '小燕子', version: '版本见原档案', platform: 'www.1905.com', url: 'https://www.1905.com/mdb/film/2210520/', note: '1905电影网也明确记载片中插曲《小燕子》由王丹凤亲自演唱。（批次 21 · L24）', kind: 'archive', batch: '21' },
  { id: '21-05', title: '快乐的节日', version: '版本见原档案', platform: 'www.rmrb.zhouenlai.info', url: 'https://www.rmrb.zhouenlai.info/人民日报（1946-2003）/1954/05/1954-05-31.htm', note: '名单明确将《快乐的节日》列为二等奖，署名管桦词、李群曲；同一名单中还列出《早操歌》（管桦词、瞿希贤曲）等作品。（批次 21 · L35）', kind: 'archive', batch: '21' },
  { id: '21-06', title: '快乐的节日', version: '版本见原档案', platform: 'www.csmes.org', url: 'https://www.csmes.org/show-9-145968.html', note: '报道称《快乐的节日》创作于1953年春，管桦词、李群曲，专为“六一”儿童节创作，经中央人民广播电台少儿合唱团演唱播放后迅速流传，并在1954年评奖获奖。此来源为音乐教育机构网站报道，适合补充传播史，但原始广播节目单/录音仍需另查。（批次 21 · L38）', kind: 'archive', batch: '21' },
  { id: '21-09', title: '让我们荡起双桨', version: '版本见原档案', platform: '百度', url: 'https://bkso.baidu.com/item/让我们荡起双桨/3063579', note: '该页面为百科性质，需进一步用电影片头/片尾字幕、电影原声资料或中国电影资料馆目录独立确认领唱者和演唱团体。（批次 21 · L56）', kind: 'archive', batch: '21' },
  { id: '21-11', title: '我们的田野', version: '版本见原档案', platform: '中国作家网', url: 'https://www.chinawriter.com.cn/n1/2024/1017/c418956-40341356.html', note: '作者回忆，最早听到的童声合唱来自中央人民广播电台“小喇叭”节目；文章还称“据说”最早原唱者为张金利，1953年曾示唱。（批次 21 · L65）', kind: 'archive', batch: '21' },
  { id: '21-12', title: '卖报歌', version: '版本见原档案', platform: '中国作家网', url: 'https://www.chinawriter.com.cn/n1/2020/0813/c404063-31820380.html', note: '文章记述聂耳邀请安娥写词，聂耳谱曲，并根据卖报女孩“小毛头”的建议修改歌词中的具体句子；文章称“小毛头”成为歌曲首唱者。（批次 21 · L75）另见批次 23 交叉引用。', kind: 'archive', batch: '21' },
  { id: '21-13', title: '卖报歌', version: '版本见原档案', platform: '中国新闻网', url: 'https://www.chinanews.com/cul/2013/02-22/4586801.shtml', note: '该文补充了1933年秋创作过程的叙述，但属于传记内容的新闻转述，建议后续与《聂耳日记》、安娥传记正式版本及聂耳作品年表交叉核验。（批次 21 · L78）另见批次 23 交叉引用。', kind: 'archive', batch: '21' },
  { id: '21-14', title: '卖报歌', version: '版本见原档案', platform: '中国知网', url: 'https://yyxy.cbpt.cnki.net/portal/journal/portal/client/paper/583ca80f5d7d0331648e12455b1b05b2', note: '论文摘要将《卖报歌》列为聂耳1934年创作、安娥作词的儿童歌曲之一，可作为学术论文线索。（批次 21 · L81）另见批次 23 交叉引用。', kind: 'archive', batch: '21' },
  { id: '21-15', title: '听妈妈讲那过去的事情', version: '版本见原档案', platform: '中国交响乐团', url: 'https://www.cnso.com.cn/zgjxyt/ycrc/201906/1e4188f6a5754727b43da79672754195.shtml', note: '页面列明2019年6月22日中国交响乐团合唱团演出《听妈妈讲那过去的事情》，管桦词、瞿希贤曲，并列出女声合唱、领唱人员。（批次 21 · L89）另见批次 22、23 交叉引用。', kind: 'archive', batch: '21' },

  // 批次 22：按 docs/research/ 原文登记的外部来源线索；档案/曲谱/史料类不是可播放音频。
  { id: '22-01', title: '小燕子', version: '版本见原档案', platform: '中国曲谱网', url: 'https://www.qupu123.com/shaoer/sanzi/p433.html', note: '页面标注：王路、王云阶词，王云阶曲；电影《护士日记》插曲。（批次 22 · L11）', kind: 'archive', batch: '22' },
  { id: '22-02', title: '小燕子', version: '版本见原档案', platform: '中国曲谱网', url: 'https://qupu123.com/Mobile-view-id-250309.html', note: '页面标注王路、王云阶词，王云阶曲；属于网友推荐/整理资料，不能视为原版出版谱。（批次 22 · L15）', kind: 'archive', batch: '22' },
  { id: '22-03', title: '小燕子', version: '版本见原档案', platform: '中国曲谱网', url: 'https://www.qupu123.com/Mobile-view-id-104733.html', note: '结合批次21湖北档案馆、王丹凤访谈及新华社资料，可以确认王丹凤与电影演唱版本的关联；但当前尚未找到可独立访问、来源可靠的电影原始音轨文件。（批次 22 · L19）', kind: 'archive', batch: '22' },
  { id: '22-04', title: '我们的田野', version: '版本见原档案', platform: '中国曲谱网', url: 'https://www.qupu123.com/shaoer/wuzi/p35668.html', note: '标注管桦词、张文纲曲。（批次 22 · L26）', kind: 'archive', batch: '22' },
  { id: '22-05', title: '我们的田野', version: '版本见原档案', platform: '中国曲谱网', url: 'https://www.qupu123.com/shaoer/wuzi/p10431.html', note: '线简谱混排版本：（批次 22 · L30）', kind: 'archive', batch: '22' },
  { id: '22-06', title: '我们的田野', version: '版本见原档案', platform: '中国曲谱网', url: 'https://www.qupu123.com/Mobile-view-id-222033.html', note: '页面说明选自金声编著《云南民族器乐葫芦丝·巴乌简明演奏法》，属于器乐改编/教学谱线索，不应当作原始合唱谱。（批次 22 · L31）', kind: 'archive', batch: '22' },
  { id: '22-07', title: '我们的田野', version: '版本见原档案', platform: '清华大学', url: 'https://music.lib.tsinghua.edu.cn/index.php?a=show&c=index&catid=24&id=1419&m=content', note: '目录元数据：中新音像出版社，2001年，1CD；ISRC：CN-A68-01-411-00/A·J6。（批次 22 · L35）', kind: 'archive', batch: '22' },
  { id: '22-08', title: '我们的田野', version: '版本见原档案', platform: '清华大学', url: 'https://music.lib.tsinghua.edu.cn/index.php?a=show&c=index&catid=24&id=1413&m=content', note: '曲目01《我们的田野》，演唱团体黑鸭子，时长03:52。（批次 22 · L39）', kind: 'archive', batch: '22' },
  { id: '22-09', title: '听妈妈讲那过去的事情', version: '版本见原档案', platform: '清华大学', url: 'https://music.lib.tsinghua.edu.cn/index.php?a=show&c=index&catid=24&id=2227&m=content', note: '曲目07《听妈妈讲那过去的故事》，时长04:21。（批次 22 · L50）', kind: 'archive', batch: '22' },
  { id: '22-11', title: '让我们荡起双桨', version: '版本见原档案', platform: '中国曲谱网', url: 'https://www.qupu123.com/shaoer/qizi/p206089.html', note: '标注乔羽词、刘炽曲、童道锦配伴奏。（批次 22 · L62）', kind: 'archive', batch: '22' },
  { id: '22-12', title: '让我们荡起双桨', version: '版本见原档案', platform: 'YouTube', url: 'https://www.youtube.com/watch?v=1ThcRM56bjE', note: '两个目录显示时长差异明显，可能是演唱、编配或剪辑版本不同；需试听比对，不能直接判定哪一个更接近1955年电影原声。（批次 22 · L73）', kind: 'video', batch: '22' },

  // 批次 23：按 docs/research/ 原文登记的外部来源线索；档案/曲谱/史料类不是可播放音频。
  { id: '23-02', title: '快乐的节日', version: '版本见原档案', platform: 'oddownload.nuduseng.com', url: 'https://oddownload.nuduseng.com/16%E8%80%81%E5%85%89%E7%9B%98%E7%BE%A4%28%E7%BE%A4%E5%8F%B7854318908%29%E7%BE%A4%E5%8F%8B%E5%88%86%E4%BA%AB%E6%B1%87%E6%80%BB%202020%E5%B9%B42%E6%9C%88/2020-02-24/%E7%8B%AC%E9%92%93%E5%AF%92%E6%B1%9F/%E4%B9%89%E5%8A%A1%E6%95%99%E8%82%B2%E6%95%99%E7%A7%91%E4%B9%A6%C2%B7%E9%9F%B3%E4%B9%90%EF%BC%88%E4%B8%80%E5%B9%B4%E7%BA%A7%E8%B5%B7%E7%82%B9%EF%BC%89/%E9%9F%B3%E4%B9%904%E5%B9%B4%E7%BA%A7%E4%B8%8B%E5%86%8C.pdf', note: '一份小学音乐教材PDF检索结果展示了《快乐的节日》简谱，调号/速度标记为1=F、2/4；但该PDF来源为非出版社官方镜像，暂作为谱面比对线索，不作为正式出版授权来源：（批次 23 · L18）', kind: 'archive', batch: '23' },
  { id: '23-03', title: '听妈妈讲那过去的事情', version: '版本见原档案', platform: '中国曲谱网', url: 'https://www.qupu123.com/shaoer/jiuziyishang/p250218.html', note: '页面标注管桦词、瞿希贤曲，上传日期2016-06-22。（批次 23 · L29）', kind: 'archive', batch: '23' },
  { id: '23-04', title: '听妈妈讲那过去的事情', version: '版本见原档案', platform: '中国曲谱网', url: 'https://qupu123.com/shaoer/jiuziyishang/p1206.html', note: '页面介绍作品发表于1958年《儿童音乐》创刊号；此项出版史信息需继续寻找原刊实物或图书馆目录核实。（批次 23 · L32）', kind: 'archive', batch: '23' },
  { id: '23-05', title: '听妈妈讲那过去的事情', version: '版本见原档案', platform: '中国曲谱网', url: 'https://qupu123.com/hechang/jiuziyishang/p50354.html', note: '页面标注管桦词、瞿希贤曲，童声合唱、笛子助奏，上传日期2012-06-21。（批次 23 · L35）', kind: 'archive', batch: '23' },
  { id: '23-07', title: '听妈妈讲那过去的事情', version: '版本见原档案', platform: '中国曲谱网', url: 'https://www.qupu123.com/jipu/p308777.html', note: '页面标注朱逢博演唱，管桦词、瞿希贤曲，PDF谱面入口。（批次 23 · L44）', kind: 'archive', batch: '23' },
]

export function sampleForAudioLink(link: AudioLinkRecord): ResearchSample | undefined {
  return researchSamples.find((sample) => sample.workTitle === link.title)
}

export function audioLinksForWork(workId: string): AudioLinkRecord[] {
  const work = specialtyCatalog.find((item) => item.id === workId)
  if (!work) return []
  return audioSourceLinks.filter((link) => link.title === work.title)
}

export function audioLinkKindLabel(kind: AudioLinkKind): string {
  return audioLinkKinds.find((item) => item.value === kind)?.label ?? '外部入口'
}
