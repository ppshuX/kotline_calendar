<template>
  <div class="toolbar">
    <button class="tool-btn" @click="$emit('show-list')">
      📝 日程 ({{ eventCount }})
    </button>
    <button class="tool-btn" @click="$emit('show-fortune')">
      🔮 运势
    </button>
    <button class="tool-btn" @click="$emit('show-weather')">
      🌤️ 天气
    </button>
    <button class="tool-btn" @click="$emit('show-ai')">
      🤖 AI
    </button>
  </div>
</template>

<script>
export default {
  name: 'ToolBar',
  props: {
    eventCount: {
      type: Number,
      default: 0
    }
  }
}
</script>

<style scoped>
.toolbar {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  margin-bottom: 20px;
  flex-wrap: wrap;
  padding: 0 10px;
}

.tool-btn {
  flex: 1;
  padding: 12px 16px;
  background: white;
  color: #606266;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  white-space: nowrap;
}

.tool-btn:hover {
  background: #f5f7fa;
  border-color: #667eea;
  color: #667eea;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(102, 126, 234, 0.15);
}

/* 移除特殊样式，所有按钮统一 */
</style>

