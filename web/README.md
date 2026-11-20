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

## Node 版本基线

`web/.nvmrc` 固定为 `22.22.2`，与本地开发机一致；`nvm use`（在 `web/` 下）或任何版本管理器都应以它为准。选这个版本不是随意升级：`abbrev@5.0.0` / `nopt@10.0.1` 在 lock 里声明 `^22.22.2 || ^24.15.0 || >=26.0.0`，低于该版本时 `npm ci` 会报 `EBADENGINE`。

> ⚠️ **远程 VM 上不要改系统默认 Node。** VM 的 `/usr/local/bin/node` → `/usr/local/node22/bin/node` 是共享的 CodeBuddy 工具链（`v22.12.0` / npm `10.9.0`），同目录还有 `cbc` / `agent-browser` 等命令，且有运行中进程。本工程在 VM 上改用仓库外独立安装：

```bash
# 只在 childhood-library 的复跑会话中临时生效，不写入 profile、不改软链
export PATH=/data/cl-node/node-v22.22.2-linux-x64/bin:$PATH
node -v   # v22.22.2
npm -v    # 10.9.7
cd /data/childhood-library/web && npm ci && npm run build && npm run test
```

2026-11-20 用该独立 Node 在 VM 复跑：`npm ci` 装 167 包、`EBADENGINE` 警告从 2 条降到 **0**、`vite build` 51 模块（105.34 kB JS / 7.33 kB CSS）、`vitest run` **18/18 全绿**、`package-lock.json` SHA-256 前后不变、工作区干净；系统默认 `v22.12.0` 保持未动。独立 Node 的安装包与 `SHASUMS256.txt` 校验结果放在 `/data/cl-node/`，不进仓库。

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
