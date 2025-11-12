<template>
  <div class="fortune-content">
    <div class="sidebar-header text-center mb-3">
      <h4>🔮 今日运势</h4>
      <p class="text-secondary small mb-0">
        {{ todayDate }}
      </p>
    </div>

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
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

// 预定义数据（和Android端完全一致）
const goodThingsList = [
  "出行", "会友", "开市", "祈福", "求财", "纳财", "交易",
  "立券", "移徙", "嫁娶", "祭祀", "安床", "入宅", "动土",
  "修造", "纳采", "订盟", "理发", "求医", "治病", "沐浴",
  "扫舍", "裁衣", "作灶", "解除", "栽种", "牧养"
]

const badThingsList = [
  "诉讼", "词讼", "动土", "破土", "安葬", "开市", "交易",
  "纳财", "栽种", "嫁娶", "移徙", "入宅", "安床", "作灶",
  "修造", "出行", "祈福", "祭祀", "探病", "针灸", "求医",
  "治病", "裁衣", "解除", "伐木", "捕捉", "畋猎"
]

const luckyColorsList = [
  "红色", "橙色", "黄色", "绿色", "青色", "蓝色",
  "紫色", "粉色", "白色", "金色", "银色", "米色"
]

const elementsList = ["金", "木", "水", "火", "土"]

const fortuneDescriptionsList = [
  "今日运势极佳，万事顺意！",
  "运势平稳，适宜稳扎稳打。",
  "小有波折，需谨慎行事。",
  "运势上扬，把握机会！",
  "诸事顺利，心情愉悦。",
  "运势一般，保持平常心。",
  "运势渐好，积极进取！"
]

// 响应式数据
const todayDate = ref('')
const fortuneScore = ref(0)
const starRating = ref('')
const fortuneDescription = ref('')
const goodThings = ref([])
const badThings = ref([])
const luckyColor = ref('')
const luckyNumber = ref(0)
const luckyElement = ref('')
const weekdayTip = ref('')

// 生成今日运势
const generateFortune = () => {
  const now = new Date()
  const year = now.getFullYear()
  const month = now.getMonth() + 1
  const day = now.getDate()
  const weekday = now.getDay()
  
  const weekdayNames = ['日', '一', '二', '三', '四', '五', '六']
  todayDate.value = `${year}年${month}月${day}日 星期${weekdayNames[weekday]}`
  
  // 基于日期计算种子（确定性）
  const seed = year * 10000 + month * 100 + day
  
  // 简单的伪随机数生成器（基于seed）
  const seededRandom = (function(s) {
    let seed = s
    return function() {
      seed = (seed * 9301 + 49297) % 233280
      return seed / 233280
    }
  })(seed)
  
  // 随机选择宜忌
  const goodCount = 4 + Math.floor(seededRandom() * 4) // 4-7项
  const badCount = 3 + Math.floor(seededRandom() * 3)  // 3-5项
  
  const selectedGood = new Set()
  const selectedBad = new Set()
  
  while (selectedGood.size < goodCount) {
    const idx = Math.floor(seededRandom() * goodThingsList.length)
    selectedGood.add(goodThingsList[idx])
  }
  
  while (selectedBad.size < badCount) {
    const idx = Math.floor(seededRandom() * badThingsList.length)
    const bad = badThingsList[idx]
    if (!selectedGood.has(bad)) {
      selectedBad.add(bad)
    }
  }
  
  goodThings.value = Array.from(selectedGood)
  badThings.value = Array.from(selectedBad)
  
  // 幸运元素
  luckyColor.value = luckyColorsList[Math.floor(seededRandom() * luckyColorsList.length)]
  luckyNumber.value = Math.floor(seededRandom() * 100)
  luckyElement.value = elementsList[Math.floor(seededRandom() * elementsList.length)]
  fortuneScore.value = 60 + Math.floor(seededRandom() * 40) // 60-99分
  fortuneDescription.value = fortuneDescriptionsList[Math.floor(seededRandom() * fortuneDescriptionsList.length)]
  
  // 星级评分
  if (fortuneScore.value >= 90) starRating.value = "⭐⭐⭐⭐⭐"
  else if (fortuneScore.value >= 80) starRating.value = "⭐⭐⭐⭐"
  else if (fortuneScore.value >= 70) starRating.value = "⭐⭐⭐"
  else if (fortuneScore.value >= 60) starRating.value = "⭐⭐"
  else starRating.value = "⭐"
  
  // 温馨提示
  const tips = [
    "周日放松，为新的一周充电！⚡",
    "周一元气满满！新的一周，加油开始！💪",
    "保持节奏，稳步前进！🚀",
    "周三已过半，坚持就是胜利！🌟",
    "临近周末，再努力一把！💫",
    "愉快的周五，周末即将到来！🎉",
    "周末愉快，享受休闲时光！🌈"
  ]
  weekdayTip.value = tips[weekday]
}

// 获取幸运色的实际颜色代码
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

// 组件挂载时生成运势
onMounted(() => {
  generateFortune()
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
  font-size: 32px;
  margin-bottom: 8px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #4A148C;
  margin-bottom: 12px;
}

.card-content {
  text-align: left;
}

.score-display {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.stars {
  font-size: 20px;
}

.score-value {
  font-size: 18px;
  font-weight: 600;
  color: #667eea;
}

.fortune-desc {
  font-size: 14px;
  color: #6A1B9A;
  font-style: italic;
}

.almanac-item {
  margin-bottom: 12px;
  line-height: 1.8;
}

.almanac-item:last-child {
  margin-bottom: 0;
}

.almanac-label {
  font-weight: 600;
  font-size: 14px;
  color: #4A148C;
}

.almanac-text {
  font-size: 14px;
  color: #6A1B9A;
}

.lucky-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 10px;
}

.lucky-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: white;
  border-radius: 8px;
}

.lucky-label {
  font-size: 14px;
  color: #6A1B9A;
}

.lucky-value {
  font-size: 16px;
  font-weight: 600;
  color: #4A148C;
}

.tip-text {
  font-size: 14px;
  color: #6A1B9A;
  line-height: 1.6;
}

@media (max-width: 768px) {
  .fortune-content {
    gap: 12px;
  }
  
  .sidebar-header h4 {
    font-size: 16px;
  }
  
  .sidebar-header p {
    font-size: 11px;
  }
  
  .fortune-card {
    padding: 12px;
  }
  
  .card-icon {
    font-size: 24px;
  }
  
  .card-title {
    font-size: 14px;
  }
}

@media (max-width: 576px) {
  .fortune-content {
    gap: 10px;
  }
  
  .sidebar-header h4 {
    font-size: 15px;
  }
  
  .sidebar-header p {
    font-size: 10px;
  }
  
  .fortune-card {
    padding: 10px;
  }
  
  .card-icon {
    font-size: 20px;
    margin-bottom: 6px;
  }
  
  .card-title {
    font-size: 13px;
    margin-bottom: 8px;
  }
  
  .stars {
    font-size: 16px;
  }
  
  .score-value {
    font-size: 14px;
  }
  
  .fortune-desc {
    font-size: 12px;
  }
  
  .almanac-label,
  .almanac-text,
  .lucky-label,
  .tip-text {
    font-size: 12px;
  }
  
  .lucky-value {
    font-size: 13px;
  }
}
</style>
