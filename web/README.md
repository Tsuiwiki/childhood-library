# web/ — 童年书房 Vue 内部研究前端

Vue 3 + TypeScript + Vite 实现的内部研究界面。`design-demos/` 保持只读；本目录复用其视觉 token、页面结构和已登记研究快照，不另行复制一套内容 JSON。

## 当前页面

| 路由 | 内容与边界 |
| --- | --- |
| `/library` | 跨馆资料总览：检索 105 条音乐目录、100 条故事、60 条诗词及研究文档入口 |
| `/music` | 音乐馆、三大内容支柱、八个专题与逐曲研究档案；专题可直接进入对应录音筛选 |
| `/music/specialties/:id` | 八个音乐专题子页；保留完整候选档案，并可只看本专题已有录音或进入歌曲详情 |
| `/story` | 九个目录组、100 条研究记录，支持关键词、专题和深链接筛选 |
| `/poetry` | 十个专题、60 条研究记录，保留版本线索、资产边界与五维状态 |
| `/works` | 58 条主录音记录；搜索、类型筛选、分页、封面和全站共享底部播放器 |
| `/works?topic=<专题ID>` | 按音乐专题筛选已有录音，可返回专题档案或恢复全部录音 |
| `/works?work=<作品ID>` | 指定作品的录音详情、版本切换、歌词/谱面状态、来源与权利说明 |
| `/catalog` 等 7 个业务域 | 仍展示 API 的 `501 NOT_IMPLEMENTED`，不用本地数据伪装业务接口 |

底部播放器和当前曲目状态位于 `App.vue` 全站层。在资料总览、三馆、音乐专题和录音页之间进行 Vue 路由切换时，保留同一个 `<audio>`、播放位置和底栏；切歌、切换当前作品录音版本或主动关闭仍按原规则处理。跳到独立静态原型页会离开 Vue 应用，不属于连续播放范围。

歌曲详情还展示其所属专题，以及 GitHub 上已有的逐曲研究档案。文档关联依据现有作品 ID 与标准题名建立；不把候选音频、平台试听或研究登记描述为已获公开授权。

## 命令

```bash
cd web
npm ci                 # 依据 package-lock.json 精确安装
npm run typecheck      # vue-tsc --noEmit
npm run build          # typecheck + vite build
npm run test           # vitest run
npm run dev            # 127.0.0.1:55173（仅开发时按需启动）
```

本机与远程复跑基线：Node `v22.22.2` / npm `10.9.7`。依赖在 `package.json` 中逐个精确锁定，`package-lock.json` 为全量锁，二者都必须提交；`node_modules/`、`dist/`、`coverage/` 不入库。

## Node 版本基线

`web/.nvmrc` 固定为 `22.22.2`。`abbrev@5.0.0` / `nopt@10.0.1` 在 lock 里声明 `^22.22.2 || ^24.15.0 || >=26.0.0`，低于该版本时 `npm ci` 会报 `EBADENGINE`。

> ⚠️ **远程 VM 上不要改系统默认 Node。** 系统 Node 属于共享 CodeBuddy 工具链。本工程在 VM 使用仓库外独立安装，并只在复跑会话中显式设置 PATH：

```bash
export PATH=/data/cl-node/node-v22.22.2-linux-x64/bin:$PATH
node -v   # v22.22.2
npm -v    # 10.9.7
cd /data/childhood-library/web && npm ci && npm run build && npm run test
```

该方式已解决 `EBADENGINE`，不改变共享工具链、系统软链或 profile。独立 Node 安装包和校验文件不进仓库。

## 目录与资料边界

| 路径 | 说明 |
| --- | --- |
| `src/styles/tokens.css` | 逐值复用原型配色；纸纹、墨边、硬阴影等视觉基准不改写 |
| `src/components/` | 播放器、录音详情、研究卡片、全站地图及基础共享组件 |
| `src/composables/useAudioPlayer.ts` | 跨路由共享当前曲目；实际 `<audio>` 只在 `App.vue` 挂载一次 |
| `src/research/samples.ts` | 唯一允许读取 `design-demos/audio/samples.json` 的数据层 |
| `src/research/library.ts` | 唯一允许读取故事/诗词 `library-content.json` 的数据层 |
| `src/research/specialties.ts` | 唯一允许读取 105 条音乐目录与专题映射的数据层 |
| `src/research/documents.ts` | GitHub 研究文档的导航元数据及作品关联；不复制文档正文 |
| `src/api/` | 统一 API 客户端，解析 envelope 并如实处理 501 |
| `src/router/` | 内部研究页面、7 个业务域占位页和 404 |
| `tests/` | API、组件、播放器、录音详情、三馆、跨馆检索和路由测试 |

**所有 Vue 视图和组件必须通过上述数据层读取原型快照，禁止各自直接导入 JSON。** 新文档只建立 GitHub 原文链接，不将 Markdown 正文编译进页面。

## API 契约

后端统一响应为 `{code, message, data, request_id}`；默认 `baseURL` 为相对路径 `/api/v1`。开发期可设 `VITE_API_PROXY_TARGET=<回环地址>` 启用 Vite `/api` 代理，也可设 `VITE_API_BASE_URL`。

`listDomain()` 当前收到 501 时，调用方必须显示「尚未实现」，禁止用研究 JSON 或示例数据填充正式业务页。内部研究页面与正式业务数据库是两条明确分开的路径。

## 明确未做

- 正式业务 CRUD、编辑后台、真实数据导入和公开发布审核。
- 把原型 IndexedDB 本地音频导入/移除、Deezer 官方 30 秒面板迁入 Vue。
- 公开分发研究录音，或把内部研究页面称为已发布曲库。
- 向 GitHub 提交音频、`.env`、密钥、依赖目录或构建产物。
