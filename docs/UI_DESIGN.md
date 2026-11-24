# 童年书房前端界面设计与页面关联说明

> **状态**：2026-11-22，与 `/works` 内容卡统一同批提交到 `main`。本文是**现状说明书 + 问题清单**，不是设计方案提案，也不改变任何录音的权利状态。
>
> **阅读约定**：`[简称] L48` = 证据清单中该文件第 48 行；范围写 `[简称] L2130-L2135`。所有结论都附出处，便于独立复核。
>
> **边界**：`design-demos/` 原型只读；Vue 页面是内部研究前端，业务表仍为空、7 个业务域清单接口仍为 `501 NOT_IMPLEMENTED`；本文不把研究收录描述为公开发布授权。

---

## 0. 适用范围

本文覆盖 `web/`（Vue 3 + TypeScript + Vite）的**界面设计契约、组件规范、页面关联、数字口径、权利说明分层**，以及当前**仍然存在的设计与关联问题**（§8）。不涉及后端 API 实现、数据库导入或音频采集流程；相关背景见 [DEVELOPMENT_STATUS.md](DEVELOPMENT_STATUS.md) 与 [PRD.md](PRD.md)。

产品级原则见 [PROJECT_PRINCIPLES.md](PROJECT_PRINCIPLES.md)，权利口径见 [COPYRIGHT_POLICY.md](COPYRIGHT_POLICY.md)。工程命令与目录边界见 [../web/README.md](../web/README.md)。

---

## 1. 证据清单

| 简称 | 文件 | 行数 | 内容说明 |
| --- | --- | ---: | --- |
| `[router]` | `web/src/router/index.ts` | 69 | 路由表、页面标题、滚动行为 |
| `[app]` | `web/src/App.vue` | 100 | 全站导航、唯一 `<audio>` 挂载点、站点地图 |
| `[home]` | `web/src/views/HomeView.vue` | 192 | 内容首页：精选作品卡、计数、三馆入口、页尾折叠边界 |
| `[works]` | `web/src/views/WorksView.vue` | 249 | 录音列表：内容卡、筛选、分页、循环播放、详情弹窗 |
| `[music]` | `web/src/views/MusicView.vue` | 157 | 音乐馆：八专题、发现目录、研究档案折叠区 |
| `[catalog]` | `web/src/views/CatalogView.vue` | 233 | 百年儿歌目录：筛选、状态卡、原文行号链接 |
| `[sources]` | `web/src/views/AudioSourcesView.vue` | 152 | 音源链接：94 条外链、类型筛选、边界折叠区 |
| `[library]` | `web/src/views/LibraryIndexView.vue` | 238 | 跨馆资料总览与统一检索 |
| `[hall]` | `web/src/views/ResearchHallView.vue` | 191 | 故事馆 / 古诗词馆 |
| `[specialty]` | `web/src/views/SpecialtyView.vue` | 139 | 八个音乐专题子页 |
| `[player]` | `web/src/components/ClAudioPlayer.vue` | 251 | 底部播放器、播放列表状态 |
| `[detail]` | `web/src/components/ClTrackDetailDialog.vue` | 295 | 作品资料卡弹窗（版本、来源、权利集中处） |
| `[map]` | `web/src/components/ClLibraryMap.vue` | 79 | 页脚站点地图 |
| `[tokens]` | `web/src/styles/tokens.css` | 21 | 视觉 token（逐值复制自原型） |
| `[base]` | `web/src/styles/base.css` | 142 | 全局基础样式 |
| `[samples]` | `web/src/research/samples.ts` | 118 | 唯一读取 `samples.json` 的数据层 |
| `[audioLinks]` | `web/src/research/audioLinks.ts` | 165 | 外部音源元数据（94 条） |
| `[catalogData]` | `web/src/research/catalog.ts` | 281 | 219 条公开目录的唯一数据源 |
| `[documents]` | `web/src/research/documents.ts` | 151 | GitHub 研究文档导航元数据 |
| `[specialties]` | `web/src/research/specialties.ts` | 80 | 105 条音乐作品目录与专题映射 |
| `[libraryData]` | `web/src/research/library.ts` | 119 | 故事 / 诗词研究记录 |
| `[prototype]` | `design-demos/dir-3.html` | 1348 | 已确认的三馆首页原型（只读） |
| `[catalogDoc]` | `docs/CHINESE_CHILDRENS_SONGS_500_CATALOG.md` | — | 500 首研究目录，219 条数据的原文出处 |
| `[tests]` | `web/tests/*.spec.ts` | 13 个 spec 文件 | 71 个 Vitest 用例（另有 `audio-works-harness.ts` 夹具，不计入 spec） |

