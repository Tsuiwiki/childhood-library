# -*- coding: utf-8 -*-
"""童年书房总构建：研究候选目录 -> 三馆页面 -> 全站关联层。

一次运行完成：
1. 刷新 library-content.json（library_catalog.build）
2. 生成 story.html / poetry.html / research.html
3. 重建八个专题页与 works.html
4. 向所有既有页面幂等注入统一导航、全站地图和专题横向导航

依据：
- docs/PROJECT_PRINCIPLES.md v1.0（GitHub main）双层架构与五维状态模型
- docs/DATA_MODEL.md v0.1 §4（GitHub main）
- docs/STORY_LIBRARY_PLAN_V1.md §2 / §9、docs/MUSIC_LIBRARY_PLAN_V1.md §2.1
"""
from __future__ import annotations

import html as html_lib
import json
import re
from collections import Counter
from pathlib import Path

import build_specialty_pages
import build_works
import library_catalog

ROOT = Path(__file__).resolve().parent
CATALOG = ROOT / "library-content.json"

E = html_lib.escape

NAV_ITEMS = [
    ("dir-3.html", "书房首页"),
    ("story.html", "故事馆"),
    ("music.html", "音乐馆"),
    ("poetry.html", "古诗词馆"),
    ("research.html", "研究资源库"),
    ("works.html", "作品目录"),
]

SPECS = [
    ("childhood", "01 童年的歌"),
    ("nature", "02 大自然的歌"),
    ("play", "03 游戏与伙伴"),
    ("lullaby", "04 月亮与摇篮曲"),
    ("classical", "05 古典音乐的童年"),
    ("world", "06 世界的童谣"),
    ("forgotten", "07 被遗忘的童谣"),
    ("original", "08 新芽原创"),
]

# 仍为 generated 测试音的作品：逐组记录核查结论与已核实的权威来源线索。
# 这里只登记研究线索，不把同名不同曲、整期节目片段或商业平台条目接入作品播放。
# render_research() 会校验本表与 samples.json 的 generated 集合完全一致。
REPLACEMENT_CLUES = [
    {
        "label": "闽南童谣「念谣」· 非遗项目页的体裁举例",
        "ids": ["CN-T03", "CN-T04", "CN-T06", "CN-T07", "CN-T08", "CN-T09", "CN-T10"],
        "finding": "国家级非遗项目页把这些篇名列为连锁调、问答歌、绕口令、摇篮曲等体裁举例，本质是口传念谣，没有固定乐谱与唯一原唱。检索到的同名音频多为不同文本异文或商业平台条目：例如央视《七巧板》的原创歌曲《小蜜蜂》与闽南童谣《小蜜蜂》并非同一作品，人民日报「童声童谣」的《一两三》也不是非遗页所指的《一二三》数数歌，均不得冒充目标作品原曲。",
        "clues": [
            ("中国非遗网《童谣（闽南童谣）》项目页", "https://www.ihchina.cn/project_details/12316.html"),
            ("ISRC 申报平台《白鹭鸶》录音制品登记", "http://www.isrc.com.cn/html/2022/page_8349.html"),
            ("人民日报「童声童谣」栏目（漳州新闻网）", "https://www.peopleapp.com/rmharticle/30009804516"),
            ("央视网《七巧板》原创歌曲《小蜜蜂》· 同名不同曲", "https://tv.cctv.cn/2021/04/24/VIDErHfSo6Rq8SLxsRaoxpTB210424.shtml"),
        ],
    },
    {
        "label": "地方 / 历史童谣 · 分类专题与文献条目",
        "ids": ["CN-C30", "CN-N04", "CN-T11", "CN-T13", "CN-T14", "CN-T15", "CN-T16", "CN-T17", "CN-T18", "CN-T19", "CN-T20"],
        "finding": "多为版本分类专题、地方异文或历史文献条目，本身不对应一段可定位的单曲录音。已核实的北京童谣、湖湘童谣与《水牛儿》演出版本属于相关文化语境或相近曲目，不是这些条目的原曲，故只登记来源线索，不接入播放。",
        "clues": [
            ("中国作家网《北京童谣传唱八百年》", "https://www.chinawriter.com.cn/n1/2020/1029/c404076-31910728.html"),
            ("央视网《七巧板》歌曲《湖湘童谣》", "https://tv.cctv.com/2015/07/07/VIDE1436223441788633.shtml"),
            ("央视网《民歌·中国》北京民歌《水牛儿》", "https://tv.cctv.com/2024/10/28/VIDEqBPnvxmWPJESINiNJwsa241028.shtml"),
        ],
    },
    {
        "label": "创作儿歌 · 未找到公开机构独立单曲页",
        "ids": ["CN-C22", "CN-C23", "CN-C24"],
        "finding": "检索结果集中于歌词站、商业音乐平台与整期教学节目。央视《音乐告诉你》20120608 只是含《种瓜》片段赏析的教学节目，不是单曲原声；课程页面只有歌词与词曲信息。按「整期节目不当单曲用」的口径暂不采集，继续等待可靠单曲页或权利人授权版本。",
        "clues": [
            ("央视网《音乐告诉你》20120608 · 整期教学节目", "https://tv.cctv.com/2012/06/08/VIDE1355662984922415.shtml"),
            ("超星慕课《我们在大地上栽种鲜花》课程页", "https://mooc1.chaoxing.com/mooc-ans/ztnodedetailcontroller/visitnodedetail?courseId=200819820&knowledgeId=114368107"),
        ],
    },
]

# ---------------------------------------------------------------------------
# 共享样式
# ---------------------------------------------------------------------------
BASE_CSS = """
    :root {
      --paper: #f4eddc; --paper-light: #fffaf0; --ink: #191917;
      --red: #e64a38; --yellow: #f1bd32; --blue: #2858b8; --green: #739348; --brown: #8b5e3c;
      --line: 3px solid var(--ink); --shadow: 7px 7px 0 var(--ink);
      --serif: "Noto Serif CJK SC", "Source Han Serif SC", "Songti SC", SimSun, serif;
      --sans: "PingFang SC", "Microsoft YaHei", system-ui, -apple-system, sans-serif;
    }
    *, *::before, *::after { box-sizing: border-box; }
    html { scroll-behavior: smooth; }
    body {
      margin: 0; color: var(--ink); background-color: var(--paper);
      background-image: radial-gradient(circle, rgba(25,25,23,.18) .8px, transparent .9px);
      background-size: 9px 9px; font-family: var(--sans); font-size: 16px; line-height: 1.7;
      overflow-x: clip;
    }
    [hidden] { display: none !important; }
    a { color: inherit; } a, button { -webkit-tap-highlight-color: transparent; cursor: pointer; }
    button, input, select { font: inherit; }
    svg { display: block; max-width: 100%; }
    h1, h2, h3, p { margin-top: 0; }
    section { scroll-margin-top: 104px; }
    ::selection { color: var(--paper-light); background: var(--blue); }
    :focus-visible { outline: 4px solid var(--blue); outline-offset: 4px; }
    .shell { width: min(calc(100% - 48px), 1240px); margin-inline: auto; }
    .site-header { position: sticky; z-index: 30; top: 0; border-bottom: var(--line); background-color: var(--paper); background-image: radial-gradient(circle, rgba(25,25,23,.16) .8px, transparent .9px); background-size: 9px 9px; }
    .header-inner { min-height: 80px; display: flex; align-items: center; gap: 22px; }
    .brand { display: inline-flex; align-items: center; min-height: 48px; margin-right: auto; text-decoration: none; font-family: var(--serif); font-size: 24px; font-weight: 900; letter-spacing: .08em; white-space: nowrap; }
    .brand small { margin-left: 11px; padding-left: 11px; border-left: 2px solid var(--ink); font-family: var(--sans); font-size: 11px; font-weight: 700; line-height: 1.25; letter-spacing: .08em; }
    .desktop-nav { display: flex; align-items: center; gap: 2px; flex-wrap: wrap; }
    .desktop-nav a, .mobile-nav a { display: inline-flex; align-items: center; justify-content: center; min-height: 44px; padding: 8px 11px; text-decoration: none; font-weight: 800; font-size: 15px; }
    .desktop-nav a:hover { text-decoration: underline 3px var(--red); text-underline-offset: 6px; }
    .desktop-nav a[aria-current="page"], .mobile-nav a[aria-current="page"] { text-decoration: underline 3px var(--red); text-underline-offset: 6px; }
    .menu-toggle { display: none; width: 48px; height: 48px; padding: 11px; border: var(--line); background: var(--yellow); box-shadow: 3px 3px 0 var(--ink); }
    .menu-toggle span { display: block; width: 100%; height: 2px; margin: 4px 0; background: var(--ink); }
    .mobile-nav { padding: 8px 0 18px; border-top: 2px solid var(--ink); }
    .mobile-nav a { width: 100%; justify-content: flex-start; border-bottom: 1px dashed var(--ink); }
    .button { min-height: 48px; display: inline-flex; align-items: center; justify-content: center; gap: 10px; padding: 11px 22px; border: var(--line); background: var(--paper-light); box-shadow: 4px 4px 0 var(--ink); font-weight: 800; line-height: 1.35; text-decoration: none; transition: translate .16s ease, box-shadow .16s ease; }
    .button:hover { translate: -2px -2px; box-shadow: 6px 6px 0 var(--ink); }
    .button:active { translate: 3px 3px; box-shadow: 1px 1px 0 var(--ink); }
    .button-primary { background: var(--yellow); }
    .button svg { width: 20px; height: 20px; flex: 0 0 auto; }
    .eyebrow { display: inline-block; margin-bottom: 20px; padding: 5px 13px; border: 2px solid var(--ink); background: var(--paper-light); box-shadow: 3px 3px 0 var(--ink); font-size: 14px; font-weight: 800; letter-spacing: .12em; transform: rotate(-2deg); }
    .site-footer { margin-top: 34px; padding-block: 30px 40px; border-top: var(--line); background: var(--ink); color: var(--paper-light); }
    .site-footer p { margin: 0; font-size: 13px; opacity: .82; }
    .site-footer a { text-decoration: underline; }
    @media (max-width: 1080px) { .desktop-nav a { padding-inline: 8px; font-size: 14px; } }
    @media (max-width: 900px) { .desktop-nav { display: none; } .menu-toggle { display: block; } .header-inner { gap: 12px; } }
"""

