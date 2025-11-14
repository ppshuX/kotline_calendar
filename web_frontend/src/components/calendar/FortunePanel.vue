<template>
  <div class="fortune-content">
    <div class="sidebar-header text-center mb-3">
      <h4>🔮 今日运势</h4>
      <p class="text-secondary small mb-0">
        {{ todayDate }}
      </p>
    </div>

    <div v-if="loading" class="loading-state">
      加载中...
    </div>

    <template v-else>
      <!-- 运势指数卡片 -->
      <div class="fortune-card score">
        <div class="card-icon">📊</div>
        <div class="card-content">
          <div class="card-title">运势指数</div>
          <div class="score-display">
            <div class="stars">{{ starRating }}</div>
            <div class="score-value">({{ fortuneScore }}分)</div>
          </div>
          <div class="fortune-desc">{{ fortuneDescription }}</div>
        </div>
      </div>

      <!-- 黄历宜忌 -->
      <div class="fortune-card almanac">
        <div class="card-icon">📖</div>
        <div class="card-content">
          <div class="card-title">黄历宜忌</div>
          <div class="almanac-item good">
            <span class="almanac-label">✅ 宜：</span>
            <span class="almanac-text">{{ goodThings.join('、') }}</span>
          </div>
          <div class="almanac-item bad">
            <span class="almanac-label">❌ 忌：</span>
            <span class="almanac-text">{{ badThings.join('、') }}</span>
          </div>
        </div>
      </div>

      <!-- 幸运元素 -->
      <div class="fortune-card lucky">
        <div class="card-icon">✨</div>
        <div class="card-content">
          <div class="card-title">幸运元素</div>
          <div class="lucky-grid">
            <div class="lucky-item">
              <div class="lucky-label">🎨 幸运色</div>
              <div class="lucky-value" :style="{ color: getLuckyColorHex(luckyColor) }">
                {{ luckyColor }}
              </div>
            </div>
            <div class="lucky-item">
              <div class="lucky-label">🔢 幸运数字</div>
              <div class="lucky-value">{{ luckyNumber }}</div>
            </div>
            <div class="lucky-item">
              <div class="lucky-label">⚡ 五行</div>
              <div class="lucky-value">{{ luckyElement }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 温馨提示 -->
      <div class="fortune-card tip">
        <div class="card-icon">💡</div>
        <div class="card-content">
          <div class="card-title">温馨提示</div>
          <div class="tip-text">{{ weekdayTip }}</div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { fortuneAPI } from '@/api'

// 响应式数据
const todayDate = ref('加载中...')
const fortuneScore = ref(0)
const starRating = ref('')
const fortuneDescription = ref('')
const goodThings = ref([])
const badThings = ref([])
const luckyColor = ref('')
const luckyNumber = ref(0)
const luckyElement = ref('')
const weekdayTip = ref('')
const loading = ref(true)

// 从API加载今日运势
const loadFortune = async () => {
  try {
    const savedCity = localStorage.getItem('weather_city') || '南昌市'
    const response = await fortuneAPI.getTodayFortune(savedCity)
    
    // 设置日期
    const now = new Date()
    const year = now.getFullYear()
    const month = now.getMonth() + 1
    const day = now.getDate()
    const weekdayNames = ['日', '一', '二', '三', '四', '五', '六']
    const weekday = weekdayNames[now.getDay()]
    
    if (response.solar_term) {
      todayDate.value = `${year}年${month}月${day}日 星期${weekday} • ${response.solar_term}`
    } else {
      todayDate.value = `${year}年${month}月${day}日 星期${weekday}`
    }
    
    // 设置运势数据
    fortuneScore.value = response.fortune_score
    starRating.value = response.star_display
    fortuneDescription.value = response.description
    goodThings.value = response.good_things
    badThings.value = response.bad_things
    luckyColor.value = response.lucky_color
    luckyNumber.value = response.lucky_number
    luckyElement.value = response.lucky_element
    weekdayTip.value = response.weekday_tip
    
  } catch (error) {
    console.error('获取运势失败:', error)
    todayDate.value = '加载失败'
    fortuneDescription.value = '获取运势数据失败，请稍后重试'
  } finally {
    loading.value = false
  }
}

// 获取幸运色的颜色代码
const getLuckyColorHex = (colorName) => {
  const colorMap = {
    '红色': '#ff4757',
    '橙色': '#ffa502',
    '黄色': '#ffd93d',
    '绿色': '#6bcf7f',
    '青色': '#4ecdc4',
    '蓝色': '#667eea',
    '紫色': '#a55eea',
    '粉色': '#fc5c9c',
    '白色': '#ecf0f1',
    '金色': '#f9ca24',
    '银色': '#95afc0',
    '米色': '#f1c40f'
  }
  return colorMap[colorName] || '#667eea'
}

// 组件挂载时加载运势
onMounted(() => {
  loadFortune()
})
</script>

<style scoped>
.fortune-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
  height: 100%;
  overflow-y: auto;
  padding-right: 8px;
}