> ⚠️ 预览服务路由脚本 `cl_web_preview_server.py` 位于**仓库外**（本机 `_audit_main/`、VM `/data/cl-web-preview/`），不入库，因此无法从 GitHub 独立复核。本文涉及根路由的结论均标注为「部署态」，并在 §12 给出补充采集方式。

---

## 2. 设计原则

| # | 原则 | 落地方式 | 出处 |
| --- | --- | --- | --- |
| P1 | **内容优先** | 首屏只放能听 / 能翻的内容，权利与研究过程折叠，不占主叙事 | `[home] L122-L127`、`[works] L93-L95`、`[sources] L56-L59`、`[catalog] L84-L86`、`[music] L88-L90` |
| P2 | **真实录音优先** | 没有本地录音就如实标「待采集 / 仅目录」，不摆空播放按钮、不伪造时长与文件 | `[catalogData] L18-L21`、`[catalog] L133-L149`、`[sources] L55-L59` |
| P3 | **原型只读** | 视觉 token 逐值复制，原型文件不改写、仍可单独打开 | `[tokens] L1-L6`、`[prototype]` |
| P4 | **数据层唯一** | 每个 JSON 快照只允许一个 `research/*.ts` 读取，视图不直接导入 JSON | `[samples] L2`、`[specialties] L45`、`[libraryData] L60-L64`、`[audioLinks] L40`、`[catalogData] L30` |
| P5 | **全站唯一播放器** | `<audio>` 只在 `App.vue` 挂载一次，跨 Vue 路由切换不中断 | `[app] L70-L71`、`[player]` |
| P6 | **关联靠深链，不靠复制** | 作品用 ID / 标准题名串起来，不复制 Markdown 正文进页面 | `[home] L70`、`[library] L49-L73`、`[documents] L14` |

---

## 3. 视觉规范

### 3.1 色板与排版 token

| Token | 值 | 用途 | 出处 |
| --- | --- | --- | --- |
| `--paper` / `--paper-light` | `#f4eddc` / `#fffaf0` | 页面底 / 卡片底 | `[tokens] L8-L9` |
| `--ink` / `--ink-soft` | `#191917` / `#4a4841` | 正文 / 次要文字 | `[tokens] L10`、`L16` |
| `--red` / `--yellow` / `--blue` / `--green` | `#e64a38` / `#f1bd32` / `#2858b8` / `#739348` | 强调、按钮、专题、状态 | `[tokens] L11-L14` |
| `--line` / `--shadow` | `3px solid var(--ink)` / `7px 7px 0 var(--ink)` | 墨边、硬阴影 | `[tokens] L17-L18` |
| `--serif` / `--sans` | 思源宋体族 / 苹方雅黑族 | 标题 / 正文 | `[tokens] L19-L20` |

`[tokens] L2-L5` 明确记录取值来自 `design-demos/music.html L9-L15` 与 `works.html L9-L20`，原型是视觉基准。

### 3.2 内容卡契约（统一组件语言）

首页与录音页共用同一套内容卡字段，**卡片上不出现权利徽章、编号标签、来源 / 素材三行研究字段**。

