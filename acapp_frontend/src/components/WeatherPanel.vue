<template>
  <div class="weather-panel">
    <div class="header">
      <button class="back-btn" @click="$store.commit('updateRouterName', 'calendar')">
        ← 返回
      </button>
      <h2>🌤️ 今日天气</h2>
    </div>

    <div class="content">
      <div v-if="loading" class="loading">加载中...</div>
      <div v-else-if="error" class="error">{{ error }}</div>
      <div v-else class="weather-info">
        <!-- 当前天气 -->
        <div class="current-weather">
          <div class="weather-icon-large">{{ getWeatherIcon(weather.weather) }}</div>
          <div class="weather-main">
            <div class="temp-row">
              <span class="temp-large">{{ weather.temperature }}°</span>
              <span class="weather-desc">{{ weather.weather }}</span>
            </div>
            <div class="city-name">{{ city }}</div>
          </div>
        </div>

        <!-- 详细信息 -->
        <div class="weather-details">
          <div class="detail-item">
            <span class="detail-icon">🌡️</span>
            <span class="detail-label">体感温度</span>
            <span class="detail-value">{{ weather.feelsLike }}°C</span>
          </div>
          <div class="detail-item">
            <span class="detail-icon">💧</span>
            <span class="detail-label">湿度</span>
            <span class="detail-value">{{ weather.humidity }}%</span>
          </div>
          <div class="detail-item">
            <span class="detail-icon">💨</span>
            <span class="detail-label">风力</span>
            <span class="detail-value">{{ weather.windDirection }} {{ weather.windPower }}级</span>
          </div>
        </div>

        <!-- 城市搜索 -->
        <div class="city-search">
          <input
            v-model="searchCity"
            @keyup.enter="searchCityWeather"
            placeholder="输入城市名搜索（如：杭州市）"
            class="search-input"
          />
          <button @click="searchCityWeather" class="search-btn">
            🔍 搜索
          </button>
        </div>

        <!-- 切换城市 -->
        <div class="city-selector">
          <div class="selector-title">热门城市</div>
          <button class="city-btn" @click="changeCity('北京市')">北京</button>
          <button class="city-btn" @click="changeCity('上海市')">上海</button>
          <button class="city-btn" @click="changeCity('广州市')">广州</button>
          <button class="city-btn" @click="changeCity('深圳市')">深圳</button>
          <button class="city-btn" @click="changeCity('成都市')">成都</button>
          <button class="city-btn" @click="changeCity('杭州市')">杭州</button>
          <button class="city-btn" @click="changeCity('南昌市')">南昌</button>
          <button class="city-btn" @click="changeCity('武汉市')">武汉</button>
          <button class="city-btn" @click="changeCity('西安市')">西安</button>
          <button class="city-btn" @click="changeCity('重庆市')">重庆</button>
          <button class="city-btn" @click="changeCity('天津市')">天津</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'WeatherPanel',
  data() {
    return {
      city: '南昌市',
      searchCity: '',
      weather: {},
      loading: false,
      error: null
    }
  },
  mounted() {
    this.loadWeather()
  },
  methods: {
    async loadWeather() {
      this.loading = true
      this.error = null

      try {
        const response = await fetch(`https://app7626.acapp.acwing.com.cn/api/weather/?location=${encodeURIComponent(this.city)}`)
        
        if (!response.ok) {
          throw new Error('获取天气失败')
        }

        const result = await response.json()
        // API返回格式是 {success: true, data: {...}}
        if (result.success && result.data) {
          const data = result.data
          // 映射字段名：API返回windDir/windScale，组件使用windDirection/windPower
          this.weather = {
            temperature: data.temperature,
            weather: data.weather,
            feelsLike: data.feelsLike,
            humidity: data.humidity,
            windDirection: data.windDir || data.windDirection,
            windPower: data.windScale || data.windPower,
            location: data.location
          }
        } else {
          throw new Error(result.error || '天气数据格式错误')
        }
      } catch (err) {
        console.error('天气加载错误:', err)
        this.error = '获取天气信息失败，请稍后重试'
      } finally {
        this.loading = false
      }
    },
    changeCity(cityName) {
      this.city = cityName
      this.searchCity = ''
      this.loadWeather()
    },
    searchCityWeather() {
      if (!this.searchCity.trim()) return
      
      let cityName = this.searchCity.trim()
      // 如果输入的城市名不包含"市"，自动添加
      if (!cityName.endsWith('市') && !cityName.endsWith('省') && !cityName.endsWith('县')) {
        cityName = cityName + '市'
      }
      
      this.city = cityName
      this.loadWeather()
    },
    getWeatherIcon(weather) {
      if (!weather) return '☁️'
      const w = weather.toLowerCase()
      if (w.includes('晴')) return '☀️'
      if (w.includes('云')) return '☁️'
      if (w.includes('雨')) return '🌧️'
      if (w.includes('雪')) return '❄️'
      if (w.includes('雾') || w.includes('霾')) return '🌫️'
      if (w.includes('风')) return '💨'
      return '🌤️'
    }
  }
}
</script>

