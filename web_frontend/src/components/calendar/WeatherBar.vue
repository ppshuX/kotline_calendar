<template>
  <div class="weather-bar" :class="{ loading: loading, error: !!error }">
    <!-- 加载中 -->
    <div v-if="loading" class="weather-bar-content">
      <div class="weather-icon">🌤️</div>
      <span class="loading-text">加载天气中...</span>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="weather-bar-content">
      <div class="weather-icon">⚠️</div>
      <span class="error-text">{{ error }}</span>
      <el-button type="text" size="small" @click="loadWeather" class="retry-btn">
        <i class="bi bi-arrow-clockwise"></i> 重试
      </el-button>
    </div>

    <!-- 天气信息 -->
    <div v-else-if="weatherData" class="weather-bar-content" @click="showCityDialog = true">
      <div class="weather-main">
        <div class="weather-icon">{{ getWeatherIcon(weatherData.weather) }}</div>
        <div class="weather-info">
          <div class="weather-primary">
            <span class="temperature">{{ weatherData.temperature }}°C</span>
            <span class="weather-desc">{{ weatherData.weather }}</span>
          </div>
          <div class="weather-secondary">
            <span v-if="weatherData.windDir !== '--'">{{ weatherData.windDir }}风</span>
            <span v-if="weatherData.windScale !== '--'">{{ weatherData.windScale }}级</span>
            <span v-if="weatherData.humidity !== '--'">湿度{{ weatherData.humidity }}%</span>
          </div>
        </div>
      </div>
      <div class="weather-location">
        <i class="bi bi-geo-alt"></i>
        <span>{{ weatherData.location }}</span>
        <i class="bi bi-chevron-down"></i>
      </div>
    </div>

    <!-- 城市选择对话框 -->
    <el-dialog
      v-model="showCityDialog"
      title="选择城市"
      width="90%"
      :style="{ maxWidth: '500px' }"
    >
      <div class="city-grid">
        <el-button
          v-for="cityOption in popularCities"
          :key="cityOption"
          :type="city === cityOption ? 'primary' : 'default'"
          @click="changeCity(cityOption)"
          class="city-btn"
        >
          {{ cityOption }}
        </el-button>
      </div>
      
      <div class="custom-city mt-3">
        <el-input
          v-model="customCity"
          placeholder="输入其他城市名称"
          @keyup.enter="changeCity(customCity)"
        >
          <template #append>
            <el-button @click="changeCity(customCity)">确定</el-button>
          </template>
        </el-input>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { weatherAPI } from '@/api'

// 数据
const weatherData = ref(null)
const loading = ref(false)
const error = ref(null)
const city = ref('北京')
const customCity = ref('')
const showCityDialog = ref(false)

// 热门城市列表
const popularCities = [
  '北京', '上海', '广州', '深圳', 
  '杭州', '南京', '成都', '西安',
  '武汉', '重庆', '天津', '苏州'
]

// 加载天气
const loadWeather = async () => {
  loading.value = true
  error.value = null
  
  try {
    const response = await weatherAPI.getWeather(city.value)
    
    if (response.success) {
      weatherData.value = response.data
      // 保存到localStorage
      localStorage.setItem('weather_city', city.value)
    } else {
      error.value = response.error || '获取失败'
    }
  } catch (err) {
    console.error('获取天气失败:', err)
    error.value = '网络错误'
  } finally {
    loading.value = false
  }
}

// 切换城市
const changeCity = (newCity) => {
  if (!newCity || !newCity.trim()) {
    ElMessage.warning('请输入城市名称')
    return
  }
  
  city.value = newCity.trim()
  showCityDialog.value = false
  customCity.value = ''
  loadWeather()
  ElMessage.success('已切换到 ' + newCity)
}

// 根据天气状况返回图标
const getWeatherIcon = (weather) => {
  const iconMap = {
    '晴': '☀️',
    '多云': '⛅',
    '阴': '☁️',
    '小雨': '🌦️',
    '中雨': '🌧️',
    '大雨': '⛈️',
    '雷暴': '⚡',
    '雪': '❄️',
    '雾': '🌫️',
    '霾': '😷',
    '沙尘暴': '🌪️'
  }
  
  for (const [key, icon] of Object.entries(iconMap)) {
    if (weather && weather.includes(key)) {
      return icon
    }
  }
  
  return '🌤️'
}

// 组件挂载时加载天气
onMounted(() => {
  // 从localStorage恢复上次选择的城市
  const savedCity = localStorage.getItem('weather_city')
  if (savedCity) {
    city.value = savedCity
  }
  
  loadWeather()
})
</script>

<style scoped>
.weather-bar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  padding: 16px 24px;
  margin-bottom: 20px;
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
  transition: all 0.3s ease;
}

.weather-bar:hover {
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
  transform: translateY(-2px);
}

.weather-bar.loading,
.weather-bar.error {
  background: linear-gradient(135deg, #a8b3ff 0%, #c5a8ff 100%);
}

.weather-bar-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: white;
  cursor: pointer;
}

.weather-main {
  display: flex;
  align-items: center;
  gap: 16px;
  flex: 1;
}

.weather-icon {
  font-size: 48px;
  line-height: 1;
}

.weather-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.weather-primary {
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.temperature {
  font-size: 32px;
  font-weight: 700;
  line-height: 1;
}

.weather-desc {
  font-size: 18px;
  font-weight: 500;
}

.weather-secondary {
  display: flex;
  gap: 12px;
  font-size: 14px;
  opacity: 0.9;
}

.weather-location {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 16px;
  font-weight: 500;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  transition: all 0.2s ease;
}

.weather-location:hover {
  background: rgba(255, 255, 255, 0.3);
}

.loading-text,
.error-text {
  font-size: 16px;
  margin-left: 12px;
}

.retry-btn {
  color: white !important;
  margin-left: 12px;
}

.city-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}

.city-btn {
  width: 100%;
}

@media (max-width: 768px) {
  .weather-bar {
    padding: 10px 12px;
    margin-bottom: 12px;
    border-radius: 12px;
  }

  .weather-bar-content {
    flex-direction: row;
    gap: 8px;
    align-items: center;
  }

  .weather-main {
    gap: 8px;
    flex: 1;
  }

  .weather-icon {
    font-size: 32px;
  }

  .temperature {
    font-size: 22px;
  }

  .weather-desc {
    font-size: 14px;
  }

  .weather-secondary {
    font-size: 11px;
    gap: 6px;
  }

  .weather-location {
    font-size: 12px;
    padding: 4px 10px;
  }

  .city-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 576px) {
  .weather-bar {
    padding: 8px 10px;
  }

  .weather-icon {
    font-size: 28px;
  }

  .temperature {
    font-size: 20px;
  }

  .weather-desc {
    font-size: 13px;
  }

  .weather-secondary {
    font-size: 10px;
    gap: 4px;
  }

  .weather-location {
    font-size: 11px;
    padding: 3px 8px;
  }
}
</style>

