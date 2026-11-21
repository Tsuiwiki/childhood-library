<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import ClAudioPlayer from '@/components/ClAudioPlayer.vue'
import { useAudioPlayer } from '@/composables/useAudioPlayer'

const route = useRoute()
const { selectedTrack, closePlayer } = useAudioPlayer()
const mobileOpen = ref(false)
const isResearchHall = computed(() => ['story', 'poetry'].includes(String(route.name)))
const navItems = [
  { label: '资料总览', to: '/library', external: false },
  { label: '故事馆', to: '/story', external: false },
  { label: '音乐馆', to: '/music', external: false },
  { label: '古诗词馆', to: '/poetry', external: false },
  { label: '研究资源库', to: '/research.html', external: true },
  { label: '作品目录', to: '/works', external: false },
]

watch(() => route.fullPath, () => { mobileOpen.value = false })
</script>

<template>
  <div class="app-shell">
    <header class="site-header">
      <div class="shell header-inner">
        <a class="brand" href="/" aria-label="返回童年书房原型首页">童年书房 <small>CHILDHOOD<br>LIBRARY</small></a>
        <nav class="desktop-nav" aria-label="主导航">
          <a href="/">书房首页</a>
          <template v-for="item in navItems" :key="item.to">
            <a v-if="item.external" :href="item.to">{{ item.label }}</a>
            <RouterLink v-else :to="item.to">{{ item.label }}</RouterLink>
          </template>
        </nav>
        <button
          class="menu-toggle"
          type="button"
          :aria-expanded="mobileOpen"
          aria-controls="mobile-nav"
          :aria-label="mobileOpen ? '收起导航' : '展开导航'"
          @click="mobileOpen = !mobileOpen"
          @keydown.esc="mobileOpen = false"
        ><span></span><span></span><span></span></button>
      </div>
      <nav v-if="mobileOpen" id="mobile-nav" class="shell mobile-nav" aria-label="移动端导航" @keydown.esc="mobileOpen = false">
        <a href="/">书房首页</a>
        <template v-for="item in navItems" :key="item.to">
          <a v-if="item.external" :href="item.to">{{ item.label }}</a>
          <RouterLink v-else :to="item.to">{{ item.label }}</RouterLink>
        </template>
      </nav>
    </header>

    <main id="main-content">
      <RouterView />
    </main>

    <footer v-if="!isResearchHall" class="site-footer">
      <div class="shell">内部研究前端 · 原型页面保留在 <code>design-demos/</code>；录音与权利状态以各条目说明为准。</div>
    </footer>

    <ClAudioPlayer :track="selectedTrack" @close="closePlayer" />
  </div>
</template>

<style scoped>
.app-shell { display: flex; flex-direction: column; min-height: 100svh; }
.site-header { position: sticky; z-index: 30; top: 0; border-bottom: var(--line); background-color: var(--paper); background-image: radial-gradient(circle, rgba(25, 25, 23, 0.16) 0.8px, transparent 0.9px); /* taste-skill-ignore: 保留原型页头纸纹。 */ background-size: 9px 9px; }
.header-inner { min-height: 80px; display: flex; align-items: center; gap: 22px; padding-block: 10px; }
.brand { display: inline-flex; align-items: center; min-height: 48px; margin-right: auto; text-decoration: none; font-family: var(--serif); font-size: 24px; font-weight: 900; letter-spacing: 0.08em; white-space: nowrap; }
.brand small { margin-left: 11px; padding-left: 11px; border-left: 2px solid var(--ink); font-family: var(--sans); font-size: 11px; font-weight: 700; line-height: 1.25; letter-spacing: 0.08em; }
.desktop-nav { display: flex; flex-wrap: wrap; align-items: center; gap: 2px; }
.desktop-nav a, .mobile-nav a { display: inline-flex; align-items: center; min-height: 44px; padding: 8px 11px; text-decoration: none; font-size: 15px; font-weight: 800; }
.desktop-nav a:hover, .desktop-nav a.router-link-active, .mobile-nav a.router-link-active { text-decoration: underline 3px var(--red); text-underline-offset: 6px; }
.menu-toggle { display: none; width: 48px; height: 48px; padding: 11px; border: var(--line); background: var(--yellow); box-shadow: 3px 3px 0 var(--ink); /* taste-skill-ignore: 保留原型移动菜单按钮硬阴影。 */ }
.menu-toggle span { display: block; width: 100%; height: 2px; margin: 4px 0; background: var(--ink); }
.mobile-nav { padding: 8px 0 18px; border-top: 2px solid var(--ink); }
.mobile-nav a { width: 100%; border-bottom: 1px dashed var(--ink); /* taste-skill-ignore: 保留原型移动导航虚线分隔。 */ }
main { flex: 1; }
.site-footer { padding-block: 22px; border-top: var(--line); font-size: 13px; }
.site-footer code { padding: 1px 5px; background: rgba(25, 25, 23, 0.08); }
@media (max-width: 1080px) { .desktop-nav a { padding-inline: 8px; font-size: 14px; } }
@media (max-width: 900px) { .desktop-nav { display: none; } .menu-toggle { display: block; } .header-inner { gap: 12px; } }
@media (max-width: 640px) { .header-inner, .mobile-nav { width: min(calc(100% - 32px), 1240px); } .brand { font-size: 21px; } .brand small { font-size: 9px; } }
</style>
