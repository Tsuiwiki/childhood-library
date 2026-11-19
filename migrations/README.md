# migrations/ — Alembic 数据库迁移（T-06 已启用）

> **状态：已在 VM 启用。`cl-dev` 已 `upgrade head` 到 `8d6b729f5152`，共 20 张业务表 + `alembic_version`，业务表内 0 行数据。**

## 文件

| 路径 | 用途 |
| --- | --- |
| 仓库根 `alembic.ini` | Alembic 入口；`script_location = migrations`，**不保存连接串** |
| `env.py` | 从环境变量 / 仓库根 `.env` 读 `DATABASE_URL`，`target_metadata` 取 `app.models.Base.metadata` |
| `script.py.mako` | 版本脚本模板 |
| `versions/8d6b729f5152_initial_schema_t_06.py` | 初始迁移：20 张表、10 个索引、53 个 CHECK、35 个外键；`downgrade` 逆序删表 |

## 连接串规则

`env.py` 只读 `DATABASE_URL`（pydantic-settings；宿主机 venv 读仓库根 `.env` 的 `127.0.0.1:55432`，`api` 容器由 `compose.dev.yml` 覆盖为 `db:5432`）。**不要在 `alembic.ini`、`env.py`、版本脚本或日志里写口令**，也不要打印连接串。凭证缺失时直接报错，绝不猜测 DSN。

## 常用命令（仓库根执行）

```bash
.venv/bin/alembic -c alembic.ini current           # 当前版本
.venv/bin/alembic -c alembic.ini history           # 版本历史
.venv/bin/alembic -c alembic.ini upgrade head      # 建 / 升级到最新
.venv/bin/alembic -c alembic.ini downgrade base    # 回滚全部（会删表，仅演练环境）
```

## 已完成的验证（2026-11-19，VM）

- 隔离空库 `upgrade head → compare_metadata` **0 差异** `→ downgrade base`（只剩 `alembic_version`）`→ upgrade head` 往返通过。
- 13 项约束违规（重复键、非法枚举、越级发布、歌词缺来源、embed 越权、悬空外键等）全部按预期拒绝。
- 合成结构验证样本（多版本 / 多来源 / 多贡献角色 / 谱面 / 评审 / 权利）写入成功，样本只存在于临时库并随库删除。
- `cl-dev` 迁移后 57 个 pytest 全绿、`/readyz` 200、`pg_dump` + SHA-256 sidecar 仍可备份新 schema。

## 约束

- 迁移只能指向 `cl-dev` / `cl-test` 的独立库；**恢复演练永远先在 `cl-test` 做**，不要对生产数据执行未经演练的迁移。
- 改 ORM 模型必须与迁移同一次提交；改完重跑 `compare_metadata` 断言 0 差异。
- `downgrade` 会删除全部表结构，执行前先 `./deploy/backup.sh`。
- 本阶段不导入任何真实曲目、录音或权利结论；业务数据导入属 T-11。

依据：[DATABASE_DESIGN.md §9](../docs/DATABASE_DESIGN.md)、[DATA_MIGRATION_PLAN.md](../docs/DATA_MIGRATION_PLAN.md)、[IMPLEMENTATION_ROADMAP.md](../docs/IMPLEMENTATION_ROADMAP.md) T-06。