LINK_CSS = """
    /* ===== LIBRARY_LINKS:CSS ===== */
    .lib-map { padding-block: 26px 54px; }
    .lib-map-box { border: var(--line); background: var(--paper-light); box-shadow: var(--shadow); padding: 26px 26px 22px; }
    .lib-map-box h2 { font-family: var(--serif); font-size: clamp(24px, 3vw, 32px); font-weight: 900; margin-bottom: 6px; }
    .lib-map-box > p { font-size: 14px; color: #4a4841; margin-bottom: 20px; }
    .lib-halls { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; }
    .lib-hall { display: flex; flex-direction: column; gap: 4px; padding: 14px 14px 12px; border: var(--line); background: var(--paper-light); box-shadow: 4px 4px 0 var(--ink); text-decoration: none; transition: translate .15s ease, box-shadow .15s ease; }
    .lib-hall:hover { translate: -2px -2px; box-shadow: 6px 6px 0 var(--ink); }
    .lib-hall b { font-family: var(--serif); font-size: 20px; font-weight: 900; }
    .lib-hall span { font-size: 12px; line-height: 1.5; color: #4a4841; }
    .lib-hall.lib-story { background: #fbe3dd; }
    .lib-hall.lib-music { background: #fdf1c9; }
    .lib-hall.lib-poetry { background: #e2ebd7; }
    .lib-hall.lib-research { background: #dde5f6; }
    .lib-hall[aria-current="page"] { outline: 3px dashed var(--ink); outline-offset: 3px; }
    .lib-specs { margin-top: 20px; padding-top: 16px; border-top: 2px dashed var(--ink); display: flex; flex-wrap: wrap; align-items: center; gap: 8px; }
    .lib-specs > strong { font-size: 13px; margin-right: 4px; }
    .lib-specs a { padding: 4px 10px; border: 2px solid var(--ink); background: var(--paper-light); box-shadow: 2px 2px 0 var(--ink); font-size: 12px; font-weight: 800; text-decoration: none; }
    .lib-specs a:hover { background: var(--yellow); }
    .lib-specs a[aria-current="page"] { background: var(--yellow); }
    .lib-more { margin-top: 16px; display: flex; flex-wrap: wrap; gap: 16px; font-size: 13px; font-weight: 800; }
    .lib-more a { text-decoration: underline 2px var(--blue); text-underline-offset: 4px; }
    .lib-peers { padding-block: 6px 26px; }
    .lib-peers-inner { border: var(--line); background: var(--paper-light); box-shadow: 4px 4px 0 var(--ink); padding: 16px 18px; }
    .lib-peers-inner > strong { display: block; font-size: 13px; margin-bottom: 10px; }
    .lib-peer-list { display: flex; flex-wrap: wrap; gap: 8px; }
    .lib-peer-list a { padding: 5px 10px; border: 2px solid var(--ink); background: var(--paper-light); font-size: 12px; font-weight: 800; text-decoration: none; }
    .lib-peer-list a:hover { background: var(--yellow); }
    .lib-peer-list a[aria-current="page"] { background: var(--yellow); box-shadow: 2px 2px 0 var(--ink); }
    .lib-peer-ends { display: flex; justify-content: space-between; gap: 12px; margin-top: 14px; font-size: 13px; font-weight: 800; }
    .lib-peer-ends a { text-decoration: none; border-bottom: 2px solid var(--ink); }
    .lib-peer-ends .spacer { flex: 1; }
    @media (max-width: 1000px) { .lib-halls { grid-template-columns: repeat(2, 1fr); } }
    @media (max-width: 640px) {
      .lib-halls { grid-template-columns: 1fr; }
      .lib-map-box { padding: 20px 16px 18px; }
      .shell { width: min(calc(100% - 32px), 1240px); }
    }
    .work-spec-links { margin-top: 18px; padding: 12px 14px; border: 2px dashed var(--ink); background: #dde5f6; font-size: 13px; }
    .work-spec-links > strong { display: block; margin-bottom: 8px; }
    .work-spec-links div { display: flex; flex-wrap: wrap; gap: 8px; }
    .work-spec-links a { padding: 3px 9px; border: 2px solid var(--ink); background: var(--paper-light); box-shadow: 2px 2px 0 var(--ink); font-weight: 800; text-decoration: none; }
    .work-spec-links a:hover { background: var(--yellow); }
    /* ===== /LIBRARY_LINKS:CSS ===== */
"""

