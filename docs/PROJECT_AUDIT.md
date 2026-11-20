# 项目现状审计报告 · PROJECT_AUDIT

- 文档状态：Phase 0 Audit
- 版本：v0.1
- 审计日期：2026-11-19
- 审计基准：GitHub `Tsuiwiki/childhood-library` main `e0a883ffd3f5c1ff77005770f782f880b94ce17a`
- 方法：GitHub 连接器读取 main 目录与文件 → `git show origin/main:<path>` 导出只读快照 → `git hash-object` 与 API blob SHA 比对 → 本地文件系统清点 → 远程 VM SSH 只读探测
- 性质：只读审计；**未修改历史数据、未删除原型、未清空任何数据库**

> 引用格式：`[简称] L48` 表示该文件第 48 行。证据文件清单见 §0。

---

## 0. 证据文件清单

| 简称 | 文件 | 规模 | 说明 |
|---|---|---|---|
| [README] | `README.md` | 118 行 | 项目入口、导航、技术路线 |
| [PRINCIPLES] | `docs/PROJECT_PRINCIPLES.md` | 6,789 B | 顶层原则 |
| [V1] | `docs/MUSIC_LIBRARY_V1.md` | 272 行 | 产品定位与审美基准 |
| [IMPL] | `docs/MUSIC_LIBRARY_IMPLEMENTATION_PLAN.md` | 403 行 | 工程实施基准 |
| [DESIGN] | `docs/MUSIC_LIBRARY_DESIGN.md` | 14,607 B | 播放资源与门禁 |
| [CATALOG] | `docs/CLASSIC_SONGS_CATALOG.md` | 245 行 | 首批 100 条采集候选 |
| [RESEARCH] | `docs/CHINESE_CLASSIC_SONGS_RESEARCH.md` | 19,166 B | 中国经典儿歌研究 |
| [500CAT] | `docs/CHINESE_CHILDRENS_SONGS_500_CATALOG.md` | 349 行 | 500 首研究总目录 |
| [ROADMAP] | `docs/ROADMAP.md` | 7,092 B | 阶段路线 |
| [DEV] | `docs/DEVELOPMENT_STATUS.md` | 175 行 | 开发进度盘点 |
| [DM] | `docs/DATA_MODEL.md` | 11,124 B | 通用数据模型 |
| [MEDIA] | `docs/MEDIA_ASSET_DESIGN.md` | 260 行 | 统一媒体资产设计 |
| [ARCH] | `docs/ARCHITECTURE.md` | 4,349 B | 系统架构 |
| [PLANV1] | `docs/MUSIC_LIBRARY_PLAN_V1.md` | 451 行 | 另一份产品规划基线 |

本地数据（仓库内 JSON）：`specialties.json` 105 条、`china-materials.json` 55 条、`world-materials.json` 47 条、`audio/samples.json` 58 条、`audio/official-recordings.json` 5 条、`audio/public-recording-collection.json` 27 文件 / 28 映射、`library-content.json` 160 条。VM 探测命令编号 [C1]–[C4] 见 [REMOTE_DEVELOPMENT_ENVIRONMENT.md](REMOTE_DEVELOPMENT_ENVIRONMENT.md)。

## 1. Git 与分支基线

| 项 | 审计时状态 | 证据 |
|---|---|---|
| 审计前本地 HEAD | `b246e58` | `git rev-parse` |
| GitHub main | `e0a883f` | GitHub API `get_commit` |
| 差距 | 本地**落后 11 个提交**，全部为文档 | `git log HEAD..origin/main` |
| 工作区 | 干净，无未提交文件 | `git status --short` |
| 换行配置 | `core.autocrlf=true`（工作区 CRLF / 仓库 LF） | `git config` |
| 已执行 | 完整备份（844 文件 / 190,547,373 字节，含 `.git` 与 88 个 audio 目录文件）→ `git merge --ff-only origin/main` → 12 份文档 SHA 与 GitHub 一致 | T-01 执行记录 |

`.gitignore` 已忽略 `.env`、`.env.*`（保留 `.env.example`）、`design-demos/audio/*` 全部音频扩展名、`refs/*.png`、`design-demos/*.png` 等二进制媒体。

## 2. 文档基线

12 份指定文档在 GitHub main **全部存在**，`docs/` 共 20 份 `.md` + `assets/`。 八份目标交付文档中 `ARCHITECTURE.md`、`MEDIA_ASSET_DESIGN.md` **已存在**（按升版处理，未覆盖），其余 6 份与 `MUSIC_LIBRARY_MASTER_PLAN.md` 为本次新增。

