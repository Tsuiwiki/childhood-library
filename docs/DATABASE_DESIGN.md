# 数据库设计 · DATABASE_DESIGN

- 文档状态：Design Proposal
- 版本：v0.1
- 日期：2026-11-19
- 范围：儿童音乐馆 MVP 的关系模型；故事馆 / 诗词馆复用通用层
- 依据：[DATA_MODEL.md](DATA_MODEL.md)（跨馆通用层）、[MUSIC_LIBRARY_IMPLEMENTATION_PLAN.md §3](MUSIC_LIBRARY_IMPLEMENTATION_PLAN.md)（音乐领域层）、[MUSIC_LIBRARY_V1.md L164-L168](MUSIC_LIBRARY_V1.md)（作品与录音版本分离）

> 本文是**概念级设计**，不含最终 DDL。目标不是把现有 JSON 字段平移进表，而是让「一首作品多个录音版本、一首传统童谣多个地区/语言/歌词版本、多个贡献角色、多种谱面、来源证据、审美评审、权利与发布」都成为可长期扩展的一等实体。

---

## 1. 建模原则

1. **作品 ≠ 版本 ≠ 媒体 ≠ 播放入口**：`Work` 是抽象作品，`WorkVersion` 是文本/创作版本，`RecordingVersion` 是具体演唱录音，`MediaAsset` 是文件，`PlaybackResource` 是可用的访问入口 [MUSIC_LIBRARY_V1.md L166]。
2. **权利分对象**：作品著作权、歌词文本、乐谱、编曲、表演者权、录音制作者权分别判断 [MUSIC_LIBRARY_V1.md L168]。
3. **来源不等于权利证明**：`SourceRecord` 记录证据，`RightsRecord` 记录许可，二者独立 [MUSIC_LIBRARY_IMPLEMENTATION_PLAN.md L124-L135]。
4. **状态五维独立**：`research_status` / `rights_status` / `quality_status` / `access_method` / `publication_status` 互不替代 [DATA_MODEL.md L68-L81]。
5. **ID 稳定**：所有业务主键使用 UUID 或不可变 `work_id` / `asset_id`，不依赖供应商 URL、文件路径或卷内序号 [MUSIC_LIBRARY_IMPLEMENTATION_PLAN.md L70、MEDIA_ASSET_DESIGN.md L125]。
6. **跨馆复用**：通用层（`works` / `contributions` / `tags` / `source_records` / `media_assets` / `editorial_reviews` / `rights_records`）三馆共享；音乐特有字段放领域表或 JSONB profile，不改通用表语义。

## 2. 实体关系

```text
Work ──< WorkTitle/Alias
  ├──< Contribution >── Person
  ├──< WorkVersion ──< ScoreEdition >── MediaAsset
  ├──< RecordingVersion ──< MediaAsset
  │        └──< PlaybackResource
  ├──< SourceRecord        (支持任意实体的某一项事实)
  ├──< RightsRecord        (按对象类型 + 对象 ID)
  ├──< EditorialReview     (按作品或具体版本)
  └──< CollectionMembership >── Collection

ExternalIdentifier ──> Work           (三套历史 ID 映射)
MediaAsset ──< StorageLocation        (local / COS / BOS，供应商中立)
```

## 3. 十类核心实体

### 3.1 Work（音乐作品）

| 项 | 设计 |
|---|---|
| 主键 | `work_id` UUID（对外另发不可变 `slug`） |
| 唯一性 | `UNIQUE(slug)`；`UNIQUE(canonical_title, work_type, language, region)` 仅作**候选去重提示**，不强制唯一（同名异文合法） |
| 关键字段 | `canonical_title`、`work_type`、`pillar`、`language`(BCP47)、`region`、`culture`、`created_at_range`、`first_published_at`、`summary`、`historical_context` |
| 状态 | `research_status`、`quality_status`、`publication_status`、`catalog_status` |
| 校验 | `work_type` 枚举；`pillar` 允许 `pending`；年代范围 `start <= end`；`publication_status=published` 时必须有通过的权利与评审记录 |
| 扩展 | 音乐特有字段放 `music_work_profile` 或 `metadata JSONB`，避免为故事/诗词加空列 |

### 3.2 Contribution（贡献关系）

