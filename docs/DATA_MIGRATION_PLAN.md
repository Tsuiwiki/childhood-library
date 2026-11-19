# 历史数据迁移方案 · DATA_MIGRATION_PLAN

- 文档状态：Design Proposal
- 版本：v0.1
- 日期：2026-11-19
- 依据：[PROJECT_AUDIT.md §3–§4](PROJECT_AUDIT.md)、[DATABASE_DESIGN.md §7](DATABASE_DESIGN.md)、[MUSIC_LIBRARY_IMPLEMENTATION_PLAN.md §2、§9](MUSIC_LIBRARY_IMPLEMENTATION_PLAN.md)
- 前提：**不删除原始数据、不覆盖历史 JSON、不清空数据库；保留回滚能力**

---

## 1. 迁移前门禁

| # | 检查 | 状态 |
|---|---|---|
| 1 | Git 分支与工作区状态 | 已核对：同步到 `e0a883f`，工作区干净 |
| 2 | 完整备份（含 `.git` 与被忽略媒体） | 已完成：844 文件 / 190,547,373 字节，仓库外备份 |
| 3 | 未提交 / 被忽略文件清点 | 已清点：85 个本地音频、23 个孤儿文件、3 条缺 `sampleType` |
| 4 | 历史 JSON / HTML / Python / 图片 / 媒体文件清单 | 见 [asset-inventory.md](reports/asset-inventory.md) |
| 5 | 记录数据数量与文件清单 | 见 §2 |
| 6 | 形成数据迁移映射 | 见 §3 |
| 7 | 导入后数量 / 关联 / 完整性校验方案 | 见 §5 |

**未满足的门禁**：第二、三卷完整目录来源（决定 500 首缺口能否补齐）、本地 85 个媒体是否迁入 VM。这两项不影响元数据迁移，但影响完整目录导入，须在 T-11 前确认。

## 2. 源数据清单与数量基线

| 源 | 规模 | 位置 | 说明 |
|---|---|---|---|
| 作品发现目录 | 105 条（CN 55 / EN 50） | `design-demos/specialties.json` | 八专题映射 |
| 中国音乐资料卡 | 55 条 | `design-demos/china-materials.json` | 来源线索、歌词、谱面 |
| 世界经典资料卡 | 47 条 | `design-demos/world-materials.json` | 35 条已核验歌词 + 12 条已定性结论；47 条音频待采集 |
| 歌词来源底稿 | 47 条 | `design-demos/world-lyrics-sources.json` | 逐曲来源与公版判定 |
| 试听配置 | 58 条 / 63 版本 / 62 唯一文件名 | `design-demos/audio/samples.json` | 26 internal / 21 generated / 8 open / 3 无类型 |
| 官方预览 | 5 条 | `design-demos/audio/official-recordings.json` | Deezer 30 秒预览 |
| 内部研究采集 | 27 文件 / 28 映射 | `design-demos/audio/public-recording-collection.json` | 权利待核验 |
| 故事 / 诗词内容 | 160 条 | `design-demos/library-content.json` | Phase 5 再迁移 |
| 500 首研究目录 | 219 已编号 / 500 目标 | `docs/CHINESE_CHILDRENS_SONGS_500_CATALOG.md` | Markdown 表格，V2/V3 缺 |
| 首批采集候选 | 100 条 ID | `docs/CLASSIC_SONGS_CATALOG.md` | 中国 50 + 英文 50 |
| 乐谱与素材 | MusicXML 14、SVG 119、PNG 161 | `design-demos/song-assets/` 等 | 需逐项关联作品与权利 |
| 本地音频 | 85 个 | `design-demos/audio/`（被忽略） | 62 引用零缺失、23 孤儿 |

## 3. 字段映射

| 源字段 / 结构 | 目标实体 | 映射规则 | 禁止事项 |
|---|---|---|---|
| `specialties.json[].id/title/tags` | `Work` + `CollectionMembership` + `ExternalIdentifier` | 原 ID 存为外部标识，生成稳定 `work_id` | 不把原 ID 当主键 |
| `china-materials[].lyrics/score/cover` | `WorkVersion` / `ScoreEdition` / `MediaAsset` | 歌词挂版本，封面挂资产，谱面单独版本 | 不把歌词塞进 Work |
| `world-materials[].lyrics=[]` + `lyricsVerdict` | `WorkVersion.lyrics_status=no_lyric_applicable` + `verdict_note` | 保留已定性结论与来源 | 不回填推测歌词、不标「待采集」 |
| `samples[].file` / `variants[].file` | `RecordingVersion` + `MediaAsset` + `PlaybackResource` | 按五类资源分型：internal_local / open_license_sample / original_demo / official_preview / licensed_hosted | 不把文件路径当播放 URL |
| `samples[].sampleType` 缺失 3 条 | 补齐 `resource_type` | 迁移前修正 `EN-T01`～`EN-T03` | 不猜测类型 |
| `official-recordings[].trackId` | `PlaybackResource(official_preview)` | 保留 provider、曲目 ID、原站 URL、条款核验日期 | 不持久化预览 URL |
| `public-recording-collection[].records` | `MediaAsset` 候选 | 保留来源页、原始地址、采集时间、SHA-256 | 不因有文件元数据就视为已授权 |
| `CHINESE_CHILDRENS_SONGS_500_CATALOG.md` 表格 | 中间层 CSV/JSON → `Work` + `SourceRecord` | `V1-xxx/V4-xxx` → `ExternalIdentifier(namespace=century_vol1/vol4)`；`catalog_status=bibliography_candidate`；`SourceRecord` 指向卷次目录页 | 不把 `bibliography_verified` 提升为 `metadata_verified` / `core_selected`；不虚构 V2/V3 曲目 |
| `CLASSIC_SONGS_CATALOG.md` 100 条 | `Work` 候选 | 与 100 首精选区分，保留 `candidate` 状态 | 不自动标为精品或已授权 |
| MusicXML / SVG | `ScoreEdition` + `MediaAsset(derived_from_asset_id)` | MusicXML 为源，SVG 为派生渲染 | 不把 SVG 当唯一原始谱面 |
| `library-content.json` | 故事馆 / 诗词馆 | Phase 5 复用通用实体 | 本阶段不迁移 |

