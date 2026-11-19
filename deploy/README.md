# deploy/ — 配置骨架与运维说明

> **状态：`cl-dev` 的 `db` + `api` 均已在远程 VM 启用（healthy、仅回环），T-06 的 20 张表已完成迁移（业务表为空），`cl-test` 备份恢复演练通过。** 本目录不包含任何密钥、主机地址或账号信息。
> 环境实测与完整方案见 [REMOTE_DEVELOPMENT_ENVIRONMENT.md](../docs/REMOTE_DEVELOPMENT_ENVIRONMENT.md)。

## 文件

| 文件 | 用途 |
|---|---|
| `docker-compose.yml` | 基础服务：PostgreSQL 16（`pgvector/pgvector:pg16`）、账号口令、健康检查、日志；**必须配合 overlay 使用** |
| `compose.dev.yml` | 开发环境 overlay：独占数据库名、宿主端口、两个卷 |
| `compose.test.yml` | 测试环境 overlay：独立库 / 端口 / 卷，用于迁移与恢复演练 |
| `backup.sh` | `pg_dump` + SHA-256 sidecar + 媒体 checksum 复制 |
| `restore.sh` | 校验 dump checksum 后 `pg_restore` 到指定 project |
| 仓库根 `.env.example` | 占位模板；实际 `.env` 已被 `.gitignore` 忽略 |
| 仓库根 `Dockerfile` / `.dockerignore` | api 镜像（Python 3.12-slim、非 root）；构建上下文含 `app/` / `migrations/` / `alembic.ini` |
| 仓库根 `alembic.ini` | T-06 Alembic 入口；连接串只从 `DATABASE_URL` 读取 |
| 仓库根 `app/models/` / `migrations/versions/` | T-06 ORM 模型与初始迁移 |
| 仓库根 `requirements.lock` | 36 个包的精确版本锁，镜像构建只认它 |

`api` 服务已在 `compose.dev.yml` 定义（T-05），容器内 `DATABASE_URL` 由 `POSTGRES_USER` / `POSTGRES_PASSWORD` / `CL_DEV_DB_NAME` 拼成 `db:5432`（宿主机 venv 仍用 `.env` 里的 `127.0.0.1:55432`）。`cl-test` 仍是纯数据库 project；`web` / `nginx` 留到 T-08。七个业务路由当前全部返回 501，不代表业务已实现。

## Compose 合并契约（改动配置前必读）

Compose 多文件合并时，`environment` 这类映射按 key **覆盖**，但 `ports` / `volumes` 这类**序列是追加**，不是覆盖。因此：

- `docker-compose.yml`（base）**不声明** `ports`、`volumes`、`POSTGRES_DB`；
- `compose.dev.yml` / `compose.test.yml` 各自**独占**这三类值；
- 若把 `ports` 或 `volumes` 加回 base，会出现同一宿主端口重复绑定，以及两个卷同时挂到 `/var/lib/postgresql/data`。

健康检查用 `$$POSTGRES_USER` / `$$POSTGRES_DB`（双美元符转义 Compose 插值），由容器内 shell 展开，因此不受 host `.env` 里的库名影响。`backup.sh` / `restore.sh` 也直接从**运行中的容器**读取 `POSTGRES_USER` / `POSTGRES_DB`，不 source `.env`，避免口令含 shell 元字符时出错、也避免库名与 overlay 漂移。

## `.env` 加载规则（易踩坑）

**Compose v2 默认从第一个 `-f` 文件所在目录（这里是 `deploy/`）加载 `.env`，不是 shell 的当前目录。** 因此：

- `.env` 必须放在**仓库根**，`chmod 600`；`deploy/` 下不要放 `.env`；
- **所有** `docker compose` 命令都必须带 `--project-directory .`；
- 这个选项同时让 `${MEDIA_ROOT:-./var/media}` 一类相对卷路径基于仓库根，而不是 `deploy/var/media`；
- 漏掉该选项时，`config` 会报 `required variable POSTGRES_USER is missing a value`。

`backup.sh` / `restore.sh` 里的 Compose 数组已内置该选项，调用方不用重复传。

## 前置检查（每次启用前）

```bash
ss -lntp                 # 复核端口占用，共享机状态会变化
df -h /                  # 确认磁盘余量
python3.12 --version     # 必须显式使用 3.12，系统 python3 是 3.6.8
docker compose version   # v2.27.0
```

- 不要占用已使用的 8080 / 8090 / 4000 / 10080 / 2379 等端口。
- 不要清理或复用已有 TiDB / anydev-agent 容器。
- 确认 `.env` 权限受限，且不含任何真实密钥被提交。

## 常用命令（从仓库根执行）