HALL_CSS = """
    .hero { padding-block: 48px 26px; }
    .hero h1 { font-family: var(--serif); font-size: clamp(40px, 5vw, 62px); font-weight: 900; line-height: 1.16; letter-spacing: -.04em; margin-bottom: 16px; }
    .hero h1 .accent { color: var(--red); }
    .hero-desc { max-width: 760px; font-size: 17px; line-height: 1.9; margin-bottom: 22px; }
    .hero-actions { display: flex; flex-wrap: wrap; gap: 14px; }
    .stat-strip { display: grid; grid-template-columns: repeat(4, 1fr); border: var(--line); background: var(--paper-light); box-shadow: 5px 5px 0 var(--blue); margin-top: 30px; }
    .stat-cell { padding: 16px 18px; border-right: 2px solid var(--ink); }
    .stat-cell:last-child { border-right: 0; }
    .stat-cell b { display: block; font-family: var(--serif); font-size: 27px; font-weight: 900; line-height: 1.2; }
    .stat-cell span { font-size: 12px; color: #4a4841; }
    .notice { margin-top: 24px; padding: 14px 18px; border: 2px solid var(--ink); background: #dde5f6; box-shadow: 4px 4px 0 var(--ink); font-size: 14px; line-height: 1.75; }
    .notice b { color: var(--blue); }
    .toolbar { padding-block: 26px 8px; }
    .toolbar-inner { display: flex; flex-wrap: wrap; gap: 12px; align-items: center; padding: 14px 16px; border: var(--line); background: var(--paper-light); box-shadow: 4px 4px 0 var(--ink); }
    .toolbar label { font-size: 13px; font-weight: 800; }
    .toolbar input[type="search"], .toolbar select { min-height: 42px; padding: 8px 12px; border: 2px solid var(--ink); background: var(--paper-light); font-size: 14px; }
    .toolbar input[type="search"] { flex: 1 1 240px; }
    .toolbar .result-count { margin-left: auto; font-size: 13px; font-weight: 800; }
    .group-nav { padding-block: 16px 4px; display: flex; flex-wrap: wrap; gap: 8px; }
    .group-nav a { padding: 5px 11px; border: 2px solid var(--ink); background: var(--paper-light); box-shadow: 2px 2px 0 var(--ink); font-size: 12px; font-weight: 800; text-decoration: none; }
    .group-nav a:hover { background: var(--yellow); }
    .group-section { padding-block: 26px 12px; }
    .group-head { border-bottom: 2px dashed var(--ink); padding-bottom: 12px; margin-bottom: 20px; }
    .group-head .no { font-size: 12px; font-weight: 900; letter-spacing: .12em; }
    .group-head h2 { font-family: var(--serif); font-size: clamp(25px, 3vw, 32px); font-weight: 900; margin: 4px 0 6px; }
    .group-head h2 small { font-family: var(--sans); font-size: 14px; font-weight: 800; margin-left: 10px; color: #4a4841; }
    .group-head p { margin: 0; font-size: 14px; color: #4a4841; max-width: 900px; }
    .group-head .focus { margin-top: 6px; font-size: 13px; font-weight: 800; }
    .rec-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
    .rec-card { border: var(--line); background: var(--paper-light); box-shadow: 4px 4px 0 var(--ink); padding: 14px 15px 12px; display: flex; flex-direction: column; gap: 6px; }
    .rec-card .rid { font-size: 11px; font-weight: 900; color: var(--blue); letter-spacing: .08em; }
    .rec-card h3 { font-family: var(--serif); font-size: 19px; font-weight: 900; line-height: 1.4; margin: 0; }
    .rec-card .meta { font-size: 12px; color: #4a4841; }
    .rec-tags { display: flex; flex-wrap: wrap; gap: 5px; margin-top: 2px; }
    .rec-tags span { padding: 1px 7px; border: 2px solid var(--ink); background: var(--yellow); font-size: 10px; font-weight: 800; }
    .rec-tags span.warn { background: #dde5f6; }
    .rec-card details { margin-top: 6px; border-top: 2px dashed var(--ink); padding-top: 8px; font-size: 13px; }
    .rec-card summary { font-weight: 800; cursor: pointer; }
    .rec-card details p { margin: 8px 0 0; line-height: 1.65; color: #33322e; }
    .rec-card details a { text-decoration: underline 2px var(--blue); text-underline-offset: 3px; font-weight: 800; }
    .status-list { display: grid; grid-template-columns: auto 1fr; gap: 3px 10px; margin: 8px 0 0; font-size: 12px; }
    .status-list dt { font-weight: 800; font-family: monospace; }
    .status-list dd { margin: 0; }
    .model-band { padding-block: 30px 20px; }
    .model-box { border: var(--line); background: var(--paper-light); box-shadow: var(--shadow); padding: 24px 24px 18px; }
    .model-box h2 { font-family: var(--serif); font-size: 27px; font-weight: 900; margin-bottom: 6px; }
    .model-box > p { font-size: 14px; color: #4a4841; margin-bottom: 16px; }
    .model-table { width: 100%; border-collapse: collapse; font-size: 13px; }
    .model-table th, .model-table td { border: 2px solid var(--ink); padding: 8px 10px; text-align: left; vertical-align: top; }
    .model-table th { background: var(--yellow); font-weight: 900; }
    .model-table code { font-family: monospace; font-weight: 800; }
    .model-box .button { margin-top: 18px; }
    @media (max-width: 1000px) { .rec-grid { grid-template-columns: repeat(2, 1fr); } }
    @media (max-width: 640px) {
      .stat-strip { grid-template-columns: repeat(2, 1fr); }
      .stat-cell:nth-child(2) { border-right: 0; }
      .stat-cell:nth-child(-n+2) { border-bottom: 2px solid var(--ink); }
      .rec-grid { grid-template-columns: 1fr; }
      .hero { padding-block: 34px 20px; }
      .model-box { padding: 18px 14px 14px; }
      .model-table { font-size: 12px; }
    }
"""

RESEARCH_CSS = """
    .hero { padding-block: 48px 26px; }
    .hero h1 { font-family: var(--serif); font-size: clamp(40px, 5vw, 60px); font-weight: 900; line-height: 1.16; letter-spacing: -.04em; margin-bottom: 16px; }
    .hero h1 .accent { color: var(--blue); }
    .hero-desc { max-width: 780px; font-size: 17px; line-height: 1.9; margin-bottom: 20px; }
    .quote { padding: 16px 20px; border: var(--line); background: var(--yellow); box-shadow: var(--shadow); font-family: var(--serif); font-size: 19px; font-weight: 900; max-width: 820px; }
    .section { padding-block: 26px 10px; }
    .section h2 { font-family: var(--serif); font-size: clamp(26px, 3.2vw, 34px); font-weight: 900; margin-bottom: 8px; }
    .section > p { font-size: 15px; color: #4a4841; max-width: 860px; }
    .layer-row { display: grid; grid-template-columns: repeat(2, 1fr); gap: 18px; margin-top: 18px; }
    .layer { border: var(--line); background: var(--paper-light); box-shadow: var(--shadow); padding: 20px 20px 16px; }
    .layer.research { background: #dde5f6; }
    .layer.library { background: #e2ebd7; }
    .layer .kicker { font-size: 12px; font-weight: 900; letter-spacing: .1em; }
    .layer h3 { font-family: var(--serif); font-size: 23px; font-weight: 900; margin: 4px 0 8px; }
    .layer p { font-size: 14px; margin: 0 0 8px; }
    .layer ul { margin: 0; padding-left: 20px; font-size: 14px; }
    .dash { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-top: 18px; }
    .dash-cell { border: var(--line); background: var(--paper-light); box-shadow: 4px 4px 0 var(--ink); padding: 15px 16px; }
    .dash-cell b { display: block; font-family: var(--serif); font-size: 30px; font-weight: 900; line-height: 1.2; }
    .dash-cell span { font-size: 12px; color: #4a4841; }
    .dash-cell small { display: block; margin-top: 6px; font-size: 11px; color: #55534b; }
    .data-table { width: 100%; border-collapse: collapse; font-size: 13px; margin-top: 16px; }
    .data-table th, .data-table td { border: 2px solid var(--ink); padding: 9px 11px; text-align: left; vertical-align: top; }
    .data-table th { background: var(--yellow); font-weight: 900; }
    .data-table code { font-family: monospace; font-weight: 800; }
    .data-table a { text-decoration: underline 2px var(--blue); text-underline-offset: 3px; font-weight: 800; }
    .flow { counter-reset: step; list-style: none; padding: 0; margin: 18px 0 0; display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
    .flow li { counter-increment: step; border: 2px solid var(--ink); background: var(--paper-light); box-shadow: 3px 3px 0 var(--ink); padding: 12px 12px 12px 40px; font-size: 13px; position: relative; }
    .flow li::before { content: counter(step); position: absolute; left: 10px; top: 10px; width: 22px; height: 22px; display: grid; place-items: center; border: 2px solid var(--ink); background: var(--yellow); font-weight: 900; font-size: 12px; }
    .boundary { margin-top: 18px; border: var(--line); background: #fbe3dd; box-shadow: var(--shadow); padding: 20px 20px 14px; }
    .boundary h3 { font-family: var(--serif); font-size: 21px; font-weight: 900; }
    .boundary ul { margin: 0; padding-left: 20px; font-size: 14px; }
    .boundary li { margin-bottom: 6px; }
    .boundary a { text-decoration: underline 2px var(--blue); text-underline-offset: 3px; font-weight: 800; }
    .table-scroll { overflow-x: auto; margin-top: 16px; }
    .table-scroll .data-table { margin-top: 0; min-width: 620px; }
    @media (max-width: 1000px) { .flow { grid-template-columns: repeat(2, 1fr); } .dash { grid-template-columns: repeat(2, 1fr); } }
    @media (max-width: 640px) {
      .layer-row { grid-template-columns: 1fr; }
      .flow { grid-template-columns: 1fr; }
      .hero { padding-block: 34px 20px; }
      .data-table { font-size: 12px; }
    }
"""


# ---------------------------------------------------------------------------
# 共享 HTML 片段
# ---------------------------------------------------------------------------
def nav_links(current: str) -> str:
    out = []
    for href, label in NAV_ITEMS:
        aria = ' aria-current="page"' if href == current else ""
        out.append(f'<a href="{href}"{aria}>{E(label)}</a>')
    return "\n        ".join(out)


