# 音乐馆统一规划入口 · MUSIC_LIBRARY_MASTER_PLAN

- 文档状态：Active Master Plan
- 版本：v0.1
- 生效日期：2026-11-19
- 定位：**索引 + 口径 + 标准 + 版本登记**。本文不承载逐曲目录、字段级模型或部署命令。
- 上位依据：[项目顶层设计原则](PROJECT_PRINCIPLES.md)、[儿童经典音乐资源库 V1.0 规划](MUSIC_LIBRARY_V1.md)、[项目总入口](../README.md)。

> **本文不删除、不替换任何专项文档，也不把专项内容复制进来。** 500 首研究目录、100 首精选规划、审美准则、工程实施方案均保留原文，本文只负责统一它们之间的关系。

---

## 1. 音乐馆定位与长期目标

**以中国经典为根，以世界经典为窗，以优秀原创为未来** [MUSIC_LIBRARY_V1.md L16-L18]。

音乐馆不是一个追求歌曲数量的儿歌网站，而是长期建设的儿童音乐文化档案馆：今天收录的歌曲，将来孩子长大以后仍然值得重新打开、重新聆听 [MUSIC_LIBRARY_V1.md L18]。三个长期原则：宁缺毋滥、尊重文化、尊重版权 [MUSIC_LIBRARY_V1.md L248-L250]。

工程重构不改变这一定位，也不因资源数量降低审美标准。

## 2. 内容分层与数量口径

| 名称 | 定义 | 当前规模 | 公开层 | 可播放 |
|---|---|---|---|---|
| **500 首研究总目录** | 《中国儿童歌曲百年经典》四卷书目基线，长期研究采集对象 | 目标 500，已编号 219（第一卷 139 + 第四卷 80），第二、三卷缺 | 否（研究层） | 不适用 |
| **100 首精品精选候选** | V1.0 产品纲领：中国经典 55 / 世界经典 30 / 优秀原创 15 | 目标 100，尚无逐曲定稿 | 评审通过后 | 逐版本授权后 |
| **105 条原型发现目录** | 现有 `design-demos/specialties.json`：中国 55 + 英文 50，工程迁移对象 | 105 | 否 | 不适用 |
| **世界经典目录** | 独立研究与精选目录，含 47 条资料卡 | 47（35 条已核验歌词 + 12 条已定性结论） | 部分元数据 | 47 条音频全待采集 |
| **可播放资源** | 按「具体录音版本 + 使用权」独立统计，不计入作品数 | 58 条配置 / 63 版本 / 62 文件 / 5 官方预览；本地 85 个媒体文件 | 逐项门禁 | 逐项判断 |

**三条硬约束**：

1. 500 首是**研究目录**，不是发布目标；不得缩减为 100 首或 50 首，也不得用「500 条标题」冒充采集完成 [CHINESE_CHILDRENS_SONGS_500_CATALOG.md L20、L335]。
2. [ROADMAP.md](ROADMAP.md) 中「中文儿歌 50 条」是**早期跨馆元数据目录目标**，已在后续规划中被上述三层取代，保留为历史记录并加注，不作为音乐馆规模上限。
3. [MUSIC_LIBRARY_IMPLEMENTATION_PLAN.md L233](MUSIC_LIBRARY_IMPLEMENTATION_PLAN.md) 的「先 20 首完整档案样板」是**工程实施样板**，不改变任何研究目录规模；该文档 L237 明确「第二、三卷目录未补齐前，不得宣称 500 首已完整建档」。

## 3. 音乐审美与编辑准则

准则名：**优美 · 自然 · 童真 · 耐听** [MUSIC_LIBRARY_V1.md L100]。七个评审维度：旋律美感、童真表达、歌词文学性、音乐品质、文化价值、耐听程度、年龄适宜性 [MUSIC_LIBRARY_V1.md L102-L110]。

核心编辑原则 [MUSIC_LIBRARY_V1.md L114]：

> 不以刺激性作为吸引力，不以重复性作为记忆力，不以热度作为艺术价值。

