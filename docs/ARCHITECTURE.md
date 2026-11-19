# 系统架构设计

- 文档状态：Draft（Phase 0 审计后升版，追加 §5 实施约束）
- 版本：0.2

## 1. 架构目标

采用模块化单体 + 独立采集 Worker 的初始架构。先保证数据治理、审核和来源可追溯，再逐步扩展采集规模和媒体能力。首期不采用微服务。

## 2. 逻辑架构

```mermaid
flowchart TB
  Visitor[网站访客] --> Web[Vue Web 前台]
  Editor[内容编辑] --> Admin[Vue 管理后台]
  Web --> API[FastAPI API]
  Admin --> API
  API --> DB[(PostgreSQL)]
  API --> Search[PostgreSQL 全文检索]
  API --> Media[对象存储]
  Scheduler[定时调度] --> Queue[任务队列]
  Queue --> Worker[采集与处理 Worker]
  Worker --> Sources[开放 API / RSS / 获准来源]
  Worker --> DB
  Worker --> AI[可选 AI 辅助服务]
  Admin --> Review[内容与版权审核]
  Review --> DB
```

## 3. 技术选型

| 组件 | 初始方案 | 说明 |
| --- | --- | --- |
| Web | Vue 3 + TypeScript + Vite | 前台与后台可共享组件 |
| API | FastAPI + Pydantic | REST API、数据校验 |
| DB | PostgreSQL | 关系数据、JSONB、全文检索 |
| Ingestion | Python + HTTPX | API、RSS、允许访问的网页 |
| Parsing | BeautifulSoup / feedparser | 仅处理符合来源规则的内容 |
| Queue | Celery + Redis | 任务量上升后启用 |
| Media | S3-compatible storage | 仅存储具有明确使用权的媒体 |
| Deploy | Docker Compose + Nginx | 单机部署起步 |


## 3.1 统一媒体资产服务

音乐馆、故事馆、诗词馆共享 Media Asset Service，不分别实现供应商 SDK。媒体服务负责资产元数据、权利门禁、上传校验、访问授权和生命周期；Storage Provider Adapter 负责本地文件系统、腾讯 COS、百度 BOS 等后端的具体读写操作。

第一阶段使用本地适配器完成业务链路；云端测试时选择一家供应商，使用私有 Bucket 和短时授权 URL，暂不启用 CDN。只有在获得真实访问数据后才评估 CDN。媒体资产的稳定 ID 与 `object_key` 和供应商 URL 分离，禁止在作品主记录中硬编码临时播放地址。

详见 [统一媒体资产与对象存储设计](MEDIA_ASSET_DESIGN.md)。

## 4. 业务模块边界

- catalog：作品、作者、分类、标签、作品关系。
- content：作品正文、翻译、注释和版本。
- sources：信源、来源条目、采集策略。
- ingestion：采集任务、解析器、标准化、去重。
- rights：版权记录、许可证、证据和适用地域。
- review：人工审核、退回意见、审核历史。
- media：图片、音频及其他媒体资产。
- publishing：公开状态、发布与下架。
- search：统一检索与筛选。

## 5. 数据流

1. 信源配置进入采集调度。
2. 采集器按来源允许的方式读取目录或内容。
3. 原始响应按来源策略保留必要的审计信息，不无差别归档受保护内容。
4. 标准化生成作品候选及来源条目。
5. 去重模块匹配现有作品，无法确定时交由人工处理。
6. AI 可生成标签、摘要草稿和质量提示。
7. 权利审核与内容审核分别执行。
8. 只有满足发布条件的作品才进入公开查询。
9. 下架或授权到期时，公开接口立即停止返回相关内容。

## 6. 安全边界

- API 密钥、对象存储密钥和数据库密码只从环境变量或密钥管理服务读取。
- 管理端与公开 API 分离权限。
- 公开 API 只查询已发布且权利状态满足发布策略的数据。
- 采集器设置超时、速率限制、重试上限和域名白名单。
- 禁止绕过登录、付费墙、验证码、访问控制或明确的反自动化限制。
- 上传媒体进行类型、大小和恶意文件检查。
- 管理操作写入审计日志。

## 7. 部署拓扑

MVP 可在一台服务器上运行：
- nginx
- frontend
- api
- PostgreSQL
- Redis（启用异步任务时）
- ingestion-worker
- 对象存储使用外部 S3 服务或本地开发替代方案

生产环境应单独备份数据库和媒体元数据，并定期验证恢复流程。

## 8. 可演进方向

- 数据量增加后，将搜索迁移到 Meilisearch / OpenSearch。
- 采集任务增加优先级、来源配额和失败隔离。
- 媒体资源增加转码与 CDN。
- 将 AI 处理抽象为可替换 Provider。
- 当模块边界和规模确有需要时再拆分服务。

## 5. 实施约束（2026-11-19 Phase 0 实机勘察补充）

以下约束来自远程 Linux VM 的**只读**探测，不改动 §2–§4 的既定架构：

| 项 | 实测 | 架构约束 |
| --- | --- | --- |
| 操作系统 | TencentOS Server 3.2（el8.2 兼容），内核 5.4.241 x86_64 | 使用容器化部署，不依赖发行版特有包 |
| 计算 / 内存 / 磁盘 | 8 核、15 Gi（无 swap）、99 G 磁盘 65 G 可用 | 为容器设内存上限；媒体使用独立 volume 并监控水位 |
| Python | 系统 `python3` 为 3.6.8（EOL），另有 `python3.11` / `python3.12.11` | **显式使用 3.12 venv 或容器镜像**，禁止修改系统默认解释器 |
| 数据库 | 未安装 PostgreSQL；已有 `pgvector/pgvector:pg16` 镜像 | PG16 以容器启动，端口仅绑定回环 |
| Docker | 26.1.3 / Compose v2.27.0；Node 22.12.0 / npm 10.9.0 | 满足前后端工程化条件 |
| 主机防火墙 | `firewalld` inactive | 数据库、管理后台、管理工具**不得监听 0.0.0.0**；仅 Nginx 对外 |
| 共享机现状 | 已有 TiDB v8.5.0、anydev-agent 等容器；8080/8090/4000/10080/2379 已占用 | 独立目录、独立 Compose project name、独立 volume 与端口段；不清理已有容器 |
| 出站网络 | GitHub / PyPI / npm 均 200 | 可拉取依赖，但须锁定版本并保留离线清单 |

**边界**：本节只记录实机约束；T-04 已按此完成 VM 环境搭建，T-05 已接入 `api` 容器。实际目录、Compose、备份与恢复命令见 [远程开发环境方案](REMOTE_DEVELOPMENT_ENVIRONMENT.md)，配置见 `deploy/`，骨架说明见 `app/README.md`。SSH 主机、端口、账号与密钥路径属于敏感配置，不写入本仓库任何文档。