| 区域 | 字段 | 首页 | 录音页 | 出处 |
| --- | --- | --- | --- | --- |
| 封面 | `materials.cover` SVG，4:3 | 点击深链 `/works?work=<ID>` | 点击打开详情弹窗 | `[home] L70-L72`、`[works] L130-L138` |
| 标题 | `workTitle` | ✅ | ✅ | `[home] L74`、`[works] L140` |
| 副标题 | `author \|\| kind` | ✅ | ✅ | `[home] L75`、`[works] L141` |
| 时长 | `durationLabel ?? '时长待核'` | ✅ | ✅ | `[home] L76`、`[works] L142` |
| 主操作 | 试听 → 全站播放器 | ✅ `RouterLink` 到详情 | ✅ 直接播放 | `[home] L78-L85`、`[works] L144-L152` |
| 次操作 | 看详情 | ✅ 深链 | ✅ 弹窗 | `[home] L86`、`[works] L153-L158` |
| 权利标签 | — | ❌ | ❌（本轮移除） | `[works] L130-L165` |

样式契约：封面 `aspect-ratio: 4/3` + `object-fit: cover`，卡片 `border: var(--line)` + `5px 5px 0` 硬阴影，操作区 `2px dashed` 分隔线，按钮最小高度 42px。出处 `[home] L152-L162`、`[works] L211-L223`。

> 本轮之前 `[works]` 旧卡片带 `.id-tag` / `.status-badge` / `.card-meta`（编号 + 「权利待核验」红标 + 录音 / 来源 / 素材三行），与首页不一致；现已统一，权利信息集中在详情弹窗与页首折叠区。

### 3.3 其它组件

| 组件 | 规范 | 出处 |
| --- | --- | --- |
| 底部播放器 | 全站唯一 `<audio>`；队列用启动时完整筛选结果快照；`ended` 触发下一首，末尾回首 | `[app] L70-L71`、`[player]` |
| 作品资料卡弹窗 | 版本切换、署名 / 许可、SHA-256、歌词谱面、专题与音源线索、来源与权利说明全部集中于此 | `[detail] L89-L168` |
| 筛选 / 分页 | 搜索框 + 分组按钮 + `role="status"` 计数；录音页 9 条/页、目录页与音源页 12 条/页 | `[works] L22`、`[catalog] L23`、`[sources] L17` |
| 折叠边界区 | `<details>` 默认收起，只在用户主动展开时说明来源 / 版本 / 权利 | `[home] L123`、`[works] L93`、`[sources] L56`、`[catalog] L84`、`[music] L88` |
| 站点地图 | 页脚列出四馆、目录、音源、录音、静态研究库入口 | `[map] L8-L12` |

### 3.4 响应式断点

| 断点 | 首页作品网格 | 录音页网格 | 出处 |
| --- | --- | --- | --- |
| 默认 | 4 列 | 3 列 | `[home] L151`、`[works] L210` |
| ≤1000 / ≤1100px | 2 列 | 2 列 | `[home] L183`、`[works] L241` |
| ≤640px | 1 列 | 1 列 | `[home] L189`、`[works] L244` |

---

## 4. 页面清单

| 路由 | 视图 | 主要数据源 | 主操作 | 出处 |
| --- | --- | --- | --- | --- |
| `/` | `HomeView` | `[samples]` `[audioLinks]` `[catalogData]` `[specialties]` | 试听、看详情、翻目录 | `[router] L28`、`[home] L45-L130` |
| `/works` | `WorksView` | `[samples]` | 试听、详情弹窗、循环播放 | `[router] L29`、`[works] L83-L172` |
| `/library` | `LibraryIndexView` | 四套数据层汇总 | 跨馆检索、跳转结果 | `[router] L30`、`[library] L34-L73` |
| `/music` | `MusicView` | `[specialties]` `[documents]` | 进专题、进目录、进音源 | `[router] L31`、`[music] L24-L26` |
| `/music/sources` | `AudioSourcesView` | `[audioLinks]` | 打开原站、回录音详情 | `[router] L32`、`[sources] L49-L91` |
| `/music/catalog` | `CatalogView` | `[catalogData]` | 按卷 / 状态筛选、看原文行号 | `[router] L33`、`[catalog] L76-L164` |
| `/music/specialties/:id` | `SpecialtyView` | `[specialties]` | 只看本专题录音 | `[router] L34`、`[specialty] L40` |
| `/story` `/poetry` | `ResearchHallView` | `[libraryData]` | 分组筛选、深链记录 | `[router] L35-L36`、`[hall] L65-L66` |
| 7 个业务域 | `DomainPlaceholderView` | 无（API 501） | 显示「尚未实现」 | `[router] L20-L25`、`L37` |
| 404 | `NotFoundView` | 无 | 返回首页 | `[router] L38` |

