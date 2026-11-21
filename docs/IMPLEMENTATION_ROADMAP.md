# 实施路线与任务清单 · IMPLEMENTATION_ROADMAP

- 文档状态：Active
- 版本：v0.1
- 日期：2026-11-19
- 依据：[PROJECT_AUDIT.md](PROJECT_AUDIT.md)、[ARCHITECTURE.md](ARCHITECTURE.md)、[DATABASE_DESIGN.md](DATABASE_DESIGN.md)、[MUSIC_LIBRARY_REFACTOR_PLAN.md](MUSIC_LIBRARY_REFACTOR_PLAN.md)、[DATA_MIGRATION_PLAN.md](DATA_MIGRATION_PLAN.md)、[REMOTE_DEVELOPMENT_ENVIRONMENT.md](REMOTE_DEVELOPMENT_ENVIRONMENT.md)

---

## 1. 阶段门禁

| 门禁 | 条件 | 解锁 |
|---|---|---|
| A | 确认审计报告、500 首完整性报告、冲突清单、MASTER_PLAN 与修改清单 | 提交 GitHub 文档修改（**已确认，2026-11-19**） |
| B | 确认 VM 目录 / 端口 / 数据库方案，并在启用前复核 `ss -lntp` | T-04 在 VM 创建目录与容器（**已按 `.env.example` 默认值落地并复核 `ss -lntp`；正式确认待办**） |
| C | 确认 100 首权威定义与第二、三卷目录来源 | T-11 完整研究目录导入 |
| D | MVP 闭环验收通过 | Phase 5 扩展故事馆 / 诗词馆、云存储适配器 |

## 2. 当前进度

| 任务 | 状态 |
|---|---|
| T-01 备份与同步 | **已完成**：844 文件 / 190,547,373 字节备份，`ff-only` 同步到 `e0a883f`，12 份文档 SHA 复核一致 |
| T-02 文档基线 | **已完成**：新增 7 份文档、升版 3 份、修订 4 份，历史专项文档全部保留 |
| T-03 资产清单 | **已完成**：只读脚本与报告落盘 |
| T-04 部署配置骨架 | **已完成（VM 侧）**：修复 overlay 序列合并与仓库根 `.env` 加载；VM 已 clone、生成 `.env`（`600`）、建 3.12 venv、启动 `cl-dev`（healthy、仅回环），`cl-test` 备份恢复演练通过。⚠️ 门禁 B 正式确认与 `/data` 容量缺口待处理 |
| T-05 后端工程初始化 | **已完成**：FastAPI 3.12 骨架 + 统一 envelope / 错误码 + 结构化日志 + 7 域占位路由；`requirements.lock` 29 包；31 个 pytest 全绿；api 容器 healthy、`/healthz` 200 |
| T-06 数据库模型与迁移 | **已完成**：20 张表（10 核心 + 10 支撑）、Alembic 初始迁移、五维状态 + 发布门禁；57 个 pytest 全绿；cl-dev 已迁移且业务表为空；备份链路可 dump 新 schema |
| T-07 媒体资产模块 | **已完成**：`app/media/` 能力层、本地适配器、SHA-256 完整性、三级权利门禁、Range 响应、只读 capabilities 端点、`api` 容器 `var/media:ro` 正式挂载；VM 104 个 pytest 全绿、85/85 完整性校验、隔离库登记演练通过 |
| T-08 前端工程初始化 | **已完成并继续迁移内部研究界面**：Vue 3 + TS + Vite、精确版本锁、原型 token 与共享组件、统一 API 客户端；三馆、8 个音乐专题、58 条录音详情、71 条外部音源/目录、跨馆资料总览、跨页连续播放和筛选结果列表循环已接入；61 个 Vitest 全绿、构建通过；原型未改动、业务数据库未导入 |
| T-09 ～ T-12 | 未开始（门禁 B 正式确认 / 门禁 C 待办） |

---

## 3. 任务清单

> 每项含：任务编号、目标、前置依赖、涉及文件、实施步骤、测试方法、验收标准、风险与回滚。

### T-01 基线同步与备份
- **目标**：本地与 GitHub main 一致，并产生可回滚的完整备份。
- **前置**：无（门禁 A）。
- **文件**：整仓，含 `.git` 与被忽略媒体。
- **步骤**：记录 `git status` → 仓库外完整备份 → `git merge --ff-only origin/main` → 12 份文档 SHA 复核 → 记录备份路径与校验值。
- **测试**：`HEAD == origin/main`；备份文件数与字节数一致。
- **验收**：工作区干净、无文件丢失、备份可列举。
- **风险/回滚**：本地曾落后 11 个提交；禁止 `reset --hard`；出错从备份恢复。

