# 资产与媒体完整性清单

- 生成时间：2026-11-19 15:33:33
- 范围：local design-demos working tree (GitHub main excludes binary media via .gitignore)
- 方式：read-only; no media file was modified, moved or deleted
- 生成脚本：`scripts/asset_inventory.py`（可重复执行，输出本文件与同名 `.json`）

> 本清单只记录**本地工作区**资产。GitHub `main` 通过 `.gitignore` 排除全部二进制媒体，`design-demos/audio/` 在公开仓库中只有 JSON 清单。配置引用 ≠ 实际媒体文件；实际媒体文件 ≠ 已获公开播放、下载或分发授权。

## 1. 汇总

| 指标 | 数值 |
| --- | ---: |
| 试听配置条目 | 58 |
| 录音版本（含 variants） | 63 |
| 唯一音频文件名引用 | 62 |
| 本地真实音频文件 | 85 |
| 引用缺失文件 | 0 |
| 未被引用孤儿文件 | 23 |
| 缺少 sampleType 的条目 | 3 |
| 官方短时预览配置 | 5 |
| 内部研究采集登记文件 | 27 |
| 采集记录作品映射 | 28 |
| 世界经典资料卡 | 47 |
| 世界经典音频待采集 | 47 |
| 作品发现目录条目 | 105 |

**资源类型分布**：`MISSING` 3、`generated` 21、`internal` 26、`open` 8。

**文件类型分布**（`design-demos/` 递归，不含 `__pycache__`）：`.flac` 1、`.html` 23、`.jpg` 3、`.json` 13、`.m4a` 16、`.md` 5、`.mp3` 15、`.mp4` 1、`.musicxml` 14、`.png` 161、`.py` 26、`.svg` 119、`.wav` 52。

## 2. 基线断言

| 断言 | 期望 | 实测 | 结果 |
| --- | ---: | ---: | --- |
| 唯一音频引用 | 62 | 62 | PASS |
| 本地真实音频文件 | 85 | 85 | PASS |
| 引用缺失文件 | 0 | 0 | PASS |
| 孤儿文件 | 23 | 23 | PASS |
| 缺少 sampleType | 3 | 3 | PASS |
| 世界经典音频待采集 | 47 | 47 | PASS |

> 期望值来自 Phase 0 审计基线；若后续采集导致数字变化，应同步更新本报告、`DEVELOPMENT_STATUS.md` 与 `DATA_MIGRATION_PLAN.md`，不要静默漂移。

## 3. 引用中的音频文件（含校验和）

