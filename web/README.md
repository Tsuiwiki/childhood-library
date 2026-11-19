# web/ — Vue 3 + TypeScript + Vite 前端工程骨架（T-08）

> **状态：T-08 只做工程初始化与视觉/契约对齐。** 本目录不含任何曲目、录音、权利结论或示例业务数据；`design-demos/` 静态原型保持只读、仍可独立打开。七个业务域的清单端点仍由 API 返回 `501 NOT_IMPLEMENTED`。

## 命令

```bash
cd web
npm ci                 # 依据 package-lock.json 精确安装
npm run typecheck      # vue-tsc --noEmit
npm run build          # typecheck + vite build
npm run test           # vitest run
npm run dev            # 127.0.0.1:55173（vite dev server）
```

本机实测：Node `v22.22.2` / npm `10.9.7`。依赖在 `package.json` 中逐个精确锁定，`package-lock.json` 为全量锁，二者都必须提交；`node_modules/`、`dist/`、`coverage/` 不入库。

## 目录

| 路径 | 说明 |
| --- | --- |
| `src/styles/tokens.css` | 视觉 token：**逐值照抄** `design-demos/music.html` L9-L15 与 `design-demos/works.html` L9-L20 的 `:root`，不重新定义色值 |
| `src/styles/base.css` | 纸纹底、字体栈、焦点态、卡片/按钮基础样式，沿用原型视觉方向 |
| `src/components/` | `ClCard` / `ClFilterBar` / `ClDetailDialog`：从原型的卡片、筛选、详情交互抽出的共享组件，前后台共用 |
| `src/api/types.ts` | API envelope、错误码、7 个域名与探针/能力端点的数据类型 |
| `src/api/client.ts` | 统一 fetch 客户端：解析 `{code,message,data,request_id}`，非 `OK` 抛 `ApiClientError`；不回显连接串、不伪造数据 |
| `src/api/endpoints.ts` | `healthz` / `readyz` / `media.capabilities` / 7 域清单端点封装 |
| `src/router/` | 首页 + 7 域占位页 + 404；占位页显式展示 501，不用假数据兜底 |
| `tests/` | Vitest：API 客户端、组件交互、路由、视觉 token 一致性 |

## API 契约

后端统一响应为 `app/schemas/common.py` 的 `ApiResponse`：`{code, message, data, request_id}`；错误码见 `app/core/errors.py` `ErrorCode`（`OK` / `VALIDATION_ERROR` / `NOT_FOUND` / `METHOD_NOT_ALLOWED` / `NOT_IMPLEMENTED` / `HTTP_ERROR` / `FORBIDDEN` / `NOT_READY` / `INTERNAL_ERROR`）。

- 默认 `baseURL` 为相对路径 `/api/v1`，不硬编码主机。
- 开发期若 API 不在本机，设 `VITE_API_PROXY_TARGET=<回环地址>` 启用 Vite `/api` 代理；也可设 `VITE_API_BASE_URL`。
- **`listDomain()` 当前恒收到 501**：调用方必须捕获 `NOT_IMPLEMENTED` 并显示「尚未实现」，禁止用本地 JSON 或示例数据填充。
- 不引入 `design-demos/*.json` 中的任何内容数据；真实数据接入属 T-09 / T-10 / T-11。

## 明确未做

不启动 nginx / Compose `web` 服务、不改后端、不改原型文件、不引入 UI 框架或状态管理库、不实现业务 CRUD、不生成公开播放地址。视觉回归参考仍是 `design-demos/validate_prototypes.py`（原型未改动，其断言口径不变）。