### T-02 文档基线与 MASTER_PLAN 落地
- **目标**：统一 500/100/105 口径，落地 7 份新文档，升版 2 份既有文档，修订 4 份表述。
- **前置**：T-01。
- **文件**：`docs/*.md`、`README.md`。
- **步骤**：新建 MASTER_PLAN 与 6 份工程文档 → ARCHITECTURE / MEDIA_ASSET_DESIGN / DATA_MODEL 升版追加 → README / ROADMAP / DEVELOPMENT_STATUS / MUSIC_LIBRARY_PLAN_V1 修订 → 交叉链接校验。
- **测试**：文档相对链接可达；数量表述全局检索无冲突。
- **验收**：500 首目录未缩减；旧专项文档全部保留；MASTER_PLAN 不复制全文。
- **风险/回滚**：覆盖已有文档会丢成果 → 只追加升版；单文档 `git revert` 可回滚。

### T-03 资产与媒体完整性清单
- **目标**：产出实施基准要求的媒体完整性报告。
- **前置**：T-01。
- **文件**：`scripts/asset_inventory.py`、`docs/reports/asset-inventory.md`。
- **步骤**：只读扫描 JSON 引用 → 比对真实文件 → 计算 SHA-256 / 大小 / 格式 → 标记缺失、孤儿、重复、缺类型 → 输出报告。
- **测试**：断言 62 引用零缺失、23 孤儿、85 个音频、3 条缺 `sampleType`。
- **验收**：报告可被 T-11 直接消费；不修改任何媒体文件。
- **风险/回滚**：纯只读；删除产物即可回滚。

### T-04 远程 VM 环境初始化
- **目标**：建立独立、可复用、端口不暴露公网的开发环境。
- **前置**：T-01、门禁 B。
- **文件**：`deploy/` 配置骨架、`REMOTE_DEVELOPMENT_ENVIRONMENT.md`、VM 上 `.env` 与 `var/`。
- **步骤**：复核 `ss -lntp` → 建 `/data/childhood-library` → `python3.12 -m venv` → 起 PostgreSQL 16 容器（回环）→ 独立 volume → 日志 / 备份 / 健康检查 → 恢复演练。
- **测试**：`docker compose ps` 全 healthy；数据库端口从公网不可达；`pg_dump` + 恢复演练成功（三项均已在 T-04 通过）；`/healthz` 200 已在 T-05 验证。
- **验收**：部署 / 启动 / 停止 / 日志 / 备份 / 恢复六类说明可执行；不触碰已有 TiDB 容器。
- **风险/回滚**：`firewalld` inactive、共享机端口冲突 → 全端口绑回环 + 独立 project name；`docker compose down`（**不加 `-v`**）。

### T-05 后端工程初始化
- **目标**：FastAPI 模块化单体骨架、统一 API、日志、异常处理、测试框架。
- **前置**：T-04。
- **文件**：`app/`、`requirements` / lockfile、`tests/`、`migrations/`。
- **步骤**：Python 3.12 venv → 路由分层（catalog / versions / sources / rights / reviews / media / ingestion）→ 统一响应与错误码 → 结构化日志 → `pytest` 基线。
- **测试**：`pytest` 全绿；`/healthz`；错误码与日志格式断言；`python --version` 断言为 3.12。
- **验收**：无业务表也能启动；依赖版本锁定。
- **风险/回滚**：误用系统 Python 3.6 → CI 版本断言；骨架独立提交可 revert。
- **实测（2026-11-19）**：VM `.venv` 31 个 pytest 全绿；venv 直跑与容器两种启动方式均 `/healthz` 200（VM venv Python 3.12.11、容器 3.12.16）；`cl-dev-api-1` healthy、`58000` 仅回环、公网不可达；7 个领域路由均 501，不返回任何伪造业务数据。

