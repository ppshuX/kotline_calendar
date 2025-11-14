<template>
  <div class="ai-content">
    <div class="sidebar-header text-center mb-3">
      <h4>🤖 AI助手</h4>
      <p class="text-secondary small mb-0">
        智能问答助手（查询日程信息）
      </p>
    </div>

    <!-- 对话历史 -->
    <div class="chat-history" ref="chatHistoryRef">
      <div
        v-for="(msg, index) in chatHistory"
        :key="index"
        :class="['chat-message', msg.role]"
      >
        <div class="message-avatar">
          {{ msg.role === 'user' ? '👤' : '🤖' }}
        </div>
        <div class="message-content">
          <div class="message-text">{{ msg.content }}</div>
          <div class="message-time">{{ msg.time }}</div>
        </div>
      </div>
      
      <!-- 加载中 -->
      <div v-if="loading" class="chat-message assistant">
        <div class="message-avatar">🤖</div>
        <div class="message-content">
          <div class="message-text loading-dots">思考中...</div>
        </div>
      </div>
      
      <!-- 空状态 -->
      <div v-if="chatHistory.length === 0 && !loading" class="empty-chat">
        <div class="empty-icon">💬</div>
        <p class="empty-text">向我提问吧！</p>
        <p class="empty-hint">💡 我可以帮你查询日程、总结安排，但不能创建日程</p>
        <div class="example-questions">
          <button
            v-for="example in exampleQuestions"
            :key="example"
            @click="sendMessage(example)"
            class="example-btn"
          >
            {{ example }}
          </button>
        </div>
      </div>
    </div>

    <!-- 输入框 -->
    <div class="chat-input-container">
      <input
        v-model="inputMessage"
        @keyup.enter="sendMessage()"
        placeholder="输入问题查询日程信息..."
        class="chat-input"
        :disabled="loading"
      />
      <button
        @click="sendMessage()"
        :disabled="loading || !inputMessage.trim()"
        class="send-btn"
      >
        <i class="bi bi-send-fill"></i>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { aiAPI } from '@/api'

const chatHistory = ref([])
const inputMessage = ref('')
const loading = ref(false)
const chatHistoryRef = ref(null)

const exampleQuestions = [
  '这周有什么安排？',
  '帮我总结今天的日程',
  '明天有哪些重要事件？'
]

// 发送消息
const sendMessage = async (message) => {
  const msgText = message || inputMessage.value.trim()
  
  if (!msgText) {
    ElMessage.warning('请输入消息')
    return
  }
  
  // 添加用户消息
  chatHistory.value.push({
    role: 'user',
    content: msgText,
    time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  })
  
  inputMessage.value = ''
  loading.value = true
  
  // 滚动到底部
  await nextTick()
  scrollToBottom()
  
  try {
    // 调用AI接口
    const response = await aiAPI.chat(msgText, {
      current_date: new Date().toISOString().split('T')[0]
    })
    
    if (response.success) {
      // 添加AI回复
      chatHistory.value.push({
        role: 'assistant',
        content: response.reply,
        time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
      })
    } else {
      chatHistory.value.push({
        role: 'assistant',
        content: '抱歉，我遇到了一些问题。请稍后再试。',
        time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
      })
    }
  } catch (error) {
    console.error('AI对话失败:', error)
    chatHistory.value.push({
      role: 'assistant',
      content: '网络错误，请检查连接后重试。',
      time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
    })
  } finally {
    loading.value = false
    await nextTick()
    scrollToBottom()
  }
}

// 滚动到底部
const scrollToBottom = () => {
  if (chatHistoryRef.value) {
    chatHistoryRef.value.scrollTop = chatHistoryRef.value.scrollHeight
  }
}
</script>

<style scoped>
.ai-content {
  display: flex;
  flex-direction: column;
  height: 100%;
  gap: 12px;
}

.sidebar-header h4 {
  color: var(--text-primary);
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 6px;
}

.chat-history {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 4px;
}

.chat-message {
  display: flex;
  gap: 10px;
  align-items: flex-start;
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.chat-message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  font-size: 28px;
  flex-shrink: 0;
}

.message-content {
  max-width: 75%;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.chat-message.user .message-content {
  align-items: flex-end;
}

.message-text {
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.5;
  word-wrap: break-word;
}

.chat-message.user .message-text {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border-bottom-right-radius: 4px;
}

.chat-message.assistant .message-text {
  background: white;
  color: #333;
  border: 1px solid #e0e0e0;
  border-bottom-left-radius: 4px;
}

.message-text.loading-dots {
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}

.message-time {
  font-size: 11px;
  color: #999;
  padding: 0 6px;
}

.empty-chat {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
}

.empty-icon {
  font-size: 48px;
  opacity: 0.6;
}

.empty-text {
  font-size: 15px;
  color: #999;
  margin: 0;
}

.empty-hint {
  font-size: 12px;
  color: #aaa;
  margin: 0;
  padding: 0 20px;
  text-align: center;
}

.example-questions {
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 100%;
}

.example-btn {
  padding: 10px 16px;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 20px;
  font-size: 13px;
  color: #667eea;
  cursor: pointer;
  transition: all 0.2s ease;
}

.example-btn:hover {
  background: rgba(102, 126, 234, 0.1);
  border-color: #667eea;
}

.chat-input-container {
  display: flex;
  gap: 8px;
  padding-top: 12px;
  border-top: 1px solid #e0e0e0;
}

.chat-input {
  flex: 1;
  padding: 10px 14px;
  border: 1px solid #e0e0e0;
  border-radius: 20px;
  font-size: 14px;
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
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border: none;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.send-btn:hover:not(:disabled) {
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .sidebar-header h4 {
    font-size: 18px;
  }
  
  .message-avatar {
    font-size: 24px;
  }
  
  .message-text {
    font-size: 13px;
    padding: 9px 12px;
  }
  
  .chat-input {
    font-size: 13px;
    padding: 9px 12px;
  }
}

@media (max-width: 576px) {
  .sidebar-header h4 {
    font-size: 16px;
  }
  
  .message-avatar {
    font-size: 20px;
  }
  
  .message-content {
    max-width: 80%;
  }
  
  .message-text {
    font-size: 12px;
    padding: 8px 10px;
  }
  
  .message-time {
    font-size: 10px;
  }
  
  .chat-input {
    font-size: 12px;
    padding: 8px 10px;
  }
  
  .send-btn {
    width: 36px;
    height: 36px;
    font-size: 14px;
  }
  
  .example-btn {
    font-size: 12px;
    padding: 8px 12px;
  }
}
</style>

