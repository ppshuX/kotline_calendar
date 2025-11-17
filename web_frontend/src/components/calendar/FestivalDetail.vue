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

      <!-- 节日介绍（AI生成或默认） -->
      <div class="section-card intro">
        <div class="section-title">
          <i class="bi bi-book"></i> 节日介绍
        </div>
        <div class="section-content">
          <div v-if="loadingIntro" class="loading-text">AI生成中...</div>
          <div v-else-if="introError" class="error-text">
            <p>加载失败: HTTP 404 Not Found</p>
            <p class="error-hint">但你仍可以在下方向AI提问!</p>
          </div>
          <p v-else>{{ festivalIntro }}</p>
        </div>
      </div>

      <!-- AI问答区域 -->
      <div class="section-card qa">
        <div class="section-title">
          <i class="bi bi-robot"></i> AI助手
        </div>
        
        <!-- 快捷问题 -->
        <div class="quick-questions">
          <button
            v-for="question in quickQuestions"
            :key="question"
            @click="askQuestion(question)"
            class="quick-btn"
            :disabled="loading"
          >
            {{ question }}
          </button>
        </div>
        
        <!-- 聊天记录 -->
        <div class="chat-messages" ref="chatRef">
          <div
            v-for="(msg, index) in chatHistory"
            :key="index"
            :class="['chat-bubble', msg.role]"
          >
            <div class="bubble-content">{{ msg.content }}</div>
          </div>
          <div v-if="loading" class="chat-bubble assistant">
            <div class="bubble-content loading">思考中...</div>
          </div>
        </div>
        
        <!-- 输入框 -->
        <div class="chat-input-area">
          <input
            v-model="userInput"
            @keyup.enter="askQuestion()"
            placeholder="询问节日相关问题..."
            class="chat-input"
            :disabled="loading"
          />
          <button
            @click="askQuestion()"
            :disabled="loading || !userInput.trim()"
            class="send-btn"
          >
            <i class="bi bi-send-fill"></i>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { aiAPI } from '@/api'

const props = defineProps({
  festival: {
    type: Object,
    required: true
  }
})

defineEmits(['close'])

// 状态
const festivalIntro = ref('')
const loadingIntro = ref(false)
const introError = ref(false)
const chatHistory = ref([])
const userInput = ref('')
const loading = ref(false)
const chatRef = ref(null)

// 根据节日生成快捷问题
const quickQuestions = computed(() => {
  const name = props.festival.name
  
  if (name.includes('春节')) {
    return ['春节的传统习俗有哪些？', '为什么要贴春联？', '春节有哪些传统美食？']
  } else if (name.includes('国庆')) {
    return ['国庆节的由来？', '国庆假期有什么活动？', '国庆阅兵多少年一次？']
  } else if (name.includes('中秋')) {
    return ['中秋节为什么吃月饼？', '中秋节的传说故事？', '中秋节有哪些诗词？']
  } else if (name.includes('端午')) {
    return ['端午节为什么吃粽子？', '端午节和屈原的故事？', '端午节赛龙舟的由来？']
  } else if (name.includes('清明')) {
    return ['清明节为什么扫墓？', '清明节有什么习俗？', '清明节的诗词？']
  } else {
    return [
      `${name}的由来？`,
      `${name}有什么传统习俗？`,
      `${name}有特色美食吗？`
    ]
  }
})

// 默认介绍
const getDefaultDescription = (name) => {
  const descriptions = {
    '国庆节': '中华人民共和国国庆节，庆祝新中国成立的重大节日。每年10月1日，全国放假7天，举行盛大庆祝活动。',
    '光棍节 / 双11购物节': '源于大学生的自嘲节日，因日期"11-11"而得名，后发展为全球最大的网购狂欢节。',
    '中秋节': '中国传统节日，象征团圆，有赏月、吃月饼的习俗。农历八月十五，是仅次于春节的重要节日。',
    '春节': '中国最重要的传统节日，标志着农历新年的开始。有贴春联、拜年、放鞭炮、吃饺子等习俗。',
    '端午节': '纪念屈原的传统节日，有吃粽子、赛龙舟的习俗。农历五月初五，已有两千多年历史。',
    '清明节': '祭祖扫墓的传统节日，也是踏青郊游的好时节。既是节气也是节日，有两千多年历史。',
    '元宵节': '春节后的第一个重要节日，有赏灯、吃元宵的习俗。农历正月十五，标志着春节庆祝活动的结束。',
    '重阳节': '登高望远、赏菊饮酒的传统节日，也是敬老节。农历九月初九，寓意长久长寿。',
    '情人节': '西方情人节，2月14日，情侣们互送礼物表达爱意的浪漫节日。',
    '圣诞节': '西方传统节日，12月25日，庆祝耶稣诞生，有圣诞树、礼物、圣诞老人等元素。'
  }
  
  return descriptions[name] || `${name}是一个特殊的日子，值得纪念和庆祝。`
}

// 生成节日介绍（可选：调用AI）
const generateIntro = async () => {
  introError.value = false
  loadingIntro.value = false
  
  try {
    // 先显示默认介绍
    festivalIntro.value = getDefaultDescription(props.festival.name)
    
    // 如果想用AI生成更详细的介绍，取消下面的注释
    /*
    loadingIntro.value = true
    try {
      const systemPrompt = `你是节日知识专家，请简要介绍${props.festival.name}。要求：200字以内，包含历史由来、重要意义。`
      const response = await aiAPI.chat(`请介绍${props.festival.name}`, {
        system_prompt: systemPrompt
      })
      if (response.success) {
        festivalIntro.value = response.reply
      }
    } catch (error) {
      console.error('AI生成介绍失败:', error)
      introError.value = true
    } finally {
      loadingIntro.value = false
    }
    */
  } catch (error) {
    console.error('加载节日介绍失败:', error)
    introError.value = true
    loadingIntro.value = false
  }
}