顶层原则同时要求：项目不以数量作为唯一目标，重视艺术质量、语言质量、文化背景与长期价值；重要事实、来源和权利结论须有依据并经人工复核 [PROJECT_PRINCIPLES.md L91-L98]。

具体初筛维度、评分表与「不同录音版本分别评审」的要求见 [CLASSIC_SONGS_CATALOG.md L10-L17、L188-L201](CLASSIC_SONGS_CATALOG.md) 与 [CHINESE_CLASSIC_SONGS_RESEARCH.md](CHINESE_CLASSIC_SONGS_RESEARCH.md)。本文不复制表格。

## 4. 研究资源库 → 儿童使用层

| 阶段 | 动作 | 状态维度 | 依据 |
|---|---|---|---|
| 1 发现 | 登记标题、来源链接、版本线索 | `research_status` | PROJECT_PRINCIPLES.md §4 |
| 2 身份核验 | 词曲、年代、首发出处、别名去重 | `research_status` | DATA_MODEL.md §4 |
| 3 版本采集 | 录音版本、乐谱版本、歌词版本分别建档 | `research_status` | MUSIC_LIBRARY_IMPLEMENTATION_PLAN.md §3 |
| 4 审美评审 | 针对**具体录音版本**评审，不笼统打分 | `quality_status` | CLASSIC_SONGS_CATALOG.md §8 |
| 5 权利核验 | 作品 / 歌词 / 乐谱 / 编曲 / 表演 / 录音分开判断 | `rights_status` + `access_method` | DATA_MODEL.md §5 |
| 6 发布 | 检查全部待公开资产的权利状态 | `publication_status` | DATA_MODEL.md §6、MUSIC_LIBRARY_DESIGN.md §6 |

**五维状态互相独立**：研究完成 ≠ 版权确认 ≠ 质量适合 ≠ 公开发布 [DATA_MODEL.md L68-L81]。版权状态未知不应阻止作品进入内部研究目录，但公开播放、下载、嵌入和分发必须逐项核实 [PROJECT_PRINCIPLES.md §2、§5]。内部研究收录不等于获得公开播放授权 [MEDIA_ASSET_DESIGN.md L33]。

## 5. 500 首研究总目录

- 来源与目标：[CHINESE_CHILDRENS_SONGS_500_CATALOG.md L1-L20](CHINESE_CHILDRENS_SONGS_500_CATALOG.md)。
- 当前进度：第一卷 139 首（L39-L177）、第四卷 80 首（L185-L264），合计 219 首全部为 `bibliography_verified` +「待评审」；第二、三卷目录文本尚未取得（L266-L271）。
- 逐首采集字段与六阶段执行计划：同文档 L297-L335。
- 研究目录 ≠ 最终收录名单 ≠ 已授权资源（L20）；第二、三卷补齐前不得宣称 500 首已完整建档 [MUSIC_LIBRARY_IMPLEMENTATION_PLAN.md L237]。
- 该目录目前是 Markdown 四列表格，无稳定 `work_id`、无创作者/来源/权利字段，**不能直接批量入库**；迁移路径见 [DATA_MIGRATION_PLAN.md](DATA_MIGRATION_PLAN.md)。

## 6. 100 首精选与 105 条原型目录

- **100 首精选**：以 [MUSIC_LIBRARY_V1.md L187-L191](MUSIC_LIBRARY_V1.md) 为权威定义（55 / 30 / 15）。[CLASSIC_SONGS_CATALOG.md](CLASSIC_SONGS_CATALOG.md) 的 100 条是**首批采集候选**（中国 50 + 英文 50），构成不同，不等同于精选定稿；建议后续在文档内明确更名或加注，不删除条目。
- **105 条原型发现目录**：`specialties.json` 的作品与八专题映射，是工程迁移对象 [MUSIC_LIBRARY_IMPLEMENTATION_PLAN.md L224]。
- 三套 ID（500 首 `V1-xxx/V4-xxx`、候选 `CN-xxx/EN-xxx`、原型 `CN-xxx/EN-xxx`）**无映射表**，迁移前须建立 `external_identifiers` 与稳定 `work_id`，并完成同名异文去重。
- 世界经典目录独立建设，不与「100 首精选」中的 30 首互相替代。