def header_html(current: str) -> str:
    links = nav_links(current)
    return f"""  <header class="site-header">
    <div class="shell header-inner">
      <a class="brand" href="dir-3.html" aria-label="返回童年书房首页">童年书房<small>CHILDHOOD<br>LIBRARY</small></a>
      <nav class="desktop-nav" aria-label="主导航">
        {links}
      </nav>
      <button class="menu-toggle" id="menu-toggle" type="button" aria-expanded="false" aria-controls="mobile-nav" aria-label="展开导航">
        <span></span><span></span><span></span>
      </button>
    </div>
    <nav class="shell mobile-nav" id="mobile-nav" aria-label="移动端导航" hidden>
      {links}
    </nav>
  </header>"""


def map_html(current: str) -> str:
    halls = [
        ("lib-story", "story.html", "故事馆", "六个专题 · 100 条研究记录"),
        ("lib-music", "music.html", "音乐馆", "八专题 · 105 条发现目录"),
        ("lib-poetry", "poetry.html", "古诗词馆", "十个专题 · 60 条研究记录"),
        ("lib-research", "research.html", "研究资源库", "五维状态 · 来源与边界"),
    ]
    cards = "\n".join(
        f'<a class="lib-hall {cls}" href="{href}"{(" aria-current="+chr(34)+"page"+chr(34)) if href == current else ""}>'
        f'<b>{E(name)}</b><span>{E(desc)}</span></a>'
        for cls, href, name, desc in halls
    )
    specs = "\n".join(
        f'<a href="specialty-{key}.html"{(" aria-current="+chr(34)+"page"+chr(34)) if f"specialty-{key}.html" == current else ""}>{E(label)}</a>'
        for key, label in SPECS
    )
    return f"""<!-- LIBRARY_LINKS:MAP -->
    <section class="shell lib-map" aria-labelledby="lib-map-title">
      <div class="lib-map-box">
        <h2 id="lib-map-title">全站地图 · 三馆与研究层</h2>
        <p>童年书房分为研究资源库（Research）与儿童使用层（Library）。三馆目录可以互相跳转，音乐馆八个专题横向串联，作品目录可回链到专题与研究层。</p>
        <div class="lib-halls">
{cards}
        </div>
        <div class="lib-specs">
          <strong>音乐馆八专题：</strong>
{specs}
        </div>
        <div class="lib-more">
          <a href="works.html">作品目录（音乐馆 105 条）</a>
          <a href="../docs/PROJECT_PRINCIPLES.md">项目顶层原则</a>
          <a href="../docs/DATA_MODEL.md">统一数据模型</a>
          <a href="../docs/COPYRIGHT_POLICY.md">来源与权利说明</a>
        </div>
      </div>
    </section>
    <!-- /LIBRARY_LINKS:MAP -->"""


def peers_html(current_key: str) -> str:
    keys = [key for key, _ in SPECS]
    idx = keys.index(current_key)
    prev_key = keys[(idx - 1) % len(keys)]
    next_key = keys[(idx + 1) % len(keys)]
    label = dict(SPECS)
    items = "\n".join(
        f'<a href="specialty-{key}.html"{(" aria-current="+chr(34)+"page"+chr(34)) if key == current_key else ""}>{E(name)}</a>'
        for key, name in SPECS
    )
    return f"""<!-- LIBRARY_LINKS:PEERS -->
    <nav class="shell lib-peers" aria-label="八个专题横向导航">
      <div class="lib-peers-inner">
        <strong>音乐馆 · 八个专题串联</strong>
        <div class="lib-peer-list">
{items}
        </div>
        <div class="lib-peer-ends">
          <a href="specialty-{prev_key}.html">← 上一专题：{E(label[prev_key])}</a>
          <span class="spacer"></span>
          <a href="specialty-{next_key}.html">下一专题：{E(label[next_key])} →</a>
        </div>
      </div>
    </nav>
    <!-- /LIBRARY_LINKS:PEERS -->"""


def dialog_links_html() -> str:
    return """<!-- LIBRARY_LINKS:DIALOG -->
        <nav class="work-spec-links" id="work-spec-links" aria-label="该作品所属专题" hidden>
          <strong>所属专题 · 回看策展页</strong>
          <div id="work-spec-link-list"></div>
        </nav>
        <!-- /LIBRARY_LINKS:DIALOG -->"""


def work_spec_script() -> str:
    """作品详情 -> 所属专题：旁路注入，不改动 works 原有详情渲染逻辑。"""
    data = load_json(ROOT / "specialties.json", {"works": []})
    mapping = {w["id"]: w.get("specialties", []) for w in data.get("works", [])}
    labels = dict(SPECS)
    payload_map = json.dumps(mapping, ensure_ascii=False, separators=(",", ":"))
    payload_labels = json.dumps(labels, ensure_ascii=False, separators=(",", ":"))
    return f"""<!-- LIBRARY_LINKS:WORKSPECS -->
  <script>
  (() => {{
    const map = {payload_map};
    const labels = {payload_labels};
    function render() {{
      const nav = document.getElementById('work-spec-links');
      const box = document.getElementById('work-spec-link-list');
      if (!nav || !box) return;
      const m = /^#work-(.+)$/.exec(location.hash || '');
      const keys = (m && map[m[1]]) ? map[m[1]] : [];
      if (!keys.length) {{ nav.hidden = true; box.textContent = ''; return; }}
      box.textContent = '';
      keys.forEach(k => {{
        if (!labels[k]) return;
        const a = document.createElement('a');
        a.setAttribute('href', 'specialty-' + k + '.html');
        a.textContent = labels[k];
        box.appendChild(a);
      }});
      nav.hidden = false;
    }}
    window.addEventListener('hashchange', render);
    render();
  }})();
  </script>
  <!-- /LIBRARY_LINKS:WORKSPECS -->"""


def footer_html(note: str) -> str:
    return f"""  <footer class="site-footer">
    <div class="shell">
      <p>{E(note)}</p>
      <p>本页为内部研究与原型展示视图。候选目录不构成法律意见，也不授予任何第三方内容的使用权；具体公开、复制、翻译、改编、插画和音频使用，按目标发布地域、具体版本和实际许可逐项核实。</p>
    </div>
  </footer>"""