12 份 SHA 复核（索引 blob）= GitHub API 返回值，例如 README `b643adc8…`、ROADMAP `5e9dea40…`、500CAT `e11a4500…`、MEDIA `b45d0207…`、IMPL `a4eaa4c5…`。

## 3. 音乐馆资产与媒体引用

| 项 | 实测 | 证据 |
|---|---|---|
| `design-demos/` 文件 | 453 个：PNG 161、SVG 119、WAV 52、PY 26、HTML 23、M4A 16、MP3 15、MusicXML 14、JSON 13、MD 5、JPG 3、FLAC 1、MP4 1、PYC 3 | 本地只读清点 |
| Python 脚本 | 26 个：7 个 `validate_*` 回归、8 个构建、4 个 `probe_*` 只读探针、4 个采集接入、3 个其它 | 文件清单 |
| 作品发现目录 | 105 条（CN 55 / EN 50），八专题 | `specialties.json` |
| 试听配置 | 58 条 / 63 版本 / **62 个唯一文件名** | `samples.json` |
| 本地真实音频 | **85 个**（52 WAV、16 M4A、15 MP3、1 FLAC、1 MP4） | 本地清点 |
| 62 引用本地缺失 | **0** | 文件名集合比对 |
| 孤儿文件 | **23** | 文件名集合比对 |
| 资源类型 | `internal` 26、`generated` 21、`open` 8、**3 条无 `sampleType`**（`EN-T01`～`EN-T03`） | `samples.json` |
| 官方预览 | 5 条（`CN-C03/C04/C07/C19/C20`） | `official-recordings.json` |
| 世界经典音频 | 47 条全部「待采集」、`hasAudio=false` | `world-materials.json` |

**核心澄清**：[DEV] L74 原写「62 个音频引用没找到对应文件」，该结论对 **GitHub 仓库**成立（`.gitignore` 排除全部二进制），对**本地工作区**不成立。已在 [DEV] 中改为分环境表述。配置引用 ≠ 实际媒体文件；实际媒体文件也 ≠ 已获公开播放授权。逐项校验见 [资产与媒体完整性清单](reports/asset-inventory.md)。

## 4. 500 首计划完整性

| 卷次 | 年代 | 已编号 | 状态 | 证据 |
|---|---|---|---|---|
| 第一卷 | 1900—1948 | 139 | `bibliography_verified` / 待评审 | [500CAT] L33、L39-L177 |
| 第二卷 | 1949—1978 | 0 | 未取得可逐首核验的完整目录文本 | [500CAT] L266-L271 |
| 第三卷 | 1979—1999 | 0 | 目录与作品级来源待补 | [500CAT] L266-L271 |
| 第四卷 | 2000—2015 | 80 | `bibliography_verified` / 待评审 | [500CAT] L179、L185-L264 |
| 合计 | — | **219 / 500** | 缺约 281 首 | [500CAT] L6 |

219 行**全部**仅完成书目核对，**0 首**完成身份核验、创作者确认、音频/乐谱登记、审美评审或权利核验。另有 15 首跨卷代表作品索引，不计入编号目录 [500CAT] L273-L295。逐首采集字段与六阶段计划见 [500CAT] L297-L335。

**计划未被缩减**：500 首目录完整保留；缺的是第二、三卷目录文本，属采集进度问题。[IMPL] L233 的「20 首样板」是工程样板，[IMPL] L237 明确禁止宣称 500 首已建档。

**迁移可行性**：当前是 Markdown 四列表格，无稳定 `work_id`、无创作者 / 来源 URL / 权利字段，与 [IMPL] L70 的稳定 ID 要求不兼容；三套 ID 无映射。**不能直接批量导入**，须先建中间层与 `external_identifiers`。

## 5. 数量口径与冲突清单（11 项）

统一定义见 [MUSIC_LIBRARY_MASTER_PLAN.md §2](MUSIC_LIBRARY_MASTER_PLAN.md)。主要冲突：

