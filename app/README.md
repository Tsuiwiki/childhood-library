# app/ — FastAPI 模块化单体骨架（T-05）

> **状态：T-05 骨架。** 只有工程设施与 API 契约；**没有任何业务表、迁移或业务数据**。领域模型与 Alembic 迁移从 T-06 开始。

## 目录

| 路径 | 职责 |
|---|---|
| `main.py` | `create_app()` 工厂，装配配置 / 日志 / 中间件 / 异常处理器 / 路由 |
| `core/config.py` | `Settings`（pydantic-settings，读仓库根 `.env`），`safe_summary()` 不含任何密钥 |
| `core/runtime.py` | **Python 3.12 运行时断言**，防止误用系统 3.6.8 |
| `core/errors.py` | `ErrorCode` / `AppError` / 全局异常处理器（含 422 / 404 / 405 / 500） |
| `core/responses.py`、`schemas/common.py` | 统一响应 envelope `{code, message, data, request_id}` |
| `core/context.py`、`core/middleware.py` | 请求 ID（contextvar + `X-Request-ID` 头）与结构化访问日志 |
| `core/logging.py` | JSON 日志（stdout + 可选 `var/logs/app.log` 轮转）；字段含 request_id / status_code / duration_ms / error_code |
| `domain/status.py` | **五维状态契约**（纯枚举，非 ORM）：研究 / 权利 / 质量 / 访问方式 / 发布状态互相独立 |
| `api/v1/` | `health` + 7 个领域路由；`_skeleton.py` 生成占位路由 |
| `../tests/`、`../pytest.ini` | pytest 基线 |
| `../migrations/` | T-06 起放 Alembic；当前只有说明文件 |

## 路由

```
GET  /                                 服务元信息
GET  /healthz                          应用存活检查（始终 200）
GET  /api/openapi.json                 OpenAPI
GET  /api/docs                          Swagger UI（production 关闭）
GET  /api/v1/{catalog,versions,sources,rights,reviews,media,ingestion}
                                       占位：501 NOT_IMPLEMENTED，data.planned_from = T-06
```

七个领域全部显式返回 **501**，不返回任何伪造的示例数据；`limit` 参数已接入校验（1–100），可用 `?limit=abc` 验证 422。

`/healthz` 只表示**应用进程存活**。`checks.database_tcp` 是一次短超时 TCP 探测，结果仅为信息项，不会把健康进程变成 500（避免数据库冷启动时容器反复重启）。真实 SQL readiness 属 T-06。

## 错误码

| code | HTTP | 场景 |
|---|---|---|
| `OK` | 200 | 成功 |
| `VALIDATION_ERROR` | 422 | 请求参数校验失败 |
| `NOT_FOUND` | 404 | 路由不存在 |
| `METHOD_NOT_ALLOWED` | 405 | 方法不允许 |
| `NOT_IMPLEMENTED` | 501 | T-05 占位业务域 |
| `INTERNAL_ERROR` | 500 | 未捕获异常（堆栈只进日志，不返回客户端） |

错误响应带 `X-Error-Code` 头；所有响应带 `X-Request-ID` 头，可透传上游指定值。

## 运行（VM，Python 3.12）

```bash
python3.12 -m venv .venv && . .venv/bin/activate
pip install -r requirements.lock
uvicorn app.main:create_app --factory --host 127.0.0.1 --port 58000
pytest
```

容器内由 `deploy/compose.dev.yml` 的 `api` 服务启动，宿主端口只绑 `127.0.0.1:${CL_API_PORT:-58000}`。

## 边界（明确不做）

- 不建表、不跑 Alembic、不写 ORM 模型（T-06）。
- 不导入现有 JSON 原型数据、不生成示例曲目、不虚构任何作品 / 录音 / 权利结论。
- 不启用 Celery / Redis / 对象存储 / 搜索（按 ARCHITECTURE.md §3 后续需要时再引入）。
- 不把 `database_url`、口令或 `.env` 内容写进日志、响应或提交。
