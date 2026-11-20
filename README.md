# 童年书房 · Childhood Library

Childhood Library 首先是一个面向儿童文化的研究、发现、采集、整理与学习项目，其次才是面向儿童和家庭提供阅读、聆听与欣赏服务的资源产品。项目覆盖儿童音乐、故事文学、诗歌诗词及其他儿童文化内容。

同时，平台定位为面向大众与教育场景的免费公共数字文化数据库，以普及教育和传统文化传承为目标，免费供大众、家庭、教师及教育机构使用。

> **顶层原则：先研究采集，再判断使用。版权状态未知，不应成为有价值的儿童文化作品进入内部研究目录的门槛；公开展示、播放、下载、转载和分发，则按具体作品、版本、媒体与使用方式另行核实。**

> **项目原则：免费公共教育、广泛建立目录、来源可追溯、具体内容评审后公开。**

项目采用“研究资源库（Research）+ 儿童阅读与使用层（Library）”双层架构。研究阶段优先发现、记录和研究中国及世界的优秀儿童文化资源；使用阶段再审核来源规则、内容质量、适宜性和权利范围。

本仓库只存放软件代码、设计文档、元数据规范和必要的测试样例。研究登记不代表可以复制第三方正文或媒体；默认记录必要元数据和原始来源链接，不绕过平台限制。

## 项目目标

- 建设免费、结构化、可检索、可持续维护的儿童文化与传统文化资源目录。
- 通过开放 API、开放数据集、RSS 和明确允许的来源广泛发现资源，先建立目录和合法来源链接。
- 将不同来源的数据转换为统一作品模型，保留来源、版本和处理记录。
- 使用 AI 辅助分类、摘要、字段补全和质量检查，不让 AI 自动决定版权状态。
- 建立适用于音乐、故事文学、诗歌诗词等全部内容的研究资源库与儿童使用层：版权未知的候选作品可登记研究；公开使用按具体作品、版本、媒体及使用方式审核。
- 建立逐项内容评审流程；正文、歌词、译文、插画和音频等具体内容评审通过后才公开。
- 为大众、家庭、教师和教育机构提供统一的文学阅读、诗词学习与歌曲发现体验。

## 首期内容范围

1. 儿童文学：童话、寓言、民间故事、儿童小说、儿童诗歌。
2. 经典儿歌：中文儿歌、传统童谣及授权歌曲目录。
3. 古诗词：唐诗、宋词、元曲及儿童诗词启蒙。
4. 英文儿歌：Nursery Rhymes、字母歌、数字歌、动物与自然主题歌曲。

## 当前开发状态

**更新至 2026-11-21：T-04～T-08 已落地，Vue 内部研究前端已覆盖音乐馆、8 个音乐专题、故事馆、古诗词馆、录音列表与详情，并新增跨馆资料总览。** 当前可直接检索 105 条音乐作品目录、100 条故事研究记录、60 条诗词研究记录及已登记的逐曲研究文档；58 条主录音记录可查看封面、歌词/谱面状态、版本、来源、许可与文件校验信息。

前端保留原型视觉与研究边界，使用已有 JSON 快照和 GitHub 文档建立链接，不把研究收录当作公开发布授权。51 个 Vitest 用例与生产构建通过；真实服务在远程 VM 的只读回环预览容器中运行。85 个媒体文件仅存于 VM，不提交 GitHub。

后端已有 FastAPI 骨架、PostgreSQL 16、20 张业务表、Alembic 迁移、媒体资产模块与 104 个 pytest 基线；**业务表仍为空，7 个业务域清单接口仍为 501，正式编辑后台、业务 CRUD、数据导入与发布审核尚未完成**。因此当前 Vue 页面是内部研究前端，不是正式公开曲库。

- [开发进度盘点](docs/DEVELOPMENT_STATUS.md)：历史审计与最新实现进展。
- [前端运行与数据边界](web/README.md)：Vue 路由、测试、Node 基线和资料来源。
- [音乐馆实施优化方案](docs/MUSIC_LIBRARY_IMPLEMENTATION_PLAN.md)：领域模型、资源分类和分阶段实施路径。