### T-06 数据库模型与迁移
- **目标**：落地 10 类实体 + 跨馆通用层，明确主键、唯一性、状态流转与校验规则。
- **前置**：T-05、DATABASE_DESIGN.md 定稿。
- **文件**：`migrations/versions/*`、`app/models/`。
- **步骤**：建十实体 + `ExternalIdentifier` / `Collection` / `Tag` / `ImportBatch` / `AuditLog` → 五维状态与发布门禁约束 → Alembic 迁移。
- **测试**：upgrade / downgrade 往返；唯一约束、外键、枚举断言；一首歌多版本多来源样例写入。
- **验收**：支持 500 首目录、多录音版本、传统童谣多地区/语言/歌词版本、多贡献角色、音频/简谱/五线谱、审美评审、权利审核与发布。
- **风险/回滚**：通用层与音乐层命名冲突 → 先定映射表；downgrade 可回滚。
- **实测（2026-11-19）**：VM 隔离空库 `upgrade head → compare_metadata` 0 差异 `→ downgrade base → upgrade head` 全通过（53 CHECK / 35 FK）；13 项约束违规全部按预期拒绝；合成样例图（2 作品 / 2 文本版本 / 3 来源 / 4 贡献角色 / 录音 / 谱面 / 媒体 / 播放 / 评审 / 权利）写入成功且随临时库一并删除；`cl-dev` 已 `upgrade head`（`8d6b729f5152`），21 张表、业务表 0 行；57 个 pytest 全绿；`/healthz` 双探测 reachable、`/readyz` 200；`pg_restore -l` 列出 42 个 TABLE 条目。定型取舍见 [DATABASE_DESIGN.md §9](DATABASE_DESIGN.md)。

### T-07 媒体资产模块
- **目标**：StorageProvider 接口 + 本地适配器 + 校验和 + 权利门禁。
- **前置**：T-06。
- **文件**：`app/media/`、`var/media/`、`MEDIA_ASSET_DESIGN.md`。
- **步骤**：定义 `put/get/stat/delete/range` → 本地实现 → SHA-256 / 大小 / 时长 / 格式登记 → 关联 `rights_record_id` → 预留授权访问与 Range 播放 → 备份迁移脚本。
- **测试**：上传-读取-校验-删除往返；checksum 不一致告警；未授权资产不返回公开 URL。
- **验收**：内部研究收录不自动进公开播放目录；`object_key` 与供应商 URL 解耦。
- **风险/回滚**：不接 COS/BOS、不采购；适配器可替换，本地文件只增不删。

### T-08 前端工程初始化
- **目标**：Vue 3 + TS + Vite 骨架，复用原型视觉与交互。
- **前置**：T-04、T-05。
- **文件**：`web/`、`design-demos/music.html` / `works.html`（只读参考）。
- **步骤**：初始化工程 → 抽取原型配色/排版/卡片/筛选/详情交互为组件 → 统一 API 客户端与路由 → 前后台共享组件规范。
- **测试**：构建通过；组件测试；`validate_prototypes.py` 作视觉回归参考。
- **验收**：原型页面仍可独立打开；不推翻既有视觉方向。
- **风险/回滚**：原型只读保留；前端工程独立目录可整体移除。

### T-09 音乐馆后台 MVP
- **目标**：后台完成作品、贡献、版本、来源、权利、评审与发布门禁。
- **前置**：T-06、T-07、T-08。
- **文件**：`app/music/`、`app/reviews/`、`web/admin/`。
- **步骤**：作品 CRUD → 贡献角色 → 作品/录音/乐谱版本 → 来源证据 → 权利记录 → 审美评审 → 发布条件检查。
- **测试**：端到端用例「候选 → 完整档案 → 审核 → 发布 / 驳回」；未通过门禁的媒体不出现在公开接口。
- **验收**：操作审计可追溯；五维状态独立。
- **风险/回滚**：门禁漏判 → 公开接口集成测试卡住；功能开关可关闭。

### T-10 音乐馆前台 MVP
- **目标**：首页、分类/主题、搜索、详情、创作者、版本、乐谱、合规试听。
- **前置**：T-09。
- **文件**：`web/public/`、`README.md`。
- **步骤**：列表 / 筛选 / 搜索 → 详情与版本切换 → 来源与评审展示 → 仅对通过审核资源显示播放入口。
- **测试**：Playwright 回归；未授权资源不渲染播放按钮；移动端与控制台无错误。
- **验收**：前台与后台读同一套数据，不再有两份漂移目录。
- **风险/回滚**：误播未授权媒体 → 服务端二次校验 + feature flag 下线播放入口。