<style scoped>
.weather-panel {
  padding: 20px;
  background: #f5f7fa;
  height: 100vh;
  overflow-y: auto;
  overflow-x: hidden;
}

.content {
  max-width: 600px;
  margin: 0 auto;
}

.header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
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
  font-size: 18px;
  color: #303133;
  margin: 0;
}

.loading, .error {
  text-align: center;
  padding: 20px;
  font-size: 14px;
  color: #606266;
}

.error {
  background: rgba(255, 0, 0, 0.1);
  border-radius: 8px;
}

/* 当前天气 */
.current-weather {
  background: white;
  border-radius: 12px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 12px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
  border-left: 3px solid #3b82f6;
}

.weather-icon-large {
  font-size: 48px;
  flex-shrink: 0;
}

.weather-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.temp-row {
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.temp-large {
  font-size: 40px;
  font-weight: 700;
  color: #3b82f6;
  line-height: 1;
}

.weather-desc {
  font-size: 16px;
  color: #606266;
  font-weight: 500;
}

.city-name {
  font-size: 14px;
  font-weight: 500;
  color: #909399;
}

/* 详细信息 */
.weather-details {
  background: white;
  border-radius: 10px;
  padding: 12px;
  margin-bottom: 12px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
  border-left: 3px solid #10b981;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  margin-bottom: 6px;
  background: #f5f7fa;
  border-radius: 8px;
}

.detail-item:last-child {
  margin-bottom: 0;
}

.detail-icon {
  font-size: 18px;
}

.detail-label {
  flex: 1;
  font-size: 12px;
  color: #606266;
}

.detail-value {
  font-size: 13px;
  font-weight: 600;
  color: #303133;
}

/* 城市搜索 */
.city-search {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.search-input {
  flex: 1;
  padding: 8px 12px;
  border: 1.5px solid #dcdfe6;
  border-radius: 8px;
  font-size: 12px;
  outline: none;
  transition: all 0.3s;
}

.search-input:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.search-btn {
  padding: 8px 16px;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
  transition: all 0.3s;
  white-space: nowrap;
}

.search-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}

/* 城市选择器 */
.city-selector {
  background: white;
  border-radius: 10px;
  padding: 10px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
}

.selector-title {
  font-size: 11px;
  font-weight: 600;
  color: #606266;
  margin-bottom: 8px;
  text-align: center;
}

.city-btn {
  padding: 5px 10px;
  margin: 3px;
  background: #f5f7fa;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  cursor: pointer;
  font-size: 11px;
  font-weight: 500;
  color: #606266;
  transition: all 0.3s;
}

.city-btn:hover {
  background: #ecf5ff;
  border-color: #3b82f6;
  color: #3b82f6;
  transform: scale(1.05);
}
</style>