文档中的数量均按研究快照统计，不代表所有数据已逐条核验或所有媒体已获得公开使用许可。

## 技术路线（拟定）

| 层次 | 首选方案 |
| --- | --- |
| Web 前台 / 管理后台 | Vue 3、TypeScript、Vite |
| API | Python、FastAPI、Pydantic |
| 主数据库 | PostgreSQL |
| 采集与解析 | Python、HTTPX、BeautifulSoup（遵守来源规则） |
| 任务队列 | MVP 先用简化后台任务；规模需要时再考虑 Celery + Redis |
| 媒体存储 | 统一 Media Asset Service；本地适配器起步，云端可接 COS / BOS；仅保存获准使用的媒体 |
| 部署 | Docker Compose、Nginx |

技术选型允许在 MVP 实施中调整，避免过早引入微服务和复杂基础设施。当前静态原型是产品验证资产；API 骨架（T-05）、数据库模型与迁移（T-06）已落地，媒体存储适配器（T-07 M0 本地实现）与前端工程骨架（T-08）已落地，云端适配器与采集系统、正式业务页面仍待后续任务。

## 仓库结构

```text
.
├── README.md
├── LICENSE
├── .gitignore
├── .env.example
├── docs/                    # 项目原则、产品/架构/数据/版权/路线图文档
├── design-demos/            # 当前静态页面、JSON 数据、Python 构建脚本和原型素材
├── story-library.html       # 故事馆相关静态原型入口
├── app/                     # FastAPI 模块化单体（T-05 骨架 + T-06 ORM + T-07 媒体资产）
│   └── media/               # StorageProvider / 本地适配器 / 校验和 / 权利门禁
├── tests/                   # pytest 基线（104 用例）
├── migrations/              # Alembic 配置与初始迁移（T-06，详见 migrations/README.md）
├── alembic.ini              # Alembic 入口；连接串只从环境变量读取
├── Dockerfile / .dockerignore / pytest.ini
├── requirements.txt / requirements.lock   # 顶层依赖 + 全量精确锁（36 包）
├── web/                     # Vue 3 + TS + Vite 内部研究前端（51 个 Vitest）
│   ├── src/                 # 三馆 / 专题 / 录音详情 / 跨馆资料总览 / API 客户端
│   └── tests/               # 组件、播放器、资料关联、深链接与路由测试
├── deploy/                  # Compose / 备份恢复配置（cl-dev 的 db + api 已在 VM 启用）
├── scripts/                 # 资产盘点、媒体完整性等只读工具
└── docs/reports/            # 资产完整性与迁移报告
```

## 文档导航

### 项目总纲
- [项目顶层设计原则](docs/PROJECT_PRINCIPLES.md)
- [产品需求文档](docs/PRD.md)
- [系统架构设计](docs/ARCHITECTURE.md)
- [统一媒体资产与对象存储设计](docs/MEDIA_ASSET_DESIGN.md)
- [数据模型设计](docs/DATA_MODEL.md)
- [采集系统设计](docs/INGESTION_DESIGN.md)
- [信源清单与接入计划](docs/SOURCE_CATALOG.md)
- [版权与内容审核政策](docs/COPYRIGHT_POLICY.md)
- [项目路线图](docs/ROADMAP.md)
- [开发进度盘点](docs/DEVELOPMENT_STATUS.md)