| 编号 | 冲突 | 证据 | 处置 |
|---|---|---|---|
| C-01 | ROADMAP「中文儿歌 50 条」属早期跨馆目录目标 | [ROADMAP] L149-L152 | 加注 + 链接 MASTER_PLAN，不删历史 |
| C-02 | 「100 首」三种构成：V1 55/30/15、CATALOG 50+50、specialties 105=55+50 | [V1] L189-L191；[CATALOG] L39、L157 | MASTER_PLAN 三层定义 |
| C-03 | [DEV] L74 媒体表述与本地实测不符 | §3 | 已修订为分环境表述 |
| C-04 | ARCH / MEDIA 已存在，不能按「新建」覆盖 | `git ls-tree` | 升版追加，未覆盖 |
| C-05 | [V1] 与 [PLANV1] 双产品基线 | [V1] L1-L6；[PLANV1] L1-L8 | 加注主次，都不删 |
| C-06 | README 目录树列 `backend/frontend/ingestion/deploy`，实际 main 无这些目录 | [README] L57-L71 | 标注「规划中，尚未创建」 |
| C-07 | [DM] 通用实体与 [IMPL] 音乐实体命名不一致 | [DM] L14-L32、L237-L247；[IMPL] L42-L64 | [DATABASE_DESIGN.md](DATABASE_DESIGN.md) 映射表 |
| C-08 | 三套 ID 无交叉引用 | [500CAT] L39；[CATALOG] L39、L207 | `external_identifiers` |
| C-09 | 「20 首样板」易被误读为缩减 | [IMPL] L233、L237 | MASTER_PLAN §2 写死 |
| C-10 | [IMPL] L274-L281 要求的完整性报告未落盘 | [IMPL] L274-L281 | 本次生成 [asset-inventory.md](reports/asset-inventory.md) |
| C-11 | [DEV] L26-L36 资产统计与本地 453 文件口径不同 | [DEV] L26-L36 | 标注两套口径 |

## 6. 远程 VM 现状（只读探测概要）

| 项 | 实测 |
|---|---|
| 系统 | TencentOS Server 3.2（el8.2 兼容），内核 5.4.241 x86_64 |
| 资源 | 8 核 / 15 Gi（无 swap）/ 99 G 磁盘 65 G 可用 / inode 5% |
| 网络 | GitHub / PyPI / npm 出站均 200；`firewalld` inactive |
| 软件 | git 2.43.7、Docker 26.1.3、Compose v2.27.0、系统默认 Node 22.12.0、npm 10.9.0（Phase 0 实测快照；前端工程基线 Node 22.22.2 见 `web/.nvmrc`） |
| Python | `python3` = 3.6.8（EOL），另有 `python3.11` / `python3.12.11` |
| 数据库 | 未安装 PostgreSQL；已有 `pgvector/pgvector:pg16` 镜像 |
| 共享机 | 已有 TiDB v8.5.0、anydev-agent 等容器；8080/8090/4000/10080/2379 已占用；5432/8000/5173/3000/6379 空闲 |
| 目录 | `/data/workspace` 为空，无 childhood-library 目录 |

P0 约束：显式使用 3.12 或容器 Python；内部端口绑回环；独立目录 / project name / volume；不清理已有容器；SSH 参数不入库。详见 [REMOTE_DEVELOPMENT_ENVIRONMENT.md](REMOTE_DEVELOPMENT_ENVIRONMENT.md)。

## 7. 本次未用上的材料与补采建议

| 未覆盖 | 原因 | 建议 |
|---|---|---|
| 85 个音频的时长 / 编码 / 采样率 | 本轮以 SHA-256 与大小为主 | 后续用媒体探测补齐到 MediaAsset |
| 161 PNG / 119 SVG / 14 MusicXML 逐项关联作品与权利 | 数量大，非基线审计范围 | T-03 清单已登记数量，逐项关联列入迁移阶段 |
| 26 个 Python 脚本源码级职责与依赖 | 本轮只列文件名与分类 | 逐脚本登记，决定保留/封装/淘汰，不整批重写 [IMPL] L33 |
| 7 个 `validate_*` 回归脚本未运行 | 本轮只改文档，未改页面 | 实施前跑一次基线回归 |
| VM 的 Docker storage driver、cron、日志轮转、上层安全组 | 只读探测未覆盖 | 环境启用前补一轮，尤其因防火墙 inactive |
| `docs/assets/` 3 个 SVG、根目录设计规范文件 | 与数量/文档基线无关 | 视觉规范复用时再核 |

## 8. 结论

1. 12 份指定文档在 GitHub main 全部存在，500 首计划与审美标准有正式文档承载，未被工程重构削弱 [500CAT] L5-L6、[V1] L96-L121。
2. 审计前本地落后 11 个提交，已备份并快进同步，工作区干净。
3. 500 首目录完整保留但只完成 219 首书目核对，第二、三卷缺；Markdown 表格不能直接入库。
4. 62 个音频引用的真实情况是「GitHub 无媒体、本地 85 个文件且引用零缺失」，已修订表述。
5. 11 项数量/文档冲突已登记并给出处置，8 份目标文档中 2 份按升版处理。
6. VM 可支撑重构，但有 Python 版本、防火墙、共享机隔离与 PostgreSQL 未安装四项 P0 约束。
7. 本轮新增/修订的均为文档与只读脚本；历史原型与数据全部保留。
