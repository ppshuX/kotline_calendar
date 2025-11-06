<template>
  <div class="toolbar">
    <el-button type="primary" @click="$emit('add')">
      ➕ 添加日程
    </el-button>
    <el-button @click="$emit('refresh')">
      🔄 刷新
    </el-button>
    <el-button @click="$emit('testLunar')">
      🏮 测试农历
    </el-button>
  </div>
</template>

<script setup>
defineEmits(['add', 'refresh', 'testLunar'])
</script>

<style scoped>
.toolbar {
  display: flex;
  gap: 10px;
  justify-content: center;
  flex-wrap: wrap;
}

@media (max-width: 768px) {
  .toolbar {
    gap: 8px;
  }
}
</style>

