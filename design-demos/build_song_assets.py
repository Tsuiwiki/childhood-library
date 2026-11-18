from array import array
import math
from pathlib import Path
import re
from textwrap import dedent
import wave
import xml.etree.ElementTree as ET

import verovio

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "song-assets"
OUT.mkdir(exist_ok=True)


# Lyrics are engraved into the MusicXML itself. A middle dot separates English
# syllables; punctuation remains attached to the final syllable of each word.
# Every tuple is (lyric line, first measure, last measure), inclusive.
LYRIC_LAYOUTS = {
    "EN-T01": [
        {"language": "en", "lines": [
            ("Twin·kle, twin·kle, lit·tle star,", 1, 3),
            ("How I won·der what you are.", 4, 6),
            ("Up a·bove the world so high,", 7, 9),
            ("Like a dia·mond in the sky.", 10, 12),
        ]},
        {"language": "en", "lines": [
            ("When the blaz·ing sun is gone,", 1, 3),
            ("When he noth·ing shines up·on,", 4, 6),
            ("Then you show your lit·tle light,", 7, 9),
            ("Twin·kle, twin·kle, all the night.", 10, 12),
        ]},
    ],
    "EN-T02": [
        {"language": "en", "lines": [
            ("Ma·ry had a lit·tle lamb,", 1, 2),
            ("Lit·tle lamb, lit·tle lamb,", 3, 4),
            ("Ma·ry had a lit·tle lamb—", 5, 6),
            ("（结尾哼唱）", 7, 8),
        ]},
    ],
    "EN-T03": [
        {"language": "en", "lines": [
            ("Row, row, row your boat,", 1, 1),
            ("Gen·tly down the stream.", 2, 2),
            ("Mer·ri·ly, mer·ri·ly, mer·ri·ly, mer·ri·ly,", 3, 3),
            ("Life is but a dream.", 4, 4),
        ]},
    ],
    "CN-T01": [
        {"language": "zh", "lines": [
            ("月光光，照地堂，", 1, 2),
            ("虾仔你乖乖瞓落床，", 3, 4),
            ("听朝阿妈要赶插秧啰，", 5, 6),
            ("阿爷睇牛佢上山岗。", 7, 8),
        ]},
    ],
    "CN-C28": [
        {"language": "zh", "lines": [
            ("排排坐，吃果果，", 1, 2),
            ("你一个，我一个，", 3, 4),
            ("妹妹睡了留一个。", 5, 6),
            ("背一个，抱一个，", 7, 8),
            ("屋头还有十二个。", 9, 10),
        ]},
    ],
    "CN-C26": [
        {"language": "zh", "lines": [
            ("小老鼠，上灯台，", 1, 2),
            ("偷油吃，下不来；", 3, 4),
            ("叫小妮儿扭猫来，", 5, 6),
            ("吱扭就下来。", 7, 8),
        ]},
    ],
    "CN-C01": [
        {"language": "zh", "lines": [
            ("让我们荡起双桨，", 1, 2),
            ("小船儿推开波浪，", 3, 4),
            ("海面倒映着美丽的白塔，", 5, 6),
            ("四周环绕着绿树红墙。", 7, 8),
            ("小船儿轻轻飘荡在水中，", 9, 10),
            ("迎面吹来了凉爽的风。", 11, 12),
        ]},
        {"language": "zh", "lines": [
            ("红领巾迎着太阳，", 1, 2),
            ("阳光洒在海面上，", 3, 4),
            ("水中鱼儿望着我们，", 5, 6),
            ("悄悄地听我们愉快歌唱。", 7, 8),
            ("小船儿轻轻飘荡在水中，", 9, 10),
            ("迎面吹来了凉爽的风。", 11, 12),
        ]},
        {"language": "zh", "lines": [
            ("做完了一天的功课，", 1, 2),
            ("我们来尽情欢乐，", 3, 4),
            ("我问你亲爱的伙伴，", 5, 6),
            ("谁给我们安排下幸福的生活。", 7, 8),
            ("小船儿轻轻飘荡在水中，", 9, 10),
            ("迎面吹来了凉爽的风。", 11, 12),
        ]},
    ],
    "CN-C03": [
        {"language": "zh", "lines": [
            ("小燕子，穿花衣，", 1, 2),
            ("年年春天到这里。", 3, 4),
            ("我问燕子你为啥来？", 5, 6),
            ("燕子说：", 7, 8),
            ("这里的春天最美丽。", 9, 12),
        ]},
        {"language": "zh", "lines": [
            ("小燕子，告诉你，", 1, 2),
            ("今年这里更美丽。", 3, 4),
            ("我们盖起了大工厂，", 5, 6),
            ("装上了新机器，", 7, 8),
            ("欢迎你，长期住在这里。", 9, 12),
        ]},
    ],
    "CN-C10": [
        {"language": "zh", "lines": [
            ("请把我的歌带回你的家，", 1, 2),
            ("请把你的微笑留下。", 3, 4),
            ("请把我的歌带回你的家，", 5, 6),
            ("请把你的微笑留下。", 7, 8),
            ("明天明天这歌声，", 9, 10),
            ("飞遍海角天涯，飞遍海角天涯。", 11, 12),
            ("明天明天这微笑，", 13, 14),
            ("将是遍野春花，将是遍野春花。", 15, 16),
        ]},
        {"language": "zh", "lines": [
            ("请把我的歌带回你的家，", 1, 2),
            ("请把你的微笑留下。", 3, 4),
            ("请把我的歌带回你的家，", 5, 6),
            ("请把你的微笑留下。", 7, 8),
            ("明天明天这歌声，", 9, 10),
            ("飞遍海角天涯，飞遍海角天涯。", 11, 12),
            ("明天明天这微笑，", 13, 14),
            ("将是遍野春花，将是遍野春花。", 15, 16),
        ]},
        {"language": "en", "lines": [
            ("When you go back home, take my song with you.", 1, 2),
            ("But you nev·er take your smile a·way.", 3, 4),
            ("When you go back home, take my song with you.", 5, 6),
            ("But you nev·er take your smile a·way.", 7, 8),
            ("To·mor·row this song will be heard,", 9, 10),
            ("Ev·ery cor·ner of the world, ev·ery cor·ner of the world.", 11, 12),
            ("To·mor·row this smile will be flow·ers,", 13, 14),
            ("Blos·som in the spring·time, blos·som in the spring·time.", 15, 16),
        ]},
        {"language": "zh", "lines": [
            ("", 1, 2), ("", 3, 4), ("", 5, 6), ("", 7, 8),
            ("明天明天这歌声，", 9, 10),
            ("飞遍海角天涯，飞遍海角天涯。", 11, 12),
            ("明天明天这微笑，", 13, 14),
            ("将是遍野春花，将是遍野春花。", 15, 16),
        ]},
    ],
}


