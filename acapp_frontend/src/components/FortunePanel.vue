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
        <div class="date">{{ currentDate }}</div>

        <!-- 运势指数 -->
        <div class="fortune-card score-card">
        <div class="card-title">
          <span class="icon">📊</span> 运势指数
        </div>
        <div class="score-content">
          <div class="stars">{{ getStars() }}</div>
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
            <span class="lucky-label">幸运方位：</span>
            <span class="lucky-value">{{ luckyDirection }}</span>
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
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'FortunePanel',
  data() {
    return {
      fortuneScore: 0,
      fortuneDescription: '',
      goodThings: [],
      badThings: [],
      luckyColor: '',
      luckyNumber: '',
      luckyDirection: '',
      weekdayTip: '',
      weatherData: null,
      // 二十四节气数据（2025年）
      solarTerms: {
        '01-05': { name: '小寒', desc: '天气寒冷，宜养生保暖', boost: ['读书', '沐浴', '求医'], reduce: ['出行', '动土'] },
        '01-20': { name: '大寒', desc: '一年中最冷的时节', boost: ['祭祀', '祈福', '修造'], reduce: ['移徙', '嫁娶'] },
        '02-03': { name: '立春', desc: '春季开始，万物复苏', boost: ['开市', '求财', '纳财', '会友'], reduce: ['安葬', '破土'] },
        '02-18': { name: '雨水', desc: '降雨增多，气温回升', boost: ['栽种', '祈福', '开市'], reduce: ['动土', '修造'] },
        '03-05': { name: '惊蛰', desc: '春雷惊醒蛰伏', boost: ['出行', '交易', '求财', '会友'], reduce: ['安床', '移徙'] },
        '03-20': { name: '春分', desc: '昼夜平分，春意盎然', boost: ['嫁娶', '纳采', '祭祀'], reduce: ['诉讼', '词讼'] },
        '04-04': { name: '清明', desc: '天清地明，祭祖扫墓', boost: ['祭祀', '扫舍', '修墓'], reduce: ['嫁娶', '开市'] },
        '04-20': { name: '谷雨', desc: '雨生百谷，播种佳时', boost: ['栽种', '开市', '纳财'], reduce: ['移徙', '入宅'] },
        '05-05': { name: '立夏', desc: '夏季开始，气温升高', boost: ['出行', '会友', '交易'], reduce: ['动土', '破土'] },
        '05-21': { name: '小满', desc: '麦类作物籽粒饱满', boost: ['纳财', '开市', '求财'], reduce: ['诉讼', '安葬'] },
        '06-05': { name: '芒种', desc: '有芒作物成熟', boost: ['栽种', '纳财', '开市'], reduce: ['嫁娶', '移徙'] },
        '06-21': { name: '夏至', desc: '白昼最长，阳气最盛', boost: ['祈福', '求财', '交易'], reduce: ['词讼', '安葬'] },
        '07-07': { name: '小暑', desc: '天气炎热，注意防暑', boost: ['沐浴', '求医', '治病'], reduce: ['嫁娶', '移徙', '出行'] },
        '07-22': { name: '大暑', desc: '一年中最热的时节', boost: ['沐浴', '扫舍', '解除'], reduce: ['出行', '开市', '动土'] },
        '08-07': { name: '立秋', desc: '秋季开始，暑去凉来', boost: ['开市', '求财', '交易'], reduce: ['嫁娶', '移徙'] },
        '08-23': { name: '处暑', desc: '炎热结束，秋高气爽', boost: ['出行', '会友', '祭祀'], reduce: ['安葬', '破土'] },
        '09-07': { name: '白露', desc: '天气转凉，露水增多', boost: ['求医', '治病', '沐浴'], reduce: ['嫁娶', '移徙'] },
        '09-23': { name: '秋分', desc: '昼夜平分，丰收时节', boost: ['纳财', '开市', '祭祀'], reduce: ['诉讼', '词讼'] },
        '10-08': { name: '寒露', desc: '露水将凝，气温下降', boost: ['祈福', '祭祀', '求医'], reduce: ['嫁娶', '开市'] },
        '10-23': { name: '霜降', desc: '天气渐冷，初霜出现', boost: ['纳财', '开市', '修造'], reduce: ['移徙', '出行'] },
        '11-07': { name: '立冬', desc: '冬季开始，万物收藏', boost: ['祭祀', '修造', '纳财'], reduce: ['嫁娶', '移徙', '出行'] },
        '11-22': { name: '小雪', desc: '开始降雪，气温降低', boost: ['祭祀', '祈福', '修造'], reduce: ['嫁娶', '出行'] },
        '12-07': { name: '大雪', desc: '降雪增多，严寒将至', boost: ['修造', '祭祀', '沐浴'], reduce: ['嫁娶', '移徙', '出行'] },
        '12-21': { name: '冬至', desc: '阴极阳生，白昼最短', boost: ['祭祀', '祈福', '沐浴'], reduce: ['嫁娶', '移徙'] }
      }
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
      
      // 检查是否是节气
      const monthDay = `${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`
      const solarTerm = this.solarTerms[monthDay]
      
      if (solarTerm) {
        return `${year}年${month}月${day}日 ${weekday} • ${solarTerm.name}`
      }
      return `${year}年${month}月${day}日 ${weekday}`
    }
  },
  async mounted() {
    await this.loadWeatherForFortune()
    this.generateFortune()
  },
  methods: {
    async loadWeatherForFortune() {
      try {
        const response = await fetch('https://app7626.acapp.acwing.com.cn/api/weather/?location=南昌市')
        const data = await response.json()
        if (data.success) {
          this.weatherData = data.data
        }
      } catch (error) {
        console.log('获取天气失败，使用默认运势')
      }
    },
    generateFortune() {
      const date = new Date()
      const year = date.getFullYear()
      const month = date.getMonth() + 1
      const day = date.getDate()
      const weekday = date.getDay()
      
      const seed = year * 10000 + month * 100 + day
      
      // 伪随机数生成器（确定性）
      const seededRandom = (function(s) {
        let seed = s
        return function() {
          seed = (seed * 9301 + 49297) % 233280
          return seed / 233280
        }
      })(seed)
      
      // 检查节气
      const monthDay = `${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`
      const solarTerm = this.solarTerms[monthDay]
      
      // 基础运势分数
      let baseScore = 60 + Math.floor(seededRandom() * 40)
      
      // 宜忌列表
      const goodThingsList = ['出行', '会友', '开市', '祈福', '求财', '纳财', '交易', '立券', '移徙', '嫁娶', '祭祀', '安床', '入宅', '动土', '修造', '纳采', '订盟', '理发', '求医', '治病', '沐浴', '扫舍', '裁衣', '作灶', '解除', '栽种', '牧养']
      const badThingsList = ['诉讼', '词讼', '动土', '破土', '安葬', '开市', '交易', '纳财', '栽种', '嫁娶', '移徙', '入宅', '安床', '作灶', '修造', '出行', '祈福', '祭祀', '探病', '针灸', '求医', '治病', '裁衣', '解除', '伐木', '捕捉', '畋猎']
      
      let baseGoodThings = [...goodThingsList]
      let baseBadThings = [...badThingsList]
      
      // 如果是节气，调整宜忌
      if (solarTerm) {
        baseGoodThings = [...solarTerm.boost, ...baseGoodThings.filter(item => !solarTerm.boost.includes(item))]
        baseBadThings = [...solarTerm.reduce, ...baseBadThings.filter(item => !solarTerm.reduce.includes(item))]
      }
      
      // 根据天气调整宜忌
      if (this.weatherData) {
        const weather = this.weatherData.weather
        const temp = parseInt(this.weatherData.temperature)
        
        if (weather.includes('晴')) {
          baseGoodThings = ['出行', '会友', '祈福', '求财', ...baseGoodThings.filter(item => !['出行', '会友', '祈福', '求财'].includes(item))]
        } else if (weather.includes('雨')) {
          baseGoodThings = ['读书', '沐浴', '扫舍', '修造', ...baseGoodThings.filter(item => !['读书', '沐浴', '扫舍', '修造'].includes(item))]
          baseBadThings = ['出行', '移徙', '嫁娶', ...baseBadThings.filter(item => !['出行', '移徙', '嫁娶'].includes(item))]
        } else if (weather.includes('雪')) {
          baseGoodThings = ['祭祀', '祈福', '沐浴', ...baseGoodThings.filter(item => !['祭祀', '祈福', '沐浴'].includes(item))]
          baseBadThings = ['出行', '嫁娶', '移徙', '开市', ...baseBadThings.filter(item => !['出行', '嫁娶', '移徙', '开市'].includes(item))]
        }
        
        if (temp > 30) {
          baseBadThings = ['出行', '开市', '移徙', ...baseBadThings.filter(item => !['出行', '开市', '移徙'].includes(item))]
        } else if (temp < 5) {
          baseBadThings = ['出行', '嫁娶', '移徙', ...baseBadThings.filter(item => !['出行', '嫁娶', '移徙'].includes(item))]
        }
      }
      
      // 随机选择宜忌（从调整后的列表中选择）
      const goodCount = 4 + Math.floor(seededRandom() * 4) // 4-7项
      const badCount = 3 + Math.floor(seededRandom() * 3)  // 3-5项
      
      const selectedGood = new Set()
      const selectedBad = new Set()
      
      // 选择宜事（优先从前面选择）
      for (let i = 0; i < goodCount && selectedGood.size < goodCount; i++) {
        if (i < baseGoodThings.length) {
          selectedGood.add(baseGoodThings[i])
        }
      }
      while (selectedGood.size < goodCount && baseGoodThings.length > 0) {
        const idx = Math.floor(seededRandom() * baseGoodThings.length)
        selectedGood.add(baseGoodThings[idx])
      }
      
      // 选择忌事（优先从前面选择，且避免与宜事重复）
      for (let i = 0; i < badCount && selectedBad.size < badCount; i++) {
        if (i < baseBadThings.length && !selectedGood.has(baseBadThings[i])) {
          selectedBad.add(baseBadThings[i])
        }
      }
      while (selectedBad.size < badCount && baseBadThings.length > 0) {
        const idx = Math.floor(seededRandom() * baseBadThings.length)
        const bad = baseBadThings[idx]
        if (!selectedGood.has(bad)) {
          selectedBad.add(bad)
        }
      }
      
      this.goodThings = Array.from(selectedGood)
      this.badThings = Array.from(selectedBad)

      // 幸运元素
      const colors = ['红色', '橙色', '黄色', '绿色', '青色', '蓝色', '紫色', '粉色', '白色', '金色', '银色', '米色']
      this.luckyColor = colors[Math.floor(seededRandom() * colors.length)]
      this.luckyNumber = Math.floor(seededRandom() * 100)
      const directions = ['东方', '南方', '西方', '北方', '东南', '东北', '西南', '西北']
      this.luckyDirection = directions[Math.floor(seededRandom() * directions.length)]
      
      // 根据天气调整分数
      if (this.weatherData) {
        const weather = this.weatherData.weather
        const temp = parseInt(this.weatherData.temperature)
        
        if (weather.includes('晴')) baseScore += 5
        else if (weather.includes('雨') || weather.includes('雪')) baseScore -= 3
        
        if (temp >= 15 && temp <= 25) baseScore += 3
        else if (temp > 35 || temp < 0) baseScore -= 5
      }
      
      // 确保分数在60-99范围内
      this.fortuneScore = Math.max(60, Math.min(99, baseScore))
      
      // 运势描述
      if (solarTerm) {
        this.fortuneDescription = `今日${solarTerm.name}，${solarTerm.desc}。`
      } else if (this.weatherData) {
        const weather = this.weatherData.weather
        if (weather.includes('晴')) {
          this.fortuneDescription = '天气晴朗，运势上扬，把握机会！'
        } else if (weather.includes('雨')) {
          this.fortuneDescription = '雨天宜静养，适合思考和规划。'
        } else if (weather.includes('雪')) {
          this.fortuneDescription = '雪天出行需谨慎，适合室内活动。'
        } else {
          this.fortuneDescription = '诸事顺利，心情愉悦。'
        }
      } else {
        this.fortuneDescription = '诸事顺利，心情愉悦。'
      }

      // 温馨提示（结合天气）
      let tip = ''
      
      if (this.weatherData) {
        const weather = this.weatherData.weather
        const temp = parseInt(this.weatherData.temperature)
        
        if (weather.includes('雨')) {
          tip = '今日有雨，出门记得带伞哦！☔ '
        } else if (weather.includes('雪')) {
          tip = '今日下雪，注意保暖防滑！❄️ '
        } else if (weather.includes('晴')) {
          tip = '今日晴朗，适合户外活动！☀️ '
        } else if (weather.includes('雾') || weather.includes('霾')) {
          tip = '今日有雾霾，减少外出，注意健康！😷 '
        }
        
        if (temp > 30) {
          tip += '高温天气，多补充水分！🥤'
        } else if (temp < 5) {
          tip += '寒冷天气，注意保暖！🧣'
        } else if (temp >= 15 && temp <= 25) {
          tip += '温度适宜，心情愉悦！😊'
        }
      }
      
      if (!tip) {
        const tips = [
          '周日放松，为新的一周充电！⚡',
          '周一元气满满！新的一周，加油开始！💪',
          '保持节奏，稳步前进！🚀',
          '周三已过半，坚持就是胜利！🌟',
          '临近周末，再努力一把！💫',
          '愉快的周五，周末即将到来！🎉',
          '周末愉快，享受休闲时光！🌈'
        ]
        tip = tips[weekday]
      }
      
      if (solarTerm) {
        tip = `${solarTerm.name}：${solarTerm.desc}。${tip}`
      }
      
      this.weekdayTip = tip
    },
    getStars() {
      if (this.fortuneScore >= 90) return '⭐⭐⭐⭐⭐'
      if (this.fortuneScore >= 80) return '⭐⭐⭐⭐'
      if (this.fortuneScore >= 70) return '⭐⭐⭐'
      if (this.fortuneScore >= 60) return '⭐⭐'
      return '⭐'
    }
  }
}
</script>