| 项 | 设计 |
|---|---|
| 主键 | `contribution_id` |
| 外键 | `work_id`、`person_id` |
| 唯一性 | `UNIQUE(work_id, person_id, role, version_id NULL)`（同一人多角色合法，同一角色重复登记禁止） |
| 角色 | lyricist / composer / translator / adapter / arranger / collector / editor / performer / conductor / ensemble |
| 校验 | `role` 枚举；`confidence`（high/medium/low）与 `source_record_id`；未知作者留空并标「待考」，**不猜测补齐** |

配套 `Person`（`person_id`、`canonical_name`、`aliases`、`life_years`、`region`），支持同名人物消歧。

### 3.3 WorkVersion（作品文本 / 创作版本）

| 项 | 设计 |
|---|---|
| 主键 | `work_version_id` |
| 外键 | `work_id`、可选 `parent_version_id`（自引用，表达改编/校订链） |
| 唯一性 | `UNIQUE(work_id, version_label, language)` |
| 字段 | `version_label`、`version_type`（original / translation / adaptation / regional / editorial）、`language`、`region`、`lyrics_text`、`lyrics_status`（verified / no_lyric_applicable / pending）、`lyrics_source_id`、`notes` |
| 校验 | `lyrics_text` 非空时必须关联 `SourceRecord` 且记录逐行照录依据；`lyrics_status=no_lyric_applicable` 时必须有 `verdict_note`，**不得回填推测歌词** |
| 扩展 | 支持一首传统童谣多个地区、方言、语言与歌词版本并存 |

> 设计依据：歌词权利属于具体文本版本，不应只挂在 Work 上 [MUSIC_LIBRARY_IMPLEMENTATION_PLAN.md L97]。现有 47 条世界经典资料卡中 12 条已核验为「本条不适用单曲歌词」，需以 `lyrics_status=no_lyric_applicable` 表达，而不是留空待采集。

### 3.4 RecordingVersion（录音版本）

| 项 | 设计 |
|---|---|
| 主键 | `recording_version_id` |
| 外键 | `work_id`、可选 `work_version_id` |
| 唯一性 | `UNIQUE(work_id, performer_text, recording_year, label, version_label)`（业务唯一，允许 NULL 组合差异） |
| 字段 | 表演者 / 合唱团、录音与发行年份、专辑、厂牌、目录号、编曲者、配器、演唱形式、`version_note`（历史原唱 / 童声合唱 / 现代翻唱 / 纯音乐 / 动画版）、`source_record_id`、`primary_asset_id` |
| 校验 | 现代改编版不得标为历史首版；`primary_asset_id` 指向的 `MediaAsset` 必须存在且 `asset_role=recording` |
| 说明 | 作品相同不代表录音版本相同 [MUSIC_LIBRARY_IMPLEMENTATION_PLAN.md L111] |

### 3.5 ScoreEdition（乐谱版本）

| 项 | 设计 |
|---|---|
| 主键 | `score_edition_id` |
| 外键 | `work_id`、可选 `work_version_id` |
| 唯一性 | `UNIQUE(work_id, publisher, book_title, edition, page_start, score_type)` |
| 字段 | `score_type`（简谱 / 五线谱 / 钢琴伴奏谱 / 合唱谱 / MusicXML）、调性、拍号、声部、谱面完整性、出版社、ISBN、版次、页码、编配者、`source_record_id`、`rights_record_id` |
| 派生关系 | `MusicXML` 为可编辑源，`SVG` 为渲染结果；`MediaAsset` 记录 `derived_from_asset_id`，**不得把 SVG 当作唯一原始谱面** [MUSIC_LIBRARY_IMPLEMENTATION_PLAN.md L122] |
| 校验 | 无可考证旋律依据时禁止生成谱面；`rights_status` 必须逐版本登记 |

### 3.6 SourceRecord（来源与证据）

| 项 | 设计 |
|---|---|
| 主键 | `source_record_id` |
| 多态关联 | `supports_entity_type` + `supports_entity_id`（不使用跨表外键，改由应用层校验存在性） |
| 字段 | `source_type`、`platform`、`publisher`、`source_title`、`source_url`、`published_at`、`accessed_at`、`evidence_scope`（身份 / 作者 / 年代 / 版本 / 录音 / 谱面 / 权利）、`evidence_note`、`confidence`、`verification_status` |
| 唯一性 | `UNIQUE(source_url, supports_entity_type, supports_entity_id, evidence_scope)` |
| 校验 | URL 不是权利证明；`verification_status=checked` 必须记录 `checked_by` / `checked_at` |