def cover_svg(work_id, title_lines, art, accent):
    category = "经典创作儿歌" if work_id in {"CN-C01", "CN-C03", "CN-C10"} else "传统童谣"
    text = "".join(
        f'<text x="54" y="{98 + index * 54}" class="cover-title">{line}</text>'
        for index, line in enumerate(title_lines)
    )
    return dedent(f'''\
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600" role="img" aria-labelledby="title desc">
        <title id="title">{work_id} — {' '.join(title_lines)}</title>
        <desc id="desc">童年书房剪贴簿风格原创歌曲封面</desc>
        <defs>
          <pattern id="dots" width="18" height="18" patternUnits="userSpaceOnUse">
            <circle cx="3" cy="3" r="1.8" fill="#191917" opacity=".22"/>
          </pattern>
        </defs>
        <rect width="800" height="600" fill="#f4eddc"/>
        <rect width="800" height="600" fill="url(#dots)"/>
        <rect x="18" y="18" width="764" height="564" fill="none" stroke="#191917" stroke-width="8"/>
        <rect x="42" y="42" width="14" height="116" fill="{accent}" stroke="#191917" stroke-width="4"/>
        <rect x="548" y="48" width="184" height="52" fill="#fffaf0" stroke="#191917" stroke-width="4" transform="rotate(3 640 74)"/>
        <text x="640" y="83" text-anchor="middle" font-family="Arial, sans-serif" font-size="24" font-weight="900" fill="#191917">{work_id}</text>
        <g class="title" fill="#191917" font-family="Georgia, 'Noto Serif CJK SC', 'Songti SC', SimSun, serif" font-size="45" font-weight="900" letter-spacing="-1">{text}</g>
        {art}
        <rect x="48" y="520" width="704" height="38" fill="#fffaf0" stroke="#191917" stroke-width="4"/>
        <text x="64" y="546" font-family="Arial, 'Microsoft YaHei', sans-serif" font-size="20" font-weight="800" fill="#191917">童年书房 · {category} · 原创封面</text>
      </svg>
    ''')


