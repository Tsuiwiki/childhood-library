# 统一媒体资产与对象存储设计

- 文档状态：Design Proposal
- 版本：1.2（T-07 M0 实装）
- 更新日期：2026-11-19
- 适用范围：音乐馆、故事馆、诗词馆及后续所有媒体内容模块

## 1. 目标与决策摘要

Childhood Library 的音频、图片、乐谱等媒体文件不应放入 GitHub 代码仓库，也不应由音乐馆、故事馆、诗词馆分别建设互不兼容的文件系统。本项目采用统一的 **Media Asset Service（媒体资产服务）** 管理媒体元数据、存储位置、访问授权、完整性和生命周期。

当前用户范围以中国大陆为主，第一阶段为项目维护者和少量家庭用户测试。建议按以下顺序实施：

1. 开发阶段先使用本地文件系统适配器，完成上传、读取、校验和播放链路。
2. 需要云端测试时，在腾讯云 COS 与百度智能云 BOS 中选择一个作为首个云存储适配器。
3. 初期使用私有 Bucket 和短时授权访问地址，暂不启用 CDN，不购买大容量资源包。
4. 有真实公网播放量后，再依据地域、缓存命中率和实际账单决定 CDN 与资源包。
5. 数据模型和业务代码保持供应商中立，避免将 COS/BOS URL 写入作品或版本记录。

**初步供应商判断：** COS 与 BOS 的标准存储价格接近；BOS 在部分公开按量流量/CDN 价格档位上略有优势，但实际费用受地域、计费方式、忙闲时、资源包、回源和 CDN 配置影响。当前测试规模下，预计账单很小，价格差异不足以成为架构绑定理由。若必须先选一家，可优先评估 BOS；若已有腾讯云资源或更熟悉腾讯云运维，则 COS 同样合理。正式采购前必须在官方控制台按目标地域重新核价。

## 2. 适用范围与边界

统一管理的媒体类型包括：

- 音频：儿歌、故事朗读、诗词朗诵、音乐示范。
- 图片：封面、插画、作品配图。
- 乐谱：PDF、MusicXML、SVG、PNG 等。
- 后续可扩展视频、字幕和其他附件。

媒体资产与作品、作品版本、录音版本、乐谱版本及来源记录关联，但不与它们混为一体。

研究登记不代表可以下载、缓存、复制或托管第三方媒体。对象存储只保存项目拥有或已取得明确保存/使用许可的文件；权利待确认的第三方资源默认只登记必要元数据、证据和原始来源链接。公开播放、下载、嵌入和分发分别审核，不能仅凭“已收录”或“可在线播放”推导许可。

## 3. 逻辑架构

```text
音乐馆 / 故事馆 / 诗词馆
          |
          v
     Media API
          |
          v
   Media Asset Service
     |       |       |
     |       |       +-- Rights / Publication Gate
     |       +---------- Metadata / Checksum / Lifecycle
     +------------------ Storage Provider Adapter
                            |
             +--------------+--------------+
             |              |              |
          Local FS       Tencent COS     Baidu BOS
          (开发测试)       (云端候选)       (云端候选)
                                           |
                                  后续按需接入 CDN
```

媒体服务负责业务规则和访问控制；Provider Adapter 只负责供应商相关的上传、读取、删除、元数据查询和签名 URL 等基础操作。

## 4. 存储供应商比较

| 维度 | 腾讯云 COS | 百度智能云 BOS |
|---|---|---|
| 产品类型 | 对象存储 | 对象存储 |
| 标准存储 | 大陆公开价格约 ¥0.118/GB/月，地域及活动以控制台为准 | 大陆公开价格约 ¥0.119/GB/月，地域及活动以控制台为准 |
| 直接外网下载 | 示例公开档位约 ¥0.50/GB | 示例公开档位忙时约 ¥0.49/GB、闲时约 ¥0.25/GB |
| CDN 下行 | 示例公开档位约 ¥0.21/GB | 示例公开档位约 ¥0.20/GB |
| CDN 回源 | 示例公开档位约 ¥0.15/GB | 示例公开档位约 ¥0.14/GB |
| 生态考虑 | 腾讯云产品体系、COS SDK 和 CDN 可协同 | 百度智能云产品体系，忙闲时流量计费值得评估 |
| 当前建议 | 已使用腾讯云时优先考虑 | 若按示例价格比较，可优先做成本验证 |

上述价格为 2026-11-19 规划阶段参考值，不是报价承诺。不同地域、流量阶梯、计费模式、资源包、HTTPS 请求、回源方式和活动可能改变最终费用。正式选型前，必须在目标地域的官方价格页/控制台重新核实。

