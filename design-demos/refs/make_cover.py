from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
b64 = (ROOT / "refs" / "cn-c01-b64.txt").read_text(encoding="utf-8")

frame = """<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 800 600" role="img" aria-labelledby="title desc">
  <title id="title">CN-C01 — 让我们 荡起双桨</title>
  <desc id="desc">童年书房剪贴簿书封，内嵌手绘课本插画</desc>
  <defs>
    <pattern id="dots" width="18" height="18" patternUnits="userSpaceOnUse"><circle cx="3" cy="3" r="1.8" fill="#191917" opacity=".22"/></pattern>
    <clipPath id="art"><rect x="44" y="184" width="712" height="330" rx="6"/></clipPath>
  </defs>
  <rect width="800" height="600" fill="#f4eddc"/>
  <rect width="800" height="600" fill="url(#dots)"/>
  <rect x="18" y="18" width="764" height="564" fill="none" stroke="#191917" stroke-width="8"/>
  <rect x="42" y="42" width="14" height="116" fill="#e64a38" stroke="#191917" stroke-width="4"/>
  <rect x="548" y="48" width="184" height="52" fill="#fffaf0" stroke="#191917" stroke-width="4" transform="rotate(3 640 74)"/>
  <text x="640" y="83" text-anchor="middle" font-family="Arial, sans-serif" font-size="24" font-weight="900" fill="#191917">CN-C01</text>
  <g class="title" fill="#191917" font-family="Georgia, 'Noto Serif CJK SC', 'Songti SC', SimSun, serif" font-size="45" font-weight="900" letter-spacing="-1"><text x="54" y="98" class="cover-title">让我们</text><text x="54" y="152" class="cover-title">荡起双桨</text></g>
  <g clip-path="url(#art)"><image xlink:href="data:image/jpeg;base64,__IMG__" x="44" y="184" width="712" height="330" preserveAspectRatio="xMidYMid slice"/></g>
  <rect x="44" y="184" width="712" height="330" fill="none" stroke="#191917" stroke-width="6"/>
  <rect x="48" y="520" width="704" height="38" fill="#fffaf0" stroke="#191917" stroke-width="4"/>
  <text x="64" y="546" font-family="Arial, 'Microsoft YaHei', sans-serif" font-size="20" font-weight="800" fill="#191917">童年书房 · 经典创作儿歌 · 手绘封面</text>
</svg>
"""

svg = frame.replace("__IMG__", b64)
target = ROOT / "song-assets" / "CN-C01-cover.svg"
target.write_text(svg, encoding="utf-8")
print("written", target, len(svg))