def build_covers():
    twinkle_art = dedent('''\
      <rect x="366" y="164" width="366" height="316" fill="#2858b8" stroke="#191917" stroke-width="7" transform="rotate(2 549 322)"/>
      <circle cx="652" cy="222" r="52" fill="#f1bd32" stroke="#191917" stroke-width="6"/>
      <path d="M414 406 Q474 334 536 400 T690 388 L724 474 L376 474 Z" fill="#739348" stroke="#191917" stroke-width="6"/>
      <path d="M524 214 L540 260 L588 262 L551 293 L564 340 L524 312 L484 340 L497 293 L460 262 L508 260 Z" fill="#f1bd32" stroke="#191917" stroke-width="6"/>
      <g fill="#fffaf0" stroke="#191917" stroke-width="4">
        <path d="M416 216 l8 17 18 2-14 12 4 18-16-9-16 9 4-18-14-12 18-2z"/>
        <path d="M686 326 l7 15 16 2-12 11 3 16-14-8-14 8 3-16-12-11 16-2z"/>
      </g>
      <path d="M82 290 L290 270 L312 448 L102 468 Z" fill="#e64a38" stroke="#191917" stroke-width="7"/>
      <path d="M114 318 L264 304 M126 354 L276 340 M136 392 L286 378" fill="none" stroke="#fffaf0" stroke-width="12"/>
      <path d="M94 466 L318 444" stroke="#191917" stroke-width="10"/>
    ''')
    mary_art = dedent('''\
      <path d="M60 438 Q200 362 340 430 T740 404 L740 502 L60 502 Z" fill="#739348" stroke="#191917" stroke-width="7"/>
      <path d="M494 186 L650 132 L728 202 L708 364 L514 364 Z" fill="#e64a38" stroke="#191917" stroke-width="7"/>
      <path d="M472 196 L648 112 L746 196" fill="#f1bd32" stroke="#191917" stroke-width="9"/>
      <rect x="596" y="260" width="62" height="104" fill="#2858b8" stroke="#191917" stroke-width="6"/>
      <rect x="534" y="216" width="48" height="48" fill="#fffaf0" stroke="#191917" stroke-width="5"/>
      <g stroke="#191917" stroke-width="6">
        <ellipse cx="300" cy="348" rx="142" ry="86" fill="#fffaf0"/>
        <circle cx="182" cy="304" r="54" fill="#fffaf0"/>
        <circle cx="230" cy="272" r="56" fill="#fffaf0"/>
        <circle cx="292" cy="266" r="58" fill="#fffaf0"/>
        <circle cx="352" cy="278" r="56" fill="#fffaf0"/>
        <path d="M398 296 Q470 284 474 346 Q464 398 402 376 Z" fill="#f1bd32"/>
        <path d="M420 302 L452 268 L466 310" fill="#f1bd32"/>
        <path d="M212 410 L204 486 M282 424 L282 490 M364 410 L374 482" fill="none"/>
      </g>
      <circle cx="444" cy="334" r="6" fill="#191917"/>
      <path d="M82 196 L264 172 L274 238 L92 258 Z" fill="#2858b8" stroke="#191917" stroke-width="6"/>
      <text x="178" y="222" text-anchor="middle" font-family="Georgia, serif" font-size="28" font-weight="900" fill="#fffaf0" transform="rotate(-7 178 222)">little lamb</text>
    ''')
    row_art = dedent('''\
      <rect x="56" y="212" width="684" height="282" fill="#2858b8" stroke="#191917" stroke-width="7" transform="rotate(-2 398 353)"/>
      <circle cx="650" cy="174" r="58" fill="#e64a38" stroke="#191917" stroke-width="6"/>
      <path d="M64 332 Q130 296 198 334 T332 330 T466 328 T600 326 T734 324 M62 404 Q130 368 198 406 T332 402 T466 400 T600 398 T734 396 M64 468 Q130 432 198 470 T332 466 T466 464 T600 462 T734 460" fill="none" stroke="#fffaf0" stroke-width="14"/>
      <path d="M198 310 L530 292 L458 434 L280 448 Z" fill="#f1bd32" stroke="#191917" stroke-width="8"/>
      <path d="M198 310 L366 358 L530 292 M366 358 L458 434" fill="none" stroke="#191917" stroke-width="6"/>
      <path d="M356 304 L360 152 L510 278 Z" fill="#fffaf0" stroke="#191917" stroke-width="7"/>
      <path d="M352 290 L232 198 L352 164" fill="#e64a38" stroke="#191917" stroke-width="7"/>
      <path d="M116 250 L286 458 M566 226 L646 440" stroke="#191917" stroke-width="10" stroke-linecap="round"/>
      <path d="M92 220 L140 274 M628 214 L682 202" stroke="#f1bd32" stroke-width="18" stroke-linecap="round"/>
    ''')
    moonlight_art = dedent('''\
      <rect x="344" y="142" width="396" height="350" fill="#2858b8" stroke="#191917" stroke-width="7" transform="rotate(2 542 317)"/>
      <circle cx="620" cy="238" r="76" fill="#f1bd32" stroke="#191917" stroke-width="7"/>
      <path d="M362 372 Q428 336 494 374 T626 370 T738 366 L738 478 L362 478 Z" fill="#739348" stroke="#191917" stroke-width="6"/>
      <path d="M362 410 Q430 380 498 414 T634 408 T738 404 M364 452 Q432 422 500 456 T636 450 T736 446" fill="none" stroke="#fffaf0" stroke-width="10"/>
      <path d="M464 380 L602 372 L566 424 L494 432 Z" fill="#e64a38" stroke="#191917" stroke-width="6"/>
      <path d="M528 376 L530 294 L588 356 Z" fill="#fffaf0" stroke="#191917" stroke-width="6"/>
      <path d="M78 278 L292 250 L310 452 L98 474 Z" fill="#fffaf0" stroke="#191917" stroke-width="7"/>
      <path d="M116 318 L268 298 M122 356 L274 338 M130 396 L280 378" stroke="#e64a38" stroke-width="10"/>
      <path d="M110 462 L94 492 M284 444 L300 478" stroke="#191917" stroke-width="9"/>
    ''')
    fruit_art = dedent('''\
      <path d="M60 438 Q210 386 364 430 T740 402 L740 500 L60 500 Z" fill="#739348" stroke="#191917" stroke-width="7"/>
      <rect x="114" y="384" width="570" height="48" rx="8" fill="#f1bd32" stroke="#191917" stroke-width="7" transform="rotate(-2 399 408)"/>
      <path d="M152 426 L136 488 M646 420 L664 482" stroke="#191917" stroke-width="12"/>
      <g stroke="#191917" stroke-width="6">
        <circle cx="214" cy="276" r="52" fill="#f1bd32"/>
        <path d="M154 330 Q214 302 274 330 L284 392 L146 392 Z" fill="#e64a38"/>
        <circle cx="392" cy="260" r="54" fill="#fffaf0"/>
        <path d="M326 322 Q392 288 458 322 L468 390 L316 390 Z" fill="#2858b8"/>
        <circle cx="568" cy="278" r="50" fill="#f1bd32"/>
        <path d="M512 330 Q568 302 624 330 L640 390 L500 390 Z" fill="#fffaf0"/>
      </g>
      <g fill="#191917"><circle cx="198" cy="274" r="5"/><circle cx="230" cy="274" r="5"/><circle cx="376" cy="258" r="5"/><circle cx="408" cy="258" r="5"/><circle cx="552" cy="276" r="5"/><circle cx="584" cy="276" r="5"/></g>
      <g fill="#e64a38" stroke="#191917" stroke-width="5"><circle cx="304" cy="350" r="28"/><circle cx="480" cy="348" r="28"/><circle cx="666" cy="320" r="30"/></g>
      <path d="M302 320 Q306 298 326 296 M478 318 Q482 296 502 296 M666 288 Q672 266 692 268" fill="none" stroke="#739348" stroke-width="7"/>
      <path d="M84 188 L282 174 L290 230 L92 244 Z" fill="#2858b8" stroke="#191917" stroke-width="6"/>
      <text x="188" y="216" text-anchor="middle" font-family="SimSun, serif" font-size="27" font-weight="900" fill="#fffaf0" transform="rotate(-4 188 216)">你一个 · 我一个</text>
    ''')
    mouse_art = dedent('''\
      <rect x="424" y="144" width="286" height="348" fill="#2858b8" stroke="#191917" stroke-width="7" transform="rotate(2 567 318)"/>
      <path d="M518 432 L614 432 L596 466 L536 466 Z" fill="#e64a38" stroke="#191917" stroke-width="6"/>
      <path d="M550 430 L552 340 L584 340 L584 430" fill="#f1bd32" stroke="#191917" stroke-width="6"/>
      <path d="M512 340 Q566 296 622 340 Q568 376 512 340 Z" fill="#fffaf0" stroke="#191917" stroke-width="6"/>
      <path d="M566 304 Q532 260 570 202 Q608 260 566 304 Z" fill="#f1bd32" stroke="#191917" stroke-width="6"/>
      <g stroke="#191917" stroke-width="6">
        <ellipse cx="372" cy="310" rx="88" ry="62" fill="#fffaf0"/>
        <circle cx="308" cy="260" r="48" fill="#fffaf0"/>
        <circle cx="280" cy="216" r="26" fill="#e64a38"/>
        <circle cx="332" cy="214" r="26" fill="#e64a38"/>
        <path d="M444 334 Q520 360 484 412 Q456 438 426 408" fill="none"/>
        <path d="M336 358 L316 404 M390 366 L402 410" fill="none"/>
      </g>
      <circle cx="292" cy="260" r="6" fill="#191917"/>
      <path d="M270 274 L228 266 M272 286 L228 292" stroke="#191917" stroke-width="4"/>
      <path d="M82 410 Q144 342 206 408 L214 480 L76 480 Z" fill="#739348" stroke="#191917" stroke-width="7"/>
      <circle cx="112" cy="388" r="34" fill="#739348" stroke="#191917" stroke-width="6"/>
      <circle cx="176" cy="388" r="34" fill="#739348" stroke="#191917" stroke-width="6"/>
      <circle cx="126" cy="420" r="5" fill="#191917"/><circle cx="166" cy="420" r="5" fill="#191917"/>
    ''')
    oars_art = dedent('''\
      <rect x="44" y="182" width="700" height="314" fill="#2858b8" stroke="#191917" stroke-width="7" transform="rotate(-1 394 339)"/>
      <circle cx="650" cy="206" r="48" fill="#f1bd32" stroke="#191917" stroke-width="6"/>
      <path d="M54 344 Q122 312 190 346 T326 342 T462 340 T598 338 T734 334 M52 418 Q120 386 188 420 T324 416 T460 414 T596 412 T732 408" fill="none" stroke="#fffaf0" stroke-width="12"/>
      <path d="M222 340 L524 324 L470 432 L292 446 Z" fill="#f1bd32" stroke="#191917" stroke-width="8"/>
      <path d="M202 304 L456 456 M470 278 L304 462" stroke="#191917" stroke-width="11" stroke-linecap="round"/>
      <path d="M184 286 L224 316 M450 456 L484 480 M454 260 L488 284 M282 454 L314 480" stroke="#e64a38" stroke-width="20" stroke-linecap="round"/>
      <path d="M566 330 L566 230 L604 202 L642 230 L642 330 Z" fill="#fffaf0" stroke="#191917" stroke-width="6"/>
      <path d="M554 230 L604 180 L654 230" fill="#e64a38" stroke="#191917" stroke-width="7"/>
      <path d="M70 298 L210 284 L210 330 L70 342 Z" fill="#e64a38" stroke="#191917" stroke-width="6"/>
      <path d="M84 292 Q108 248 132 288 Q156 242 180 284" fill="#739348" stroke="#191917" stroke-width="6"/>
    ''')
    swallow_art = dedent('''\
      <rect x="352" y="144" width="386" height="346" fill="#2858b8" stroke="#191917" stroke-width="7" transform="rotate(2 545 317)"/>
      <circle cx="650" cy="212" r="48" fill="#f1bd32" stroke="#191917" stroke-width="6"/>
      <path d="M368 410 Q434 346 500 410 T632 402 T738 398 L738 482 L368 482 Z" fill="#739348" stroke="#191917" stroke-width="6"/>
      <path d="M394 310 Q454 248 514 304 Q560 244 622 278 Q566 296 530 354 Q476 302 394 310 Z" fill="#191917" stroke="#191917" stroke-width="5"/>
      <path d="M520 344 L566 396 L534 382 L510 408 L500 356 Z" fill="#191917"/>
      <path d="M476 306 Q500 318 520 348 Q486 348 462 326 Z" fill="#fffaf0"/>
      <circle cx="594" cy="282" r="5" fill="#fffaf0"/>
      <path d="M620 286 L644 294 L620 302 Z" fill="#e64a38"/>
      <path d="M76 392 Q176 312 292 382 L310 474 L68 474 Z" fill="#fffaf0" stroke="#191917" stroke-width="7"/>
      <path d="M102 386 Q110 330 158 366 Q178 308 214 360 Q260 326 280 382" fill="#e64a38" stroke="#191917" stroke-width="6"/>
      <path d="M112 430 L274 418 M120 454 L280 442" stroke="#2858b8" stroke-width="9"/>
      <path d="M100 230 Q160 196 220 230 T320 220" fill="none" stroke="#739348" stroke-width="10"/>
      <path d="M148 216 Q134 176 108 176 M226 224 Q240 184 268 184" fill="none" stroke="#739348" stroke-width="7"/>
    ''')
    smile_art = dedent('''\
      <path d="M338 154 H724 V474 H338 Z" fill="#2858b8" stroke="#191917" stroke-width="7" transform="rotate(2 531 314)"/>
      <circle cx="528" cy="308" r="116" fill="#f1bd32" stroke="#191917" stroke-width="7"/>
      <circle cx="484" cy="278" r="9" fill="#191917"/><circle cx="570" cy="278" r="9" fill="#191917"/>
      <path d="M464 334 Q526 392 592 328" fill="none" stroke="#191917" stroke-width="10" stroke-linecap="round"/>
      <g fill="#fffaf0" stroke="#191917" stroke-width="5">
        <path d="M376 192 V282 Q342 262 334 290 Q334 324 376 306 V224 L432 208 V268 Q398 250 392 278 Q394 310 432 292 V176 Z"/>
        <path d="M628 352 V426 Q596 408 590 434 Q592 464 628 448 V380 L680 366 V414 Q650 398 644 424 Q646 452 680 438 V340 Z"/>
      </g>
      <g stroke="#191917" stroke-width="5">
        <path d="M104 410 Q128 360 152 410 Q176 360 200 410 Q176 456 152 474 Q128 456 104 410 Z" fill="#e64a38"/>
        <path d="M226 390 Q250 340 274 390 Q298 340 322 390 Q298 436 274 454 Q250 436 226 390 Z" fill="#739348"/>
      </g>
      <path d="M78 224 L288 196 L300 254 L90 282 Z" fill="#e64a38" stroke="#191917" stroke-width="6"/>
      <text x="190" y="242" text-anchor="middle" font-family="SimSun, serif" font-size="28" font-weight="900" fill="#fffaf0" transform="rotate(-7 190 242)">歌声 · 微笑</text>
    ''')
    covers = {
        "EN-T01": (["TWINKLE, TWINKLE", "LITTLE STAR"], twinkle_art, "#e64a38"),
        "EN-T02": (["MARY HAD A", "LITTLE LAMB"], mary_art, "#2858b8"),
        "EN-T03": (["ROW, ROW, ROW", "YOUR BOAT"], row_art, "#739348"),
        "CN-T01": (["月光光", "照地堂"], moonlight_art, "#e64a38"),
        "CN-C28": (["排排坐", "吃果果"], fruit_art, "#2858b8"),
        "CN-C26": (["小老鼠", "上灯台"], mouse_art, "#f1bd32"),
        "CN-C01": (["让我们", "荡起双桨"], oars_art, "#e64a38"),
        "CN-C03": (["小燕子", "穿花衣"], swallow_art, "#739348"),
        "CN-C10": (["歌声", "与微笑"], smile_art, "#2858b8"),
    }
    for work_id, (lines, art, accent) in covers.items():
        (OUT / f"{work_id}-cover.svg").write_text(cover_svg(work_id, lines, art, accent), encoding="utf-8")


