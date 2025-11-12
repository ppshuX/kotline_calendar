<template>
  <div class="holiday-content">
    <div class="sidebar-header text-center mb-3">
      <h4>🎉 节日信息</h4>
      <p class="text-secondary small mb-0">
        {{ displayDateLabel }}
      </p>
    </div>

    <!-- 农历信息卡片：总是显示 -->
    <div class="holiday-card lunar">
      <div class="holiday-icon">🏮</div>
      <div class="holiday-info">
        <div class="holiday-name">农历</div>
        <div class="holiday-type">{{ todayHolidays?.lunar || '加载中...' }}</div>
      </div>
    </div>

    <!-- 法定节假日卡片 -->
    <div class="holiday-card major" v-if="holiday">
      <div class="holiday-icon">🎉</div>
      <div class="holiday-info">
        <div class="holiday-name">法定节假日</div>
        <div class="holiday-type">今日为国家法定节假日</div>
      </div>
    </div>

    <!-- 所有节日统一显示（使用4色循环） -->
    <div
      v-for="(festival, index) in allFestivals"
      :key="`festival-${index}`"
      class="holiday-card"
      :class="getFestivalColorClass(index)"
    >
      <div class="holiday-icon">{{ festival.emoji || '🎊' }}</div>
      <div class="holiday-info">
        <div class="holiday-name">{{ festival.name }}</div>
        <div class="holiday-type">点击查看详情</div>
      </div>
    </div>

    <!-- 无节日提示 -->
    <div
      v-if="!holiday && allFestivals.length === 0"
      class="holiday-card empty"
    >
      <div class="holiday-icon">📅</div>
      <div class="holiday-info">
        <div class="holiday-name">今日无特殊节日</div>
        <div class="holiday-type">享受平凡的一天 ☀️</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  todayHolidays: {
    type: Object,
    default: () => null
  },
  selectedDateLabel: {
    type: String,
    default: ''
  }
})

// 显示日期标签（如果有传入则使用，否则显示今天）
const displayDateLabel = computed(() => {
  if (props.selectedDateLabel) {
    return props.selectedDateLabel
  }
  
  // 默认显示今天
  return new Date().toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'long'
  })
})

const holiday = computed(() => props.todayHolidays?.holiday || null)

// 合并所有节日（国际 + 传统）
const allFestivals = computed(() => {
  const international = props.todayHolidays?.international_festivals || []
  const traditional = props.todayHolidays?.traditional_festivals || []
  return [...international, ...traditional]
})

// 获取节日卡片颜色类（4色循环）
const getFestivalColorClass = (index) => {
  const colors = ['pink', 'purple', 'blue', 'green']
  return colors[index % 4]
}
</script>

<style scoped>
.holiday-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
  height: 100%;
  overflow-y: auto;
  padding-right: 8px;
}

.sidebar-header h4 {
  color: var(--text-primary);
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 6px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.section-title i {
  font-size: 18px;
  color: var(--primary-color);
}

.holiday-card {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  border-radius: 12px;
  transition: transform 0.25s ease, box-shadow 0.25s ease;
  margin-bottom: 12px;
  cursor: pointer;
}

/* 农历卡片：橙色系 */
.holiday-card.lunar {
  background-color: #FFE0B2;
  cursor: default;
}

/* 法定节假日卡片：黄色系 */
.holiday-card.major {
  background-color: #FFF9C4;
  cursor: default;
}

/* 节日卡片：4色循环 */
.holiday-card.pink {
  background-color: #F8BBD0;
}

.holiday-card.purple {
  background-color: #E1BEE7;
}

.holiday-card.blue {
  background-color: #BBDEFB;
}

.holiday-card.green {
  background-color: #C5E1A5;
}

/* 无节日卡片：灰蓝色 */
.holiday-card.empty {
  background-color: #ECEFF1;
  cursor: default;
}

/* 只有节日卡片才有hover效果 */
.holiday-card.pink:hover,
.holiday-card.purple:hover,
.holiday-card.blue:hover,
.holiday-card.green:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.holiday-card.pink:active,
.holiday-card.purple:active,
.holiday-card.blue:active,
.holiday-card.green:active {
  transform: translateY(0px);
  transition: transform 0.1s ease;
}

.holiday-icon {
  font-size: 32px;
}

.holiday-info {
  flex: 1;
}

.holiday-name {
  font-size: 18px;
  font-weight: 600;
  color: #4A148C;
  margin-bottom: 4px;
}

.holiday-type {
  font-size: 14px;
  color: #6A1B9A;
}

@media (max-width: 768px) {
  .sidebar-header h4 {
    font-size: 18px;
  }
  
  .section-title {
    font-size: 15px;
  }
  
  .holiday-card {
    padding: 14px;
    gap: 12px;
    margin-bottom: 12px;
  }

  .holiday-icon {
    font-size: 28px;
  }

  .holiday-name {
    font-size: 16px;
  }
  
  .holiday-type {
    font-size: 13px;
  }
}

@media (max-width: 576px) {
  .holiday-content {
    gap: 16px;
  }
  
  .sidebar-header h4 {
    font-size: 16px;
  }
  
  .section-title {
    font-size: 14px;
  }
  
  .holiday-card {
    padding: 12px;
    gap: 10px;
  }
  
  .holiday-icon {
    font-size: 24px;
  }
  
  .holiday-name {
    font-size: 15px;
  }
  
  .holiday-type {
    font-size: 12px;
  }
}
</style>
