# 数据模型设计

- 文档状态：Draft
- 版本：0.1

## 1. 建模原则

1. 作品、内容版本、来源记录、媒体资产和版权记录分离。
2. 一个作品可以有多个版本、译文、注释和媒体资产。
3. 一个作品可以有多个来源；来源条目不等同于作品本身。
4. 版权状态必须细化到具体内容或媒体资产，不能只在作品级设置一个笼统状态。
5. 所有审核与发布变更均可追溯。

## 2. 核心实体

| 实体 | 职责 |
| --- | --- |
| works | 作品主记录 |
| authors | 作者、作词者、作曲者、译者等人物 |
| work_contributors | 作品与贡献者的多对多关系及角色 |
| work_contents | 正文、歌词、译文、注释等内容版本 |
| categories | 多级内容分类 |
| tags | 主题标签 |
| work_categories / work_tags | 作品分类与标签关系 |
| sources | 信源定义与采集规则 |
| source_items | 来源侧发现的条目及来源 URL |
| ingestion_tasks | 采集任务及执行状态 |
| media_assets | 图片、音频等资产 |
| rights_records | 作品或资产的权利记录 |
| review_records | 人工审核记录 |
| work_relations | 作品之间的关联 |
| collections | 专题合集 |

## 3. 作品类型

建议枚举：
- literature
- song
- poem
- nursery_rhyme

语言使用 BCP 47 风格标签，例如 zh-CN、en、zh-Hant。

### 3.1 音乐资源三大支柱（V1.0 新增）

音乐馆按「以中国经典为根，以世界经典为窗，以优秀原创为未来」的定位，为 `works` 增加 `pillar` 字段，建议枚举：

- `china_classic`：中国经典（核心支柱，初期建设精力约 55%）
- `world_classic`：世界经典（重要支柱，约 30%）
- `original`：优秀原创（未来支柱，约 15%）

`pillar` 与既有 `work_type`、`language` 正交：同一支柱下可有童谣、创作儿歌、民歌、器乐等多种作品类型。早期若未显式赋值，可视为 `pending`（待归类），不默认归入任一支柱。

### 3.2 中国经典七个专题（V1.0 新增）

`china_classic` 支柱内进一步细分专题，建议用 `china_theme` 枚举或 `tags` 表达：

- `classic_children_song`：经典儿童歌曲
- `traditional_rhyme`：传统童谣
- `school_and_childhood`：校园与童年
- `nature_and_seasons`：自然与四季
- `animals_and_life`：动物与生命
- `classical_poetry_music`：古诗词音乐
- `folk_and_regional`：民族与地方音乐

分类注意：校园歌曲、儿童歌曲、成人创作的怀旧歌曲不应混为一谈；可按创作视角与音乐定位归入不同专题（如《童年》归入「校园与童年」而非「传统童谣」）。

## 4. 版权状态

建议枚举：
- pending：待核实
- public_domain_verified：已核实公版（需记录地区及依据）
- open_license：开放许可
- authorized：已获得授权
- link_only：仅允许展示基础信息和外链
- restricted：禁止公开使用
- expired_or_revoked：授权失效或撤回

版权记录应包含：
- rights_holder
- license_name / license_url
- territory
- permitted_uses
- attribution_requirement
- valid_from / valid_until
- evidence_url / evidence_file
- reviewer / reviewed_at
- notes

## 5. 发布状态

- draft
- pending_review
- approved
- published
- rejected
- withdrawn

发布校验必须检查内容状态和所有待公开资产的权利状态。版权待确认的正文或媒体不得被公开接口返回。

## 6. 建议 PostgreSQL 表结构（概念级）

