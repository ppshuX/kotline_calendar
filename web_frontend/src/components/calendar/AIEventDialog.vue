<template>
  <el-dialog
    v-model="visible"
    title="🤖 AI创建日程"
    width="90%"
    :style="{ maxWidth: '500px' }"
    @close="handleClose"
  >
    <div class="ai-event-dialog">
      <!-- 输入区域 -->
      <div class="input-section">
        <div class="input-label">
          <i class="bi bi-chat-dots"></i> 告诉我你的安排
        </div>
        <textarea
          v-model="userInput"
          placeholder="例如：明天下午3点开会，讨论项目方案&#10;或：周五晚上7点和朋友吃饭"
          class="event-input"
          rows="3"
          @keyup.ctrl.enter="parseEvent"
          :disabled="loading"
        ></textarea>
        <div class="input-hint">
          💡 Ctrl+Enter 快速提交 | 支持自然语言描述
        </div>
      </div>

      <!-- AI解析结果 -->
      <div v-if="parsedEvent" class="parsed-result">
        <div class="result-title">
          <i class="bi bi-check-circle-fill"></i> AI已理解
        </div>
        
        <div class="result-items">
          <div class="result-item">
            <div class="item-label">📌 标题</div>
            <div class="item-value">{{ parsedEvent.title }}</div>
          </div>
          
          <div class="result-item">
            <div class="item-label">📅 日期</div>
            <div class="item-value">{{ parsedEvent.date }}</div>
          </div>
          
          <div class="result-item" v-if="parsedEvent.time">
            <div class="item-label">🕐 时间</div>
            <div class="item-value">{{ parsedEvent.time }}</div>
          </div>
          
          <div class="result-item" v-if="parsedEvent.description">
            <div class="item-label">📝 备注</div>
            <div class="item-value">{{ parsedEvent.description }}</div>
          </div>
        </div>
      </div>

      <!-- 加载中 -->
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>AI正在理解你的描述...</p>
      </div>

      <!-- 错误提示 -->
      <div v-if="error" class="error-state">
        <i class="bi bi-exclamation-circle"></i>
        <p>{{ error }}</p>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button
          v-if="!parsedEvent"
          type="primary"
          @click="parseEvent"
          :loading="loading"
          :disabled="!userInput.trim()"
        >
          <i class="bi bi-magic"></i> AI解析
        </el-button>
        <el-button
          v-else
          type="success"
          @click="confirmCreate"
        >
          <i class="bi bi-check-lg"></i> 确认创建
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { aiAPI } from '@/api'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'create'])

const visible = ref(props.modelValue)
const userInput = ref('')
const parsedEvent = ref(null)
const loading = ref(false)
const error = ref('')

// 同步visible状态
watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val) {
    // 打开时重置状态
    userInput.value = ''
    parsedEvent.value = null
    error.value = ''
  }
})

watch(visible, (val) => {
  emit('update:modelValue', val)
})

// AI解析日程
const parseEvent = async () => {
  if (!userInput.value.trim()) {
    ElMessage.warning('请输入日程描述')
    return
  }
  
  loading.value = true
  error.value = ''
  
  try {
    const response = await aiAPI.parseEvent(userInput.value)
    
    if (response.success && response.event) {
      parsedEvent.value = response.event
      ElMessage.success('AI解析成功！请确认信息')
    } else {
      error.value = response.error || 'AI解析失败，请尝试更清晰的描述'
    }
  } catch (err) {
    console.error('AI解析失败:', err)
    error.value = '网络错误，请稍后重试'
  } finally {
    loading.value = false
  }
}

// 确认创建
const confirmCreate = () => {
  if (!parsedEvent.value) return
  
  // 发送事件给父组件
  emit('create', parsedEvent.value)
  handleClose()
  ElMessage.success('日程创建成功！')
}

// 关闭对话框
const handleClose = () => {
  visible.value = false
  userInput.value = ''
  parsedEvent.value = null
  error.value = ''
}
</script>

<style scoped>
.ai-event-dialog {
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-height: 200px;
}

.input-section {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.input-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 600;
  color: #4A148C;
}

.event-input {
  width: 100%;
  padding: 12px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  line-height: 1.6;
  resize: vertical;
  outline: none;
  transition: border-color 0.2s ease;
}

.event-input:focus {
  border-color: #667eea;
}

.event-input:disabled {
  background: #f5f5f5;
  cursor: not-allowed;
}

.input-hint {
  font-size: 12px;
  color: #999;
}

.parsed-result {
  padding: 16px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05), rgba(118, 75, 162, 0.05));
  border-radius: 12px;
  border-left: 4px solid #667eea;
}

.result-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #667eea;
  margin-bottom: 12px;
}

.result-items {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.result-item {
  display: flex;
  gap: 12px;
}

.item-label {
  font-size: 14px;
  color: #6A1B9A;
  font-weight: 500;
  min-width: 60px;
}

.item-value {
  font-size: 14px;
  color: #4A148C;
  font-weight: 600;
  flex: 1;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 40px 20px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-state p {
  font-size: 14px;
  color: #999;
  margin: 0;
}

.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 20px;
  background: rgba(255, 107, 107, 0.1);
  border-radius: 8px;
}

.error-state i {
  font-size: 32px;
  color: #ff6b6b;
}

.error-state p {
  font-size: 14px;
  color: #ff6b6b;
  margin: 0;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

@media (max-width: 576px) {
  .event-input {
    font-size: 13px;
    padding: 10px;
  }
  
  .input-hint {
    font-size: 11px;
  }
  
  .result-title {
    font-size: 15px;
  }
  
  .item-label,
  .item-value {
    font-size: 13px;
  }
}
</style>