官方入口：
- 腾讯 COS：<https://cloud.tencent.com/product/cos>；价格：<https://cloud.tencent.com/document/product/436/6239>
- 腾讯 CDN：<https://cloud.tencent.com/product/cdn>；价格：<https://cloud.tencent.com/document/product/228/2949>
- 百度 BOS：<https://cloud.baidu.com/product/bos.html>；价格：<https://cloud.baidu.com/doc/BOS/index.html>
- 百度 CDN：<https://cloud.baidu.com/product/cdn.html>

## 5. 初期费用估算

### 5.1 规划假设

- 标准存储 10GB。
- 中国大陆用户。
- 暂不购买资源包。
- 请求次数费用在小规模测试中忽略。
- 不含税费、域名、HTTPS 证书、转码、图片处理和其他增值服务。
- 价格采用上节的示例公开档位，实际费用以账单为准。

### 5.2 直接从对象存储播放

| 每月播放流量 | COS 估算 | BOS 估算 |
|---:|---:|---:|
| 10GB | 约 ¥6.18 | 约 ¥5.37 |
| 20GB | 约 ¥11.18 | 约 ¥9.55 |
| 50GB | 约 ¥26.18 | 约 ¥22.09 |
| 100GB | 约 ¥51.18 | 约 ¥42.99 |

BOS 估算按 70% 忙时、30% 闲时的示例流量构成计算；真实忙闲时分布不同，费用会变化。

### 5.3 使用 CDN 播放

假设 CDN 下行流量按 20GB/月计算、缓存命中率 80%，回源流量按未命中部分 4GB 粗略估算：

| 项目 | COS | BOS |
|---|---:|---:|
| 10GB 标准存储 | ¥1.18 | ¥1.19 |
| 20GB CDN 下行 | ¥4.20 | ¥4.00 |
| 4GB 回源 | ¥0.60 | ¥0.56 |
| 合计 | 约 ¥5.98 | 约 ¥5.75 |

以上是用于比较的简化模型，不是 CDN 账单模拟器。实际回源计费取决于 CDN 与对象存储的产品关系、回源地域、流量类型、缓存规则和供应商优惠；需在开通前核对是否存在额外回源费用或免计费政策，避免重复计算或漏算。

### 5.4 当前成本结论

测试阶段如果仅有自己和少量家庭用户，建议先直连私有对象存储的短时授权地址，不急于启用 CDN。按 10GB 存储、每月 10–20GB 播放流量估算，直接播放月费用约为数元至十余元量级。不要为了很小的账单差异提前引入 CDN、跨云复制或复杂缓存系统。

## 6. MediaAsset 数据模型

建议媒体资产元数据与物理存储位置分离。

### media_assets

- `asset_id`：稳定资产 ID，不依赖供应商。
- `work_id` / `version_id`：关联作品及具体版本，可为空以支持通用素材。
- `asset_role`：cover / recording / narration / score / illustration / subtitle / attachment。
- `media_type`、`mime_type`、`file_extension`。
- `file_size_bytes`、`duration_ms`、`width`、`height`。
- `checksum_sha256`：完整性校验。
- `rights_record_id`：关联具体资产的权利记录。
- `publication_status`：private / pending_review / approved / published / withdrawn。
- `created_at`、`updated_at`。

### storage_locations

- `storage_location_id`。
- `asset_id`。
- `provider`：local / tencent_cos / baidu_bos / s3_compatible。
- `region`、`bucket`、`object_key`。
- `storage_class`。
- `is_primary`、`replica_status`。
- `created_at`、`verified_at`。

### playback_resources

记录外部官方播放入口、官方预览或经授权的站内播放方式。不要把临时签名 URL 当作永久资源地址。

- `resource_id`、`asset_id` 或 `recording_version_id`。
- `resource_type`：external_link / official_preview / hosted_asset / official_embed。
- `provider`、`external_url`、`provider_resource_id`。
- `access_policy`、`review_status`、`last_verified_at`。

## 7. 对象 Key 与目录约定

使用稳定 ID，不使用可能变更的中文标题作为唯一对象路径：

```text
childhood-library/
  audio/
    music/{work_id}/{asset_id}.mp3
    stories/{work_id}/{asset_id}.mp3
    poetry/{work_id}/{asset_id}.mp3
  images/
    covers/{work_id}/{asset_id}.webp
    illustrations/{work_id}/{asset_id}.webp
  scores/
    {work_id}/{asset_id}.pdf
    {work_id}/{asset_id}.musicxml
  backups/
    database/{date}/...
    manifests/{date}/...
```

原始文件与处理后的播放文件应区分角色和版本。不要通过覆盖对象来悄悄替换已发布资产；替换时创建新资产或新版本，保留校验值和变更记录。

## 8. 上传、播放和访问控制

### 上传