导航项定义 `[app] L18-L26`；页面标题映射 `[router] L41-L50`。

---

## 5. 页面关联矩阵

| 起点 | 触发元素 | 目标 | 参数 / 条件 | 出处 |
| --- | --- | --- | --- | --- |
| 首页 | 作品卡封面 | `/works` | `?work=<ID>` | `[home] L70` |
| 首页 | 「看详情」 | `/works` | `?work=<ID>` | `[home] L86` |
| 首页 | 试听按钮 | 全站播放器 | `toPlayerTrack(sample)` | `[home] L36-L38` |
| 首页 | 四个计数块 | 目录 / 录音 / 音源 / 资料总览 | 固定路由 | `[home] L23-L28` |
| 首页 | 三馆卡片 | `/music` `/story` `/poetry` | 固定路由 | `[home] L30-L34` |
| 音乐馆 | 主按钮 | `/works` `/music/catalog` `/music/sources` | 数量内嵌在按钮文案 | `[music] L24-L26` |
| 专题页 | 「只看本专题」 | `/works` | `?topic=<专题ID>` | `[specialty] L40` |
| 专题页 | 作品卡 | `/works` | 仅 `hasResearchAudio` 为真时可点 | `[specialty] L48-L58` |
| 目录页 | 「试听已有录音」 | `/works` | `?work=<ID>` | `[catalog] L139-L143` |
| 目录页 | 「查看音源线索」 | `/music/sources` | 查询参数 | `[catalog] L144-L148` |
| 目录页 | 「所属专题」 | `/music/specialties/:id` | 专题 ID | `[catalog] L150-L153` |
| 目录页 | 「目录原文 Lxx」 | GitHub 原文 | `#L<sourceLine>` | `[catalog] L155`、`[catalogData] L252-L253` |
| 音源页 | 「查看已有研究录音」 | `/works` | `?work=<ID>`，仅当 `sampleForAudioLink` 命中 | `[sources] L91`、`[audioLinks] L160` |
| 音源页 | 主按钮 | 外部原站 | `target="_blank" rel="noopener noreferrer"` | `[sources] L81-L101` |
| 跨馆检索 | 音乐作品结果 | `/works` 或专题页 | 有录音走详情，无录音走专题 | `[library] L49-L50` |
| 跨馆检索 | 目录结果 | `/music/catalog` | `?q=<作品名>` | `[library] L62` |
| 跨馆检索 | 故事 / 诗词结果 | `/story` `/poetry` | `?q=<记录ID>` | `[library] L73` |
| 三馆页 | 「研究资源库」 | `/research.html` | **静态页，离开 Vue** | `[hall] L66`、`L129` |
| 导航 | 「研究资源库」 | `/research.html` | `external: true` | `[app] L25` |
| 站点地图 | 研究资源库 | `/research.html` | 同上 | `[map] L12` |

**部署态补充**：预览服务把 `/` 与全部 Vue 路由指向 `web/dist/index.html`，把 `/dir-3.html` 等原型按原字节提供，`/music.html` `/works.html` 等旧入口 302 到 Vue 路由。该逻辑在仓库外脚本中（见 §12）。

---

## 6. 数字口径定义

首屏并列出现四个数字，**分母不同，不能相加，也不代表曲库总量**。