### T-11 历史数据迁移
- **目标**：按映射导入 105 / 55 / 47 / 58 / 5 / 500 首目录，产出报告并保留回滚能力。
- **前置**：T-03、T-06、T-07，门禁 C。
- **文件**：`scripts/import_*`、`docs/reports/migration-report.md`、全部源 JSON 与 500 首目录。
- **步骤**：中间层转换 → 稳定 ID 与映射 → 重复/别名检测 → 分批导入（带 `import_batch_id`）→ 数量/关联/权利/发布校验 → 报告。
- **测试**：导入前后计数一致；孤儿为 0 或全部登记；3 条缺类型已修正；219 首仍为 `bibliography_candidate`。
- **验收**：原始数据文件未被改写；可按批次回滚；500 首目录数量不缩减。
- **风险/回滚**：研究候选被误标为已授权 → 导入脚本硬断言状态；按 `import_batch_id` 回滚。

### T-12 回归验证与原型保留
- **目标**：验证新系统闭环，同时确认历史原型未被破坏。
- **前置**：T-09、T-10、T-11。
- **文件**：7 个 `validate_*.py`、`design-demos/`（只读保留）。
- **步骤**：跑后端/前端测试 → 跑 7 个原型回归 → 核对 105 条页面、58/63 试听、5 官方预览 → 记录 PASS 清单 → 复跑一次备份恢复演练。
- **测试**：全部测试通过；控制台/网络无错误。
- **验收**：新系统通过验证前不删除任何旧页面；文档与实测数字一致。
- **风险/回滚**：保留旧原型即为最终兜底；新系统可整体停用回退到静态页面。

---

## 4. 全局验收标准

- 数据迁移可重复执行，且可按批次回滚。
- 核心逻辑有自动化测试；错误处理和日志可定位。
- 权限与版权发布门禁有效，未授权媒体不进公开层。
- 文档与示例配置同步更新；数据、媒体、来源之间引用完整可验证。
- 500 首研究目录、100 首精选候选、105 条原型目录三层口径清晰，不互相冒充。
- 历史静态原型在新系统验收前完整保留。

## 5. 依赖顺序

```text
T-01 → T-02 → T-03 ─┐
         └→ T-04 → T-05 → T-06 ─┬→ T-07 ─┐
                    └→ T-08 ─────┴→ T-09 → T-10 → T-11 → T-12
```

T-11 另依赖门禁 C；T-12 之后才进入 Phase 5（故事馆 / 诗词馆）。

## 6. T-07 实测记录（2026-11-19）

- 提交 `e4ae3dd`（22 文件 / +1762 行）；GitHub main 与 VM `/data/childhood-library` 均同步到该提交，工作区干净。
- 本地静态校验：`verify_compose.py` / `verify_t05.py` / `verify_t06.py` / `verify_t07.py` / `verify_docs.py` 全绿；143 条本地链接 0 断、0 密钥、9 个受保护文件检查通过。
- VM 实机：`git pull --ff-only` 到 `e4ae3dd`；两段 overlay `config -q` PASS；`docker compose build api` + `up -d --wait` 后三服务 healthy；104 个 pytest 全绿；`alembic current` 仍为 `8d6b729f5152 (head)`。
- 媒体完整性：`scripts/media_integrity.py --root var/media` → 85 条清单 / 85 校验通过 / 0 失败 / 0 意外文件；`api` 容器内可读 85 个文件且写入被 `Read-only file system` 拒绝。
- 隔离库演练 `cl_t07_media`：put/get/stat/checksum/range/delete 往返、篡改告警、object_key 沙箱、只读挂载守卫、`rights_record_id` 关联、未授权 `public_url` 拒绝、删除留审计；库随演练删除，`cl-dev` 业务表仍 0 行。
- ⚠️ 踩坑：① `.gitignore` 的 `media/` 会匹配任意层级同名目录，导致 `app/media/` 整个被忽略，已收窄为 `/media/`；② `up -d` 只重建容器不重建镜像，新路由曾返回 404，必须先 `build api`；③ `app/models/__init__.py` 会注册全部 ORM，故 `app/media/__init__.py` 改为惰性导出，保证 `app.media.integrity` 这类纯 Python 路径不被 SQLAlchemy 拖住。
- ⚠️ 仍待确认：门禁 B / 门禁 C 未变；媒体业务 CRUD 端点属 T-09/T-10；云端适配器属 M1。

## 7. T-08 实测记录（2026-11-19）

