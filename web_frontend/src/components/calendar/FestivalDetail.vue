<template>
  <div class="festival-detail">
    <div class="detail-header">
      <button @click="$emit('close')" class="back-btn">
        <i class="bi bi-arrow-left"></i> 返回
      </button>
    </div>

    <div class="detail-content">
      <div class="festival-title">
        <div class="festival-emoji">{{ festival.emoji || '🎊' }}</div>
        <h3>{{ festival.name }}</h3>
      </div>

      <div class="festival-info-card">
        <div class="info-item">
          <div class="info-label">节日类型</div>
          <div class="info-value">{{ getFestivalTypeName(festival.type) }}</div>
        </div>
      </div>

      <div class="festival-description">
        <p>{{ getDefaultDescription(festival.name) }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  festival: {
    type: Object,
    required: true
  }
})

defineEmits(['close'])

const getFestivalTypeName = (type) => {
  const typeMap = {
    'legal': '法定节假日',
    'international': '国际节日',
    'traditional': '传统节日'
  }
  return typeMap[type] || '节日'
}

const getDefaultDescription = (name) => {
  const descriptions = {
    '国庆节': '中华人民共和国国庆节，庆祝新中国成立的重大节日。',
    '光棍节 / 双11购物节': '源于大学生的自嘲节日，后发展为全球最大的网购狂欢节。',
    '中秋节': '中国传统节日，象征团圆，有赏月、吃月饼的习俗。',
    '春节': '中国最重要的传统节日，标志着农历新年的开始。',
    '端午节': '纪念屈原的传统节日，有吃粽子、赛龙舟的习俗。',
    '清明节': '祭祖扫墓的传统节日，也是踏青郊游的好时节。',
    '元宵节': '春节后的第一个重要节日，有赏灯、吃元宵的习俗。',
    '重阳节': '登高望远、赏菊饮酒的传统节日，也是敬老节。',
    '情人节': '西方情人节，表达爱意的浪漫节日。',
    '圣诞节': '西方传统节日，庆祝耶稣诞生。'
  }
  
  return descriptions[name] || `${name}是一个特殊的日子，值得纪念和庆祝。`
}
</script>

<style scoped>
.festival-detail {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.detail-header {
  margin-bottom: 16px;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: transparent;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  color: #667eea;
  cursor: pointer;
  transition: all 0.2s ease;
}

.back-btn:hover {
  background: rgba(102, 126, 234, 0.1);
  border-color: #667eea;
}

.detail-content {
  flex: 1;
  overflow-y: auto;
}

.festival-title {
  text-align: center;
  margin-bottom: 24px;
}

.festival-emoji {
  font-size: 64px;
  margin-bottom: 12px;
}

.festival-title h3 {
  font-size: 24px;
  font-weight: 600;
  color: #4A148C;
  margin: 0;
}

.festival-info-card {
  background: white;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
}

.info-label {
  font-size: 14px;
  color: #6A1B9A;
  font-weight: 500;
}

.info-value {
  font-size: 16px;
  color: #4A148C;
  font-weight: 600;
}

.festival-description {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05), rgba(118, 75, 162, 0.05));
  border-left: 4px solid #667eea;
  border-radius: 8px;
  padding: 16px;
}

.festival-description p {
  font-size: 15px;
  color: #4A148C;
  line-height: 1.8;
  margin: 0;
}

@media (max-width: 768px) {
  .festival-emoji {
    font-size: 48px;
  }
  
  .festival-title h3 {
    font-size: 20px;
  }
  
  .info-item {
    padding: 10px 0;
  }
  
  .info-label,
  .festival-description p {
    font-size: 13px;
  }
  
  .info-value {
    font-size: 14px;
  }
}

@media (max-width: 576px) {
  .festival-emoji {
    font-size: 40px;
    margin-bottom: 8px;
  }
  
  .festival-title h3 {
    font-size: 18px;
  }
  
  .festival-info-card {
    padding: 12px;
  }
  
  .info-label,
  .festival-description p {
    font-size: 12px;
  }
  
  .info-value {
    font-size: 13px;
  }
  
  .festival-description {
    padding: 12px;
  }
}
</style>

