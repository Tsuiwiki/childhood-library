# app/ — FastAPI 模块化单体（T-05 骨架 + T-06 数据层 + T-07 媒体能力）

> **状态：T-06 已落地 20 张表的关系模型、Alembic 迁移、发布门禁规则与 SQL 就绪探针；T-07 已落地 `app/media/` 能力层与 `api` 容器的 `var/media:ro` 正式挂载。`cl-dev` 已完成迁移但所有业务表为空；7 个业务域的清单端点仍返回 501，不产生任何示例业务数据。**

## 目录

| 路径 | 职责 |
| --- | --- |
| `main.py` | `create_app()` 工厂，装配配置 / 日志 / 中间件 / 异常处理器 / 路由 |
| `core/config.py` | `Settings`（读仓库根 `.env`），`safe_summary()` 不含 `DATABASE_URL` / 任何密钥 |
| `core/runtime.py` | **Python 3.12 运行时断言**，防止误用系统 3.6.8 |
| `core/errors.py` | `ErrorCode` / `AppError` / 全局异常处理器（422 / 404 / 405 / 501 / 503 / 500） |
| `core/responses.py`、`schemas/common.py` | 统一响应 envelope `{code, message, data, request_id}` |
| `core/context.py`、`core/middleware.py` | 请求 ID（contextvar + `X-Request-ID`）与结构化访问日志 |
| `core/logging.py` | JSON 日志（stdout + 可选轮转文件），字段含 request_id / status_code / duration_ms / error_code |
| `domain/status.py` | **五维状态契约**（纯枚举）：研究 / 权利 / 质量 / 访问方式 / 发布状态互相独立 |
| `domain/publication_gate.py` | T-06 发布门禁 5 条规则（跨对象部分），T-09 接入发布命令 |
| `models/` | T-06 ORM：10 类核心实体 + 10 张支撑表；`VARCHAR + CHECK` 枚举、UUID 主键、JSONB 扩展字段 |
| `media/` | T-07：StorageProvider 接口、本地适配器、签名/时长探测、SHA-256 完整性、三级权利门禁、Range 响应与元数据登记；包初始化惰性 |
| `db/probe.py`、`db/session.py` | 短超时 SQL 就绪探针（延迟导入 SQLAlchemy）/ Engine 与 Session 工厂 |
| `api/v1/` | `health` / `readyz` + 7 个领域路由；`_skeleton.py` 生成占位路由 |
| `../migrations/`、`../alembic.ini` | Alembic 配置与初始迁移 `8d6b729f5152` |
| `../tests/`、`../pytest.ini` | pytest 基线（VM 57 个用例） |

## 路由

```
GET  /                                 服务元信息
GET  /healthz                          应用存活检查（始终 200；依赖状态仅为信息项）
GET  /readyz                           严格就绪检查（SQL 不可达 / 未启用时 503）
GET  /api/openapi.json                 OpenAPI
GET  /api/docs                          Swagger UI（production 关闭）
GET  /api/v1/{catalog,versions,sources,rights,reviews,media,ingestion}
                                       占位：501 NOT_IMPLEMENTED，data.planned_from = post-T-06
GET  /api/v1/media/capabilities        T-07 只读能力状态（不返回任何 URL）
```

七个领域全部显式返回 **501**，不返回任何伪造的示例数据。`limit` 参数已接入校验（1–100）。

`/healthz` 的 `checks.database_tcp` / `checks.database_sql` 只是信息项，依赖未就绪不会把健康进程变成 500（避免数据库冷启动时容器反复重启）；`/readyz` 才是可能返回 503 的严格探针。两者都不回显连接串。

## 错误码

| code | HTTP | 场景 |
| --- | --- | --- |
| `OK` | 200 | 成功 |
| `VALIDATION_ERROR` | 422 | 请求参数校验失败 |
| `NOT_FOUND` | 404 | 路由不存在 |
| `METHOD_NOT_ALLOWED` | 405 | 方法不允许 |
| `NOT_IMPLEMENTED` | 501 | 占位业务域 |
| `FORBIDDEN` | 403 | 媒体访问未通过权利门禁 |
| `HTTP_ERROR` | 400 | 其它 HTTP 错误 |
| `NOT_READY` | 503 | `/readyz` 依赖未就绪 |
| `INTERNAL_ERROR` | 500 | 未捕获异常（堆栈只进日志，不返回客户端） |

错误响应带 `X-Error-Code` 头；所有响应带 `X-Request-ID` 头，可透传上游指定值。

## 数据层要点

- 五维状态是 `works` 上**五个独立列 + 各自 CHECK**，不是单一审核 flag；对象级权利另走 `rights_records`。
- 版本号、录音版本、乐谱版本、来源证据、媒体资产、播放入口是一等实体，不用 JSON 字段平移。
- `lyrics_status = no_lyric_applicable` 是**已定性结论**：必须有 `verdict_note`，且 CHECK 禁止同时存歌词文本；有歌词文本必须关联 `SourceRecord`。
- 发布门禁：单表部分由 CHECK 保证，跨对象部分由 `publication_gate.py` 判断；研究状态不参与门禁。
- 初始迁移可 `downgrade base` 完整回滚；迁移与 ORM 元数据比对 0 差异。定型取舍见 [DATABASE_DESIGN.md §9](../docs/DATABASE_DESIGN.md)。

## 运行（VM，Python 3.12）

```bash
python3.12 -m venv .venv && . .venv/bin/activate
pip install -r requirements.lock
.venv/bin/alembic -c alembic.ini upgrade head
uvicorn app.main:create_app --factory --host 127.0.0.1 --port 58000
pytest
```

容器内由 `deploy/compose.dev.yml` 的 `api` 服务启动，宿主端口只绑 `127.0.0.1:${CL_API_PORT:-58000}`；容器内 `DATABASE_URL` 指向 Compose 网络内的 `db:5432`。

## 边界（明确不做）

- **不导入现有 JSON 原型数据、不生成示例曲目、不虚构任何作品 / 录音 / 权利结论**；`cl-dev` 业务表为空。
- 不启用 `web` / `nginx`、Celery / Redis、对象存储或独立搜索（按 ARCHITECTURE.md §3 后续引入）。
- 发布门禁尚未接入发布命令（T-09）；StorageProvider M0 本地适配器已由 T-07 落地，但媒体业务 CRUD 端点属 T-09/T-10，云端适配器属 M1；`api` 容器只读挂载媒体，写入走宿主机管理端。
- 不把 `database_url`、口令或 `.env` 内容写进日志、响应或提交。