### 3.7 MediaAsset（媒体资源）

| 项 | 设计 |
|---|---|
| 主键 | `asset_id`（不依赖供应商） |
| 关联 | `work_id` / `version_id` 可空以支持通用素材；`rights_record_id` |
| 字段 | `asset_role`、`media_type`、`mime_type`、`file_extension`、`file_size_bytes`、`duration_ms`、`width/height`、`checksum_sha256`、`publication_status` [MEDIA_ASSET_DESIGN.md L123-L133] |
| 唯一性 | `UNIQUE(checksum_sha256, file_size_bytes)` 用于重复检测（不作硬拒绝，需人工确认） |
| 校验 | `publication_status=published` 必须有 `rights_status=verified` 的 `RightsRecord`；`checksum` 与存储实测不一致时禁用播放 |

### 3.8 StorageLocation / StorageProvider

| 项 | 设计 |
|---|---|
| 主键 | `storage_location_id`；外键 `asset_id` |
| 字段 | `provider`（local / tencent_cos / baidu_bos / s3_compatible）、`region`、`bucket`、`object_key`、`storage_class`、`is_primary`、`replica_status`、`verified_at` [MEDIA_ASSET_DESIGN.md L135-L143] |
| 接口 | `put / get / stat / delete / range`；业务层只见 `asset_id`，不保存供应商专属永久 URL [MEDIA_ASSET_DESIGN.md L18] |
| 阶段 | 本阶段只实现 `local`，不采购云资源 |

### 3.9 PlaybackResource（播放资源）

| 项 | 设计 |
|---|---|
| 主键 | `resource_id`；外键 `asset_id` 或 `recording_version_id` |
| 字段 | `resource_type`（external_link / official_preview / hosted_asset / official_embed）、`provider`、`provider_resource_id`、`external_url`、`access_policy`、`review_status`、`last_verified_at`、`embed_allowed`、`embed_enabled` [MEDIA_ASSET_DESIGN.md L145-L152；MUSIC_LIBRARY_DESIGN.md L85-L101] |
| 唯一性 | `UNIQUE(provider, provider_resource_id, resource_type)` |
| 校验 | `embed_enabled` 默认 `false`；临时签名 URL 不得作为永久资源地址；官方预览不持久化、不缓存 |

### 3.10 RightsRecord / EditorialReview

| 实体 | 主键 | 关键字段 | 唯一性 / 校验 |
|---|---|---|---|
| `RightsRecord` | `rights_record_id` | `subject_type` + `subject_id`（作品/版本/媒体）、`rights_holder`、`license_name/url`、`territory`、`permitted_uses`、`attribution_requirement`、`valid_from/until`、`evidence_url`、`reviewer/reviewed_at`、`rights_status` | 同一对象可有多条（不同地域/用途）；`permitted_uses` 不得包含未列明的再分发；过期自动失效 [DATA_MODEL.md L94-L103] |
| `EditorialReview` | `review_id` | `subject_type` + `subject_id`、评审维度分数（旋律美感/歌词文学性/儿童视角/编曲/演唱/耐听性/适龄性）、`reviewed_recording_version_id`、`conclusion`（核心收藏/文化收藏/扩展收藏/历史参考/暂不推荐）、`reviewer`、`reviewed_at` | 必须针对**具体录音版本** [CLASSIC_SONGS_CATALOG.md L201]；AI 只给建议，不自动判定权利或发布 [PROJECT_PRINCIPLES.md L98] |

### 3.11 支撑表

| 表 | 用途 |
|---|---|
| `ExternalIdentifier` | 三套历史 ID（`V1-xxx` / `CN-xxx` / `EN-xxx`）→ 稳定 `work_id` 映射；`UNIQUE(namespace, identifier)` |
| `Collection` / `CollectionMembership` | 专题、主题集合、年龄与场景导航 |
| `Tag` / `WorkTag` | 统一标签，跨馆复用 |
| `WorkRelation` | 作品关系（同曲异文、改编自、收录于专辑） |
| `ImportBatch` / `AuditLog` | 迁移批次与操作审计，支持按批次回滚 |

## 4. 状态流转

