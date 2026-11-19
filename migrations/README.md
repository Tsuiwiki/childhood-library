# migrations/ — 数据库迁移（T-06 起启用）

**当前状态：目录占位，没有任何 Alembic 配置、版本脚本或业务表。**

T-05 只初始化 FastAPI 工程骨架，验收标准明确「无业务表也能启动」。数据库模型、十类领域实体、五维状态约束与发布门禁由 T-06 落地，届时在此目录引入 Alembic（`env.py` / `versions/`）并保证 `upgrade` / `downgrade` 可往返。

依据：[DATABASE_DESIGN.md](../docs/DATABASE_DESIGN.md)、[DATA_MIGRATION_PLAN.md](../docs/DATA_MIGRATION_PLAN.md)、[IMPLEMENTATION_ROADMAP.md](../docs/IMPLEMENTATION_ROADMAP.md) T-06。

> 迁移只能指向 `cl-dev` / `cl-test` 的独立库，恢复演练永远先在 `cl-test` 做；不要对生产数据执行未经演练的迁移。
