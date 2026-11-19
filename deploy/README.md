# deploy/ — 配置骨架与运维说明

> **状态：源码骨架已入库，远程 VM 尚未启用。** 本目录不包含任何密钥、主机地址或账号信息。
> 环境实测与完整方案见 [REMOTE_DEVELOPMENT_ENVIRONMENT.md](../docs/REMOTE_DEVELOPMENT_ENVIRONMENT.md)。

## 文件

| 文件 | 用途 |
|---|---|
| `docker-compose.yml` | 基础服务：PostgreSQL 16（`pgvector/pgvector:pg16`），端口仅绑定 `127.0.0.1` |
| `compose.dev.yml` | 开发环境 overlay，独立 project / volume / 媒体目录 |
| `compose.test.yml` | 测试环境 overlay，独立库与卷，用于迁移与恢复演练 |
| `backup.sh` | `pg_dump` + SHA-256 校验文件 + 媒体 checksum 复制 |
| `restore.sh` | `pg_restore` 到指定 project，先校验 checksum |
| 仓库根 `.env.example` | 占位模板；实际 `.env` 已被 `.gitignore` 忽略 |

`api` / `web` / `nginx` 服务在 T-05 / T-08 工程初始化后加入；当前只定义数据库，避免半成品服务被误启动。

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
cp .env.example .env && vi .env       # 填 POSTGRES_* / 端口 / MEDIA_ROOT / BACKUP_ROOT
python3.12 -m venv .venv && . .venv/bin/activate

# 启动 / 停止（注意：down 不加 -v，避免删卷）
docker compose -p cl-dev -f deploy/docker-compose.yml -f deploy/compose.dev.yml up -d
docker compose -p cl-dev -f deploy/docker-compose.yml -f deploy/compose.dev.yml down

# 日志与状态
docker compose -p cl-dev logs -f db
docker compose -p cl-dev ps
curl -fsS http://127.0.0.1:${CL_API_PORT:-58000}/healthz   # T-05 后才可用

# 测试环境（独立 project，绝不指向开发库）
docker compose -p cl-test -f deploy/docker-compose.yml -f deploy/compose.test.yml up -d

# 备份 / 恢复
CL_PROJECT=cl-dev bash deploy/backup.sh
CL_PROJECT=cl-test CL_COMPOSE_OVERLAY=deploy/compose.test.yml bash deploy/restore.sh var/backups/db-cl-dev-YYYYMMDD-HHMMSS.dump

# 自动化测试
pytest
```

## 安全约定

1. 数据库端口、管理后台与任何管理工具**只绑定 `127.0.0.1`**；VM 的 `firewalld` 为 inactive，`0.0.0.0` 监听可能直达公网。
2. 只有 Nginx 作为对外入口；启用前需单独评审访问控制。
3. `.env`、SSH 参数、数据库口令、对象存储密钥不写入文档、代码或提交信息。
4. 数据库与媒体使用独立 volume；备份同时校验 checksum；恢复演练先在 `cl-test` 完成。
5. 本阶段不启用 COS / BOS / CDN，不采购云资源。

## 当前未完成

- VM 上未创建 `/data/childhood-library` 目录，未启动任何容器，未写入任何文件。
- `api` / `web` / `nginx` 服务定义、健康检查端点、迁移执行与自动化测试尚未落地。
- 端口值、备份保留周期、异地副本策略待门禁 B 确认后定稿。
