<script setup lang="ts">
import ClLibraryMap from '@/components/ClLibraryMap.vue'
import { specialtyCount, specialtyDefinitions } from '@/research/specialties'

const pillars = [
  { key: 'ROOT', name: '中国经典', count: '55 首', description: '创作儿歌、传统童谣、地方歌谣、诗词音乐等。', className: 'p-china' },
  { key: 'WINDOW', name: '世界经典', count: '30 首', description: '多语言童谣、摇篮曲、儿童古典音乐等。', className: 'p-world' },
  { key: 'FUTURE', name: '优秀原创', count: '15 首', description: '通过编辑评审且授权路径清楚的原创作品。', className: 'p-original' },
]
</script>

<template>
  <div class="music-page">
    <section class="shell hero" aria-labelledby="page-title">
      <span class="eyebrow"><!-- taste-skill-ignore: 保留原型旋转眉题。 -->儿童音乐馆 · MUSIC HALL</span>
      <h1 id="page-title">以中国经典为根，<br><span class="accent">以世界经典为窗</span>，以优秀原创为未来。</h1>
      <p class="hero-desc">一座免费供大众及教育使用的儿童音乐数据库。以清楚的来源、版本与权利记录为基础，让孩子听见自然、优美、安静与想象。</p>
      <div class="hero-actions">
        <RouterLink class="button button-primary" to="/works">浏览候选目录 <span aria-hidden="true">→</span></RouterLink>
        <a class="button" href="#specialties">看八个专题</a>
      </div>
    </section>

    <section class="shell specialties" id="specialties" aria-labelledby="spec-title">
      <div class="section-heading">
        <h2 id="spec-title">八个专题</h2>
        <p>音乐馆按八个内容专题策展。专题可以多选，不替代作品类型、地区、语言与年代等基础字段。</p>
      </div>
      <div class="spec-grid">
        <RouterLink
          v-for="specialty in specialtyDefinitions"
          :key="specialty.id"
          class="spec-card"
          :class="`s-${specialty.id}`"
          :to="`/music/specialties/${specialty.id}`"
        >
          <span class="count">{{ specialtyCount(specialty.id) || '待授权' }}<template v-if="specialtyCount(specialty.id)"> 首</template></span>
          <span class="no">{{ specialty.no }} · {{ specialty.name }}</span>
          <h3>{{ specialty.name }}</h3>
          <p>{{ specialty.shortDescription }}</p>
          <span class="go">进入专题 <span aria-hidden="true">→</span></span>
        </RouterLink>
      </div>
    </section>

    <section class="shell pillars" aria-labelledby="pillars-title">
      <div class="section-heading">
        <h2 id="pillars-title">三大支柱 · 首批 100 首种子库</h2>
        <p>启动期资源分配：中国经典 55%、世界经典 30%、优秀原创 15%。候选数、资料完整数、授权可播放数分别统计。</p>
      </div>
      <div class="pillar-row">
        <article v-for="pillar in pillars" :key="pillar.name" class="pillar-card" :class="pillar.className">
          <span class="kicker"><!-- taste-skill-ignore: 保留原型支柱标签。 -->{{ pillar.name }} · {{ pillar.key }}</span>
          <h3>{{ pillar.name }}</h3>
          <span class="num">{{ pillar.count }}</span>
          <p>{{ pillar.description }}</p>
        </article>
      </div>
    </section>

    <section class="shell catalogue" aria-labelledby="catalogue-title">
      <div class="catalogue-band">
        <div class="copy">
          <h2 id="catalogue-title">发现目录 · 105 条已登记</h2>
          <p>中国经典 55 张资料卡与世界经典 47 条资料卡构成当前发现目录。已有录音的作品提供真实来源、版本和权利说明；暂未取得可核验真实录音的播放位标为“待采集”，不以程序合成音冒充原曲。当前 Vue 内部曲目页展示其中 58 条有录音的研究记录，完整 105 条正式业务目录尚未导入数据库。</p>
        </div>
        <RouterLink class="button" to="/works">打开内部曲目 <span aria-hidden="true">→</span></RouterLink>
      </div>
    </section>

    <section class="shell footnote" aria-label="馆藏边界">
      <h2 class="visually-hidden">馆藏边界</h2>
      <p>本页面为儿童音乐馆馆藏导览层，依据《儿童经典音乐图书馆建设方案》§2.1 八个专题与 §11 信息架构整理。所有曲目均为候选发现层，不构成法律意见，也不授予任何第三方内容的使用权。</p>
    </section>

    <ClLibraryMap current="music" />
  </div>
