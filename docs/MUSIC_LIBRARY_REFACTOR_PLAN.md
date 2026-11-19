# 儿童音乐馆重构计划 · MUSIC_LIBRARY_REFACTOR_PLAN

- 文档状态：Design Proposal
- 版本：v0.1
- 日期：2026-11-19
- 上位文档：[MUSIC_LIBRARY_MASTER_PLAN.md](MUSIC_LIBRARY_MASTER_PLAN.md)（口径与内容标准）、[MUSIC_LIBRARY_IMPLEMENTATION_PLAN.md](MUSIC_LIBRARY_IMPLEMENTATION_PLAN.md)（工程实施基准）
- 范围：音乐馆作为第一个完整业务模块；故事馆 / 诗词馆复用底层设施，本阶段不实现

> 原则：**先建立可长期演进的工程基础，不快速堆功能**；保留现有原型中值得使用的视觉与交互，不因技术重构全部推翻。

---

## 1. 目标与边界

**目标**：实现一条从「后台建档」到「前台合规展示/试听」的完整闭环，验证统一模型、权利门禁与媒体服务确实可用，再扩展到批量管理与其它内容馆。

**不是**：在线音乐播放器、全量自动采集、把 500 首目录全塞进前台、三馆各建一套互不兼容系统 [MUSIC_LIBRARY_IMPLEMENTATION_PLAN.md L375]。

## 2. MVP 闭环（9 步）

| # | 环节 | 落地实体 | 验收要点 |
|---|---|---|---|
| 1 | 后台创建音乐作品 | `Work` + `ExternalIdentifier` | 稳定 `work_id`；同名异文不强制合并 |
| 2 | 管理创作者与贡献关系 | `Person` + `Contribution` | 词/曲/译配/改编/编曲/采录/演唱多角色；未知留「待考」 |
| 3 | 录入作品版本及录音版本 | `WorkVersion` + `RecordingVersion` | 一首作品可挂多个版本；现代改编不冒充历史首版 |
| 4 | 添加来源和证据 | `SourceRecord` | `evidence_scope` 指明支持哪项事实；URL 不当权利证明 |
| 5 | 记录媒体资源及权利状态 | `MediaAsset` + `StorageLocation` + `RightsRecord` | SHA-256 / 大小 / 格式 / 时长；分对象权利 |
| 6 | 进行内容审核 | `EditorialReview` | 针对**具体录音版本**评审美与适龄性 |
| 7 | 发布条件检查 | 发布门禁 | 五维状态独立；未通过门禁的媒体不进公开层 |
| 8 | 前台查询作品和详情 | 公开 API + Vue 页面 | 前后台读同一套数据，不维护两份目录 |
| 9 | 合规资源试听 | `PlaybackResource` | 仅展示通过审核的外链 / 官方预览 / 授权站内播放 |

## 3. 领域模型

十类实体（`Work`、`Contribution`、`WorkVersion`、`RecordingVersion`、`ScoreEdition`、`SourceRecord`、`MediaAsset`、`PlaybackResource`、`RightsRecord`、`EditorialReview`）的主键、唯一性、关系、状态流转与校验规则见 [DATABASE_DESIGN.md](DATABASE_DESIGN.md)。

关键设计判断：

- **不能把 JSON 字段平移进表**。`samples.json` 的 `file` 字段要拆成 `RecordingVersion` + `MediaAsset` + `PlaybackResource`；`lyrics` 要挂到 `WorkVersion` 而非 `Work`。
- **`lyrics_status=no_lyric_applicable` 是一等状态**：现有 47 条世界经典资料卡中 12 条经核验为「本条不适用单曲歌词」，不能回填推测歌词，也不能笼统标「待采集」。
- **三个支柱 / 七个专题是分类维度**，用 `pillar` + `Tag` / `Collection` 表达，不建成三张表 [DATA_MODEL.md L44-L66]。
- **研究层与使用层分离**：版权未知的候选可进研究目录，公开播放按具体作品、版本、媒体与用途审核 [PROJECT_PRINCIPLES.md]。

## 4. 管理能力（分阶段）

| 阶段 | 能力 |
|---|---|
| MVP | 作品 CRUD、贡献角色、作品/录音/乐谱版本、来源证据、媒体元数据、权利记录、审美评审、发布门禁、操作审计 |
| 扩展 | 标签/分类/主题集合、批量导入导出、重复作品识别、数据完整性检查、来源 Adapter 与任务日志 |
| 后续 | AI 辅助分类与查重（只给建议）、收藏与个人使用体验 |

