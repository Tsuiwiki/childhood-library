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
