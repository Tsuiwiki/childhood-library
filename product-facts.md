# Childhood Library · 事实与来源

采集日期：2026-11-18（2026-11-18 补记全文篇章原则）

## 项目事实

- 项目：童年书房 · Childhood Library。
- 当前阶段：Phase 0，项目定义与基础设计；仓库尚无可运行的前后端程序。
- 2026-11-18 规则修订：平台定位为免费供大众及教育使用的公共儿童文学与传统文化数据库；采用「目录先行、内容后审」，广泛建立可合法发现资源的目录与合法来源链接，具体内容逐项评审后公开。
- 2026-11-18 原则修订：按用户要求落实 `docs/PROJECT_PRINCIPLES.md`（GitHub main，SHA `f60cbb0931d196f098459c8eef6774ee8150d2f6`）与「必须全文篇章填充」——正文默认录入完整篇章、全卷或全书，不以节选、梗概、导读或原创整理稿冒充正文；研究资源库与儿童使用层分开，五类状态分别记录。
- 本地 checkout 原先缺少 `docs/PROJECT_PRINCIPLES.md`，已按远程 main 原文逐字同步补入，避免原型与 Spec 的引用悬空。
- 本次对象：儿童故事馆（Story Library）前台 Web 原型。
- 规划基线：`docs/STORY_LIBRARY_PLAN_V1.md` v1.0，更新日期 2026-11-18。
- 官方仓库：https://github.com/Tsuiwiki/childhood-library
- 规划原文：https://github.com/Tsuiwiki/childhood-library/blob/main/docs/STORY_LIBRARY_PLAN_V1.md
- 顶层原则：https://github.com/Tsuiwiki/childhood-library/blob/main/docs/PROJECT_PRINCIPLES.md

## 原型全文来源（逐字核对）

| 作品 | 全文范围 | 源与权利线索 |
| --- | --- | --- |
| 女娲补天 | 《淮南子·览冥训》全篇20段 | `NiuTrans/Classical-Modern` 的 `古文原文/淮南子/览冥训/text.txt`，仓库 LICENSE 为 MIT；古籍原文属公版。维基文库《覽冥訓》页面供人工对照 |
| 精卫填海 | 《山海经·北山经》三节全篇92段 | `NiuTrans/Classical-Modern` 的 `古文原文/山海经/山经/北山经/text.txt`；维基文库《北山经》供对照 |
| 守株待兔 | 《韩非子·五蠹》全篇17段 | `NiuTrans/Classical-Modern` 的 `古文原文/韩非子/五蠹/text.txt`；维基文库《五蠹》供对照 |
| 田螺姑娘 | 《搜神后记·卷五》全卷9条目 | https://zh.wikisource.org/zh-hans/搜神後記/05 ，页面标注「此晋朝作品在全世界都属于公有领域」 |
| 丑小鸭 | 英文历史文本全篇40段 | Project Gutenberg #27200 |
| 青蛙王子 | 历史英译全篇14段 | Project Gutenberg #2591 |
| 爱丽丝梦游仙境 | 英文原作全书12章790段 | Project Gutenberg #11 |
| 稻草人 | 不提供原作正文 | https://zh.wikisource.org/wiki/稻草人 ，页面说明中国等地区仍有版权限制、本站暂不刊登正文；仅登记研究线索与来源链接 |

中文古典全文与本地下载源逐段精确匹配；《搜神后记·卷五》九条目与维基文库页面逐条一致。英文作品文本逐段与 ODU Gutenberg mirror 下载的纯文本精确匹配（主站当时返回维护页，未绕过限制）。

## 不可误读的数据

- 「首批100条」是候选作品档案建设目标，不是已上架故事数量，也不是可公开正文、插画或音频数量。
- 中国55% / 世界30% / 优秀原创15%是编辑研究投入建议，不是文学价值排名。
- 候选题材不等于完成版本考证或取得转载授权。
- 原型中的权利状态只用于表达产品机制，不构成真实版权结论。
- **全文已采集 ≠ 已获公开授权**。公版判断须结合目标发布地区、具体版本与页面权利说明；Project Gutenberg 的电子书权利说明尤其需要按发布地区复核。
- 英文原作或历史英译不是现代中文译本；导读、缩写本、绘本与原作各有自己的贡献者，不互相替代。

## 外部参考事实

- StoryWeaver 官方介绍确认其提供多语言儿童故事、阅读分级、筛选、书架等功能：https://storyweaver.org.in/en/about
- BookTrust 官方页面确认其按年龄、主题与编辑书单组织儿童书籍推荐：https://www.booktrust.org.uk/book-recommendations/booklists
- 两个外部站点仅作为信息架构参照，不使用其品牌资产，不复制其页面。
- `ctext.org` 页面明确禁止自动下载；本次未绕过该限制，古典全文改由开放语料与维基文库页面核对。
- 维基文库公开 API 对当前网络曾返回 403（Too Many Reqs）；未重试绕过，改用页面渲染结果与公开仓库语料。