.loading-state {
  text-align: center;
  padding: 40px;
  font-size: 16px;
  color: #909399;
}

.sidebar-header h4 {
  color: var(--text-primary);
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 6px;
}

.fortune-card {
  padding: 16px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.fortune-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.fortune-card.score {
  background: linear-gradient(135deg, rgba(255, 215, 0, 0.15), rgba(255, 165, 0, 0.15));
}

.fortune-card.almanac {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
}

.fortune-card.lucky {
  background: linear-gradient(135deg, rgba(78, 205, 196, 0.1), rgba(255, 107, 107, 0.1));
}

.fortune-card.tip {
  background: linear-gradient(135deg, rgba(255, 193, 7, 0.1), rgba(255, 152, 0, 0.1));
}

.card-icon {
  font-size: 24px;
  margin-bottom: 8px;
}

.card-content {
  flex: 1;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
}

/* 运势指数样式 */
.score-display {
  text-align: center;
  margin: 12px 0;
}

.stars {
  font-size: 24px;
  margin-bottom: 8px;
}

.score-value {
  font-size: 28px;
  font-weight: 700;
  color: #f39c12;
  margin-bottom: 8px;
}

.fortune-desc {
  font-size: 15px;
  color: #606266;
  text-align: center;
}

/* 黄历宜忌样式 */
.almanac-item {
  margin-bottom: 10px;
  font-size: 14px;
  line-height: 1.8;
}

.almanac-item:last-child {
  margin-bottom: 0;
}

.almanac-label {
  font-weight: 600;
  color: #303133;
}

.almanac-text {
  color: #606266;
}

/* 幸运元素样式 */
.lucky-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.lucky-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 8px;
}

.lucky-label {
  font-size: 14px;
  color: #606266;
}

.lucky-value {
  font-size: 16px;
  font-weight: 600;
  color: #667eea;
}

/* 温馨提示样式 */
.tip-text {
  font-size: 14px;
  color: #606266;
  line-height: 1.8;
}

/* 移动端优化 */
@media (max-width: 576px) {
  .fortune-content {
    gap: 10px;
    padding-right: 4px;
  }
  
  .sidebar-header h4 {
    font-size: 14px;
    margin-bottom: 4px;
  }
  
  .sidebar-header p {
    font-size: 10px;
  }
  
  .fortune-card {
    padding: 10px;
    border-radius: 8px;
  }
  
  .card-icon {
    font-size: 18px;
    margin-bottom: 6px;
  }
  
  .card-title {
    font-size: 13px;
    margin-bottom: 8px;
  }
  
  /* 运势指数 */
  .score-display {
    margin: 8px 0;
  }
  
  .stars {
    font-size: 18px;
    margin-bottom: 4px;
  }
  
  .score-value {
    font-size: 20px;
    margin-bottom: 6px;
  }
  
  .fortune-desc {
    font-size: 11px;
  }
  
  /* 黄历宜忌 */
  .almanac-item {
    margin-bottom: 6px;
    font-size: 11px;
    line-height: 1.6;
  }
  
  /* 幸运元素 */
  .lucky-grid {
    gap: 8px;
  }
  
  .lucky-item {
    padding: 8px;
    border-radius: 6px;
  }
  
  .lucky-label {
    font-size: 11px;
  }
  
  .lucky-value {
    font-size: 13px;
  }
  
  /* 温馨提示 */
  .tip-text {
    font-size: 11px;
    line-height: 1.6;
  }
}
</style>
