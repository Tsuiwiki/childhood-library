<script setup lang="ts">
import { DOMAIN_NAMES } from '@/api/types'
</script>

<template>
  <div class="app-shell">
    <header class="site-header">
      <div class="shell header-inner">
        <RouterLink class="brand" to="/">
          童年书房 <small>T-08 · 前端工程骨架</small>
        </RouterLink>
        <nav class="desktop-nav" aria-label="领域占位导航">
          <RouterLink v-for="domain in DOMAIN_NAMES" :key="domain" :to="`/${domain}`">
            {{ domain }}
          </RouterLink>
        </nav>
      </div>
    </header>

    <main id="main-content">
      <RouterView />
    </main>

    <footer class="site-footer">
      <div class="shell">
        原型页面仍在 <code>design-demos/</code> 下可独立打开；本工程不改动原型、不导入业务数据。
      </div>
    </footer>
  </div>
</template>

<style scoped>
.app-shell { display: flex; flex-direction: column; min-height: 100vh; }
.site-header { position: sticky; z-index: 30; top: 0; border-bottom: var(--line); background-color: var(--paper); background-image: radial-gradient(circle, rgba(25, 25, 23, 0.16) 0.8px, transparent 0.9px); background-size: 9px 9px; }
.header-inner { min-height: 84px; display: flex; align-items: center; gap: 24px; flex-wrap: wrap; padding-block: 12px; }
.brand { display: inline-flex; align-items: center; min-height: 48px; margin-right: auto; text-decoration: none; font-family: var(--serif); font-size: 24px; font-weight: 900; letter-spacing: 0.08em; }
.brand small { margin-left: 12px; padding-left: 12px; border-left: 2px solid var(--ink); font-family: var(--sans); font-size: 12px; font-weight: 700; letter-spacing: 0.08em; }
.desktop-nav { display: flex; flex-wrap: wrap; align-items: center; gap: 4px; }
.desktop-nav a { display: inline-flex; align-items: center; min-height: 40px; padding: 6px 10px; text-decoration: none; font-size: 13px; font-weight: 700; }
.desktop-nav a:hover, .desktop-nav a.router-link-active { text-decoration: underline 3px var(--red); text-underline-offset: 6px; }
main { flex: 1; }
.site-footer { padding-block: 22px; border-top: var(--line); font-size: 13px; }
.site-footer code { padding: 1px 5px; background: rgba(25, 25, 23, 0.08); }
@media (max-width: 720px) { .desktop-nav { display: none; } }
</style>