## 7. 工程与数据基线索引

| 主题 | 文档 |
|---|---|
| 工程实施基准、10 类领域实体、M0–M4 | [MUSIC_LIBRARY_IMPLEMENTATION_PLAN.md](MUSIC_LIBRARY_IMPLEMENTATION_PLAN.md) |
| 播放资源字段与发布门禁 | [MUSIC_LIBRARY_DESIGN.md](MUSIC_LIBRARY_DESIGN.md) |
| 通用数据模型与五维状态 | [DATA_MODEL.md](DATA_MODEL.md) |
| 表结构、主键、唯一性与状态流转 | [DATABASE_DESIGN.md](DATABASE_DESIGN.md) |
| 统一媒体资产与 StorageProvider | [MEDIA_ASSET_DESIGN.md](MEDIA_ASSET_DESIGN.md) |
| 系统架构与 VM 实施约束 | [ARCHITECTURE.md](ARCHITECTURE.md) |
| 现状审计 / 迁移 / 路线 / 环境 | [PROJECT_AUDIT.md](PROJECT_AUDIT.md)、[DATA_MIGRATION_PLAN.md](DATA_MIGRATION_PLAN.md)、[IMPLEMENTATION_ROADMAP.md](IMPLEMENTATION_ROADMAP.md)、[REMOTE_DEVELOPMENT_ENVIRONMENT.md](REMOTE_DEVELOPMENT_ENVIRONMENT.md) |

工程实施以 [MUSIC_LIBRARY_IMPLEMENTATION_PLAN.md](MUSIC_LIBRARY_IMPLEMENTATION_PLAN.md) 为基准；本文不复制其阶段与字段。

## 8. 文档职责矩阵与版本记录

| 文档 | 版本 / 状态 | 职责 |
|---|---|---|
| PROJECT_PRINCIPLES.md | — | 顶层原则、双层架构（上位） |
| MUSIC_LIBRARY_V1.md | 1.0 Draft | **产品定位与审美基准** |
| MUSIC_LIBRARY_PLAN_V1.md | v1.0 | 产品与内容规划**历史扩展版**（内容保留，主次已加注） |
| MUSIC_LIBRARY_IMPLEMENTATION_PLAN.md | — | **工程实施基准** |
| MUSIC_LIBRARY_DESIGN.md | — | 播放资源与发布门禁 |
| CLASSIC_SONGS_CATALOG.md | v0.1 | 首批 100 条采集候选 |
| CHINESE_CHILDRENS_SONGS_500_CATALOG.md | v0.1 | **500 首研究总目录**（内容完整保留） |
| CHINESE_CLASSIC_SONGS_RESEARCH.md | v0.1 | 中国经典儿歌研究与字段建议 |
| DATA_MODEL.md / MEDIA_ASSET_DESIGN.md / ARCHITECTURE.md | 0.2 / 1.1 / 0.2 | 数据模型 / 媒体资产 / 系统架构（升版，未覆盖） |
| ROADMAP.md / DEVELOPMENT_STATUS.md / README.md | 0.2 / 2026-11-19 / — | 路线 / 状态 / 入口（已同步口径） |

| 版本 | 日期 | 变更 | 依据 |
|---|---|---|---|
| v0.1 | 2026-11-19 | 建立统一入口；定义 500 / 100 / 105 口径；登记专项文档职责 | Phase 0 文档基线审计（PROJECT_AUDIT.md） |

## 9. 明确不做的事

- 不删除或缩减 500 首目录，不合并卷内编号，不把第二、三卷缺口当成已完成。
- 不把 `bibliography_verified` 提升为 `metadata_verified` / `core_selected`。
- 不把内部研究录音、开放许可示例、官方短时预览自动标为「已授权」。
- 不因工程重构改变 MUSIC_LIBRARY_V1.md 的音乐审美定位。
- 不复制专项文档正文；本文只做索引、口径与版本登记。
