<template>
  <div class="holiday-content">
    <!-- 节日详情页 -->
    <FestivalDetail 
      v-if="showingDetail" 
      :festival="selectedFestival"
      @close="showingDetail = false"
    />
    
    <!-- 节日列表页 -->
    <div v-else>
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
      @click="showFestivalDetail(festival)"
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
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import FestivalDetail from './FestivalDetail.vue'

// 详情页状态
const showingDetail = ref(false)
const selectedFestival = ref(null)

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

const holiday = computed(() => {
  console.log('节日数据:', props.todayHolidays)
  return props.todayHolidays?.is_holiday || false
})

// 合并所有节日（API返回的festivals数组）
const allFestivals = computed(() => {
  const festivals = props.todayHolidays?.festivals || []
  console.log('所有节日:', festivals)
  return festivals
})

// 获取节日卡片颜色类（4色循环）
const getFestivalColorClass = (index) => {
  const colors = ['pink', 'purple', 'blue', 'green']
  return colors[index % 4]
}

// 显示节日详情
const showFestivalDetail = (festival) => {
  if (!festival || !festival.name) return
  
  selectedFestival.value = festival
  showingDetail.value = true
  console.log('显示节日详情:', festival)
}
</script>

<style scoped>
.holiday-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
  height: 100%;
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
  padding: 16px;
  border-radius: 12px;
  transition: transform 0.25s ease, box-shadow 0.25s ease;
  margin-bottom: 12px;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
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

/* 节日卡片悬浮效果（4色） */
.holiday-card.pink:hover,
.holiday-card.purple:hover,
.holiday-card.blue:hover,
.holiday-card.green:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.18);
  cursor: pointer;
}

.holiday-card.pink:active,
.holiday-card.purple:active,
.holiday-card.blue:active,
.holiday-card.green:active {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
  transition: all 0.1s ease;
}

/* 不可点击的卡片浅色阴影 */
.holiday-card.lunar,
.holiday-card.major,
.holiday-card.empty {
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}

.holiday-card.lunar:hover,
.holiday-card.major:hover,
.holiday-card.empty:hover {
  transform: none;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
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
  .holiday-content {
    gap: 12px;
  }
  
  .sidebar-header h4 {
    font-size: 16px;
  }
  
  .sidebar-header p {
    font-size: 11px;
  }
  
  .holiday-card {
    padding: 12px;
    gap: 10px;
    margin-bottom: 10px;
  }

  .holiday-icon {
    font-size: 24px;
  }

  .holiday-name {
    font-size: 14px;
  }
  
  .holiday-type {
    font-size: 12px;
  }
}

@media (max-width: 576px) {
  .holiday-content {
    gap: 10px;
  }
  
  .sidebar-header h4 {
    font-size: 15px;
  }
  
  .sidebar-header p {
    font-size: 10px;
  }
  
  .holiday-card {
    padding: 10px;
    gap: 8px;
    margin-bottom: 8px;
  }
  
  .holiday-icon {
    font-size: 20px;
  }
  
  .holiday-name {
    font-size: 13px;
  }
  
  .holiday-type {
    font-size: 11px;
  }
}
</style>