<style scoped>
.fortune-panel {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f5f7fa;
  overflow: hidden;
}

.header {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 20px;
  background: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
  flex-shrink: 0;
}

.scroll-container {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 20px;
}

.content-card {
  max-width: 600px;
  margin: 0 auto;
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.back-btn {
  padding: 8px 16px;
  background: white;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.back-btn:hover {
  background: #ecf5ff;
  border-color: #409eff;
  color: #409eff;
}

h2 {
  font-size: 22px;
  color: #303133;
  margin: 0;
}

.date {
  text-align: center;
  font-size: 16px;
  color: #606266;
  margin-bottom: 20px;
  font-weight: 500;
}

.fortune-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 15px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: all 0.3s;
}

.fortune-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
  transform: translateY(-2px);
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.icon {
  font-size: 20px;
}

/* 运势指数卡片 - 统一配色 */
.score-card {
  background: white;
  border-left: 4px solid #fbbf24;
}

.score-content {
  text-align: center;
}

.stars {
  font-size: 24px;
  margin-bottom: 10px;
}

.score-value {
  font-size: 28px;
  font-weight: 700;
  color: #fbbf24;
  margin-bottom: 10px;
}

.score-desc {
  font-size: 16px;
  color: #606266;
  font-weight: 500;
}

/* 黄历卡片 - 统一配色 */
.almanac-card {
  background: white;
  border-left: 4px solid #667eea;
}

.almanac-card .card-title {
  color: #303133;
}

.almanac-section {
  margin-bottom: 12px;
  font-size: 15px;
  line-height: 1.8;
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

/* 幸运元素卡片 - 统一配色 */
.lucky-card {
  background: white;
  border-left: 4px solid #10b981;
}

.lucky-card .card-title {
  color: #303133;
}

.lucky-item {
  margin-bottom: 10px;
  font-size: 15px;
  color: #606266;
}

.lucky-item:last-child {
  margin-bottom: 0;
}

.lucky-label {
  font-weight: 600;
  color: #303133;
}

.lucky-value {
  color: #667eea;
  font-weight: 500;
}

/* 提示卡片 - 统一配色 */
.tip-card {
  background: white;
  border-left: 4px solid #f59e0b;
}

.tip-card .card-title {
  color: #303133;
}

.tip-content {
  font-size: 15px;
  color: #606266;
  line-height: 1.8;
}
</style>