</template>

<style scoped>
.music-page { --page-width: 1280px; }
.music-page > .shell { width: min(calc(100% - 48px), var(--page-width)); }
.hero { padding-block: 60px 50px; }
.hero h1 { margin-bottom: 18px; font-family: var(--serif); font-size: clamp(42px, 5vw, 64px); font-weight: 900; line-height: 1.14; letter-spacing: -.04em; }
.accent { color: var(--red); }
.hero-desc { max-width: 620px; margin-bottom: 26px; font-size: 18px; line-height: 1.9; font-weight: 500; }
.hero-actions { display: flex; flex-wrap: wrap; gap: 16px; }
.specialties, .pillars { padding-block: 24px 36px; scroll-margin-top: 104px; }
.section-heading { margin-bottom: 30px; }
.spec-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 18px; }
.spec-card { display: flex; flex-direction: column; gap: 8px; text-align: left; border: var(--line); background: var(--paper-light); box-shadow: 5px 5px 0 var(--ink); /* taste-skill-ignore: 保留原型专题卡硬阴影。 */ padding: 18px 16px; text-decoration: none; transition: translate .15s ease, box-shadow .15s ease; position: relative; }
.spec-card:hover { translate: -2px -2px; box-shadow: 7px 7px 0 var(--ink); /* taste-skill-ignore: 保留原型专题卡悬停硬阴影。 */ }
.no { font-size: 12px; font-weight: 900; letter-spacing: .1em; }
.spec-card h3 { margin: 0; font-family: var(--serif); font-size: 20px; font-weight: 900; }
.spec-card p { margin: 0; font-size: 13px; color: var(--ink-soft); line-height: 1.55; }
.go { margin-top: auto; display: inline-flex; align-items: center; gap: 6px; font-size: 13px; font-weight: 800; }
.count { position: absolute; top: -11px; right: 12px; padding: 1px 8px; border: 2px solid var(--ink); background: var(--yellow); font-size: 11px; font-weight: 800; transform: rotate(2deg); }
.s-childhood .no { color: var(--red); } .s-nature .no { color: var(--green); } .s-play .no { color: #8a640b; } .s-lullaby .no, .s-world .no { color: var(--blue); } .s-classical .no, .s-forgotten .no { color: var(--brown); } .s-original .no { color: var(--green); }
.pillar-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
.pillar-card { border: var(--line); background: var(--paper-light); box-shadow: var(--shadow); /* taste-skill-ignore: 保留原型支柱与目录横幅硬阴影。 */ padding: 22px 20px; }
.kicker { font-size: 12px; font-weight: 800; letter-spacing: .12em; } /* taste-skill-ignore: 保留原型支柱标签。 */
.pillar-card h3 { font-family: var(--serif); font-size: 22px; font-weight: 900; margin: 6px 0; }
.num { font-size: 26px; font-weight: 900; font-family: var(--serif); }
.pillar-card p { margin: 6px 0 0; font-size: 13px; color: var(--ink-soft); }
.p-china .num, .p-china .kicker { color: var(--red); } .p-world .num, .p-world .kicker { color: var(--blue); } .p-original .num, .p-original .kicker { color: var(--green); } /* taste-skill-ignore: 保留原型支柱标签配色。 */
.catalogue { padding-block: 24px 56px; }
.catalogue-band { border: var(--line); background: var(--blue); box-shadow: var(--shadow); /* taste-skill-ignore: 保留原型支柱与目录横幅硬阴影。 */ color: var(--paper-light); padding: 32px; display: flex; align-items: center; gap: 26px; flex-wrap: wrap; }
.copy { flex: 1 1 380px; }
.catalogue-band h2 { font-family: var(--serif); font-size: 26px; font-weight: 900; margin-bottom: 8px; }
.catalogue-band p { margin: 0; font-size: 15px; }
.catalogue-band .button { background: var(--yellow); color: var(--ink); flex-shrink: 0; }
.footnote { padding-block: 8px 60px; }
.footnote p { max-width: 780px; font-size: 13px; color: var(--ink-soft); }
@media (max-width: 1000px) { .spec-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 900px) { .pillar-row { grid-template-columns: 1fr; } }
@media (max-width: 640px) { .music-page > .shell { width: min(calc(100% - 32px), var(--page-width)); } .spec-grid { grid-template-columns: 1fr; } .hero { padding-block: 40px 36px; } .hero h1 { font-size: clamp(34px, 10vw, 48px); } .catalogue-band { padding: 26px 22px; } }
</style>