| 数字 | 含义 | 数据源 | 出处 |
| --- | --- | --- | --- |
| 219 | 《中国儿童歌曲百年经典》已核对公开目录（第一卷 139 + 第四卷 80） | `catalogEntries` | `[catalogData] L24-L27`、`L30-L250`、`L274-L280`；原文 `[catalogDoc]` |
| 58 | 主录音记录（有本地音频文件） | `design-demos/audio/samples.json` | `[samples] L2`；`[works] L91` |
| 94 | 外部音源 / 目录入口（批次 04–13） | `audioSourceLinks` | `[audioLinks] L40`、`[sources] L17-L18` |
| 105 | 音乐作品档案（候选资料卡） | `specialties.json` | `[specialties] L45`；`[home] L27` |
| 100 / 60 | 故事 / 诗词研究记录 | `library-content.json` | `[libraryData] L60-L64` |
| 8 | 首页「现在可以听」精选数量 | 硬编码 `featuredIds` | `[home] L13-L16` |
| 14 | 音源页中已关联本地录音的作品数 | `linkedRecordingCount` | `[sources] L18`、`L55` |
| 3 / 6 / 210 | 目录采集状态：有录音 / 有音源 / 仅目录 | `catalogAvailability` | `[catalogData] L268-L280`、`[catalog] L79-L82` |

---

## 7. 权利与来源说明的分层

| 层级 | 位置 | 默认可见 | 出处 |
| --- | --- | --- | --- |
| L1 内容层 | 卡片、首屏 | 不出现权利字样 | `[home] L69-L89`、`[works] L130-L165` |
| L2 页级边界 | 5 个页面各自的 `<details>` | 收起 | `[home] L123`、`[works] L93`、`[sources] L56`、`[catalog] L84`、`[music] L88` |
| L3 作品级 | 详情弹窗「来源、权利与采集状态」 | 主动打开才可见 | `[detail] L118-L168` |
| L4 播放器 | 底栏 `player-kicker` | 播放时常驻 | `[player] L154` |
| L5 独立静态页 | `/research.html` 五维状态与权利台账 | 离开 Vue | `[hall] L66`、`[map] L12` |

---

## 8. 已知问题：设计与关联仍有问题的地方

> 本节是「感觉页面设计和关联还是有问题」的逐条拆解。每条都给现象、证据、影响与建议，**不代替拍板**。

### P0（影响产品观感，建议优先）

| # | 现象 | 证据 | 影响 | 建议 |
| --- | --- | --- | --- | --- |
| 8.1 | **视觉语言仍有三套**：内容卡（首页 / 录音页）、研究台账卡（专题 / 三馆 / 跨馆结果）、表单式筛选卡 | `[home] L69-L89`、`[works] L130-L165` vs `[hall]`、`[specialty] L48-L58`、`[library] L124-L149`、`[works] L101-L128` | 像几个产品拼在一起，用户不确定哪套是「作品」 | 把内容卡契约（§3.2）推广到所有「作品 / 记录」结果卡，研究字段统一收进展开区 |
| 8.2 | **首页精选是硬编码 8 个 ID**，与 58 首录音、219 条目录没有生成规则或自动关联 | `[home] L13-L16` | 内容不随采集进度变化，容易被误读为「只有 8 首」 | 改为按「有录音 + 有封面 + 专题覆盖」自动生成，或明确标注「今日精选」并给「查看全部」 |
| 8.3 | **219 条目录里 210 首「仅目录」没有作品详情页**，只能跳 GitHub 原文行 | `[catalog] L133-L149`、`[catalogData] L268-L280` | 从目录到「作品」的链路断在半路，翻目录无法继续逛 | 为仅目录条目建统一作品占位页（展示题名、卷、年代、来源行号、待采集状态），再挂关联入口 |
| 8.4 | **三套作品编号并存**：`CN-Cxx`（录音）、`V1-xxx / V4-xxx`（目录）、`EN-Mxx`（世界经典），同一首歌在三个页面各自出现，没有统一作品 ID | `[samples] L2`、`[catalogData] L31-L250`、`[specialties] L45` | 关联靠「标准题名字符串相等」，改名 / 异体字就断链 | 建立作品主表与别名映射，所有关联改走 ID；当前字符串匹配见 `[audioLinks] L160`、`[catalogData] L256-L261` |
| 8.5 | **静态原型是孤岛**：`/research.html`、`/dir-3.html` 在 Vue 之外；导航「研究资源库」标 `external: true`，跳过去会离开 Vue 并中断连续播放 | `[app] L25`、`[map] L12`、`[hall] L66`、`L129`、`[library] L117`、`[prototype]` | 同一站点两套交互模型；原型卡片点击只开本地 dialog，不深链 Vue | 把研究状态看板迁入 Vue 路由，原型保留为只读归档入口；或在导航里明确标注「归档 / 新窗口」 |
| 8.6 | **权利说明分散在 5 个折叠区 + 播放器 kicker + 详情弹窗**，措辞不统一，且播放器播放时常驻「权利待核验」 | §7 表、`[player] L154` | 「权利下沉」只做了一半，播放时仍像被提醒 | 收敛到单一「来源与权利」页 + 详情弹窗，页级折叠文案统一，播放器只显示曲目信息 |
| 8.7 | **首屏四个数字并列、分母不同且无说明** | §6 表、`[home] L23-L28`、`[home] L57-L61` | 容易被读成「曲库只有 219 首 / 或 105 首」，与录音页「58 条」看起来矛盾 | 首屏只保留一个主口径，其余折叠成「内容构成」说明；每个数字加一句分母说明 |
| 8.8 | **94 条音源绝大多数只有原站链接**，没有反向关联到作品 / 目录条目 | `[sources] L81-L101`、`[audioLinks] L40-L158` | 从作品看不到「这个版本还有哪些线索」，从线索也回不到作品 | 给音源记录补作品 ID 字段，双向挂接（当前靠 `sampleForAudioLink` 题名匹配，`[audioLinks] L160`） |

