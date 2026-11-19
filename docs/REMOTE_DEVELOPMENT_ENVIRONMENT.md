# 远程开发环境建设方案 · REMOTE_DEVELOPMENT_ENVIRONMENT

- 文档状态：Design Proposal（**方案已确认，环境尚未在 VM 启用**）
- 版本：v0.1
- 日期：2026-11-19
- 依据：Phase 0 远程 VM 只读实机探测（命令编号 C1–C4）、[PROJECT_AUDIT.md §6](PROJECT_AUDIT.md)、[ARCHITECTURE.md §5](ARCHITECTURE.md)

> **安全约定**：SSH 主机、端口、账号、密钥路径、数据库口令与云密钥属于敏感配置，只存放在本机 `~/.ssh/config` 与 VM 上的 `.env`（已由 `.gitignore` 忽略），**不写入本仓库任何文档或代码**。本文只用「远程主机」指代。

---

## 1. 实机勘察结果（只读）

| 项 | 实测 | 命令 |
|---|---|---|
| 系统 | TencentOS Server 3.2（el8.2 兼容），内核 `5.4.241-1-tlinux4-0023.11` x86_64 | [C1][C2] |
| CPU | 8 核；负载 0.17 / 0.25 / 0.23，已运行 92 天 | [C1][C3] |
| 内存 | 15 Gi 总 / 4.4 Gi 已用 / 10 Gi 可用 / **Swap 0** | [C1] |
| 磁盘 | `/` 99 G，31 G 已用，**65 G 可用（32%）**；inode 使用 5% | [C1][C2] |
| 出站网络 | GitHub 200、PyPI 200、npm registry 200 | [C3] |
| Git | 2.43.7 | [C1] |
| Docker / Compose | 26.1.3 / v2.27.0 | [C1][C4] |
| Node / npm | v22.12.0 / 10.9.0 | [C1] |
| Python | 系统 `python3` = **3.6.8（EOL）**；另有 `python3.11`、`python3.12.11` | [C1][C2][C4] |
| PostgreSQL | **未安装**（无 `psql/postgres/initdb`）；已有 `pgvector/pgvector:pg16` 镜像 438 MB | [C2] |
| 现有容器 | 运行中：TiDB v8.5.0（pd / server / tikv）、anydev-agent；退出：db-agent-ollama、db-agent-pg | [C2] |
| 已占用端口 | 36000 / 56000(sshd)、4000、10080、8080、8090、2379、8765/8766/8767、8899、9110、42222 等 | [C2][C4] |
| 空闲目标端口 | 5432 / 8000 / 8001 / 5173 / 3000 / 6379 / 8081 / 9000 未监听 | [C4] |
| 防火墙 | `firewalld` **inactive** | [C3] |
| 目录 | `/data/workspace` 为空；`/data` 下已有 `BinlogLens`、`dba-forum`、`ticket-kb` 等其它项目；**无 childhood-library 目录** | [C2][C4] |
| 时间 | CST，与本地一致 | [C3] |

命令清单：[C1] `uname -srm; nproc; free -h; df -h /; command -v …; --version`；[C2] `cat /etc/os-release; ls /usr/bin/python3*; docker ps -a; docker images; ss -lntp; df -i /`；[C3] `curl -w %{http_code} <github/pypi/npm>; systemctl is-active firewalld; date; uptime`；[C4] `ss -lntp; ls -la /data/workspace; python3.12 --version; docker compose version`。全部为只读，未安装软件、未启停容器、未写 VM 文件。

## 2. 必须遵守的约束

