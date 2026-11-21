<script setup lang="ts">
import { specialtyDefinitions } from '@/research/specialties'

withDefaults(defineProps<{ current?: 'story' | 'music' | 'poetry' | 'research' }>(), {
  current: undefined,
})

const halls = [
  { id: 'story', name: '故事馆', to: '/story', description: '九个目录组 · 100 条研究记录' },
  { id: 'music', name: '音乐馆', to: '/music', description: '八专题 · 105 条发现目录' },
  { id: 'poetry', name: '古诗词馆', to: '/poetry', description: '十个专题 · 60 条研究记录' },
  { id: 'research', name: '研究资源库', to: '/research.html', description: '五维状态 · 来源与边界' },
] as const
</script>

<template>
  <section class="shell lib-map" aria-labelledby="library-map-title">
    <div class="lib-map-box">
      <h2 id="library-map-title">全站地图 · 三馆与研究层</h2>
      <p>童年书房分为研究资源库与儿童使用层。三馆目录可以互相跳转，音乐馆八个专题横向串联，作品目录可回链到专题与研究层。</p>
      <div class="lib-halls">
        <component
          :is="hall.to.endsWith('.html') ? 'a' : 'RouterLink'"
          v-for="hall in halls"
          :key="hall.id"
          class="lib-hall"
          :class="`lib-${hall.id}`"
          :href="hall.to.endsWith('.html') ? hall.to : undefined"
          :to="hall.to.endsWith('.html') ? undefined : hall.to"
          :aria-current="current === hall.id ? 'page' : undefined"
        >
          <b>{{ hall.name }}</b><span>{{ hall.description }}</span>
        </component>
      </div>
      <div class="lib-specs">
        <strong>音乐馆八专题：</strong>
        <RouterLink
          v-for="specialty in specialtyDefinitions"
          :key="specialty.id"
          :to="`/music/specialties/${specialty.id}`"
        >{{ specialty.no }} {{ specialty.name }}</RouterLink>
      </div>
      <div class="lib-more">
        <RouterLink to="/library">跨馆资料总览与检索</RouterLink>
        <RouterLink to="/music/catalog">百年儿歌目录</RouterLink>
        <RouterLink to="/music/sources">音源链接</RouterLink>
        <RouterLink to="/works">内部曲目与录音详情</RouterLink>
        <a href="https://github.com/Tsuiwiki/childhood-library/blob/main/docs/PROJECT_PRINCIPLES.md" target="_blank" rel="noopener noreferrer">项目顶层原则</a>
        <a href="https://github.com/Tsuiwiki/childhood-library/blob/main/docs/DATA_MODEL.md" target="_blank" rel="noopener noreferrer">统一数据模型</a>
        <a href="https://github.com/Tsuiwiki/childhood-library/blob/main/docs/COPYRIGHT_POLICY.md" target="_blank" rel="noopener noreferrer">来源与权利说明</a>
      </div>
    </div>
  </section>
</template>

<style scoped>
.lib-map { padding-block: 26px 54px; scroll-margin-top: 104px; }
.lib-map-box { border: var(--line); background: var(--paper-light); box-shadow: var(--shadow); /* taste-skill-ignore: 保留原型全站地图硬阴影。 */ padding: 26px 26px 22px; }
.lib-map-box h2 { font-family: var(--serif); font-size: clamp(24px, 3vw, 32px); font-weight: 900; margin-bottom: 6px; }
.lib-map-box > p { font-size: 14px; color: var(--ink-soft); margin-bottom: 20px; }
.lib-halls { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; }
.lib-hall { display: flex; flex-direction: column; gap: 4px; padding: 14px 14px 12px; border: var(--line); background: var(--paper-light); box-shadow: 4px 4px 0 var(--ink); /* taste-skill-ignore: 保留原型场馆卡硬阴影。 */ text-decoration: none; transition: translate .15s ease, box-shadow .15s ease; }
.lib-hall:hover { translate: -2px -2px; box-shadow: 6px 6px 0 var(--ink); /* taste-skill-ignore: 保留原型悬停硬阴影。 */ }
.lib-hall b { font-family: var(--serif); font-size: 20px; font-weight: 900; }
.lib-hall span { font-size: 12px; line-height: 1.5; color: var(--ink-soft); }
.lib-story { background: #fbe3dd; }
.lib-music { background: #fdf1c9; }
.lib-poetry { background: #e2ebd7; }
.lib-research { background: #dde5f6; }
.lib-hall[aria-current='page'] { outline: 3px dashed var(--ink); outline-offset: 3px; }
.lib-specs { margin-top: 20px; padding-top: 16px; border-top: 2px dashed var(--ink); display: flex; flex-wrap: wrap; align-items: center; gap: 8px; }
.lib-specs > strong { font-size: 13px; margin-right: 4px; }
.lib-specs a { padding: 4px 10px; border: 2px solid var(--ink); background: var(--paper-light); box-shadow: 2px 2px 0 var(--ink); /* taste-skill-ignore: 保留原型专题链接硬阴影。 */ font-size: 12px; font-weight: 800; text-decoration: none; }
.lib-specs a:hover { background: var(--yellow); }
.lib-more { margin-top: 16px; display: flex; flex-wrap: wrap; gap: 16px; font-size: 13px; font-weight: 800; }
.lib-more a { text-decoration: underline 2px var(--blue); text-underline-offset: 4px; }
@media (max-width: 1000px) { .lib-halls { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 640px) { .lib-halls { grid-template-columns: 1fr; } .lib-map-box { padding: 20px 16px 18px; } }
</style>