### P1（体验细节）

| # | 现象 | 证据 | 建议 |
| --- | --- | --- | --- |
| 8.9 | 跨馆检索结果按数据种类分叉到 4 类目标，结果卡样式不统一 | `[library] L49`、`L62`、`L73`、`L149` | 结果卡统一为「标题 + 类型徽章 + 一句摘要 + 动作」 |
| 8.10 | 专题页无录音的作品卡渲染成不可点 `<article>`，只显示「候选 · 待核验」，用户不知道为何不能点 | `[specialty] L48-L58` | 给不可点卡片明确动作（看目录 / 看线索）而非静默禁用 |
| 8.11 | 网格密度不一致：首页 4 列、录音页 3 列每页 9 条、目录 / 音源 12 条 | `[home] L151`、`[works] L22`、`L210`、`[catalog] L23`、`[sources] L17` | 统一栅格与每页条数，或按内容类型显式说明差异 |
| 8.12 | 7 个业务域仍是 501 占位页，路由存在但导航不可达；未来接入时页面结构要重做 | `[router] L20-L25`、`L37` | 在本文补一章「正式业务页设计占位」，避免届时与内部研究页混用 |
| 8.13 | 音乐馆、录音页、资料总览各自有「研究档案 / 权利边界」入口，名称不同但指向相近 | `[music] L88-L90`、`[works] L93`、`[library] L117` | 合并命名与入口 |
| 8.14 | **新采集的研究批次不会自动进入页面关联**：远端批次 14《1970 年代历史唱片与〈金色年华〉逐曲入口》已合入 `docs/research/`，但 `[documents]` 导航只到批次 13、`[audioLinks]` 仍是 94 条，资料总览和音源页看不到这批线索 | `[documents] L119-L126`、`[audioLinks] L40`、`§12` | 每次 GitHub 新增采集文档后，页面内容会静默落后一拍，正是「关联没接上」的观感来源 | 建立「采集文档 → 导航元数据 / A 类音源」的核对清单，随每次 ff-only 同步一起跑；或先把批次 14 补入两个数据层 |

---

## 9. 改进路线（建议顺序，不含排期）

1. **先统一作品身份**：建作品主 ID 与别名映射，替换 `[audioLinks] L160`、`[catalogData] L256-L261` 的题名字符串匹配；这是 §8.3 / §8.4 / §8.8 的共同前置。
2. **再统一卡片语言**：把 §3.2 内容卡契约抽成共享组件，推广到专题、三馆、跨馆结果（§8.1 / §8.9 / §8.10）。
3. **补作品占位页**：让 210 首仅目录条目有可落地页（§8.3）。
4. **收拢权利说明**：单一入口 + 统一措辞，播放器改纯曲目信息（§8.6 / §8.13）。
5. **处理静态孤岛与首屏口径**：研究看板迁 Vue（§8.5）、数字口径加说明（§8.2 / §8.7）。
6. 每批完成后按 §10 验收，并回写本文对应行号。