批量导入与去重规则见 [DATA_MIGRATION_PLAN.md](DATA_MIGRATION_PLAN.md)；任务编号与验收见 [IMPLEMENTATION_ROADMAP.md](IMPLEMENTATION_ROADMAP.md)。

## 5. 前台能力

| 页面 / 能力 | 说明 | 复用原型 |
|---|---|---|
| 音乐馆首页 | 三大支柱入口、专题、今日推荐 | `design-demos/music.html` 信息架构与视觉 |
| 作品分类与主题集合 | 中国经典七专题、世界经典、年龄与场景 | `music.html` / `specialty-*.html` |
| 作品搜索与筛选 | 标题、别名、专题、年代、语言 | `design-demos/works.html` 交互 |
| 作品详情 | 作品档案、历史背景、来源与编辑评审 | `works.html` 详情面板 |
| 创作者信息 | 贡献角色与作品反查 | 新增 |
| 不同录音版本 | 版本切换、表演者、年代、版本说明 | `works.html` 多版本选择器 |
| 乐谱与相关资料 | 简谱 / 五线谱 / MusicXML / SVG、歌词 | `song-assets/` 与资料卡 |
| 合规音频试听 | 仅对通过门禁的资源显示入口 | `works.html` 播放逻辑 + 官方预览实验 |

**保留要求**：静态原型在新系统验收前全部只读保留；前端组件化时抽取既有配色、卡片、筛选、详情与移动端交互，不重做视觉方向 [MUSIC_LIBRARY_IMPLEMENTATION_PLAN.md L26-L34]。

## 6. 媒体资源管理

- 独立 `Media Asset Service` + `StorageProvider` 接口（`put/get/stat/delete/range`），第一阶段只实现 `local` 适配器 [MEDIA_ASSET_DESIGN.md](MEDIA_ASSET_DESIGN.md)。
- 元数据：文件大小、格式、时长、SHA-256、存储位置、来源、与作品/录音版本的关联、播放资源状态、备份与迁移记录。
- **权利门禁**：内部研究收录不等于公开播放、下载或分发授权；27 个 `internal` 录音只登记在研究层；47 条世界经典音频仍标「真实录音待采集」，不硬配合成音冒充原曲。
- 预留授权访问、Range 播放、校验和备份迁移；不在本阶段购买 COS / BOS 资源。

## 7. 统一支撑故事馆与诗词馆

复用：通用作品、贡献关系、分类标签、来源证据、媒体资产、审核与发布机制、搜索能力。独立：故事馆的插图/朗读者/文本版本，诗词馆的时代/体裁/校勘/注释/译文。

**边界**：音乐馆验证通过后才抽象公共层，不提前为三馆设计过度通用的抽象 [MUSIC_LIBRARY_IMPLEMENTATION_PLAN.md L373]。

## 8. 验收标准

1. 编辑可从一条候选歌曲完成「身份 → 贡献 → 版本 → 来源 → 媒体 → 权利 → 评审 → 发布」全流程，且全流程可追溯。
2. 未通过发布门禁的媒体**不会**被公开接口返回，前台不渲染播放入口。
3. 前台与后台读取同一套数据；改变后台状态后前台同步变化。
4. 一首作品可关联多个创作者、多个演唱版本、多个乐谱版本与多个来源，原始证据不丢失。
5. 具备合法播放条件的资源可试听；官方短时预览点击触发、不缓存、不持久化 URL。
6. 现有静态原型仍可独立打开，7 个 `validate_*.py` 回归通过。
7. 备份与恢复演练在 testing 环境通过。

## 9. 风险与回滚

| 风险 | 应对 |
|---|---|
| 误把研究候选标为已授权 | 导入脚本硬断言状态；发布门禁集成测试 |
| 覆盖或删除历史原型 | 原型目录只读保留，新工程放独立目录 |
| 双份目录漂移 | 公开页与编辑端共用 API；回归断言数量一致 |
| 未授权媒体被播放 | 服务端二次校验 + feature flag 一键下线播放入口 |
| 500 首目录被误当成可发布内容 | `catalog_status=bibliography_candidate`，导入断言不提升状态 |
| VM 共享机端口/容器冲突 | 独立 project name / volume / 端口段，启用前复核 `ss -lntp` |