1. 管理端请求 API 创建上传任务。
2. API 校验用户权限、文件类型、大小及目标用途。
3. API 生成短时上传授权，或由受信任后端上传。
4. 文件进入私有 Bucket。
5. 服务端检查对象存在性、大小、MIME 和 SHA-256。
6. 写入 MediaAsset 与 StorageLocation 元数据。
7. 资产进入待审核状态，不因上传成功自动公开。

### 播放

1. 客户端请求播放资源。
2. API 检查登录/访问策略、发布状态和该资产的权利记录。
3. 对私有且获准访问的资产，按需生成短时签名 URL。
4. 浏览器使用 HTTPS 播放；音频服务需支持 Range 请求，以便拖动进度。
5. 授权失效、撤回或下架时，API 停止签发新地址；已签发地址应使用较短有效期降低暴露窗口。

公开内容也应通过发布门禁；不要把 Bucket 整体设为公共读来简化开发。

## 9. 安全、备份与运维

- Access Key / Secret Key 只保存在服务端环境变量或密钥管理服务，不进入前端、GitHub、日志和文档示例。
- 优先使用最小权限子账号或临时凭证；分离开发、测试和生产 Bucket。
- 私有 Bucket 默认拒绝匿名访问。
- 上传限制 MIME、扩展名、大小；验证文件签名，不能只信任客户端 Content-Type。
- 对上传文件计算 SHA-256，定期做完整性抽检。
- 数据库备份与媒体文件备份分开规划；对象存储版本控制/生命周期规则按成本和恢复目标配置。
- 重要资产保留清单 manifest，记录 asset_id、object_key、checksum、size 和 rights_record_id。
- 设置月度费用预算和流量告警；测试环境可设置较低阈值。
- 删除、替换和授权撤回均保留审计记录。

## 10. 实施路线

### M0：本地适配器

- [x] 定义 StorageProvider 接口（T-07：`app/media/provider.py`）。
- [x] 实现 LocalStorageAdapter（T-07：`app/media/local.py`）。
- [x] 实现上传、下载/读取、删除、HEAD、checksum（T-07，含 HTTP Range 206/416）。
- [x] 实现 MediaAsset 与 StorageLocation 元数据（T-07：`app/media/service.py`，含 AuditLog）。
- [x] 增加媒体文件存在性和完整性检查脚本（T-07：`scripts/media_integrity.py`）。

### M1：云端适配器

- [ ] 在 COS 与 BOS 中选定一家进行小批量试用。
- [ ] 建立私有 Bucket 与最小权限凭证。
- [ ] 实现对应 Provider Adapter。
- [ ] 验证短时上传授权、短时播放 URL、Range 播放和删除。
- [ ] 记录实际上传速度、播放延迟、流量账单和权限配置。
- [ ] 保留对象清单和可迁移导出方案。

### M2：按需 CDN

- [ ] 先收集真实播放量、地域和缓存命中率。
- [ ] 对可公开播放的稳定资产配置 CDN。
- [ ] 配置缓存 TTL、版本化对象 Key 和下架策略。
- [ ] 核算 CDN 下行、回源、请求和 HTTPS 费用。
- [ ] 对私有内容评估签名 URL / CDN 鉴权，不开放公共 Bucket。

### M3：备份与迁移

- [ ] 实现媒体资产清单导出。
- [ ] 支持对象批量复制和 checksum 对账。
- [ ] 验证从云端恢复到本地或另一供应商。
- [ ] 明确备份保留期、恢复目标和费用上限。

## 11. 暂不实施事项

- 暂不同时接入 COS 和 BOS 双写。
- 暂不为少量家庭测试启用 CDN。
- 暂不购买大容量或长期资源包。
- 暂不对研究目录中的第三方媒体进行批量下载、镜像或托管。
- 暂不将对象存储作为数据库；作品、来源、权利和资产元数据仍由 PostgreSQL 管理。

## 12. 相关文档

- [系统架构设计](ARCHITECTURE.md)
- [数据模型设计](DATA_MODEL.md)
- [音乐馆实施优化方案](MUSIC_LIBRARY_IMPLEMENTATION_PLAN.md)
- [项目路线图](ROADMAP.md)
- [版权与内容审核政策](COPYRIGHT_POLICY.md)

## 13. 本地资产清单与迁移前校验（2026-11-19 补充）

本节不改动 §6 数据模型与 §8 访问控制，只补第一阶段落地要求：