```text
research_status:  discovered → researching → reviewed → rejected
rights_status:    unknown → pending → verified / restricted → revoked
quality_status:   unreviewed → suitable / needs_context / unsuitable
publication_status: draft → pending_review → approved → published → withdrawn
access_method:    none → source_link / official_embed / licensed_media / own_original
```

**发布门禁**（应用层 + 数据库约束双重）：`publication_status → published` 要求

1. 作品 `quality_status=suitable`；
2. 所有待公开的 `WorkVersion.lyrics_text`、`ScoreEdition`、`MediaAsset` 均有 `rights_status=verified` 的 `RightsRecord`；
3. 对应 `PlaybackResource.review_status=approved`；
4. `EditorialReview` 存在且 `conclusion` 非「暂不推荐」；
5. 全部变更写入 `AuditLog`。

版权待确认的正文或媒体不得被公开接口返回 [DATA_MODEL.md L114]。研究状态推进**不要求**权利状态推进；权利未知不阻止研究登记。

## 5. 数据校验规则汇总

| 层次 | 规则 |
|---|---|
| 数据库 | 非空、枚举 CHECK、外键、唯一约束、年代范围、`embed_enabled` 默认 false、checksum 唯一提示 |
| 应用层 | 未知作者不得猜测补齐；无证旋律不得生成谱面；`no_lyric_applicable` 不得回填歌词；官方预览 URL 不持久化；未授权媒体不返回公开 URL |
| 导入 | 每条记录带 `import_batch_id`；导入前后对比数量、关联、孤儿、重复标题、权利分布；按批次可回滚 |
| 媒体 | 上传时计算 SHA-256 / 大小 / mime / 时长；与 `StorageLocation` 实测比对，不一致禁用 |
| 审计 | 权利状态、发布状态、评审结论的每次变更记录操作者、时间、前后值 |

## 6. 长期扩展能力自检

| 场景 | 是否支持 | 落点 |
|---|---|---|
| 500 首研究目录 | 支持 | `Work` + `ExternalIdentifier` + `SourceRecord`，`catalog_status=bibliography_candidate` |
| 一首作品多个录音版本 | 支持 | `RecordingVersion` 一对多 |
| 传统童谣多地区 / 语言 / 歌词版本 | 支持 | `WorkVersion(version_type=regional)` + 自引用父版本 |
| 创作者 / 演唱者 / 编曲者 | 支持 | `Contribution` 角色关联 + `RecordingVersion` 表演者字段 |
| 音频 / 简谱 / 五线谱 | 支持 | `ScoreEdition` + `MediaAsset` 派生关系 |
| 来源证据与历史背景 | 支持 | `SourceRecord(evidence_scope)` + `Work.historical_context` |
| 审美评审 | 支持 | `EditorialReview` 绑定具体录音版本 |
| 权利审核与公开发布 | 支持 | `RightsRecord` 分对象 + 发布门禁 |
| 故事馆 / 诗词馆复用 | 支持 | 通用层共享，独立领域表扩展 |

## 7. 与现有 JSON 的映射（详见 DATA_MIGRATION_PLAN.md）

| 源 | 目标 |
|---|---|
| `specialties.json` 105 条 | `Work` + `CollectionMembership` + `ExternalIdentifier` |
| `china-materials.json` / `world-materials.json` 55 / 47 | `WorkVersion` + `SourceRecord` + 封面 `MediaAsset` |
| `samples.json` 58 / 63 / 62 | `RecordingVersion` + `MediaAsset` + `PlaybackResource` |
| `official-recordings.json` 5 | `PlaybackResource(official_preview)` |
| `public-recording-collection.json` 27 | `MediaAsset` 候选（研究层） |
| `CHINESE_CHILDRENS_SONGS_500_CATALOG.md` 219 | 中间层 → `Work` + `SourceRecord` |
| MusicXML / SVG | `ScoreEdition` + `MediaAsset(derived_from_asset_id)` |

## 8. 待确认

- PostgreSQL 具体主版本（建议 16，VM 已有 `pgvector:pg16` 镜像）、UUID 生成策略、JSONB 与独立 profile 表的取舍。
- 迁移工具（建议 Alembic）与全量/增量导入的批次策略。
- 搜索方案：MVP 用 PostgreSQL 全文检索，不提前引入独立搜索引擎 [ARCHITECTURE.md L19]。