- 工程：`web/` Vue 3.5.45 + TypeScript 5.9.3 + Vite 6.4.6 + Vitest 3.2.7；`package.json` 10 个顶层依赖精确锁，`package-lock.json` lockfileVersion 3 / 218 个包。全新空目录 `npm ci` 重装 167 包后 lock 文件哈希不变、`vue=3.5.45`。
- 本地验证：`vue-tsc --noEmit` + `vite build` 通过（51 模块，105.34 kB JS / 7.33 kB CSS）；`vitest run` **18/18 全绿**；`_audit_main/verify_t08.py` **107 项静态检查 PASSED**（T-08 交付时口径；本轮新增 5 项 Node 基线检查后为 112 项，见下方补记）。
- 视觉回归：`design-demos/validate_prototypes.py` 对 dir-1/2/3.html **3/3 PASS**（筛选、搜索、空结果/重置、dialog/Escape、移动菜单、溢出、控制台错误）；原型目录 `git status` 为空，`tokens.css` 的 7 个核心色值与 music.html / works.html 逐值一致。
- 契约对齐：`web/src/api/types.ts` 的 7 个域名与 9 个错误码由静态脚本对照 `app/api/v1/router.py` L6-L7、`app/core/errors.py` L17-L26 逐项比对；API 客户端默认相对 `/api/v1`，不硬编码主机；7 域清单端点仍 501，占位页显式呈现而不造数据。
- 边界：`design-demos/` 原型、`app/` 后端与 `deploy/` 下的 Compose/备份配置全部未改动（`deploy/README.md` 仅同步状态文字）；不导入业务数据；不启动 nginx / Compose `web` 服务；不引入 UI 框架或状态管理库。
- ⚠️ 踩坑：① Windows PowerShell 5.1 执行策略禁止 `npm.ps1`，须用 `npm.cmd`；② vitest 会把 `import.meta.url` 重写为非 file 协议，`fileURLToPath` 不可用，测试改用 `process.cwd()` 解析；③ 在已有 `node_modules` 上跑 `npm ci` 会触发沙箱批量删除保护（57 个 `.bin` 文件 > 50 阈值）导致半成品安装，改用**全新空目录**复制 `package.json` + `package-lock.json` 后 `npm ci` 验证锁可重现。
- **VM 补记（2026-11-20）**：SSH 通道重新授权后，VM `/data/childhood-library` 已 `git pull --ff-only` 到 `137cf68`；`web/` 实测 Node v22.12.0 / npm 10.9.0、`npm ci` 装 167 包、`vue-tsc --noEmit` + `vite build` 通过（51 模块 / 105.34 kB JS / 7.33 kB CSS）、`vitest run` **18/18 全绿**；`node_modules/` 与 `dist/` 均被忽略，工作区干净。当时 `npm ci` 出现两条 `EBADENGINE` 警告（`abbrev@5.0.0` / `nopt@10.0.1` 要求 Node `^22.22.2 || ^24.15.0 || >=26.0.0`，VM 为 22.12.0），构建与测试不受影响；该问题已在同日按下方「Node 版本对齐」补记闭环。
- **Node 版本对齐补记（2026-11-20）**：新增 `web/.nvmrc` 固定工程基线 `22.22.2`；**不改 VM 系统默认 Node**（`/usr/local/bin/node` → `/usr/local/node22` 是共享 CodeBuddy 工具链，含 `cbc` / `agent-browser` 且有运行中进程），改为在仓库外 `/data/cl-node/` 安装官方 `node-v22.22.2-linux-x64`，用 `SHASUMS256.txt` 校验 `node-v22.22.2-linux-x64.tar.xz: OK`，仅在 childhood-library 复跑会话中显式 `export PATH=/data/cl-node/node-v22.22.2-linux-x64/bin:$PATH`。复跑结果：Node v22.22.2 / npm 10.9.7、`npm ci` 装 167 包且 `EBADENGINE` 警告 **0 条**、`vite build` 51 模块（105.34 kB JS / 7.33 kB CSS）、`vitest run` **18/18 全绿**、`package-lock.json` SHA-256 前后同为 `88ac1ceb…`、`git status` 0 行、`node_modules/` 与 `dist/` 仍被忽略；系统默认仍为 v22.12.0 / npm 10.9.0。本轮不改 `package.json` / `package-lock.json`、不改原型/后端/Compose、不新增端口或容器。
- ⚠️ 仍待确认：门禁 B / 门禁 C 未变；`web` / `nginx` 服务定义与业务页面属 T-09/T-10。