1. **先盘点再迁移**：以 `scripts/asset_inventory.py` 生成只读清单，输出配置引用数、唯一文件数、实际文件数、缺失、孤立、重复、SHA-256、大小、格式与时长；报告落在 `docs/reports/asset-inventory.md`。
2. **基线数字**：`samples.json` 58 条 / 63 版本 / 62 个唯一文件名；本地 85 个真实音频；62 个引用零缺失、23 个孤儿文件、3 条缺 `sampleType`。这些数字是本地工作区口径，GitHub `main` 因 `.gitignore` 不托管二进制媒体。
3. **权利门禁**：27 个 `internal` 研究录音、21 个 `generated` 合成示范音、5 个官方短时预览与站内授权媒体分别登记；`internal` 只进研究层，不自动进入公开播放目录。
4. **StorageProvider 顺序**：先本地适配器验证 put/get/stat/delete/Range 与校验和；COS/BOS 仅保留接口与配置位，本阶段不采购、不上传第三方媒体。
5. **备份与迁移**：媒体与数据库使用独立 volume；备份同时校验 checksum，恢复演练先在 testing 环境完成。孤儿文件在迁移报告中单列，不自动删除。

关联：[数据迁移方案](DATA_MIGRATION_PLAN.md)、[项目现状审计报告](PROJECT_AUDIT.md)。

## 14. T-07 实装与定型（2026-11-19）

本节不回改 §1–§13 的概念设计，只记录 M0 落地结果与取舍。任务口径见 `IMPLEMENTATION_ROADMAP.md` L94-L101（「T-07 媒体资产模块」）与该文 §6 实测记录，实机约束见 §13。

### 14.1 已落地

| 项 | 实现 |
| --- | --- |
| Provider 接口 | `app/media/provider.py`：`put / get / stat / delete / range / checksum`，`ObjectStat` / `ByteRange` 与 6 类异常 |
| 本地适配器 | `app/media/local.py`：`object_key` 沙箱（拒绝绝对 / `..` / 非规范路径）、临时文件 + `os.replace` 原子写、声明 checksum 先校验再替换、`read_only` 显式拒绝写 |
| 格式与时长 | `app/media/probe.py`：签名优先（不信任客户端 Content-Type / 扩展名）；WAV 用标准库 `wave`，其余在 PyAV 可选可用时探测，**无解码器记 `None` 不猜测**，口径与 `scripts/asset_inventory.py` L37-L57 一致 |
| 完整性 | `app/media/integrity.py` + `scripts/media_integrity.py`：SHA-256 比对只报告、不自动修复或删除；孤儿文件单列 |
| 权利门禁 | `app/media/rights_gate.py`：`research_metadata`（恒允许）/ `internal_content`（需校验和通过）/ `public_url`（需有效权利核验 + published + approved + 非 none 访问方式）三级；复用 T-06 `rights_clearance_is_valid()` |
| Range 响应 | `app/media/http.py`：200 / 206 / 416，先过访问决策再出字节，**不生成任何 URL** |
| 元数据登记 | `app/media/service.py`：写 `MediaAsset` + `StorageLocation` + `AuditLog`，默认 `rights_status=unknown` / `publication_status=draft`，**从不创建 `PlaybackResource`** |
| 可观测端点 | `GET /api/v1/media/capabilities`（只读、不返 URL）；七个域的清单端点仍为 501，业务 CRUD 属 T-09/T-10 |
| 正式挂载 | `deploy/compose.dev.yml` 给 `api` 增加 `${MEDIA_ROOT}:/app/var/media:ro` 与 `MEDIA_READ_ONLY=true`，不再依赖仓库外临时 overlay |

### 14.2 三处定型取舍

1. **不引入新依赖**：M0 只用标准库 + 已有 FastAPI/SQLAlchemy 栈，`requirements.txt` 仍 8 个顶层依赖、`requirements.lock` 仍 36 包；时长不靠新增解码器硬凑。
2. **`object_key` 与供应商 URL 解耦**：`childhood-library/{audio|images|scores|attachments}/.../{asset_id}{ext}` 是内部键；DTO 显式标注 `object_key_note`，不返回任何访问地址，COS/BOS 适配器可后续替换而不改表。
3. **写入走受信任宿主管理端**：`api` 容器只读挂载（保护已迁移的 85 个平铺文件），`put/delete` 由宿主机 venv / 管理命令执行；云适配器与在线上传留待 M1 / T-09。

### 14.3 实机验证（VM）

104 个 pytest 全绿（T-06 为 57）；两段 overlay `config -q` 自足；`scripts/media_integrity.py` 对 VM `var/media/` 85/85 校验通过、0 意外文件；隔离临时库 `cl_t07_media` 完成 put/get/stat/checksum/range/delete 往返、篡改告警、`rights_record_id` 关联、未授权 `public_url` 拒绝与审计留痕后删库；`cl-dev` 五张业务表仍 0 行；`/readyz` 200，端口仅回环。

### 14.4 明确未做

不导入任何真实曲目 / 录音 / 权利结论；不创建公开播放资源或签名 URL；不采购或上传第三方云存储；不启用 CDN；不实现媒体业务 CRUD 端点。