### 儿童音乐馆
- [音乐馆统一规划入口（MASTER PLAN）](docs/MUSIC_LIBRARY_MASTER_PLAN.md)
- [儿童经典音乐资源库 V1.0 规划](docs/MUSIC_LIBRARY_V1.md)
- [音乐馆设计：歌曲目录、版权与播放资源](docs/MUSIC_LIBRARY_DESIGN.md)
- [音乐馆实施优化方案](docs/MUSIC_LIBRARY_IMPLEMENTATION_PLAN.md)
- [经典儿童歌曲候选目录（首批采集）](docs/CLASSIC_SONGS_CATALOG.md)
- [中国经典儿歌研究与资源采集](docs/CHINESE_CLASSIC_SONGS_RESEARCH.md)
- [中国儿童歌曲500首研究目录](docs/CHINESE_CHILDRENS_SONGS_500_CATALOG.md)
- [逐曲研究：历史作品与版本线索](docs/CHINESE_CHILDRENS_SONGS_RESEARCH_BATCH_2026-11-20.md)
- [逐曲研究档案·批次02](docs/research/CHINESE_CHILDRENS_SONGS_BATCH_02.md)
- [逐曲研究档案·批次03](docs/research/CHINESE_CHILDRENS_SONGS_BATCH_03.md)
- [音频入口与版本核验·批次04](docs/research/CHINESE_CHILDRENS_SONGS_AUDIO_BATCH_04.md)
- [音频优先采集档案·批次04](docs/research/CHINESE_CHILDRENS_SONGS_BATCH_04_AUDIO.md)
- [音频链接采集·批次05](docs/research/CHINESE_CHILDRENS_SONGS_BATCH_05_AUDIO_LINKS.md)

### 工程、迁移与环境
- [项目现状审计报告](docs/PROJECT_AUDIT.md)
- [目标架构与数据库设计](docs/DATABASE_DESIGN.md)
- [远程开发环境方案](docs/REMOTE_DEVELOPMENT_ENVIRONMENT.md)
- [音乐馆重构计划](docs/MUSIC_LIBRARY_REFACTOR_PLAN.md)
- [数据迁移方案](docs/DATA_MIGRATION_PLAN.md)
- [实施路线与任务清单](docs/IMPLEMENTATION_ROADMAP.md)
- [资产与媒体完整性清单](docs/reports/asset-inventory.md)
- [后端骨架与数据模型说明](app/README.md)
- [数据库迁移说明](migrations/README.md)
- [部署与运维命令](deploy/README.md)

### 儿童故事馆与其他内容馆
- [儿童故事馆建设方案 v1.1（图文版）](docs/STORY_LIBRARY_PLAN_V1.md)

## 基本原则

- 遵循「先研究采集，再判断使用」：研究资源库（Research）与儿童阅读使用层（Library）分开，逐项记录 `research_status`、`rights_status`、`quality_status`、`access_method`、`publication_status`。
- 正文默认按完整篇章、全卷或全书采集，不以节选、梗概、导读或原创整理稿冒充正文；全文已采集不等于已获公开授权。
- 默认不抓取登录后内容、付费内容、受技术限制的内容或明确禁止自动访问的页面。
- 尊重 robots.txt、网站服务条款、API 使用政策、速率限制和授权范围。
- “可访问”“公版作品”“开放许可”“允许转载”不是同一个概念，必须逐项核实。
- 作品正文、译文、歌词、插画、录音和编曲分别记录权利状态。
- 待确认或授权不明的内容可以进入内部研究库，记录必要元数据和原始来源链接；不得据此公开受保护正文或媒体，也不得默认下载、缓存、镜像或分发第三方媒体文件。
- 可合法发现的资源先进入公共候选目录；待评审资源可公开必要的基础元数据与合法来源链接，但不公开受保护正文、不分发未经许可的媒体文件。
- 保留原始来源、采集时间、版本、转换记录和审核轨迹。

## License

本仓库中的软件代码采用 [MIT License](LICENSE)，除非某个文件或组件另有明确声明。

**内容资源不自动适用 MIT License。** 项目收录或未来收录的文学作品、歌词、翻译、注释、插画、音频、视频及其他第三方媒体，其版权归属和使用条件以各自的版权记录、来源条款及授权文件为准。未经授权，不得复制、分发或商业使用这些内容。

MIT License 仅适用于项目维护者有权授权的代码及明确纳入该许可证的文件，不授予第三方内容的任何额外权利。