| 文件 | 类型 | 大小 (KB) | 时长 (s) | SHA-256 (前 12 位) |
| --- | --- | ---: | ---: | --- |
| `CN-C01-original.mp3` | internal | 6801.8 | 143.69 | `f362616eb1cc` |
| `CN-C02-gxzf.flac` | internal | 15630.7 | 189.68 | `541db2ffc65d` |
| `CN-C02-xuexi-chorus.m4a` | internal | 2896.2 | 187.07 | `8ec9568caba8` |
| `CN-C03-original.mp4` | internal | 7072.5 | 66.73 | `8b77aa56b45a` |
| `CN-C03-xuexi-chorus.mp3` | internal | 3635.0 | 155.01 | `252c84360cfe` |
| `CN-C04-CN-C16-xuexi.mp3` | internal | 3390.7 | 144.59 | `8b5c2f16ea82` |
| `CN-C05-cctv.m4a` | internal | 305.0 | 80.09 | `32aaca82a675` |
| `CN-C06-xuexi.mp3` | internal | 2079.2 | 88.63 | `b71237e91c53` |
| `CN-C07-xuexi.mp3` | internal | 2422.7 | 103.29 | `84cb3bf3b5df` |
| `CN-C08-cctv-hsl.m4a` | internal | 345.5 | 91.09 | `e731e5ce906b` |
| `CN-C08-cctv-mgzg.m4a` | internal | 652.2 | 172.25 | `1d30a32b9091` |
| `CN-C09-cctv.m4a` | internal | 325.7 | 85.99 | `a2c27f72bdde` |
| `CN-C10-original.mp3` | internal | 3179.0 | 203.37 | `58c8cfba39e7` |
| `CN-C11-xuexi.m4a` | internal | 2815.0 | 283.20 | `d07b03e3547c` |
| `CN-C12-xuexi-galaxy.m4a` | internal | 1027.8 | 251.60 | `e943bfcd8c86` |
| `CN-C13-xuexi.mp3` | internal | 5022.3 | 214.21 | `578d5399f322` |
| `CN-C14-xuexi.mp3` | internal | 683.9 | 29.10 | `e083a891c2d7` |
| `CN-C15-xuexi.mp3` | internal | 1595.0 | 67.97 | `d7f7ae445780` |
| `CN-C17-xuexi.mp3` | internal | 2544.6 | 108.49 | `401b5d2f1a1a` |
| `CN-C18-hbwy.m4a` | internal | 1406.7 | 93.16 | `32e2c8681698` |
| `CN-C19-xuexi.mp3` | internal | 3129.2 | 133.43 | `bf679209d9e4` |
| `CN-C20-cctv.m4a` | internal | 277.5 | 73.26 | `fbb51fce1558` |
| `CN-C21-cctv.m4a` | internal | 221.7 | 58.39 | `45031ca204f7` |
| `CN-C22.wav` | generated | 494.7 | 11.48 | `29323ee5ba6f` |
| `CN-C23.wav` | generated | 421.1 | 9.78 | `287e0e992dc0` |
| `CN-C24.wav` | generated | 401.7 | 9.33 | `ebf06965ebfe` |
| `CN-C25.wav` | open | 906.6 | 21.05 | `eb1e85926db7` |
| `CN-C26.wav` | open | 783.5 | 18.19 | `a1b90c89be2c` |
| `CN-C27.wav` | open | 1285.6 | 29.85 | `419f980ccc8c` |
| `CN-C28.wav` | open | 1078.9 | 25.05 | `5f14b6176f23` |
| `CN-C29.wav` | open | 1618.1 | 37.57 | `79780330548d` |
| `CN-C30.wav` | generated | 401.7 | 9.33 | `ebf06965ebfe` |
| `CN-N01-xuexi.mp3` | internal | 506.2 | 64.68 | `073546f6a4ef` |
| `CN-N02-cctv-jcyyh.m4a` | internal | 840.5 | 222.42 | `636f94c7f9c6` |
| `CN-N02-cctv-kldb.m4a` | internal | 267.1 | 69.93 | `0b18730c9896` |
| `CN-N03-cctv.m4a` | internal | 271.2 | 71.08 | `77f9eae1a343` |
| `CN-N04.wav` | generated | 421.1 | 9.78 | `287e0e992dc0` |
| `CN-N05-cctv-dqsx.m4a` | internal | 256.4 | 67.09 | `8de0a9547369` |
| `CN-N05-cctv-jcyyh.m4a` | internal | 669.1 | 176.62 | `eb0a78951150` |
| `CN-T01.wav` | open | 1053.6 | 24.46 | `a4273755126d` |
| `CN-T02.wav` | open | 1053.6 | 24.46 | `55737042d04d` |
| `CN-T03.wav` | generated | 442.8 | 10.28 | `457afb0f8a34` |
| `CN-T04.wav` | generated | 421.1 | 9.78 | `287e0e992dc0` |
| `CN-T05.wav` | open | 2032.9 | 47.20 | `f8e7122a3876` |
| `CN-T06.wav` | generated | 467.1 | 10.85 | `d329757f6196` |
| `CN-T07.wav` | generated | 494.7 | 11.48 | `29323ee5ba6f` |
| `CN-T08.wav` | generated | 467.1 | 10.85 | `d329757f6196` |
| `CN-T09.wav` | generated | 442.8 | 10.28 | `457afb0f8a34` |
| `CN-T10.wav` | generated | 421.1 | 9.78 | `287e0e992dc0` |
| `CN-T11.wav` | generated | 442.8 | 10.28 | `457afb0f8a34` |
| `CN-T12-cctv.m4a` | internal | 565.7 | 149.67 | `d075660852d2` |
| `CN-T13.wav` | generated | 421.1 | 9.78 | `287e0e992dc0` |
| `CN-T14.wav` | generated | 467.1 | 10.85 | `d329757f6196` |
| `CN-T15.wav` | generated | 442.8 | 10.28 | `457afb0f8a34` |
| `CN-T16.wav` | generated | 401.7 | 9.33 | `ebf06965ebfe` |
| `CN-T17.wav` | generated | 494.7 | 11.48 | `29323ee5ba6f` |
| `CN-T18.wav` | generated | 467.1 | 10.85 | `d329757f6196` |
| `CN-T19.wav` | generated | 442.8 | 10.28 | `457afb0f8a34` |
| `CN-T20.wav` | generated | 421.1 | 9.78 | `287e0e992dc0` |
| `EN-T01.mp3` | MISSING | 726.3 | 24.58 | `6f18c286021f` |
| `EN-T02.mp3` | MISSING | 227.1 | 10.31 | `462c5c3c4acb` |
| `EN-T03.mp3` | MISSING | 975.0 | 44.69 | `fb6969a5b424` |

