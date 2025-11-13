<template>
  <div class="ai-panel">
    <div class="header">
      <button class="back-btn" @click="$store.commit('updateRouterName', 'calendar')">
        ← 返回
      </button>
      <h2>🤖 AI助手</h2>
    </div>

    <div class="content">
      <!-- 快捷问题 -->
      <div class="quick-questions">
        <div class="section-title">📌 快捷提问</div>
        <button
          v-for="(question, index) in quickQuestions"
          :key="index"
          class="quick-btn"
          @click="askQuestion(question)"
          :disabled="loading"
        >
          {{ question }}
        </button>
      </div>

      <!-- 聊天记录 -->
      <div class="chat-area" ref="chatArea">
        <div
          v-for="(msg, index) in chatHistory"
          :key="index"
          :class="['chat-message', msg.role]"
        >
          <div class="message-avatar">
            {{ msg.role === 'user' ? '👤' : '🤖' }}
          </div>
          <div class="message-bubble">
            {{ msg.content }}
          </div>
        </div>

        <div v-if="loading" class="chat-message assistant">
          <div class="message-avatar">🤖</div>
          <div class="message-bubble loading">
            思考中<span class="dots">...</span>
          </div>
        </div>

        <div v-if="chatHistory.length === 0 && !loading" class="empty-state">
          💬 你好！我是AI助手，有什么可以帮你的吗？
        </div>
      </div>

      <!-- 输入区域 -->
      <div class="input-area">
        <input
          v-model="userInput"
          @keyup.enter="sendMessage"
          placeholder="输入你的问题..."
          class="chat-input"
          :disabled="loading"
        />
        <button
          @click="sendMessage"
          :disabled="loading || !userInput.trim()"
          class="send-btn"
        >
          发送
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AIAssistantPanel',
  data() {
    return {
      chatHistory: [],
      userInput: '',
      loading: false,
      quickQuestions: [
        '今天有什么日程？',
        '本周的日程安排',
        '推荐一些时间管理技巧',
        '如何提高工作效率？'
      ]
    }
  },
  methods: {
    askQuestion(question) {
      this.userInput = question
      this.sendMessage()
    },
    async sendMessage() {
      if (!this.userInput.trim() || this.loading) return

      const userMessage = this.userInput.trim()
      this.chatHistory.push({
        role: 'user',
        content: userMessage
      })
      this.userInput = ''
      this.loading = true

      // 滚动到底部
      this.$nextTick(() => {
        this.scrollToBottom()
      })

      try {
        const response = await fetch('https://app7626.acapp.acwing.com.cn/api/ai/chat/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            message: userMessage
          })
        })

        if (!response.ok) {
          throw new Error('AI请求失败')
        }

        const data = await response.json()
        
        this.chatHistory.push({
          role: 'assistant',
          content: data.reply || '抱歉，我暂时无法回答这个问题。'
        })
      } catch (error) {
        console.error('AI错误:', error)
        this.chatHistory.push({
          role: 'assistant',
          content: '抱歉，服务暂时不可用，请稍后重试。'
        })
      } finally {
        this.loading = false
        this.$nextTick(() => {
          this.scrollToBottom()
        })
      }
    },
    scrollToBottom() {
      const chatArea = this.$refs.chatArea
      if (chatArea) {
        chatArea.scrollTop = chatArea.scrollHeight
      }
    }
  }
}
</script>

<style scoped>
.ai-panel {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f5f7fa;
}

.header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 15px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  flex-shrink: 0;
}

.back-btn {
  padding: 5px 10px;
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  color: white;
  transition: all 0.3s;
}

.back-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

h2 {
  font-size: 16px;
  margin: 0;
}

.content {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 10px;
  overflow: hidden;
  min-height: 0;
}

/* 快捷问题 */
.quick-questions {
  margin-bottom: 10px;
  flex-shrink: 0;
}

.section-title {
  font-size: 11px;
  font-weight: 600;
  color: #606266;
  margin-bottom: 6px;
}

.quick-btn {
  padding: 4px 10px;
  margin: 0 4px 4px 0;
  background: white;
  border: 1px solid #dcdfe6;
  border-radius: 12px;
  cursor: pointer;
  font-size: 11px;
  color: #606266;
  transition: all 0.3s;
  white-space: nowrap;
}

.quick-btn:hover:not(:disabled) {
  background: #ecf5ff;
  border-color: #409eff;
  color: #409eff;
}

.quick-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 聊天区域 */
.chat-area {
  flex: 1;
  overflow-y: auto;
  background: white;
  border-radius: 8px;
  padding: 10px;
  margin-bottom: 10px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  min-height: 0;
}

.empty-state {
  text-align: center;
  padding: 20px 10px;
  color: #909399;
  font-size: 12px;
}

.chat-message {
  display: flex;
  gap: 8px;
  margin-bottom: 10px;
  animation: fadeIn 0.3s;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-avatar {
  font-size: 20px;
  flex-shrink: 0;
}

.message-bubble {
  padding: 6px 10px;
  border-radius: 8px;
  max-width: 75%;
  font-size: 11px;
  line-height: 1.4;
}

.chat-message.user .message-bubble {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border-bottom-right-radius: 4px;
}

.chat-message.assistant .message-bubble {
  background: #f0f2f5;
  color: #303133;
  border-bottom-left-radius: 4px;
}

.message-bubble.loading {
  font-style: italic;
  color: #909399;
}

.dots {
  animation: dots 1.5s infinite;
}

@keyframes dots {
  0%, 20% {
    content: '.';
  }
  40% {
    content: '..';
  }
  60%, 100% {
    content: '...';
  }
}

/* 输入区域 */
.input-area {
  display: flex;
  gap: 6px;
  flex-shrink: 0;
}

.chat-input {
  flex: 1;
  padding: 6px 10px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  font-size: 11px;
  outline: none;
  transition: all 0.3s;
}

.chat-input:focus {
  border-color: #409eff;
}

.chat-input:disabled {
  background: #f5f7fa;
  cursor: not-allowed;
}

.send-btn {
  padding: 6px 16px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 11px;
  font-weight: 500;
  transition: all 0.3s;
  white-space: nowrap;
}

.send-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>

