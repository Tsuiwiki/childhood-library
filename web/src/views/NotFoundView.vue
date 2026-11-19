<script setup lang="ts">
// Static 404 view: no data access, no redirect tricks.
</script>

<template>
  <section class="shell missing">
    <span class="eyebrow">404</span>
    <h1>这一页还没有折好</h1>
    <p>路径不存在。前端骨架当前只提供首页与七个领域占位页。</p>
    <RouterLink class="button button-primary" to="/">返回首页</RouterLink>
  </section>
</template>

<style scoped>
.missing { padding-block: 72px; }
.missing h1 { font-family: var(--serif); font-size: clamp(32px, 5vw, 50px); font-weight: 900; }
.missing p { max-width: 560px; margin-bottom: 26px; }
</style>