## 4. 迁移步骤

1. **Schema 定稿**：以 [DATABASE_DESIGN.md](DATABASE_DESIGN.md) 建表与约束，Alembic 迁移可 upgrade / downgrade 往返。
2. **中间层生成**：把 500 首 Markdown 表格、100 条候选、各类 JSON 转为带 `import_batch_id` 的统一中间 JSON；所有转换只读源文件。
3. **ID 与去重**：建立 `ExternalIdentifier` 映射；按「标准名 + 别名 + 类型 + 语言 + 地域」做重复候选检测，**人工确认后才合并**；同名异文保留为不同 `WorkVersion`。
4. **分批导入**：每批 25–50 首或按数据集分批，事务提交，记录新增 / 更新 / 跳过 / 冲突 / 失败。
5. **媒体登记**：逐文件计算 SHA-256、大小、mime、时长；孤儿文件单列，不自动删除；权利待核验的 `internal` 只写研究层。
6. **校验与报告**：按 §5 输出迁移报告；与源数量逐项对比。
7. **回滚准备**：保留 `import_batch_id`、原始文件与导入日志；原型目录全程只读。

## 5. 完整性校验方案

| 类别 | 校验项 | 期望 |
|---|---|---|
| 数量 | 作品 105、中国资料卡 55、世界资料卡 47、试听 58 / 63 / 62、官方预览 5、500 首已编号 219 | 导入前后一致 |
| 关联 | 每条 `MediaAsset` 可回溯作品 / 版本 / 来源 / 权利记录 | 孤儿关联数为 0 或全部登记 |
| 媒体 | 62 个引用零缺失；85 个文件 checksum 与清单一致；23 个孤儿单列 | 无静默丢失 |
| 类型 | 3 条缺 `sampleType` 已修正；五类资源互斥 | 无「未分类」进入公开层 |
| 歌词 | 35 条已核验、12 条 `no_lyric_applicable`；无推测歌词 | 状态与来源一致 |
| 权利 | 27 个 internal 保持「待核验」；47 条世界经典音频保持「待采集」 | 无自动提升 |
| 发布 | `publication_status=published` 的记录全部满足发布门禁 | 门禁违规数 0 |
| 500 首 | 219 条仍为 `bibliography_candidate`，第二、三卷不伪造 | 数量不缩减、不虚报 |

## 6. 缺失媒体与研究目录缺口处理

- **GitHub 无媒体是既定合规口径**：`.gitignore` 排除全部二进制；公开仓库只托管 JSON 清单，不因迁移而改变。
- **本地 85 个媒体**：是否迁入 VM 需单独确认；迁入时只登记元数据与 checksum，权利状态逐项核验，不自动开放播放。
- **23 个孤儿文件**：在迁移报告中单列，人工判断归档或淘汰，不自动删除。
- **47 条世界经典音频待采集**：保持 `待采集`，不硬配程序合成音冒充原曲。
- **500 首第二、三卷缺口**：取得合法完整目录前不推测标题、不用搜索片段拼「完整 500 首」[CHINESE_CHILDRENS_SONGS_500_CATALOG.md L271]。

## 7. 迁移报告内容

每批输出：批次 ID、时间、源数据集、记录数（新增/更新/跳过/冲突/失败）、ID 映射表、重复候选清单、缺失与孤儿媒体清单、权利状态分布、发布门禁违规数、校验断言结果、回滚命令。

## 8. 回滚

| 层级 | 方式 |
|---|---|
| 数据库 | 按 `import_batch_id` 删除该批记录；迁移用 Alembic downgrade |
| 媒体 | 只增不删；孤儿文件保留 |
| 源文件 | 全程只读，不改写一个历史 JSON / HTML / Markdown |
| 原型 | `design-demos/` 只读保留，直到新系统验收通过 |
| 兜底 | 新系统可整体停用，回退到静态页面与仓库外完整备份 |

## 9. 待确认

- 第二、三卷完整目录来源（纸本 / 合法电子书 / 出版社目录）。
- 本地 85 个媒体与 27 个 `internal` 录音是否迁入 VM。
- 导入工具与批次大小、重复候选的人工确认流程。