```sql
CREATE TABLE works (
  id BIGSERIAL PRIMARY KEY,
  slug TEXT UNIQUE,
  title TEXT NOT NULL,
  work_type TEXT NOT NULL,
  language TEXT,
  description TEXT,
  age_min SMALLINT,
  age_max SMALLINT,
  publication_status TEXT NOT NULL DEFAULT 'draft',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE authors (
  id BIGSERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  original_name TEXT,
  nationality TEXT,
  birth_year INTEGER,
  death_year INTEGER,
  biography TEXT
);

CREATE TABLE work_contributors (
  work_id BIGINT REFERENCES works(id),
  author_id BIGINT REFERENCES authors(id),
  role TEXT NOT NULL,
  PRIMARY KEY (work_id, author_id, role)
);

CREATE TABLE work_contents (
  id BIGSERIAL PRIMARY KEY,
  work_id BIGINT NOT NULL REFERENCES works(id),
  content_type TEXT NOT NULL,
  language TEXT,
  version_label TEXT,
  content_text TEXT,
  source_item_id BIGINT,
  rights_record_id BIGINT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE sources (
  id BIGSERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  base_url TEXT,
  source_type TEXT NOT NULL,
  access_method TEXT NOT NULL,
  policy_url TEXT,
  enabled BOOLEAN NOT NULL DEFAULT false,
  notes TEXT
);

CREATE TABLE source_items (
  id BIGSERIAL PRIMARY KEY,
  source_id BIGINT NOT NULL REFERENCES sources(id),
  external_id TEXT,
  source_url TEXT NOT NULL,
  source_title TEXT,
  discovered_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  fetched_at TIMESTAMPTZ,
  content_hash TEXT,
  processing_status TEXT NOT NULL DEFAULT 'discovered',
  UNIQUE (source_id, source_url)
);

CREATE TABLE media_assets (
  id BIGSERIAL PRIMARY KEY,
  work_id BIGINT NOT NULL REFERENCES works(id),
  media_type TEXT NOT NULL,
  storage_uri TEXT,
  external_url TEXT,
  mime_type TEXT,
  checksum TEXT,
  rights_record_id BIGINT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE rights_records (
  id BIGSERIAL PRIMARY KEY,
  work_id BIGINT REFERENCES works(id),
  media_asset_id BIGINT REFERENCES media_assets(id),
  rights_status TEXT NOT NULL DEFAULT 'pending',
  rights_holder TEXT,
  license_name TEXT,
  license_url TEXT,
  territory TEXT[],
  permitted_uses TEXT[],
  valid_from DATE,
  valid_until DATE,
  evidence_url TEXT,
  evidence_notes TEXT,
  reviewed_at TIMESTAMPTZ
);

CREATE TABLE review_records (
  id BIGSERIAL PRIMARY KEY,
  work_id BIGINT NOT NULL REFERENCES works(id),
  reviewer_id TEXT,
  review_type TEXT NOT NULL,
  decision TEXT NOT NULL,
  comments TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

以上为概念起点。实际迁移需要补充外键、索引、检查约束、审计字段、角色权限，并解决媒体资产与版权记录的双向引用设计。

## 7. 去重策略

- 首选来源外部 ID 和规范化 URL。
- 标题 + 作者 + 类型作为候选匹配，不直接自动合并。
- 正文可在合法保存范围内计算内容哈希。
- 不同译本、改编本、朗读录音和插画版本应保留为不同版本或资产。
- 模糊匹配结果进入人工确认队列。


## 8. 音乐馆扩展模型（目录阶段预留）

音乐馆采用“作品—版本—播放资源”分层，避免把某个视频或录音误当成歌曲作品本身。

建议后续增加以下实体：

| 实体 | 职责 |
| --- | --- |
| song_versions | 具体演唱、编曲、录音或 MV 版本；关联作品及表演者、发行信息 |
| playback_resources | Bilibili、音乐平台、官方站点或授权站内音频等播放入口 |
| media_rights_records | 对具体录音、视频、封面等媒体资产分别记录权利与授权范围 |

建议字段：

**song_versions**
- id, work_id, version_label
- performer, arranger, recording_label, recording_year
- region, language, notes

**playback_resources**
- id, song_version_id, platform, resource_type
- resource_url, platform_video_id, embed_url, fallback_url
- embed_allowed, embed_enabled（默认 false）
- platform_terms_checked_at, review_status, review_notes

**作品分类字段（V1.0 新增）**
- `pillar`：china_classic / world_classic / original（对应三大支柱）
- `china_theme`：中国经典七专题（见 3.2 节）
- `age_min` / `age_max` 或 `age_band`：0–2 / 2–4 / 4–6 / 6–12 岁推荐层级，仅作参考而非限制
- `editorial_note`：编辑推荐语，承载「每首歌一篇小档案」的内容定位

**权利记录补充**
- 对歌词/词作、曲/旋律、译词/改编/编曲、表演、录音制品、MV/视频画面分别核验。
- 记录目标地域、允许用途、期限、署名要求、权利人和证据。
- 作品公版状态不能自动推导具体录音、编曲或视频也可使用。

首期可以先用现有 works、work_contributors、sources 和 rights_records 管理歌曲元数据；在实现播放功能前，再通过数据库迁移增加版本与播放资源表。详细字段和阶段要求见 [音乐馆设计](MUSIC_LIBRARY_DESIGN.md)，长期定位与选曲纲领见 [儿童经典音乐资源库 V1.0 规划](MUSIC_LIBRARY_V1.md)。
