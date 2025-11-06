<script setup>
import { RouterView } from 'vue-router'
</script>

<template>
  <RouterView />
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

/* 去除所有链接下划线 */
a {
  text-decoration: none !important;
}

a:hover {
  text-decoration: none !important;
}

html, body {
  margin: 0;
  padding: 0;
  overflow-x: hidden;
}

body {
  font-family: 'Helvetica Neue', Arial, 'PingFang SC', 'Microsoft YaHei', sans-serif;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

#app {
  min-height: 100vh;
}
</style>