---

## 10. 验收清单

| 项 | 命令 / 断言 | 期望 |
| --- | --- | --- |
| 类型与构建 | `npm run typecheck`、`npm run build` | 通过 |
| 单元测试 | `npm run test` | 全绿（当前 71 个用例，13 个 spec 文件） |
| 静态检查 | 仓库外 `verify_t08.py` / `verify_docs.py` | PASSED；本地链接 0 断、密钥候选 0 |
| 原型不变 | `design-demos/validate_prototypes.py` + 原型页 SHA-256 比对 | 3/3 PASS，逐字节一致 |
| 浏览器验收 | 首页 8 卡 / 8 试听 / 深链 `/works?work=CN-C01` / 真实播放 / 目录 219 首 19 页 / 音源 94 条 8 页 / 390px 无溢出 | PASS |
| 权利折叠 | 5 个 `<details>` 默认 `open === false` | PASS |
| 关联 | §5 每条深链可达且参数正确 | 逐条回归 |

> 仓库外脚本不在 GitHub 中；本地复核方式见 §12。

---

## 11. ⚠️ 待确认项

| 优先级 | 事项 | 为什么必须先确认 |
| --- | --- | --- |
| P0 | 内容卡是否推广到三馆 / 专题 / 跨馆结果（§8.1） | 决定要不要抽共享组件，影响 5 个视图与既有测试断言 |
| P0 | 是否引入统一作品主 ID（§8.4） | 决定关联实现是继续题名匹配还是改数据模型，影响 4 个数据层 |
| P0 | 静态原型是保留只读归档，还是迁入 Vue（§8.5） | 决定「研究资源库」导航形态与连续播放边界 |
| P1 | 权利说明是否收敛到单一页面（§8.6） | 涉及 `COPYRIGHT_POLICY.md` 口径与播放器文案，需法务/产品确认 |
| P1 | 首屏数字是否改成单一主口径（§8.7） | 涉及产品叙事，不宜由工程单方决定 |
| P1 | 171 预览服务是否从对外绑定恢复为仅回环 | 当前手机验收用的对外绑定仍生效，回环配置已保留 |

---

## 12. 本文未纳入的材料及原因

| 材料 | 原因 | 补充采集建议 |
| --- | --- | --- |
| `_audit_main/*.py` / `*.mjs`（本机）、`/data/cl-web-preview/server.py`（VM） | 仓库外验收与部署脚本，不入库，GitHub 读者无法复核 | 若要复核根路由，在 VM 执行 `curl -sS -o /dev/null -w '%{http_code}' http://127.0.0.1:58090/` 与 `ss -ltn \| grep 58090`，把输出附到交付记录 |
| `design-demos/audio/*` 音频、`web/dist/` 构建产物、`web/node_modules/` | 明确不入库 | 需要时用 VM 上 `var/media/` 的 SHA-256 清单比对 |
| `docs/research/` 23 份逐曲研究文档 | 是数据来源而非界面设计；导航元数据已在 `web/src/research/documents.ts` 与 `audioLinks.ts`（覆盖到批次 23） | 查具体版本线索时按文档导航的 GitHub 原文链接打开；批次 14–23 的音源/曲谱/史料线索见 `/music/sources` |
| `web/tests/` 逐条断言 | 本文只引用结论与文件清单 | 需要逐条证据时直接看对应 spec |
| 后端 `app/`、Compose 配置 | 与界面设计无关 | 见 `docs/ARCHITECTURE.md`、`deploy/README.md` |

---

**维护约定**：改动任一视图模板后，回写本文 §1 行数、§3 组件契约、§5 关联矩阵与 §10 期望值；行号失效比结论错误更容易误导复核者。