def page_shell(title: str, desc: str, current: str, css: str, main: str, footer_note: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="{E(desc)}">
  <title>{E(title)}｜童年书房</title>
  <style>
{BASE_CSS}{LINK_CSS}{css}  </style>
</head>
<body id="top">
{header_html(current)}

  <main id="main">
{main}
{map_html(current)}
  </main>
{footer_html(footer_note)}

  <script>
    (() => {{
      const t = document.getElementById('menu-toggle');
      const n = document.getElementById('mobile-nav');
      if (t && n) t.addEventListener('click', () => {{
        const e = t.getAttribute('aria-expanded') === 'true';
        t.setAttribute('aria-expanded', String(!e)); n.hidden = e;
      }});
    }})();
  </script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# 三馆页面
# ---------------------------------------------------------------------------
def status_tags(record: dict, labels: dict) -> str:
    keys = ["researchStatus", "rightsStatus", "qualityStatus", "accessMethod", "publicationStatus"]
    out = []
    for key in keys:
        value = record[key]
        label = labels.get(value, value)
        cls = " warn" if key in ("rightsStatus", "publicationStatus") else ""
        out.append(f'<span class="{cls.strip()}" title="{E(key)}">{E(label)}</span>')
    return "".join(out)


def card_html(record: dict, labels: dict, accent: str) -> str:
    search = " ".join([
        record["id"], record["title"], record["contributor"], record["origin"],
        record["note"], record["groupName"],
    ]).lower()
    kind = "征集选题" if record["isTopic"] else ("版本 / 资产线索" if record["isAsset"] else "作品线索")
    status_rows = "\n".join(
        f"<dt>{E(key)}</dt><dd>{E(record[field])} · {E(labels.get(record[field], ''))}</dd>"
        for field, key in [
            ("researchStatus", "research_status"), ("rightsStatus", "rights_status"),
            ("qualityStatus", "quality_status"), ("accessMethod", "access_method"),
            ("publicationStatus", "publication_status"),
        ]
    )
    source_url = record["sourceUrl"]
    source_link = (
        f'<a href="{E(source_url)}" target="_blank" rel="noopener noreferrer">{E(record["sourceName"])} ↗</a>'
        if source_url.startswith("http")
        else f'<a href="{E(source_url)}">{E(record["sourceName"])} ↗</a>'
    )
    return f"""<article class="rec-card" data-group="{E(record['group'])}" data-search="{E(search)}">
      <span class="rid">{E(record['id'])} · {E(kind)}</span>
      <h3>{E(record['title'])}</h3>
      <span class="meta">{E(record['origin'])} · {E(record['contributor'])}</span>
      <span class="meta">适读 {E(record['ageBand'])} 岁 · {E(record['groupName'])}</span>
      <div class="rec-tags">{status_tags(record, labels)}</div>
      <details>
        <summary>研究备注与来源线索</summary>
        <p><b>待核验事项：</b>{E(record['note'])}</p>
        <p><b>来源线索：</b>{source_link}（机构/栏目入口，具体作品页面待逐条考证）</p>
        <p><b>资产边界：</b>{E(record['assetNote'])}</p>
        <dl class="status-list">{status_rows}</dl>
      </details>
    </article>"""


def render_hall(hall: str, data: dict) -> str:
    labels = data["statusLabels"]
    is_story = hall == "story"
    name = "儿童故事馆" if is_story else "古诗词馆"
    eyebrow = "STORY HALL · 研究目录" if is_story else "POETRY HALL · 研究目录"
    desc = (
        "以中国经典为根，以世界文学为窗，以优秀原创为未来的儿童文学图书馆。"
        if is_story
        else "古典诗词、儿童诗、民间歌谣，以及不同译注、吟诵与朗诵版本的儿童诗歌档案。"
    )
    intro = (
        "这里登记的是<b>研究候选目录</b>：作品身份、文化来源、来源线索与待核验事项。"
        "按《项目顶层设计原则》「先研究采集，再判断使用」，版权状态未知的作品同样登记，不因尚未核实权利就被排除。"
        if is_story
        else "这里按主题与<b>版本层级</b>登记研究线索：作品文本、译注、绘本、吟诵与朗诵分别建档，"
        "不把某个录音或绘本误当成作品本身。作品文本通常属古典公版范畴，但本项目尚未逐条完成地区与版本证据归档，"
        "因此权利状态一律记为 pending，不自动标为已核验。"
    )
    stats = data["stats"][hall]
    groups = [g for g in data["groups"] if g["hall"] == hall]

    group_nav = "\n".join(
        f'<a href="#group-{E(g["id"])}">{E(g["no"])} {E(g["name"])}</a>' for g in groups
    )
    sections = []
    for g in groups:
        rows = [r for r in data["records"] if r["hall"] == hall and r["group"] == g["id"]]
        cards = "\n".join(card_html(r, labels, g["accent"]) for r in rows)
        kind_note = (
            '<span class="focus">本组为编辑征集方向，不是已登记作品；进入目录前须经编辑评审并取得清晰授权。</span>'
            if g.get("isTopic")
            else ('<span class="focus">本组为版本 / 媒体资产层线索，不是独立作品。</span>' if g.get("isAsset") else "")
        )
        sections.append(f"""    <section class="shell group-section" id="group-{E(g['id'])}" data-group-section="{E(g['id'])}">
      <div class="group-head">
        <span class="no" style="color:{E(g['accent'])}">{E(g['no'])} · {E(eyebrow)}</span>
        <h2>{E(g['name'])}<small>{len(rows)} 条线索 / 规划目标 {g['target']} 条</small></h2>
        <p>{E(g['desc'])}</p>
        <p class="focus">编辑关注：{E(g['focus'])}</p>
        {kind_note}
      </div>
      <div class="rec-grid">
{cards}
      </div>
    </section>""")

    model_rows = "\n".join(
        f"<tr><td><code>{E(m['field'])}</code></td><td>{E(m['values'])}</td><td>{E(m['question'])}</td></tr>"
        for m in data["statusModel"]
    )
    filter_options = "\n".join(
        f'<option value="{E(g["id"])}">{E(g["no"])} {E(g["name"])}</option>' for g in groups
    )

    main = f"""    <section class="shell hero" aria-labelledby="page-title">
      <span class="eyebrow">{E(eyebrow)}</span>
      <h1 id="page-title">{E(name)} · <span class="accent">{'让好故事陪伴童年' if is_story else '把诗，读成声音与画面'}</span></h1>
      <p class="hero-desc">{E(desc)} 目前按{'《儿童故事馆建设方案》§2 / §9' if is_story else '《项目顶层设计原则》§3 儿童诗歌与诗词范围'}建立研究目录，共 {stats['groups']} 个专题、{stats['total']} 条研究记录。</p>
      <div class="hero-actions">
        <a class="button button-primary" href="research.html">看研究资源库与五维状态
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true"><path d="M5 12h14M14 6l6 6-6 6"/></svg>
        </a>
        <a class="button" href="#groups">按专题浏览</a>
      </div>
      <div class="stat-strip">
        <div class="stat-cell"><b>{stats['total']}</b><span>研究记录总数</span></div>
        <div class="stat-cell"><b>{stats['groups']}</b><span>一级专题</span></div>
        <div class="stat-cell"><b>{stats['works']}</b><span>作品 / 题材线索</span></div>
        <div class="stat-cell"><b>{stats['topics'] + stats['assets']}</b><span>征集方向 / 版本资产线索</span></div>
      </div>
      <div class="notice"><b>这一页是「研究资源库」视图，不是儿童阅读页。</b>{intro} 所有记录当前 <code>publication_status = draft</code>、<code>quality_status = unreviewed</code>，页面不展示任何正文、译文、插画或音视频。</div>
    </section>

    <section class="shell toolbar" id="groups" aria-label="目录筛选">
      <div class="toolbar-inner">
        <label for="hall-search">检索目录</label>
        <input type="search" id="hall-search" placeholder="输入作品、作者或编号" autocomplete="off">
        <label for="hall-group">专题</label>
        <select id="hall-group"><option value="all">全部专题</option>{filter_options}</select>
        <span class="result-count" id="hall-visible">显示 {stats['total']} / {stats['total']} 条</span>
      </div>
      <nav class="group-nav" aria-label="专题快捷导航">{group_nav}</nav>
    </section>

{chr(10).join(sections)}

    <section class="shell model-band" aria-labelledby="model-title">
      <div class="model-box">
        <h2 id="model-title">统一状态模型 · 五个维度互不替代</h2>
        <p>研究完成不等于版权已确认；版权确认不等于质量审核通过；内容适合儿童也不等于获得公开传播许可。依据《项目顶层设计原则》§6 与《数据模型设计》§4。</p>
        <table class="model-table">
          <thead><tr><th>字段</th><th>建议状态</th><th>回答的问题</th></tr></thead>
          <tbody>{model_rows}</tbody>
        </table>
        <a class="button" href="research.html#dashboard">查看研究状态看板</a>
      </div>
    </section>"""

    filter_js = """
    (() => {
      const q = document.getElementById('hall-search');
      const g = document.getElementById('hall-group');
      const out = document.getElementById('hall-visible');
      const cards = [...document.querySelectorAll('.rec-card')];
      const sections = [...document.querySelectorAll('[data-group-section]')];
      const total = cards.length;
      function apply() {
        const needle = (q.value || '').trim().toLowerCase();
        const group = g.value;
        let visible = 0;
        cards.forEach(card => {
          const ok = (!needle || card.dataset.search.includes(needle)) && (group === 'all' || card.dataset.group === group);
          card.hidden = !ok;
          if (ok) visible += 1;
        });
        sections.forEach(sec => {
          sec.hidden = [...sec.querySelectorAll('.rec-card')].every(card => card.hidden);
        });
        out.textContent = `显示 ${visible} / ${total} 条`;
      }
      q.addEventListener('input', apply);
      g.addEventListener('change', apply);
    })();
"""

    html = page_shell(
        name, desc, f"{hall}.html", HALL_CSS, main,
        f"{name}研究目录 · 依据项目顶层原则与统一数据模型建立，{data['generatedOn']} 生成。",
    )
    return html.replace("  </script>\n</body>", "  " + filter_js + "  </script>\n</body>")


# ---------------------------------------------------------------------------
# 研究资源库
# ---------------------------------------------------------------------------
def load_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def research_stats(data: dict) -> dict:
    specialties = load_json(ROOT / "specialties.json", {"works": []})
    samples = load_json(ROOT / "audio" / "samples.json", [])
    official = load_json(ROOT / "audio" / "official-recordings.json", [])
    collection = load_json(ROOT / "audio" / "public-recording-collection.json", {})
    materials = load_json(ROOT / "china-materials.json", {})
    world_materials = load_json(ROOT / "world-materials.json", [])
    world_clues = load_json(ROOT / "world-audio-clues.json", {})
    versions = sum(1 + len(s.get("variants", [])) for s in samples)
    # 与 build_works.py:149 / integrate_public_recordings.py:117 一致：
    # 早期 3 条 CC 开放许可录音未显式写 sampleType，按项目既有缺省口径计为 open。
    types = Counter(s.get("sampleType", "open") for s in samples)
    return {
        "musicWorks": len(specialties.get("works", [])),
        "materials": len(materials),
        "worldMaterials": len(world_materials),
        "materialTotal": len(materials) + len(world_materials),
        "worldAudioClues": len(world_clues.get("verifiedCandidates", [])),
        "samples": len(samples),
        "versions": versions,
        "types": dict(types),
        "official": len(official) if isinstance(official, list) else len(official.get("recordings", [])),
        "files": collection.get("fileCount", 0),
        "mappings": collection.get("workMappingCount", 0),
        "story": data["stats"]["story"]["total"],
        "poetry": data["stats"]["poetry"]["total"],
    }


def render_research(data: dict) -> str:
    s = research_stats(data)
    labels = data["statusLabels"]
    model_rows = "\n".join(
        f"<tr><td><code>{E(m['field'])}</code></td><td>{E(m['values'])}</td><td>{E(m['question'])}</td><td>{E(m['note'])}</td></tr>"
        for m in data["statusModel"]
    )
    sources = [
        ("中国国家图书馆", "https://www.nlc.cn/", "中国故事源流、地方异文、古籍与诗词版本"),
        ("中国非物质文化遗产网", "https://www.ihchina.cn/", "口传童谣、吟诵调、地方采录线索"),
        ("Project Gutenberg", "https://www.gutenberg.org/", "世界儿童文学历史版本与书目发现"),
        ("International Children's Digital Library", "http://www.childrenslibrary.org/", "多语言儿童书籍发现"),
        ("Library of Congress", "https://www.loc.gov/", "书目、历史馆藏与版本考证"),
        ("StoryWeaver", "https://storyweaver.org.in/", "开放许可故事；许可需逐本核验"),
    ]
    source_rows = "\n".join(
        f"<tr><td>{E(name)}</td><td><a href=\"{E(url)}\" target=\"_blank\" rel=\"noopener noreferrer\">机构入口 ↗</a></td><td>{E(use)}</td></tr>"
        for name, url, use in sources
    )
    flow_items = [
        "发现作品或来源线索", "登记候选作品与来源，不因权利未知丢弃", "核实身份、作者、版本、年代与文化背景",
        "内容质量与儿童适宜性评估", "逐项核验正文、译文、插画、录音、视频权利",
        "按使用方式选择外链、官方嵌入、授权媒体或仅保留目录", "人工审核后发布", "授权或来源变化时重新评估",
    ]
    flow_html = "\n".join(f"<li>{E(item)}</li>" for item in flow_items)

    # 剩余非原曲测试音：线索表必须与 samples.json 的 generated 集合逐条对齐
    samples = load_json(ROOT / "audio" / "samples.json", [])
    generated_ids = [x["id"] for x in samples if x.get("sampleType") == "generated"]
    clue_ids = [i for group in REPLACEMENT_CLUES for i in group["ids"]]
    if len(clue_ids) != len(set(clue_ids)) or set(clue_ids) != set(generated_ids):
        raise ValueError(
            "Replacement clues must match remaining generated works exactly; "
            f"missing={sorted(set(generated_ids) - set(clue_ids))}, "
            f"stale={sorted(set(clue_ids) - set(generated_ids))}"
        )
    replacement_rows = "\n".join(
        "<tr><td><b>{}</b></td><td>{} 首</td><td><code>{}</code></td><td>{}</td><td>{}</td></tr>".format(
            E(group["label"]), len(group["ids"]), E(", ".join(group["ids"])),
            E(group["finding"]),
            "<br>".join(
                '<a href="{}" target="_blank" rel="noopener noreferrer">{} ↗</a>'.format(E(url), E(name))
                for name, url in group["clues"]
            ),
        )
        for group in REPLACEMENT_CLUES
    )

    # 世界经典：47 条资料卡已补齐，但按「真实录音优先」口径，音频一律标「待采集」。
    world_records = load_json(ROOT / "world-materials.json", [])
    world_clues = load_json(ROOT / "world-audio-clues.json", {})
    if len(world_records) != 47:
        raise ValueError(f"Expected 47 world material records, got {len(world_records)}")
    if any(r.get("audioStatus") != "待采集" or r.get("hasAudio") is not False for r in world_records):
        raise ValueError("Every world material must keep audio pending")
    world_lyrics_ready = sum(1 for r in world_records if r.get("lyrics"))
    world_pending_rows = "\n".join(
        "<tr><td><code>{}</code></td><td>{}</td></tr>".format(E(c["id"]), E(c["note"]))
        for c in world_clues.get("verifiedCandidates", [])
    )

    main = f"""    <section class="shell hero" aria-labelledby="page-title">
      <span class="eyebrow">RESEARCH LAYER · 研究资源库</span>
      <h1 id="page-title">先尽可能完整地<span class="accent">发现与理解</span>，再审慎决定每项资源可以如何被使用。</h1>
      <p class="hero-desc">童年书房首先是一个面向儿童文化的研究、发现、采集、整理与学习项目，其次才是面向儿童和家庭的资源产品。这一页展示研究层的数据口径、状态模型、采集边界与当前进度。</p>
      <div class="quote">版权状态未知，不等于没有研究价值；暂时不能公开使用，不等于不应该收录研究线索。</div>
      <div class="hero-actions" style="margin-top:22px">
        <a class="button button-primary" href="#dashboard">看状态看板</a>
        <a class="button" href="#boundary">看使用边界</a>
      </div>
    </section>

    <section class="shell section" aria-labelledby="layers-title">
      <h2 id="layers-title">双层架构：研究资源库 / 儿童使用层</h2>
      <p>同一份作品可以同时存在于两层，但两层回答不同的问题、受不同的门禁约束。</p>
      <div class="layer-row">
        <article class="layer research">
          <span class="kicker">A · RESEARCH</span>
          <h3>研究资源库</h3>
          <p>用于发现、登记、研究和维护候选作品及其版本线索。当前三馆目录页都属于这一层。</p>
          <ul>
            <li>可登记权利未知、待核验或权利复杂的作品候选</li>
            <li>保留作品身份、版本描述、来源名称、发布者、原始 URL、发现日期与核验状态</li>
            <li>优先保存必要元数据与原始来源链接，而不是复制第三方内容</li>
            <li>作品、内容版本、来源条目、媒体资产、权利记录分开建模</li>
          </ul>
        </article>
        <article class="layer library">
          <span class="kicker">B · LIBRARY</span>
          <h3>儿童阅读与使用层</h3>
          <p>面向儿童和家庭提供经过编辑整理的内容体验。进入具体使用场景前逐项判断。</p>
          <ul>
            <li>展示作品介绍或目录信息</li>
            <li>展示正文、歌词、译文、注释或插画</li>
            <li>跳转原始来源 / 嵌入第三方播放器</li>
            <li>站内播放、下载、转载或分发</li>
          </ul>
        </article>
      </div>
    </section>

    <section class="shell section" id="model" aria-labelledby="model-title">
      <h2 id="model-title">统一状态模型 · 五个维度</h2>
      <p>研究进度、权利状态、内容质量、访问方式与发布状态必须分开管理，不能用一个「是否可用」相互替代。依据顶层原则 §6 与 GitHub 版《数据模型设计》§4。</p>
      <table class="data-table">
        <thead><tr><th>字段</th><th>建议状态</th><th>回答的问题</th><th>本项目口径</th></tr></thead>
        <tbody>{model_rows}</tbody>
      </table>
    </section>

    <section class="shell section" id="dashboard" aria-labelledby="dash-title">
      <h2 id="dash-title">研究状态看板 · 当前实际进度</h2>
      <p>下列数字由项目内数据文件实时计算：专题目录、作品目录、资料卡、本地录音清单与官方试听清单。数字分别统计「已登记」「资料完整」「可公开播放」三类，互不混同。录音类型沿用项目既有缺省口径：早期 3 条 CC 开放许可录音未显式写 <code>sampleType</code>，按 <code>open</code> 计。</p>
      <div class="dash">
        <div class="dash-cell"><b>{s['musicWorks']}</b><span>音乐馆发现目录条目</span><small>中国 55 / 英文 50，属发现目录，不等同 100 首种子库</small></div>
        <div class="dash-cell"><b>{s['materialTotal']}</b><span>作品资料卡</span><small>中国 {s['materials']} / 世界经典 {s['worldMaterials']}；歌词、谱面与封面按实际状态展示</small></div>
        <div class="dash-cell"><b>{s['story']} + {s['poetry']}</b><span>故事 / 诗词研究记录</span><small>本轮按原则新增，全部 publication_status = draft</small></div>
        <div class="dash-cell"><b>{s['samples']} / {s['versions']}</b><span>本地作品录音 / 可播放版本</span><small>含多版本选择器；不等于已获公开播放授权</small></div>
        <div class="dash-cell"><b>{s['files']} / {s['mappings']}</b><span>本轮采集媒体文件 / 作品映射</span><small>内部研究采集，含公开页面完整录音与视频原声音轨</small></div>
        <div class="dash-cell"><b>{s['official']}</b><span>官方发行 30 秒试听</span><small>点击加载、逐次核验曲目身份、不持久化预览 URL</small></div>
        <div class="dash-cell"><b>{s['types'].get('internal', 0)} / {s['types'].get('generated', 0)} / {s['types'].get('open', 0)}</b><span>internal / generated / open</span><small>internal = 权利待核验；generated = 非原曲测试音；open = 开放素材</small></div>
        <div class="dash-cell"><b>0</b><span>已由本站完成公开再发布核验的媒体</span><small>公共部署仍须逐项通过权利门禁，当前均为研究 / 原型层</small></div>
      </div>
      <table class="data-table">
        <thead><tr><th>数据文件</th><th>用途</th><th>说明</th></tr></thead>
        <tbody>
          <tr><td><a href="library-content.json">library-content.json</a></td><td>故事馆 / 古诗词馆研究候选目录</td><td>{s['story']} + {s['poetry']} 条，含五维状态与来源线索</td></tr>
          <tr><td><a href="specialties.json">specialties.json</a></td><td>音乐馆发现目录与八专题映射</td><td>{s['musicWorks']} 条作品记录</td></tr>
          <tr><td><a href="audio/samples.json">audio/samples.json</a></td><td>作品录音与资料卡入口</td><td>{s['samples']} 条 / {s['versions']} 个可播放版本</td></tr>
          <tr><td><a href="china-materials.json">china-materials.json</a></td><td>中国经典资料卡</td><td>{s['materials']} 条，含歌词、谱面与原创封面</td></tr>
          <tr><td><a href="world-materials.json">world-materials.json</a></td><td>世界经典资料卡</td><td>{s['worldMaterials']} 条，封面 / 已核验歌词 / 来源 / 权利状态；音频一律「待采集」</td></tr>
          <tr><td><a href="world-lyrics-sources.json">world-lyrics-sources.json</a></td><td>世界经典歌词与来源逐曲核验底稿</td><td>{s['worldMaterials']} 条，无证歌词置 null 并写明原因</td></tr>
          <tr><td><a href="world-audio-clues.json">world-audio-clues.json</a></td><td>开放许可音频线索与采集受阻记录</td><td>{s['worldAudioClues']} 组已核验候选，均未接入播放</td></tr>
          <tr><td><a href="audio/public-recording-collection.json">audio/public-recording-collection.json</a></td><td>累计两轮内部研究采集清单</td><td>{s['files']} 个文件 / {s['mappings']} 条映射，含来源、SHA-256 与时长</td></tr>
          <tr><td><a href="audio/official-recordings.json">audio/official-recordings.json</a></td><td>官方发行试听清单</td><td>{s['official']} 首，30 秒预览，不与内部完整录音混同</td></tr>
        </tbody>
      </table>
    </section>

    <section class="shell section" aria-labelledby="sources-title">
      <h2 id="sources-title">来源线索 · 机构入口</h2>
      <p>下表为发现与考证入口，不是具体作品页面，也不构成转载许可。研究库默认只保存必要元数据与原始页面链接。</p>
      <table class="data-table">
        <thead><tr><th>信源</th><th>入口</th><th>主要用途</th></tr></thead>
        <tbody>{source_rows}</tbody>
      </table>
    </section>

    <section class="shell section" id="replacement" aria-labelledby="replacement-title">
      <h2 id="replacement-title">非原曲测试音替换进展 · 剩余 {len(generated_ids)} 首</h2>
      <p>原始 44 条程序合成的「原创播放示范 · 非原曲」测试音中，两轮已累计替换 <b>{44 - len(generated_ids)} 首</b>为可核验的公开来源真实录音（第一轮 15 首；第二轮 8 首，来自央视网独立单曲页原声音轨与学习强国童谣诵读音频）。剩余 {len(generated_ids)} 首按核查结论分三组登记。<b>找不到的不硬配</b>：同名不同曲、整期节目片段、商业平台条目一律不接入作品播放，只保留研究线索，避免把不相关音频标成目标作品原曲。</p>
      <table class="data-table">
        <thead><tr><th>分组</th><th>数量</th><th>作品 ID</th><th>核查结论</th><th>已核实来源线索</th></tr></thead>
        <tbody>{replacement_rows}</tbody>
      </table>
    </section>

    <section class="shell section" id="world-pending" aria-labelledby="world-pending-title">
      <h2 id="world-pending-title">世界经典资料卡 · {len(world_records)} 条已补齐，真实录音待采集</h2>
      <p>作品目录 105 条现已全部配置资料卡：中国 55 条、世界经典 {len(world_records)} 条，另 3 条英语条目随示例音频提供资料。世界经典逐曲核验了公版歌词与权威来源，其中 <b>{world_lyrics_ready} 条</b>照录到可逐行复核的歌词，<b>{len(world_records) - world_lyrics_ready} 条</b>因来源未刊全文而明确留白并写明原因；没有可考证旋律的一律不生成五线谱。</p>
      <p><b>真实录音优先 · 找不到的不硬配</b>：{len(world_records)} 首的播放位统一标「待采集」，不接程序合成音冒充原曲。Commons API 检索经 WebFetch 通道逐项核验，本地出口 IP 被 Wikimedia 403 / 429 限流、upload.wikimedia.org 无法下载；已命中的候选还包含器乐片段、MIDI 数据、同名异曲与现代专辑录音，未逐项完成版本与授权复核前不接入。</p>
      <table class="data-table">
        <thead><tr><th>作品 ID</th><th>已核验的开放许可候选与核查结论</th></tr></thead>
        <tbody>{world_pending_rows}</tbody>
      </table>
      <p>依据文件：<a href="world-materials.json">world-materials.json</a> · <a href="world-lyrics-sources.json">world-lyrics-sources.json</a> · <a href="world-audio-clues.json">world-audio-clues.json</a>；生成脚本 <code>build_world_materials.py</code>，探针 <code>probe_commons.py</code>。</p>
    </section>

    <section class="shell section" aria-labelledby="flow-title">
      <h2 id="flow-title">从研究到公开的八步流程</h2>
      <p>版权审核不是研究采集的入口门槛，而是进入具体公开使用场景前的必要判断。</p>
      <ol class="flow">{flow_html}</ol>
    </section>

    <section class="shell section" id="boundary" aria-labelledby="boundary-title">
      <h2 id="boundary-title">采集边界与待办</h2>
      <div class="boundary">
        <h3>⚠️ 当前明确边界</h3>
        <ul>
          <li>研究库默认只登记元数据、研究笔记与原始链接；<b>不因「内部研究」默认下载、缓存、镜像或转存第三方媒体</b>。</li>
          <li>累计两轮经项目明确批准，为版本鉴定与内部原型验证保存了 {s['files']} 个公开页面内完整录音 / 原声音轨（{s['mappings']} 条作品映射），统一标为 <code>internal · 权利待核验</code>；每个文件均记录来源页、原始地址、版本、采集日期、处理方式、大小与 SHA-256。第二轮新增央视网「独立单曲页」原声音轨与学习强国童谣诵读音频，诵读 / 表演 / 改编版本均在资料卡中如实标注，不冒充歌曲原唱。详见<a href="audio/public-recording-collection.json">采集清单</a>与<a href="../docs/COPYRIGHT_POLICY.md">来源与权利说明</a>。</li>
          <li>政府、高校、公共文化机构或教育平台上的完整歌曲页面，可作为可靠的来源与版本核验线索；<b>其公开展示本身不代表本站获得再发布授权</b>。</li>
          <li>仍有 {s['types'].get('generated', 0)} 个 <code>generated</code> 条目是程序合成的「原创播放示范 · 非原曲」测试音，页面持续标注，不得当作目标作品原声；需继续寻找可靠原曲录音。</li>
          <li>世界经典 {s['worldMaterials']} 条资料卡只补齐元数据与原创封面，<b>未接入任何第三方音频</b>；歌词按来源页照录或明确留白，谱面不伪造，播放位统一标「待采集」。资料卡齐备不等于取得公开播放授权。</li>
          <li>{s['official']} 首官方 30 秒试听属于平台预览，点击才加载、逐首核验曲目身份、不持久化预览 URL，与内部完整录音分开管理。</li>
          <li>故事馆「当代原创」15 条是编辑征集方向，不是已登记作品；古诗词馆 12 条是版本 / 媒体资产层线索，不是独立作品。统计中单独列出，不虚报作品数。</li>
        </ul>
      </div>
      <div class="boundary" style="background:#fdf1c9">
        <h3>下一步待办（按优先级）</h3>
        <ul>
          <li>为故事馆与古诗词馆每条候选补具体来源页面 URL、发现日期与版本考证记录，把 <code>research_status</code> 从 discovered 推进到 researching / reviewed。</li>
          <li>逐条完成权利证据归档，把 <code>rights_status</code> 从 pending / unknown 推进到 verified；证据含目标地域、权利人、许可、用途、期限与复核人。</li>
          <li>补齐剩余 {s['types'].get('generated', 0)} 首非原曲测试音对应的真实录音，替换时保留原有版本与来源记录。</li>
          <li>为世界经典 {s['worldMaterials']} 首逐项完成开放许可 / 公开机构录音的身份、表演者、版本与授权复核；条件允许时再采集，未复核前继续标「待采集」，不硬配。</li>
          <li>为 {len(world_records) - world_lyrics_ready} 条未取得歌词全文的世界经典补权威公版文本，并考证可生成五线谱的旋律依据；无证内容继续保持留白。</li>
          <li>公共部署前逐项执行发布门禁：<code>publication_status</code> 为 published 的内容，其正文与所有待公开资产的权利状态必须通过校验。</li>
          <li>文档口径待同步：GitHub main 版《数据模型设计》已新增 §4「研究状态、权利状态与访问方式」四字段，本地 <a href="../docs/DATA_MODEL.md">docs/DATA_MODEL.md</a> 仍是旧版章节结构（含 3.1 三大支柱 / 3.2 中国经典七专题 / 作品分类字段）。本页按 GitHub 版建模；同步时应保留本地独有分类字段作为附录，不直接丢弃。</li>
        </ul>
      </div>
    </section>"""

    html = page_shell(
        "研究资源库", "童年书房研究资源库：双层架构、五维状态模型、研究看板、来源线索与采集边界。",
        "research.html", RESEARCH_CSS, main,
        f"研究资源库 · 依据 docs/PROJECT_PRINCIPLES.md v1.0 与 docs/DATA_MODEL.md v0.1 §4，{data['generatedOn']} 生成。",
    )
    # 宽表在窄屏由容器横向滚动，避免撑开整个文档
    return re.sub(
        r'(<table class="data-table">.*?</table>)',
        r'<div class="table-scroll">\1</div>',
        html, flags=re.S,
    )


# ---------------------------------------------------------------------------
# 向既有页面注入统一导航与关联层
# ---------------------------------------------------------------------------
CSS_MARK_RE = re.compile(r"\n?/\* ===== LIBRARY_LINKS:CSS ===== \*/.*?/\* ===== /LIBRARY_LINKS:CSS ===== \*/\n?", re.S)
MAP_MARK_RE = re.compile(r"\n?<!-- LIBRARY_LINKS:MAP -->.*?<!-- /LIBRARY_LINKS:MAP -->\n?", re.S)
PEER_MARK_RE = re.compile(r"\n?<!-- LIBRARY_LINKS:PEERS -->.*?<!-- /LIBRARY_LINKS:PEERS -->\n?", re.S)
NAV_DESKTOP_RE = re.compile(r'(<nav class="desktop-nav"[^>]*>).*?(</nav>)', re.S)
NAV_MOBILE_RE = re.compile(r'(<nav class="shell mobile-nav"[^>]*>).*?(</nav>)', re.S)

TARGETS = [
    "dir-3.html", "music.html", "works.html", "works-template.html",
    "specialty-template.html", "story.html", "poetry.html", "research.html",
] + [f"specialty-{key}.html" for key, _ in SPECS]


def inject_one(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    name = path.name
    current = name
    if name.startswith("specialty-") and name != "specialty-template.html":
        current = name  # 专题页在地图中高亮自己
    elif name == "works-template.html":
        current = "works.html"

    # 1) 样式：幂等替换
    text = CSS_MARK_RE.sub("\n", text)
    if "</style>" in text:
        text = text.replace("</style>", LINK_CSS + "</style>", 1)

    # 2) 主导航：只替换 nav 内部，保留 header 其它元素（含首页 CTA）
    links = nav_links("music.html" if name.startswith("specialty-") and name != "specialty-template.html" else current)
    if name == "works-template.html":
        links = nav_links("works.html")
    text = NAV_DESKTOP_RE.sub(lambda m: m.group(1) + "\n        " + links + "\n      " + m.group(2), text, count=1)
    text = NAV_MOBILE_RE.sub(lambda m: m.group(1) + "\n      " + links + "\n    " + m.group(2), text, count=1)

    # 3) 全站地图
    text = MAP_MARK_RE.sub("\n", text)
    if "</main>" in text:
        text = text.replace("</main>", map_html(current) + "\n  </main>", 1)

    # 4) 专题页横向串联（模板不需要，靠生成后的八个页面承载）
    text = PEER_MARK_RE.sub("\n", text)
    m = re.match(r"specialty-(.+)\.html$", name)
    if m and m.group(1) in dict(SPECS):
        anchor = '<div class="shell back-band">'
        if anchor in text:
            text = text.replace(anchor, peers_html(m.group(1)) + "\n\n    " + anchor, 1)
        elif "</main>" in text:
            text = text.replace("</main>", peers_html(m.group(1)) + "\n  </main>", 1)

    # 5) 作品详情弹窗 -> 所属专题反向回链（仅 works.html 生成物）
    dialog_re = re.compile(r"\n?<!-- LIBRARY_LINKS:DIALOG -->.*?<!-- /LIBRARY_LINKS:DIALOG -->\n?", re.S)
    specjs_re = re.compile(r"\n?<!-- LIBRARY_LINKS:WORKSPECS -->.*?<!-- /LIBRARY_LINKS:WORKSPECS -->\n?", re.S)
    text = dialog_re.sub("\n", text)
    text = specjs_re.sub("\n", text)
    if name == "works.html":
        anchor = '<div class="dialog-body">'
        if anchor in text:
            text = text.replace(anchor, anchor + "\n" + dialog_links_html(), 1)
        if "</body>" in text:
            text = text.replace("</body>", work_spec_script() + "\n</body>", 1)

    path.write_text(text, encoding="utf-8")
    return name


def inject_all() -> list[str]:
    done = []
    for filename in TARGETS:
        path = ROOT / filename
        if path.exists():
            done.append(inject_one(path))
    return done


def main():
    data = library_catalog.build()
    (ROOT / "story.html").write_text(render_hall("story", data), encoding="utf-8")
    (ROOT / "poetry.html").write_text(render_hall("poetry", data), encoding="utf-8")
    (ROOT / "research.html").write_text(render_research(data), encoding="utf-8")

    # 先重建生成物，再统一注入（否则注入内容会被重建覆盖）
    build_specialty_pages.main()
    build_works.main()
    injected = inject_all()

    print(json.dumps({
        "catalog": CATALOG.name,
        "records": len(data["records"]),
        "stats": data["stats"],
        "research": research_stats(data),
        "generated": ["story.html", "poetry.html", "research.html"],
        "injected": len(injected),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