// 询问问题
const askQuestion = async (question) => {
  const questionText = question || userInput.value.trim()
  
  if (!questionText) {
    ElMessage.warning('请输入问题')
    return
  }
  
  // 添加用户问题
  chatHistory.value.push({
    role: 'user',
    content: questionText
  })
  
  userInput.value = ''
  loading.value = true
  
  await nextTick()
  scrollToBottom()
  
  try {
    // 构建针对节日的提示词
    const systemPrompt = `你是节日知识专家，专门回答关于${props.festival.name}的问题。要求：准确、简洁、使用emoji。`
    
    const response = await aiAPI.chat(questionText, {
      system_prompt: systemPrompt,
      festival_name: props.festival.name
    })
    
    if (response.success) {
      chatHistory.value.push({
        role: 'assistant',
        content: response.reply
      })
    } else {
      chatHistory.value.push({
        role: 'assistant',
        content: '抱歉，我遇到了一些问题。请稍后再试。'
      })
    }
  } catch (error) {
    // AI问答失败，已在UI中显示错误信息
    chatHistory.value.push({
      role: 'assistant',
      content: '网络错误，请检查连接后重试。'
    })
  } finally {
    loading.value = false
    await nextTick()
    scrollToBottom()
  }
}

// 滚动到底部
const scrollToBottom = () => {
  if (chatRef.value) {
    chatRef.value.scrollTop = chatRef.value.scrollHeight
  }
}

// 组件挂载时生成介绍
onMounted(() => {
  generateIntro()
})
</script>

<style scoped>
.festival-detail {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.detail-header {
  margin-bottom: 12px;
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
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.festival-title {
  text-align: center;
  margin-bottom: 8px;
}

.festival-emoji {
  font-size: 56px;
  margin-bottom: 8px;
}

.festival-title h3 {
  font-size: 22px;
  font-weight: 600;
  color: #4A148C;
  margin: 0;
}

.section-card {
  background: white;
  border-radius: 12px;
  padding: 14px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 600;
  color: #4A148C;
  margin-bottom: 12px;
}

.section-title i {
  font-size: 16px;
  color: #667eea;
}

.section-content p {
  font-size: 14px;
  color: #6A1B9A;
  line-height: 1.7;
  margin: 0;
}

.loading-text {
  font-size: 13px;
  color: #999;
  font-style: italic;
}

.error-text {
  font-size: 13px;
  color: #333;
  line-height: 1.6;
}

.error-text p {
  margin: 0;
  margin-bottom: 8px;
}

.error-text p:first-child {
  color: #e74c3c;
  font-weight: 500;
}

.error-hint {
  color: #666 !important;
  font-size: 12px;
  margin-left: 20px;
  position: relative;
}

.error-hint::before {
  content: '💬';
  position: absolute;
  left: -18px;
}

.quick-questions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}

.quick-btn {
  padding: 6px 12px;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 16px;
  font-size: 12px;
  color: #667eea;
  cursor: pointer;
  transition: all 0.2s ease;
}

.quick-btn:hover:not(:disabled) {
  background: rgba(102, 126, 234, 0.1);
  border-color: #667eea;
}

.quick-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.chat-messages {
  max-height: 200px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 12px;
  padding: 8px;
  background: #f8f9fc;
  border-radius: 8px;
}

.chat-bubble {
  display: flex;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(5px); }
  to { opacity: 1; transform: translateY(0); }
}

.chat-bubble.user {
  justify-content: flex-end;
}

.bubble-content {
  max-width: 80%;
  padding: 8px 12px;
  border-radius: 12px;
  font-size: 13px;
  line-height: 1.5;
  word-wrap: break-word;
}

.chat-bubble.user .bubble-content {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border-bottom-right-radius: 4px;
}

.chat-bubble.assistant .bubble-content {
  background: white;
  color: #333;
  border: 1px solid #e0e0e0;
  border-bottom-left-radius: 4px;
}

.bubble-content.loading {
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}

.chat-input-area {
  display: flex;
  gap: 8px;
}

.chat-input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 16px;
  font-size: 13px;
  outline: none;
  transition: border-color 0.2s ease;
}

.chat-input:focus {
  border-color: #667eea;
}

.chat-input:disabled {
  background: #f5f5f5;
  cursor: not-allowed;
}

.send-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border: none;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.send-btn:hover:not(:disabled) {
  transform: scale(1.1);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .festival-emoji {
    font-size: 48px;
  }
  
  .festival-title h3 {
    font-size: 20px;
  }
  
  .section-card {
    padding: 12px;
  }
  
  .section-content p {
    font-size: 13px;
  }
  
  .chat-messages {
    max-height: 180px;
  }
}

@media (max-width: 576px) {
  .festival-emoji {
    font-size: 40px;
    margin-bottom: 6px;
  }
  
  .festival-title h3 {
    font-size: 18px;
  }
  
  .section-card {
    padding: 10px;
  }
  
  .section-title {
    font-size: 14px;
  }
  
  .section-content p {
    font-size: 12px;
  }
  
  .quick-btn {
    font-size: 11px;
    padding: 5px 10px;
  }
  
  .bubble-content {
    font-size: 12px;
    padding: 7px 10px;
  }
  
  .chat-messages {
    max-height: 150px;
  }
  
  .chat-input {
    font-size: 12px;
    padding: 7px 10px;
  }
  
  .send-btn {
    width: 32px;
    height: 32px;
    font-size: 12px;
  }
}
</style>

