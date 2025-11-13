<template>
  <div class="fortune-panel">
    <div class="header">
      <button class="back-btn" @click="$store.commit('updateRouterName', 'calendar')">
        ← 返回
      </button>
      <h2>🔮 今日运势</h2>
    </div>

    <div class="scroll-container">
      <div class="content-card">
        <div v-if="loading" class="loading-state">加载中...</div>

        <template v-else>
          <div class="date">{{ currentDate }}</div>

          <!-- 运势指数 -->
          <div class="fortune-card score-card">
            <div class="card-title">
              <span class="icon">📊</span> 运势指数
            </div>
            <div class="score-content">
              <div class="stars">{{ starDisplay }}</div>
              <div class="score-value">({{ fortuneScore }}分)</div>
              <div class="score-desc">{{ fortuneDescription }}</div>
            </div>
          </div>

          <!-- 黄历宜忌 -->
          <div class="fortune-card almanac-card">
            <div class="card-title">
              <span class="icon">📖</span> 黄历宜忌
            </div>
            <div class="almanac-content">
              <div class="almanac-section good">
                <span class="label">宜：</span>
                <span class="items">{{ goodThings.join('、') }}</span>
              </div>
              <div class="almanac-section bad">
                <span class="label">忌：</span>
                <span class="items">{{ badThings.join('、') }}</span>
              </div>
            </div>
          </div>

          <!-- 幸运元素 -->
          <div class="fortune-card lucky-card">
            <div class="card-title">
              <span class="icon">✨</span> 幸运元素
            </div>
            <div class="lucky-content">
              <div class="lucky-item">
                <span class="lucky-label">幸运颜色：</span>
                <span class="lucky-value">{{ luckyColor }}</span>
              </div>
              <div class="lucky-item">
                <span class="lucky-label">幸运数字：</span>
                <span class="lucky-value">{{ luckyNumber }}</span>
              </div>
              <div class="lucky-item">
                <span class="lucky-label">五行：</span>
                <span class="lucky-value">{{ luckyElement }}</span>
              </div>
            </div>
          </div>

          <!-- 温馨提示 -->
          <div class="fortune-card tip-card">
            <div class="card-title">
              <span class="icon">💡</span> 温馨提示
            </div>
            <div class="tip-content">
              {{ weekdayTip }}
            </div>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'FortunePanel',
  data() {
    return {
      loading: true,
      fortuneScore: 0,
      starDisplay: '',
      fortuneDescription: '',
      goodThings: [],
      badThings: [],
      luckyColor: '',
      luckyNumber: 0,
      luckyElement: '',
      weekdayTip: '',
      solarTerm: null
    }
  },
  computed: {
    currentDate() {
      const date = new Date()
      const year = date.getFullYear()
      const month = date.getMonth() + 1
      const day = date.getDate()
      const weekdays = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六']
      const weekday = weekdays[date.getDay()]
      
      if (this.solarTerm) {
        return `${year}年${month}月${day}日 ${weekday} • ${this.solarTerm}`
      }
      return `${year}年${month}月${day}日 ${weekday}`
    }
  },
  async mounted() {
    await this.loadFortune()
  },
  methods: {
    async loadFortune() {
      this.loading = true
      try {
        const response = await fetch('https://app7626.acapp.acwing.com.cn/api/fortune/today/?city=南昌市')
        const data = await response.json()
        
        // 设置运势数据
        this.fortuneScore = data.fortune_score
        this.starDisplay = data.star_display
        this.fortuneDescription = data.description
        this.goodThings = data.good_things
        this.badThings = data.bad_things
        this.luckyColor = data.lucky_color
        this.luckyNumber = data.lucky_number
        this.luckyElement = data.lucky_element
        this.weekdayTip = data.weekday_tip
        this.solarTerm = data.solar_term
        
      } catch (error) {
        console.error('获取运势失败:', error)
        this.fortuneDescription = '获取运势数据失败，请稍后重试'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.fortune-panel {
  display: flex;
  flex-direction: column;
  height: 100vh;
  max-height: 100vh;
  background: #f5f7fa;
  overflow: hidden;
  position: relative;
}

.header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
  flex-shrink: 0;
}

.scroll-container {
  flex: 1;
  overflow-y: auto !important;
  overflow-x: hidden;
  padding: 8px;
  -webkit-overflow-scrolling: touch;
  min-height: 0;
  max-height: 100%;
  position: relative;
}

.content-card {
  max-width: 600px;
  margin: 0 auto;
  background: white;
  border-radius: 8px;
  padding: 8px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06);
}

.loading-state {
  text-align: center;
  padding: 60px 20px;
  font-size: 16px;
  color: #909399;
}

.back-btn {
  padding: 4px 8px;
  background: white;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  cursor: pointer;
  font-size: 11px;
  transition: all 0.3s;
}

.back-btn:hover {
  background: #ecf5ff;
  border-color: #409eff;
  color: #409eff;
}

h2 {
  font-size: 14px;
  color: #303133;
  margin: 0;
}

.date {
  text-align: center;
  font-size: 10px;
  color: #606266;
  margin-bottom: 6px;
  font-weight: 500;
}

.fortune-card {
  background: white;
  border-radius: 6px;
  padding: 8px;
  margin-bottom: 6px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: all 0.3s;
}

.fortune-card:last-child {
  margin-bottom: 0;
}

.fortune-card:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
}

.card-title {
  font-size: 11px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 5px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.icon {
  font-size: 12px;
}

/* 运势指数卡片 */
.score-card {
  border-left: 2px solid #fbbf24;
}

.score-content {
  text-align: center;
}

.stars {
  font-size: 14px;
  margin-bottom: 2px;
}

.score-value {
  font-size: 14px;
  font-weight: 700;
  color: #fbbf24;
  margin-bottom: 2px;
}

.score-desc {
  font-size: 10px;
  color: #606266;
  font-weight: 500;
}

/* 黄历卡片 */
.almanac-card {
  border-left: 2px solid #667eea;
}

.almanac-section {
  margin-bottom: 4px;
  font-size: 10px;
  line-height: 1.4;
  color: #606266;
}

.almanac-section:last-child {
  margin-bottom: 0;
}

.label {
  font-weight: 600;
  color: #303133;
}

.items {
  color: #606266;
}

/* 幸运元素卡片 */
.lucky-card {
  border-left: 2px solid #10b981;
}

.lucky-content {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.lucky-item {
  font-size: 10px;
  color: #606266;
}

.lucky-label {
  font-weight: 600;
  color: #303133;
}

.lucky-value {
  color: #667eea;
  font-weight: 500;
}

/* 提示卡片 */
.tip-card {
  border-left: 2px solid #f59e0b;
}

.tip-content {
  font-size: 10px;
  color: #606266;
  line-height: 1.4;
}
</style>