def lyric_tokens(text, language):
    """Return (printed text, MusicXML syllabic value) pairs for one line."""
    if not text:
        return []
    if language == "zh" or not re.search(r"[A-Za-z]", text):
        return [(character, "single") for character in re.findall(r"[\u3400-\u9fff]", text)]
    tokens = []
    for word in text.split():
        pieces = word.split("·")
        for index, piece in enumerate(pieces):
            match = re.search(r"[A-Za-z]+", piece)
            if not match:
                continue
            printed = match.group(0)
            if index == len(pieces) - 1:
                printed += piece[match.end():]
            if len(pieces) == 1:
                syllabic = "single"
            elif index == 0:
                syllabic = "begin"
            elif index == len(pieces) - 1:
                syllabic = "end"
            else:
                syllabic = "middle"
            tokens.append((printed, syllabic))
    return tokens


def duration_notation(duration, divisions):
    choices = (
        ("whole", divisions * 4),
        ("half", divisions * 2),
        ("quarter", divisions),
        ("eighth", divisions // 2),
        ("16th", divisions // 4),
    )
    for note_type, base in choices:
        if duration == base:
            return note_type, False
        if duration == base * 3 // 2:
            return note_type, True
    raise ValueError(f"Cannot engrave duration {duration} with divisions {divisions}")


def split_note(note, factor, divisions):
    pitch, duration, note_type, dot, triplet, _lyrics = note
    if factor == 1:
        return [list(note)]
    if triplet or duration % factor:
        raise ValueError(f"Cannot split note {note[:5]} into {factor} parts")
    new_duration = duration // factor
    new_type, new_dot = duration_notation(new_duration, divisions)
    return [[pitch, new_duration, new_type, new_dot, False, {}] for _ in range(factor)]


def can_split_note(note, factor, divisions):
    if factor == 1:
        return True
    if note[4] or note[1] % factor:
        return False
    try:
        duration_notation(note[1] // factor, divisions)
        return True
    except ValueError:
        return False


def prepare_lyric_measures(measures, divisions, verses):
    """Subdivide teaching-notes when needed, then attach one lyric token per note."""
    prepared = []
    for measure in measures:
        normalized_measure = []
        for note in measure:
            values = list(note) + [False, False, {}]
            normalized_measure.append([values[0], values[1], values[2], values[3], values[4], {}])
        prepared.append(normalized_measure)

    first_verse_ranges = [(start, end) for _text, start, end in verses[0]["lines"]]
    for verse in verses[1:]:
        assert [(start, end) for _text, start, end in verse["lines"]] == first_verse_ranges

    for line_index, (start, end) in enumerate(first_verse_ranges):
        token_counts = [
            len(lyric_tokens(verse["lines"][line_index][0], verse["language"]))
            for verse in verses
        ]
        note_count = sum(len(prepared[index - 1]) for index in range(start, end + 1))
        factor = max(1, math.ceil(max(token_counts) / note_count))
        while not all(
            can_split_note(note, factor, divisions)
            for index in range(start, end + 1)
            for note in prepared[index - 1]
        ):
            factor += 1
            if factor > 8:
                raise ValueError(f"Unable to fit complete lyrics in measures {start}-{end}")
        for measure_index in range(start, end + 1):
            split_measure = []
            for note in prepared[measure_index - 1]:
                split_measure.extend(split_note(note, factor, divisions))
            prepared[measure_index - 1] = split_measure

    for verse_number, verse in enumerate(verses, start=1):
        for text, start, end in verse["lines"]:
            tokens = lyric_tokens(text, verse["language"])
            segment = [
                note
                for measure_index in range(start, end + 1)
                for note in prepared[measure_index - 1]
            ]
            if len(tokens) > len(segment):
                raise ValueError(f"Not enough notes for complete lyric line: {text}")
            for note_index, note in enumerate(segment):
                token_start = note_index * len(tokens) // len(segment)
                token_end = (note_index + 1) * len(tokens) // len(segment)
                if token_end > token_start:
                    assert token_end == token_start + 1
                    note[5][verse_number] = tokens[token_start]
    return prepared


def add_note(measure, pitch, duration, note_type, dot=False, triplet=False, lyrics=None):
    note = ET.SubElement(measure, "note")
    pitch_node = ET.SubElement(note, "pitch")
    ET.SubElement(pitch_node, "step").text = pitch[0]
    ET.SubElement(pitch_node, "octave").text = str(pitch[1])
    ET.SubElement(note, "duration").text = str(duration)
    ET.SubElement(note, "voice").text = "1"
    ET.SubElement(note, "type").text = note_type
    if dot:
        ET.SubElement(note, "dot")
    if triplet:
        modification = ET.SubElement(note, "time-modification")
        ET.SubElement(modification, "actual-notes").text = "3"
        ET.SubElement(modification, "normal-notes").text = "2"
        notations = ET.SubElement(note, "notations")
        if triplet in {"start", "stop"}:
            ET.SubElement(notations, "tuplet", type=triplet)
    for number, (text, syllabic) in sorted((lyrics or {}).items()):
        lyric = ET.SubElement(note, "lyric", number=str(number))
        ET.SubElement(lyric, "syllabic").text = syllabic
        ET.SubElement(lyric, "text").text = text


def build_musicxml(work_id, title, measures, divisions, breaks, creator="Traditional"):
    root = ET.Element("score-partwise", version="4.0")
    work = ET.SubElement(root, "work")
    ET.SubElement(work, "work-title").text = title
    identification = ET.SubElement(root, "identification")
    ET.SubElement(identification, "creator", type="composer").text = creator
    encoding = ET.SubElement(identification, "encoding")
    ET.SubElement(encoding, "software").text = "Childhood Library prototype MusicXML generator"
    part_list = ET.SubElement(root, "part-list")
    score_part = ET.SubElement(part_list, "score-part", id="P1")
    ET.SubElement(score_part, "part-name").text = "Melody"
    part = ET.SubElement(root, "part", id="P1")
    for number, notes in enumerate(measures, start=1):
        if sum(note[1] for note in notes) != divisions * 4:
            raise ValueError(f"Measure {number} of {work_id} does not contain four quarter-note beats")
        measure = ET.SubElement(part, "measure", number=str(number))
        if number in breaks:
            ET.SubElement(measure, "print", **{"new-system": "yes"})
        if number == 1:
            attributes = ET.SubElement(measure, "attributes")
            ET.SubElement(attributes, "divisions").text = str(divisions)
            key = ET.SubElement(attributes, "key")
            ET.SubElement(key, "fifths").text = "0"
            ET.SubElement(key, "mode").text = "major"
            time = ET.SubElement(attributes, "time")
            ET.SubElement(time, "beats").text = "4"
            ET.SubElement(time, "beat-type").text = "4"
            clef = ET.SubElement(attributes, "clef")
            ET.SubElement(clef, "sign").text = "G"
            ET.SubElement(clef, "line").text = "2"
        for note in notes:
            add_note(measure, *note)
        if number == len(measures):
            barline = ET.SubElement(measure, "barline", location="right")
            ET.SubElement(barline, "bar-style").text = "light-heavy"
    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ")
    path = OUT / f"{work_id}-score.musicxml"
    tree.write(path, encoding="utf-8", xml_declaration=True)
    return path


def build_scores():
    q = lambda pitch: (pitch, 4, "quarter")
    h = lambda pitch: (pitch, 8, "half")
    w = lambda pitch: (pitch, 16, "whole")
    C4, D4, E4, F4, G4, A4, B4 = ("C", 4), ("D", 4), ("E", 4), ("F", 4), ("G", 4), ("A", 4), ("B", 4)
    A3 = ("A", 3)
    C5, D5, E5, G5, A5 = ("C", 5), ("D", 5), ("E", 5), ("G", 5), ("A", 5)
    twinkle = [
        [q(C4), q(C4), q(G4), q(G4)], [q(A4), q(A4), h(G4)],
        [q(F4), q(F4), q(E4), q(E4)], [q(D4), q(D4), h(C4)],
        [q(G4), q(G4), q(F4), q(F4)], [q(E4), q(E4), h(D4)],
        [q(G4), q(G4), q(F4), q(F4)], [q(E4), q(E4), h(D4)],
        [q(C4), q(C4), q(G4), q(G4)], [q(A4), q(A4), h(G4)],
        [q(F4), q(F4), q(E4), q(E4)], [q(D4), q(D4), h(C4)],
    ]
    mary = [
        [q(E4), q(D4), q(C4), q(D4)], [q(E4), q(E4), h(E4)],
        [q(D4), q(D4), h(D4)], [q(E4), q(G4), h(G4)],
        [q(E4), q(D4), q(C4), q(D4)], [q(E4), q(E4), q(E4), q(E4)],
        [q(D4), q(D4), q(E4), q(D4)], [w(C4)],
    ]
    row_q = lambda pitch: (pitch, 12, "quarter")
    row_h = lambda pitch: (pitch, 24, "half")
    de = lambda pitch: (pitch, 9, "eighth", True)
    sixteenth = lambda pitch: (pitch, 3, "16th")
    triplet = lambda pitch, marker=False: (pitch, 4, "eighth", False, marker)
    row = [
        [row_q(C4), row_q(C4), de(C4), sixteenth(D4), row_q(E4)],
        [de(E4), sixteenth(D4), de(E4), sixteenth(F4), row_h(G4)],
        [triplet(C5, "start"), triplet(C5), triplet(C5, "stop"),
         triplet(G4, "start"), triplet(G4), triplet(G4, "stop"),
         triplet(E4, "start"), triplet(E4), triplet(E4, "stop"),
         triplet(C4, "start"), triplet(C4), triplet(C4, "stop")],
        [de(G4), sixteenth(F4), de(E4), sixteenth(D4), row_h(C4)],
    ]
    moonlight = [
        [q(E4), q(G4), q(A4), q(G4)], [q(E4), q(D4), h(E4)],
        [q(G4), q(A4), q(C5), q(A4)], [q(G4), q(E4), h(D4)],
        [q(E4), q(G4), q(A4), q(C5)], [q(A4), q(G4), h(E4)],
        [q(D4), q(E4), q(G4), q(E4)], [q(D4), q(E4), h(C4)],
    ]
    fruit = [
        [q(C4), q(E4), q(G4), q(E4)], [q(F4), q(A4), h(G4)],
        [q(E4), q(G4), q(A4), q(G4)], [q(E4), q(D4), h(C4)],
        [q(G4), q(A4), q(C5), q(A4)], [q(G4), q(E4), h(D4)],
        [q(E4), q(G4), q(A4), q(G4)], [q(E4), q(D4), h(E4)],
        [q(D4), q(E4), q(G4), q(E4)], [q(D4), q(E4), h(C4)],
    ]
    mouse = [
        [q(G4), q(G4), q(A4), q(G4)], [q(E4), q(E4), h(D4)],
        [q(G4), q(A4), q(C5), q(A4)], [q(G4), q(E4), h(D4)],
        [q(E4), q(E4), q(G4), q(A4)], [q(G4), q(E4), h(D4)],
        [q(C4), q(D4), q(E4), q(G4)], [q(E4), q(D4), h(C4)],
    ]
    oars = [
        [q(A4), q(C5), q(D5), q(E5)], [q(G5), q(E5), h(C5)],
        [q(D5), q(C5), q(A4), q(C5)], [q(A4), q(C5), q(D5), q(E5)],
        [q(G5), q(G5), h(A5)], [q(G5), q(E5), h(D5)],
        [q(E5), q(E5), q(G5), q(A5)], [q(G5), q(E5), h(D5)],
        [q(C5), q(D5), q(E5), q(G5)], [q(E5), q(D5), h(C5)],
        [q(D5), q(E5), q(C5), q(A4)], [q(D5), q(E5), h(C5)],
    ]
    swallow = [
        [q(E4), q(G4), q(C5), q(A4)], [q(G4), q(E4), q(G4), q(E4)],
        [q(A4), q(C5), h(G4)], [q(C5), q(E5), q(D5), q(D5)],
        [q(C5), q(D5), q(C5), q(A4)], [q(C5), q(G4), h(E4)],
        [q(E4), q(G4), q(A4), q(C5)], [q(A4), q(G4), h(E4)],
        [q(G4), q(A4), q(C5), q(D5)], [q(E5), q(D5), h(C5)],
        [q(D5), q(C5), q(A4), q(G4)], [q(E4), q(D4), h(C4)],
    ]
    smile = [
        [q(A3), q(A3), q(C4), q(D4)], [q(E4), q(G4), h(E4)],
        [q(D4), q(D4), q(D4), q(E4)], [q(G4), q(G4), h(E4)],
        [q(A3), q(A3), q(C4), q(D4)], [q(E4), q(G4), h(E4)],
        [q(D4), q(D4), q(D4), q(E4)], [q(G4), q(G4), h(A4)],
        [q(C5), q(C5), q(C5), q(C5)], [q(C5), q(C5), h(B4)],
        [q(C5), q(C5), q(C5), q(C5)], [q(D5), q(D5), h(C5)],
        [q(C5), q(C5), q(C5), q(C5)], [q(C5), q(C5), h(B4)],
        [q(D5), q(D5), q(D5), q(E5)], [q(D5), q(C5), h(A4)],
    ]
    specs = [
        ("EN-T01", "Twinkle, Twinkle, Little Star — simplified melody", twinkle, 4, {5, 9}, "Traditional", 96),
        ("EN-T02", "Mary Had a Little Lamb — simplified melody", mary, 4, {5}, "Traditional", 104),
        ("EN-T03", "Row, Row, Row Your Boat — simplified melody", row, 12, set(), "Traditional", 96),
        ("CN-T01", "月光光 — 原创器乐示范", moonlight, 4, {5}, "童年书房原创示范", 82),
        ("CN-C28", "排排坐 — 原创器乐示范", fruit, 4, {5, 9}, "童年书房原创示范", 100),
        ("CN-C26", "小老鼠上灯台 — 原创器乐示范", mouse, 4, {5}, "童年书房原创示范", 112),
        ("CN-C01", "让我们荡起双桨 — 三段完整歌词 · 主旋律教学简化", oars, 4, {5, 9}, "乔羽词 · 刘炽曲", 88),
        ("CN-C03", "小燕子 — 两段完整歌词 · 主旋律教学简化", swallow, 4, {5, 9}, "王路、王云阶词 · 王云阶曲", 92),
        ("CN-C10", "歌声与微笑 — 中英文完整唱词 · 主旋律教学简化", smile, 4, {5, 9, 13}, "王健词 · 谷建芬曲", 112),
    ]
    toolkit = verovio.toolkit()
    toolkit.setOptions({
        "pageWidth": 2200,
        "pageHeight": 2800,
        "scale": 45,
        "adjustPageHeight": True,
        "breaks": "encoded",
        "header": "none",
        "footer": "none",
        "pageMarginTop": 60,
        "pageMarginBottom": 60,
        "pageMarginLeft": 60,
        "pageMarginRight": 60,
    })
    engraved_specs = []
    for work_id, title, measures, divisions, breaks, creator, tempo in specs:
        lyric_measures = prepare_lyric_measures(measures, divisions, LYRIC_LAYOUTS[work_id])
        path = build_musicxml(work_id, title, lyric_measures, divisions, breaks, creator)
        if not toolkit.loadFile(str(path)):
            raise RuntimeError(f"Verovio could not load {path}")
        if toolkit.getPageCount() != 1:
            raise RuntimeError(f"Expected one-page score for {work_id}")
        svg = toolkit.renderToSVG(1)
        (OUT / f"{work_id}-score.svg").write_text(svg, encoding="utf-8")
        engraved_specs.append((work_id, title, lyric_measures, divisions, breaks, creator, tempo))
    return engraved_specs


def pitch_frequency(pitch):
    steps = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
    midi = (pitch[1] + 1) * 12 + steps[pitch[0]]
    return 440.0 * (2 ** ((midi - 69) / 12))


def add_tone(samples, sample_rate, start, duration, frequency, amplitude, softness=0.0):
    first = max(0, int(start * sample_rate))
    count = min(int(duration * sample_rate), len(samples) - first)
    attack = min(0.035, duration / 4)
    release = min(0.18 + softness, duration / 2)
    for offset in range(count):
        position = offset / sample_rate
        remaining = duration - position
        envelope = min(1.0, position / attack) * min(1.0, remaining / release)
        fundamental = math.sin(2 * math.pi * frequency * position)
        harmonic = math.sin(2 * math.pi * frequency * 2 * position)
        third = math.sin(2 * math.pi * frequency * 3 * position)
        samples[first + offset] += amplitude * envelope * (fundamental + 0.24 * harmonic + 0.07 * third)


def build_audio(specs):
    audio_dir = ROOT / "audio"
    sample_rate = 22050
    chinese_ids = {"CN-T01", "CN-C28", "CN-C26"}
    for work_id, _title, measures, divisions, _breaks, _creator, tempo in specs:
        if work_id not in chinese_ids:
            continue
        seconds_per_beat = 60 / tempo
        lead_in = 0.25
        tail = 0.8
        total_seconds = lead_in + len(measures) * 4 * seconds_per_beat + tail
        samples = array("f", [0.0]) * int(total_seconds * sample_rate)
        beat_cursor = 0.0
        for measure_index, measure in enumerate(measures):
            bass = ("C", 3) if measure_index % 4 in {0, 1, 3} else ("G", 3)
            add_tone(samples, sample_rate, lead_in + beat_cursor * seconds_per_beat,
                     3.7 * seconds_per_beat, pitch_frequency(bass), 0.045, 0.3)
            for pitch, duration, _note_type, *_rest in measure:
                beats = duration / divisions
                start = lead_in + beat_cursor * seconds_per_beat
                add_tone(samples, sample_rate, start, beats * seconds_per_beat * 0.92,
                         pitch_frequency(pitch), 0.22)
                beat_cursor += beats
        peak = max(abs(value) for value in samples) or 1.0
        scale = 0.82 / peak
        pcm = array("h", (int(max(-1.0, min(1.0, value * scale)) * 32767) for value in samples))
        path = audio_dir / f"{work_id}.wav"
        with wave.open(str(path), "wb") as output:
            output.setnchannels(1)
            output.setsampwidth(2)
            output.setframerate(sample_rate)
            output.writeframes(pcm.tobytes())


if __name__ == "__main__":
    build_covers()
    score_specs = build_scores()
    build_audio(score_specs)
    print(f"Built {len(score_specs)} covers and engraved scores; 3 traditional-rhyme WAV demonstrations in {ROOT}")
