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