完整 SHA-256、字节数、时长与路径见 `asset-inventory.json`。时长为尽力探测：WAV 使用标准库读取，其余格式在 PyAV 可用时探测；无解码器时记 `-`，不猜测。

## 4. 孤儿文件（未被任何试听配置引用）

| 文件 | 大小 (KB) | SHA-256 (前 12 位) |
| --- | ---: | --- |
| `CN-C02.wav` | 467.1 | `d329757f6196` |
| `CN-C04.wav` | 401.7 | `ebf06965ebfe` |
| `CN-C05.wav` | 467.1 | `d329757f6196` |
| `CN-C06.wav` | 467.1 | `d329757f6196` |
| `CN-C07.wav` | 442.8 | `457afb0f8a34` |
| `CN-C08.wav` | 421.1 | `287e0e992dc0` |
| `CN-C09.wav` | 401.7 | `ebf06965ebfe` |
| `CN-C11.wav` | 401.7 | `ebf06965ebfe` |
| `CN-C12.wav` | 494.7 | `29323ee5ba6f` |
| `CN-C13.wav` | 442.8 | `457afb0f8a34` |
| `CN-C14.wav` | 421.1 | `287e0e992dc0` |
| `CN-C15.wav` | 421.1 | `287e0e992dc0` |
| `CN-C16.wav` | 494.7 | `29323ee5ba6f` |
| `CN-C17.wav` | 494.7 | `29323ee5ba6f` |
| `CN-C18.wav` | 467.1 | `d329757f6196` |
| `CN-C19.wav` | 401.7 | `ebf06965ebfe` |
| `CN-C20.wav` | 494.7 | `29323ee5ba6f` |
| `CN-C21.wav` | 442.8 | `457afb0f8a34` |
| `CN-N01.wav` | 494.7 | `29323ee5ba6f` |
| `CN-N02.wav` | 467.1 | `d329757f6196` |
| `CN-N03.wav` | 442.8 | `457afb0f8a34` |
| `CN-N05.wav` | 401.7 | `ebf06965ebfe` |
| `CN-T12.wav` | 401.7 | `ebf06965ebfe` |

> 孤儿文件在迁移报告中单列，由人工判断归档或淘汰，**不自动删除**。

## 5. 数据完整性缺口

- 缺少 `sampleType` 的条目：`EN-T01`, `EN-T02`, `EN-T03`。迁移前须按 `MUSIC_LIBRARY_IMPLEMENTATION_PLAN.md` §6 的五类资源补齐，不得猜测。
- 引用缺失文件：0 个。
- 27 个 `internal` 研究录音保持「权利待核验」，只登记在研究层；21 个 `generated` 是程序合成示范音，页面标注「非原曲」。
- 47 条世界经典音频全部「真实录音待采集」，不硬配合成音冒充原曲。

## 6. 与迁移的关系

本清单是 `DATA_MIGRATION_PLAN.md` §5 完整性校验的输入：导入后须复核数量、关联、孤儿、重复、权利分布与发布门禁；媒体文件按 `import_batch_id` 登记，只增不删，可按批次回滚。