```bash
# 配置
cp .env.example .env && vi .env       # 填 POSTGRES_USER / POSTGRES_PASSWORD / CL_*_DB_NAME / 端口 / MEDIA_ROOT
chmod 600 .env
python3.12 -m venv .venv && . .venv/bin/activate

# 两个环境的统一入口（--project-directory . 不可省略）
DEV="docker compose --project-directory . -p cl-dev  -f deploy/docker-compose.yml -f deploy/compose.dev.yml"
TEST="docker compose --project-directory . -p cl-test -f deploy/docker-compose.yml -f deploy/compose.test.yml"

# 配置校验（先做，不启动容器；-q 不回显口令）
$DEV config -q && $TEST config -q

# 构建 / 启动 / 停止（注意：down 不加 -v，避免删卷）
$DEV build api
$DEV up -d --wait
$DEV down

# 日志与状态（必须带同一组 -f / -p / --project-directory）
$DEV logs -f api db
$DEV ps
curl -fsS http://127.0.0.1:${CL_API_PORT:-58000}/healthz
curl -fsS http://127.0.0.1:${CL_API_PORT:-58000}/readyz   # SQL 不可达时 503

# 数据库迁移（宿主机 venv；连接串读仓库根 .env，不写入 alembic.ini）
.venv/bin/alembic -c alembic.ini current
.venv/bin/alembic -c alembic.ini upgrade head
.venv/bin/alembic -c alembic.ini downgrade base   # 仅演练环境，down 会删全部表

# 测试环境（独立 project，绝不指向开发库）
$TEST up -d

# 备份 / 恢复（脚本从运行中的容器读取库名与账号）
CL_PROJECT=cl-dev ./deploy/backup.sh
CL_PROJECT=cl-test CL_COMPOSE_OVERLAY=deploy/compose.test.yml \
  CL_MEDIA_ROOT=./var/media-test ./deploy/backup.sh
CL_PROJECT=cl-test CL_COMPOSE_OVERLAY=deploy/compose.test.yml \
  ./deploy/restore.sh var/backups/db-cl-dev-YYYYMMDD-HHMMSS.dump

# 自动化测试
pytest
```

> 备份/恢复不需要手动 `source .env`；Compose 通过 `--project-directory .` 自己读取仓库根 `.env`。`CL_MEDIA_ROOT` 只影响附带的媒体复制，数据库部分不受影响。`var/` 与 `*.dump` 已被 `.gitignore` 忽略。

## 安全约定

1. 数据库端口、管理后台与任何管理工具**只绑定 `127.0.0.1`**；VM 的 `firewalld` 为 inactive，`0.0.0.0` 监听可能直达公网。
2. 只有 Nginx 作为对外入口；启用前需单独评审访问控制。
3. `.env`、SSH 参数、数据库口令、对象存储密钥不写入文档、代码或提交信息。
4. 数据库与媒体使用独立 volume；备份同时校验 checksum；恢复演练先在 `cl-test` 完成。
5. 本阶段不启用 COS / BOS / CDN，不采购云资源。

## 当前状态与未完成

**已完成（2026-11-19，VM）**

- `/data/childhood-library` 已 clone；仓库根 `.env`（`600`）、`python3.12` venv、`var/` 均已建立且被 `.gitignore` 忽略。
- `cl-dev`（`127.0.0.1:55432`，`childhood_library_dev`）运行中且 healthy；公网 IP 探测不可达。
- `cl-test`（`127.0.0.1:55433`，`childhood_library_test`）备份 / 恢复演练通过，演练后容器已停止、卷保留。
- 已有 TiDB / anydev-agent 容器未受影响。
- T-05：`api` 容器（Python 3.12-slim、非 root）healthy，`127.0.0.1:58000` 仅回环、公网 IP 探测不可达；`/healthz` 200、占位域 501、JSON 访问日志含 request_id / status_code / duration_ms。
- T-05：VM `.venv` 下 31 个 pytest 用例全绿；`requirements.lock` 的 29 个包两次安装结果一致。
- T-06：`alembic upgrade head` 已在 `cl-dev` 完成（20 张业务表 + `alembic_version`，业务表 0 行）；隔离空库 `upgrade → downgrade → upgrade` 往返与 `compare_metadata` 0 差异通过；13 项约束违规全部按预期拒绝。
- T-06：VM 57 个 pytest 全绿；`/healthz` 的 `database_tcp` / `database_sql` 均 reachable、`/readyz` 200；`pg_dump` + SHA-256 sidecar 仍可 dump 新 schema（`pg_restore -l` 42 个 TABLE 条目）。

**未完成 / 待确认**

- `web` / `nginx` 服务定义、媒体存储适配器与业务回归测试尚未落地（T-07 / T-08+）；数据库迁移与业务表已由 T-06 建好，但**尚未导入任何数据**、发布门禁尚未接入发布命令（T-09）。
- ⚠️ 门禁 B 正式确认仍待：端口 `55432` / `55433` / `58000` 目前按 `.env.example` 默认值落地；备份保留周期、异地副本策略未定。
- ⚠️ `/data` 实测可用 14 G，低于检查清单的 ≥ 20 G；本阶段只放代码 + venv + 空库，迁移 85 个媒体文件前需扩容评估。