| # | 约束 | 原因 |
|---|---|---|
| P0-1 | 显式使用 `python3.12 -m venv` 或容器 Python，**禁止修改系统默认 `python3`** | 系统 3.6.8 已 EOL，无法承载现代 FastAPI / Pydantic v2 [C1] |
| P0-2 | 数据库、管理后台、管理工具端口一律绑定 `127.0.0.1`，仅 Nginx 对外 | `firewalld` inactive，`0.0.0.0` 监听可能直达公网 [C3] |
| P0-3 | 使用独立目录、独立 Compose project name、独立 volume、独立端口段 | 共享机已有其它项目容器，不得清理或复用 [C2] |
| P0-4 | PostgreSQL 以容器启动，不安装系统服务；不改动现有容器 | 未安装 psql；已有 pg16 镜像 [C2] |
| P0-5 | 数据库与媒体分别持久化，定期备份并做恢复演练 | 用户要求；无 swap 需控制内存上限 |
| P0-6 | `.env` 与 SSH 参数不入库 | `.gitignore` 已忽略 `.env/.env.*`，`.env.example` 只保留占位 |
| P0-7 | 暂不接 COS/BOS、不启用 CDN、不采购大容量资源包 | [MEDIA_ASSET_DESIGN.md L14-L18](MEDIA_ASSET_DESIGN.md) |

## 3. 目录结构（VM）

```text
/data/childhood-library/                 # 独立目录，避开 /data 下已有项目
├── app/                                 # 模块化单体后端
│   ├── common/                          # 跨馆通用：work / contribution / tag / source / review
│   ├── music/                           # 音乐馆独立领域层
│   └── catalog/ versions/ sources/ rights/ reviews/ media/ ingestion/
├── web/                                 # Vue 前台 + 编辑后台
├── migrations/                          # Alembic
├── scripts/                             # 导入、导出、校验、备份、恢复
├── tests/
├── design-demos/                        # 历史原型（只读保留，直到新系统验收）
├── docs/
├── var/
│   ├── media/                           # 本地媒体持久化（独立 volume）
│   ├── backups/                         # 数据库备份
│   └── logs/                            # 应用与审计日志
├── deploy/                              # Compose 配置骨架与备份/恢复脚本
│   ├── docker-compose.yml               # 基础服务（db）
│   ├── compose.dev.yml                  # development overlay
│   ├── compose.test.yml                 # testing overlay
│   ├── backup.sh / restore.sh           # 备份与恢复
│   └── README.md                        # 运维命令
└── .env                                 # 不入库（模板见 .env.example）
```

## 4. 三环境分离

| 环境 | 用途 | 隔离方式 |
|---|---|---|
| `development` | 日常开发、编辑端试听 | 独立 Compose project `cl-dev`、独立 DB schema、独立媒体目录、端口绑回环 |
| `testing` | 自动化测试、迁移与恢复演练 | 独立 project `cl-test`、独立库与 volume、**禁止指向开发库** |
| `production` | 后续正式服务 | 暂不启用；启用前单独评审端口、备份、权限与发布门禁 |

三套环境不共用数据库、媒体目录或 `.env`；配置通过 `compose.<env>.yml` 叠加，不复制整份 Compose。

## 5. 服务与端口策略

| 服务 | 绑定 | 持久化 | 说明 |
|---|---|---|---|
| `db`（PostgreSQL 16） | `127.0.0.1:<未占用>` | `var/db` volume | 账号口令走 `.env`，**端口不暴露公网** |
| `api`（FastAPI） | `127.0.0.1:<未占用>` | — | `/healthz`、结构化日志、统一异常处理 |
| `web`（Vite / 构建产物） | `127.0.0.1:<未占用>` | — | 由 Nginx 反向代理 |
| `nginx` | 对外唯一入口 | 配置只读挂载 | 管理后台加访问控制 |
| `adminer` 等管理工具 | 默认**不启用** | — | 需要时临时、仅回环、用完停止 |

端口在启用前**必须再跑一次 `ss -lntp`** 复核，因为共享机状态会变化；不要硬编码已占用的 8080 / 8090 / 4000 / 10080 / 2379。

## 6. 敏感配置

- `.env.example` 已含 `APP_ENV`、`DATABASE_URL`、`REDIS_URL`、`S3_*`、`AI_*` 等占位项，需补齐 `POSTGRES_USER` / `POSTGRES_PASSWORD`、`CL_DEV_DB_NAME` / `CL_TEST_DB_NAME`、`MEDIA_ROOT` / `TEST_MEDIA_ROOT`、`BACKUP_ROOT` 与端口变量。数据库名由环境 overlay 决定，不设全局 `POSTGRES_DB`，避免开发与测试库名漂移。
- `.env` 只放**仓库根**。Compose v2 默认从第一个 `-f` 文件所在目录（`deploy/`）加载 `.env`，因此所有 Compose 命令必须带 `--project-directory .`；漏掉会报 `required variable POSTGRES_USER is missing a value`。详见 `deploy/README.md`。
- `.gitignore` 已忽略 `.env`、`.env.*`（保留 `.env.example`）；提交前做密钥扫描。
- SSH 别名、主机、端口、账号、`IdentityFile` 路径只保留在本机 `~/.ssh/config`，不写入文档、脚本或提交信息。
- 对象存储密钥位保持为空；本阶段不接云存储。

## 7. 运维说明（部署 / 启动 / 停止 / 日志 / 备份 / 恢复）

以下为**命令形态示意**，完整可执行命令见 `deploy/README.md`；T-04 已按此表在 VM 落地并完成备份 / 恢复演练。

| 动作 | 命令形态 |
|---|---|
| 备份本地项目（已执行） | 完整复制到仓库外备份目录，含 `.git` 与被忽略媒体；记录文件数与字节数 |
| 部署 | `git clone` → 仓库根 `cp .env.example .env` 并填值（`chmod 600`）→ `python3.12 -m venv .venv` → `docker compose --project-directory . -p cl-dev -f deploy/docker-compose.yml -f deploy/compose.dev.yml up -d`（完整命令见 `deploy/README.md`） |
| 启动 / 停止 | `docker compose … up -d` / `docker compose … down`（**不带 `-v`，避免删卷**） |
| 日志查看 | `docker compose logs -f api db`；应用日志落 `var/logs`，含请求 ID、错误码、审计事件 |
| 状态检查 | `docker compose ps`、`curl /healthz`、数据库连接探测、`df -h` 与媒体目录水位 |
| 数据库备份 | 定时 `pg_dump -Fc` 到 `var/backups/<timestamp>.dump`，同时写 SHA-256 校验文件；保留周期与异地副本待定 |
| 媒体备份 | `rsync` / 快照到独立备份卷，逐文件比对 checksum，只增不删 |
| 恢复 | 新建空库 → `pg_restore` → 跑迁移 → 校验数量与关联 → 媒体按 checksum 比对；**恢复演练先在 `testing` 环境做** |
| 自动化测试 | 后端 `pytest`、前端组件测试、现有 7 个 `validate_*.py` 作为原型回归基线 |
| 版本锁定 | 依赖写入 lockfile，保留离线清单；出站网络可用不代表可以不锁版本 |

## 8. 启用前的检查清单

- [x] 再次 `ss -lntp` 复核端口占用（T-04 启用前已复核，`55432` / `55433` / `58000` 未占用）
- [x] 确认 `/data/childhood-library` 无同名目录冲突
- [ ] ⚠️ 磁盘余量 ≥ 20 G：`/data` 实测仅 **14 G** 可用，未达标；本阶段（代码 + venv + 空库）够用，**迁移 85 个媒体文件前需扩容评估**
- [x] 确认不会与 TiDB / anydev-agent 容器争用端口与 volume
- [x] `.env` 已填写且权限受限（`600`）
- [x] `python3.12 --version` 与 venv 可用（3.12.11）
- [x] 备份/恢复演练在 `testing` 通过
- [x] 数据库端口从公网不可达（`127.0.0.1` 绑定 + 公网 IP 探测失败）
- [x] 未启用云存储 / CDN / 管理工具

> **当前状态（2026-11-19，T-04 已落地）**：VM `/data/childhood-library` 已 clone 到 `38d4d8d`；仓库根 `.env`（`600`）、`python3.12` venv、`var/` 均建立且被忽略。`cl-dev`（`127.0.0.1:55432`）运行中 healthy，`cl-test` 备份 / 恢复演练通过后已停止并保留卷。`api` / `web` / `nginx` 与业务表仍属 T-05+。
>
> ⚠️ 门禁 B（端口 / 备份策略正式确认）与 `/data` 容量缺口仍待处理；当前端口按 `.env.example` 默认值落地。
